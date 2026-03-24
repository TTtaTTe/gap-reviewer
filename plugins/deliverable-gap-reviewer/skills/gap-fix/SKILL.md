---
name: gap-fix
description: "gap-review 검토 결과를 바탕으로 보완 자료를 분석하고, 작업물의 누락/미흡 항목을 수정합니다. 보완 자료의 커버리지를 먼저 보여주고, 사용자 확인 후 수정을 진행합니다. Use after gap-review to fix gaps in a deliverable using supplementary materials."
argument-hint: "[검토보고서.json] [보완자료 파일경로...]"
user-invocable: true
allowed-tools: Read, Write, Bash, Agent, Glob, Grep, AskUserQuestion
---

# Deliverable Gap Fixer

## 목적

gap-review가 생성한 검토보고서(JSON)를 기반으로, 사용자가 제공하는 보완 자료를 활용하여 작업물의 누락/미흡 항목을 수정하는 보완 에이전트.

## 핵심 원칙

1. **gap-review 결과 기반** — 자체 분석이 아닌, gap-review JSON의 체크리스트를 그대로 사용
2. **커버리지 먼저, 수정은 나중에** — 보완 자료로 뭘 고칠 수 있는지 먼저 보여주고, 사용자 확인 후 수정
3. **원본 보존** — 원본 작업물은 수정하지 않고, 항상 새 파일로 생성
4. **실용적 수정** — 꼬투리 잡기 없이, 누락된 내용을 추가하거나 미흡한 부분을 보강하는 데 집중

## 출력 양식 원칙

**반드시 아래 정해진 양식만 출력한다.** 추가 테이블, 요약, 부연설명, 해설을 붙이지 않는다.
각 Step의 "출력 양식" 또는 알림 양식에 정의된 형식을 그대로 따른다.

## 입력

### 필수
- **검토보고서 JSON**: gap-review가 생성한 `검토보고서_*.json` 파일
  - `$ARGUMENTS[0]`으로 경로를 받거나, 사용자에게 요청

### 보완 자료
- **보완 자료 파일**: 1개 이상의 참고 자료 (PDF, DOCX, PPTX, XLSX)
  - `$ARGUMENTS[1:]`으로 경로를 받거나, 사용자에게 요청

## JSON 스키마

입력 JSON의 정확한 스키마는 gap-review의 [output_schema.md](../gap-review/references/output_schema.md) 참조.

---

## 워크플로우 실행

### Step 0: 입력 파일 읽기

1. `$ARGUMENTS[0]`이 있으면 Read 도구로 JSON 파일을 읽는다. 없으면 사용자에게 요청.
2. JSON의 `schema_version`이 "1.0.0"인지 확인한다. 아니면 호환성 경고.
3. JSON에서 보완이 필요한 항목(final_score < 10.0)을 추출한다.
4. 보완 필요 항목이 0개이면: "모든 항목이 충족 상태입니다. 보완이 필요하지 않습니다." → 종료.
5. 보완 자료 파일을 Read 도구로 읽는다. 없으면 사용자에게 요청.

사용자에게 **반드시 아래 양식만** 출력한다. 추가 표, 해설을 붙이지 않는다:
```
검토보고서 로드 완료
- 전체 항목: {total_items}개
- 보완 필요: {보완 필요 수}개 (누락: X, 미흡: Y, 부분충족: Z, 대부분충족: W)

보완 자료를 분석합니다...
```

---

## Phase 3: 커버리지 분석

### Step 1: 커버리지 매핑 에이전트

Agent 도구로 서브에이전트(subagent_type: general-purpose)를 생성한다.

프롬프트에 반드시 포함할 내용:
- 역할: "커버리지 분석가"
- 보완 필요 항목 목록 (JSON에서 final_score < 10.0인 항목)
- 보완 자료 전체 내용
- 분석 기준:
  - 각 보완 필요 항목에 대해, 보완 자료에 관련 내용이 있는지 매핑
  - 관련 내용이 있으면: 어떤 파일의 어느 부분(섹션/페이지)에 있는지 명시
  - 관련 내용이 없으면: "커버 불가" 표시
- 원칙: 내용이 유사하면 커버 가능으로 판단, 어감/표현 차이는 무시
- 출력: **반드시 유효한 JSON**

```json
{
  "coverage": [
    {
      "item_id": 1,
      "requirement": "요구항목명",
      "final_score": 3.0,
      "coverable": true,
      "cover_source": "보완자료1.pdf 3페이지 '비용 분석' 섹션",
      "cover_description": "보완 자료에 초기 도입비용 및 월간 운영비 산출 내역이 포함되어 있음"
    },
    {
      "item_id": 2,
      "requirement": "요구항목명",
      "final_score": 0.0,
      "coverable": false,
      "cover_source": null,
      "cover_description": "보완 자료에 관련 내용 없음"
    }
  ],
  "summary": {
    "total_gaps": 10,
    "coverable_count": 6,
    "not_coverable_count": 4,
    "coverage_rate": 60.0
  }
}
```

### Step 2: 커버리지 결과 표시 및 사용자 확인

사용자에게 **반드시 아래 양식만** 출력한다. 추가 해설, 요약을 붙이지 않는다:

```
커버리지 분석 완료

보완 가능: {coverable_count}/{total_gaps}개 ({coverage_rate}%)

[커버 가능 항목]
  #{item_id} {requirement} ({final_score}점) ← {cover_source}
  ...

[커버 불가 항목]
  #{item_id} {requirement} ({final_score}점) — 관련 자료 없음
  ...
```

AskUserQuestion 도구로 사용자에게 선택지를 제시한다:

질문: "어떻게 진행할까요?"
옵션:
1. "현재 자료로 수정 진행" — 커버 가능한 항목만 수정
2. "추가 자료 첨부 후 재분석" — 사용자가 파일 추가 후 Phase 3 재실행
3. "수정 중단" — 종료

#### 옵션별 처리

**옵션 1 선택 시**: Phase 4로 진행
**옵션 2 선택 시**: 사용자에게 추가 파일을 요청 → 추가 파일을 Read로 읽기 → Step 1부터 재실행 (기존 보완 자료 + 추가 자료 합산 분석)
**옵션 3 선택 시**: "수정을 중단합니다." → 종료

---

## Phase 4: 수정 반영

### Step 3: 원본 작업물 확인

JSON의 `report.deliverable_file_path`에서 원본 작업물 경로를 가져온다.

원본 파일을 Read 도구로 읽는다. 읽기 실패 시 사용자에게 경로를 다시 요청.

#### 원본이 PDF인 경우

PDF는 직접 수정이 불가능하므로, AskUserQuestion으로 사용자에게 출력 형식을 선택하게 한다:

질문: "원본 작업물이 PDF입니다. 수정본을 어떤 형식으로 생성할까요?"
옵션:
1. "Word 문서 (DOCX)" — DOCX로 수정본 생성
2. "마크다운 (MD)" — MD로 수정본 생성
3. "둘 다 생성" — DOCX + MD 모두 생성

#### 원본이 DOCX/PPTX/기타인 경우

원본과 동일한 형식으로 수정본을 생성한다. (항상 새 파일, 원본 미수정)

### Step 4: 수정 반영 에이전트

Agent 도구로 서브에이전트(subagent_type: general-purpose)를 생성한다.

프롬프트에 반드시 포함할 내용:
- 역할: "문서 수정 전문가"
- 원본 작업물 전체 내용
- 커버 가능 항목 목록 (coverable: true인 항목)
- 각 항목의 cover_source와 cover_description
- 보완 자료 중 해당 부분 원문
- gap-review JSON의 suggestion_direction과 suggestion_example
- 수정 원칙:
  - 원본의 기존 구조와 문체를 최대한 유지
  - 누락된 항목은 적절한 위치에 새 섹션/내용 추가
  - 미흡한 항목은 기존 내용을 보강 (삭제하지 않고 추가/확장)
  - 보완 자료의 내용을 반영하되, 원본의 톤과 맥락에 맞게 조정
  - 수정된 부분은 `[수정됨]` 주석으로 표시
- 출력: 수정된 전체 문서 내용 (텍스트)

### Step 5: 수정 이력 생성 에이전트

Agent 도구로 서브에이전트를 생성한다.

프롬프트에 반드시 포함할 내용:
- 역할: "수정 이력 작성자"
- 원본 작업물 + 수정본 + 커버리지 분석 결과 + gap-review JSON
- 출력: **반드시 유효한 JSON**

```json
{
  "modification_log": {
    "source_json": "검토보고서 JSON 파일명",
    "original_file": "원본 작업물 파일명",
    "output_file": "수정본 파일명",
    "total_gaps": 10,
    "fixed_count": 6,
    "remaining_count": 4,
    "modifications": [
      {
        "item_id": 1,
        "requirement": "요구항목명",
        "before_score": 3.0,
        "action": "섹션 추가 / 내용 보강 / 표 추가 등",
        "description": "비용 분석 섹션을 3장 뒤에 추가. 초기비용/월비용/연비용 표 포함.",
        "cover_source": "보완자료1.pdf"
      }
    ],
    "remaining_items": [
      {
        "item_id": 2,
        "requirement": "요구항목명",
        "final_score": 0.0,
        "reason": "보완 자료에 관련 내용 없음"
      }
    ]
  }
}
```

---

## 출력 생성

**중요: 아래 4개 파일만 생성한다. 이 외의 파일을 절대 추가로 만들지 않는다.**

모든 파일의 타임스탬프는 동일하게 맞춘다.
저장 경로: 원본 작업물과 같은 폴더 (불가 시 Downloads)

### 생성할 파일 목록 (정확히 4개)

| # | 파일명 | 내용 | 생성 방법 |
|---|--------|------|----------|
| 1 | `수정본_YYYYMMDD_HHMMSS.md` | 수정된 작업물 전문 | Write 도구 |
| 2 | `수정본_YYYYMMDD_HHMMSS.docx` | 위 MD와 동일 내용의 Word 문서 | Python 스크립트 |
| 3 | `수정이력_YYYYMMDD_HHMMSS.md` | 수정 이력 보고서 | Write 도구 |
| 4 | `수정이력_YYYYMMDD_HHMMSS.docx` | 위 MD와 동일 내용의 Word 문서 | Python 스크립트 |

### 1단계: 수정본 MD 생성

Write 도구로 Step 4 수정 반영 에이전트의 출력을 저장한다.
파일명: `수정본_YYYYMMDD_HHMMSS.md`

### 2단계: 수정본 DOCX 생성

**반드시 실행한다.** MD만 생성하고 DOCX를 건너뛰지 않는다.

먼저 Step 4의 수정본 텍스트를 임시 .txt 파일로 저장한 뒤:
```bash
python "${CLAUDE_SKILL_DIR}/scripts/generate_fix_docx.py" "none" "{수정본_txt_임시파일_경로}" "{수정본_YYYYMMDD_HHMMSS.docx 경로}"
```

DOCX 생성 완료 후 임시 .txt 파일은 삭제한다.

### 3단계: 수정이력 MD 생성

Write 도구로 수정 이력 보고서를 생성한다.
파일명: `수정이력_YYYYMMDD_HHMMSS.md`

MD 보고서 구조 (이 형식을 정확히 따른다):

```markdown
# 수정 이력 보고서

생성일시: YYYY-MM-DD HH:MM

## 1. 개요

| 항목 | 내용 |
|------|------|
| 검토보고서 | {JSON 파일명} |
| 원본 작업물 | {파일명} |
| 수정본 파일 | {파일명} |
| 전체 보완 필요 | {total_gaps}개 |
| 수정 완료 | {fixed_count}개 |
| 잔여 항목 | {remaining_count}개 |

## 2. 수정 항목 상세

### #{item_id} {requirement} (기존 {before_score}점)
- 수정 내용: {action} — {description}
- 출처: {cover_source}

(각 수정 항목 반복)

## 3. 미수정 잔여 항목

| # | 요구항목 | 점수 | 미수정 사유 |
|---|---------|------|-----------|

## 4. 커버리지 비교

| 구분 | 수정 전 | 수정 후 |
|------|--------|--------|
| 보완 필요 항목 | {total_gaps}개 | {remaining_count}개 |
| 커버율 | 0% | {fixed_count/total_gaps * 100}% |
```

### 4단계: 수정이력 DOCX 생성

**반드시 실행한다.**

Step 5의 수정 이력 JSON을 임시 파일로 저장한 뒤:
```bash
python "${CLAUDE_SKILL_DIR}/scripts/generate_fix_docx.py" "{수정이력_json_임시파일_경로}" "none" "{수정이력_YYYYMMDD_HHMMSS.docx 경로}"
```

DOCX 생성 완료 후 임시 JSON 파일은 삭제한다.

### 5단계: 완료 알림

**반드시 아래 양식만** 출력한다:

```
수정 완료!

수정 항목: {fixed_count}/{total_gaps}개
잔여 항목: {remaining_count}개

생성된 파일:
- {수정본 MD 경로}
- {수정본 DOCX 경로}
- {수정이력 MD 경로}
- {수정이력 DOCX 경로}
```

remaining_count > 0인 경우에만 아래를 추가:
```
미수정 항목이 {remaining_count}개 있습니다.
추가 자료를 준비하여 /gap-fix를 다시 실행하면 잔여 항목을 추가 수정할 수 있습니다.
```

---

## 오류 처리

1. JSON 파일 읽기 실패 → "검토보고서 JSON 파일을 읽을 수 없습니다. gap-review를 먼저 실행해주세요."
2. schema_version 불일치 → "이 JSON은 현재 gap-fix와 호환되지 않을 수 있습니다. 계속 진행할까요?" (AskUserQuestion)
3. 원본 작업물 읽기 실패 → 사용자에게 경로 재요청
4. 보완 자료 없이 실행 → "보완 자료 파일을 첨부해주세요."
5. DOCX 생성 실패 → MD만 출력하고 DOCX 실패 사유 안내
6. 보완 필요 항목 0개 → "모든 항목이 충족 상태입니다." → 종료
