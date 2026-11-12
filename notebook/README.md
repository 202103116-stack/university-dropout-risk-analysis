# 노트북 사용 안내 (Colab이 정본)

- 팀 정본 Colab: https://colab.research.google.com/drive/1JCE1qZSWkixXybo86cDwFJpl4_n-Tbmc?usp=sharing
- GitHub 저장소: https://github.com/202103116-stack/university-dropout-risk-analysis

1. `팀프로젝트2_14조.ipynb`를 Google Drive에 업로드하고 Colab으로 엽니다
   (Drive → 새로 만들기 → 파일 업로드 → 우클릭 → Google Colaboratory로 열기).
2. Colab 왼쪽 파일(폴더) 아이콘 → 업로드 → `../data/raw/교육부_대학알리미_중도탈락 학생 현황 _대학_학과별_20260831.csv`를 함께 올립니다.
   노트북 0번 셀이 Colab(`/content/`)과 로컬(`../data/raw/`) 후보 경로를 차례로 찾습니다. Drive 마운트를 쓰면 후보 경로에 추가합니다.
3. 우측 상단 **공유** → "링크가 있는 모든 사용자" → 링크를 복사해 `../logs/재현성_확인표.md`와 보고서 표지(Colab 노트북 칸)에 붙입니다. `[팀 입력]`
4. 이후 작업은 Colab 노트북을 정본으로 삼습니다. 이 폴더의 .ipynb는 로컬 테스트, 백업용입니다. 로컬을 고치기 전에 Colab과 동기화 상태를 먼저 확인합니다.
5. 제출 직전, 팀원 3명이 각자 자기 Google 계정으로 **런타임 → 다시 시작 및 모두 실행**을 돌려 `../logs/재현성_확인표.md`를 채웁니다.
6. 그림은 `figures/`에 저장합니다(보고서 `report/docx/make_report.js`가 이 폴더에서 읽음).
7. 노트북 구성은 안내문 5단계(① 문제 정의, ② 수집, ③ 정제, ④ 분석, ⑤ 발표)와 부록(재현성)입니다. 수치를 출력하는 셀은 맨 위 주석에 셀 ID(예: `s3-16`)가 있습니다. 보고서나 발표에 옮길 때는 `(출처: 노트북 §③ 셀 s3-16)`처럼 적습니다.
8. 집단별 탈락률 계산(④)은 `00_문제정의_가설.md` v2가 커밋되고 git 태그 `hypotheses-locked-v2`가 달린 뒤에만 합니다.

로컬 실행: VS Code에서 커널 "Python (팀프로젝트2 14조)"(`.venv`, Python 3.13)를 선택합니다.
