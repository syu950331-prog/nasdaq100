import streamlit as st
import os
from pathlib import Path

# Set up page configurations
st.set_page_config(
    page_title="Nasdaq-100 Candidate PoC Prototype",
    page_icon="📈",
    layout="wide"
)

from src.prototype.components import render_sidebar
from src.prototype.pages import (
    render_overview,
    render_inclusion_candidates,
    render_exclusion_candidates,
    render_ai_analysis
)

# Helper to check if output files exist
OUTPUTS_DIR = Path(__file__).resolve().parent / "outputs"
RESULT_JSON_PATH = OUTPUTS_DIR / "poc_result.json"

def main():
    # If the output files do not exist, guide the user to run refresh first
    if not RESULT_JSON_PATH.exists():
        st.title("Nasdaq-100 편입·편출 관찰 리포트 Prototype")
        st.error("⚠️ 수집된 PoC 결과가 존재하지 않습니다.")
        st.markdown(
            "이 Prototype은 기존 PoC 실행 결과를 읽어와 시각화합니다.\n"
            "앱을 시작하기 위해 아래 명령어를 터미널에서 실행하여 외부 데이터를 수집해 주세요.\n\n"
            "```bash\n"
            "python run_poc.py --refresh\n"
            "```\n"
            "또는 사이드바의 **'PoC 데이터 새로고침'** 버튼을 클릭하여 수집 프로세스를 실행할 수 있습니다."
        )
        # Render sidebar anyway so user can click the refresh button!
        render_sidebar()
        return

    # Render sidebar controls & navigation
    render_sidebar()
    
    # Simple navigation routing
    if "nav_page" not in st.session_state:
        st.session_state["nav_page"] = "Overview"
        
    page = st.sidebar.radio(
        "화면 선택",
        ["Overview", "편입 관찰 후보", "편출 관찰 후보", "AI 분석 기능 예정"]
    )
    
    if page == "Overview":
        render_overview()
    elif page == "편입 관찰 후보":
        render_inclusion_candidates()
    elif page == "편출 관찰 후보":
        render_exclusion_candidates()
    elif page == "AI 분석 기능 예정":
        render_ai_analysis()

if __name__ == "__main__":
    main()
