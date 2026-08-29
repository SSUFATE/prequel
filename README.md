# PREQUEL (프리퀄)

> **K-콘텐츠에서 한국문학으로 이어지는 새로운 발견**

PREQUEL은 영화·드라마 등 **K-콘텐츠와 한국문학의 유사성을 분석하여 문학 작품을 추천하는 웹 서비스**입니다.

사용자가 관심 있는 K-콘텐츠를 선택하면 작품의 **시대·장르·소재·정서·관계·문화적 맥락**을 기반으로 유사한 한국문학을 추천하고, 작품 간 공통점을 함께 제공합니다.

---

## 1. 프로젝트 소개

K-콘텐츠를 통해 한국 문화에 관심을 가지게 된 사용자가 자연스럽게 한국문학까지 탐색할 수 있도록 하는 것을 목표로 합니다.

단순히 인기 있는 문학 작품을 추천하는 것이 아니라, **K-콘텐츠와 한국문학의 내용적·문화적 유사성**을 기반으로 작품을 연결합니다.

### 주요 목표

* K-콘텐츠를 기반으로 한국문학 탐색
* 태그 기반의 설명 가능한 문학 추천
* 작품 간 유사도 및 추천 이유 제공
* 한국문학의 작품 정보 및 번역본 정보 제공

---

## 2. 기술 스택

### Frontend

* Next.js
* React
* TypeScript
* CSS
* Axios

### Backend

* FastAPI
* SQLAlchemy
* Pydantic
* JWT Authentication

### Database

* PostgreSQL
* Alembic

### External API

* TMDb API
* 국립중앙도서관 API

### Tools

* Git / GitHub
* Figma
* Swagger

---

## 3. 주요 기능

### K-콘텐츠 탐색

* K-콘텐츠 목록 조회
* 제목 검색
* 검색어 자동완성
* 영화 / 드라마 콘텐츠 정보 제공

### 한국문학 추천

선택한 K-콘텐츠와 유사한 한국문학 작품을 추천합니다.

* 콘텐츠별 추천 문학 Top N 제공
* 전체 유사도 제공
* 6개 카테고리별 유사도 제공
* 공통 태그 및 작품 태그 제공
* 카테고리별 추천 결과 조회

### 문학 상세 정보

* 작품 기본 정보
* 책 소개
* 작품 태그
* K-콘텐츠와의 유사도
* 추천 이유
* 번역본 정보
* 시대적 배경 정보

### 사용자 기능

* 회원가입
* 로그인 / 로그아웃
* 사용자 정보 관리
* 관심 문학 작품 찜

---

## 4. 추천 방식

PREQUEL은 K-콘텐츠와 한국문학에 부여된 태그를 기반으로 작품 간 유사도를 계산합니다.

### 태그 카테고리

태그는 다음 6개 카테고리로 분류됩니다.

| Category           | 설명      |
| ------------------ | ------- |
| `ERA_SETTING`      | 시대 및 배경 |
| `GENRE`            | 장르      |
| `SUBJECT`          | 소재 및 주제 |
| `MOOD`             | 정서      |
| `RELATIONSHIP`     | 인물 관계   |
| `CULTURAL_CONTEXT` | 문화적 맥락  |

각 콘텐츠와 문학 작품에는 작품에서 해당 특징이 얼마나 중요한지를 나타내는 **가중치(weight)**가 부여됩니다.

추천 시 동일한 태그를 가진 K-콘텐츠와 문학 작품을 탐색하고, 각 태그의 가중치를 이용하여 유사도 점수를 계산합니다.

### 추천 과정

```text
K-콘텐츠 선택
      ↓
콘텐츠 태그 조회
      ↓
한국문학 태그와 비교
      ↓
공통 태그 및 가중치 기반 점수 계산
      ↓
카테고리별 유사도 계산
      ↓
전체 유사도 계산
      ↓
유사도 순으로 추천 문학 반환
```

추천 결과에는 단순한 점수뿐만 아니라 **공통 태그와 카테고리별 유사도**를 함께 제공하여 사용자가 추천 이유를 확인할 수 있도록 구성했습니다.

---

## 5. 프로젝트 구조

```text
PREQUEL
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── public/
│   └── ...
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── crud/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── ...
│   ├── alembic/
│   └── ...
│
└── README.md
```

> 실제 프로젝트의 최종 디렉터리 구조에 맞게 수정합니다.

---

## 6. 프로젝트 화면

### Home

<!-- 홈 화면 이미지 -->

### Search

<!-- 검색 화면 이미지 -->

### Recommendation

<!-- 문학 추천 목록 화면 이미지 -->

### Literature Detail

<!-- 문학 상세 화면 이미지 -->

### Login / Sign Up

<!-- 로그인 및 회원가입 화면 이미지 -->

### Favorites

<!-- 찜 화면 이미지 -->

---

## 7. 팀원 역할

| 담당   | 주요 역할                                                                                 |
| ---- | ------------------------------------------------------------------------------------- |
| 팀원 1 | K-콘텐츠 및 문학 데이터 구축, 추천 로직 및 Backend API 구현, 홈·검색·콘텐츠 목록·추천 문학 목록 Frontend 구현 및 API 연동  |
| 팀원 2 | 사용자 인증 및 회원 기능, 문학 상세 및 찜 기능 Backend API 구현, 로그인·회원가입·문학 상세·찜 화면 Frontend 구현 및 API 연동 |

> 실제 역할 분담에 맞게 이름과 담당 내용을 수정합니다.

---

## 8. 프로젝트 실행

### Requirements

#### Frontend

* Node.js
* npm

#### Backend

* Python
* PostgreSQL

### Environment Variables

프로젝트 실행 전 환경변수를 설정해야 합니다.

#### Frontend

`frontend/.env.local`

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8001/api/v1
```

#### Backend

`.env`

```env
DATABASE_URL=
SECRET_KEY=
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=
TMDB_API_KEY=
```

> API Key, Database 비밀번호, JWT Secret Key 등의 실제 값은 GitHub에 업로드하지 않습니다.

### Frontend 실행

```bash
cd frontend
npm install
npm run dev
```

기본적으로 다음 주소에서 실행됩니다.

```text
http://localhost:3000
```

### Backend 실행

가상환경을 활성화한 후 서버를 실행합니다.

```bash
cd backend
uvicorn app.main:app --reload --port 8001
```

---

## 9. API 문서

FastAPI에서 제공하는 Swagger UI를 통해 API 명세 및 테스트가 가능합니다.

Backend 서버 실행 후:

```text
http://127.0.0.1:8001/docs
```

주요 API는 다음과 같이 구성됩니다.

```text
/api/v1/auth
/api/v1/users
/api/v1/k-contents
/api/v1/literatures
/api/v1/favorites
```

> README에 모든 엔드포인트를 일일이 작성하기보다는 주요 API 영역과 Swagger 주소만 제공하고, 세부 명세는 Swagger에서 확인하도록 구성합니다.

---

## 10. Branch Naming Convention

프로젝트는 `main`과 `develop` 브랜치를 기준으로 기능별 브랜치를 생성하여 작업합니다.

```text
main
└── develop
    ├── feat/frontend-ui
    ├── feat/frontend-api
    ├── feat/backend-*
    └── fix/*
```

### Branch Prefix

| Prefix      | 설명        | 예시                        |
| ----------- | --------- | ------------------------- |
| `feat/`     | 새로운 기능 개발 | `feat/frontend-api`       |
| `fix/`      | 버그 수정     | `fix/literature-routing`  |
| `refactor/` | 코드 구조 개선  | `refactor/recommendation` |
| `docs/`     | 문서 수정     | `docs/readme`             |

기능 개발은 별도 브랜치에서 진행하고, 작업 완료 후 Pull Request를 통해 `develop` 브랜치에 병합합니다.

안정화된 버전은 최종적으로 `main` 브랜치에 반영합니다.




# 📄Backend Convention

## Layer Structure

## 🌱 Branch Strategy

### Branch 종류

| Branch | Description |
|---------|-------------|
| main | 배포 가능한 안정 버전 |
| develop | 개발 통합 브랜치 |
| feat/* | 새로운 기능 개발 |
| fix/* | 버그 수정 |
| refactor/* | 리팩토링 |
| docs/* | 문서 수정 |
| test/* | 테스트 코드 작성 |
| chore/* | 설정 및 기타 작업 |
| hotfix/* | 긴급 수정 |

---

### Branch Naming

형식
type/#이슈번호-작업내용

예시
feat/#12-login-api


## ✨Commit Message

형식
Type: 작업 내용

예시
feat: 로그인 API 구현
fix: JWT 토큰 검증 오류 수정

---

### Commit Type

| Type | Description |
|------|-------------|
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

---

### Rules

- 하나의 커밋은 하나의 작업만 포함한다.
- 의미 없는 커밋(message, update 등)은 지양한다.
- 기능 구현 후 정상 동작 확인 후 커밋한다.
