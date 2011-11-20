#!/usr/bin/python
# -*- coding: utf-8 -*-
# http://docs.disqus.com/developers/export/
import db
import argparse

conn = db.get_db_connection()
cursor = db.get_cursor(conn)

sql = """
        SELECT ua.dst, n.changed, c.comment FROM node n 
        INNER JOIN url_alias ua ON ua.src = CONCAT('node/', n.nid)
        INNER JOIN comments c ON n.nid = c.nid
        WHERE n.status = 1
        ORDER BY n.changed DESC
    """

cursor.execute(sql)
for row in cursor.fetchall():
    print row

conn.close()