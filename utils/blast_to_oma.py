import time
import Bio.SearchIO
import Bio.SeqIO
import os
import gzip
import collections
import itertools
import logging
import pyopa

logger = logging.getLogger(__name__)
OmaID = collections.namedtuple('OmaID', 'genome nr')
MatchData = collections.namedtuple('MatchData', 'bits rng1 rng2')
OmaMatchData = collections.namedtuple('OmaMatchData', 'score dist rng1 rng2 var')


class IdMapper(object):
    def __init__(self):
        self.genomes = []
        self.ids = {}
        self.nr_entries = {}

    def add_genome(self, fn):
        open_ = gzip.open if fn.endswith('.gz') else open
        gname, _ = os.path.basename(fn).split('.')
        nr = 0
        with open_(fn, 'r') as fh:
            seqs = Bio.SeqIO.parse(fh, 'fasta')
            for k, prot in enumerate(seqs):
                nr = k + 1
                ids = frozenset([prot.id, prot.id.split(' ')[0]])
                for cur_id in ids:
                    if cur_id in self.ids:
                        raise KeyError('id "{}" already assigned: {}'.format(cur_id, self.ids[cur_id]))
                    self.ids[cur_id] = OmaID(gname, nr)
        self.genomes.append(gname)
        self.nr_entries[gname] = nr
        logger.info("added {} with {} entries".format(gname, nr))

    def map_id(self, gid):
        try:
            return self.ids[gid]
        except KeyError:
            return self.ids[gid.split(' ')[0]]

    def order_pair(self, id1, id2):
        if id1.genome == id2.genome:
            return (id1, id2) if id1.nr <= id2.nr else (id2, id1)
        if (self.nr_entries[id1.genome] < self.nr_entries[id2.genome] or
                (self.nr_entries[id1.genome] == self.nr_entries[id2.genome] and id1.genome < id2.genome)):
            return (id1, id2)
        else:
            return (id2, id1)


class MLDistanceEstimator(object):
    def __init__(self):
        import pyopa
        envs = pyopa.load_default_environments()
        self.dist_opt = pyopa.MutipleAlEnv(envs['environments'], envs['log_pam1'])
        self.trans_table = str.maketrans('BUZJO$*-', 'X' * 7 + '_')

    def process_hit(self, hsp):
        if hsp is None or hsp.query_id == hsp.hit_id:
            return None
        s1, s2 = (pyopa.Sequence(str(z.seq).translate(self.trans_table)) for z in list(hsp.aln))
        score, dist, var = self.dist_opt.estimate_pam(s1, s2)
        return OmaMatchData(score, dist, tuple(z + 1 for z in hsp.query_range),
                            tuple(z + 1 for z in hsp.hit_range), var)


class KernelDistanceEstimator(object):
    def process_hit(self, hsp):
        if hsp is None:
            return None
        return MatchData(hsp.bitscore, tuple(1 + z for z in hsp.query_range),
                         tuple(1 + z for z in hsp.hit_range))


class MatchConverter(object):
    def __init__(self, idmapper, cacheroot):
        self.idmapper = idmapper
        self.root = cacheroot
        self.matches = collections.defaultdict(dict)
        os.makedirs(os.path.join(cacheroot, 'AllAll'), exist_ok=True)

    def add_match_to_buffer(self, query, target, match):
        if match is None:
            return
        gene1, gene2 = self.idmapper.order_pair(query, target)
        try:
            existing_match = self.matches[(gene1.genome, gene2.genome)][(gene1.nr, gene2.nr)]
        except KeyError:
            # create a fake tuple and compare score with that one
            existing_match = (-1e5,)
        # compare scores and keep higher one
        if existing_match[0] < match[0]:
            if query != gene1:
                # reverse the match
                if isinstance(match, OmaMatchData):
                    match = OmaMatchData(match.score, match.dist, match.rng2, match.rng1, match.var)
                else:
                    match = MatchData(match.bits, match.rng2, match.rng1)
            self.matches[(gene1.genome, gene2.genome)][(gene1.nr, gene2.nr)] = match

    def convert_xml(self, file, format='blast-xml', dist_estimator=None):
        if dist_estimator is None:
            dist_estimator = KernelDistanceEstimator()
        open_ = gzip.open if file.endswith('.gz') else open
        tot_hits = 0
        cnt_hsps, hsps_since_t0, t0 = 0, 0, time.time()
        with open_(file) as fh:
            p = Bio.SearchIO.parse(fh, format)
            for query_res in p:
                try:
                    query_oma_id = self.idmapper.map_id(query_res.id)
                except KeyError:
                    logger.error('Cannot find {} in fasta files'.format(query_res.id))
                    continue
                hits = 0
                for hit in query_res:
                    try:
                        target_oma_id = self.idmapper.map_id(hit.id)
                    except KeyError:
                        logger.error('cannot find subject {} in fasta files'.format(hit.id))
                        continue
                    max_hsp_score, max_hit = -10, None
                    for hsp in hit.hsps:
                        cnt_hsps += 1
                        if hsp.bitscore > max_hsp_score:
                            max_hsp_score, max_hit = hsp.bitscore, hsp
                        if cnt_hsps % 2000 == 0 and time.time() - t0 > 10:
                            logger.info('analysed {:d} high scoring pairs, rate: {:.1f}/sec'.format(
                                cnt_hsps, (cnt_hsps - hsps_since_t0) / (time.time() - t0)))
                            hsps_since_t0, t0 = cnt_hsps, time.time()

                    hits += 1
                    match = dist_estimator.process_hit(max_hit)
                    self.add_match_to_buffer(query_oma_id, target_oma_id, match)
                logger.debug('processed {} hits for {}'.format(hits, query_res.id))
                tot_hits += hits
            logger.info('processed {} hits in total'.format(tot_hits))
        self.process_matches()

    def process_matches(self):
        for gnr1, gnr2 in itertools.product(range(len(self.idmapper.genomes)), repeat=2):
            nr_entries1, nr_entries2 = (self.idmapper.nr_entries[self.idmapper.genomes[z]] for z in (gnr1, gnr2))
            if ((nr_entries1 > nr_entries2) or
                    (nr_entries1 == nr_entries2 and
                     self.idmapper.genomes[gnr1] > self.idmapper.genomes[gnr2])):
                gnr1, gnr2 = gnr2, gnr1
            g1, g2 = (self.idmapper.genomes[g] for g in (gnr1, gnr2))
            os.makedirs(os.path.join(self.root, 'AllAll', g1), exist_ok=True)
            with gzip.open(os.path.join(self.root, 'AllAll', g1, g2 + ".gz"), 'w') as fh:
                fh.write(b'RefinedMatches([\n')
                matches_x_x, matches_x_y, matches_y_y = (self.matches[pair] for pair in
                                                         ((g1, g1), (g1, g2), (g2, g2)))
                logger.info('processing {}/{} with {} matches'.format(g1, g2, len(matches_x_y)))
                for (i, j), match in matches_x_y.items():
                    if gnr1 == gnr2 and i >= j:
                        logger.warning('these pairs should not exist: {}/{}'.format(i, j))
                        continue
                    try:
                        if isinstance(match, MatchData):
                            dist = max(matches_x_x[(i, i)].bits + matches_y_y[(j, j)].bits - 2 * match.bits, 0.045)
                            oma_match = OmaMatchData(match.bits, dist, match.rng1, match.rng2, dist ** 2)
                        else:
                            oma_match = match
                        fh.write(
                            "[{i:d},{j:d},{score:f},{dist:f},{rng1[0]:d}..{rng1[1]:d}"
                            ",{rng2[0]:d}..{rng2[1]:d},{var:f}],\n"
                            .format(i=i, j=j, **oma_match._asdict()).encode('utf-8'))
                    except KeyError as e:
                        logger.warning('cannot access self match {} in {}'.format(e, match))

                fh.write(b'NULL]):\n')


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser("Convert a blast AllAll run into OMA standalone AllAll")
    p.add_argument('--out', '-o', default="Cache", help="path to OMA Cache directory. defaults to 'Cache/'")
    p.add_argument('--format', '-f', default='xml', help="format of allall file, either 'xml' or 'tab'")
    p.add_argument('--dist', '-d', default="kernel", help="used distance estimation, eiterh 'kernel' or 'ML'",
                   choices=['ML', 'kernel'])
    p.add_argument('allall_file', help="path to blast allall file.")
    p.add_argument('genomes', nargs="+", help="Fasta formatted input genome")
    p.add_argument('-v', action="count", help="increase verbosity level", default=0)
    conf = p.parse_args()

    logging.basicConfig(level=max(30 - 10 * conf.v, 10))
    idmapper = IdMapper()
    for genome in conf.genomes:
        idmapper.add_genome(genome)
    if conf.dist == 'ML':
        dist_estimator = MLDistanceEstimator()
    elif conf.dist == 'kernel':
        dist_estimator = KernelDistanceEstimator()
    converter = MatchConverter(idmapper, conf.out)
    converter.convert_xml(conf.allall_file, 'blast-' + conf.format, dist_estimator)
