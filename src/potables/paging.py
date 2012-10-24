from sqlalchemy.sql import func
from flask import request
from flask.ext.restful import abort, reqparse
import urllib
import urlparse
import math


parser = reqparse.RequestParser()
parser.add_argument("Page", dest='page', type=int, default=0)
parser.add_argument("PageSize", dest='page_size', type=int, default=50)

def abort_out_of_range():
    abort(400, status=400, message='Out of Range Paging', code=20006)

class ListPaginator(object):

    def __init__(self, data):
        self.args = parser.parse_args()
        self.data = data


    def metadata(self):
        page = self.args['page']
        page_size = self.args['page_size']
        start, stop = self.get_slice()

        total = self.get_total()
        end_offset = stop - 1
        if total - 1 < end_offset:
            end_offset = max(total -1, 0)

        meta = {
            "page": page,
            "page_size": page_size,
            "first_page_uri": self.get_first(),
            "next_page_uri": self.get_next(),
            "previous_page_uri": self.get_prev(),
            "last_page_uri": self.get_last(),
            "start": start,
            "end": end_offset,
            "num_pages": int(math.ceil(self.get_total() / float(page_size))),
            "total": total,
            "uri": self.get_current(),
            }

        return meta

    def page(self):
        start, stop = self.get_slice()
        return self.data[start:stop]

    def get_total(self):
        return len(self.data)

    def get_current(self):
        return self._get_url(paging=False)

    def get_last(self):
        total = self.get_total()
        page_size = self.args['page_size']
        if total <= 1:
            page = 0
        else:
            page = (total - 1) / page_size

        return self._get_url(page=page, page_size=page_size)

    def get_prev(self):
        page_size = self.args['page_size']
        page = self.args['page']
        if page <= 0:
            return None
        return self._get_url(page=page - 1, page_size=page_size)

    def get_next(self):
        count = len(self.page())
        total = self.get_total()
        page_size = self.args['page_size']
        page = self.args['page']

        if count < page_size:
            return None

        if page_size * (page + 1) >= total:
            return None

        return self._get_url(page=page + 1, page_size=page_size)

    def get_first(self):
        return self._get_url(page_size=self.args['page_size'])

    def get_slice(self):
        page = self.args['page']
        page_size = self.args['page_size']
        return page * page_size, (page + 1) * page_size

    def _get_url(self, page=0, page_size=50, paging=True):
        query = urlparse.parse_qsl(request.query_string)
        if paging:
            query.append(("PageSize", page_size))
            query.append(("Page", page))
        query_dict = dict(query)
        query_dict.pop('ext', '')
        query_dict.pop('account_sid', '')
        if not paging:
            query_dict.pop('PageSize', '')
            query_dict.pop('Page', '')
        if self.get_total() == 0:
            return None
        if not query_dict:
            return u"{}".format(request.path)
        url =  u"{}?{}".format(request.path,
            urllib.urlencode(query_dict))
        return url



def cache(func):
    cache_name = '__{}_cache'.format(func.__name__)
    def inner_func(self, *args, **kwargs):
        if not hasattr(self, cache_name):
            result = func(self, *args, **kwargs)
            setattr(self, cache_name, result)
        return getattr(self, '__{}_cache'.format(func.__name__))
    return inner_func


class QueryPaginator(ListPaginator):

    @cache
    def page(self):
        try:
            start, stop = self.get_slice()
            return self.data.slice(start, stop).all()
        except AttributeError:
            return super(QueryPaginator, self).page()

    @cache
    def get_total(self):
        try:
            return self.data.count()
        except (AttributeError, TypeError):
            return super(QueryPaginator, self).get_total()


class EfficientQueryPaginator(QueryPaginator):

    @cache
    def get_total(self):
        try:
            return self.data.with_entities(func.count(1)).scalar()
        except AttributeError:
            return super(EfficientQueryPaginator, self).get_total()
