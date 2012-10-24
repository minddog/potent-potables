from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData
from .. import base

Declarative = declarative_base()

class GameshowQuery(base.BaseQuery):
    pass

class GameshowBase(base.BaseModel):
    pass