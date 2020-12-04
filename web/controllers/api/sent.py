
from web.controllers.api import route_api
from common.models.pay.PayOrder import PayOrder
from common.models.food.hall import Hall
from common.libs.Help import getCurrentDate,getFormatDate
from common.models.pay.PayOrderItem import PayOrderItem
from common.models.food.food import Food
from common.models.member.MemberAddress import MemberAddress
from flask import request, jsonify,g
from application import app, db
import json, decimal




@route_api.route("/sent/info", methods=[ "POST" ])
def sentInfo():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}


    sent_order_list =[]
    order_info_list = PayOrder.query.filter_by(status=-7 ).order_by( PayOrder.created_time.desc() ).all()
    if order_info_list:
        for item in order_info_list:
            hall_info = Hall.query.filter_by(id =item.hall_id ).first()
            adress_info = MemberAddress.query.filter_by( id = item.express_address_id,status = 1 ).first()
            food_item = PayOrderItem.query.filter_by(pay_order_id=item.id).all()
            text = ''
            for item2 in food_item:
                food_info = Food.query.filter_by(id=item2.food_id).first()
                text = food_info.name+"+"+text
            tmp_data = {
                'id': item.id,
                'text2': hall_info.name + '--' + adress_info.area_str,
                'text':text

            }

            sent_order_list.append(tmp_data)
    resp['data']['list'] = sent_order_list


    return jsonify(resp)

@route_api.route("/sent/catch", methods=[ "POST" ])
def sentCatch():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    id = int(req.get("id", 0))
    order_info = PayOrder.query.filter_by(id=id).first()
    member_info = g.member_info


    order_info.sent_member_id = int(member_info.id)
    order_info.updated_time = getCurrentDate()
    order_info.status = -6
    db.session.add(order_info)
    db.session.commit()

    return jsonify(resp)