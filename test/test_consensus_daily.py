#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fnspace.core import FnSpace

def test_consensus_daily():
    """consensus-earning-daily API 호출 테스트"""
    
    # API 키 설정
    api_key = "Your API Key"  # 실제 API 키로 변경
    fs = FnSpace(api_key)
    
    # 삼성전자 코드
    code = '005930'
    
    # 테스트할 항목들
    items = ['E121000', 'E121500', 'E122500', 'E122700']
    
    # 직접 API 호출
    print("=== consensus-earning-daily 데이터 요청 테스트 ===")
    
    # 수정된 코드로 API 호출
    data = fs.get_data(
        category='consensus-earning-daily',
        code=code,
        item=items,
        consolgb='M',
        annualgb='A',
        accdategb='C',
        from_year='2018',
        to_year='2019',
        from_date='20190531',
        to_date='20190607'
    )
    
    # 결과 출력
    if data is not None and not data.empty:
        print(f"API 호출 성공! 데이터 크기: {data.shape}")
        print("\n데이터 샘플:")
        print(data.head())
    else:
        print("API 호출 실패 또는 빈 결과 반환")
    
    return data

if __name__ == "__main__":
    test_consensus_daily() 