# -*- coding: utf-8 -*-
"""
Created on Wed May  7 08:24:38 2025

@author: coorung77
"""


import requests
import datetime
from datetime import timedelta
import pandas as pd
import json
from fnspace import FnSpace

#%%
if __name__ == '__main__':
            
    # API 키 설정 및 FnSpace 인스턴스 생성
    api_key = "your API key"
    fs = FnSpace(api_key)
    
    # 1. 출력 변수 목록 불러오기
    item_df = fs.get_data(category="item_list", data_type="account") # 재무 데이터의 출력 변수 리스트
    item_df = fs.get_data(category="item_list", data_type="macro") # 재무 데이터의 출력 변수 리스트
    item_df = fs.get_data(category="item_list", data_type="consensus-earning-daily") # 재무 데이터의 출력 변수 리스트
    
    
    # 2. 재무 데이터 불러오기
    account_df = fs.get_data(category = 'account', 
                             code = ['005930', '005380'], # 종목코드 리스트. 예) 삼성전자, 현대자동차
                             item = ['M122700', 'M123955'], # 출력 변수 리스트. 예) 당기순이익, 보고서발표일 (default : 전체 item)
                             consolgb = 'M', # 회계기준. 주재무제표(M)/연결(C)/별도(I) (default : 주재무제표(M))
                             annualgb = 'A', # 연간(A)/분기(QQ)/분기누적(QY) (default : 연간(A))
                             accdategb = 'C', # 컨센서스 결산년월 선택 기준. Calendar(C)/Fiscal(F) (default : Calendar(C))
                             from_year = '2024', # 조회 시작 연도 (default : 직전 연도)
                             to_year = '2025', # 조회 종료 연도 (default : 직전 연도)
                             kor_item_name = True # 컬럼명 한글 출력 여부 (default : ITEM_CD 그대로)
                             )

    
    # 3. 주식 리스트 데이터 불러오기
    stock_list_df = fs.get_data(category = 'stock_list', 
                                mkttype ='4', # KOSPI(1)/KOSDAQ(2)/KONEX(3)/KOSPI+KOSDAQ(4)/KOSPI200(5)/KOSDAQ150(6)
                                date ='20250507') # 조회 기준일
    
    # 4. 주가 데이터 불러오기
    price_df = fs.get_data(category = 'stock_price', 
                           code = ['005930', '005380'], # 종목코드 리스트. 예) 삼성전자, 현대자동차
                           item = ['S100300'], # 출력 변수 리스트. 예) 시가, 고가 (default : 수정 OLHCV)
                           from_date = '20230101', # 조회 시작 일자 (default : to_date-365일)
                           to_date ='20240624') # 조회 종료 일자 (default : 오늘 일자)
    
    # 5. 경제 데이터 불러오기 
    macro_df = fs.get_data(category = 'macro', 
                           item = ['arKOFXUSDD', 'aKOPSCCSDHCN', 'aaKOMBM2A', 'aaKOBP', 'aaKOEITB'], # 출력 변수 리스트. 예) 원달러환율, 부도업체 수, M2통화량(십억원), 경상수지(백만달러), 무역수지(천달러)
                           from_date = '20240101', # 조회 시작 일자 (default : to_date-365일)
                           to_date ='20250507', # 조회 종료 일자 (default : 오늘 일자)
                           kor_item_name=True) # 컬럼명 한글 출력 여부 (default : ITEM_CD 그대로)
    
    # 6. 컨센서스 데이터 불러오기
    ## 6-1) 컨센서스 - 투자의견 & 목표주가
    consensus_price_df = fs.get_data(category = 'consensus-price', 
                                    item = ['E610100', 'E612500'], # 출력 변수 리스트. 예) 투자의견, 목표주가(Adj.)
                                    code = ['005930', '005380'],
                                    from_date = '20230101', # 조회 시작 일자 (default : to_date-365일)
                                    to_date ='20250507',
                                    kor_item_name=True) # 컬럼명 한글 출력 여부 (default : ITEM_CD 그대로)
     
    ## 6-2) 컨센서스 - 추정실적 - Fiscal 조회
    consensus_earning_df = fs.get_data(category = 'consensus-earning-fiscal', 
                                   item = ['E122700'], # 출력 변수 리스트. 예) 당기순이익 (default : 전체 item)
                                   code = ['005930', '005380'],
                                   consolgb = "M", # 회계기준. 주재무제표(M)/연결(C)/별도(I) (default : 주재무제표(M))
                                   annualgb = "A", # 연간(A)/분기(Q) (default : 연간(A))
                                   from_year = "2023", # 조회 시작 연도 (default : 직전 연도)
                                   to_year = "2024", # 조회 종료 연도 (default : 직전 연도)
                                   kor_item_name=True) # 컬럼명 한글 출력 여부 (default : ITEM_CD 그대로)
    
    ## 6-3 컨센서스 - 추정실적 - daily 조회 
    consensus_earning_df = fs.get_data(category = 'consensus-earning-daily',
                                    item = ['E121500'], # 출력 변수 리스트. 예) 당기순이익
                                    code = ['005930', '005380'],
                                    consolgb = "M", # 회계기준. 주재무제표(M)/연결(C)/별도(I) (default : 주재무제표(M))
                                    annualgb = "A", # 연간(A)/분기(Q) (default : 연간(A))
                                    accdategb = "C", # 컨센서스 결산년월 선택 기준. Calendar(C)/Fiscal(F)/Present Base(P) (default : Calendar(C))
                                    from_year = "2023", # 조회 시작 연도 (default : 직전 연도)
                                    to_year = "2024", # 조회 종료 연도 (default : 직전 연도)
                                    from_date = "20230101", # 조회 시작 일자 (default : to_date-365일)
                                    to_date = "20240620", # 조회 종료 일자 (default : 오늘 일자)
                                    kor_item_name=True # 컬럼명 한글 출력 여부 (default : ITEM_CD 그대로)
                                )
    
    ## 6-4 컨센서스 - forward 지표
    consensus_forward_df = fs.get_data(category = 'consensus-forward', 
                                   item = ['E121560'], # 출력 변수 리스트. 예) 영업이익(Fwd.12M) (default : 전체 item)
                                   code = ['005930', '005380'],
                                   consolgb = "M", # 회계기준. 주재무제표(M)/연결(C)/별도(I) (default : 주재무제표(M))
                                   from_date = "20230101", # 조회 시작 일자 (default : to_date-365일)
                                   to_date = "20240620", # 조회 종료 일자 (default : 오늘 일자)
                                   kor_item_name=True) # 컬럼명 한글 출력 여부 (default : ITEM_CD 그대로)
    