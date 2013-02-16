#!/usr/bin/python
# -*- coding: utf-8 -*-
# TODOs
# convert HTML entities? see http://stackoverflow.com/a/12614706/291931
# fix internal links
# make sure all fields are included
import os
import re
import imp
import csv
import yaml
import argparse
import StringIO
from datetime import datetime
from lxml import etree

htmlparser = etree.HTMLParser()

parser = argparse.ArgumentParser(description='node export converter')
parser.add_argument('-f', required=True, help='Drupal Node export CSV file name')
parser.add_argument('-m', required=True, help='File with mapping of Drupal fields to logya fields')
args = parser.parse_args()

def mkdir(name):
    if not os.path.exists(name): os.makedirs(name)

# http://stackoverflow.com/a/250373/291931
def smart_truncate(content, length=100, suffix='...'):
    if len(content) <= length:
        return content
    else:
        return ' '.join(content[:length+1].split(' ')[0:-1]) + suffix

allowed_exts = ['html', 'htm', 'xml', 'json', 'js', 'css', 'php', 'md', 'markdown']
def check_ext(path):
    for e in allowed_exts:
        if path.endswith(e):
            return True
    return False


re_ws = re.compile(r'\s+')
fieldmap = {}
docs = []
mapping = imp.load_source('module.name', args.m)

dirdst = 'content'
mkdir(dirdst)

dirtpl = 'templates'
mkdir(dirtpl)

fcsv = open(args.f, 'rU')
reader = csv.reader(fcsv, quotechar='"', quoting=csv.QUOTE_ALL)
headers = reader.next()

# determine fields to be converted
for dfield, lfield in mapping.mapping.items():
    if dfield in headers:
        fieldmap[headers.index(dfield)] = lfield

for row in reader:
    l = len(row)
    doc = {}
    for idx, name in fieldmap.items():
        if idx < l and row[idx]:
            doc[name] = row[idx].decode('utf-8')

    tags = []
    for t in mapping.tags:
        if t in doc:
            if doc[t]: tags += doc[t].lower().split(', ')
            del doc[t]
    doc['tags'] = tags

    if 'path' not in doc or 'nid' not in doc: continue
    doc['url'] = '/' + doc['path'].lstrip('/')
    # append slash if path does not end in allowed file extension
    if not check_ext(doc['url']):
        doc['url'] = doc['url'].rstrip('/') + '/'

    del doc['path']

    if mapping.template in doc:
        doc['template'] = '%s.html' % doc[mapping.template]
        del doc[mapping.template]
    else:
        doc['template'] = 'default.html'

    fnametpl = os.path.join(dirtpl, doc['template'])
    if not os.path.exists(fnametpl):
        ftpl = open(fnametpl, 'w')
        ftpl.write('')
        ftpl.close()

    if mapping.created in doc and doc[mapping.created]:
        doc[mapping.created] = datetime.fromtimestamp(int(doc[mapping.created]))

    body = doc['body'].strip()
    del doc['body']
    for br in mapping.bodyremoves: body = body.replace(br, '')

    desc = doc['description'].strip()

    # strip HTML
    tree = etree.parse(StringIO.StringIO(desc), htmlparser)
    doc['description'] = etree.tostring(tree.getroot(), encoding=unicode, method='text')

    # replace multiple white space chars with one space
    doc['description'] = re.sub(re_ws, ' ', doc['description'])

    # truncate to 160 chars, about the number Google shows in search results.
    doc['description'] = smart_truncate(doc['description'], length=160, suffix='')

    fname = os.path.join(dirdst, doc['nid'] + '.html')
    del doc['nid']
    fdoc = open(fname, 'w')
    fdoc.write('---\n%s---\n%s' % (yaml.safe_dump(doc), body.encode('utf-8')))
    fdoc.close()

