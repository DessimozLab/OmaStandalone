import Bio.SeqIO
import requests
import json
import os

def retrieve_from_uniprot_rest(endpoint):
    url = "https://www.ebi.ac.uk/proteins/api/taxonomy/" + endpoint
    r = requests.get(url, headers={"Accept": "application/json"})
    if not r.ok:
        r.raise_for_status()
    return json.loads(r.text)


def darwin_header_from_uniprot_rest(taxid):
    os_data = retrieve_from_uniprot_rest("id/{:d}".format(taxid))
    lineage = retrieve_from_uniprot_rest("lineage/{:d}".format(taxid))
    header = {'SCINAME': os_data['scientificName'],
              '5LETTERNAME': os_data['mnemonic'],
              'TAXONID': os_data['taxonomyId']}
    if 'commonName' in os_data:
        header['COMMONNAME'] = os_data['commonName']
    if 'synonym' in os_data:
        header['SYNNAME'] = os_data['synonym']
    lin = [z['scientificName'] for z in lineage['taxonomies']]
    while lin[-1] not in ('Eukaryota','Bacteria','Archaea'):
        lin.pop()
    header['KINGDOM'] = lin[-1]
    lin.reverse()
    header['OS'] = "; ".join(lin)
    return header


class ProteomeSeqxmlConverter(object):

    def __init__(self, fname):
        open_ = gzip.GzipFile if fname.endswith('.gz') else open
        self.fh = open_(fname, 'rb')
        self.headers = self._load_header()

    def __del__(self):
        self.fh.close()

    def _load_header(self):
        rec = next(Bio.SeqIO.parse(self.fh, 'seqxml'))
        taxid = int(rec.annotations['ncbi_taxid'])
        self.fh.seek(0)
        return darwin_header_from_uniprot_rest(taxid)

    def convert(self, base_folder):
        db_folder = os.path.join(base_folder, "DB")
        drw_db_fold = os.path.join(base_folder, "Cache", "DB")
        os.makedirs(db_folder, exist_ok=True)
        os.makedirs(drw_db_fold, exist_ok=True)
        with open(os.path.join(db_folder, self.headers['5LETTERNAME']+'.fa'), 'w') as fa, \
             open(os.path.join(drw_db_fold, self.headers['5LETTERNAME']+".db"), 'w') as db:
            # write db headers
            for k, v in self.headers.items():
                db.write('<{0}>{1}</{0}>\n'.format(k,v)) 
            for entry in self.parse():
                db.write("<E>" + "".join(['<{0}>{1}</{0}>'.format(k,v) for k, v in entry.items()]) + "</E>\n")
                fa.write(">{}\n{}\n\n".format(entry['ID'], entry['SEQ']))

    def parse(self):
        unknown_aa_to_X_table = str.maketrans('BUZJO$*', 'X' * 7)
        xrefs = frozenset(['Gene_Name', 'DNAsource', 'CRC64', 'RefSeq', 'GeneID', 
                           'EnsemblGenome', 'EnsemblGenome_PRO', 'Ensembl', 'Ensembl_PRO'])
        for rec in Bio.SeqIO.parse(self.fh, 'seqxml'):
            data = {'ID': rec.id, 'SEQ': str(rec.seq).translate(unknown_aa_to_X_table)}
            if rec.description:
                data['DE'] = rec.description
            
            for xref in rec.dbxrefs:
                src, val = xref.split(":", 1)
                if src in xrefs:
                    data[src] = val

            try:
                cDNA = rec.annotations['DNAseq'][0]
                cDNA = Bio.Seq.Seq(cDNA)
            except KeyError:
                cDNA = Bio.Seq.UnknownSeq(3*(len(rec)+1), character="N")
            data['DNA'] = cDNA
            yield data

def main():
    import argparse
    p = argparse.ArgumentParser(description="Convert Reference Proteomes to OMA standalone format")
    p.add_argument('-b', '--folder', default="./", help="Path to base folder")
    p.add_argument('xml', nargs="+", help="Input reference proteomes in xml format")
    conf = p.parse_args()

    for refgenome in conf.xml:
        c = ProteomeSeqxmlConverter(refgenome)
        c.convert(conf.folder)


if __name__ == "__main__":
    main()
