#!/usr/bin/env python

import re
import os
import collections


def compact_allall_folder(cachedir):
    """this function compacts the chunk files of the AllAll computation.

    :param cachedir: the path to the Cache folder to be compacted.
                     Don't add the AllAll folder."""
 
    allall_root = os.path.normpath(os.path.join(cachedir, 'AllAll'))
    _dirs_top = [ f for f in os.listdir(allall_root) 
        if os.path.isdir(os.path.join(allall_root,f)) ]
    buf_size = 2**16
    
    for _dir in _dirs_top:
        allfiles = []
        for d, subd, dfiles in os.walk(os.path.join(allall_root, _dir)): 
            allfiles.extend(list(map(lambda f: os.path.join(d,f), dfiles)))
        tots = collections.defaultdict(int)
        cnts = collections.defaultdict(int)
        files = collections.defaultdict(list)    
        part_re = re.compile(r'.*{0}{1}(?P<species>\w*)({1}part)?_(?P<nr>\d+)-(?P<tot>\d+).gz'.format(
            os.path.join(allall_root, _dir), os.path.sep))
        for _file in allfiles:
            match = part_re.match(_file);
            if match:
                spec2 = match.group('species')
                if tots[spec2]==0:
                    tots[spec2] = int(match.group('tot'))
                cnts[spec2] += 1
                files[spec2].append(_file)
    
        for spec2 in tots:
            if cnts[spec2]==tots[spec2]:
                outfn = os.path.join(allall_root, _dir, spec2 + ".gz")
                if os.path.isfile(outfn):
                    print('{} already exists. Leaving part files untouched!'.format(outfn))
                    continue

                with open(os.path.join(allall_root, _dir, spec2 + ".gz"), 'wb') as dest:
                    for f in files[spec2]:
                        with open(f, 'rb') as src:
                            for chunk in iter(lambda:src.read(buf_size), ''):
                                if chunk==b'':
                                    break
                                dest.write(chunk)
                for f in files[spec2]:
                    os.remove(f)
                try:
                    os.rmdir(os.path.join(allall_root, _dir, spec2))
                except FileNotFoundError:
                    pass
                  
                print('compacted {} vs {}'.format(_dir, spec2))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(prog="AllAll Compactor")
    parser.add_argument('cachedir', help="path to the Cache folder that should be compacted")
    conf = parser.parse_args()

    compact_allall_folder(conf.cachedir)
