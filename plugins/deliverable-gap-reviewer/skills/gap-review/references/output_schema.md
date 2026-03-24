# 검토보고서 JSON 스키마 (gap-review ↔ gap-fix 데이터 계약)

이 문서는 gap-review가 생성하고, gap-fix가 소비하는 JSON 파일의 정확한 스키마를 정의한다.
**gap-review와 gap-fix 양쪽 모두 이 스키마를 반드시 준수해야 한다.**

---

## 파일 저장 규칙

### 파일명 형식
```
검토보고서_YYYYMMDD_HHMMSS.json
검토보고서_YYYYMMDD_HHMMSS.md
검토보고서_YYYYMMDD_HHMMSS.docx
```
- 타임스탬프는 3개 파일 모두 동일해야 한다.
- 예: `검토보고서_20260324_143052.json`

### 저장 경로 우선순위
1. 지시서 파일과 **같은 폴더**
2. 1번이 쓰기 불가능할 경우 → 사용자 **Downloads 폴더**
3. 2번도 불가능할 경우 → 사용자에게 경로를 직접 질문

### gap-fix가 JSON을 찾는 방법
- `$ARGUMENTS[0]`으로 JSON 경로를 직접 받는다.
- 경로가 없으면 사용자에게 "gap-review 결과 JSON 파일을 첨부해주세요"라고 요청한다.

---

## JSON 스키마 정의

```json
{
  "schema_version": "1.0.0",

  "report": {
    "instruction_file": "(string) 지시서 파일명. 예: '재지시서.pdf'",
    "deliverable_file": "(string) 작업물 파일명. 예: '제안보고서.docx'",
    "instruction_file_path": "(string) 지시서 전체 경로. 예: 'C:/문서/재지시서.pdf'",
    "deliverable_file_path": "(string) 작업물 전체 경로. 예: 'C:/문서/제안보고서.docx'",
    "phase1_score": "(number) Phase 1 분석 신뢰도. 0.0~10.0",
    "phase2_overall_score": "(number) Phase 2 종합 점수. 0.0~10.0",
    "total_items": "(integer) 전체 체크리스트 항목 수",
    "fulfilled_count": "(integer) 충족 항목 수 (10.0점)",
    "partial_high_count": "(integer) 대부분충족 항목 수 (7.0~9.9점)",
    "partial_count": "(integer) 부분충족 항목 수 (4.0~6.9점)",
    "insufficient_count": "(integer) 미흡 항목 수 (1.0~3.9점)",
    "missing_count": "(integer) 누락 항목 수 (0.0점)"
  },

  "items": [
    {
      "id": "(integer) 항목 번호. 1부터 순차",
      "category": "(string) 분류명. 예: '비용 분석', '솔루션 비교'",
      "requirement": "(string) 요구항목 이름. 간결하게. 예: '솔루션 비교표 포함'",
      "detail": "(string) 상세 내용. Phase 2에서 검증 가능한 수준. 예: '3개 이상 솔루션의 기능/비용/지원 비교'",
      "source": "(string) 'explicit' 또는 'implicit'. 명시적/암묵적 요구사항 구분",
      "priority": "(string) 'required' 또는 'recommended'. 필수/권장 구분",
      "score_r1": "(number) Round 1 최종 점수. 0.0~10.0",
      "score_r2": "(number) Round 2 최종 점수. 0.0~10.0",
      "final_score": "(number) 최종 점수 = min(score_r1, score_r2)",
      "status": "(string) 'fulfilled' | 'mostly_fulfilled' | 'partial' | 'insufficient' | 'missing'",
      "tag": "(string|null) 'common' | 'reference' | null. 2회 모두 지적=common, 1회만=reference, 충족=null",
      "current_state": "(string|null) 현재 작업물의 해당 항목 상태. 충족 시 null",
      "suggestion_direction": "(string|null) 보완 방향. 충족 시 null",
      "suggestion_example": "(string|null) 이렇게 쓰라는 작성 예시. 충족 시 null"
    }
  ],

  "phase1_history": [
    {
      "round": "(string) 단계명. 예: '1차 분석', '리뷰어 피드백', '보완 분석', '최종 확인'",
      "score": "(number) 해당 단계 점수. 0.0~10.0"
    }
  ]
}
```

---

## 필드별 제약조건

| 필드 | 타입 | 필수 | 제약 |
|------|------|------|------|
| schema_version | string | O | 현재 "1.0.0" 고정 |
| report.* | - | O | 모든 report 하위 필드 필수 |
| items[].id | integer | O | 1부터 순차, 중복 불가 |
| items[].final_score | number | O | min(score_r1, score_r2)와 일치해야 함 |
| items[].status | string | O | final_score와 일치하는 상태여야 함 |
| items[].tag | string/null | O | final_score < 10.0일 때만 common/reference |
| items[].suggestion_direction | string/null | 조건부 | final_score < 10.0이면 반드시 있어야 함 |
| items[].suggestion_example | string/null | 조건부 | final_score < 10.0이면 반드시 있어야 함 |

## status 결정 규칙

| final_score | status |
|-------------|--------|
| 10.0 | fulfilled |
| 7.0 ~ 9.9 | mostly_fulfilled |
| 4.0 ~ 6.9 | partial |
| 1.0 ~ 3.9 | insufficient |
| 0.0 | missing |
