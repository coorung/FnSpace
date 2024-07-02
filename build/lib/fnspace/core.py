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
import json

class FnSpace(object):
    def __init__(self, api_key):
        self.api_key = api_key
        self.id_dict = {"stock_price" : "A000001", 
                        "account" : "A000002",
                        "consensus-price" : "A000003",
                        "consensus-earning-fiscal" : "A000004",
                        "consensus-earning-daily" : "A000005",
                        "consensus-forward" : "A000006",
                        "macro" : "A000007"
                        }
        
        # item_cd와 한글명 포함된 csv load
        self.item_df = pd.read_csv("../ITEM_LIST.csv", encoding="ANSI", index_col=0)

    def get_data(self, category, **kwargs):
        """
        Sends a request to the API using the provided parameters.
    
        :param kwargs: Keywords required for the API request
        :return: The requested data in DataFrame format
        """
        
        # Include API key and convert kwargs format to fit request url format
        if category == 'item_list':

            try :
                data_type = self.id_dict[kwargs.get("data_type")]
            
            except ValueError:
                print("Please enter 'data_type' one of the following ; \n 'stock_price', 'account', 'consensus-price', 'consensus-earning-fiscal', 'consensus-earning-daily', 'consensus-forward', 'macro'")
                return None
                
            # Setting the base URL
            base_url = 'https://www.fnspace.com/Api/ItemListApi'
            
            params = {
                'key' : self.api_key,
                'format': 'json',
                'apigb': data_type
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
                
                if json_data["success"] != 'true':
                    print("Data Loading failed. : {}".format(json_data["errmsg"]))
                    
                df = pd.DataFrame(json_data['dataset'])
                return df
            
            except ValueError:
                print("Failed to convert JSON data")
                return None
        
        elif category == 'stock_list':
    
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
            all_list = self.item_df[self.item_df['DATA_TYPE'] == category]['ITEM_CD'].tolist()
            codes = kwargs.get('code', [])
            items = kwargs.get('item', all_list)

            # Check if 'code' and 'item' are single strings and convert them to lists if so
            if isinstance(codes, str):
                codes = [codes]
            if isinstance(items, str):
                items = [items]
            
            # Setting the base URL
            base_url = 'https://www.fnspace.com/Api/FinanceApi'
            
            requested_codes = set(f"A{x}" for x in codes)
            
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
                
                if json_data["success"] != 'true':
                    print("Data Loading failed. : {}".format(json_data["errmsg"]))
                    
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
                
                if kwargs.get("kor_item_name", False):
                    kor_items = self.item_df[self.item_df["ITEM_CD"].isin(items)].set_index('ITEM_CD')["ITEM_NM_KOR"].to_dict()
                    df = df.rename(columns=kor_items)
                    
                return df
            
            except ValueError:
                print("Failed to convert JSON data")
                return None
        
        elif category == 'stock_price':
            
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
            
            requested_codes = set(f"A{x}" for x in codes)
            
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
                
                if json_data["success"] != 'true':
                    print("Data Loading failed. : {}".format(json_data["errmsg"]))
                    
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
                
                if kwargs.get("kor_item_name", False):
                    kor_items = self.item_df[self.item_df["ITEM_CD"].isin(items)].set_index('ITEM_CD')["ITEM_NM_KOR"].to_dict()
                    df = df.rename(columns=kor_items)
                    
                return df
            
            except ValueError:
                print("Failed to convert JSON data")
                return None
            
        elif category == "macro":
            
            base_url = 'https://www.fnspace.com/Api/EconomyApi'
            
            all_list = self.item_df[self.item_df['DATA_TYPE'] == category]['ITEM_CD'].tolist()

            items = kwargs.get('item', all_list)

            # Check if 'item' is single strings and convert them to lists if so
            if isinstance(items, str):
                items = [items]
            
            # Setting the base URL
   
            params = {
                'key' : self.api_key,
                'format': 'json',
                'item': ','.join(items),
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
                if json_data["success"] != 'true':
                    print("Data Loading failed. : {}".format(json_data["errmsg"]))
                df = pd.DataFrame(json_data['dataset'])
                
                if kwargs.get("kor_item_name", False):
                    kor_items = self.item_df[self.item_df["ITEM_CD"].isin(items)].set_index('ITEM_CD')["ITEM_NM_KOR"].to_dict()
                    df = df.rename(columns=kor_items)
                
                return df
            
            except ValueError:
                print("Failed to convert JSON data")
                return None
        
        elif category == "consensus-price":
            
            base_url = 'https://www.fnspace.com/Api/Consensus1Api'
            
            all_list = self.item_df[self.item_df['DATA_TYPE'] == category]['ITEM_CD'].tolist()

            # Ensure that 'code' and 'item' are lists
            codes = kwargs.get('code', [])
            items = kwargs.get('item', all_list)

            # Check if 'code' and 'item' are single strings and convert them to lists if so
            if isinstance(codes, str):
                codes = [codes]
            if isinstance(items, str):
                items = [items]
            
            
            # Setting the base URL
            requested_codes = set(f"A{x}" for x in codes)
        
            params = {
                'key' : self.api_key,
                'format': 'json',
                'code': ','.join(requested_codes),
                'item': ','.join(items),
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
                
                if json_data["success"] != 'true':
                    print("Data Loading failed. : {}".format(json_data["errmsg"]))
                    
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
                
                if kwargs.get("kor_item_name", False):
                    kor_items = self.item_df[self.item_df["ITEM_CD"].isin(items)].set_index('ITEM_CD')["ITEM_NM_KOR"].to_dict()
                    df = df.rename(columns=kor_items)
                    
                return df
            
            except ValueError:
                print("Failed to convert JSON data")
                return None
        
        elif category == 'consensus-earning-fiscal':
            
            # Ensure that 'code' and 'item' are lists
            all_list = self.item_df[self.item_df['DATA_TYPE'] == category]['ITEM_CD'].tolist()
            codes = kwargs.get('code', [])
            items = kwargs.get('item', all_list)

            # Check if 'code' and 'item' are single strings and convert them to lists if so
            if isinstance(codes, str):
                codes = [codes]
            if isinstance(items, str):
                items = [items]
            
            # Setting the base URL
            base_url = 'https://www.fnspace.com/Api/Consensus2Api'
            
            requested_codes = set(f"A{x}" for x in codes)
            
            params = {
                'key' : self.api_key,
                'format': 'json',
                'code': ','.join(requested_codes),
                'item': ','.join(items),
                'consolgb': kwargs.get('consolgb', 'M'),
                'annualgb': kwargs.get('annualgb', 'A'),
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
                
                if json_data["success"] != 'true':
                    print("Data Loading failed. : {}".format(json_data["errmsg"]))
                    
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
                
                if kwargs.get("kor_item_name", False):
                    kor_items = self.item_df[self.item_df["ITEM_CD"].isin(items)].set_index('ITEM_CD')["ITEM_NM_KOR"].to_dict()
                    df = df.rename(columns=kor_items)
                    
                return df
            
            except ValueError:
                print("Failed to convert JSON data")
                return None
        
        elif category == 'consensus-earning-daily':
            
            # Ensure that 'code' and 'item' are lists
            all_list = self.item_df[self.item_df['DATA_TYPE'] == category]['ITEM_CD'].tolist()
            codes = kwargs.get('code', [])
            items = kwargs.get('item', all_list)

            # Check if 'code' and 'item' are single strings and convert them to lists if so
            if isinstance(codes, str):
                codes = [codes]
            if isinstance(items, str):
                items = [items]
            
            # Setting the base URL
            base_url = 'https://www.fnspace.com/Api/Consensus3Api'
            
            requested_codes = set(f"A{x}" for x in codes)
            
            params = {
                'key' : self.api_key,
                'format': 'json',
                'code': ','.join(requested_codes),
                'item': ','.join(items),
                'consolgb': kwargs.get('consolgb', 'M'),
                'annualgb': kwargs.get('annualgb', 'A'),
                'fraccyear': kwargs.get('from_year', str(datetime.datetime.now().year-1)),
                'toaccyear': kwargs.get('to_year', str(datetime.datetime.now().year-1)),
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
                
                if json_data["success"] != 'true':
                    print("Data Loading failed. : {}".format(json_data["errmsg"]))
                    
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
                
                if kwargs.get("kor_item_name", False):
                    kor_items = self.item_df[self.item_df["ITEM_CD"].isin(items)].set_index('ITEM_CD')["ITEM_NM_KOR"].to_dict()
                    df = df.rename(columns=kor_items)
                    
                return df
            
            except ValueError:
                print("Failed to convert JSON data")
                return None
        
        elif category == 'consensus-forward':
            # Ensure that 'code' and 'item' are lists
            all_list = self.item_df[self.item_df['DATA_TYPE'] == category]['ITEM_CD'].tolist()
            codes = kwargs.get('code', [])
            items = kwargs.get('item', all_list)

            # Check if 'code' and 'item' are single strings and convert them to lists if so
            if isinstance(codes, str):
                codes = [codes]
            if isinstance(items, str):
                items = [items]
            
            # Setting the base URL
            base_url = 'https://www.fnspace.com/Api/Consensus4Api'
            
            requested_codes = set(f"A{x}" for x in codes)
            
            params = {
                'key' : self.api_key,
                'format': 'json',
                'code': ','.join(requested_codes),
                'item': ','.join(items),
                'consolgb': kwargs.get('consolgb', 'M'),
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
                
                if json_data["success"] != 'true':
                    print("Data Loading failed. : {}".format(json_data["errmsg"]))
                    
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
                
                if kwargs.get("kor_item_name", False):
                    kor_items = self.item_df[self.item_df["ITEM_CD"].isin(items)].set_index('ITEM_CD')["ITEM_NM_KOR"].to_dict()
                    df = df.rename(columns=kor_items)
                    
                return df
            
            except ValueError:
                print("Failed to convert JSON data")
                return None
        
        else:
            print("Please check your category name of the folling ; \n 'stock_price', 'account', 'consensus-price', 'consensus-earning-fiscal', 'consensus-earning-daily', 'consensus-forward', 'macro' " )
       
#%%
if __name__ == '__main__':
            
    # API 키 설정 및 FnSpace 인스턴스 생성
    api_key = "Your API key"
    fs = FnSpace(api_key)
    
    
    # 1. 출력 변수 목록 불러오기
    item_df = fs.get_data(category="item_list", data_type="account") # 재무 데이터의 출력 변수 리스트
    
    
    # 2. 재무 데이터 불러오기
    
    account_df = fs.get_data(category = 'account', 
                             code = ['005930', '005380'], # 종목코드 리스트. 예) 삼성전자, 현대자동차
                             item = ['M122700', 'M123955'], # 출력 변수 리스트. 예) 당기순이익, 보고서발표일 (default : 전체 item)
                             consolgb = 'M', # 회계기준. 주재무제표(M)/연결(C)/별도(I) (default : 주재무제표(M))
                             annualgb = 'A', # 연간(A)/분기(QQ)/분기누적(QY) (default : 연간(A))
                             accdategb = 'C', # 컨센서스 결산년월 선택 기준. Calendar(C)/Fiscal(F) (default : Calendar(C))
                             from_year = '2020', # 조회 시작 연도 (default : 직전 연도)
                             to_year = '2020', # 조회 종료 연도 (default : 직전 연도)
                             kor_item_name = True # 컬럼명 한글 출력 여부 (default : ITEM_CD 그대로)
                             )

    
    # 3. 주식 리스트 데이터 불러오기
    
    stock_list_df = fs.get_data(category = 'stock_list', 
                                mkttype ='4', # KOSPI(1)/KOSDAQ(2)/KONEX(3)/KOSPI+KOSDAQ(4)/KOSPI200(5)/KOSDAQ150(6)
                                date ='20240624') # 조회 기준일
    
    # 4. 주가 데이터 불러오기
    
    price_df = fs.get_data(category = 'stock_price', 
                           code = ['005930', '005380'], # 종목코드 리스트. 예) 삼성전자, 현대자동차
                           item = ['S100300'], # 출력 변수 리스트. 예) 시가, 고가 (default : 수정 OLHCV)
                           from_date = '20230101', # 조회 시작 일자 (default : to_date-365일)
                           to_date ='20240624') # 조회 종료 일자 (default : 오늘 일자)
    
    # 5. 경제 데이터 불러오기 => 현재 출력 X
    price_df = fs.get_data(category = 'macro', 
                           item = ['aKONA10NIGDPW', 'aKONA10GSGSR'], # 출력 변수 리스트. 예) 국민총소득(명목,원화)(십억원), 총저축률(명목)(%) (default : 전체 item)
                           from_date = '20230101', # 조회 시작 일자 (default : to_date-365일)
                           to_date ='20240624', # 조회 종료 일자 (default : 오늘 일자)
                           kor_item_name=True) # 컬럼명 한글 출력 여부 (default : ITEM_CD 그대로)
    
    # 6. 컨센서스 데이터 불러오기
    ## 6-1) 컨센서스 - 투자의견 & 목표주가
    consensus_price_df = fs.get_data(category = 'consensus-price', 
                                    item = ['E612500'], # 출력 변수 리스트. 예) 국민총소득(명목,원화)(십억원), 총저축률(명목)(%) (default : 전체 item)
                                    code = ['005930', '005380'],
                                    from_date = '20230101', # 조회 시작 일자 (default : to_date-365일)
                                    to_date ='20240624',
                                    kor_item_name=True) # 컬럼명 한글 출력 여부 (default : ITEM_CD 그대로)
     
    ## 6-2) 컨센서스 - 추정실적 - Fiscal 조회
    consensus_earning_df = fs.get_data(category = 'consensus-earning-fiscal', 
                                   item = ['E122700'], # 출력 변수 리스트. 예) 당기순이익 (default : 전체 item)
                                   code = ['005930', '005380'],
                                   consolgb = "M", # 회계기준. 주재무제표(M)/연결(C)/별도(I) (default : 주재무제표(M))
                                   annualgb = "A", # 연간(A)/분기(QQ)/분기누적(QY) (default : 연간(A))
                                   from_year = "2023", # 조회 시작 연도 (default : 직전 연도)
                                   to_year = "2024", # 조회 종료 연도 (default : 직전 연도)
                                   kor_item_name=True) # 컬럼명 한글 출력 여부 (default : ITEM_CD 그대로)
    
    ## 6-3 컨센서스 - 추정실적 - daily 조회 => 서비스 도중 에러가 발생하였습니다. 관리자에게 문의하세요. 에러 
    consensus_earning_df = fs.get_data(category = 'consensus-earning-daily', 
                                   item = ['E121500'], # 출력 변수 리스트. 예) 당기순이익 (default : 전체 item)
                                   code = ['005930', '005380'],
                                   consolgb = "M", # 회계기준. 주재무제표(M)/연결(C)/별도(I) (default : 주재무제표(M))
                                   annualgb = "A", # 연간(A)/분기(QQ)/분기누적(QY) (default : 연간(A))
                                   from_year = "2023", # 조회 시작 연도 (default : 직전 연도)
                                   to_year = "2024", # 조회 종료 연도 (default : 직전 연도)
                                   from_date = "20230101", # 조회 시작 일자 (default : to_date-365일)
                                   to_date = "20240620", # 조회 종료 일자 (default : 오늘 일자)
                                   kor_item_name=True) # 컬럼명 한글 출력 여부 (default : ITEM_CD 그대로)
    
    ## 6-4 컨센서스 - forward 지표
    consensus_forward_df = fs.get_data(category = 'consensus-forward', 
                                   item = ['E121560'], # 출력 변수 리스트. 예) 영업이익(Fwd.12M) (default : 전체 item)
                                   code = ['005930', '005380'],
                                   consolgb = "M", # 회계기준. 주재무제표(M)/연결(C)/별도(I) (default : 주재무제표(M))
                                   from_date = "20230101", # 조회 시작 일자 (default : to_date-365일)
                                   to_date = "20240620", # 조회 종료 일자 (default : 오늘 일자)
                                   kor_item_name=True) # 컬럼명 한글 출력 여부 (default : ITEM_CD 그대로)
    

