# Claude Code 마켓플레이스 등록 체크리스트

플러그인을 마켓플레이스에 등록할 때 한 번에 문제 없이 등록하기 위한 가이드.

---

## 1. 디렉토리 구조 체크

```
my-marketplace/                          ← 레포 루트
├── .claude-plugin/
│   └── marketplace.json                 ← 마켓플레이스 카탈로그 (필수)
├── README.md
└── plugins/
    └── my-plugin/                       ← 플러그인 (반드시 별도 하위 디렉토리)
        ├── .claude-plugin/
        │   └── plugin.json              ← 플러그인 매니페스트
        └── skills/
            └── my-skill/
                ├── SKILL.md             ← 스킬 진입점 (필수)
                └── (부가 파일들)
```

### 체크항목

- [ ] `.claude-plugin/marketplace.json`이 **레포 루트**에 있는가
- [ ] `.claude-plugin/plugin.json`이 **플러그인 하위 디렉토리**에 있는가
- [ ] marketplace와 plugin의 `.claude-plugin/`이 **서로 다른 디렉토리**에 있는가
- [ ] `skills/`, `agents/`, `commands/`가 **플러그인 루트 레벨**에 있는가 (`.claude-plugin/` 내부 아님)
- [ ] 플러그인 외부 파일을 `../`로 참조하지 않는가 (캐시 복사 시 깨짐)

---

## 2. marketplace.json 체크

```json
{
  "name": "my-marketplace",           // 필수: kebab-case
  "owner": {
    "name": "팀명"                     // 필수
  },
  "metadata": {
    "description": "설명",             // 권장
    "version": "1.0.0"                // 권장
  },
  "plugins": [
    {
      "name": "my-plugin",            // 필수: kebab-case
      "source": "./plugins/my-plugin", // 필수: ./ 로 시작
      "description": "설명",           // 권장
      "version": "1.0.0"              // 권장 (plugin.json에 없을 때)
    }
  ]
}
```

### 체크항목

- [ ] `name`이 kebab-case인가 (소문자, 숫자, 하이픈만)
- [ ] `owner.name`이 있는가
- [ ] `plugins` 배열에 최소 1개 항목이 있는가
- [ ] 각 플러그인에 `name`과 `source`가 있는가
- [ ] `source` 상대경로가 `./`로 시작하는가 (`"."` 아님!)
- [ ] `source`가 가리키는 경로에 실제 플러그인 디렉토리가 있는가
- [ ] 플러그인 `name`이 중복되지 않는가
- [ ] 예약된 이름을 사용하지 않는가 (claude-code-marketplace, anthropic-* 등)

---

## 3. plugin.json 체크

```json
{
  "name": "my-plugin",                // 필수: kebab-case, 스킬 네임스페이스로 사용됨
  "version": "1.0.0",                 // 권장
  "description": "설명",               // 권장
  "author": {
    "name": "작성자"                   // 권장
  },
  "keywords": ["tag1", "tag2"]        // 권장
}
```

### 체크항목

- [ ] `name`이 있는가 (매니페스트가 있으면 필수)
- [ ] `name`이 kebab-case인가
- [ ] 버전이 marketplace.json과 plugin.json **양쪽에 동시 설정되지 않았는가** (한 곳만)
- [ ] `category`, `license` 등 불필요한 비표준 필드가 오류를 일으키지 않는가

---

## 4. SKILL.md frontmatter 체크 (가장 중요!)

```yaml
---
name: my-skill                      # 선택 (없으면 폴더명 사용)
description: "스킬 설명"              # 권장 (없으면 첫 문단 사용)
user-invocable: true                # 사용자가 /로 호출하려면 반드시 true
allowed-tools: Read, Write, Bash    # 스킬이 사용할 도구
---
```

### 체크항목

- [ ] **`user-invocable: true`가 명시되어 있는가** (빠지면 기본값 true이지만, 명시 권장)
- [ ] `description`이 있는가 (없으면 Claude가 자동 호출 판단 못함)
- [ ] `allowed-tools`에 스킬에 필요한 모든 도구가 나열되어 있는가
- [ ] `name`이 소문자, 숫자, 하이픈만 사용하는가 (최대 64자)
- [ ] YAML 문법이 올바른가 (따옴표, 들여쓰기)

### frontmatter 조합 주의사항

| 설정 | 사용자 /호출 | Claude 자동 호출 | 비고 |
|------|-------------|-----------------|------|
| (아무것도 안 씀) | O | O | 기본값. 대부분 이걸 원함 |
| `user-invocable: true` | O | O | 명시적으로 동일 |
| `disable-model-invocation: true` | O | X | 수동 전용. 설명이 컨텍스트에 안 올라감 |
| `user-invocable: false` | X | O | 배경 지식 전용 |
| `disable-model-invocation: true` + `user-invocable` 미지정 | O | X | **함정!** 작동은 하지만 혼동 가능 |

---

## 5. 배포 전 검증

```bash
# 1. JSON/YAML 구문 검증
claude plugin validate .

# 2. 로컬 마켓플레이스 등록 테스트
claude plugin marketplace add ./my-marketplace

# 3. 플러그인 설치 테스트
claude plugin install my-plugin@my-marketplace

# 4. 새 세션에서 스킬 호출 테스트 (중요!)
# Claude Code 재시작 후:
/my-plugin:my-skill

# 5. 문제 시 디버그
claude --debug
```

### 체크항목

- [ ] `claude plugin validate .` 통과하는가
- [ ] 로컬 경로로 마켓플레이스 등록이 되는가
- [ ] 플러그인 설치가 되는가
- [ ] **새 세션에서** `/plugin-name:skill-name`으로 호출이 되는가
- [ ] 스킬 실행 시 도구 권한 오류가 없는가

---

## 6. 흔한 실수 TOP 10

| # | 실수 | 증상 | 해결 |
|---|------|------|------|
| 1 | marketplace.json 없이 plugin.json만 있음 | "마켓플레이스 추가 실패" | `.claude-plugin/marketplace.json` 생성 |
| 2 | marketplace와 plugin이 같은 `.claude-plugin/` 공유 | 마켓플레이스 등록 실패 | 플러그인을 `plugins/` 하위로 분리 |
| 3 | source가 `"."` 또는 `"./"` 없이 시작 | 경로 못 찾음 | `"./plugins/my-plugin"` 형태로 수정 |
| 4 | `user-invocable: true` 누락 | 스킬이 `/` 메뉴에 안 나옴 | frontmatter에 명시 추가 |
| 5 | `skills/`를 `.claude-plugin/` 안에 넣음 | 스킬 인식 안 됨 | 플러그인 루트 레벨로 이동 |
| 6 | plugin.json과 marketplace.json 양쪽에 버전 | marketplace 버전 무시됨 | 한 곳에만 설정 |
| 7 | 플러그인 이름에 대문자/공백 사용 | Claude.ai 동기화 거부 | kebab-case만 사용 |
| 8 | 세션 중간에 설치 후 바로 테스트 | 스킬 인식 안 됨 | 새 세션에서 테스트 |
| 9 | 스크립트 경로에 절대경로 사용 | 다른 환경에서 실패 | `${CLAUDE_SKILL_DIR}` 또는 `${CLAUDE_PLUGIN_ROOT}` 사용 |
| 10 | YAML frontmatter 구문 오류 | 스킬이 메타데이터 없이 로드 | `---` 사이의 YAML 문법 확인 |

---

## 7. 최소 필수 파일 요약

마켓플레이스에 스킬 1개를 등록하기 위한 **절대 최소 구성**:

```
repo/
├── .claude-plugin/
│   └── marketplace.json          # name, owner.name, plugins[].name, plugins[].source
└── plugins/
    └── my-plugin/
        ├── .claude-plugin/
        │   └── plugin.json       # name
        └── skills/
            └── my-skill/
                └── SKILL.md      # user-invocable: true, description
```

**파일 3개, 필수 필드 5개**만 채우면 등록 가능.

---

## 8. 호출 형식

등록 후 사용자는 아래 형식으로 호출:

```
# 마켓플레이스 등록
/plugin marketplace add owner/repo

# 플러그인 설치
/plugin install {plugin-name}@{marketplace-name}

# 스킬 실행
/{plugin-name}:{skill-name} [인자]
```

예시:
```
/plugin marketplace add TTtaTTe/gap-reviewer
/plugin install deliverable-gap-reviewer@gap-reviewer
/deliverable-gap-reviewer:gap-review 지시서.pdf 작업물.docx
```
