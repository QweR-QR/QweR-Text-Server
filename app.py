from flask import Flask, request, jsonify
from urllib.request import urlopen
from bs4 import BeautifulSoup
import sys

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
    html = urlopen(url).read()
    soup = BeautifulSoup(html, features="html.parser")

    for script in soup(["script", "style"]):
        script.extract()

    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return text
