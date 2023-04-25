from flask import Flask, request, jsonify
from goose3 import Goose
from newspaper import Article
from bs4 import BeautifulSoup
from urllib.request import urlopen

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
    print("추출할 url:", url)

    # 추출한 url에서 content parsing
    content1 = extract3(url)
    print("goose로 추출된 컨텐츠: ", content1)

    content2 = extract2(url)
    print("newspaper로 추출된 컨텐츠: ", content2)

    content3 = ""
    length = len(content1) + len(content2)
    if length > 10:
        # response body에 content 담아서 return
        return jsonify({'content': content1 + content2})
    else:
        # response body에 content 담아서 return
        content3 = extract1(url)
        return jsonify({'content': content3})


def extract3(url):
    article = g.extract(url=url)
    text = article.cleaned_text
    return text


def extract2(url):
    article = Article(url, language='ko')
    article.download()
    article.parse()

    text = article.text
    return text


def extract1(url):
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
