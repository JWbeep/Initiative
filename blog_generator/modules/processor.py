
import os

def clean_text_for_llm(text):
    """
    LLM에 넣기 좋게 텍스트를 다듬습니다.
    (추후 구체적인 정제 로직 추가 예정: 이모티콘 제거, 너무 긴 문장 자르기 등)
    """
    # 1. 연속된 공백 제거
    import re
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r' +', ' ', text)
    
    return text.strip()

def load_processed_data(processed_dir="data/processed"):
    """
    저장된 모든 블로그 글을 읽어옵니다.
    """
    documents = []
    if not os.path.exists(processed_dir):
        return documents

    for filename in os.listdir(processed_dir):
        if filename.endswith(".txt"):
            filepath = os.path.join(processed_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                documents.append(f.read())
    
    return documents
