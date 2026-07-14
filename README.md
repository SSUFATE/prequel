📄Backend Convention

## Layer Structure
backend
└── app
├── main.py
...

## 🌱 Branch Strategy

### Branch 종류

| Branch | Description |
|---|---|
| main | 배포 가능한 안정 버전 |
| develop | 개발 통합 브랜치 |
| feat/* | 새로운 기능 개발 |
| fix/* | 버그 수정 |
| refactor/* | 리팩토링 |
| docs/* | 문서 수정 |
| test/* | 테스트 코드 작성 |
| chore/* | 설정 및 기타 작업 |
| hotfix/* | 긴급 수정 |

### Branch Naming

형식: `type/#이슈번호-작업내용`

예시: `feat/#12-login-api`

## ✨ Commit Message

형식: `Type: 작업 내용`

예시:
feat: 로그인 API 구현
fix: JWT 토큰 검증 오류 수정

### Commit Type

| Type | Description |
|---|---|
| feat | 새로운 기능 |
| fix | 버그 수정 |
| refactor | 리팩토링 |
| docs | 문서 수정 |
| style | 코드 스타일 변경 (포맷팅 등) |
| test | 테스트 코드 |
| chore | 설정 변경, 의존성 추가 |
| build | 빌드 관련 |
| ci | CI/CD 관련 |
| perf | 성능 개선 |
| revert | 이전 커밋 되돌리기 |

### Rules

- 하나의 커밋은 하나의 작업만 포함한다.
- 의미 없는 커밋(message, update 등)은 지양한다.
- 기능 구현 후 정상 동작 확인 후 커밋한다.
