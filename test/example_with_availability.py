#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fnspace.core import FnSpace
import pandas as pd

def main():
    # API 키 설정
    api_key = "Your API Key"  # 실제 사용 시 API 키로 변경
    fs = FnSpace(api_key)
    
    # 1. 사용 가능한 경제 데이터 항목만 필터링해서 확인
    available_macro = fs.item_df[(fs.item_df['DATA_TYPE'] == 'macro') & 
                               (fs.item_df['IS_AVAILABLE'] == 'Y')]
    
    print(f"사용 가능한 경제 데이터(macro) 항목 수: {len(available_macro)}")
    print(f"사용 불가능한 경제 데이터(macro) 항목 수: {len(fs.item_df[(fs.item_df['DATA_TYPE'] == 'macro') & (fs.item_df['IS_AVAILABLE'] == 'N')])}")
    
    # 카테고리별 사용 가능한 항목 수 확인
    print("\n=== 카테고리별 사용 가능한 항목 수 ===")
    categories = fs.item_df['DATA_TYPE'].unique()
    for category in categories:
        available = len(fs.item_df[(fs.item_df['DATA_TYPE'] == category) & (fs.item_df['IS_AVAILABLE'] == 'Y')])
        total = len(fs.item_df[fs.item_df['DATA_TYPE'] == category])
        print(f"{category}: {available}/{total} ({available/total*100:.1f}%)")
    
    # 2. 사용 가능한 항목으로만 데이터 요청 예제
    
    # 예제 1: 사용 가능한 경제 데이터 항목 중 첫 5개로 데이터 요청
    print("\n=== 사용 가능한 경제 데이터 요청 예제 ===")
    if not available_macro.empty:
        sample_items = available_macro.index[:5].tolist()
        print(f"요청할 항목: {sample_items}")
        
        macro_data = fs.get_data(
            category='macro',
            item=sample_items,
            from_date='20230101',
            to_date='20240624'
        )
        
        if macro_data is not None and not macro_data.empty:
            print(f"데이터 요청 성공! 결과 크기: {macro_data.shape}")
        else:
            print("데이터 요청 실패 또는 결과 없음")
    
    # 예제 2: 컨센서스 데이터 요청
    print("\n=== 사용 가능한 컨센서스 데이터 요청 예제 ===")
    available_consensus = fs.item_df[(fs.item_df['DATA_TYPE'] == 'consensus-earning-fiscal') & 
                                  (fs.item_df['IS_AVAILABLE'] == 'Y')]
    
    if not available_consensus.empty:
        sample_items = available_consensus.index[:3].tolist()
        print(f"요청할 항목: {sample_items}")
        
        consensus_data = fs.get_data(
            category='consensus-earning-fiscal',
            item=sample_items,
            code=['005930', '005380'],  # 삼성전자, 현대차
            from_year='2023',
            to_year='2024',
            consolgb='M',
            annualgb='A'
        )
        
        if consensus_data is not None and not consensus_data.empty:
            print(f"데이터 요청 성공! 결과 크기: {consensus_data.shape}")
        else:
            print("데이터 요청 실패 또는 결과 없음")
    
    # 3. 주가 데이터 요청 예제
    print("\n=== 주가 데이터 요청 예제 ===")
    available_stock = fs.item_df[(fs.item_df['DATA_TYPE'] == 'stock_price') & 
                              (fs.item_df['IS_AVAILABLE'] == 'Y')]
    
    if not available_stock.empty:
        sample_items = available_stock.index[:3].tolist() if not available_stock.empty else []
        print(f"요청할 항목: {sample_items}")
        
        stock_data = fs.get_data(
            category='stock_price',
            item=sample_items,
            code=['005930', '005380'],  # 삼성전자, 현대차
            from_date='20230101',
            to_date='20240624'
        )
        
        if stock_data is not None and not stock_data.empty:
            print(f"데이터 요청 성공! 결과 크기: {stock_data.shape}")
        else:
            print("데이터 요청 실패 또는 결과 없음")

if __name__ == "__main__":
    main() 