# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.schema import FetchedValue
from application import db
from application import app


class CabintData(db.Model):
    __tablename__ = 'cabint_data'

    id = db.Column(db.Integer, primary_key=True)
    cabint_id = db.Column(db.Integer, nullable=False, index=True, server_default=db.FetchedValue())
    order_sn = db.Column(db.String(40), nullable=False, index=True, server_default=db.FetchedValue())
    action = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
