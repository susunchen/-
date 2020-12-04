# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.schema import FetchedValue



from application import db


class Image(db.Model):



    __tablename__ = 'images'

    id = Column(Integer, primary_key=True)
    file_key = Column(String(60), nullable=False, server_default=FetchedValue())
    created_time = Column(DateTime, nullable=False, server_default=FetchedValue())
