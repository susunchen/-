from flask import Blueprint,request,redirect,jsonify
from common.libs.Help import ops_render,iPagination,getCurrentDate
from application import app ,db
from common.libs.UrlManager import UrlManager
from common.models.cabint.cabint_status import CabintStatu
from common.models.cabint.cabint_data import CabintData
from common.models.pay.PayOrder import PayOrder
import requests
import json



route_cabint = Blueprint( 'cabint_page',__name__ )




@route_cabint.route( "/index" )
def index():
    resp_data = {}
    req = request.values
    page = int(req['p']) if ('p' in req and req['p']) else 1
    query = CabintStatu.query



    if 'status' in req and int(req['status']) > -1:
        query = query.filter(CabintStatu.status == int(req['status']))


    page_params = {
        'total': query.count(),
        'page_size': app.config['PAGE_SIZE'],
        'page': page,
        'display': app.config['PAGE_DISPLAY'],
        'url': request.full_path.replace("&p={}".format(page), "")
    }

    pages = iPagination(page_params)
    offset = (page - 1) * app.config['PAGE_SIZE']
    list = query.order_by(CabintStatu.id.desc()).offset(offset).limit(app.config['PAGE_SIZE']).all()




    resp_data['list'] = list
    resp_data['pages'] = pages
    resp_data['search_con'] = req
    resp_data['cabint_status_mapping'] = app.config['CABINT_STATUS_MAPPING']
    resp_data['status_mapping'] = app.config['STATUS_MAPPING']
    resp_data['current'] = 'index'






    return ops_render("cabint/index.html", resp_data)

@route_cabint.route( "/ops",methods = [ "POST" ] )
def ops():
    resp = {'code': 200, 'msg': '操作成功~~', 'data': {}}
    req = request.values

    id = req['id'] if 'id' in req else 0
    act = req['act'] if 'act' in req else ''
    if not id:
        resp['code'] = -1
        resp['msg'] = "请选择要操作的柜子~~"
        return jsonify(resp)

    if act not in ['remove', 'recover']:
        resp['code'] = -1
        resp['msg'] = "操作有误，请重试~~"
        return jsonify(resp)

    cabint_info = CabintStatu.query.filter_by(id=id).first()
    if not cabint_info:
        resp['code'] = -1
        resp['msg'] = "指定柜子不存在~~"
        return jsonify(resp)

    if act == "remove":
        cabint_info.status = 0
    elif act == "recover":
        cabint_info.status = 1

        cabint_info.update_time = getCurrentDate()
    db.session.add(cabint_info)
    db.session.commit()
    return jsonify(resp)

@route_cabint.route( "/choose" ,methods = [ "POST" ])# 需要添加参数有效性验证
def choose():

    while True:
        resp = {'code': 200, 'msg': '操作成功~~', 'data': {}}
        req = request.values
        qrcode_id = req['qrcode_id'] if 'qrcode_id' in req and req['qrcode_id'] else ""
        pay_order_info = PayOrder.query.filter_by(qrcode_id=qrcode_id).first()
        cabint_info =  CabintStatu.query.filter_by(cabint_status=1,status = 1).first()
        cabint_id = cabint_info.id
        url_1 = 'http://172.26.186.171:9888/check'
        data = {
            'cabint_id': cabint_id
        }
        response = requests.post(url_1, data=data)
        res = json.loads(response.text)
        if res['code'] != 200:
            cabint_info.status = 0
            cabint_info.updated_time = getCurrentDate()
            db.session.add(cabint_info)
            db.session.commit()
        if res['code'] == 200:
            pay_order_info.cabint_id = cabint_id
            pay_order_info.status = -4
            db.session.add(pay_order_info)
            # db.session.commit()

            model_cabintDate = CabintData()
            model_cabintDate.cabint_id = cabint_id
            model_cabintDate.order_sn = pay_order_info.order_sn
            model_cabintDate.created_time = getCurrentDate()
            db.session.add(model_cabintDate)
            # db.session.commit()

            cabint_info.cabint_status = 0
            cabint_info.updated_time = getCurrentDate()
            db.session.add(cabint_info)
            db.session.commit()

            resp['data']['cabint_id'] = cabint_id
            return jsonify(resp)









@route_cabint.route( "/confirm" ,methods = [ "POST" ])# 需要添加参数有效性验证，改变订单状态
def confirm():
    resp = {'code': 200, 'msg': '操作成功~~', 'data': {}}
    req = request.values
    qrcode_id = int(req['qrcode_id']) if 'qrcode_id' in req and req['qrcode_id'] else 0
    cabint_id = int(req['cabint_id']) if 'cabint_id' in req and req['cabint_id'] else 0

    order_list = PayOrder.query.filter_by( qrcode_id = qrcode_id).first()
    order_list.status = -4
    order_list.updated_time = getCurrentDate()
    order_list.cabint_id = cabint_id
    db.session.add(order_list)
    db.session.commit()


    return(resp)


