# -*- coding: utf-8 -*-
from pages.utils import get_site_from_request
import settings

class LogSqlMiddleware(object):
    
    def process_response(self, request, response):
        from django import db
        import logging
        logging.basicConfig(filename="sql_log.txt", level=logging.DEBUG,)
        logging.debug(request.path + " : " + str(len(db.connection.queries)))
        a = []  
        print "SQL requests : %d" % len(db.connection.queries)
        for q in db.connection.queries:
            a.append(q['sql'])
        a.sort()
        for q in a:
            logging.debug(q)
        return response
