#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pandas as pd
from fnspace.core import FnSpace
import csv

def test_data_availability():
    # API 키 설정
    api_key = "Your API Key"
    fs = FnSpace(api_key)
    
    # 테스트할 데이터 카테고리
    categories = [
        'macro',
        'consensus-price',
        'consensus-earning-fiscal',
        'consensus-earning-daily',
        'consensus-forward'
    ]
    
    # 결과를 저장할 리스트
    all_results = []
    
    for category in categories:
        print(f"\n===== {category} 데이터 테스트 시작 =====")
        
        # 해당 카테고리 항목만 필터링
        items = fs.item_df[fs.item_df['DATA_TYPE'] == category].copy()
        
        if items.empty:
            print(f"{category} 데이터 항목이 없습니다.")
            continue
            
        total_items = len(items)
        print(f"총 {total_items}개 항목 테스트 시작...")
        
        # 샘플 종목코드 (삼성전자, 현대차)
        sample_codes = ['005930', '005380']
        
        for i, (idx, row) in enumerate(items.iterrows()):
            item_cd = row['ITEM_CD']
            item_nm = row['ITEM_NM_KOR'] if 'ITEM_NM_KOR' in row else row['ITEM_CD']
            
            print(f"테스트 중 ({i+1}/{total_items}): {item_cd} - {item_nm}")
            
            try:
                # 항목 테스트 (카테고리에 따라 다른 파라미터 사용)
                if category == 'macro':
                    df = fs.get_data(
                        category=category,
                        item=[item_cd],
                        from_date='20240101',
                        to_date='20240624'
                    )
                # 컨센서스 데이터는 종목코드 필요
                else:
                    df = fs.get_data(
                        category=category,
                        item=[item_cd],
                        code=sample_codes,
                        from_date='20230101',
                        to_date='20240624',
                        from_year='2023',
                        to_year='2024',
                        consolgb='M',
                        annualgb='A'
                    )
                
                # 결과 기록
                is_available = 'Y' if df is not None and not df.empty else 'N'
                all_results.append({
                    'DATA_TYPE': category,
                    'ITEM_CD': item_cd,
                    'ITEM_NM_KOR': item_nm,
                    'IS_AVAILABLE': is_available
                })
                
                print(f"  결과: {'성공' if is_available == 'Y' else '실패'}")
                
            except Exception as e:
                print(f"  오류 발생: {e}")
                all_results.append({
                    'DATA_TYPE': category,
                    'ITEM_CD': item_cd,
                    'ITEM_NM_KOR': item_nm,
                    'IS_AVAILABLE': 'N'
                })
    
    # 결과를 DataFrame으로 변환
    results_df = pd.DataFrame(all_results)
    
    # 카테고리별로 성공/실패 집계
    print("\n===== 테스트 결과 요약 =====")
    for category in categories:
        cat_results = results_df[results_df['DATA_TYPE'] == category]
        if not cat_results.empty:
            success_count = len(cat_results[cat_results['IS_AVAILABLE'] == 'Y'])
            fail_count = len(cat_results[cat_results['IS_AVAILABLE'] == 'N'])
            total = len(cat_results)
            print(f"{category}: 총 {total}개 중 성공 {success_count}개, 실패 {fail_count}개")
    
    return results_df

def update_item_list_csv(results_df):
    # GitHub에서 최신 ITEM_LIST.csv 파일 다운로드
    fs = FnSpace("dummy_key")  # 아무 키나 사용 (API 호출 안 함)
    item_df = fs.item_df.copy()
    
    # IS_AVAILABLE 컬럼 초기화 (모든 항목을 'Y'로 설정)
    item_df['IS_AVAILABLE'] = 'Y'
    
    # 테스트 결과에 따라 항목의 IS_AVAILABLE 업데이트
    for idx, row in results_df.iterrows():
        item_cd = row['ITEM_CD']
        is_available = row['IS_AVAILABLE']
        
        item_df.loc[item_df["ITEM_CD"]==item_cd, 'IS_AVAILABLE'] = is_available
    
    # 결과 저장
    item_df.to_csv('ITEM_LIST.csv', encoding='ANSI')
    print("\nITEM_LIST_UPDATED.csv 파일에 결과가 저장되었습니다.")
    
    # 이용 불가능한 항목만 따로 CSV로 저장
    unavailable_items = results_df[results_df['IS_AVAILABLE'] == 'N']
    if not unavailable_items.empty:
        unavailable_items.to_csv('unavailable_items.csv', encoding='ANSI', index=False)
        print("이용 불가능한 항목만 unavailable_items.csv 파일에 저장되었습니다.")

if __name__ == "__main__":
    # 각 데이터 항목 테스트
    results_df = test_data_availability()
    
    # ITEM_LIST.csv 파일 업데이트
    update_item_list_csv(results_df) 