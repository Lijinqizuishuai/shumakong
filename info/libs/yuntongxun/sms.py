from ronglian_sms_sdk import SmsSDK

accId = '8a216da878005a8001788757c21632b5'
accToken = '2ed3c4b28e734a4186d923e9f8d80727'
appId = '8a216da878005a8001788757c3f432bb'


def send_message():
    sdk = SmsSDK(accId, accToken, appId)
    tid = '1'
    mobile = '17721235356'
    datas = ('变量1', '变量2')
    resp = sdk.sendMessage(tid, mobile, datas)
    print(resp)

send_message()
