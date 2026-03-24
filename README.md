# Deliverable Gap Reviewer

지시서(요청서)와 작업물을 비교하여 주요 누락/미흡 항목을 검출하는 Claude Code 멀티에이전트 플러그인.

## 목적

업무 지시서(요청서)의 주요 요구사항이 작업물(보고서)에 빠짐없이 반영되었는지 확인합니다.
단어의 어감이나 표현 방식이 아닌, **주요 항목의 누락 여부**에 집중합니다.

## 워크플로우

### Phase 1: 지시서 분석
```
분석가 → 리뷰어(피드백) → 분석가(보완) → 리뷰어(최종) → 정리자
```
- 6개 에이전트가 순차적으로 요구사항을 추출/검증/구조화
- 신뢰도 점수 10.0점 기준으로 분석 품질 평가

### Phase 2: 작업물 대조
```
(항목대조자 → 품질검토자) x 2회 독립 수행 → 종합보고자
```
- 2회 독립 검토 후 낮은 점수 채택 (보수적 평가)
- [공통] / [참고] 태그로 이슈 신뢰도 구분
- 보완 방향 + 작성 예시 함께 제안

## 출력

- **MD 파일**: 마크다운 형식 상세 보고서
- **DOCX 파일**: 맑은고딕 기반 Word 문서 (동일 내용)

## 설치

### Claude Code에서 직접 설치
```bash
/plugin install deliverable-gap-reviewer@gap-reviewer
```

### 로컬 설치
```bash
git clone https://github.com/TTtaTTe/gap-reviewer.git
# Claude Code에서:
/plugin marketplace add ./gap-reviewer
/plugin install deliverable-gap-reviewer@gap-reviewer
```

## 사용법

```
/gap-review [지시서 파일경로] [작업물 파일경로]
```

또는 파일 경로 없이 실행하면 대화형으로 파일을 요청합니다:
```
/gap-review
```

### 지원 파일 형식
- PDF, DOCX, PPTX, XLSX

## 채점 기준

| 점수 | 상태 | 의미 |
|------|------|------|
| 10.0 | 충족 | 요구사항 정확히 반영 |
| 7.0~9.9 | 대부분충족 | 경미한 보완 필요 |
| 4.0~6.9 | 부분충족 | 상당 부분 미흡 |
| 1.0~3.9 | 미흡 | 요구사항과 거리 있음 |
| 0.0 | 누락 | 해당 항목 없음 |

## 요구사항

- Claude Code
- Python 3.8+
- python-docx (`pip install python-docx`)

## 라이선스

MIT
