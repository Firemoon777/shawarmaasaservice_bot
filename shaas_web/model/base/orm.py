from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class BaseTableNoID(Base):
    __abstract__ = True

    created = Column(DateTime, server_default=func.now())
    updated = Column(DateTime, onupdate=func.now())


class BaseTable(BaseTableNoID):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)