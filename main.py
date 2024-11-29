from flask import Flask, render_template, request
import requests
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# API 기본 정보
BASE_URL = "https://api.odcloud.kr/api/ApplyhomeInfoDetailSvc/v1/getAPTLttotPblancDetail"
SERVICE_KEY = os.getenv('SERVICE_KEY')  # .env 파일에서 서비스 키 로드

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results', methods=['POST'])
def results():
    year = request.form['year']
    subscrpt_area_name = request.form['subscrpt_area_name']
    
    # 입력한 연도를 바탕으로 시작일과 종료일 설정
    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"
    
    # 요청 파라미터 설정
    params = {
        "page": 1,
        "perPage": 10,
        "cond[RCRIT_PBLANC_DE::GTE]": start_date,  # 시작일 필터링 (입력한 연도의 1월 1일)
        "cond[RCRIT_PBLANC_DE::LTE]": end_date,    # 종료일 필터링 (입력한 연도의 12월 31일)
        "cond[SUBSCRPT_AREA_CODE_NM::EQ]": subscrpt_area_name,  # 지역명 필터링
        "serviceKey": SERVICE_KEY
    }

    try:
        # API 요청
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()  # HTTP 에러 발생 시 예외 처리

        # 결과 출력
        data = response.json()

        # 데이터 확인 및 결과 페이지로 전달
        if data.get('data'):
            return render_template('results.html', data=data['data'], year=year, area=subscrpt_area_name)
        else:
            return render_template('results.html', data=None, year=year, area=subscrpt_area_name)

    except requests.exceptions.RequestException as e:
        return f"API 호출 중 오류 발생: {e}"
