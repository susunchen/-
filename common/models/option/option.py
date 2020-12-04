# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.schema import FetchedValue
from application import db
from application import app


class Option(db.Model):
    __tablename__ = 'option'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue())
    nodeId = db.Column(db.String(50), nullable=True, server_default=db.FetchedValue())
    deviceId = db.Column(db.String(50), nullable=False, server_default=db.FetchedValue())
    option_type = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    option_id = db.Column(db.Integer, nullable=False, unique=False, server_default=db.FetchedValue())
    hall_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    work_status = db.Column(db.String(10), nullable=True, server_default=db.FetchedValue())
    note = db.Column(db.String(50), nullable=True, server_default=db.FetchedValue())
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())


    @property
    def option_type_desc(self):
        if self.option_type==0:
            return "未定义"

        return app.config['OPTION_TYPE_MAPPING'][str(self.option_type)]