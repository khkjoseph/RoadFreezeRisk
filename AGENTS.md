# AGENTS.md — Instructions for Codex

이 저장소는 전북 고속도로 결빙위험도 분석용 초기 템플릿이다. 사용자 제공 이미지 `docs/data_dictionary.md`에 기술된 소스 종류를 반영하지만 실제 데이터의 정확한 필드명은 미확인이다.

## 최우선 규칙

- 실데이터를 열어 `reports/data_inventory.json`과 샘플 헤더를 확인하기 전 **컬럼명을 추측해서 JOIN하거나 학습 성공을 주장하지 말 것**.
- 모든 원본 보존: raw 수정 금지, 임의 데이터 생성 금지, 원본의 누락값을 0 또는 non-Ice로 임의 대체 금지.
- 원본 시간대/KST 변환, 관측 주기, 결측률을 먼저 확인. 과거·미래 특성 사용 시 평가 시점에서 이용 가능 여부 검증.
- RWIS 노면온도(`road_surface_temp_c`)와 노면상태(`road_state`, `is_ice`)는 타깃 또는 정답으로 취급한다. 미관측 구간 예측 시 학습 입력에 직접 포함 금지. 모델이 추정한 온도만 별도 생성해 classifier에 넣는다면 out-of-fold 예측으로 누수를 막아야 한다.
- 관측소 홀드아웃 ID는 `configs/experiment.yaml`에 명시; 예시 ID는 공식 대회 자료와 실제 소스로 확인할 것. 검증 관측소의 통계량이 훈련 피처 엔지니어링에 유출되지 않게 할 것.
- `roads/`와 `hydro/`는 SHP 계열 다중 파일을 함께 관리하고 정확한 CRS 확인. 단위는 meters와 degrees 구별. 거리 계산에 EPSG:4326 도 단위를 사용하지 않는다.
- 모델 성능표는 실제 실행 로그로만 채운다. 결과를 만들어내지 않는다.
- 새로운 dependency와 데이터 구조를 변경하면 README 및 tests 동시 업데이트.

## 권장 진행 순서

1. `python -m road_icing inventory ...` 실행 및 ZIP/CSV/SHP 소스 확인.
2. `configs/column_mapping.example.yaml`를 복사하여 실제 원본 필드에 대한 `configs/column_mapping.local.yaml` 작성(로컬 파일 Git 제외).
3. 소스별 정상화와 CSV 한글 인코딩 지원(UTF-8-sig, cp949 포함); 단위·주기 검증.
4. 10분 기준 시간·공간 정합 및 지리공간 특징 생성(관측값이 없는 곳에서 계산 가능한 특징만 사용).
5. `model_table.parquet` 생성, 검증, 관측소 홀드아웃 및 베이스라인 학습.
6. 노면온도 예측 / Ice 이진분류 별도 리포트 및 비교; 위험지도 생성은 이후 진행.

Codex에게 요청할 상세 프롬프트는 `docs/CODEX_HANDOFF.md` 참고.
