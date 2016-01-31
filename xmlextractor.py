# -*- coding: utf-8 -*-

import os
import argparse
import regex as re
# import re # to use regular expressions
import time
import fnmatch
from lxml import etree, objectify
import datetime
import pandas as pd
import sys
import unidecode as ud
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


class WikiExtractor(object):
    """Extract metadata and recipes from rezeptewikiorg XML dump.
    
    Produces a CSV file and TEI files respectively.
    """

    @timeit
    def __init__(self):
        self.ns = 'http://www.mediawiki.org/xml/export-0.6/'
        self.xml = 'http://www.w3.org/XML/1998/namespace'
        self.tei = 'http://www.tei-c.org/ns/1.0'
        self.tei_template = 'utils/tei_lite_template.xml'
        self.metadata = {}
        self.licenses = {
                         'Wurm':{'resp':'Andrea Wurm',
                                 'license':'<p>Recipe transcribed by <ref target="mailto:a.wurm@mx.uni-saarland.de">Andrea Wurm</ref> is licensed under a <ref target="http://creativecommons.org/licenses/by/3.0/">Creative Commons Attribution 3.0 Unported License</ref>.</p>'},
                         'Knopf':{'resp':'Katrin Leppert, Kristin Lückel and Thomas Gloning',
                                  'url':'http://www.uni-giessen.de/gloning/tx/1800hakb.htm',
                                  'license':'<p>Recipes of Knopf 1800 based on the transcriptions at <ref target="http://www.uni-giessen.de/gloning/tx/1800hakb.htm">http://www.uni-giessen.de/gloning/tx/1800hakb.htm</ref> by Katrin Leppert, Kristin Lückel and Thomas Gloning are licensed under a <ref target="http://creativecommons.org/licenses/by-nc-sa/3.0/">Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License</ref>.</p>'},
                         'Franckfurt':{'resp':'Silvia Micha, Christina Muth, Mascha Schacht and Thomas Gloning',
                                       'url':'http://www.uni-giessen.de/gloning/tx/1789ffkb.htm',
                                       'license':'<p>Recipes of Franckfurt 1789 based on the transcriptions at <ref target="http://www.uni-giessen.de/gloning/tx/1789ffkb.htm">http://www.uni-giessen.de/gloning/tx/1789ffkb.htm</ref> by Silvia Micha, Christina Muth, Mascha Schacht and Thomas Gloning are licensed under a <ref target="http://creativecommons.org/licenses/by-nc-sa/3.0/">Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License</ref>.</p>'},
                         'Graz':{'resp':'Thomas Gloning',
                                 'url':'http://www.uni-giessen.de/gloning/tx/graz2.htm',
                                 'license':'<p>Recipes of Grätz 1686 based on the transcriptions at <ref target="http://www.uni-giessen.de/gloning/tx/graz2.htm">http://www.uni-giessen.de/gloning/tx/graz2.htm</ref> by Thomas Gloning are licensed under a <ref target="http://creativecommons.org/licenses/by-nc-sa/3.0/">Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License</ref>.</p>'}
                         } # info about the licenses applying to each source, ideally license statement for TEI template
        self.cli()
        for odir in [self.xmldir,self.metadir]:
            if not os.path.exists(odir):
                os.makedirs(odir)
        self.main() # function running in the background
        
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
    
    def strip_nodes(self,tree,nodes):
        for node in nodes:
            xslt_strip_nodes = etree.XML('''
            <xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="node()|@*" >
       <xsl:copy>
          <xsl:apply-templates select="node()|@*" />
       </xsl:copy>
    </xsl:template>
    <xsl:template match="//{}" >
       <xsl:apply-templates/>
    </xsl:template>
    </xsl:stylesheet>
            '''.format(node))
            transform = etree.XSLT(xslt_strip_nodes)
#             try:
#                 result = transform(result)
#             except:
            result = transform(tree)
        return result

    def serialize(self,tree,infile):
        outpath = os.path.join(self.outdir,infile+'.vrt')
        tree.write(outpath, xml_declaration=True, encoding='utf-8')
        pass
    
    def add_text_mixed(self,parent,s):
        if len(parent) == 0:
            parent.text = (parent.text or "") + '\n' + s
        else:
            youngest = parent[-1]
            youngest.tail = (youngest.tail or "") + '\n' + s
        pass
    
    def clean_tree(self,tree,fbasename):
        output = self.strip_nodes(tree)
        root = output.getroot()
        for attribute in root.attrib:
            if attribute != 'id':
                del root.attrib[attribute]
        return output
    
    def cleaninputxml(self,element):
        # strip the subelements but keep text
        simplified = self.strip_nodes(element,['seg'])
        
        # strip lines
        text = simplified.xpath('//{}'.format(element.tag))[0].text
        text = text.strip()
        # split by lines
        text = text.split('\n')
        # for each line keep only first field (word form)
        text = [re.sub(r'^(.+?)\t.+',r'\1',x) for x in text]
        # join separating with white spaces
        text = ' '.join(text)
        return text
    
    def get_preparation(self,revision):
        """Get the preparation section of a particular revision.
        
        It takes a revision element as input. It returns a string.
        """
        title = revision.xpath('//title')
        if len(title) > 0:
            title = self.cleaninputxml(title[0])
        else:
            title = ""
        preparation = revision.xpath('//body')[0]
        preparation = self.cleaninputxml(preparation)
        return title, preparation
    
    def add_text_id(self,tei,text_id):
        """Add the id attribute to the text element of a TDABf."""
        text = tei.xpath('//x:text', namespaces = {'x':self.tei})[0]
        text.set('{}id'.format('{'+self.xml+'}'),text_id)
        pass
    
    def add_divs(self,tei,title,preparation):
        """Add the div, head, p and lb to the body element of a TDABf."""
        # get the body element
        body = tei.xpath('//x:body',namespaces = {'x':self.tei})[0]
        # append the first division type recipe
        div1 = etree.SubElement(body,'div',attrib={'n':'1','type':'recipe'})
        # add the first header as title
        head1 = etree.SubElement(div1,'head')
        head1.text = title
        # check if there are subdivisions
        # add the first paragraph
        preparation = re.sub(r'\n',r' ',preparation)
#             preparation = re.sub(r'\n',r'<lb/>',preparation)
        p1 = etree.fromstring('<p>'+preparation+'</p>')
        div1.append(p1)
        # add the string as the content of the first paragraph
#             p1.text = '\n'+preparation+'\n'
        pass
    
    def generate_text(self,tei,title,text_id,preparation):
        """Create the text element of a TEI file."""
        # add text id
        self.add_text_id(tei, text_id)
        # add div, div n, div type
        self.add_divs(tei, title, preparation)
        pass
    
    def generate_teiheader(self,tei,title,source):
        # add title
        title_element = tei.xpath('//x:title', namespaces = {'x':self.tei})[0]
        title_element.text = title
        # add authors
        resp_element = tei.xpath('//x:name', namespaces = {'x':self.tei})[0]
        source_element = tei.xpath('//x:sourceDesc/x:p', namespaces = {'x':self.tei})[0]
        license_element = tei.xpath('//x:availability/x:p', namespaces = {'x':self.tei})[0]
        if source in self.licenses:
            resp_element.text = self.licenses[source]['resp']
            source_element.text = self.licenses[source]['url']
            license = license_element.getparent()
            license.remove(license_element)
            license_content = etree.fromstring(self.licenses[source]['license'])
            license.append(license_content)
        else:
            resp_element.text = self.licenses['Wurm']['resp']
            license = license_element.getparent()
            license.remove(license_element)
            license_content = etree.fromstring(self.licenses['Wurm']['license'])
            license.append(license_content)
        pass
    
    def create_tei(self,title,text_id,preparation,source):
        """Create a TEI lite file from a wiki recipe."""
        # get the template
        tei = self.read_xml(self.tei_template)
        # teiHeader
        self.generate_teiheader(tei,title,source)
        # generate text
        self.generate_text(tei,title,text_id,preparation)
        teiasstring = etree.tostring(tei,encoding='utf-8').decode()
        teiasstring = re.sub(r'><',r'>\n<',teiasstring)
        parser = etree.XMLParser(remove_blank_text=True)
        otei = etree.ElementTree(etree.XML(teiasstring,parser))
        otei.write(os.path.join(self.xmldir,text_id+'.xml'),encoding='utf-8',pretty_print=True,xml_declaration=True)
        return(otei)
    
    def add_metadata(self,text_id,title,source,year):
        """Add metadata instances to a data structure."""
        collection = 'historical'
        decade = str((int(year)//10)*10)
        def get_period(year):
            p1 = year[:2]
            p2 = year[2:]
            if int(p2) < 50:
                p2 = '00'
            elif int(p2) >= 50:
                p2 = '50'
            return p1+p2
        period = get_period(year)
        self.metadata[text_id] = {
                                              'title':title,
                                              'year':year,
                                              'decade':decade,
                                              'period':period,
                                              'source':source,
                                              'collection':collection
                                              }
        pass
    
    def extract_info(self,text_id):
        source, year, id = text_id.split('_')
        text_id = ud.unidecode(source).lower()+'_'+id
        return(text_id,source,year)
    
    def create_metadata(self):
        outpath = os.path.join(self.metadir,'historical-metadata.csv')
        df = pd.DataFrame(self.metadata).transpose()
        df.to_csv(outpath, sep = '\t')
        pass
    
    def main(self):
        # open wikidump file
        self.infiles = self.get_files(self.indir, '*.vrt')
        self.total = len(self.infiles)
        self.success = 0
        for infile in self.infiles:
            file_id = os.path.splitext(os.path.basename(infile))[0]
            print(file_id)
            inxml = self.read_xml(infile)
            # clean the preparation and get the title
            title, preparation = self.get_preparation(inxml)
            # get info from file name: text_id, source, year, subid
            text_id,source,year = self.extract_info(file_id)
#             # for tei: title in tei header, author, availability (license), sourceDesc, div/head/p
            tei = self.create_tei(title,text_id,preparation,source)
            self.add_metadata(text_id,title,source,year)
            self.success += 1
        # save metadata
        self.create_metadata()
        pass
        
    def cli(self):
        """CLI parses command-line arguments"""
        parser = argparse.ArgumentParser()
        parser.add_argument("-i","--input", help="path to the input folder.")
        parser.add_argument("-x","--xml", help="output directory for TEI/XML files.")
        parser.add_argument("-m","--meta", help="output directory for the metadata file.")
        args = parser.parse_args()
        noneargs = [x for x in args.__dict__.values()].count(None)
        if noneargs == 3:
            print("Running in test mode!")
            self.indir ='test/historical/source'
            self.xmldir ='test/historical/tei'
            self.metadir ='test/metadata'
        elif noneargs < 3 and noneargs > 0:
            options = ["'-"+k[0]+"'" for k,v in args.__dict__.items() if v == None]
            options = ', '.join(options)
            exit_message = '\n'.join(["You forgot option(s): {}".format(options),
                                     "Provide no option to run in test mode: 'python3 {}'".format(os.path.basename(__file__)),
                                     "Get help with option '-h': 'python3 {} -h'".format(os.path.basename(__file__))]
                                     )
            sys.exit(exit_message)
        else:
            self.indir = args.input
            self.xmldir = args.xml
            self.metadir = args.meta
        pass
             
print(WikiExtractor())