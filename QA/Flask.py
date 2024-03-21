from models.chatbot_graph import ChatBotGraph
# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, render_template
import json, os
from flask_restplus import Api, Resource
from flask_cors import CORS


app = Flask(__name__)
app.debug = False
# api = Api(app)
bot = ChatBotGraph()

@app.route('/qa', methods=["POST"])
def qa():
    data = request.get_data()
    print(data)
    # json_data = json.loads(data.decode("utf-8"))
    json_data = json.loads(data)
    sent = json_data["sent"]
    ans = bot.chat_main(sent)
    res = {"text": ans, "code": 200}
    return jsonify(res)

#
# @app.route('/home')
# def home():
#     return render_template("index.html")


if __name__ == '__main__':
    CORS(app, supports_credentials=True)
    app.run(host='0.0.0.0', port=8088,debug=False) # 这里指定了地址和端口号。
