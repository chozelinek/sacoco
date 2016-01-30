# -*- coding: utf-8 -*-

import os
import re # to use regular expressions
import argparse # to parse command-line arguments
import time
import fnmatch
import pandas as pd
from lxml import etree
import sys

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
        parser.add_argument("-i","--input", nargs='+', help="path to the input file.")
        parser.add_argument("-o", "--output", help="target file where to save the output.")
        args = parser.parse_args()
        noneargs = [x for x in args.__dict__.values()].count(None)
        if noneargs == 2:
            print("Running in test mode!")
            self.indirs = ['test/contemporary/meta','test/historical/meta']
            self.outfile = 'test/sacoco.vrt'
        elif noneargs < 2 and noneargs > 0:
            options = ["'-"+k[0]+"'" for k,v in args.__dict__.items() if v == None]
            options = ', '.join(options)
            exit_message = '\n'.join(["You forgot option(s): {}".format(options),
                                     "Provide no option to run in test mode: 'python3 {}'".format(os.path.basename(__file__)),
                                     "Get help with option '-h': 'python3 {} -h'".format(os.path.basename(__file__))]
                                     )
            sys.exit(exit_message)
        else:
            self.indirs = args.input
            self.outfile = args.output
        self.outdir = os.path.split(self.outfile)[0]
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

#     def main(self):
#         input_files = []
#         for folder in self.indirs:
#             input_files += self.get_files(folder, '*.vrt')
#         self.total = len(input_files)
#         self.success = 0
#         corpus = []
#         for file in input_files:
#             tree = self.read_infile(file)
#             text = tree.getroot()
#             sentences = text.xpath('//s')
#             for sentence in sentences:
#                 sentence.text = sentence.text.strip()
#             corpus.append(etree.tostring(text, encoding='utf-8', method='xml').decode())
#             self.success += 1
# 
# #         corpus = etree.tostring(corpus, encoding='unicode', method='xml') # convert the XML tree into a string to manipulate it
# #         corpus = re.sub(r"><", r">\n<", corpus)
# #         corpus = re.sub(r">([^<\n])", r">\n\1", corpus)
# #         corpus = re.sub(r"([^\n])<", r"\1\n<", corpus)
# #         vrt = etree.ElementTree(etree.fromstring(corpus)) # parse the string as an element and convert the element in a tree
# #         vrt.write(self.outfile, encoding="utf8", xml_declaration=True, method="xml")
#         corpus = '\n'.join(corpus)
#         with open(self.outfile, 'w', encoding='utf-8') as outfile:
#             outfile.write(corpus)

    
    def main(self):
        input_files = []
        for folder in self.indirs:
            input_files += self.get_files(folder, '*.vrt')
        self.total = len(input_files)
        self.success = 0
        otree = etree.ElementTree(etree.Element('text'))
        corpus = otree.getroot()
        for file in input_files:
            tree = self.read_infile(file)
            text = tree.getroot()
            corpus.append(text)
            self.success += 1
        sentences = corpus.xpath('//s')
        for sentence in sentences:
            sentence.text = sentence.text.strip()
#         corpus = etree.tostring(corpus, encoding='unicode', method='xml') # convert the XML tree into a string to manipulate it
#         corpus = re.sub(r"><", r">\n<", corpus)
#         corpus = re.sub(r">([^<\n])", r">\n\1", corpus)
#         corpus = re.sub(r"([^\n])<", r"\1\n<", corpus)
#         vrt = etree.ElementTree(etree.fromstring(corpus)) # parse the string as an element and convert the element in a tree
#         vrt.write(self.outfile, encoding="utf8", xml_declaration=True, method="xml")
        corpus = etree.ElementTree(corpus)
        corpus.write(self.outfile, encoding="utf8", xml_declaration=True, method="xml")
            
print(Texts2Corpus())