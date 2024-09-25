from flask import Flask, request, abort

# 載入 json 標準函式庫，處理回傳的資料格式
import json

# 載入 LINE Message API 相關函式庫
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, QuickReply, QuickReplyButton, MessageAction
import os
from dotenv import load_dotenv
load_dotenv()

from pymongo import MongoClient

app = Flask(__name__)

access_token = os.environ.get('LINE_BOT_ACCESS_TOKEN')
secret = os.environ.get('LINE_BOT_SECRET')
line_bot_api = LineBotApi(access_token)              # 確認 token 是否正確
handler = WebhookHandler(secret)                     # 確認 secret 是否正確

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)                    # 取得收到的訊息內容
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

#client = MongoClient('mongodb://gai24311cosmosdbru:pMUWSrwunN9FcPix9MVMZoQHDjGEWNGFw6fTY0FihEcGPcxJi5o3Bi9DIT0FCu1JpqrW9NIuLJNiACDb4GtnpA==@gai24311cosmosdbru.mongo.cosmos.azure.com:10255/?ssl=true&retrywrites=false&replicaSet=globaldb&maxIdleTimeMS=120000&appName=@gai24311cosmosdbru@')
mongodb_uri = os.getenv('MONGODB_URI')
client = MongoClient(mongodb_uri)
db = client['CareDB']
collection = db['taipei']

# @handler.add(MessageEvent, message=TextMessage)
# def handle_message(event):
#     msg = str(event.message.text)
#     line_bot_api.reply_message(event.reply_token, TextSendMessage(msg))

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg=str(event.message.text)
    #if msg == '士林':
    if '士林' in msg:
         #reply='這是選單一'
         #line_bot_api.reply_message(event.reply_token, TextSendMessage(reply))
        #遦線到mondb並查詢士林區的資料
         try:
             #client = MongoClient(MONGODB_URI)
             #db = client['CareDB']
             #collection = db['taipei']
             print('連線成功')
             # 查詢資料
             query = {
                 "$or": [
                     {"行政區": "士林區"},
                     {"區域別": "士林區"}
                 ]
             }

             result = collection.find(query)
             response = ""
             for item in result:
                 name = item.get('據點名稱') or item.get('機構名稱')
                 address = item.get('據點地址') or item.get('地址')
                 phone = item.get('電話')
                 response += f"據點名稱: {name}\n地址: {address}\n電話: {phone}\n\n"

             if not response:
                 response = "查無資料"

            
             line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response))
         except Exception as e:
             print(f'連線失敗: {e}')
             line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f'連線失敗: {e}'))
        #  finally:
        #      client.close()
    #elif msg == '選單二':
    elif '大同' in msg:
        try:
             #client = MongoClient(MONGODB_URI)
             #db = client['CareDB']
             #collection = db['taipei']
             print('連線成功')
             # 查詢資料
             query = {
                 "$or": [
                     {"行政區": "大同區"},
                     {"區域別": "大同區"}
                 ]
             }

             result = collection.find(query)
             response = ""
             for item in result:
                 name = item.get('據點名稱') or item.get('機構名稱')
                 address = item.get('據點地址') or item.get('地址')
                 phone = item.get('電話')
                 response += f"據點名稱: {name}\n地址: {address}\n電話: {phone}\n\n"

             if not response:
                 response = "查無資料"

            
             line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response))
        except Exception as e:
             print(f'連線失敗: {e}')
             line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f'連線失敗: {e}'))
    #elif msg =='選單三':
    elif '北投' in msg:
        try:
             #client = MongoClient(MONGODB_URI)
             #db = client['CareDB']
             #collection = db['taipei']
             print('連線成功')
             # 查詢資料
             query = {
                 "$or": [
                     {"行政區": "北投區"},
                     {"區域別": "北投區"}
                 ]
             }

             result = collection.find(query)
             response = ""
             for item in result:
                 name = item.get('據點名稱') or item.get('機構名稱')
                 address = item.get('據點地址') or item.get('地址')
                 phone = item.get('電話')
                 response += f"據點名稱: {name}\n地址: {address}\n電話: {phone}\n\n"

             if not response:
                 response = "查無資料"

            
             line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response))
        except Exception as e:
             print(f'連線失敗: {e}')
             line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f'連線失敗: {e}'))
    
    #         reply = TextSendMessage(
    #             text='$你選擇了選單3',
    #             emojis=[
    #                 {
    #                     'index': 0,
    #                     'productId': '5ac1bfd5040ab15980c9b435',
    #                     'emojiId': '003'
    #                 },
    #             ]
    #         )
    #         line_bot_api.reply_message(event.reply_token, reply)
    # else:
    #     line_bot_api.reply_message(event.reply_token, TextSendMessage(msg))

if __name__ == "__main__":
    app.run()
