from flask import Blueprint, request, redirect, jsonify
from common.libs.Help import ops_render, iPagination, getCurrentDate
from application import app, db
from common.libs.UrlManager import UrlManager
from common.models.Qrcpde_date import QrcodeDate

route_qrcode = Blueprint('Qrcode_page', __name__)

@route_qrcode.route("/get", methods=["POST"]) #写入日志
def get():

    resp = {'code': 200, 'msg': '操作成功~~', 'data': {}}

    req = request.values
    camera_id = int(req['camera_id']) if 'camera_id' in req and req['camera_id'] else 0
    qrcode_id = req['qrcode_id']if 'qrcode_id' in req and req['qrcode_id'] else 0
    if camera_id < 1:
        resp['code'] = -1
        resp['msg'] = "摄像头识别错误~~"
        return jsonify(resp)
#    if qrcode_id < 1:
#        resp['code'] = -1
  #      resp['msg'] = "二维码识别错误~~"
 #       return jsonify(resp)

    model_QrcodeDate = QrcodeDate()
    model_QrcodeDate.camera_id = camera_id
    model_QrcodeDate.qrcode_id = qrcode_id
    model_QrcodeDate.created_time = getCurrentDate()
    db.session.add(model_QrcodeDate)
    db.session.commit()
    return jsonify(resp)

