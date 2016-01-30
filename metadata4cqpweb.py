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

class MetadataForCqpWeb(object):
    '''
    Instantiate a class whose name is built from CL arguments
    '''
    @timeit
    def __init__(self):
        self.cli()
        self.success = 0
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)
        self.main()
        
    def __str__(self):
        if self.success > 0:
            message = [
                       "{} files processed!".format(str(self.success)),
                       "Guten Appetit!"
                       ]
        else:
            message = [
                       "{} files processed!".format(str(self.success)),
                       "Ups! Maybe something went wrong!"
                       ]
        return " ".join(message)
    
    
    
    def cli(self):
        """CLI parses command-line arguments"""
        parser = argparse.ArgumentParser()
        parser.add_argument("-i","--input", nargs='+', help="input files.")
        parser.add_argument("-o","--output", help="output file.")
        parser.add_argument("-c","--columns", help="columns to be extracted.")
        args = parser.parse_args()
        noneargs = [x for x in args.__dict__.values()].count(None)
        if noneargs == 3:
            print("Running in test mode!")
            self.infiles = ['test/metadata/contemporary-metadata.csv']
#             self.infiles = ['test/metadata/contemporary-metadata.csv','test/metadata/historical-metadata.csv']
            self.outfile = 'test/sacoco.meta'
            self.columns = ['year','decade','period','collection','source', 'title', 'ingredients']
        elif noneargs > 0 and noneargs < 3:
            options = ["'-"+k[0]+"'" for k,v in args.__dict__.items() if v == None]
            options = ', '.join(options)
            exit_message = '\n'.join(["You forgot option(s): {}".format(options),
                                     "Provide no option to run in test mode: 'python3 {}'".format(os.path.basename(__file__)),
                                     "Get help with option '-h': 'python3 {} -h'".format(os.path.basename(__file__))]
                                     )
            sys.exit(exit_message)
        else:
            self.infiles = args.input
            self.outfile = args.output
            self.columns = args.columns
        self.outdir = os.path.split(self.outfile)[0]
        pass
    
    def get_files(self, directory, fileclue):
        matches = []
        for root, dirnames, filenames in os.walk(directory):
            for filename in fnmatch.filter(filenames, fileclue):
                matches.append(os.path.join(root, filename))
        return matches 
    
    def main(self):
        # merge files in one data frame
        if len(self.infiles) == 1:
            # read the file
            df = pd.read_csv(self.infiles[0], sep = '\t')
            self.success = 1
        elif len(self.infiles[1:]) >= 1:
            # read the first
            df = pd.read_csv(self.infiles[0], sep = '\t')
            self.success = 1
            # read the rest
            for file in self.infiles[1:]:
                # read file
                newdf = pd.read_csv(file, sep = '\t')
                # concatenate to first
                newdf = newdf.reset_index(drop=True)
                df = pd.concat([df, newdf], axis=0)
                self.success += 1
        # filter the columns we want
        df = df.rename(columns = {'Unnamed: 0':'text_id'})
        df = df[['text_id']+self.columns]
        df.to_csv(self.outfile, sep = '\t', index = False, header = False)
        
print(MetadataForCqpWeb())