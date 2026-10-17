# Codex 작업 지시서

아래 내용을 Codex 작업창에 붙여 넣고 이 GitHub repository를 대상으로 실행하세요.

## 복사할 프롬프트

> 이 저장소의 `AGENTS.md`, `docs/data_dictionary.md`, `configs/sources.yaml`, `configs/experiment.yaml`을 먼저 읽어라. 저장소는 KISTI 전북 고속도로 결빙위험도 분석 프로젝트이다. 사용자가 `data/raw/`에 대회 실제 파일을 복사했다고 가정하되, 아직 파일이 없다면 파이프라인을 완성한 척하지 말고 필요한 파일 목록과 원본 컬럼 확인 사항만 보고하라.
>
> 1) `python -m road_icing inventory --raw-dir data/raw --out reports/data_inventory.json`으로 데이터 구조·필드·형식·기간·CRS를 조사하고, 실제 필드와 정규화 필드를 매핑하라. CSV 한국어 인코딩 및 shapefile sidecar 파일을 확인하라. 원본 파일 변경 금지.
> 2) `src/road_icing/pipeline/`에 RWIS/ASOS/AWS 관측값의 시간정합(10분 단위가 맞는지 확인), 관측소 ID 네임스페이스, 유효한 CRS 기반 최근접 공간결합, 교량·터널/고도/하천 거리 특징 생성 로직을 구현하라. 임의의 미래정보/정답 노면온도가 모델 피처에 들어가지 않도록 하라.
> 3) 정규화된 `data/processed/model_table.parquet`를 생성하고 `python -m road_icing validate`와 `pytest`를 실행하라.
> 4) `python -m road_icing train`으로 관측소 홀드아웃 기반 노면온도 회귀·Ice 분류 베이스라인을 실행하고 MAE, RMSE, Bias, Precision, Recall, F1을 보고하라. 실제 관측소 ID와 기간 및 공식 평가 방식을 재확인하라.
> 5) 시간/위치 데이터 누수 방지, 결측/관측소 불균형, 낮은 결빙 발생률 문제를 테스트에 추가하라. 미관측 구간별 500m/1km 지도·위험점수표는 학습/검증이 완료된 뒤 구현하라.
> 6) 사용한 입력·가정·실험·실패 이유를 README, docs, reports에 기록하라. 원본 데이터·대규모 가중치는 커밋하지 마라.
>
> 우선 1~3만 완료하고 실제 파일의 스키마와 문제점을 요약해 보고하라. 4~6은 실측 데이터와 제출 규칙을 확인한 뒤 진행하라.

## 완료 조건

- 실데이터의 샘플 행을 실제로 읽고 컬럼명·단위·시차·CRS 확인
- 데이터 결측·중복·관측기간 검증
- 관측소 홀드아웃 및 피처 누수 자동 테스트
- 모델의 입력·출력 및 학습 재현성 확보
- 제공 데이터 및 공모전 라이선스 준수
