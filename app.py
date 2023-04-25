from flask import Flask, request, jsonify
from goose3 import Goose

g = Goose({'browser_user_agent': 'Mozilla', 'parser_class': 'lxml'})


# __name__ => 모듈명. 여기서는 app.py 라는 모듈이 실행 되므로 main 이라는 문자열이 담긴다.
app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello!"


@app.route('/extract', methods=['POST'])
def textExtract():
    # request body에서 url 추출
    url = request.json['url']

    # 추출한 url에서 content parsing
    content = extract(url)

    # response body에 content 담아서 return
    return jsonify({'content': content})


def extract(url):
    article = g.extract(url=url)
    text = article.cleaned_text
    return text
