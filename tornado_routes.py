# -*- coding: utf-8 -*-
#
# Author: Pavel Reznikov <pashka.reznikov@gmail.com>
#
# Created: 23/01/13
#
# Id: $Id$

from pprint import pformat
import operator
from tornado import web
from tornado.web import URLSpec
import logging
import six

from route_parser import Parser

logger = logging.getLogger(__name__)

__ALL__ = ('make_handlers', 'include', 'route', 'routes',)

route_classes = {}


def route(path, params=None, name=None):
    params = params or {}

    def decorator(cls):
        if repr(cls) in route_classes:
            raise Exception('Cannot bind route "{}" to %s. It already has route to "{}".'
                            .format(path, cls, route_classes[repr(cls)]))
        route_classes[repr(cls)] = path
        cls.route_path = path
        cls.route_params = params
        url_name = params.pop('url_name', name)
        cls.url_name = url_name
        return cls

    return decorator


def routes(*routes):
    def decorator(cls):
        cls.routes = routes
        return cls

    return decorator


def include(module):
    def load_module(m):
        m = m.split('.')
        ms, m = '.'.join(m), m[-1]
        m = __import__(ms, fromlist=[m], level=0)
        return m

    if isinstance(module, six.string_types):
        module = load_module(module)

    p = Parser()

    def parse(member, routes):
        func_dict = {
            'routes': p.parse_routes,
            'route_path': p.parse_route_path,
            'rest_route_path': p.parse_rest_route_path,
        }
        for key in func_dict.keys():
            func_dict.get(key)(member, key, routes)

    routes = []
    for member in dir(module):
        member = getattr(module, member)
        if isinstance(member, type) and issubclass(member, web.RequestHandler):
            parse(member, routes)
    return Handlers(None, routes)


class Handlers(object):

    def __init__(self, prefix, items):
        self.prefix = prefix
        self.items = items

    def get_handler_name(self, handler, r):
        name = getattr(handler, 'url_name', None)
        if name:
            return name
        if hasattr(handler, 'get_url_name'):
            name = handler.get_url_name(*r)
        if name:
            return name
        if len(r) == 3 and 'url_name' in r[2]:
            name = r[2].pop('url_name')
        if name:
            return name
        return Parser().handler_repr(handler)

    def build(self, prefix=None):
        prefix = prefix or self.prefix or ''

        res = []
        for r in self.items:
            if len(r) != 2:
                raise Exception('Url item must be typle which length is 2. Invalid item is {}'.format(r))

            ro = '/' + '/'.join([prefix.strip('/')] + r[0].strip('/').split('/')).strip('/')

            if isinstance(r[1], Handlers):
                res += r[1].build(ro)
            elif isinstance(r[1], six.string_types):
                m = r[1].split('.')
                ms, m, h = '.'.join(m[:-1]), m[-2], m[-1]
                m = __import__(ms, fromlist=[m], level=0)
                handler = getattr(m, h)[0]
                d = {'name': self.get_handler_name(handler, r)}
                d.update(r[2:])
                res.append(URLSpec(ro, handler, **d))
            else:
                handler = r[1:][0]
                d = {'name': self.get_handler_name(handler, r)}
                if len(r) == 3:
                    d['kwargs'] = r[2]
                res.append(URLSpec(ro, handler, **d))

        return res

    def make_handlers(self):
        res = tuple(self.build())

        rr = [(x.regex.pattern, x.handler_class, x.kwargs, x.name) for x in res]
        logger.debug('\n' + pformat(sorted(rr, key=operator.itemgetter(0)), width=200))

        return res
