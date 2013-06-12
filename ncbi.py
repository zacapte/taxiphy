import urllib2
import Bio.Phylo as bp
from Bio.Phylo import BaseTree
import os
import tarfile
from taxonomy import Taxonomy


class Ncbi(Taxonomy):
    name = 'ncbi'
    
    def main(self, tree_filename, tree_format='newick'):
        col_delimiter = '\t|\t'
        row_delimiter = '\t|\n'
        url = 'ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump.tar.gz'
        
        # download the taxonomy archive
        self.download_file(url)
        
        # extract the text dump
        for extract in ('nodes.dmp', 'names.dmp'):
            if os.path.exists(os.path.join(self.data_dir, extract)):
                print 'Using existing copy of %s' % extract
            else:
                print 'Extracting %s from %s...' % (extract, filename)
                archive = tarfile.open(name=filename, mode='r:gz')
                archive.extract(extract, path=self.data_dir)
                archive.close()
        
        # get names for all tax_ids from names.dmp
        print 'Getting names...'
        scientific_names = {}
        common_names = {}
        with open(os.path.join(self.data_dir, 'names.dmp')) as names_file:
            for line in names_file:
                line = line.rstrip(row_delimiter)
                values = line.split(col_delimiter)
                tax_id, name_txt, _, name_type = values[:4]
                if name_type == 'scientific name':
                    scientific_names[tax_id] = name_txt
                elif name_type == 'common name':
                    common_names[tax_id] = name_txt
        
        # read all node info from nodes.dmp
        print 'Reading taxonomy...'
        nodes = {}
        with open(os.path.join(self.data_dir, 'nodes.dmp')) as nodes_file:
            for line in nodes_file:
                line = line.rstrip(row_delimiter)
                values = line.split(col_delimiter)
                tax_id, parent_id = values[:2]
                this_node = BaseTree.Clade(name=scientific_names[tax_id])
                if tax_id in common_names:
                    this_node.comment = common_names[tax_id]
                nodes[tax_id] = this_node
                this_node.parent_id = parent_id
        
        print 'Found %s OTUs.' % len(nodes)
        
        # create tree from nodes dictionary
        print 'Building tree...'
        for node_id, this_node in nodes.iteritems():
            if node_id == this_node.parent_id:
                root_node = this_node
                print 'Found root.'
            else:
                parent_node = nodes[this_node.parent_id]
                parent_node.clades.append(this_node)
                
            del this_node.parent_id
        
        tree = BaseTree.Tree(root=root_node)
        
        # write tree to file
        print 'Writing %s tree to %s...' % (tree_format, tree_filename)
        bp.write([tree], tree_filename, tree_format)
        
        print 'Done!'
