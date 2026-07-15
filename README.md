# Nasdaq-100 편입·편출 관찰 후보 PoC 및 Prototype

본 프로젝트는 Nasdaq-100 지수의 편입 및 편출 관찰 후보 기업을 실제 공개 데이터(Nasdaq, SEC, yfinance)를 기반으로 산정하는 Python 기반 PoC 프로그램과 이를 시각적으로 모니터링하기 위한 Streamlit Prototype 웹 애플리케이션입니다.

## 1. 프로젝트 소개
- 공개 데이터를 기반으로 Nasdaq-100 편입·편출 관찰 후보를 자동 산출하고, Streamlit 웹 대시보드로 요약 및 비교 결과를 한눈에 확인하는 Prototype 프로그램입니다.
- 공식 Nasdaq 편입·편출 확정 결과가 아니며, 투자 추천 목적이 아닙니다.

## 2. 주요 기능
- **PoC 결과 요약 (Overview)**: 분석 대상 유니버스 크기, 현재 구성 종목 수, 관찰 후보군 지표, 데이터 품질 및 재현성 검증 상태 요약 제공
- **편입 관찰 후보 Top 10**: 적격성 검증을 통과한 상위 10개 비구성 종목의 순위, 시가총액, 업종, 관찰 근거 및 상세 카드 뷰 제공
- **편출 관찰 후보 Top 10**: 현재 지수 구성 종목 중 시가총액 하위 10개 기업 목록 및 상세 정보 뷰 제공
- **AI 분석 기능 예정 화면**: 향후 탑재될 금융 RAG, SEC 공시 요약, 시나리오 모델링 기능 안내 및 Mockup 체험 제공
- **데이터 새로고침**: 사이드바의 버튼 클릭 시 Python 백엔드 파이프라인(`PoCPipeline`)을 직접 실행하여 실시간 API 데이터 수집 및 캐시 업데이트 수행

## 3. 프로젝트 구조
```
nasdaq100-candidate-poc/
├── data/
│   ├── raw/                 # 수집된 원본 JSON 데이터 (스냅숏 캐시)
│   └── processed/           # 정규화 및 결합된 마스터 CSV 파일
├── outputs/                 # 후보 산정 및 검증 결과 리포트
│   ├── inclusion_watch_top10.csv
│   ├── exclusion_watch_top10.csv
│   ├── data_quality_report.json
│   └── poc_result.json
├── src/
│   ├── collectors/          # 데이터 수집 (Nasdaq, SEC, yfinance)
│   ├── processing/          # 데이터 병합, 금융섹터 판정, 순위 산정
│   ├── validation/          # 데이터 품질 및 재현성 검증
│   ├── prototype/           # Streamlit Prototype 구현 파일
│   │   ├── __init__.py
│   │   ├── data_loader.py   # @st.cache_data를 이용한 파일 로딩 및 형변환
│   │   ├── components.py   # 사이드바 렌더링 및 새로고침 트리거
│   │   └── pages.py        # Overview, 편입, 편출, AI Mockup 페이지 렌더링
│   ├── config.py            # 경로 및 API 설정
│   ├── models.py            # 데이터 타입 구조화
│   └── pipeline.py          # 전체 수집·처리 파이프라인 제어
├── tests/                   # pytest 단위 테스트
├── .env.example             # 환경변수 템플릿
├── .gitignore
├── requirements.txt         # 파이썬 의존성 패키지
├── run_poc.py               # CLI 실행 프로그램
├── app.py                   # Streamlit 메인 진입점
├── AGENTS.md                # 에이전트 개발 규칙 및 Done 조건
└── README.md
```

## 4. 설치 및 실행 방법

### 환경 설정 및 패키지 설치
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Streamlit 앱 실행
기존 캐시 데이터가 있는 경우 바로 실행 가능합니다:
```bash
streamlit run app.py
```

### 실제 데이터를 새로 수집하는 경우 (3~4분 소요)
터미널에서 수집 명령 실행 후 웹 앱을 실행합니다:
```bash
python run_poc.py --refresh
streamlit run app.py
```

### 단위 테스트 실행
```bash
python -m pytest tests -q
```

## 5. 후보 산정 규칙
- **편입 관찰 후보**: Nasdaq 상장 비금융 비구성 기업 중 시가총액 기준 내림차순 상위 10개
- **편출 관찰 후보**: 현재 Nasdaq-100 구성 종목 중 시가총액 기준 오름차순 상위 10개

## 6. AI 기능 상태
- **현재 AI 모델 미연결**: Prototype 상태에서는 실제 LLM이나 OpenAI API 등을 호출하지 않습니다.
- 공식 문서 요약, SEC 기업 사건 추출, 원문 인용 연결 등은 추후 RAG 모듈 연동을 통해 제공할 예정이며, 화면은 UI 형태로만 제공됩니다.

## 7. 제한 사항 및 면책 조항
- **제한 사항**:
  1. 실제 Nasdaq 지수선정위원회의 최종 정성적 재량권 및 유동성 기준 등 세부 방법론은 반영되지 않습니다.
  2. SEC 공시 데이터 조회 제한(초당 10회 미만)으로 인해 수집 시 지연 대기가 포함되어 있습니다.
  3. 일부 시장 데이터는 보조 출처(`yfinance`)를 기반으로 가공됩니다.
- **투자 면책 조항**: 본 프로그램의 결과는 어떠한 경우에도 투자 추천, 목표주가 제시 또는 예상 수익률 산정을 목적으로 하지 않으며, 투자 의사결정의 근거로 사용할 수 없습니다.
