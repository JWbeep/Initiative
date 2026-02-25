
import requests
from bs4 import BeautifulSoup
import re
import html
import os
import time

def extract_text_from_url(url):
    """
    URL에서 본문 텍스트를 추출합니다.
    네이버 블로그의 경우 iframe 내부의 진짜 URL을 찾아야 할 수도 있습니다.
    """
    try:
        # 1. HTML 가져오기
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8' # 한글 깨짐 방지
        html_content = response.text

        soup = BeautifulSoup(html_content, 'html.parser')

        # 네이버 블로그는 iframe 안에 실제 내용이 있는 경우가 많음
        iframe = soup.find('iframe', id='mainFrame')
        if iframe:
            real_url = "https://blog.naver.com" + iframe['src']
            print(f"Iframe detected. Redirecting to: {real_url}")
            return extract_text_from_url(real_url)

        # 2. 본문 추출 (네이버 스마트에디터 기준)
        # se-main-container 또는 postViewArea 클래스 등을 주로 사용
        content_div = soup.find('div', class_='se-main-container')
        
        if not content_div:
            # 구버전 에디터 등 다른 구조 시도
            content_div = soup.find('div', id='postViewArea')

        if not content_div:
             # 그래도 없으면 전체에서 텍스트만 추출 (최후의 수단)
             text = soup.get_text(separator='\n')
        else:
            text = content_div.get_text(separator='\n')

        # 3. 정제 (빈 줄 제거 등)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        cleaned_text = '\n'.join(lines)
        
        return cleaned_text

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def save_blog_post(url, output_dir="data/processed"):
    """
    URL의 내용을 스크래핑하여 파일로 저장합니다.
    파일명은 URL의 뒷부분(ID 등)을 사용하거나 타임스탬프를 씁니다.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    content = extract_text_from_url(url)
    if content:
        # 파일명 생성 (간단하게 타임스탬프 사용)
        filename = f"post_{int(time.time())}.txt"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Source: {url}\n\n")
            f.write(content)
        
        print(f"Saved: {filepath}")
        return filepath
    else:
        print("Failed to extract content.")
        return None

if __name__ == "__main__":
    # 테스트용 URL (사용자가 직접 변경해서 테스트 가능)
    test_url = "https://blog.naver.com/moon-over/223879064676"
    print(f"Testing scraper with: {test_url}")
    save_blog_post(test_url, r"c:\Python Practice\Project_blog_generator\blog_generator\data\processed")
