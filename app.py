import torch
import math
from flask import Flask, request, jsonify
from goose3 import Goose
from newspaper import Article
from bs4 import BeautifulSoup
from urllib.request import urlopen
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import re
from transformers import PreTrainedTokenizerFast
from transformers.models.bart import BartForConditionalGeneration

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
    if "naver.me" in url:
        content1 = extract4(url)
        return jsonify({'content': content1})
    else:
        content1 = extract3(url)
        print("goose로 추출된 컨텐츠: ", content1)

        content2 = extract2(url)
        print("newspaper로 추출된 컨텐츠: ", content2)

        content3 = ""
        length = len(content1) + len(content2)

        if length > 30:
            # response body에 content 담아서 return
            return jsonify({'content': content1 + content2})
        else:
            # response body에 content 담아서 return
            content3 = extract1(url)
        return jsonify({'content': content3})


@app.route('/summarize', methods=['POST'])
def summarizeByBart():
    content = request.json['content']

    summary = summarize(content)
    print("Summarized By KoBART = ", summary)

    return jsonify({'content': summary})


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


def extract4(url):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(executable_path="/home/mas/qwer/chromedriver", chrome_options=chrome_options)
    driver.get(url)
    html_source = driver.page_source
    soup = BeautifulSoup(html_source, 'html.parser')
    for script in soup(["script", "style"]):
        script.decompose()
    text = soup.get_text()
    text = re.sub(r'\s+', ' ', text)
    return text


def summarize(text):
    model = BartForConditionalGeneration.from_pretrained('/home/mas/qwer/qwer-text-train/kobart_summary')
    tokenizer = PreTrainedTokenizerFast.from_pretrained('gogamza/kobart-base-v1')

    input_ids = tokenizer.encode(text)
    input_ids = torch.tensor(input_ids)
    input_ids = input_ids.unsqueeze(0)
    output = model.generate(input_ids, eos_token_id=1, max_length=512, num_beams=5)
    summary = tokenizer.decode(output[0], skip_special_tokens=True)

    return summary
