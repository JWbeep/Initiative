
import streamlit as st
import os
from generator import BlogGenerator

# 페이지 설정
st.set_page_config(
    page_title="롱단쓰 AI 블로그 생성기",
    page_icon="🍜",
    layout="wide"
)

# 세션 상태 초기화 (결과 저장을 위해)
if 'generated_post' not in st.session_state:
    st.session_state.generated_post = ""

# 스타일 설정
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
    }
    .stTextArea>div>div>textarea {
        border-radius: 10px;
    }
    h1 {
        color: #667eea;
        text-align: center;
    }
    /* 메뉴 가격 number_input 위아래 여백 제거 */
    div[data-testid="stNumberInput"] {
        padding-top: 0px;
        padding-bottom: 0px;
        margin-top: 0px;
        margin-bottom: 0px;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("🍜 롱단쓰 스타일 블로그 생성기")
    st.write("여자친구분의 블로그 스타일을 완벽하게 재현합니다. 주제와 키워드만 입력하세요!")

    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.subheader("📝 설정 및 입력")
        
        with st.expander("🛠️ 데이터 관리", expanded=False):
            data_count = len([f for f in os.listdir("blog_generator/data/processed") if f.endswith(".txt")])
            st.info(f"현재 학습된 블로그 글 개수: {data_count}개")
            if st.button("새로운 글 수집하러 가기"):
                st.write("`collect_urls.html`을 열어주세요!")

        topic = st.text_input("📍 블로그 주제", placeholder="예: 용인 수지 맛집 '도넛 하우스' 방문기")

        # ── 핵심 키워드 (최대 7개) ──────────────────────────────────
        st.markdown("**🔑 핵심 키워드 및 반복 횟수** (최대 7개)")
        st.caption("키워드를 입력하고, 본문에 반드시 등장해야 하는 최소 횟수를 설정하세요.")

        hcol1, hcol2, hcol3 = st.columns([3, 1, 0.3])
        hcol1.markdown("<small>키워드</small>", unsafe_allow_html=True)
        hcol2.markdown("<small>최소 횟수</small>", unsafe_allow_html=True)
        hcol3.markdown("<small>&nbsp;</small>", unsafe_allow_html=True)

        keyword_list = []
        for i in range(7):
            kcol1, kcol2, kcol3 = st.columns([3, 1, 0.3])
            kw = kcol1.text_input(
                f"키워드 {i+1}",
                key=f"kw_{i}",
                placeholder="예: 빵집" if i == 0 else "",
                label_visibility="collapsed"
            )
            cnt = kcol2.number_input(
                f"횟수 {i+1}",
                key=f"cnt_{i}",
                min_value=1,
                max_value=20,
                value=3,
                label_visibility="collapsed"
            )
            kcol3.markdown("&nbsp;", unsafe_allow_html=True)
            if kw.strip():
                keyword_list.append((kw.strip(), int(cnt)))

        # ── 대표 메뉴 및 가격 (최대 7개) ────────────────────────────
        st.markdown("**🍽️ 대표 메뉴 및 가격** (선택, 최대 7개)")
        st.caption("메뉴명을 입력하고 가격은 숫자만 입력하세요.")

        mhcol1, mhcol2, mhcol3 = st.columns([3, 1, 0.3])
        mhcol1.markdown("<small>메뉴명</small>", unsafe_allow_html=True)
        mhcol2.markdown("<small>가격</small>", unsafe_allow_html=True)
        mhcol3.markdown("<small>&nbsp;</small>", unsafe_allow_html=True)

        menu_list = []
        for i in range(7):
            mcol1, mcol2, mcol3 = st.columns([3, 1, 0.3])
            menu_name = mcol1.text_input(
                f"메뉴 {i+1}",
                key=f"menu_{i}",
                placeholder="예: 아메리카노" if i == 0 else "",
                label_visibility="collapsed"
            )
            price = mcol2.number_input(
                f"가격 {i+1}",
                key=f"price_{i}",
                min_value=0,
                max_value=999999,
                value=0,
                step=500,
                label_visibility="collapsed"
            )
            mcol3.markdown("<small>원</small>", unsafe_allow_html=True)
            if menu_name.strip() and price > 0:
                menu_list.append((menu_name.strip(), price))
        
        if st.button("🚀 블로그 글 생성 시작"):
            if not topic:
                st.error("주제를 입력해 주세요!")
            else:
                with st.spinner("롱단쓰의 말투를 배우는 중... 잠시만 기다려 주세요!"):
                    try:
                        gen = BlogGenerator()
                        result_placeholder = st.empty()
                        full_text = ""
                        
                        for chunk in gen.generate_stream(topic, keyword_list, menu_list):
                            full_text += chunk
                            result_placeholder.text_area("실시간 생성 중...", full_text, height=400)
                        
                        st.session_state.generated_post = full_text
                        st.success("글 생성이 완료되었습니다!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"오류가 발생했습니다: {e}")

    with col2:
        st.subheader("✨ 생성된 블로그 초안")
        if st.session_state.generated_post:
            st.text_area("결과물 (복사해서 사용하세요)", st.session_state.generated_post, height=600)
            
            # 다운로드 버튼
            st.download_button(
                label="📥 텍스트 파일로 저장",
                data=st.session_state.generated_post,
                file_name=f"generated_post.txt",
                mime="text/plain"
            )
        else:
            st.info("왼쪽에서 정보를 입력하고 '생성 시작' 버튼을 눌러주세요.")

    # 하단 정보
    st.markdown("---")
    st.caption("© 2024 Blog Style Generator. Powered by Google Gemini Flash.")

if __name__ == "__main__":
    main()
