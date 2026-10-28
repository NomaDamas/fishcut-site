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

`tools/check.py`는 Google OAuth 검증과 YouTube API 정책이 요구하는 항목(방침과 약관 링크, YouTube API Services 고지, 제한적 사용(Limited Use) 문장, 권한 취소 링크, 상표 문구 등), 두 언어의 구조가 같은지, 로컬 링크와 자산이 모두 있는지를 봅니다. 외부 요청은 글꼴 CDN만 허용합니다. 예시 쇼츠의 YouTube 플레이어는 HTML에 없고, 방문자가 재생을 누르면 `main.js`가 `youtube-nocookie.com` 플레이어를 그 카드에 넣습니다. 검사는 이 주소 말고 다른 플레이어가 없는지와 방침에 이 동작이 적혀 있는지를 봅니다. 디자인은 판단하지 않습니다.

## 공개 문구와 구현 상태

개인정보처리방침, 이용약관과 업로드 동작 설명은 2026-10-27에 적용한 권한 취소/보관 동작과 2026-10-28에 적용한 인증 정보 보호/명시적 방침 동의/업로드 고지를 설명합니다. 기존 설치의 평문은 자동으로 변환하지 않으며, 한 실행본의 적용 결과를 모든 설치의 이전 완료로 표현하지 않습니다. 게시 전에는 `python3 -I tools/check.py --publish`도 통과하는지 봅니다. 이 모드는 초안 언어와 초안 메모(`<aside class="note draft">`)가 남아 있으면 실패합니다. 내용 검사 통과는 공개 승인이나 준법 인증을 대신하지 않습니다.

- 연결 해제의 Google 토큰 취소, 실패 대기/재시도, 별도 30일 보관 기준은 에디터 [PR #474](https://github.com/NomaDamas/fishcut-dev/pull/474)에 반영됐습니다. 인증 정보와 재개용 세션의 AES-256-GCM 보호, OS 키 보관, 연결/검토/전송 전 사람의 명시적 동의, 일반/예약 업로드의 최종 고지는 [PR #488](https://github.com/NomaDamas/fishcut-dev/pull/488)에 반영됐습니다. 종료/절전 중 달력 기준 삭제 기한과 Google 판단은 [이슈 #336](https://github.com/NomaDamas/fishcut-dev/issues/336)에 남아 있습니다.
- 저장 보호 범위는 인증 정보와 재개용 세션이며 DB/프로젝트 전체 암호화가 아닙니다. 기존 평문은 모든 게시기를 멈추고 별도 승인한 명령으로만 변환합니다. 키가 없거나 손상된 상태는 사용과 유지보수를 중단하며, 키를 교체하거나 연결을 삭제해 우회하지 않습니다. 백업 삭제와 잠긴 Keychain, 재부팅/전원 손실, 다른 플랫폼의 동작을 검증했다고 표현하지 않습니다.
- 방침 동의는 앱의 명시적인 버전과 연결됩니다. 웹페이지 갱신일만 바꾸면 자동으로 재동의를 요구한다고 약속하지 않습니다. 공개 문구의 변경은 완성된 diff를 승인받은 뒤 발행합니다. 이전 화면 이미지는 캡션에서 현재 동의 UI 추가 전의 예시임을 밝힙니다.
- 운영자는 기존 NomaDamas, 법인 (주)Markr이며 영어 표기 "Markr"도 그대로 유지합니다. 이번 문구 정정은 운영자 변경이나 등기 영문명 확인을 뜻하지 않습니다.
- 개인정보처리방침 5절은 MCP로 AI 에이전트가 연결한 YouTube 채널 이름과 업로드 기록(영상 주소 포함)을 읽는 지금 동작을 그대로 적었습니다. 이 동작을 유지할지 에디터 쪽에서 정한 뒤 문장을 맞춥니다.
- GitHub 링크는 공개용 소개 저장소 `github.com/NomaDamas/fishcut`입니다. `src/strings.json`의 `github` 값이 한국어와 영어의 모든 GitHub 링크에 적용됩니다. 현재 공개 범위는 README이며 개발 코드나 레퍼런스 자료는 포함하지 않습니다.
- 홈의 설치 구역은 지금 "곧 공개합니다" 안내입니다. 실제 코드와 설치 방법을 공개하면 설치 카드 두 개(에이전트에게 보낼 문장, 직접 실행 명령)를 되살립니다. README만 공개한 상태에서는 설치 안내를 유지합니다. 원본은 커밋 9efcde6의 `src/ko/home.html` 설치 구역이고, 영어도 같은 구조로 넣습니다. 코드 공개 후 히어로의 "공개 준비 중"과 자주 묻는 질문의 "공개할 예정입니다"도 함께 고칩니다.

## 게시

- GitHub Pages는 `main` 브랜치 루트를 배포하고, 사용자 지정 도메인 `fishcut.nomadamas.org`에 HTTPS를 강제합니다. 도메인은 `CNAME` 파일에 적혀 있습니다. `.nojekyll`은 Jekyll 처리를 끄는 빈 파일입니다.
- DNS는 Cloudflare에서 `fishcut` CNAME을 `nomadamas.github.io`로 두고 프록시는 끕니다. link.nomadamas.org와 같은 방식입니다.
- 동의 화면에 이 주소를 넣으려면, Google Search Console에서 `nomadamas.org`를 Domain 속성(DNS)으로 확인한 계정이 GCP 프로젝트의 소유자나 편집자여야 합니다.

## 로컬에서 보기

`python3 -m http.server -d . 8000`을 실행한 뒤 http://127.0.0.1:8000 을 열면 됩니다. 링크가 폴더(`privacy/`)를 가리키므로 파일을 직접 열면 페이지 사이를 오갈 수 없습니다.
