# Deliverable Gap Reviewer

지시서(요청서)와 작업물을 비교하여 주요 누락/미흡 항목을 검출하고, 보완 자료를 활용하여 수정까지 수행하는 Claude Code 멀티에이전트 플러그인.

---

## 기능 안내

### 1. gap-review — 검토 (Phase 1~2)

지시서의 주요 요구사항이 작업물에 빠짐없이 반영되었는지 확인합니다.

**Phase 1: 지시서 분석**
- 분석가가 요구사항을 항목별로 추출
- 리뷰어가 누락/오독 검증 후 피드백
- 분석가가 피드백 반영 → 리뷰어 최종 확인
- 정리자가 구조화된 체크리스트(JSON) 생성

**Phase 2: 작업물 대조**
- 항목 대조자 + 품질 검토자가 2회 독립 검토
- 2회 중 낮은 점수 채택 (보수적 평가)
- [공통]/[참고] 태그로 이슈 신뢰도 구분
- 보완 방향 + 작성 예시 함께 제안

**출력물**: 검토보고서 (MD + DOCX + JSON)

### 2. gap-fix — 보완 수정 (Phase 3~4)

gap-review 결과를 기반으로, 보완 자료를 활용하여 작업물의 누락/미흡 항목을 수정합니다.

**Phase 3: 커버리지 분석**
- 보완 자료가 체크리스트의 어떤 항목을 커버할 수 있는지 매핑
- 커버 가능/불가능 항목을 사용자에게 먼저 보여줌
- 사용자가 "진행" 또는 "추가 자료 첨부"를 선택

**Phase 4: 수정 반영**
- 커버 가능한 항목을 원본 작업물에 반영하여 수정본 생성
- 원본이 PDF인 경우: DOCX, MD 등 다른 형식으로 수정본 생성
- 수정 이력 보고서 (MD + DOCX) 함께 생성

**출력물**: 수정본 파일 + 수정이력 보고서 (MD + DOCX)

---

## 사용 방법

### 설치

```bash
# Claude Code에서 마켓플레이스 등록
/plugin marketplace add TTtaTTe/gap-reviewer

# 플러그인 설치
/plugin install deliverable-gap-reviewer@gap-reviewer
```

### gap-review 실행

```bash
# 파일 경로 직접 지정
/gap-review 지시서.pdf 작업물.docx

# 또는 대화형 (파일을 순차적으로 요청)
/gap-review
```

### gap-fix 실행

```bash
# gap-review 결과 JSON + 보완 자료
/gap-fix 검토보고서_20260324_143052.json 보완자료.pdf

# 또는 대화형
/gap-fix
```

### 지원 파일 형식

- PDF, DOCX, PPTX, XLSX

---

## 채점 기준

| 점수 | 상태 | 의미 |
|------|------|------|
| 10.0 | 충족 | 요구사항 정확히 반영 |
| 7.0~9.9 | 대부분충족 | 경미한 보완 필요 |
| 4.0~6.9 | 부분충족 | 상당 부분 미흡 |
| 1.0~3.9 | 미흡 | 요구사항과 거리 있음 |
| 0.0 | 누락 | 해당 항목 없음 |

---

## 요구사항

- Claude Code
- Python 3.8+
- python-docx (`pip install python-docx`)

## 라이선스

MIT

---

# Deliverable Gap Reviewer (English)

A Claude Code multi-agent plugin that compares instruction documents against deliverables to detect missing or insufficient items, and applies fixes using supplementary materials.

---

## Features

### 1. gap-review — Review (Phase 1~2)

Checks whether all key requirements from an instruction document are reflected in the deliverable.

**Phase 1: Instruction Analysis**
- Analyst extracts requirements item by item
- Reviewer verifies for omissions/misinterpretations and provides feedback
- Analyst incorporates feedback → Reviewer final confirmation
- Organizer generates structured checklist (JSON)

**Phase 2: Deliverable Comparison**
- Compliance Checker + Quality Reviewer run 2 independent rounds
- Lower score adopted from 2 rounds (conservative evaluation)
- [Common]/[Reference] tags indicate issue confidence
- Provides remediation direction + writing examples

**Output**: Review report (MD + DOCX + JSON)

### 2. gap-fix — Remediation (Phase 3~4)

Based on gap-review results, uses supplementary materials to fix missing/insufficient items in the deliverable.

**Phase 3: Coverage Analysis**
- Maps which checklist items can be covered by supplementary materials
- Shows coverable/non-coverable items to user first
- User chooses to "proceed" or "add more materials"

**Phase 4: Apply Fixes**
- Applies coverable items to the original deliverable, generating a revised version
- If original is PDF: generates revised version in DOCX, MD, or other formats
- Generates modification log report (MD + DOCX)

**Output**: Revised deliverable + Modification log (MD + DOCX)

---

## Usage

### Installation

```bash
# Register marketplace in Claude Code
/plugin marketplace add TTtaTTe/gap-reviewer

# Install plugin
/plugin install deliverable-gap-reviewer@gap-reviewer
```

### Run gap-review

```bash
# Specify file paths directly
/gap-review instruction.pdf deliverable.docx

# Or interactive mode (files requested sequentially)
/gap-review
```

### Run gap-fix

```bash
# gap-review result JSON + supplementary materials
/gap-fix review_report_20260324_143052.json supplement.pdf

# Or interactive mode
/gap-fix
```

### Supported File Formats

- PDF, DOCX, PPTX, XLSX

---

## Scoring Criteria

| Score | Status | Meaning |
|-------|--------|---------|
| 10.0 | Fulfilled | Requirement accurately reflected |
| 7.0~9.9 | Mostly Fulfilled | Minor improvement needed |
| 4.0~6.9 | Partially Fulfilled | Significant gaps remain |
| 1.0~3.9 | Insufficient | Far from requirement |
| 0.0 | Missing | Item not present at all |

---

## Requirements

- Claude Code
- Python 3.8+
- python-docx (`pip install python-docx`)

## License

MIT
