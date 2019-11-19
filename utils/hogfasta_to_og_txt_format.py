import os
import re
import sys
id_re = re.compile(r'>\s*(?P<id>.*)\s+\[(?P<species>.*)\]')


def extract_ids(fname):
    with open(fname, 'r') as fh:
        for line in fh:
            if not line.startswith('>'):
                continue
            m = id_re.match(line)
            yield "{}:{}".format(m.group('species'), m.group('id'))


def reformat(hogfasta, outfile):
    with open(outfile,'w') as fout:
        for fname in os.listdir(hogfasta):
            if not fname.endswith('.fa'):
                continue
            ids = list(extract_ids(os.path.join(hogfasta, fname)))
            fout.write("{}\t{}\n".format(fname[:-3], "\t".join(ids)))


if __name__ == "__main__":
    reformat(sys.argv[1], sys.argv[2])
