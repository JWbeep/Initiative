
import os
import random
from blog_generator.modules.llm_client import LLMClient
from blog_generator.modules.processor import load_processed_data, clean_text_for_llm

class BlogGenerator:
    def __init__(self):
        self.llm = LLMClient(use_local=False)
        self.data_dir = r"blog_generator/data/processed"

    def get_style_examples(self, num_examples=4):
        """
        창고에서 기존 글들을 가져와서 AI에게 보여줄 예시로 만듭니다.
        매번 다른 글이 선택되어 다양한 말투가 반영됩니다.
        """
        all_posts = load_processed_data(self.data_dir)
        if not all_posts:
            return ""
        
        # 무작위로 4개 선택 (25개 중 매번 다른 조합으로 선택됨)
        examples = random.sample(all_posts, min(num_examples, len(all_posts)))
        
        style_context = "### 기존 블로그 글 스타일 예시 ###\n\n"
        for i, post in enumerate(examples, 1):
            cleaned_post = clean_text_for_llm(post)
            # 2000자를 사용하여 말투를 충분히 학습
            style_context += f"예시 {i}:\n{cleaned_post[:2000]}\n\n---\n\n"
        
        return style_context

    def _build_prompt(self, topic, keyword_list=None, menu_list=None):
        """
        System Prompt와 사용자 요청을 한 곳에서 생성합니다.
        keyword_list: [(keyword, count), ...] 형태의 리스트
        menu_list:    [(menu_name, price), ...] 형태의 리스트
        """
        style_examples = self.get_style_examples(num_examples=4)

        system_prompt = f"""
당신은 블로거 '롱단쓰'입니다. 아래 예시 글들의 말투와 구성 방식을 그대로 따라서 글을 써주세요.

글 구성 규칙:
- "안녕하세요, 롱단쓰입니다"로 시작
- "~했답니다", "~하더라구요", "~인 것 같아요", "~거든요" 같은 구어체 어미 사용
- 이모티콘을 자연스럽게 섞어서 사용
- 위치, 메뉴, 가격, 팁을 상세하게 설명
- 예시 글의 마무리 패턴을 참고해서 자연스럽게 마무리

{style_examples}
"""
        # 키워드별 반복 횟수 규칙 생성
        keyword_rules = ""
        keyword_summary = ""
        if keyword_list:
            rules = [f"  - '{kw}': 반드시 {cnt}회 이상 등장" for kw, cnt in keyword_list]
            keyword_rules = "\n\n[필수 키워드 규칙 - 반드시 지켜주세요]\n" + "\n".join(rules)
            keyword_summary = ", ".join([kw for kw, _ in keyword_list])

        # 대표 메뉴 및 가격 (가격은 쉼표 포함 형식으로 포맷)
        menu_section = ""
        if menu_list:
            lines = [f"  - {name}: {price:,}원" for name, price in menu_list]
            menu_section = "\n대표메뉴 및 가격:\n" + "\n".join(lines)

        user_content = (
            f"주제: {topic}\n"
            f"키워드: {keyword_summary}"
            f"{menu_section}"
            f"{keyword_rules}\n\n"
            f"위 주제와 키워드를 바탕으로 블로그 포스팅을 작성해줘. "
            f"메뉴와 가격이 있다면 글 안에 자연스럽게 언급해줘. "
            f"필수 키워드 규칙을 반드시 지켜서 각 키워드가 지정된 횟수 이상 본문에 등장하도록 해줘."
        )

        return system_prompt, user_content

    def generate(self, topic, keyword_list=None, menu_list=None):
        """
        주제와 키워드를 바탕으로 블로그 글을 생성합니다. (한 번에 완성본 반환)
        """
        system_prompt, user_content = self._build_prompt(topic, keyword_list, menu_list)

        print(f"[정보] '{topic}' 주제로 AI에게 집필 요청을 보냅니다...")
        generated_blog = self.llm.generate_text(system_prompt, user_content)
        print("[정보] AI 집필 완료!")
        
        return generated_blog
    
    def generate_stream(self, topic, keyword_list=None, menu_list=None):
        """
        스트리밍 방식으로 블로그 글을 생성합니다. (실시간 한 글자씩 출력)
        """
        print("[정보] 스타일 예시를 재료 창고에서 꺼내오는 중...")
        system_prompt, user_content = self._build_prompt(topic, keyword_list, menu_list)
        print("[정보] 스타일 예시 준비 완료. AI에게 스트리밍 집필 요청...")

        for chunk in self.llm.generate_text_stream(system_prompt, user_content):
            yield chunk

if __name__ == "__main__":
    import sys
    # 한글 및 이미지 출력을 위한 인코딩 설정
    if sys.version_info >= (3, 7):
        sys.stdout.reconfigure(encoding='utf-8')

    # 테스트 실행
    gen = BlogGenerator()
    test_topic = "성수동 핫한 카페 투어"
    test_keywords = "카멜커피, 디저트맛집, 주말데이트"
    
    result = gen.generate(test_topic, test_keywords)
    print("\n" + "="*50)
    print("--- 생성된 블로그 글 ---")
    print("="*50)
    print(result)
