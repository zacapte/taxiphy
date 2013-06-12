#!/usr/bin/env python
import argparse
import Bio.Phylo as bp
import sys
reload(sys)
sys.setdefaultencoding('latin1')
from itis import Itis
from ncbi import Ncbi
from gbif import Gbif
taxonomies = {
              'itis': Itis, 
              'ncbi': Ncbi,
              'gbif': Gbif,
              'ALL': None,
              }

parser = argparse.ArgumentParser()
parser.add_argument('taxonomy', help='name of taxonomy to download (%s)' % 
                    ', '.join(sorted(taxonomies.keys())))
parser.add_argument('filename', help='file to save tree', 
                    nargs='?', default=None)
parser.add_argument('format', help='tree format (%s)' %
                    ', '.join(sorted(bp._io.supported_formats.keys())),
                    nargs='?', default='newick')

args = parser.parse_args()

if args.taxonomy == 'ALL':
    classes = [x for x in taxonomies.values() if not x is None]
    args.filename = None
else:
    classes = [taxonomies[args.taxonomy]]
    
for c in classes:
    taxonomy = c()
    print '** %s **' % taxonomy.name
    filename = args.filename or ('%s_taxonomy.%s' % (taxonomy.name, args.format))
    taxonomy.main(filename, tree_format=args.format)
