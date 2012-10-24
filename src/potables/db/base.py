from sqlalchemy.orm import Query

import logging
logging.basicConfig()
logging.getLogger('db.base').setLevel(logging.DEBUG)
logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)

class BaseQuery(Query):
    def get_sid(self, sid):
        return self.filter_by(sid = sid).first()
        
class BaseModel(object):
    __query_cls__ = BaseQuery

    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        cls.query_master.session.add(obj)
        return obj

    def update(self, **kwargs):
        self.__dict__.update(**kwargs)

    def delete(self, **kwargs):
        self.__class__.query_master.session.delete(self)

