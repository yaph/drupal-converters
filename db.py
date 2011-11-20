#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import argparse
import MySQLdb

def get_db_connection():
    parser = argparse.ArgumentParser(description='database info')
    parser.add_argument('-d', required=True, help='Database name')
    parser.add_argument('-u', required=True, help='Database user')
    parser.add_argument('-p', required=True, help='Database password')
    parser.add_argument('--host', help='Database host')
    args = parser.parse_args()

    dbname = args.d
    dbuser = args.u
    dbpass = args.p
    dbhost = 'localhost'
    if args.host:
        dbhost = args.host

    try:
        return MySQLdb.connect(dbhost, dbuser, dbpass, dbname);
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit(1)

def get_cursor(conn):
    return conn.cursor(MySQLdb.cursors.DictCursor)