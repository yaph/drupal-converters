#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import csv
import imp
import os
import re

from datetime import datetime

from logya import allowed_exts
from logya.writer import write_content


# http://stackoverflow.com/a/250373/291931
def smart_truncate(content, length=100, suffix='...'):
    if len(content) <= length:
        return content
    else:
        return ' '.join(content[:length + 1].split(' ')[0:-1]) + suffix


def check_ext(path):
    for e in allowed_exts:
        if path.endswith(e):
            return True
    return False


docs = []
fieldmap = {}
re_ws = re.compile(r'\s+')
re_tag = re.compile(r'<[^<]+?>')

parser = argparse.ArgumentParser(description='node export converter')
parser.add_argument('csv_file', help='Drupal Node export CSV file name')
parser.add_argument('mapping_file', help='File with mapping of Drupal fields to logya fields')
args = parser.parse_args()

mapping = imp.load_source('module.name', args.mapping_file)

dirdst = 'content'
os.makedirs(dirdst, exist_ok=True)

dirtpl = 'templates'
os.makedirs(dirtpl, exist_ok=True)

fcsv = open(args.csv_file, 'rU')
reader = csv.reader(fcsv, quotechar='"', quoting=csv.QUOTE_ALL)
headers = next(reader)

# Determine fields to be converted.
for dfield, lfield in mapping.mapping.items():
    if dfield in headers:
        fieldmap[headers.index(dfield)] = lfield

for row in reader:
    l = len(row)
    doc = {}
    for idx, name in fieldmap.items():
        if idx < l and row[idx]:
            doc[name] = row[idx]

    tags = []
    for t in mapping.tags:
        if t in doc:
            if doc[t]:
                tags += doc[t].lower().split(', ')
            del doc[t]
    doc['tags'] = tags

    if 'path' not in doc or 'nid' not in doc:
        continue

    doc['url'] = '/' + doc['path'].lstrip('/')

    # Append slash if path does not end in allowed file extension.
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
        with open(fnametpl, 'w') as f:
            f.write('')

    if mapping.created in doc and doc[mapping.created]:
        doc[mapping.created] = datetime.fromtimestamp(int(doc[mapping.created]))

    body = doc['body'].strip()
    del doc['body']
    del doc['nid']

    # Remove tokens in body.
    for br in mapping.bodyremoves:
        body = body.replace(br, '')

    # Strip HTML with regex, YES!
    doc['description'] = re.sub(re_tag, '', doc.get('description', ''))

    # Replace multiple white space chars with one space.
    doc['description'] = re.sub(re_ws, ' ', doc['description']).strip()

    # Truncate to 160 chars, about the number Google shows in search results.
    doc['description'] = smart_truncate(doc['description'], length=160, suffix='')

    write_content(dirdst, doc, body)
