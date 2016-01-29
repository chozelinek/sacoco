# -*- coding: utf-8 -*-

import os
import argparse
import regex as re
# import re # to use regular expressions
import time
# import numpy as np
import fnmatch
from lxml import etree, objectify
import datetime
import pandas as pd
import getpass
import requests
import io
import subprocess

#===============================================================================
# Function to time functions
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
        
#===============================================================================
# Class if needed
#===============================================================================


class WebLichtWrapper(object):
    """Extract recipes from rezeptewikiorg XML dump and produces a TEI/DTABf file.
    
    """

    @timeit
    def __init__(self):
        self.tcf = 'http://www.dspin.de/data/textcorpus'
        self.url = 'https://weblicht.sfs.uni-tuebingen.de/WaaS/api/1.0/chain/process'
        self.xml = 'http://www.w3.org/XML/1998/namespace'
        self.log = []
        self.cli()
        self.apikey = getpass.getpass('Enter your API key:')
#         self.xmldir = os.path.join(self.outdir,'source','xml')
#         self.metadir = os.path.join(self.outdir,'metadata')
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)
        self.main() # function running in the background
        
    def __str__(self):
        message = ["Guten Appetit!"]
        return " ".join(message)
    
    # Function to get all files in a directory
    def get_files(self, directory, fileclue):
        matches = []
        for root, dirnames, filenames in os.walk(directory):
            for filename in fnmatch.filter(filenames, fileclue):
                matches.append(os.path.join(root, filename))
        return matches
    
    def read_xml(self,infile):
        """Parse the XML file."""
        parser = etree.XMLParser(remove_blank_text=True,encoding="utf-8")
        with open(infile, encoding='utf-8',mode='r') as input:
            return etree.parse(input, parser)
        
    def deprettyfy(self,tree):
        # tree to string
        tree = etree.tostring(tree, encoding="utf-8", method="xml")
        tree = tree.decode('utf-8')
        tree = re.sub(r"(\n) +(<)", r"\1\2", tree)
        tree = re.sub(r"> *<", r">\n<", tree)
        tree = re.sub(r"\n\n+", r"\n", tree)
        tree = etree.fromstring(tree)
        tree = etree.ElementTree(tree)
        return tree
    
    def serialize(self,tree,outdir,outfile):
        outpath = os.path.join(outdir,outfile+'.vrt')
        tree.write(outpath, xml_declaration=True, encoding='utf-8')
        pass
    
    def weblichtfy(self,element):
        multiple_files = {'chains': open(self.chain, 'rb'),
                          'content': element.text,
                          'apikey': self.apikey}
        with requests.Session() as s:
            s.mount(self.url,requests.adapters.HTTPAdapter(max_retries=5))
            r = s.post(self.url, files = multiple_files, timeout=(5.0, 10.00),allow_redirects = True)
        if r.status_code == 200:
            output = etree.ElementTree(etree.fromstring(r.content))
        else:
#             print(r.status_code, r.content, r.headers, r.request.headers)
            print('Error {}: {}'.format(r.status_code, r.content.decode()))
            output = False
#             output = None
        return output
    
    def get_word(self,tcf,token_id):
        word = tcf.xpath('//x:token[@ID="{}"]'.format(token_id),namespaces = {'x':self.tcf})[0].text
        return word
    
    def get_lemma(self,tcf,token_id):
        lemma = tcf.xpath('//x:lemma[@tokenIDs="{}"]'.format(token_id),namespaces = {'x':self.tcf})[0].text
        return lemma
    
    def get_pos(self,tcf,token_id):
        pos = tcf.xpath('//x:tag[@tokenIDs="{}"]'.format(token_id),namespaces = {'x':self.tcf})[0].text
        return pos
    
    def get_norm(self,tcf,token_id):
        pass
    
    def transform(self,tcf,p):
        sentences = tcf.xpath('//x:sentence', namespaces = {'x':self.tcf})
        for sentence in sentences:
            token_ids = sentence.attrib['tokenIDs'].split(' ')
            new_sentence = etree.SubElement(p,'s')
            tokens = []
            for token_id in token_ids:
                word = self.get_word(tcf,token_id)
                pos = self.get_pos(tcf, token_id)
                lemma = self.get_lemma(tcf, token_id) 
#                 norm = self.get_norm(tcf, token_id)
                tokens.append([
                               word,
                               pos,
                               lemma,
#                                norm
                               ])
            tokens = '\n'.join(['\t'.join(x) for x in tokens])
            new_sentence.text = '\n'+tokens+'\n'
        pass
    
    def tcf2vrt(self,tcf):
        """Converts TCF ElementTree into VRT"""
        p = etree.Element(self.element)
        self.transform(tcf, p)
        return p
    
    def remove_namespaces(self, tree):
        for elem in tree.getiterator():
            if not hasattr(elem.tag, 'find'): continue  # (1)
            i = elem.tag.find('}')
            if i >= 0:
                elem.tag = elem.tag[i+1:]
        objectify.deannotate(tree, cleanup_namespaces=True)
        etree.strip_attributes(tree, '{}id'.format('{'+self.xml+'}'))
        pass
    
    def main(self):
        # get all input files
        infiles = self.get_files(self.indir, '*.xml')
        for infile in infiles:
            # parse file
            text_id = os.path.splitext(os.path.basename(infile))[0]
            inxml = self.read_xml(infile)
            outxml = etree.Element('text',id=text_id)
            # strip namespaces
            self.remove_namespaces(inxml)
            # find elements containing text to be processed
            elements = inxml.xpath('//div//{}'.format(self.element))
            for i, element in enumerate(elements):
                tcf = self.weblichtfy(element)
                tries = 10
                while tcf == False and tries > 0:
                    tcf = self.weblichtfy(element)
                    tries -= 1
                if tcf == False:
                    print('Chunk {} in {} could not be processed!'.format(i, text_id))
                    self.log.append((text_id,i))
                else:
                    vrt = self.tcf2vrt(tcf)
                    outxml.append(vrt)
            outxml = self.deprettyfy(outxml)
            self.serialize(outxml, self.outdir, text_id)
            nerrors = self.log.count(text_id)
            if nerrors > 0:
                print(text_id,nerrors)
            else:
                print(text_id)
#             os.remove(infile)
        print('Error log:',sorted(set(self.log)))
        pass
        
    def cli(self):
        """CLI parses command-line arguments"""
        parser = argparse.ArgumentParser()
        parser.add_argument("-i","--input", default='test/contemporary/tei', help="input directory.")
        parser.add_argument("-o","--output", default='test/contemporary/vrt', help="output directory.")
        parser.add_argument("-c","--chain", required = True, help = "chain file.")
        parser.add_argument("-e","--element", default='p', help = "tag of the element to be processed by WebLicht.")
        args = parser.parse_args()
        self.indir = args.input
        self.outdir = args.output
        self.chain = args.chain
        self.element = args.element
        pass
             
print(WebLichtWrapper())