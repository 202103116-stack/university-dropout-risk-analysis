// 보고서 템플릿(스타일 견본) 생성: node make_template.js → ../팀프로젝트2_보고서_템플릿.docx
// 이어서 python postprocess.py <docx> 로 제목 1~4 스타일에 자동 번호(Ⅰ./1./가./1))를 연결한다.
const fs = require('fs');
const path = require('path');
const { Document, Packer, AlignmentType } = require('docx');
const S = require('./styles');
const { cover, toc } = require('./cover');

const COVER = {
  kicker: '빅데이터분석 팀 프로젝트 보고서',
  title: '(보고서 제목) 다음 학년도 중도탈락 고위험 학과는 어디인가',
  subtitle: '(부제) 학업지속 지원 대상 학과 선정을 위한 대학알리미 학과별 중도탈락 패널(2023~2026) 분석 및 예측',
  info: [
    ['과 목', '빅데이터분석 (AI 기반 비즈니스 데이터 분석)'],
    ['담당교수', '박주원'],
    ['조', '14조'],
    ['팀 원', '정승엽, 박유진, 신효주'],
    ['분석 자료', '교육부 대학알리미 중도탈락 학생 현황(대학, 학과별), 공공데이터포털 15164570'],
    ['자료 저장소', 'github.com/202103116-stack/university-dropout-risk-analysis'],
    ['Colab 노트북', 'https://colab.research.google.com/drive/1JCE1qZSWkixXybo86cDwFJpl4_n-Tbmc?usp=sharing'],
  ],
  date: '2026. 11. 12.',
  team: '14조',
  mark: fs.readFileSync(path.join(__dirname, 'assets', 'hufs_watermark.png')),
};

const body = [
  S.H(1, '대제목: 제목 1 (한국외대체 B 17pt, 아래 구분선)'),
  S.P('본문은 휴먼명조 11pt, 줄 간격 160%, 양쪽 정렬입니다. 공공기관 보고서처럼 핵심 내용은 아래의 □ ○ - 기호 체계로 나누어 씁니다. 강조할 단어는 **굵게** 표시합니다.'),
  S.H(2, '중제목: 제목 2 (한국외대체 B 13.5pt)'),
  S.B('1단계 글머리: 핵심 주장이나 결론 한 줄'),
  S.B('2단계 글머리: 주장을 뒷받침하는 근거', 1),
  S.B('3단계 글머리: 수치·세부 내용', 2),
  S.B('4단계 글머리: 보충 설명', 3),
  S.H(3, '소제목: 제목 3 (한국외대체 M 12pt)'),
  S.P('제목 번호(Ⅰ. → 1. → 가. → 1))는 Word의 다단계 목록에 연결되어 있어, 제목을 추가하거나 지우면 자동으로 다시 매겨집니다.'),
  S.H(4, '세부 항목: 제목 4 (휴먼명조 11pt 굵게)'),
  S.P('제목 4는 본문과 같은 글꼴을 쓰되 굵게 표시해 세부 항목을 구분합니다.'),
  S.NOTE('참고 박스: 한계, 용어 정의, 데이터 주의사항 등 본문과 구분해 강조할 내용을 넣습니다(맑은 고딕 9.5pt, 연한 음영).'),

  S.H(2, '표·그림 양식'),
  S.tableCaption('표 양식 예시 (제목은 표 위, 번호 자동)'),
  S.table(
    ['구분', '항목', '수치', '비고'],
    [
      ['예시 1', '표 본문은 맑은 고딕 10pt', '27,203', '숫자는 오른쪽 정렬'],
      ['예시 2', '머리글은 굵게·음영·가운데', '18.86%', '위·아래 굵은 선'],
    ],
    [1600, 3638, 1600, 2800],
    { align: [AlignmentType.CENTER, AlignmentType.LEFT, AlignmentType.RIGHT, AlignmentType.LEFT] },
  ),
  S.SOURCE('자료: 출처 표기 양식(맑은 고딕 8pt, 오른쪽 정렬)'),
  S.figurePlaceholder(),
  S.figureCaption('그림 양식 예시 (제목은 그림 아래, 번호 자동)'),

  S.H(1, '두 번째 대제목 (번호가 II.로 이어짐)'),
  S.H(2, '중제목 번호가 1.부터 다시 시작'),
  S.H(3, '소제목 가.'),
  S.H(3, '소제목 나.'),
  S.H(4, '세부 항목 1)'),
  S.H(4, '세부 항목 2)'),
];

const doc = new Document({
  creator: '14조',
  title: '빅데이터분석 팀 프로젝트2 보고서 템플릿',
  styles: S.styles,
  numbering: S.numbering,
  features: { updateFields: true },
  sections: [S.frontSection([...cover(COVER), ...toc()]), S.bodySection(body)],
});

const out = path.resolve(__dirname, '..', process.argv[2] || '팀프로젝트2_보고서_템플릿.docx');
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(out, buf); console.log('written', out); });
