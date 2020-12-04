# coding: utf-8
from sqlalchemy import BigInteger, Column, DateTime, Integer
from sqlalchemy.schema import FetchedValue
from application import db







class QrcodeDate(db.Model):
    __tablename__ = 'qrcode_date'

    id = db.Column(db.Integer, primary_key=True)
    camera_id = db.Column(db.Integer, nullable=False, index=True, server_default=db.FetchedValue())
    qrcode_id = db.Column(db.BigInteger, nullable=False, index=True, server_default=db.FetchedValue())
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
