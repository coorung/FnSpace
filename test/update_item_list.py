#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import pandas as pd

def update_item_list():
    """
    테스트 결과로 생성된 ITEM_LIST_UPDATED.csv를 ITEM_LIST.csv로 복사하고
    필요한 정리 작업 수행
    """
    # ITEM_LIST_UPDATED.csv가 존재하는지 확인
    if os.path.exists('ITEM_LIST_UPDATED.csv'):
        # CSV 파일 읽기
        item_df = pd.read_csv('ITEM_LIST_UPDATED.csv', encoding='ANSI', index_col=0)
        
        # 필요한 추가 정리 작업 수행
        # 모든 항목에 IS_AVAILABLE 컬럼이 있는지 확인
        if 'IS_AVAILABLE' not in item_df.columns:
            item_df['IS_AVAILABLE'] = 'Y'  # 기본값 설정
            
        # consensus-earning-daily 카테고리는 모두 'N'으로 설정 (서비스 오류 있음)
        daily_items = item_df[item_df['DATA_TYPE'] == 'consensus-earning-daily'].index
        if not daily_items.empty:
            item_df.loc[daily_items, 'IS_AVAILABLE'] = 'N'
        
        # 최종 파일 저장
        item_df.to_csv('ITEM_LIST.csv', encoding='ANSI')
        print("ITEM_LIST.csv 파일이 업데이트되었습니다.")
        
        # 원본 GitHub 저장소에 반영할 수 있는 가이드 출력
        print("\nGitHub 저장소에 업데이트된 ITEM_LIST.csv를 적용하려면:")
        print("1. GitHub 저장소 클론 또는 포크")
        print("2. 기존 ITEM_LIST.csv 대신 새로 생성된 파일로 교체")
        print("3. 변경사항 커밋 및 푸시")
    else:
        print("ITEM_LIST_UPDATED.csv 파일이 존재하지 않습니다.")
        print("먼저 test_data_items.py를 실행하여 테스트 결과를 생성하세요.")

if __name__ == "__main__":
    update_item_list() 