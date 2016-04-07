#!/usr/bin/env python

import re
import os
import collections


def compact_allall_folder(cachedir):
    """this function compacts the chunk files of the AllAll computation.

    :param cachedir: the path to the Cache folder to be compacted.
                     Don't add the AllAll folder."""
 
    part_re = re.compile(r'(?P<species>\w*)_(?P<nr>\d+)-(?P<tot>\d+).gz')
    allall_root = os.path.join(cachedir, 'AllAll')
    _dirs_top = [ f for f in os.listdir(allall_root) 
        if os.path.isdir(os.path.join(allall_root,f)) ]
    buf_size = 2**16
    
    for _dir in _dirs_top:
        allfiles = [f for f in os.listdir(os.path.join(allall_root, _dir ))
                        if os.path.isfile(os.path.join(allall_root, _dir, f))]
        tots = collections.defaultdict(int)
        cnts = collections.defaultdict(int)
        files = collections.defaultdict(list)    
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
                with open(os.path.join(allall_root, _dir, spec2 + ".gz"), 'wb') as dest:
                    for f in files[spec2]:
                        with open(os.path.join(allall_root, _dir, f), 'rb') as src:
                            for chunk in iter(lambda:src.read(buf_size), ''):
                                dest.write(chunk)
                for f in files[spec2]:
                    os.remove(os.path.join(allall_root, _dir, f))
                print('compacted '+spec2)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(prog="AllAll Compactor")
    parser.add_argument('cachedir', help="path to the Cache folder that should be compacted")
    conf = parser.parse_args()

    compact_allall_folder(conf.cachedir)
