#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 23 10:16:08 2024

@author: jin
"""

import requests
import datetime
from datetime import timedelta
import pandas as pd

class FnSpace(object):
    def __init__(self, api_key):
        self.api_key = api_key

    def get_data(self, category, **kwargs):
        """
        Sends a request to the API using the provided parameters.
    
        :param kwargs: Keywords required for the API request
        :return: The requested data in DataFrame format
        """
        
        # Include API key and convert kwargs format to fit request url format
        if category == 'stock_list':
            
            """
            key   string      필수      발급받은 개인 인증키
            mkttype   string   필수      KOSPI(1)/KOSDAQ(2)/KONEX(3)/KOSPI+KOSDAQ(4)/KOSPI200(5)/KOSDAQ150(6)
            date   string   필수      기준일(YYYYMMDD)
            format   string   필수      조회 결과 포맷. json/xml
            """

    
            # Setting the base URL
            base_url = 'https://www.fnspace.com/Api/CompanyListApi'
            params = {
                'key' : self.api_key,
                'format': 'json',
                'mkttype': kwargs.get('mkttype', '4'),
                'date': kwargs.get('date', datetime.datetime.now().date().strftime('%Y%m%d')),
            }
            
            try:
                # API request
                response = requests.get(base_url, params=params)
                response.raise_for_status()
                # print("API Response:", response.text)
            except requests.RequestException as e:
                print(f"API request error occurred: {e}")
                return None
        
            try:
                # Convert JSON response to DataFrame
                json_data = response.json()
                df = pd.DataFrame(json_data['dataset'])
                return df
            
            except ValueError:
                print("Failed to convert JSON data")
                return None
        
        elif category == 'account':
            # Ensure that 'code' and 'item' are lists
            codes = kwargs.get('code', [])
            items = kwargs.get('item', [])

            # Check if 'code' and 'item' are single strings and convert them to lists if so
            if isinstance(codes, str):
                codes = [codes]
            if isinstance(items, str):
                items = [items]
            
            # Setting the base URL
            base_url = 'https://www.fnspace.com/Api/FinanceApi'
            
            requested_codes = set(f"A{x}" for x in kwargs['code'])
            
            params = {
                'key' : self.api_key,
                'format': 'json',
                'code': ','.join(requested_codes),
                'item': ','.join(items),
                'consolgb': kwargs.get('consolgb', 'M'),
                'annualgb': kwargs.get('annualgb', 'A'),
                'accdategb': kwargs.get('accdategb', 'C'),
                'fraccyear': kwargs.get('from_year', str(datetime.datetime.now().year-1)),
                'toaccyear': kwargs.get('to_year', str(datetime.datetime.now().year-1))
            }
            
            try:
                # API request
                response = requests.get(base_url, params=params)
                response.raise_for_status()
                # print("API Response:", response.text)
            except requests.RequestException as e:
                print(f"API request error occurred: {e}")
                return None
        
            try:
                # Convert JSON response to DataFrame
                json_data = response.json()
                data_entries = []
                received_codes = set()
                for entry in json_data.get('dataset', []):
                    code = entry.get('CODE', '')
                    name = entry.get('NAME', '')
                    received_codes.add(code)
                    for data in entry.get('DATA', []):
                        data['CODE'] = code
                        data['NAME'] = name
                        data_entries.append(data)
                
                missing_codes = requested_codes - received_codes
                if missing_codes:
                    print(f"Warning: No data available for these codes: {', '.join(missing_codes)}")
                
                df = pd.DataFrame(data_entries)
                return df
            
            except ValueError:
                print("Failed to convert JSON data")
                return None
        
        elif category == 'stock_price':
            """
            kwargs = {'code' : ['005930', '005380'], 
                      'item' : ['S100310', 'S100320', 'S100330', 'S100300', 'S100950']}
            """
            # Ensure that 'code' and 'item' are lists
            codes = kwargs.get('code', [])
            items = kwargs.get('item', [])

            # Check if 'code' and 'item' are single strings and convert them to lists if so
            if isinstance(codes, str):
                codes = [codes]
            if isinstance(items, str):
                items = [items]
            
            # Setting the base URL
            base_url = 'https://www.fnspace.com/Api/StockApi'
            
            requested_codes = set(f"A{x}" for x in kwargs['code'])
            
            params = {
                'key' : self.api_key,
                'format': 'json',
                'code': ','.join(requested_codes),
                'item': ','.join(items if len(items)!=0 else ['S100310', 'S100320', 'S100330', 'S100300', 'S100950']),
                'frdate': kwargs.get('from_date', str((datetime.datetime.now()-timedelta(days=365)).strftime("%Y%m%d"))),
                'todate': kwargs.get('to_date', str(datetime.datetime.now().strftime("%Y%m%d"))),
            }
            
            try:
                # API request
                response = requests.get(base_url, params=params)
                response.raise_for_status()
                # print("API Response:", response.text)
            except requests.RequestException as e:
                print(f"API request error occurred: {e}")
                return None
        
            try:
                # Convert JSON response to DataFrame
                json_data = response.json()
                
                data_entries = []
                received_codes = set()
                for entry in json_data.get('dataset', []):
                    code = entry.get('CODE', '')
                    name = entry.get('NAME', '')
                    received_codes.add(code)
                    for data in entry.get('DATA', []):
                        data['CODE'] = code
                        data['NAME'] = name
                        data_entries.append(data)
                
                missing_codes = requested_codes - received_codes
                if missing_codes:
                    print(f"Warning: No data available for these codes: {', '.join(missing_codes)}")
                
                df = pd.DataFrame(data_entries)
                return df
            
            except ValueError:
                print("Failed to convert JSON data")
                return None

if __name__ == '__main__':
            
    # API 키 설정 및 FnSpace 인스턴스 생성
    api_key = "Your API key"
    fs = FnSpace(api_key)
    
    # 1. 재무 데이터 불러오기
    account_df = fs.get_data(category = 'account', 
                             code = ['005930', '005380'], # 종목코드 리스트. 예) 삼성전자, 현대자동차
                             item = ['M122700', 'M123955'], # 출력 변수 리스트. 예) 당기순이익, 보고서발표일
                             consolgb = 'M', # 회계기준. 주재무제표(M)/연결(C)/별도(I) (default : 주재무제표(M))
                             annualgb = 'A', # 연간(A)/분기(QQ)/분기누적(QY) (default : 연간(A))
                             accdategb = 'C', # 컨센서스 결산년월 선택 기준. Calendar(C)/Fiscal(F) (default : Calendar(C))
                             from_year = '2020', # 조회 시작 연도 (default : 직전 연도)
                             to_year = '2020' # 조회 종료 연도 (default : 직전 연도)
                             )  
    
    # 2. 주식 리스트 데이터 불러오기
    
    stock_list_df = fs.get_data(category = 'stock_list', 
                                mkttype ='4', # KOSPI(1)/KOSDAQ(2)/KONEX(3)/KOSPI+KOSDAQ(4)/KOSPI200(5)/KOSDAQ150(6)
                                date ='20240624') # 조회 기준일
    
    # 3. 주가 데이터 불러오기
    
    price_df = fs.get_data(category = 'stock_price', 
                           code = ['005930', '005380'], # 종목코드 리스트. 예) 삼성전자, 현대자동차
                           item = ['S100300'], # 출력 변수 리스트. 예) 시가, 고가 (default : 수정 OLHCV)
                           from_date = '20230101', # 조회 시작 일자 (default : to_date-365일)
                           to_date ='20240624') # 조회 종료 일자 (default : 오늘 일자)
    
    # price_df = fs.get_data('stock_price', code = ['005930', '005380'])
