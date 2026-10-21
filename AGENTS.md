# fishcut-site

fishcut 랜딩 페이지 저장소다. 구성, 명령, 게시 방법은 `README.md`가 정본이다.

## 규칙

- 만든 파일(`index.html`, `privacy/`, `terms/`, `how-it-works/`, `en/`, `404.html`, `sitemap.xml`, `robots.txt`)을 직접 고치지 않는다. `src/`와 `assets/`를 고치고 `python3 -I tools/build.py`로 다시 만든다.
- 한국어와 영어 본문은 같은 구조(태그, class, id, 링크)를 유지한다. 한쪽만 고치면 `tools/check.py`가 실패한다.
- 커밋 전에 `python3 -I tools/build.py --check`와 `python3 -I tools/check.py`를 통과시킨다.
- 외부 요청은 글꼴 CDN만 둔다. 분석 도구, 추적 스크립트, iframe을 넣으려면 개인정보처리방침부터 고쳐야 하고, 넣을지는 사용자가 정한다.
- 개인정보처리방침과 이용약관의 문장은 에디터의 실제 동작과 같아야 한다. 에디터에서 확인하지 않은 동작을 적지 않는다.
- Pages 설정, 사용자 지정 도메인, DNS는 사용자 승인 뒤에만 바꾼다.
- 화면에 보이는 글에는 화살표, em dash, 가운뎃점, 동그라미 숫자, 이모지를 쓰지 않는다. `tools/check.py`가 잡는다.
- 앱 이름은 문장 처음에서도 소문자 `fishcut`이다.
