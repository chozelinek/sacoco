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
        cuisines = [
                    "Deutsche Küche",
                    "Badische Küche",
                    "Bayerische Küche",
                    "Berliner Küche",
                    "Brandenburger Küche",
                    "DDR-Küche",
                    "Deutscher Käse",
                    "Hamburger Küche",
                    "Hessische Küche",
                    "Mecklenburger Küche",
                    "Moselländische Küche",
                    "Niedersächsische Küche",
                    "Pfälzer Küche",
                    "Rheinische Küche",
                    "Saarländische Küche",
                    "Sachsen-Anhalter Küche",
                    "Sächsische Küche",
                    "Schleswig-Holsteinische Küche",
                    "Schwäbische Küche",
                    "Thüringer Küche",
                    "Westfälische Küche",
                    "Maultaschen",
                    "Fränkische Küche",
                    "Currywurst",
                    "Grünkohl",
                    "Friesische Küche",
                    "Fryslâns Küche‎",
                    "Groninger Küche‎",
                    "Hamburger Küche",
                    "Quiche",
                    "Erzgebirgische Küche",
                    "Spätzle‎",
                    "Österreichische Küche",
                    "Burgenländische Küche",
                    "Kärntner Küche",
                    "Niederösterreichische Küche",
                    "Mostviertler Küche",
                    "Waldviertler Küche",
                    "Weinviertler Küche",
                    "Oberösterreichische Küche",
                    "Innviertler Küche",
                    "Linzer Küche",
                    "Mühlviertler Küche",
                    "Salkammergut Küche",
                    "Österreichischer Käse",
                    "Salzburger Küche",
                    "Salkammergut Küche",
                    "Steirische Küche",
                    "Tiroler Küche",
                    "Ost- und Nordtiroler Küche",
                    "Südtiroler Küche",
                    "Vorarlberger Küche",
                    "Wiener Küche",
                    "Schweizer Küche",
                    "Appenzeller Küche",
                    "Genfer Küche",
                    "Glarner Küche",
                    "Graubündner Küche",
                    "Tessiner Küche",
                    "Waadtländer Küche",
                    "Walliser Küche",
                    ]
        self.isgermancuisine = re.compile(r'\[\[Kategorie:({})\]\]'.format('|'.join(cuisines)))
        self.cli()
#         self.teidir = os.path.join(self.xmldir,'source','tei')
#         self.xmldir = os.path.join(self.outdir,'source','xml')
#         self.metadir = os.path.join(self.outdir,'metadata')
        for odir in [self.xmldir,self.metadir]:
#         for odir in [self.teidir,self.xmldir,self.metadir]:
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
    
    def strip_nodes(self,tree):
        for node in self.nodes:
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
            try:
                result = transform(result)
            except:
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
    
    def get_all_nodes(self,tree):
        nodes = tree.findall('.//*')
        self.nodes = set(x.tag for x in nodes)
#         self.nodes.add(tree.getroot().tag)
        pass
    
    def clean_tree(self,tree,fbasename):
        output = self.strip_nodes(tree)
        root = output.getroot()
        for attribute in root.attrib:
            if attribute != 'id':
                del root.attrib[attribute]
        return output
    
    def get_newest_revision(self,page):
        """Get the newest revision for a wiki page.
        
        It takes a page element as input. It returns a revision element.
        
        get_newest_revision(page)
        """
        date_format = "%Y-%m-%dT%H:%M:%SZ"
        all_timestamps = page.xpath('.//x:timestamp', namespaces = {'x':self.ns})
        newest_date = max([datetime.datetime.strptime(x.text, date_format) for x in all_timestamps]).strftime(date_format)
        year = re.match(r'(\d{4})-', newest_date).group(1)
        for timestamp in all_timestamps:
            if timestamp.text == newest_date:
                return(timestamp.getparent(),year)
            
    def get_title(self,page):
        """Get the title of a particular revision.
        
        It takes a page element as input. It returns a string.
        """
        title = page.xpath('./x:title', namespaces = {'x':self.ns})[0].text
        return(title)
    
    def get_preparation(self,revision):
        """Get the preparation section of a particular revision.
        
        It takes a revision element as input. It returns a string.
        """
        text = revision.xpath('./x:text', namespaces = {'x':self.ns})[0].text
        getpreparation = re.compile(r'== Zubereitung ==\n(.+?)\n== ', re.DOTALL)
        preparation = getpreparation.search(text)
        if preparation == None:
            return(None)
        else:
            preparation = preparation.group(1)
        return(preparation)
    
    def clean_preparation(self, preparation):
        """Cleans preparation section.
        
        It takes as input and returns a string.
        """
        preparation = re.sub(r'\* ?',r'',preparation)
        preparation = re.sub(r'\[+.+?:.+?\|(.+?)\]+',r'\1',preparation)
        preparation = re.sub(r"''",r'"',preparation)
        preparation = re.sub(r'\[+.+?\|(.+?)\]+',r'\1',preparation)
        preparation = re.sub(r'\[+(.+?)\]+',r'\1',preparation)
        preparation = re.sub(r'\[+.+?:.+?\|(.+)\}+', r'\1', preparation)
        preparation = re.sub(r'\[+.+?:.+?\|',r'',preparation)
        preparation = re.sub(r'\{+Zubereitung:.+?\|(.+?)\]+',r'\1',preparation)
        preparation = re.sub(r'\(?Zubereitung:.+?\|(.+?)\]+',r'\1',preparation)
        preparation = re.sub(r'(\{\{B\|1\|2)\]\]',r'\1}}',preparation)
        preparation = re.sub(r' .+?\|(.+?)\]+',r'\1', preparation)
        preparation = re.sub(r'\]+',r'',preparation)
        preparation = re.sub(r'(\{+.+?)\)\)',r'\1}}',preparation)
        preparation = re.sub(r'\{\{Grad\|(.+?)\}\}',r'\1 °C',preparation)
        preparation = re.sub(r'\{\{G\|(.+?)\}\}',r'\1 °C',preparation)
        preparation = re.sub(r'\{{(Unterhitze|Alkohol|Umluft|Umbruch|Oberhitze|Grill|OberUnterhitze)\}\}',r'',preparation)
        preparation = re.sub(r'\{+B\|1\|3\}+',r'1/3', preparation)
        preparation = re.sub(r'\{+B\|3\|8\}+',r'3/8', preparation)
        preparation = re.sub(r'\{+B\|1\|8\}+',r'1/8',preparation)
        preparation = re.sub(r'\{+B\|1\|2\}+',r'1/2',preparation)
        preparation = re.sub(r'\{+B\|2\|3\}+',r'2/3',preparation)
        preparation = re.sub(r'\{+B\|4\|5\}+',r'4/5',preparation)
        preparation = re.sub(r'\{+B\|1\|4\}+',r'1/4',preparation)
        preparation = re.sub(r'\{+B\|3\|4\}+',r'3/4',preparation)
        preparation = re.sub(r'<sup>1</sup>/<sub>2</sub>',r'1/2',preparation)
        preparation = re.sub(r'<sup>1</sup>∕<sub>4</sub>',r'1/4',preparation)
        preparation = re.sub(r'<br.*?>',r'',preparation)
        preparation = re.sub(r'<Center>.+?</Center>',r'',preparation,flags=re.DOTALL)
        preparation = re.sub(r'<div align.+?>.+?</div>',r'',preparation,flags=re.DOTALL)
        preparation = re.sub(r'<span style="color:#ff0000">(.+?)</span>',r'\1',preparation)
        preparation = re.sub(r'&nbsp;',r' ',preparation)
        preparation = re.sub(r'^ +',r'',preparation,flags=re.MULTILINE)
        preparation = re.sub(r'\n\n+',r'\n',preparation)
        preparation = re.sub(r' +\n',r'\n',preparation)
        preparation = re.sub(r'<!--.+?-->',r'',preparation)
        preparation = re.sub(r'<!-- Verborgen, siehe Diskussionsseite',r'',preparation)
        preparation = re.sub(r'<[g|G]allery.*?>.+?</[g|G]allery>',r'',preparation, flags = re.DOTALL)
        preparation = re.sub(r'\p{Zs}',r' ',preparation)
        preparation = re.sub(r'\n\n+',r'\n',preparation)
        preparation = re.sub(r'&',r'&amp;',preparation)
        preparation = re.sub(r'  +',r' ',preparation)
        preparation = re.sub(r'==Bilder==',r'',preparation)
        preparation = preparation.strip()
        return(preparation)
    
    def get_page_id(self, page):
        page_id = page.xpath('./x:id', namespaces = {'x':self.ns})[0].text
        return(page_id)
    
    def get_revision_id(self, revision):
        revision_id = revision.xpath('./x:id', namespaces = {'x':self.ns})[0].text
        return(revision_id)
    
    def get_ingredients(self, revision):
        text = revision.xpath('./x:text', namespaces = {'x':self.ns})[0].text
        getingredients = re.compile(r'== Zutaten ==\n(.+?)\n== ', re.DOTALL)
        ingredients = getingredients.search(text)
        if ingredients == None:
            return('')
        else:
            ingredients = re.findall(r'\[\[Zutat:(.+?)\|.+?\]\]',ingredients.group(1))
            ingredients = [re.sub(r'\[+.+?:',r'',x) for x in ingredients]
            ingredients = [re.sub(r'(.+?)\]+',r'\1',x) for x in ingredients]
            ingredients = set(ingredients)
            return(ingredients)
    
    def get_tools(self, revision):
        text = revision.xpath('./x:text', namespaces = {'x':self.ns})[0].text
        gettools = re.compile(r'== Kochgeschirr ==\n(.+?)\n== ', re.DOTALL)
        tools = gettools.search(text)
        if tools == None:
            return('')
        else:
            tools = re.findall(r'\[\[Zubereitung:(.+?)\|.+?\]\]',tools.group(1))
            tools = set(tools)
            return(tools)
    
    def get_methods(self, preparation):
        getmethods = re.compile(r'\[\[Zubereitung:(.+?)\|.+?\]\]')
        methods = getmethods.findall(preparation)
        methods = set(methods)
        return(methods)
    
    def get_authors(self, page):
        authors = page.xpath('.//x:contributor/x:username', namespaces = {'x':self.ns})
        authors = [x.text for x in authors]
        authors = set(authors)
        return(authors)
    
    def add_text_id(self,tei,revision_id):
        """Add the id attribute to the text element of a TDABf."""
        text_id = 'wiki_'+revision_id
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
        hassubdivisions = re.search(r'==+',preparation)
        if hassubdivisions == None:
            # add the first paragraph
            preparation = re.sub(r'\n',r' ',preparation)
#             preparation = re.sub(r'\n',r'<lb/>',preparation)
            p1 = etree.fromstring('<p>'+preparation+'</p>')
            div1.append(p1)
            # add the string as the content of the first paragraph
#             p1.text = '\n'+preparation+'\n'
        else:
            # process subdivisions
            preparation = re.sub(r'==+ (.+?) ==+',r'<div n="2" type="contents"><head>\1</head><p>',preparation)
            preparation = re.sub(r'([^>])\n(<div)',r'\1</p></div>\2',preparation)
            preparation = preparation + '</p></div>'
#             if preparation[0] != '<':
#                 preparation = re.sub('.+?</p></div>',r'',preparation)
            preparation = '<text>' + preparation + '</text>'
            preparation = re.sub(r'<text>[^<].+?<div',r'<text><div',preparation,flags=re.DOTALL)
            preparation = re.sub(r'<p>\n',r'<p>',preparation)
            preparation = re.sub(r'\n',r' ',preparation)
#             preparation = re.sub(r'\n',r'<lb/>',preparation)
            preparation = re.sub(r'</head><p><div',r'</head></div><div',preparation)
#             preparation = re.sub(r'<lb/>',r' ',preparation)
            outxml = etree.fromstring(preparation)
            allelements = outxml.xpath('//div')
            for element in allelements:
                div1.append(element)
#         paragraphs = tei.xpath('//x:p',namespaces = {'x':self.tei})
        paragraphs = tei.xpath('//p')
        for p in paragraphs:
            if p.text == None:
                pparent = p.getparent()
                pparent.remove(p)
        pass
    
    def generate_text(self,tei,title,revision_id,preparation):
        """Create the text element of a TEI file."""
        # add text id
        self.add_text_id(tei, revision_id)
        # add div, div n, div type
        self.add_divs(tei, title, preparation)
        pass
    
    def generate_teiheader(self,tei,title,revision_id,authors):
        # add title
        title_element = tei.xpath('//x:title', namespaces = {'x':self.tei})[0]
        title_element.text = title
        # add authors
        author_element = tei.xpath('//x:author', namespaces = {'x':self.tei})[0]
        author_element.text = ', '.join(authors)
        source = tei.xpath('//x:sourceDesc/x:p', namespaces = {'x':self.tei})[0]
        url = 'http://www.kochwiki.org/w/index.php?oldid='+revision_id
        source.text = url
        pass
    
    def create_tei(self,title,revision_id,authors,preparation):
        """Create a TEI lite file from a wiki recipe."""
        # get the template
        tei = self.read_xml(self.tei_template)
        # teiHeader
        self.generate_teiheader(tei,title,revision_id,authors)
        # generate text
        self.generate_text(tei,title,revision_id,preparation)
        teiasstring = etree.tostring(tei,encoding='utf-8').decode()
        teiasstring = re.sub(r'><',r'>\n<',teiasstring)
        parser = etree.XMLParser(remove_blank_text=True)
        otei = etree.ElementTree(etree.XML(teiasstring,parser))
        obasename = 'wiki_'+revision_id
        otei.write(os.path.join(self.xmldir,obasename+'.xml'),encoding='utf-8',pretty_print=True,xml_declaration=True)
        return(otei)
    
    def create_xml(self,tei,revision_id):
        """Create a simplified XML file only containing the text to be processed with WebLicht."""
        for elem in tei.getiterator():
            if not hasattr(elem.tag, 'find'): continue  # (1)
            i = elem.tag.find('}')
            if i >= 0:
                elem.tag = elem.tag[i+1:]
        objectify.deannotate(tei, cleanup_namespaces=True)
        etree.strip_attributes(tei, '{}id'.format('{'+self.xml+'}'))
        content = tei.xpath('./text/body/div')[0]
        text = etree.Element('text', id = 'wiki_'+revision_id)
        text.append(content)
        outpath = os.path.join(self.xmldir,'wiki_'+revision_id+'.xml')
        tree = etree.ElementTree(text)
        tree.write(outpath, encoding = 'utf-8', pretty_print=True, xml_declaration=True)
        pass
    
    def add_metadata(self,revision_id,title,authors,ingredients,tools,methods,year,categories):
        """Add metadata instances to a data structure."""
        def formatasfeature(values):
            if len(values) == 0:
                output = "|"
            else:
                output = "|{}|".format('|'.join(values))
            return output
         
        authors = formatasfeature(authors)
        ingredients = formatasfeature(ingredients)
        tools = formatasfeature(tools)
        methods = formatasfeature(methods)
        categories = formatasfeature(categories)
        source = 'wiki'
        collection = 'contemporary'
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
        self.metadata['wiki_'+revision_id] = {
                                              'title':title,
                                              'year':year,
                                              'decade':decade,
                                              'period':period,
                                              'source':source,
                                              'authors':authors,
                                              'ingredients':ingredients,
                                              'tools':tools,
                                              'methods':methods,
                                              'cuisines':categories,
                                              'collection':collection
                                              }
        pass
    
    def extract_info(self,page,revision,preparation):
        title = self.get_title(page)
        page_id = self.get_page_id(page)
        revision_id = self.get_revision_id(revision)
        authors = self.get_authors(page)
        ingredients = self.get_ingredients(revision)
        tools = self.get_tools(revision)
        methods = self.get_methods(preparation)
        preparation = self.clean_preparation(preparation)
        return(page_id,revision_id,title,authors,ingredients,tools,methods,preparation)
    
    def create_metadata(self):
        outpath = os.path.join(self.metadir,'contemporary-metadata.csv')
        df = pd.DataFrame(self.metadata).transpose()
        df.to_csv(outpath, sep = '\t')
        pass
    
    def main(self):
        # open wikidump file
        inxml = self.read_xml(self.infile)
        all_pages = [x.getparent() for x in inxml.xpath('//x:ns[text()="0"]', namespaces = {'x':self.ns})]
        self.total = len(all_pages)
        self.success = 0
        for page in all_pages:
            if self.isgermancuisine.search(etree.tostring(page, encoding='utf-8').decode()):
                categories = set(self.isgermancuisine.findall(etree.tostring(page, encoding='utf-8').decode()))
                revision, year = self.get_newest_revision(page)
                preparation = self.get_preparation(revision)
                if preparation == None:
                    continue
                else:
                    page_id,revision_id,title,authors,ingredients,tools,methods,preparation = self.extract_info(page,revision,preparation)
                    tei = self.create_tei(title,revision_id,authors,preparation)
#                     xml = self.create_xml(tei,revision_id)
                    self.add_metadata(revision_id,title,authors,ingredients,tools,methods,year,categories)
                    self.success += 1 
        # save metadata
        self.create_metadata()
        pass
        
    def cli(self):
        """CLI parses command-line arguments"""
        parser = argparse.ArgumentParser()
        parser.add_argument("-i","--input", help="path to the input file.")
        parser.add_argument("-x","--xml", help="output directory for TEI/XML files.")
        parser.add_argument("-m","--meta", help="output directory for the metadata file.")
        args = parser.parse_args()
        noneargs = [x for x in args.__dict__.values()].count(None)
        if noneargs == 3:
            print("Running in test mode!")
            self.infile ='test/contemporary/source/rezeptewikiorg-20140325-history.xml'
            self.xmldir ='test/contemporary/tei'
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
            self.infile = args.input
            self.xmldir = args.xml
            self.metadir = args.meta
        pass
             
print(WikiExtractor())