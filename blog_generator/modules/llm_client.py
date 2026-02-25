
import os
import google.generativeai as genai
from dotenv import load_dotenv

# .env 파일 로드 (여러 경로 시도)
load_dotenv() # 현재 디렉토리
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env')) # 상위 디렉토리
load_dotenv(os.path.join(os.path.dirname(__file__), '.env')) # 현재 디렉토리 (절대경로)

class LLMClient:
    def __init__(self, use_local=False):
        self.use_local = use_local
        self.model = None
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not self.use_local and api_key:
            print(f"[정보] LLM 초기화 중... (API 키 발견)")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-flash-latest') # 호환성 확인된 모델로 변경
        elif not self.use_local:
             print("[경고] .env 파일에서 GOOGLE_API_KEY를 찾을 수 없습니다.")

    def generate_text(self, system_prompt, user_content):
        """
        시스템 프롬프트와 사용자 입력을 받아서 텍스트를 생성합니다.
        """
        if self.use_local:
            return "Local Ollama generation is not yet implemented."
        
        if not self.model:
            return "오류: 모델이 초기화되지 않았습니다. API 키를 확인해 주세요."

        try:
            print("[정보] Gemini API 요청 시작 (최대 120초 대기)...")
            full_prompt = f"{system_prompt}\n\n사용자 요청: {user_content}"
            # 타임아웃을 120초로 늘림 (기본값보다 길게 설정)
            response = self.model.generate_content(
                full_prompt,
                request_options={"timeout": 120}
            )
            print("[정보] Gemini API 응답 수신 성공!")
            return response.text
        except Exception as e:
            return f"Error generating text: {e}"
    
    def generate_text_stream(self, system_prompt, user_content):
        """
        스트리밍 방식으로 텍스트를 생성합니다 (실시간으로 한 글자씩 반환).
        """
        if self.use_local:
            yield "Local Ollama generation is not yet implemented."
            return
        
        if not self.model:
            yield "오류: 모델이 초기화되지 않았습니다. API 키를 확인해 주세요."
            return

        try:
            print("[정보] Gemini API 스트리밍 요청 시작...")
            full_prompt = f"{system_prompt}\n\n사용자 요청: {user_content}"
            response = self.model.generate_content(
                full_prompt,
                stream=True  # 스트리밍 활성화
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
            
            print("[정보] Gemini API 스트리밍 완료!")
        except Exception as e:
            yield f"Error generating text: {e}"

if __name__ == "__main__":
    # 간단 테스트
    client = LLMClient()
    print(client.generate_text("당신은 친절한 AI입니다.", "자기소개 부탁해."))
