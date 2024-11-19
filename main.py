from flask import Flask, render_template, jsonify
import requests
from requests.exceptions import RequestException
import json
import time
from datetime import datetime, timedelta
import socket

app = Flask(__name__)

def 获取台湾地震数据(max_retries=3, retry_delay=5, limit=100):
    # 計算 300 天前的日期
    thirty_days_ago = (datetime.now() - timedelta(days=300)).strftime("%Y-%m-%d")

    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0015-001?Authorization=CWA-5DB843F5-B1FD-433C-953A-415EEFEABF5C"

    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            print(f"成功獲取 API 數據，正在處理...")

            if 'records' in data and 'Earthquake' in data['records']:
                return data['records']['Earthquake']
            else:
                print("意外的數據結構:", data)
                return []
        except RequestException as e:
            print(f"嘗試 {attempt + 1}/{max_retries} 失敗: {str(e)}")
            if attempt < max_retries - 1:
                print(f"等待 {retry_delay} 秒後重試...")
                time.sleep(retry_delay)
            else:
                print("無法獲取地震數據")
                return []

def 分析台湾地震数据(地震):
    try:
        return {
            "發生時間": 地震['EarthquakeInfo']['OriginTime'],
            "震級": 地震['EarthquakeInfo']['EarthquakeMagnitude']['MagnitudeValue'],
            "深度": 地震['EarthquakeInfo']['FocalDepth'],
            "地點": 地震['EarthquakeInfo']['Epicenter']['Location'],
            "嚴重程度": "較強" if float(地震['EarthquakeInfo']['EarthquakeMagnitude']['MagnitudeValue']) >= 5.0 else "輕微"
        }
    except KeyError as e:
        print(f"分析地震數據時出錯: {str(e)}")
        return None

@app.route('/')
def 台湾地震速报系统():
    return render_template('earthquake_report.html')

@app.route('/get_latest_data')
def get_latest_data():
    地震列表 = 获取台湾地震数据()
    分析结果 = [分析台湾地震数据(地震) for 地震 in 地震列表]
    分析结果 = [结果 for 结果 in 分析结果 if 结果 is not None]
    return jsonify(分析结果)

@app.route('/ip')
def get_ip():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return f"主機名：{hostname}<br>IP 地址：{ip_address}"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)