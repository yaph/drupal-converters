#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import imp
import csv
import yaml
import argparse
from datetime import datetime

parser = argparse.ArgumentParser(description='node export converter')
parser.add_argument('-f', required=True, help='Drupal Node export CSV file name')
parser.add_argument('-m', required=True, help='File with mapping of Drupal fields to logya fields')
args = parser.parse_args()

def mkdir(name):
    if not os.path.exists(name): os.makedirs(name)

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
    doc['url'] = '/%s/' % doc['path'].strip('/')
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
    fname = os.path.join(dirdst, doc['nid'] + '.html')
    del doc['nid']
    fdoc = open(fname, 'w')
    fdoc.write('---\n%s---\n%s' % (yaml.dump(doc), body.encode('utf-8')))
    fdoc.close()

