# road-icing-risk

**KISTI DATA·AI 2026 — 전북 고속도로 결빙위험도 분석 연구용 저장소 (초기 템플릿)**

도로기상(RWIS), 종관기상(ASOS), 방재기상(AWS), 교량·터널, 도로망, 표고, 하천경계를 결합하여 **미관측 고속도로 구간의 노면온도·결빙위험을 추정**하고 구간별 위험도를 분석하기 위한 프로젝트입니다.

> 현재 상태: 제공된 **데이터 설명 이미지**만 반영했습니다. 실제 데이터 파일·컬럼명·좌표계·제출 포맷은 검증되지 않았습니다. 프로젝트에는 공개되지 않은 원본 데이터, 학습 결과, 생성된 지도 등이 들어 있지 않습니다.

## 빠른 시작

Python 3.10 이상 권장.

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e '.[dev]'
pytest -q
python -m road_icing inventory --raw-dir data/raw --out reports/data_inventory.json
```

원본 데이터는 `data/raw/`의 해당 소스 폴더에 별도로 배치합니다. `.gitignore`로 원본 데이터와 모델 가중치는 Git에서 제외합니다.

학습은 **실제 파일을 탐색한 후** 원본 컬럼명을 매핑하고 모든 데이터셋을 정규화해 `data/processed/model_table.parquet`를 만든 뒤 실행합니다. `prepare`는 고의로 자동 구현하지 않았습니다. 관측소, 시간, 공간 좌표계가 확정되기 전에는 안전한 JOIN을 보장할 수 없기 때문입니다. `docs/CODEX_HANDOFF.md`를 Codex에 전달해 데이터 구조에 맞는 파이프라인을 완성하세요.

정규화 테이블의 필수 컬럼은 `station_id`, `timestamp`, `road_surface_temp_c`, `road_state` 또는 `is_ice`이며, 학습용 입력 특성은 `configs/experiment.yaml`에서 지정합니다. 실제 테이블 준비 후:

```bash
python -m road_icing validate --table data/processed/model_table.parquet
python -m road_icing train --table data/processed/model_table.parquet --config configs/experiment.yaml
```

모델 학습 전에 **관측소 그룹 분할**을 적용하고, 미관측 구간에서 사용할 수 없는 RWIS 노면온도·노면상태를 입력 특성에 포함하지 않습니다. 예측 대상 관측소 자체의 RWIS 정보는 평가의 정답용으로만 취급합니다.

## 구조

```text
road-icing-risk/
├── AGENTS.md                    # Codex 필수 작업 지침
├── configs/                    # 데이터 경로, 학습 설정, holdout 설정
├── data/
│   ├── raw/                    # 실제 대회 원본 (Git 제외)
│   │   ├── rwis/
│   │   ├── asos/
│   │   ├── aws/
│   │   ├── roads/bridge_tunnel/
│   │   ├── roads/centerline/
│   │   ├── terrain/elevation/
│   │   └── hydro/rivers/
│   ├── interim/                # 정규화·시간/위치 정합 결과
│   ├── processed/              # 모델 테이블
│   └── external/               # 별도 외부 허용 자료
├── docs/                       # 데이터 사전, 분할·리서치·Codex 지침
├── notebooks/                  # 탐색 분석
├── research/                   # 물리학 / 산업공학 연구 노트
├── src/road_icing/             # Python 패키지 + CLI
├── tests/                      # 데이터 누수/분할/인벤토리 점검
├── reports/                    # 평가 결과와 그림
├── models/                     # 학습 모델 (Git 제외)
└── .github/workflows/ci.yml    # 자동 테스트
```

## 주요 원칙

1. `station_id + timestamp`를 정규화 관측의 기본 키로 사용합니다(추가 키 필요 여부는 데이터 확인).
2. 시간대는 기본적으로 한국 표준시(KST)를 가정하되, 실제 타임스탬프에 오프셋이 있다면 변환 규칙을 명확히 기록합니다.
3. `road_state == "Ice"`만 결빙으로 정의합니다. 원본의 결측 상태는 비결빙으로 치환하지 않습니다.
4. AWS 강수감지 `0=무강수`, `1=강수`, `null=관측결측/별도 확인`으로 취급하며 이미지의 `Null: 음수` 주기는 해석 전 확인이 필요합니다.
5. 모델 평가는 무작위 행 분할이 아닌 관측소 홀드아웃을 기본으로 합니다.
6. 공간 데이터의 CRS/EPSG는 확인하기 전 WGS84로 임의 변환하지 않습니다.
7. 제출 규정·마감·홀드아웃 관측소 명단은 공식 문제 페이지로 재확인합니다.

## 팀 협업

- 물리학: `research/physics.md` — 결빙 메커니즘, 지표온도·기온 차, 이슬점, 복사냉각, 선행 강수
- 산업공학: `research/industrial_engineering.md` — 구간 위험도, 결빙탐지 비용, 점수표, 관측소 배치·검증
- 모델 개발: `src/road_icing/` — 데이터 정합성, 학습, 그룹 기반 검증, 지리공간 특성

본 저장소는 GitHub 원격 저장소에 자동으로 업로드된 상태가 아닙니다. 코드와 설정은 템플릿이며 데이터에 대한 평가 점수를 주장하지 않습니다.
