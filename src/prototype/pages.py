import streamlit as st
import pandas as pd
from typing import Dict, Any
from src.prototype.data_loader import (
    load_inclusion_candidates,
    load_exclusion_candidates,
    load_data_quality_report,
    load_poc_result,
    format_market_cap
)

def render_overview():
    """Render the Overview screen containing summary KPIs, data sources, and PoC checkmarks."""
    st.title("Nasdaq-100 편입·편출 관찰 리포트 Prototype")
    
    # Header warnings & notices
    st.info(
        "💡 **안내:** 본 프로그램은 공개 데이터와 내부 PoC 가설 규칙을 바탕으로 구성된 **기술 Prototype**입니다. "
        "공식 Nasdaq-100 지수의 편입·편출 확정 결과가 아니며, 어떠한 형태의 **투자 추천도 아닙니다**."
    )
    
    try:
        poc_res = load_poc_result()
        dq_rep = load_data_quality_report()
    except FileNotFoundError as e:
        st.error(f"데이터를 불러올 수 없습니다:\n{e}")
        return
        
    st.markdown("### 📊 주요 요약 지표")
    
    # Render KPI Cards in columns
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("분석 대상 유니버스", f"{dq_rep.get('total_universe_count', 0)}개")
    col2.metric("현재 구성 종목 수", f"{dq_rep.get('constituent_count', 0)}개")
    col3.metric("편입 관찰 후보", f"{poc_res.get('inclusion_candidate_count', 0)}개")
    col4.metric("편출 관찰 후보", f"{poc_res.get('exclusion_candidate_count', 0)}개")
    
    col5, col6, col7 = st.columns(3)
    
    completeness = poc_res.get("data_completeness_rate", 0.0)
    col5.metric("데이터 완전성", f"{completeness:.1f}%")
    
    repro = "PASS" if poc_res.get("reproducibility_passed") else "FAIL"
    col6.metric("재현성 검증", repro)
    
    status = poc_res.get("overall_result", "UNKNOWN")
    col7.metric("PoC 최종 상태", status)
    
    st.markdown("---")
    
    # Detailed statistics
    st.markdown("### 🔍 PoC 검증 세부 항목")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("**데이터 수집 내역:**")
        st.write(f"- SEC CIK 매치 기업 수: `{dq_rep.get('sec_matched_count')}개`")
        st.write(f"- 시장 데이터 매치 기업 수: `{dq_rep.get('market_data_matched_count')}개`")
        st.write(f"- 누락된 섹터 기업 수: `{dq_rep.get('missing_sector_count')}개`")
        st.write(f"- 누락된 시가총액 기업 수: `{dq_rep.get('missing_market_cap_count')}개`")
        st.write(f"- 판정 불가능(unknown) 기업 수: `{dq_rep.get('unknown_eligibility_count')}개`")
        
    with col_b:
        st.markdown("**파이프라인 요약:**")
        st.write(f"- 재현성 여부 (동일 스냅숏): `{poc_res.get('reproducibility_passed')}`")
        st.write(f"- 공식 소스 비중: `{poc_res.get('official_source_ratio') * 100:.1f}%`")
        
        st.markdown("**사용 소스:**")
        st.write(f"- 공식 소스: `{', '.join(dq_rep.get('official_sources_used', []))}`")
        st.write(f"- 보조 소스: `{', '.join(dq_rep.get('secondary_sources_used', []))}`")

    st.markdown("---")
    
    # Limitations section
    st.markdown("### ⚠️ 주요 제한 사항")
    for limit in poc_res.get("limitations", []):
        st.warning(limit)

def render_inclusion_candidates():
    """Render the Inclusion Watch Candidates screen."""
    st.title("📈 Nasdaq-100 편입 관찰 후보")
    st.caption("아래 목록은 공개 데이터와 PoC 규칙으로 계산한 편입 관찰 후보입니다. 공식 Nasdaq 예상 순위나 편입 확정 목록이 아닙니다.")
    
    try:
        df = load_inclusion_candidates()
    except FileNotFoundError as e:
        st.error(f"데이터를 불러올 수 없습니다:\n{e}")
        return

    # Filter section
    st.markdown("#### 🔍 필터 및 검색")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_query = st.text_input("티커 또는 기업명 검색", "").strip().upper()
    with col2:
        sectors = ["전체"] + sorted(list(df["sector"].dropna().unique()))
        selected_sector = st.selectbox("업종(Sector) 필터", sectors)
    with col3:
        statuses = ["전체"] + sorted(list(df["eligibility_status"].dropna().unique()))
        selected_status = st.selectbox("적격 상태 필터", statuses)
        
    # Apply filters
    filtered_df = df.copy()
    if search_query:
        filtered_df = filtered_df[
            filtered_df["ticker"].str.upper().str.contains(search_query) |
            filtered_df["company_name"].str.upper().str.contains(search_query)
        ]
    if selected_sector != "전체":
        filtered_df = filtered_df[filtered_df["sector"] == selected_sector]
    if selected_status != "전체":
        filtered_df = filtered_df[filtered_df["eligibility_status"] == selected_status]
        
    # Format market cap for rendering
    display_df = filtered_df.copy()
    if "market_cap" in display_df.columns:
        display_df["formatted_market_cap"] = display_df["market_cap"].apply(format_market_cap)
        
    # Re-order columns for display
    cols_to_show = [
        "watch_rank", "ticker", "company_name", "formatted_market_cap", 
        "sector", "eligibility_status", "market_data_date", "rationale"
    ]
    
    # Hide indices
    st.dataframe(
        display_df[cols_to_show].rename(columns={
            "watch_rank": "순위",
            "ticker": "티커",
            "company_name": "기업명",
            "formatted_market_cap": "시가총액",
            "sector": "업종",
            "eligibility_status": "적격 상태",
            "market_data_date": "기준일",
            "rationale": "관찰 근거"
        }),
        use_container_width=True,
        hide_index=True
    )
    
    # Detail Section
    st.markdown("### 🏢 기업 상세 정보")
    if len(filtered_df) == 0:
        st.write("선택된 필터에 해당하는 기업이 없습니다.")
    else:
        selected_ticker = st.selectbox("상세 정보를 확인할 기업을 선택하세요.", filtered_df["ticker"].tolist())
        comp_row = filtered_df[filtered_df["ticker"] == selected_ticker].iloc[0]
        
        st.markdown(f"#### **{comp_row['company_name']} ({comp_row['ticker']})**")
        
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.markdown(f"**시가총액:** {format_market_cap(comp_row['market_cap'])}")
            st.markdown(f"**업종 (Sector):** {comp_row['sector']}")
            st.markdown(f"**현재 구성 상태:** 지수 비구성 종목")
            st.markdown(f"**데이터 기준일:** {comp_row['market_data_date']}")
            
        with col_d2:
            st.markdown(f"**적격 상태:** `{comp_row['eligibility_status']}`")
            st.markdown(f"**관찰 근거:** {comp_row['rationale']}")
            st.markdown(f"**제한 사항:** {comp_row.get('limitation', '없음')}")

def render_exclusion_candidates():
    """Render the Exclusion Watch Candidates screen."""
    st.title("📉 Nasdaq-100 편출 관찰 후보")
    st.caption("아래 목록은 현재 구성 종목 가운데 공개 데이터 기준 시가총액 하위권에 있는 관찰 대상입니다. 편출 확정 또는 기업 부실을 의미하지 않습니다.")
    
    try:
        df = load_exclusion_candidates()
    except FileNotFoundError as e:
        st.error(f"데이터를 불러올 수 없습니다:\n{e}")
        return

    # Filter section
    st.markdown("#### 🔍 필터 및 검색")
    col1, col2 = st.columns(2)
    
    with col1:
        search_query = st.text_input("티커 또는 기업명 검색", "").strip().upper()
    with col2:
        sectors = ["전체"] + sorted(list(df["sector"].dropna().unique()))
        selected_sector = st.selectbox("업종(Sector) 필터", sectors)
        
    # Apply filters
    filtered_df = df.copy()
    if search_query:
        filtered_df = filtered_df[
            filtered_df["ticker"].str.upper().str.contains(search_query) |
            filtered_df["company_name"].str.upper().str.contains(search_query)
        ]
    if selected_sector != "전체":
        filtered_df = filtered_df[filtered_df["sector"] == selected_sector]
        
    # Format market cap for rendering
    display_df = filtered_df.copy()
    if "market_cap" in display_df.columns:
        display_df["formatted_market_cap"] = display_df["market_cap"].apply(format_market_cap)
        
    # Re-order columns for display
    cols_to_show = [
        "watch_rank", "ticker", "company_name", "formatted_market_cap", 
        "sector", "market_data_date", "rationale"
    ]
    
    st.dataframe(
        display_df[cols_to_show].rename(columns={
            "watch_rank": "순위",
            "ticker": "티커",
            "company_name": "기업명",
            "formatted_market_cap": "시가총액",
            "sector": "업종",
            "market_data_date": "기준일",
            "rationale": "관찰 근거"
        }),
        use_container_width=True,
        hide_index=True
    )
    
    # Detail Section
    st.markdown("### 🏢 기업 상세 정보")
    if len(filtered_df) == 0:
        st.write("선택된 필터에 해당하는 기업이 없습니다.")
    else:
        selected_ticker = st.selectbox("상세 정보를 확인할 기업을 선택하세요.", filtered_df["ticker"].tolist())
        comp_row = filtered_df[filtered_df["ticker"] == selected_ticker].iloc[0]
        
        st.markdown(f"#### **{comp_row['company_name']} ({comp_row['ticker']})**")
        
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.markdown(f"**시가총액:** {format_market_cap(comp_row['market_cap'])}")
            st.markdown(f"**업종 (Sector):** {comp_row['sector']}")
            st.markdown(f"**현재 구성 상태:** 지수 구성 종목 (하위권)")
            st.markdown(f"**데이터 기준일:** {comp_row['market_data_date']}")
            
        with col_d2:
            st.markdown(f"**관찰 근거:** {comp_row['rationale']}")
            st.markdown(f"**편출 확정이 아닌 이유:** 지수 공식 위원회의 최종 평가 및 교체 일정 조정이 동반되어야 확정됩니다.")
            st.markdown(f"**제한 사항:** {comp_row.get('limitation', '없음')}")

def render_ai_analysis():
    """Render the AI Analysis mock features screen."""
    st.title("🤖 AI 분석 기능 (추후 연결 예정)")
    st.info("💡 **안내:** 현재 AI 모델이나 API가 연결되어 있지 않은 상태입니다. 아래 카드는 향후 구현 예정인 기능 설명입니다.")
    
    # Render Mock AI cards in columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(
            """
            <div style="padding: 15px; border-radius: 5px; border: 1px solid #ddd; margin-bottom: 10px;">
                <h4>📄 공식 문서 요약</h4>
                <p style="color: #666; font-size: 0.9em;"><strong>상태:</strong> ⏳ AI 연결 대기 중</p>
                <p>Nasdaq 지수 방법론 가이드라인과 공식 변경 발표 원문 문서를 금융 특화 LLM을 통해 요약하여 제공할 예정입니다.</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        st.markdown(
            """
            <div style="padding: 15px; border-radius: 5px; border: 1px solid #ddd; margin-bottom: 10px;">
                <h4>🔗 원문 인용 연결</h4>
                <p style="color: #666; font-size: 0.9em;"><strong>상태:</strong> ⏳ AI 연결 대기 중</p>
                <p>AI 모델이 제안하는 요약 근거가 실제 SEC 10-K/Q 공시나 지수 가이드라인의 어느 영역에 위치하는지 연결(Citation)을 제공할 예정입니다.</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
    with col2:
        st.markdown(
            """
            <div style="padding: 15px; border-radius: 5px; border: 1px solid #ddd; margin-bottom: 10px;">
                <h4>📰 기업 사건 추출</h4>
                <p style="color: #666; font-size: 0.9em;"><strong>상태:</strong> ⏳ AI 연결 대기 중</p>
                <p>SEC 공시(8-K 등) 및 보도 자료를 감시하여 인수합병(M&A), 상장폐지, 기업분할 등 지수 편입 배제 사유가 되는 주요 이벤트를 자동 감지합니다.</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        st.markdown(
            """
            <div style="padding: 15px; border-radius: 5px; border: 1px solid #ddd; margin-bottom: 10px;">
                <h4>📊 시나리오 시뮬레이션</h4>
                <p style="color: #666; font-size: 0.9em;"><strong>상태:</strong> ⚙️ 추후 검토 예정</p>
                <p>Bull/Base/Bear 조건부 시나리오 분석을 통해 특정 기업의 성장이 지수 후보 기준에 어떤 영향을 주는지 가상 변화 조건을 비교합니다. (수익률 예측 제외)</p>
            </div>
            """, 
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown("### 🧪 AI 분석 체험하기 (Mockup)")
    
    # Load tickers list for select box dropdown
    tickers = ["AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL"]
    try:
        inc = load_inclusion_candidates()
        exc = load_exclusion_candidates()
        tickers = sorted(list(set(inc["ticker"].tolist() + exc["ticker"].tolist())))
    except Exception:
        pass
        
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        selected_ticker = st.selectbox("분석 대상 종목 선택", tickers)
    with col_in2:
        analysis_type = st.selectbox("분석 유형 선택", ["SEC 공시 요약", "지수 방법론 비교", "시나리오 모델링"])
        
    if st.button("분석 실행", use_container_width=True):
        st.info("현재 Prototype에서는 AI 모델을 연결하지 않았습니다. 향후 공식 문서 기반 RAG와 인용 검증 기능을 추가할 예정입니다.")
