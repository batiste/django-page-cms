# -*- coding: utf-8 -*-
from pages.utils import get_site_from_request
import settings

class LazySite(object):
    def __get__(self, request, obj_type=None):
        if not hasattr(request, '_cached_site'):
            request._cached_site = get_site_from_request(request)
        return request._cached_site

class CurrentSiteMiddleware(object):

    def process_request(self, request):
        request.__class__.site = LazySite()
        return None

    if settings.SQL_DEBUGGING:
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
