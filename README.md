# 2024-1-DSCD-ASAP-4
## 지도 플랫폼 크롤링 프로그램 개발

## Member

|이름|직책|학과|
|---------|--|---------|
|**홍지호**| 팀장 | 산업시스템공학과 |
|**안태진**| 팀원 | 산업시스템공학과 |
|**김부겸**| 팀원 | 통계학과 |
|**최대한**| 팀원 | 통계학과 |

## 실행 가이드

1. codes 폴더 경로에 selenium_multi.py / crawling_visualmap_html.py 이 잘 위치하였는지 <br/> data 폴더에 법정동.csv 이 잘 위치하였는지 확인
2. crawling_visualmap_html.py 실행
```
bokeh serve --show crawling_visualmap_html.py
```
3. 실행된 HTML에서 지역 및 키워드 입력 <br/>
    ex)
    - 동 단위 까지 검색 -> 동 까지 작성 + 키워드
    - 구 단위 까지 검색 -> 구 까지 작성 (동 작성 x) + 키워드
    - 시 단위 까지 검색 -> 시 까지 작성 + 키워드
    - 전국 -> 키워드만 입력
4. selenium_multi.py 실행되면서 크롤링 작동
5. 크롤링 완료 후 result 폴더 안에 multi_result_{}.csv 생성
6. 결과 csv를 바탕으로 HTML에 지도 시각화 결과 생성

<br/> 전체 실행 과정
-----------------------------
![framework](https://github.com/CSID-DGU/2024-1-DSCD-ASAP-4/assets/112798232/2ea8f009-9981-450e-b212-6e882d725d3d)


## Commit Message 작성 가이드

|타입 이름|내용|
|---------|:-----------------------|
|**FEAT**| 새로운 기능을 추가할 경우 |
|**FIX**| 버그를 고친 경우 |
|**DOCS**| 문서 수정한 경우 |
|**STYLE**| 코드 포맷 변경, 세미 콜론 누락, 코드 수정이 없는 경우 |
|**REFACTOR**| 프로덕션 코드 refactoring |
|**TEST**| 테스트 추가, 테스트 refactoring (프로덕션 코드 변경 없음) |
|**CHORE**| 빌드 테스크 업데이트, 패키지 매니저 설정할 경우 (프로덕션 코드 변경 없음) |
- 제목의 처음은 동사 원형으로 시작하고 첫 글자는 대문자로 작성한다.
- "Fixed", "Added", "Changed" 등 과거 시제가 아닌 "Fix", "Add", "Change"로 명령어로 시작한다.
- 총 글자수는 50자 이내며 마지막에 마침표(.)를 붙이지 않는다.
