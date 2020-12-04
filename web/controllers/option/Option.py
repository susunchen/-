from flask import Blueprint,request,redirect,jsonify
from common.libs.Help import ops_render,iPagination,getCurrentDate
from application import app ,db
from common.libs.UrlManager import UrlManager
from common.models.option.option import Option
from common.models.food.hall import Hall
from common.libs.huawei.huawei_help import hwawei_help

import requests
import json


route_option = Blueprint( 'option_page',__name__ )


@route_option.route( "/index" )
def index():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    page = int(req['p']) if ('p' in req and req['p']) else 1
    resp_data = {}
    token = hwawei_help.getAccessToken()
    (mun,HUAoption)=hwawei_help.GET(token)
    option = Option.query.order_by(Option.hall_id.desc()).all()

    add_register = 0
    for item1 in HUAoption:
        if_register = False
        if_set = False
        nodeId = item1["deviceInfo"]["nodeId"]
        if option:
            for item2 in option:
                if nodeId == item2.nodeId:
                    if_register = True
        if if_register ==False:
            add_register = add_register + 1
            Model_option = Option()
            Model_option.name = "未命名"
            Model_option.deviceId = item1["deviceId"]
            Model_option.nodeId = nodeId
            Model_option.hall_id = 0
            Model_option.option_type = 0
            Model_option.option_id = 0
            Model_option.status = 1
            Model_option.created_time = Model_option.updated_time = getCurrentDate()
            db.session.add(Model_option)
            db.session.commit()




    option = Option.query.order_by(Option.hall_id.desc()).all()
    if option:
        for item2 in option:
            for item1 in HUAoption:
                if item1["deviceInfo"]["nodeId"]==item2.nodeId:
                    item2.onlion_status = item1["deviceInfo"]["status"]
                    break
    need_set_munber = 0
    for item in option:
        if item.name == "未命名":
            need_set_munber = need_set_munber + 1


    page_params = {
        'total': Option.query.count(),
        'page_size': app.config['PAGE_SIZE'],
        'page': page,
        'display': app.config['PAGE_DISPLAY'],
        'url': request.full_path.replace("&p={}".format(page), "")
    }
    pages = iPagination(page_params)

    resp_data["add_register"] = add_register
    resp_data["need_set_munber"] = need_set_munber
    resp_data['list'] = option
    resp_data['pages'] = pages
    resp_data['search_con'] = req
    resp_data['option_type_mapping'] = app.config['OPTION_TYPE_MAPPING']
    resp_data['status_mapping'] = app.config['STATUS_MAPPING']
    resp_data['current'] = 'option'

    return ops_render("option/index.html", resp_data)

@route_option.route( "/set",methods = [ "GET","POST" ] )
def set():
    if request.method == "GET":
        resp_data = {}
        req = request.args
        id = int( req.get( "id",0 ) )
        option_type = []
        option_type_list = []
        option_type = app.config["OPTION_TYPE_MAPPING"]
        n = 1
        for item,velaue in option_type.items():
            tep_data = {
                "id": item,
                "name":velaue
            }
            option_type_list.append(tep_data)
        info = None
        hall_list = Hall.query.all()
        if id :
            info = Option.query.filter_by( id = id ).first()
        resp_data['info'] = info
        resp_data['hall_list'] = hall_list
        resp_data['option_type_list'] = option_type_list
        return ops_render( "option/set.html",resp_data )

    resp = {'code': 200, 'msg': '操作成功~~', 'data': {}}
    req = request.values

    id = req['id'] if 'id' in req else 0
    name = req['name'] if 'name' in req else ''
    option_type = req['option_type'] if 'option_type' in req else 0
    option_id = req['option_id'] if 'option_id' in req else 0
    hall_id = req['hall_id'] if 'hall_id' in req else 0
    note = req['note'] if 'note' in req else ''

    if name is None or len(name) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的名称~~"
        return jsonify(resp)

    if option_type is None or int(option_type) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的设备类型~~"
        return jsonify(resp)

    if option_id is None or int(option_id) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的设备编号~~"
        return jsonify(resp)

    if hall_id is None or int(hall_id) < 1:
        resp['code'] = -1
        resp['msg'] = "请输入符合规范的餐厅编号~~"
        return jsonify(resp)

    option_info = Option.query.filter_by( id = id).first()
    deviceId = option_info.deviceId
    serviceId = "SetOption"
    method = "Set"
    body = {
        "hall_id": hall_id,
        "option_type":option_type,
        "option_id":option_id
    }
    token = hwawei_help.getAccessToken()
    # hwawei_help.sendCommand(token = token,deviceId=deviceId,serviceId=serviceId,method=method,body=body)
    # 用下面这个
    back = hwawei_help.CMD(token=token, deviceId=deviceId, serviceId=serviceId, method=method, paras=body)

    option_info.name = name
    option_info.option_type = option_type
    option_info.option_id = option_id
    option_info.hall_id = hall_id
    option_info.note = note
    option_info.updated_time = getCurrentDate()
    db.session.add(option_info)
    db.session.commit()




    return jsonify(resp)



@route_option.route("/ops",methods = [ "POST" ])
def Ops():
    resp = {'code': 200, 'msg': '操作成功~~', 'data': {}}
    req = request.values

    id = req['id'] if 'id' in req else 0
    act = req['act'] if 'act' in req else ''
    if not id :
        resp['code'] = -1
        resp['msg'] = "请选择要操作的账号~~"
        return jsonify(resp)

    if  act not in [ 'remove','recover' ] :
        resp['code'] = -1
        resp['msg'] = "操作有误，请重试~~"
        return jsonify(resp)

    option_info = Option.query.filter_by( id= id ).first()
    if not option_info:
        resp['code'] = -1
        resp['msg'] = "指定设备不存在~~"
        return jsonify(resp)

    if act == "remove":
        option_info.status = 0
    elif act == "recover":
        option_info.status = 1

        option_info.update_time = getCurrentDate()
    db.session.add( option_info )
    db.session.commit()
    return jsonify(resp)