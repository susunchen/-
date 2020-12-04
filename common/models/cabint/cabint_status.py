# coding: utf-8
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.schema import FetchedValue
from application import db
from application import app


class CabintStatu(db.Model):
    __tablename__ = 'cabint_status'

    id = db.Column(db.Integer, primary_key=True)
    cabint_status = db.Column(db.Integer, nullable=False, index=True, server_default=db.FetchedValue())
    status = db.Column(db.Integer, nullable=False, index=True, server_default=db.FetchedValue())
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())

    @property
    def status_desc(self):
            return app.config['STATUS_MAPPING'][str(self.status)]
    @property
    def cabint_status_desc(self):
            return app.config['CABINT_STATUS_MAPPING'][str(self.cabint_status)]