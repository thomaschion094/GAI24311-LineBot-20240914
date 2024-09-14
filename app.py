import json
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

def linebot(request):
    try:
        access_token = 'FcJ4pkfxpTb2w092vkxqxFPGmUkqzkEYITKCQo570s7m3W24FXKKGQwyeZoIMkk/ODd1pPjXrvy6GVwUzMCtEa35f7CqO33JM6TTlMDxI3hg7gaTFvvL8k/pgNWO/Yc5oBsnI8axYg9/WQxIV1tU8AdB04t89/1O/w1cDnyilFU='
        secret = '0078b45ed2d1cd04c8da9fe6797a80d1'
        body = request.get_data(as_text=True)
        json_data = json.loads(body)
        line_bot_api = LineBotApi(access_token)
        handler = WebhookHandler(secret)
        signature = request.headers['X-Line-Signature']
        handler.handle(body, signature)
        msg = json_data['events'][0]['message']['text']
        tk = json_data['events'][0]['replyToken']
        line_bot_api.reply_message(tk,TextSendMessage(msg))
        print(msg, tk)
    except:
        print(request.args)
    return 'OK'
