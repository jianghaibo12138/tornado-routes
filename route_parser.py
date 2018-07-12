#!/usr/bin/python
# -*- coding: utf-8 -*-
import re

__author__ = "jianghaibo"


class Parser(object):
    def __init__(self):
        super(Parser, self).__init__()

    def handler_repr(self, cls):
        return re.search("'(.+)'", repr(cls)).groups()[0]

    def parse_routes(self, member, key, routes):
        if not all([hasattr(member, key), isinstance(routes, list)]):
            return
        for i, (route_path, route_params) in enumerate(member.routes):
            route_path.strip('/')
            if not route_params:
                route_params = {}
            if 'url_name' not in route_params:
                route_params['url_name'] = '{}~{}'.format(self.handler_repr(member), i + 1)
            routes.append((route_path, member, route_params))

    def parse_route_path(self, member, key, routes):
        if not all([hasattr(member, key), isinstance(routes, list)]):
            return
        route_path, route_params = member.route_path, member.route_params

        route_path.strip('/')
        if route_params:
            routes.append((route_path, member, route_params))
        else:
            routes.append((route_path, member))

    def parse_rest_route_path(self, member, key, routes):
        if not all([hasattr(member, key), isinstance(routes, list)]):
            return
        route_path, route_params = member.rest_route_path, member.route_params

        route_path.strip('/')
        if route_params:
            routes.append((route_path, member, route_params))
            routes.append((route_path + r'/([0-9]+)', member, route_params))
        else:
            routes.append((route_path, member))
            routes.append((route_path + r'/([0-9]+)', member))
