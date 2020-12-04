from flask import Blueprint,request,redirect,jsonify,make_response ,render_template
from common.libs.Help import ops_render,iPagination,getCurrentDate
from application import app ,db
from common.libs.UrlManager import UrlManager
from common.models.pay.PayOrderItem import PayOrderItem
from common.models.pay.PayOrder import PayOrder
from common.models.food.food import Food



route_production = Blueprint( 'production_page',__name__ )


@route_production.route("/show",methods = ["GET",])
def show():


    pay_order_info = PayOrder.query.filter_by(status = -6).first()
    id  = pay_order_info.id
    PayOrderItem_info = PayOrderItem.query.filter_by(pay_order_id =id ).all()
    list_1 = []
    for item in PayOrderItem_info:
        food_info = Food.query.filter_by(id =item.food_id).first()
        tmp_data = {
                    'name': food_info.name,
                    }
        list_1.append (tmp_data)

    return render_template( "production/show.html" ,list_1 =list_1 )


@route_production.route("/set",methods = ["POST",])
def set():
    resp = {'code': 200, 'msg': '操作成功~~', 'data': {}}
    req = request.values
    qrcode_id  = req.get("qrcode_id", '')
    camera_id = int(req.get("camera_id", 0))
    if camera_id < 1:
            resp = {'code': -1, 'msg': '摄像头数据错误~~', 'data': {}}
            return  (resp)
    # if qrcode_id <1:
    #     #         resp = {'code': -1, 'msg': '二维码数据错误~~', 'data': {}}
    #     #         return (resp)
    if camera_id == 1:
        pay_order_info = PayOrder.query.filter_by(qrcode_id=qrcode_id).first()
        pay_order_info.status = -5
        pay_order_info.express_status = -5
        pay_order_info.updated_time = getCurrentDate()
        db.session.add(pay_order_info)
        db.session.commit()
        return (resp)


    if camera_id ==2:

        pay_order_info = PayOrder.query.filter_by(qrcode_id=qrcode_id).first()
        pay_order_info.status = -3
        pay_order_info.express_status = -3
        pay_order_info.updated_time = getCurrentDate()
        db.session.add(pay_order_info)
        db.session.commit()
        return(resp)