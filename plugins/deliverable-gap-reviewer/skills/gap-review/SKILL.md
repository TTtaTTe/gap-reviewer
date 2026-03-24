---
name: gap-review
description: "지시서(요청서)와 작업물을 비교하여 주요 누락/미흡 항목을 검출합니다. 두 개의 파일(지시서 + 작업물)을 받아 멀티에이전트 분석 후 MD/DOCX 보고서를 생성합니다. Use when comparing an instruction document against a deliverable to find gaps."
argument-hint: "[지시서 파일경로] [작업물 파일경로]"
user-invocable: true
allowed-tools: Read, Write, Bash, Agent, Glob, Grep, AskUserQuestion
---

# Deliverable Gap Reviewer

## 목적

지시서(요청서)의 **주요 요구사항**이 작업물에 빠짐없이 반영되었는지 확인하는 멀티에이전트 리뷰 시스템.

## 핵심 원칙 (모든 에이전트에 반드시 적용)

1. **큰 항목 누락 검출이 목적** - 단어의 어감, 표현 방식, 문체 등은 검토 대상이 아님
2. **꼬투리 잡기 금지** - "~합니다 vs ~한다" 같은 문체 차이, 어감 차이는 무시
3. **주요 요구사항 중심** - 지시서가 명시적으로 요청한 핵심 항목만 체크
4. **실용적 보완 제안** - 문제 지적에 그치지 않고, 방향 + 작성 예시를 함께 제시

## 입력

- 지원 형식: PDF, DOCX, PPTX, XLSX
- 인자: `$ARGUMENTS` 로 두 파일 경로를 받거나, 대화에서 파일을 요청
  - `$ARGUMENTS[0]`: 지시서(요청서) 파일 경로
  - `$ARGUMENTS[1]`: 작업물 파일 경로 (없으면 Phase 1 완료 후 요청)

## 채점 기준

상세 채점 기준은 [scoring_rubric.md](references/scoring_rubric.md) 참조.

## JSON 출력 스키마 및 저장 규칙

gap-fix 스킬과의 데이터 연결을 위해, Phase 2 완료 후 반드시 JSON 파일을 생성한다.
상세 스키마는 [output_schema.md](references/output_schema.md) 참조.

### 저장 경로 우선순위
1. 지시서 파일과 **같은 폴더**
2. 쓰기 불가 시 → 사용자 **Downloads 폴더**
3. 그래도 불가 시 → 사용자에게 경로 질문

### 파일명 형식
`검토보고서_YYYYMMDD_HHMMSS.json` (MD, DOCX와 동일 타임스탬프)

---

## 워크플로우 실행

### 파일 읽기

1. `$ARGUMENTS[0]`이 있으면 Read 도구로 지시서 파일을 읽는다. 없으면 사용자에게 요청한다.
2. 읽은 내용을 이후 에이전트들에게 전달한다.

---

## Phase 1: 지시서 분석

### Step 1: 분석가 (Analyst) - 1차 추출

Agent 도구로 서브에이전트(subagent_type: general-purpose)를 생성한다.

프롬프트에 반드시 포함할 내용:
- 역할: "요구사항 분석가"
- 지시서 원문 전체
- 추출 기준: 주요 요구항목, 체크포인트, 요청사항을 항목별로 추출
- 원칙: 큰 항목 위주 추출, 세부 표현/어감/문체 무시
- 분류: "명시적 요구사항" / "암묵적 요구사항" / "기타 조건/제약사항"
- 출력 형식: 표 형태 (# | 요구항목 | 상세내용 | 근거위치)

분석가의 출력을 기억해둔다.

### Step 2: 리뷰어 (Reviewer) - 1차 검토

Agent 도구로 서브에이전트를 생성한다.

프롬프트에 반드시 포함할 내용:
- 역할: "요구사항 리뷰어"
- 지시서 원문 전체 + 분석가 결과
- 검토 기준: 완전성(2.5) + 정확성(2.5) + 구체성(2.5) + 분류체계(2.5) = 10.0점
- 원칙: 꼬투리 잡기 금지, 주요 항목 누락만 지적
- 출력: 누락된 항목 / 잘못 해석된 항목 / 보완 필요 항목 + 신뢰도 점수

### Step 3: 분석가 (Analyst) - 피드백 반영

Agent 도구로 서브에이전트를 생성한다.

프롬프트에 반드시 포함할 내용:
- 역할: "요구사항 분석가" - 리뷰어 피드백을 반영하여 보완
- 지시서 원문 + 1차 추출 결과 + 리뷰어 피드백
- 새로 추가/수정된 항목에 [보완됨] 태그
- 출력: 보완된 전체 요구사항 목록

### Step 4: 리뷰어 (Reviewer) - 최종 확인

Agent 도구로 서브에이전트를 생성한다.

프롬프트에 반드시 포함할 내용:
- 역할: "요구사항 리뷰어" - 최종 확인
- 지시서 원문 + 보완된 분석 결과 + 1차 피드백
- 출력: 피드백 반영 여부 + 추가 누락 + 최종 신뢰도 점수(10.0 기준)

### Step 5: 정리자 (Organizer) - 체크리스트 생성

Agent 도구로 서브에이전트를 생성한다.

프롬프트에 반드시 포함할 내용:
- 역할: "체크리스트 정리자"
- 최종 분석 결과 + 리뷰어 최종 확인
- 출력 형식: **반드시 유효한 JSON** 으로 출력

```json
{
  "checklist": [
    {
      "id": 1,
      "category": "분류명",
      "requirement": "요구항목 이름",
      "detail": "상세 내용 (검증 가능한 수준)",
      "source": "명시적 / 암묵적",
      "priority": "필수 / 권장"
    }
  ],
  "total_items": 숫자,
  "phase1_score": 숫자
}
```

- 원칙: 각 항목이 Phase 2에서 "있다/없다"로 판별 가능해야 함, 우선순위 구분

### Phase 1 완료 알림

사용자에게 알린다:
```
Phase 1 분석 완료
- 추출된 요구항목: {total_items}개 (필수: X개, 권장: Y개)
- 분석 신뢰도: {phase1_score}/10.0

작업물(보고서) 파일을 첨부해주세요.
```

`$ARGUMENTS[1]`이 있으면 바로 Phase 2로 진행한다.

---

## Phase 2: 작업물 대조 검토

Read 도구로 작업물 파일을 읽는다.

### Round 1

#### Step 6: 항목 대조자 (Compliance Checker) - 1차

Agent 도구로 서브에이전트를 생성한다.

프롬프트에 반드시 포함할 내용:
- 역할: "항목 대조자" - 체크리스트 항목이 작업물에 존재하는지 1:1 대조
- 체크리스트 JSON + 작업물 전체 내용
- 채점: 10.0(완전충족) ~ 0.0(누락)
- 원칙: 표현 방식 달라도 내용 동일하면 충족, 어감/문체 차이 감점 안 함
- 출력: 표 (# | 요구항목 | 점수 | 판단근거)

#### Step 7: 품질 검토자 (Quality Reviewer) - 1차

Agent 도구로 서브에이전트를 생성한다.

프롬프트에 반드시 포함할 내용:
- 역할: "품질 검토자" - 충족 수준 심층 평가
- 체크리스트 JSON + 작업물 전체 내용 + 항목 대조 결과
- 평가: 의도 반영 여부, 내용 깊이, 구성요소 포함 여부
- 원칙: 큰 그림 평가, 완벽한 문장 불요구
- 부족 항목에 "무엇이 부족한지" 구체 기술
- 출력: 표 (# | 요구항목 | 점수 | 충족수준 | 부족한 부분)

### Round 2

**중요**: 1차 결과를 보여주지 않고 독립적으로 Step 6, 7을 다시 수행한다.

### Step 8: 종합 보고자 (Report Generator)

Agent 도구로 서브에이전트를 생성한다.

프롬프트에 반드시 포함할 내용:
- 역할: "종합 보고자"
- 1차/2차 항목대조 결과 + 1차/2차 품질검토 결과 + 체크리스트 JSON
- 점수 처리 규칙:
  - 각 항목 최종 점수 = 2회 중 **낮은 점수** 채택
  - 종합 점수 = 전체 항목 평균 (필수 항목 1.5배 가중)
  - 2회 모두 지적 → [공통] 태그
  - 1회만 지적 → [참고] 태그
- 보완 제안: suggestion_direction(방향) + suggestion_example(작성 예시) 반드시 작성
- 출력: **반드시 유효한 JSON**

```json
{
  "schema_version": "1.0.0",
  "report": {
    "instruction_file": "파일명",
    "deliverable_file": "파일명",
    "instruction_file_path": "전체 경로",
    "deliverable_file_path": "전체 경로",
    "phase1_score": 숫자,
    "phase2_overall_score": 숫자,
    "total_items": 숫자,
    "fulfilled_count": 숫자,
    "partial_high_count": 숫자,
    "partial_count": 숫자,
    "insufficient_count": 숫자,
    "missing_count": 숫자
  },
  "items": [
    {
      "id": 1,
      "category": "분류명",
      "requirement": "요구항목",
      "detail": "상세 내용 (검증 가능한 수준)",
      "source": "explicit 또는 implicit",
      "priority": "required 또는 recommended",
      "score_r1": 숫자,
      "score_r2": 숫자,
      "final_score": 숫자,
      "status": "충족/대부분충족/부분충족/미흡/누락",
      "tag": "공통/참고/null",
      "current_state": "현재 상태 또는 null",
      "suggestion_direction": "보완 방향 또는 null",
      "suggestion_example": "작성 예시 또는 null"
    }
  ],
  "phase1_history": [
    {"round": "1차 분석", "score": 숫자},
    {"round": "최종 확인", "score": 숫자}
  ]
}
```

---

## 출력 생성

### 1. MD 파일 생성

Write 도구로 마크다운 보고서를 생성한다.
파일명: `검토보고서_YYYYMMDD_HHMMSS.md`
저장 경로: 지시서 파일과 같은 폴더, 또는 사용자 Downloads 폴더.

MD 보고서 구조:
1. 개요 (파일명, 점수, 요약 표)
2. 항목별 대조 결과 (전체 항목 표)
3. 보완 필요 체크리스트 (점수대별 분류, 각 항목에 현재상태 + 보완방향 + 작성예시)
4. 충족 항목
5. Phase 1 분석 이력

### 2. DOCX 파일 생성

종합 보고자의 JSON 결과를 임시 JSON 파일로 저장한 뒤, 아래 명령으로 DOCX를 생성한다:

```bash
python "${CLAUDE_SKILL_DIR}/scripts/generate_docx.py" "{json_path}" "{output_docx_path}"
```

파일명: `검토보고서_YYYYMMDD_HHMMSS.docx`
DOCX는 MD와 동일한 내용을 맑은고딕 폰트로 출력한다.

### 3. 완료 알림

```
검토 완료!

종합 점수: {phase2_overall_score} / 10.0
- 충족: {fulfilled_count}개
- 보완 필요: {나머지}개

보고서 저장 위치:
- {md_path}
- {docx_path}
```

---

## 오류 처리

1. 파일 읽기 실패 → "파일을 읽을 수 없습니다. 다른 형식으로 첨부해주세요."
2. JSON 파싱 실패 → 해당 에이전트에게 JSON만 재요청 (1회)
3. DOCX 생성 실패 → MD만 출력하고 DOCX 실패 사유 안내
4. Phase 1 신뢰도 9.5 미만 → 경고 표시 후 최고 점수 버전으로 진행
