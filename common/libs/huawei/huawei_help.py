
from application import app,db
import hashlib,requests,uuid,json,datetime
from common.libs.Help import getCurrentDate
from common.models.huawei.HuaweiOauthAccessToken import HuaweiOauthAccessToken



class hwawei_help():
    def __init__(self):
        pass

    @staticmethod
    def getAccessToken():
        requests.packages.urllib3.disable_warnings()
        token = None
        token_info = HuaweiOauthAccessToken.query.filter(HuaweiOauthAccessToken.expired_time >= getCurrentDate()).first()
        if token_info:
            token = token_info.access_token
            return token
        url = "https://49.4.92.191:8743/iocm/app/sec/v1.1.0/login"
        header = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "appId": app.config['HUAWEI_IOT']['appId'],
            "secret": app.config['HUAWEI_IOT']['secret']
        }
        r = requests.post(url, headers=header, data=data, cert=("cert/client.crt", "cert/client.key"), verify=False);
        if r.status_code != 200 or not r.text:
            return token
        data = json.loads(r.text)
        now = datetime.datetime.now()
        date = now + datetime.timedelta(seconds=data['expiresIn'] - 200)
        model_token = HuaweiOauthAccessToken()
        model_token.access_token = data['accessToken']
        model_token.refresh_token = data['refreshToken']
        model_token.expired_time = date.strftime("%Y-%m-%d %H:%M:%S")
        model_token.created_time = getCurrentDate()
        db.session.add(model_token)
        db.session.commit()

        return data['accessToken']

    @staticmethod
    def sendCommand(token,deviceId,serviceId,method,body):
        msg = False
        requests.packages.urllib3.disable_warnings()
        now_time = datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
        requestId = now_time
        header = {
            "mode": "NOACK",
            "method":method ,
            "requestId" : requestId
        }

        headers = {
            "app_key":  app.config['HUAWEI_IOT']['appId'],
            "Authorization": "Bearer " + token ,
            "Content-Type": "application/json"
        }
        data = {
            "header": header,
            "body": body
        }
        url= "https://49.4.92.191:8743/iocm/app/signaltrans/v1.1.0/devices/" + deviceId \
               + "/services/" + serviceId + "/sendCommand?appId=" + app.config['HUAWEI_IOT']['appId']
        r = requests.post(url=url, headers=headers, data=json.dumps(data),cert=("cert/client.crt", "cert/client.key"),
                          verify=False)

        return r.text
    @staticmethod
    def CMD(token,deviceId,serviceId,method,paras):
        requests.packages.urllib3.disable_warnings()
        now_time = datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
        requestId = now_time
        headers = {
            "app_key":  app.config['HUAWEI_IOT']['appId'],
            "Authorization": "Bearer " + token ,
            "Content-Type": "application/json"
        }
        command = {
            "serviceId":serviceId,
            "method":method,
            "paras":paras
        }
        data = {
            "deviceId":deviceId,
            "command":command,
            "expireTime":0


        }
        url= "https://49.4.92.191:8743/iocm/app/cmd/v1.4.0/deviceCommands?appid=" + app.config['HUAWEI_IOT']['appId']
        r = requests.post(url=url, headers=headers, data=json.dumps(data),cert=("cert/client.crt", "cert/client.key"),
                          verify=False)
        return r

    @staticmethod
    def GET(token):
        requests.packages.urllib3.disable_warnings()
        headers = {
            "app_key": app.config['HUAWEI_IOT']['appId'],
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json"
        }
        appId = app.config['HUAWEI_IOT']['appId']
        munber = 0
        option = []
        n = str(0)
        while True:
            while True:
                url1 = "https://49.4.92.191:8743/iocm/app/dm/v1.4.0/devices?appId=" + appId + "&pageNo=" + n + "&pageSize=2"
                r = requests.get(url=url1, headers=headers, cert=("cert/client.crt", "cert/client.key"), verify=False);
                text = json.loads(r.text)
                option = option + text["devices"]
                if text["pageSize"] > text["totalCount"]:
                    munber = munber + text["totalCount"]
                    return (text["totalCount"], option)
                munber = munber + text["pageSize"]
                if munber >= text["totalCount"]:
                    return (text["totalCount"],option)
                n = str(int(n) + 1)
        return
