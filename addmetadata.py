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
        if self.success > 0:
            message = [
                       "{} recipes out of {} processed!".format(str(self.success),str(self.total)),
                       "Guten Appetit!"
                       ]
        else:
            message = [
                       "{} recipes out of {} processed!".format(str(self.success),str(self.total)),
                       "Ups! Maybe something went wrong!"
                       ]
        return " ".join(message)
    
    
    
    def cli(self):
        """CLI parses command-line arguments"""
        parser = argparse.ArgumentParser()
        parser.add_argument("-i","--input", help="input directory.")
        parser.add_argument("-m","--metadata", help = "metadata file.")
        parser.add_argument("-o","--output", help="output directory.")
        parser.add_argument("-t","--test", choices = ['contemporary','historical'], help = "run in test mode.")
        args = parser.parse_args()
        noneargs = [x for x in args.__dict__.values()].count(None)
        if noneargs == 3 and args.test != None:
            print("Running in test mode!")
            self.indir = 'test/{}/vrt'.format(args.test)
            self.outdir = 'test/{}/meta'.format(args.test)
            self.metadata = 'test/metadata/{}-metadata.csv'.format(args.test)
        elif noneargs > 1 and args.test == None:
            options = ["'-"+k[0]+"'" for k,v in args.__dict__.items() if v == None]
            options = ', '.join(options)
            exit_message = '\n'.join(["You forgot option(s): {}".format(options),
                                     "Provide option '-t [contemporary|historical]' to run in test mode: 'python3 {} -t contemporary'".format(os.path.basename(__file__)),
                                     "Get help with option '-h': 'python3 {} -h'".format(os.path.basename(__file__))]
                                     )
            sys.exit(exit_message)
        else:
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
        self.total = len(input_files)
        self.success = 0
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
                self.success += 1
            else:
                print('Text ID "{}" is unknown!'.format(text_id))
            
print(AddMetadata())