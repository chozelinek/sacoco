# -*- coding: utf-8 -*-

import os
import re # to use regular expressions
import argparse # to parse command-line arguments
import time
import fnmatch
import pandas as pd
from lxml import etree

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args,**kw)
        te = time.time()

        print('%r %2.2f sec' % \
              (method.__name__, te-ts))
        return result

    return timed

class Texts2Corpus(object):
    '''
    Instantiate a class whose name is built from CL arguments
    '''
    @timeit
    def __init__(self):
        self.cli()
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)
        self.main()
        
    def __str__(self):
        message = ["Guten Appetit!"]
        return ", ".join(message)
    
    def cli(self):
        """CLI parses command-line arguments"""
        parser = argparse.ArgumentParser()
        parser.add_argument("-i", "--input", nargs='*', default='test/contemporary/meta', help="path(s) to input folder(s).")
        parser.add_argument("-o", "--output", default='test/contemporary/meta/sacoco.vrt', help="target file where to save the output.")
        args = parser.parse_args()
        self.indirs = args.input
        self.outfile = args.output
        self.outdir = os.path.split(args.output)[0]
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
        with open(infile, encoding='utf-8',mode='r+') as input:
            return etree.parse(input, parser)
    
    def main(self):
        input_files = []
        for folder in self.indirs:
            input_files += self.get_files(folder, '*.vrt')
        otree = etree.ElementTree(etree.Element('corpus'))
        corpus = otree.getroot()
        for file in input_files:
            tree = self.read_infile(file)
            text = tree.getroot()
            corpus.append(text)
        corpus = etree.tostring(corpus, encoding='unicode', method='xml') # convert the XML tree into a string to manipulate it
        corpus = re.sub(r"><", r">\n<", corpus)
        corpus = re.sub(r">([^<\n])", r">\n\1", corpus)
        corpus = re.sub(r"([^\n])<", r"\1\n<", corpus)
        vrt = etree.ElementTree(etree.fromstring(corpus)) # parse the string as an element and convert the element in a tree
        vrt.write(self.outfile, encoding="utf8", xml_declaration=True, method="xml")
            
print(Texts2Corpus())