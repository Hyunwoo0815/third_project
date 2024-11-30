from flask import Flask, render_template, request, send_from_directory
import requests
from dotenv import load_dotenv
import os
import logging

# .env 파일 로드
load_dotenv()

# API 기본 정보
BASE_URL = "https://api.odcloud.kr/api/ApplyhomeInfoDetailSvc/v1/getAPTLttotPblancDetail"
SERVICE_KEY = os.getenv('SERVICE_KEY')  # .env 파일에서 서비스 키 로드

# 로깅 설정
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# /robots.txt 처리
@app.route('/robots.txt')
def robots_txt():
    return send_from_directory('static', 'robots.txt')

# 최신 공고 10개를 가져오는 함수
def fetch_latest_announcements():
    params = {
        "page": 1,
        "perPage": 10,
        "serviceKey": SERVICE_KEY
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if data.get('data'):
            latest_announcements = [(item['HOUSE_NM'], item['PBLANC_URL']) for item in data['data']]
            return latest_announcements
        return []
    except requests.exceptions.RequestException as e:
        logging.error(f"API 호출 중 오류 발생: {e}")
        return []

@app.route('/')
def index():
    latest_house_links = fetch_latest_announcements()
    return render_template('index.html', latest_house_links=latest_house_links, enumerate=enumerate)

@app.route('/results', methods=['POST'])
def results():
    year = request.form['year']
    subscrpt_area_name = request.form['subscrpt_area_name']
    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"
    params = {
        "page": 1,
        "perPage": 10,
        "cond[RCRIT_PBLANC_DE::GTE]": start_date,
        "cond[RCRIT_PBLANC_DE::LTE]": end_date,
        "cond[SUBSCRPT_AREA_CODE_NM::EQ]": subscrpt_area_name,
        "serviceKey": SERVICE_KEY
    }
    logging.info(f"Sending request with params: {params}")

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if data.get('data'):
            return render_template('results.html', data=data['data'], year=year, area=subscrpt_area_name)
        return render_template('results.html', data=None, year=year, area=subscrpt_area_name)
    except requests.exceptions.RequestException as e:
        logging.error(f"API 호출 중 오류 발생: {e}")
        return f"API 호출 중 오류 발생: {e}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
