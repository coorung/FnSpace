#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pandas as pd
from fnspace.core import FnSpace
import csv

def test_macro_items():
    # API 키 설정
    api_key = "Your API Key"
    fs = FnSpace(api_key)
    
    # 경제 데이터 관련 항목만 필터링
    macro_items = fs.item_df[fs.item_df['DATA_TYPE'] == 'macro'].copy()
    
    # 결과를 저장할 리스트
    results = []
    
    # 각 항목 테스트
    total_items = len(macro_items)
    print(f"총 {total_items}개 항목 테스트 시작...")
    
    for i, (idx, row) in enumerate(macro_items.iterrows()):
        item_cd = row['ITEM_CD']
        item_nm = row['ITEM_NM_KOR'] if 'ITEM_NM_KOR' in row else row['ITEM_CD']
        
        print(f"테스트 중 ({i+1}/{total_items}): {item_cd} - {item_nm}")
        
        try:
            # 항목 테스트
            df = fs.get_data(
                category='macro',
                item=[item_cd],
                from_date='20230101',
                to_date='20240624'
            )
            
            # 결과 기록
            is_available = 'Y' if df is not None and not df.empty else 'N'
            results.append({
                'ITEM_CD': item_cd,
                'ITEM_NM_KOR': item_nm,
                'IS_AVAILABLE': is_available
            })
            
            print(f"  결과: {'성공' if is_available == 'Y' else '실패'}")
            
        except Exception as e:
            print(f"  오류 발생: {e}")
            results.append({
                'ITEM_CD': item_cd,
                'ITEM_NM_KOR': item_nm,
                'IS_AVAILABLE': 'N'
            })
    
    # 결과를 DataFrame으로 변환
    results_df = pd.DataFrame(results)
    print("\n테스트 완료!")
    
    # 성공한 항목과 실패한 항목 개수 출력
    success_count = len(results_df[results_df['IS_AVAILABLE'] == 'Y'])
    fail_count = len(results_df[results_df['IS_AVAILABLE'] == 'N'])
    print(f"성공: {success_count}개, 실패: {fail_count}개")
    
    return results_df

def update_item_list_csv(results_df):
    # GitHub에서 최신 ITEM_LIST.csv 파일 다운로드
    fs = FnSpace("dummy_key")  # 아무 키나 사용 (API 호출 안 함)
    item_df = fs.item_df.copy()
    
    # IS_AVAILABLE 컬럼 초기화 (모든 항목을 'Y'로 설정)
    item_df['IS_AVAILABLE'] = 'Y'
    
    # 테스트 결과에 따라 macro 항목의 IS_AVAILABLE 업데이트
    for idx, row in results_df.iterrows():
        item_cd = row['ITEM_CD']
        is_available = row['IS_AVAILABLE']
        
        # 해당 항목 찾아서 IS_AVAILABLE 값 업데이트
        if item_cd in item_df.index:
            item_df.loc[item_cd, 'IS_AVAILABLE'] = is_available
    
    # 결과 저장
    item_df.to_csv('ITEM_LIST_UPDATED.csv', encoding='ANSI')
    print("ITEM_LIST_UPDATED.csv 파일에 결과가 저장되었습니다.")

if __name__ == "__main__":
    # 각 경제 데이터 항목 테스트
    results_df = test_macro_items()
    
    # ITEM_LIST.csv 파일 업데이트
    update_item_list_csv(results_df) 