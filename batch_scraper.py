"""
일괄 블로그 스크래핑 스크립트
collect_urls.html에서 저장한 blog_urls.json 파일을 읽어서
모든 URL을 자동으로 스크래핑합니다.
"""

import json
import os
import sys
import time
from blog_generator.modules.scraper import save_blog_post

def batch_scrape(json_file_path="blog_urls.json"):
    """
    JSON 파일에서 URL 목록을 읽어서 일괄 스크래핑합니다.
    """
    # JSON 파일 읽기
    if not os.path.exists(json_file_path):
        print(f"❌ 오류: {json_file_path} 파일을 찾을 수 없습니다.")
        print("💡 먼저 collect_urls.html 페이지에서 URL을 입력하고 저장해 주세요.")
        return
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    urls = data.get('urls', [])
    total = len(urls)
    
    if total == 0:
        print("❌ URL이 하나도 없습니다.")
        return
    
    print(f"[시작] 총 {total}개의 URL을 스크래핑합니다...\n")
    
    success_count = 0
    fail_count = 0
    failed_urls = []
    
    for idx, url in enumerate(urls, 1):
        print(f"[{idx}/{total}] 처리 중: {url}")
        
        try:
            result = save_blog_post(
                url, 
                output_dir=r"blog_generator\data\processed"
            )
            
            if result:
                success_count += 1
                print(f"[성공]!\n")
            else:
                fail_count += 1
                failed_urls.append(url)
                print(f"[실패]\n")
            
            # 서버 부하 방지를 위해 잠시 대기
            if idx < total:
                time.sleep(1)
                
        except Exception as e:
            fail_count += 1
            failed_urls.append(url)
            print(f"[오류] 발생: {e}\n")
    
    # 결과 요약
    print("\n" + "="*50)
    print("--- 스크래핑 완료! ---")
    print("="*50)
    print(f"✅ 성공: {success_count}개")
    print(f"❌ 실패: {fail_count}개")
    
    if failed_urls:
        print("\n실패한 URL 목록:")
        for url in failed_urls:
            print(f"  - {url}")
    
    print(f"\n💾 저장 위치: blog_generator\\data\\processed\\")

if __name__ == "__main__":
    # 한글 출력 설정
    if sys.version_info >= (3, 7):
        sys.stdout.reconfigure(encoding='utf-8')
    
    # JSON 파일 경로 (다운로드 폴더에서 가져온 경우 경로 수정 필요)
    json_path = "blog_urls.json"
    
    # 커맨드 라인 인자로 경로를 받을 수도 있음
    if len(sys.argv) > 1:
        json_path = sys.argv[1]
    
    batch_scrape(json_path)
