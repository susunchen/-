from web.controllers.api import route_api
from  flask import request,jsonify,g
from common.libs.Help import ops_render, iPagination, getCurrentDate
from application import  app,db
import requests,json
from common.libs.huawei.huawei_help import hwawei_help
from common.models.Qrcpde_date import QrcodeDate
from common.models.pay.PayOrderItem import PayOrderItem
from common.models.pay.PayOrder import PayOrder
from common.models.cabint.cabint_status import CabintStatu
from common.models.cabint.cabint_data import CabintData
from common.models.option.option import Option


@route_api.route("/huawei/get", methods=["POST"] )
def getmessage():
    resp = {"Status Code": "200 OK"}
    req = request.json
    notifyType = req["notifyType"]
    if notifyType =="deviceDataChanged":   #服务为数据推送服务
        service = req["service"]
        if service["serviceType"]=='Scan': #扫描器发出扫描数据
            data = service["data"]
            qrcode_id = data["qrcode_id"]
            option_id = data["option_id"]
            hall_id = data["hall_id"]
            option_type = data["option_type"]

            #model_QrcodeDate = QrcodeDate()
            #model_QrcodeDate.camera_id = option_id
            #model_QrcodeDate.qrcode_id = qrcode_id
            #model_QrcodeDate.created_time = getCurrentDate()
            #db.session.add(model_QrcodeDate)
            #db.session.commit()

            if int(option_type) == 1:
                pay_order_info = PayOrder.query.filter_by(qrcode_id=qrcode_id).first()
                #option_info = Option.query.filter(Option.option_type == 5).filter(Option.hall_id == hall_id) \
                #     .first()
                # deviceId =option_info.deviceId
                # serviceId = "PrintQR"
                # method = "Print"
                # body = {
                #     "QRcore": "qrcode_id",
                # }
                # token = hwawei_help.getAccessToken()
                # #hwawei_help.sendCommand(token = token,deviceId=deviceId,serviceId=serviceId,method=method,body=body)
                # # 用下面这个
                # hwawei_help.CMD(token = token,deviceId=deviceId,serviceId=serviceId,method=method,paras=body)

                pay_order_info.status = -5
                pay_order_info.express_status = -5
                pay_order_info.updated_time = getCurrentDate()
                db.session.add(pay_order_info)
                db.session.commit()
                return jsonify(resp)

            if int(option_type) == 2:
                option_info = Option.query.filter (Option.option_type == 3).filter (Option.hall_id == hall_id)\
                .first()
                deviceId =option_info.deviceId
                serviceId = "MoveToCabint"
                cabint_info = CabintStatu.query.filter_by(cabint_status =1).first()
                if not cabint_info:
                    return jsonify(resp)
                pay_order_info = PayOrder.query.filter(PayOrder.qrcode_id==qrcode_id).filter(PayOrder.status==-5).first()
                if not pay_order_info:
                    return jsonify(resp)
                cabint_id =cabint_info.id
                cabint_info.cabint_status = 0
                db.session.add(cabint_info)
                db.session.commit()
                method = "MOVE"
                body = {
                    "cabint_id": cabint_id,#分配
                }
                token = hwawei_help.getAccessToken()
                #hwawei_help.sendCommand(token = token,deviceId=deviceId,serviceId=serviceId,method=method,body=body)
                #用下面这个
                hwawei_help.CMD(token=token, deviceId=deviceId, serviceId=serviceId, method=method, paras=body)
                pay_order_info = PayOrder.query.filter_by(qrcode_id=qrcode_id).first()
                pay_order_info.express_status = -4
                pay_order_info.updated_time = getCurrentDate()
                pay_order_info.cabint_id = cabint_info.id
                db.session.add(pay_order_info)
                cabint_data_info = CabintData()
                cabint_data_info.cabint_id = cabint_id
                cabint_data_info.order_sn = pay_order_info.order_sn
                cabint_data_info.action = 1
                cabint_data_info.created_time = getCurrentDate()
                db.session.add(cabint_data_info)

                db.session.commit()
                return jsonify(resp)


        if service["serviceType"] == 'RUNSTATUS':
            data = service["data"]
            option_id = data["option_id"]
            hall_id = data["hall_id"]
            option_type = data["option_type"]
            first_transducer = data["first_transducer"]
            if first_transducer=="1":
                transporter_info = Option.query.filter(Option.option_type == 6).filter(Option.hall_id == hall_id) \
                    .first()
                transporter_deviceId = transporter_info.deviceId
                motor_info = Option.query.filter(Option.option_type ==3 ).filter(Option.hall_id == hall_id) \
                    .first()
                motor_deviceId = motor_info.deviceId
                if motor_info.work_status == "waiting":
                    token = hwawei_help.getAccessToken()
                    transporter_serviceId = "Change_Stop"
                    transporter_method = "Stop"
                    transporter_paras = {
                            "status":"stop"
                    }
                    hwawei_help.CMD(token=token, deviceId=transporter_deviceId, serviceId=transporter_serviceId,
                                    method=transporter_method
                                    , paras=transporter_paras) #让传送带停止
                    moter_serviceId = "Ready"
                    moter_method = "Ready"
                    moter_paras = {
                        "Ready": "Ready"
                    }
                    hwawei_help.CMD(token=token,
                                    deviceId=motor_deviceId, serviceId=moter_serviceId,
                                    method=moter_method, paras=moter_paras) #让电机下来
                if motor_info.work_status == "working":
                    token = hwawei_help.getAccessToken()
                    transporter_serviceId = "Change_Stop"
                    transporter_method = "Stop"
                    transporter_paras = {
                        "status": "stop"
                    }
                    hwawei_help.CMD(token=token, deviceId=transporter_deviceId, serviceId=transporter_serviceId,
                                    method=transporter_method
                                    , paras=transporter_paras)  # 让传送带停止
                    return jsonify(resp)

        if service["serviceType"] == 'Work_status':
            data = service["data"]
            option_id = data["option_id"]
            hall_id = data["hall_id"]
            option_type = data["option_type"]
            Work_status = data["Work_status"]
            if Work_status == "ready":
                transporter_info = Option.query.filter(Option.option_type == 6).filter(Option.hall_id == hall_id) \
                    .first()
                token = hwawei_help.getAccessToken()
                transporter_deviceId = transporter_info.deviceId
                transporter_serviceId = "Change_Run"
                transporter_method = "Run"
                transporter_paras = {
                    "status": "run"
                }
                hwawei_help.CMD(token=token, deviceId=transporter_deviceId, serviceId=transporter_serviceId,
                                method=transporter_method
                                , paras=transporter_paras)  # 让传送带启动

            motor_info = Option.query.filter(Option.option_type == 3).filter(Option.hall_id == hall_id) \
                    .first()
            motor_info.work_status = Work_status
            motor_info.updated_time = getCurrentDate()
            db.session.add(motor_info)
            db.session.commit()
            return jsonify(resp)
        if service["serviceType"] == 'status_change':
            cabint_id = data["cabint_id"]
            hall_id = data["hall_id"]
            pay_order_info = PayOrder.query.filter(PayOrder.cabint_id==cabint_id).filter(PayOrder.hall_id==hall_id).first()
            pay_order_info.status = -4
            pay_order_info.updated_time = getCurrentDate()
            db.session.add(pay_order_info)
            db.session.commit()

    return jsonify(resp)

