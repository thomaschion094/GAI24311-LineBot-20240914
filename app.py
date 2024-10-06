from flask import Flask, request, abort, jsonify
import os
from dotenv import load_dotenv
from pymongo import MongoClient

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

load_dotenv()

app = Flask(__name__)

# 獲取環境變數
access_token = os.environ.get('LINE_BOT_ACCESS_TOKEN')
secret = os.environ.get('LINE_BOT_SECRET')
mongodb_uri = os.getenv('MONGODB_URI')

# 初始化 LINE Bot API 和 WebhookHandler
configuration = Configuration(access_token=access_token)
handler = WebhookHandler(secret)

# 連接到 MongoDB
client = MongoClient(mongodb_uri)
db = client['CareDB']

from bson import ObjectId
import json

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

def mongo_to_dict(obj):
    return json.loads(JSONEncoder().encode(obj))

def query_database(district, collection_name='taipei'):
    try:
        # 移除 "區" 字，以便匹配 "town" 字段
        district = district.replace("區", "").strip()
        
        query = {
            "$and": [
                {"county": {"$regex": "新北市", "$options": "i"}},
                {"town": {"$regex": f"^{district}", "$options": "i"}}
            ]
        }
        app.logger.info(f"Querying {collection_name} collection with query: {query}")
        
        result = list(db[collection_name].find(query))
        app.logger.info(f"Raw query result: {[mongo_to_dict(doc) for doc in result[:2]]}")  # 只記錄前兩個結果
        
        response = ""
        count = 0
        for item in result:
            count += 1
            title = item.get('title', '')
            address = item.get('address', '')
            tel = item.get('tel', '')
            response += f"機構名稱: {title}\n"
            response += f"地址: {item['county']}{item['town']}{address}\n"
            response += f"電話: {tel}\n\n"

        app.logger.info(f"Query returned {count} results")

        if not response:
            # 如果沒有結果，嘗試一個更寬鬆的查詢
            loose_query = {
                "$or": [
                    {"county": {"$regex": "新北市", "$options": "i"}},
                    {"town": {"$regex": district, "$options": "i"}},
                    {"address": {"$regex": district, "$options": "i"}},
                    {"title": {"$regex": district, "$options": "i"}}
                ]
            }
            app.logger.info(f"Performing loose query: {loose_query}")
            loose_result = list(db[collection_name].find(loose_query))
            app.logger.info(f"Loose query raw result: {[mongo_to_dict(doc) for doc in loose_result[:2]]}")
            
            for item in loose_result:
                count += 1
                title = item.get('title', '')
                address = item.get('address', '')
                tel = item.get('tel', '')
                response += f"機構名稱: {title}\n"
                response += f"地址: {item['county']}{item['town']}{address}\n"
                response += f"電話: {tel}\n\n"
            
            app.logger.info(f"Loose query returned {count} results")

        if not response:
            response = "查無資料"
        return response

    except Exception as e:
        app.logger.error(f'查詢失敗: {e}')
        return f'查詢失敗: {e}'

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    msg = event.message.text
    app.logger.info(f"Received message: {msg}")

    if '士林' in msg:
        response = query_database("士林區", collection_name='taipei')
    elif '大同' in msg:
        response = query_database("大同區", collection_name='taipei')
    elif '北投' in msg:
        response = query_database("北投區", collection_name='taipei')
    elif '蘆洲' in msg:
        app.logger.info("Querying for 蘆洲區 in newtaipei collection")
        response = query_database("蘆洲區", collection_name='newtaipei')
        app.logger.info(f"Query response length: {len(response)}")
    else:
        response = "未識別的區域"

    app.logger.info(f"Sending response: {response[:100]}...")  # 只記錄前100個字符

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=response)]
            )
        )

@app.route("/check_newtaipei", methods=['GET'])
def check_newtaipei():
    try:
        # 獲取集合中的文檔數量
        doc_count = db['newtaipei'].count_documents({})
        
        # 獲取前5個文檔作為樣本
        sample_docs = list(db['newtaipei'].find().limit(5))
        
        # 獲取集合中的所有唯一字段名
        all_fields = set()
        for doc in sample_docs:
            all_fields.update(doc.keys())
        
        return jsonify({
            "document_count": doc_count,
            "sample_documents": [{k: str(v) for k, v in doc.items()} for doc in sample_docs],
            "all_fields": list(all_fields)
        })
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/test_db", methods=['GET'])
def test_db():
    try:
        # 檢查數據庫連接
        db.command('ping')
        
        # 獲取 newtaipei 集合的文檔數量
        doc_count = db['newtaipei'].count_documents({})
        
        # 獲取一個示例文檔
        sample_doc = db['newtaipei'].find_one()
        
        return jsonify({
            "status": "success",
            "message": "Database connection successful",
            "newtaipei_doc_count": doc_count,
            "sample_document": {k: str(v) for k, v in sample_doc.items()} if sample_doc else None
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Database operation failed: {str(e)}"
        })

@app.route("/check_luzhou", methods=['GET'])
def check_luzhou():
    try:
        result = list(db['newtaipei'].find({"$or": [
            {"county": {"$regex": "新北市", "$options": "i"}},
            {"town": {"$regex": "蘆洲", "$options": "i"}},
            {"address": {"$regex": "蘆洲", "$options": "i"}},
            {"title": {"$regex": "蘆洲", "$options": "i"}}
        ]}))
        return jsonify({
            "count": len(result),
            "samples": [mongo_to_dict(doc) for doc in result[:5]]  # 返回前5個結果作為樣本
        })
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
