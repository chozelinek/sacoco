# -*- coding: utf-8 -*-

import sys
import os
import glob
import codecs # to handle properly unicode
import re # to use regular expressions
import argparse # to parse command-line arguments
import time
import fnmatch
import math
import pandas as pd

#===============================================================================
# Import XML module
#===============================================================================
from lxml import etree

#===============================================================================
# Following code block is only needed if lxml is not used as the parser
#===============================================================================

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args,**kw)
        te = time.time()

#         print '%r (%r, %r) %2.2f sec' % \
#               (method.__name__, args, kw, te-ts)
        print('%r %2.2f sec' % \
              (method.__name__, te-ts))
        return result

    return timed

class AddMetadata(object):
    '''
    Instantiate a class whose name is built from CL arguments
    '''
    @timeit
    def __init__(self):
        self.cli()
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)
        self.add_metadata()
        
    def __str__(self):
        message = ["Guten Appetit!"]
        return ", ".join(message)
    
    def cli(self):
        """CLI parses command-line arguments"""
        parser = argparse.ArgumentParser()
        parser.add_argument("-i", "--input", default='test/contemporary/vrt', help="input directory where to find the input.")
        parser.add_argument("-m", "--metadata", default='test/metadata/wiki-metadata-textid.csv', help="metadata file.")
        parser.add_argument("-o","--output", default='test/contemporary/meta', help="target directory where to save the output.")
        args = parser.parse_args()
        self.indir = args.input
        self.outdir = args.output
        self.metadata = args.metadata
        pass
    
    
    def get_files(self, directory, fileclue):
        matches = []
        for root, dirnames, filenames in os.walk(directory):
            for filename in fnmatch.filter(filenames, fileclue):
                matches.append(os.path.join(root, filename))
        return matches 
    
    def read_infile(self,infile):
        """Parse the XML file."""
        parser = etree.XMLParser(remove_blank_text=True)
        with codecs.open(infile, encoding='utf-8',mode='r+') as input:
            return etree.parse(input, parser)
    
    def add_metadata(self):
        input_files = self.get_files(self.indir, '*.vrt')
        df = pd.read_csv(self.metadata, sep = '\t')
        metadata = df.set_index('Unnamed: 0').T.to_dict('dict')
        for file in input_files:
            output_file = os.path.join(self.outdir,os.path.basename(file))
            tree = self.read_infile(file)
            root = tree.getroot()
            text_id = os.path.splitext(os.path.basename(file))[0]
            if text_id in metadata.keys():
                for key in metadata[text_id].keys():
                    root.set(key,str(metadata[text_id][key]))
                vrt = etree.tostring(tree, encoding='unicode', method='xml') # convert the XML tree into a string to manipulate it
                vrt = re.sub(r"><", r">\n<", vrt)
                vrt = re.sub(r">([^<\n])", r">\n\1", vrt)
                vrt = re.sub(r"([^\n])<", r"\1\n<", vrt)
                vrt = etree.ElementTree(etree.fromstring(vrt)) # parse the string as an element and convert the element in a tree
                vrt.write(output_file, encoding="utf8", xml_declaration=True, method="xml")
            else:
                print('Text ID "{}" is unknown!'.format(text_id))
            
print(AddMetadata())