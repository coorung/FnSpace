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
import os

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
        
        self.item_df = pd.read_csv("https://raw.githubusercontent.com/coorung/FnSpace/main/ITEM_LIST.csv", encoding="ANSI", index_col=0)
        # ITEM_NM_KOR 컬럼의 앞뒤 공백 제거
        if 'ITEM_NM_KOR' in self.item_df.columns:
            self.item_df['ITEM_NM_KOR'] = self.item_df['ITEM_NM_KOR'].str.strip()
        
        # IS_AVAILABLE 컬럼이 없으면 모든 항목을 'Y'로 초기화
        if 'IS_AVAILABLE' not in self.item_df.columns:
            self.item_df['IS_AVAILABLE'] = 'Y'

    def _filter_available_items(self, category, items):
        """
        항목 목록에서 IS_AVAILABLE='Y'인 항목만 필터링

        :param category: 데이터 카테고리
        :param items: 필터링할 항목 목록
        :return: (필터링된 항목 목록, 사용 불가능한 항목 목록)
        """
        # 리스트로 변환
        if isinstance(items, str):
            items = [items]
            
        # IS_AVAILABLE 필드 확인
        filtered_items = []
        unavailable_items = []
        
        for item in items:
            if item in self.item_df.index and self.item_df.loc[item, 'IS_AVAILABLE'] == 'N':
                unavailable_items.append(item)
            else:
                filtered_items.append(item)
        
        if unavailable_items:
            print(f"경고: 다음 항목들은 현재 API에서 지원하지 않아 제외됩니다: {', '.join(unavailable_items)}")
        
        if not filtered_items:
            print("사용 가능한 항목이 없습니다. 다른 항목을 선택해주세요.")
            
        return filtered_items, unavailable_items

    def _make_api_request(self, base_url, params):
        """
        API 요청을 수행하고 에러를 처리하는 공통 메서드

        :param base_url: API 기본 URL
        :param params: API 요청 파라미터
        :return: 성공 시 응답 객체, 실패 시 None
        """
        try:
            # API request
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            return response
        except requests.HTTPError as e:
            print(f"API HTTP 오류 발생: 상태 코드 {response.status_code}")
            print(f"URL: {response.url}")
            print(f"응답: {response.text[:500]}{'...' if len(response.text) > 500 else ''}")
            return None
        except requests.ConnectionError as e:
            print(f"API 연결 오류: {e}")
            print(f"URL: {base_url}")
            print(f"파라미터: {params}")
            return None
        except requests.Timeout as e:
            print(f"API 요청 시간 초과: {e}")
            print(f"URL: {base_url}")
            print(f"파라미터: {params}")
            return None
        except requests.RequestException as e:
            print(f"API 요청 오류 발생: {e}")
            print(f"URL: {base_url}")
            print(f"파라미터: {params}")
            return None

    def _process_json_response(self, response, requested_codes=None, kor_item_name=False, filtered_items=None):
        """
        JSON 응답을 처리하여 DataFrame으로 변환

        :param response: API 응답 객체
        :param requested_codes: 요청한 종목코드 집합 (선택적)
        :param kor_item_name: 한글 항목명 변환 여부
        :param filtered_items: 필터링된 항목 목록 (선택적)
        :return: 성공 시 DataFrame, 실패 시 None
        """
        try:
            # JSON 응답을 DataFrame으로 변환
            json_data = response.json()
            
            if json_data["success"] != 'true':
                print("데이터 로딩 실패: {}".format(json_data["errmsg"]))
                return None
            
            # 응답 구조에 따라 다른 처리 방식 적용
            if 'dataset' in json_data and isinstance(json_data['dataset'], list) and \
               len(json_data['dataset']) > 0 and 'DATA' in json_data['dataset'][0]:
                # CODE와 NAME이 별도로 있고 DATA가 리스트인 경우 (대부분의 API)
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
                
                if requested_codes and requested_codes != received_codes:
                    missing_codes = requested_codes - received_codes
                    if missing_codes:
                        print(f"경고: 다음 종목 코드에 대한 데이터가 없습니다: {', '.join(missing_codes)}")
                
                df = pd.DataFrame(data_entries)
            
            elif 'dataset' in json_data:
                # 단순 리스트 형태의 데이터셋 (일부 API)
                df = pd.DataFrame(json_data['dataset'])
            
            else:
                print("예상치 못한 JSON 구조")
                return None
            
            # 컬럼명이 ITEM_NM_KOR인 경우 공백 제거
            if 'ITEM_NM_KOR' in df.columns:
                df['ITEM_NM_KOR'] = df['ITEM_NM_KOR'].str.strip()
                
            # 한글 항목명으로 변환
            if kor_item_name and filtered_items:
                kor_items = self.item_df[self.item_df["ITEM_CD"].isin(filtered_items)].set_index('ITEM_CD')["ITEM_NM_KOR"].str.strip().to_dict()
                df = df.rename(columns=kor_items)
                
            return df
        
        except ValueError as e:
            print(f"JSON 데이터 변환 실패: {e}")
            if response:
                print(f"응답 내용: {response.text[:500]}{'...' if len(response.text) > 500 else ''}")
            return None
        except Exception as e:
            print(f"JSON 응답 처리 중 오류 발생: {e}")
            return None

    def get_data(self, category, **kwargs):
        """
        제공된 파라미터를 사용하여 API에 요청을 보냅니다.
    
        :param kwargs: API 요청에 필요한 키워드 인자
        :return: 요청한 데이터를 DataFrame 형식으로 반환
        """
        
        # API 키 포함 및 kwargs 형식을 요청 URL 형식에 맞게 변환
        if category == 'item_list':

            try:
                data_type = self.id_dict[kwargs.get("data_type")]
            
            except ValueError:
                print("'data_type'에 다음 값 중 하나를 입력해주세요: \n 'stock_price', 'account', 'consensus-price', 'consensus-earning-fiscal', 'consensus-earning-daily', 'consensus-forward', 'macro'")
                return None
                
            # 기본 URL 설정
            base_url = 'https://www.fnspace.com/Api/ItemListApi'
            
            params = {
                'key' : self.api_key,
                'format': 'json',
                'apigb': data_type
            }
            
            # API 요청 수행
            response = self._make_api_request(base_url, params)
            if response is None:
                return None
                
            # JSON 응답 처리
            api_df = self._process_json_response(response)
            
            if api_df is not None:
                # API 응답에 IS_AVAILABLE 컬럼 추가
                data_type_value = kwargs.get("data_type")
                
                # 데이터 타입에 맞는 항목만 필터링
                is_available_df = self.item_df[self.item_df['DATA_TYPE'] == data_type_value].copy()
                
                # ITEM_CD가 인덱스인 경우 컬럼으로 변환
                if 'ITEM_CD' not in api_df.columns and 'ITEM_CD' in api_df.index.names:
                    api_df = api_df.reset_index()
                
                # 두 데이터프레임 모두 ITEM_CD를 컬럼으로 가지고 있어야 함
                if 'ITEM_CD' in api_df.columns:
                    # ITEM_CD 타입 통일
                    api_df['ITEM_CD'] = api_df['ITEM_CD'].astype(str)
                    
                    # 데이터프레임 병합 (양쪽 모두 ITEM_CD 컬럼으로 병합)
                    merged_df = pd.merge(
                        api_df, 
                        is_available_df[['ITEM_CD', 'IS_AVAILABLE']], 
                        on='ITEM_CD', 
                        how='left'
                    )
                    
                    # IS_AVAILABLE이 NaN인 경우 'Y'로 채움
                    merged_df['IS_AVAILABLE'] = merged_df['IS_AVAILABLE'].fillna('Y')
                    return merged_df
            
            return api_df
        
        elif category == 'stock_list':
    
            # 기본 URL 설정
            base_url = 'https://www.fnspace.com/Api/CompanyListApi'
            params = {
                'key' : self.api_key,
                'format': 'json',
                'mkttype': kwargs.get('mkttype', '4'),
                'date': kwargs.get('date', datetime.datetime.now().date().strftime('%Y%m%d')),
            }
            
            # API 요청 수행
            response = self._make_api_request(base_url, params)
            if response is None:
                return None
                
            # JSON 응답 처리
            return self._process_json_response(response)
        
        elif category == 'account':
            
            # 'code'와 'item'이 리스트인지 확인
            all_list = self.item_df[self.item_df['DATA_TYPE'] == category]['ITEM_CD'].tolist()
            codes = kwargs.get('code', [])
            items = kwargs.get('item', all_list)

            # 'code'와 'item'이 문자열인 경우 리스트로 변환
            if isinstance(codes, str):
                codes = [codes]
            
            # 사용 가능한 항목 필터링
            filtered_items, _ = self._filter_available_items(category, items)
            if not filtered_items:
                return None
            
            # 기본 URL 설정
            base_url = 'https://www.fnspace.com/Api/FinanceApi'
            
            requested_codes = set(f"A{x}" for x in codes)
            
            params = {
                'key' : self.api_key,
                'format': 'json',
                'code': ','.join(requested_codes),
                'item': ','.join(filtered_items),
                'consolgb': kwargs.get('consolgb', 'M'),
                'annualgb': kwargs.get('annualgb', 'A'),
                'accdategb': kwargs.get('accdategb', 'C'),
                'fraccyear': kwargs.get('from_year', str(datetime.datetime.now().year-1)),
                'toaccyear': kwargs.get('to_year', str(datetime.datetime.now().year-1))
            }
            
            # API 요청 수행
            response = self._make_api_request(base_url, params)
            if response is None:
                return None
                
            # JSON 응답 처리
            return self._process_json_response(
                response, 
                requested_codes=requested_codes,
                kor_item_name=kwargs.get("kor_item_name", False),
                filtered_items=filtered_items
            )
        
        elif category == 'stock_price':
            
            # 'code'와 'item'이 리스트인지 확인
            codes = kwargs.get('code', [])
            items = kwargs.get('item', [])

            # 'code'와 'item'이 문자열인 경우 리스트로 변환
            if isinstance(codes, str):
                codes = [codes]
            
            # 사용 가능한 항목 필터링
            if items:
                filtered_items, _ = self._filter_available_items(category, items)
                if not filtered_items:
                    items = ['S100310', 'S100320', 'S100330', 'S100300', 'S100950']
                    print("사용 가능한 항목이 없어 기본 항목으로 대체합니다.")
                else:
                    items = filtered_items
            else:
                items = ['S100310', 'S100320', 'S100330', 'S100300', 'S100950']
            
            # 기본 URL 설정
            base_url = 'https://www.fnspace.com/Api/StockApi'
            
            requested_codes = set(f"A{x}" for x in codes)
            
            params = {
                'key' : self.api_key,
                'format': 'json',
                'code': ','.join(requested_codes),
                'item': ','.join(items),
                'frdate': kwargs.get('from_date', str((datetime.datetime.now()-timedelta(days=365)).strftime("%Y%m%d"))),
                'todate': kwargs.get('to_date', str(datetime.datetime.now().strftime("%Y%m%d"))),
            }
            
            # API 요청 수행
            response = self._make_api_request(base_url, params)
            if response is None:
                return None
                
            # JSON 응답 처리
            return self._process_json_response(
                response, 
                requested_codes=requested_codes,
                kor_item_name=kwargs.get("kor_item_name", False),
                filtered_items=items
            )
            
        elif category == "macro":
            
            base_url = 'https://www.fnspace.com/Api/EconomyApi'
            
            all_list = self.item_df[self.item_df['DATA_TYPE'] == category]['ITEM_CD'].tolist()

            items = kwargs.get('item', all_list)
            
            # 사용 가능한 항목 필터링
            filtered_items, _ = self._filter_available_items(category, items)
            if not filtered_items:
                return None
            
            # 기본 URL 설정
            params = {
                'key' : self.api_key,
                'format': 'json',
                'item': ','.join(filtered_items),
                'frdate': kwargs.get('from_date', str((datetime.datetime.now()-timedelta(days=365)).strftime("%Y%m%d"))),
                'todate': kwargs.get('to_date', str(datetime.datetime.now().strftime("%Y%m%d"))),
            }
            
            # API 요청 수행
            response = self._make_api_request(base_url, params)
            if response is None:
                return None
                
            # JSON 응답 처리
            return self._process_json_response(
                response,
                kor_item_name=kwargs.get("kor_item_name", False),
                filtered_items=filtered_items
            )
        
        elif category == "consensus-price":
            
            base_url = 'https://www.fnspace.com/Api/Consensus1Api'
            
            all_list = self.item_df[self.item_df['DATA_TYPE'] == category]['ITEM_CD'].tolist()

            # 'code'와 'item'이 리스트인지 확인
            codes = kwargs.get('code', [])
            items = kwargs.get('item', all_list)

            # 'code'와 'item'이 문자열인 경우 리스트로 변환
            if isinstance(codes, str):
                codes = [codes]
            
            # 사용 가능한 항목 필터링
            filtered_items, _ = self._filter_available_items(category, items)
            if not filtered_items:
                return None
            
            # 기본 URL 설정
            requested_codes = set(f"A{x}" for x in codes)
        
            params = {
                'key' : self.api_key,
                'format': 'json',
                'code': ','.join(requested_codes),
                'item': ','.join(filtered_items),
                'frdate': kwargs.get('from_date', str((datetime.datetime.now()-timedelta(days=365)).strftime("%Y%m%d"))),
                'todate': kwargs.get('to_date', str(datetime.datetime.now().strftime("%Y%m%d"))),
            }
            
            # API 요청 수행
            response = self._make_api_request(base_url, params)
            if response is None:
                return None
                
            # JSON 응답 처리
            return self._process_json_response(
                response, 
                requested_codes=requested_codes,
                kor_item_name=kwargs.get("kor_item_name", False),
                filtered_items=filtered_items
            )
        
        elif category == 'consensus-earning-fiscal':
            
            # 'code'와 'item'이 리스트인지 확인
            all_list = self.item_df[self.item_df['DATA_TYPE'] == category]['ITEM_CD'].tolist()
            codes = kwargs.get('code', [])
            items = kwargs.get('item', all_list)

            # 'code'와 'item'이 문자열인 경우 리스트로 변환
            if isinstance(codes, str):
                codes = [codes]
            
            # 사용 가능한 항목 필터링
            filtered_items, _ = self._filter_available_items(category, items)
            if not filtered_items:
                return None
            
            # 기본 URL 설정
            base_url = 'https://www.fnspace.com/Api/Consensus2Api'
            
            requested_codes = set(f"A{x}" for x in codes)
            
            params = {
                'key' : self.api_key,
                'format': 'json',
                'code': ','.join(requested_codes),
                'item': ','.join(filtered_items),
                'consolgb': kwargs.get('consolgb', 'M'),
                'annualgb': kwargs.get('annualgb', 'A'),
                'accdategb': kwargs.get('accdategb', 'C'),
                'fraccyear': kwargs.get('from_year', str(datetime.datetime.now().year-1)),
                'toaccyear': kwargs.get('to_year', str(datetime.datetime.now().year-1))
            }
            
            # API 요청 수행
            response = self._make_api_request(base_url, params)
            if response is None:
                return None
                
            # JSON 응답 처리
            return self._process_json_response(
                response, 
                requested_codes=requested_codes,
                kor_item_name=kwargs.get("kor_item_name", False),
                filtered_items=filtered_items
            )
        
        elif category == 'consensus-earning-daily':
            
            # 'code'와 'item'이 리스트인지 확인
            all_list = self.item_df[self.item_df['DATA_TYPE'] == category]['ITEM_CD'].tolist()
            codes = kwargs.get('code', [])
            items = kwargs.get('item', all_list)

            # 'code'와 'item'이 문자열인 경우 리스트로 변환
            if isinstance(codes, str):
                codes = [codes]
            
            # 사용 가능한 항목 필터링
            filtered_items, _ = self._filter_available_items(category, items)
            if not filtered_items:
                return None
            
            # 기본 URL 설정
            base_url = 'https://www.fnspace.com/Api/Consensus3Api'
            
            requested_codes = set(f"A{x}" for x in codes)
            
            params = {
                'key' : self.api_key,
                'format': 'json',
                'code': ','.join(requested_codes),
                'item': ','.join(filtered_items),
                'consolgb': kwargs.get('consolgb', 'M'),
                'annualgb': kwargs.get('annualgb', 'A'),
                'accdategb': kwargs.get('accdategb', 'C'),
                'fraccyear': kwargs.get('from_year', str(datetime.datetime.now().year-1)),
                'toaccyear': kwargs.get('to_year', str(datetime.datetime.now().year-1)),
                'frdate': kwargs.get('from_date', str((datetime.datetime.now()-timedelta(days=365)).strftime("%Y%m%d"))),
                'todate': kwargs.get('to_date', str(datetime.datetime.now().strftime("%Y%m%d"))),
            }
            
            # API 요청 수행
            response = self._make_api_request(base_url, params)
            if response is None:
                return None
                
            # JSON 응답 처리
            return self._process_json_response(
                response, 
                requested_codes=requested_codes,
                kor_item_name=kwargs.get("kor_item_name", False),
                filtered_items=filtered_items
            )
        
        elif category == 'consensus-forward':
            # 'code'와 'item'이 리스트인지 확인
            all_list = self.item_df[self.item_df['DATA_TYPE'] == category]['ITEM_CD'].tolist()
            codes = kwargs.get('code', [])
            items = kwargs.get('item', all_list)

            # 'code'와 'item'이 문자열인 경우 리스트로 변환
            if isinstance(codes, str):
                codes = [codes]
            
            # 사용 가능한 항목 필터링
            filtered_items, _ = self._filter_available_items(category, items)
            if not filtered_items:
                return None
            
            # 기본 URL 설정
            base_url = 'https://www.fnspace.com/Api/Consensus4Api'
            
            requested_codes = set(f"A{x}" for x in codes)
            
            params = {
                'key' : self.api_key,
                'format': 'json',
                'code': ','.join(requested_codes),
                'item': ','.join(filtered_items),
                'consolgb': kwargs.get('consolgb', 'M'),
                'frdate': kwargs.get('from_date', str((datetime.datetime.now()-timedelta(days=365)).strftime("%Y%m%d"))),
                'todate': kwargs.get('to_date', str(datetime.datetime.now().strftime("%Y%m%d"))),
            }
            
            # API 요청 수행
            response = self._make_api_request(base_url, params)
            if response is None:
                return None
                
            # JSON 응답 처리
            return self._process_json_response(
                response, 
                requested_codes=requested_codes,
                kor_item_name=kwargs.get("kor_item_name", False),
                filtered_items=filtered_items
            )
        
        else:
            print("카테고리 이름을 확인해주세요. 다음 중 하나여야 합니다: \n 'stock_price', 'account', 'consensus-price', 'consensus-earning-fiscal', 'consensus-earning-daily', 'consensus-forward', 'macro'")
            return None

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
    

