# Nasdaq-100 Observation Candidate PoC & Prototype

## Project Goal
- 실제 공개 데이터(Nasdaq, SEC, yfinance)를 기반으로 Nasdaq-100 편입·편출 관찰 후보를 보여주는 PoC 및 시각화 Prototype입니다.
- 공식 지수 편입·편출 예측 또는 투자 추천 서비스가 아닙니다.

## Architecture
- **기존 PoC**: 데이터 수집 (Nasdaq, SEC, yfinance), 데이터 정규화 및 병합, 적격성 판정, 후보군 순위 산정, 데이터 품질 및 재현성 검증.
- **Streamlit Prototype**: 기존 PoC 파이프라인의 결과 출력 파일들(CSV, JSON)을 로드하여 대시보드로 시각화.
- **AI 기능**: 현재 미연결 상태이며, 향후 공식 문서 가이드라인 기반 금융 RAG 서비스로 확장 예정입니다.

## Development Rules
- **가짜 데이터 생성 금지**: 외부 API 수집 실패 시 조용히 가짜 데이터를 임의 생성하지 않으며 에러 및 누락 상황을 명시합니다.
- **기존 PoC 로직 중복 구현 금지**: UI 코드에 기존 계산 로직을 복사하거나 가공 로직을 중복 작성하지 않고, 파이프라인 결과물을 재사용합니다.
- **역할 분리**: 수식 및 정형 계산(Code)과 AI의 요약 설명 영역을 명확히 분리합니다.
- **데이터 투명성**: 데이터의 공식 출처와 기준일, 경고 문구 및 투자 면책 조항을 UI 화면에 명시합니다.
- **결측값 보간 금지**: 데이터 누락 시 임의로 보간하지 않으며 "미확인(unknown)" 상태로 처리합니다.
- **투자 추천 금지**: 목표주가, 예상수익률, 매수/매도 등 투자 자문이나 추천 성격의 표현을 엄격히 배제합니다.
- **안정성 유지**: Streamlit 추가로 인해 기존 PoC 코드의 실행이나 기존 테스트가 깨지지 않도록 합니다.

## Commands
- **의존성 패키지 설치**:
  ```bash
  pip install -r requirements.txt
  ```
- **PoC 수집 파이프라인 실행 (데이터 리프레시)**:
  ```bash
  python run_poc.py --refresh
  ```
- **Streamlit Prototype 로컬 실행**:
  ```bash
  streamlit run app.py
  ```
- **단위 테스트 실행**:
  ```bash
  python -m pytest tests -q
  ```

## Definition of Done
- **캐시 기반 실행**: 기존 outputs 디렉터리에 결과 파일이 있는 경우 즉시 앱 실행 가능.
- **핵심 4개 화면 렌더링**: Overview, 편입 관찰 후보, 편출 관찰 후보, AI 분석 기능 예정 탭이 모두 구현됨.
- **데이터 새로고침 동작**: 사이드바 버튼 클릭 시 backend `PoCPipeline`이 작동하고 Streamlit 캐시가 정상적으로 지워진 뒤 재로딩됨.
- **AI 미연결 검증**: AI 분석 실행 시 실제 호출을 하지 않고 RAG 대기 상태를 나타내는 안내 메시지를 출력함.
- **테스트 통과**: 기존 테스트 4개와 Streamlit 데이터 로더 테스트 5개를 포함해 총 9개 테스트 케이스가 통과됨.
- **README 정렬**: README.md의 명령어와 실행 구성이 실제 파일들과 일치함.
