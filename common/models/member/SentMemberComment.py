# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.schema import FetchedValue
from application import db


class SentMemberComment(db.Model):
    __tablename__ = 'sent_member_comments'

    id = db.Column(db.Integer, primary_key=True)
    sent_member_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    member_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    pay_order_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    order_sn = db.Column(db.String(40, 'utf8_bin'), nullable=False, server_default=db.FetchedValue())
    score = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
