import streamlit as st
import datetime
import traceback
from typing import Dict, Any
from src.pipeline import PoCPipeline
from src.prototype.data_loader import load_poc_result, load_data_quality_report

def render_sidebar():
    """Render the sidebar containing navigation metadata, status checks, and the refresh action."""
    st.sidebar.title("Nasdaq-100 PoC")
    st.sidebar.markdown("---")

    # Load results to display metadata
    try:
        poc_res = load_poc_result()
        dq_rep = load_data_quality_report()
        
        # 1. PoC 결과 상태
        status = poc_res.get("overall_result", "UNKNOWN")
        st.sidebar.subheader("PoC 결과 상태")
        if status == "PASS":
            st.sidebar.success("🟢 PASS")
        elif status == "CONDITIONAL_PASS":
            st.sidebar.warning("🟡 CONDITIONAL PASS")
        elif status == "FAIL":
            st.sidebar.error("🔴 FAIL")
        else:
            st.sidebar.info("⚪ UNKNOWN")

        # 2. 현재 데이터 기준일
        collected_at_str = dq_rep.get("collected_at", "")
        if collected_at_str:
            try:
                # Convert ISO timestamp to readable date/time
                dt = datetime.datetime.fromisoformat(collected_at_str.replace("Z", "+00:00"))
                formatted_date = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
            except Exception:
                formatted_date = collected_at_str
        else:
            formatted_date = "N/A"
        st.sidebar.markdown(f"**데이터 기준일 (수집시각):**\n`{formatted_date}`")

        # 3. 데이터 출처 안내
        st.sidebar.subheader("데이터 출처")
        st.sidebar.markdown(
            "- **Nasdaq-100 Constituents**: Nasdaq API\n"
            "- **Nasdaq Universe**: Stock Screener\n"
            "- **SEC Company Data**: SEC submissions & facts\n"
            "- **Market Data & Sectors**: yfinance (Secondary)"
        )
        
    except FileNotFoundError:
        st.sidebar.warning("⚠️ 캐시된 데이터가 존재하지 않습니다.")
        st.sidebar.info("데이터 새로고침을 실행하여 데이터를 수집하세요.")
    except Exception as e:
        st.sidebar.error(f"오류: {e}")

    st.sidebar.markdown("---")
    
    # 4. 데이터 새로고침 버튼
    st.sidebar.subheader("데이터 업데이트")
    st.sidebar.caption("외부 데이터 수집에는 시간이 걸리거나 일부 출처 접근이 실패할 수 있습니다. (SEC 호출 제한으로 약 3~4분 소요)")
    
    if st.sidebar.button("PoC 데이터 새로고침", use_container_width=True):
        with st.spinner("실시간 데이터 수집 및 PoC 검증 실행 중..."):
            try:
                pipeline = PoCPipeline()
                result = pipeline.run(refresh=True)
                
                # Clear Streamlit's cache
                st.cache_data.clear()
                st.sidebar.success("데이터 업데이트 완료!")
                st.rerun()
            except Exception as e:
                st.sidebar.error("새로고침 실패")
                st.sidebar.code(traceback.format_exc(), language="python")

    st.sidebar.markdown("---")
    
    # 5. 투자 면책 조항
    st.sidebar.subheader("투자 면책 조항")
    st.sidebar.caption(
        "본 서비스는 공개 데이터를 활용하여 가설을 검증하기 위한 기술 Prototype입니다. "
        "어떠한 경우에도 투자 추천, 매수/매도 권유, 목표주가나 예상수익률을 제시하지 않으며, "
        "실제 Nasdaq-100 지수의 최종 변경 결과는 지수 위원회 재량에 따라 다를 수 있습니다."
    )
