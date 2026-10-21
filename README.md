# fishcut-site

fishcut 랜딩 페이지입니다. fishcut은 AI 에이전트가 쇼츠 초안을 만들고 사람이 다듬어 YouTube에 올리는, 내 컴퓨터에서 도는 쇼츠 에디터입니다. 이 페이지는 Google OAuth 동의 화면의 홈, 개인정보처리방침, 이용약관 주소이기도 합니다.

https://fishcut.nomadamas.org

## 주소

| 페이지 | 한국어 | 영어 |
|---|---|---|
| 홈 | `/` | `/en/` |
| 개인정보처리방침 | `/privacy/` | `/en/privacy/` |
| 이용약관 | `/terms/` | `/en/terms/` |
| 업로드 동작 설명 | `/how-it-works/` | `/en/how-it-works/` |

동의 화면에는 리디렉션 없는 최종 주소를 넣어야 하므로 끝의 `/`까지 그대로 적습니다. GitHub Pages는 `/privacy`를 `/privacy/`로 옮기는 응답(301)을 줍니다.

## 구성

- `src/shell.html`이 모든 페이지의 머리, 머리말, 꼬리말 틀입니다. 홈은 `src/layout-home.html`, 문서는 `src/layout-doc.html`이 본문을 감쌉니다.
- 본문은 언어 폴더 `src/ko/`, `src/en/`의 `home.html`, `privacy.html`, `terms.html`, `how-it-works.html`입니다.
- 언어마다 달라지는 머리말, 꼬리말 문구와 사이트 주소, 연락처, 링크는 `src/strings.json`에 있습니다. `"draft": true`인 언어는 만들지 않습니다.
- 스타일과 스크립트는 `assets/style.css`, `assets/main.js` 하나씩입니다. 스크립트가 화면에 쓰는 문구는 `main.js` 맨 위 `TEXT`에 언어별로 있습니다.
- `python3 -I tools/build.py`가 이것들을 합쳐 `index.html`, `privacy/`, `terms/`, `how-it-works/`, `en/`, `404.html`, `sitemap.xml`, `robots.txt`를 만듭니다. Python 3만 있으면 되고 설치할 패키지는 없습니다.
- 만든 파일도 커밋합니다. GitHub Pages가 빌드 단계 없이 `main` 브랜치 루트를 그대로 배포하기 때문입니다. 만든 파일을 직접 고치면 다음 빌드에서 덮어써집니다.

## 고치는 순서

1. `src/`나 `assets/`를 고칩니다. 한국어와 영어 본문은 같은 구조여야 하므로 한쪽을 고치면 다른 쪽도 함께 고칩니다.
2. `python3 -I tools/build.py`로 다시 만듭니다.
3. `python3 -I tools/build.py --check`와 `python3 -I tools/check.py`가 통과하는지 봅니다. CI(`.github/workflows/check.yml`)도 같은 두 명령을 돌립니다.

`tools/check.py`는 Google OAuth 검증과 YouTube API 정책이 요구하는 항목(방침과 약관 링크, YouTube API Services 고지, 제한적 사용(Limited Use) 문장, 권한 취소 링크, 상표 문구 등), 두 언어의 구조가 같은지, 로컬 링크와 자산이 모두 있는지를 봅니다. 외부 요청은 글꼴 CDN만 허용합니다. 디자인은 판단하지 않습니다.

## 초안 메모를 지우기 전에

사이트는 문서에 초안 메모를 단 채로 게시돼 있습니다(2026-10-21). 아래 항목을 끝내고 초안 메모를 지운 뒤 `python3 -I tools/check.py --publish`가 통과하는지 봅니다. 이 모드는 초안 언어와 초안 메모(`<aside class="note draft">`)가 남아 있으면 실패합니다.

- 개인정보처리방침, 이용약관, 업로드 동작 설명의 일부 문장(연결 해제 시 토큰 취소, 30일 재확인, 업로드 직전 고지문, 토큰 암호화, 연결 전 방침 동의)은 에디터 수정이 들어간 뒤의 동작입니다. 에디터와 다시 대조한 뒤 초안 메모를 지웁니다.
- 영어 문서는 운영 법인을 "Markr"로만 적었습니다. 등기된 영문 이름을 확인한 뒤 영어 초안 메모를 지웁니다.
- 개인정보처리방침 5절은 MCP로 AI 에이전트가 연결한 YouTube 채널 이름과 업로드 기록(영상 주소 포함)을 읽는 지금 동작을 그대로 적었습니다. 이 동작을 유지할지 에디터 쪽에서 정한 뒤 문장을 맞춥니다.
- GitHub 링크는 fishcut 저장소를 공개하기 전까지 조직 페이지(`github.com/NomaDamas`)입니다. 공개하면 `src/strings.json`의 `github` 값만 바꾸면 됩니다.
- 홈의 설치 구역은 지금 "곧 공개합니다" 안내입니다. 저장소를 공개하면 설치 카드 두 개(에이전트에게 보낼 문장, 직접 실행 명령)를 되살립니다. 원본은 커밋 9efcde6의 `src/ko/home.html` 설치 구역이고, 영어도 같은 구조로 넣습니다. 히어로의 "공개 준비 중"과 자주 묻는 질문의 "공개할 예정입니다"도 함께 고칩니다.

## 게시

- GitHub Pages는 `main` 브랜치 루트를 배포하고, 사용자 지정 도메인 `fishcut.nomadamas.org`에 HTTPS를 강제합니다. 도메인은 `CNAME` 파일에 적혀 있습니다. `.nojekyll`은 Jekyll 처리를 끄는 빈 파일입니다.
- DNS는 Cloudflare에서 `fishcut` CNAME을 `nomadamas.github.io`로 두고 프록시는 끕니다. link.nomadamas.org와 같은 방식입니다.
- 동의 화면에 이 주소를 넣으려면, Google Search Console에서 `nomadamas.org`를 Domain 속성(DNS)으로 확인한 계정이 GCP 프로젝트의 소유자나 편집자여야 합니다.

## 로컬에서 보기

`python3 -m http.server -d . 8000`을 실행한 뒤 http://127.0.0.1:8000 을 열면 됩니다. 링크가 폴더(`privacy/`)를 가리키므로 파일을 직접 열면 페이지 사이를 오갈 수 없습니다.
