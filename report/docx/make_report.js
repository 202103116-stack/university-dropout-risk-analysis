// 팀 프로젝트2 보고서 생성 골격: node make_report.js → ../팀프로젝트2_14조_보고서.docx
// 이어서 python postprocess.py ../팀프로젝트2_14조_보고서.docx (제목 번호 연결)
//       powershell -ExecutionPolicy Bypass -File finalize.ps1 <docx 절대경로> <pdf 절대경로> (목차·필드 갱신, PDF)
//
// 규칙(CLAUDE.md): 본문의 모든 수치는 노트북 셀 출력에서 옮기고 출처(셀 번호·파일)를 함께 적는다.
// 실행 결과가 없는 숫자는 쓰지 않는다. 결론은 H1~H4별로 "맞았다/틀렸다"를 명시하고 한계 3종을 빠뜨리지 않는다.
const fs = require('fs');
const path = require('path');
const { Document, Packer, AlignmentType } = require('docx');
const S = require('./styles');
const { cover, toc } = require('./cover');
const { H, P, B, NOTE, SOURCE, tableCaption, figureCaption, table, figure, figurePlaceholder } = S;

const ASSET = (f) => fs.readFileSync(path.join(__dirname, 'assets', f));
const FIG = (f) => path.join(__dirname, '..', '..', 'notebook', 'figures', f); // 노트북이 저장한 그림

const COVER = {
  kicker: '빅데이터분석 팀 프로젝트 보고서',
  title: '다음 학년도 중도탈락 고위험 학과는 어디인가',
  subtitle: '학업지속 지원 대상 학과 선정을 위한 대학알리미 학과별 중도탈락 패널(2023~2026) 분석 및 예측',
  info: [
    ['과 목', '빅데이터분석 (AI 기반 비즈니스 데이터 분석)'],
    ['담당교수', '박주원'],
    ['조', '14조'],
    ['팀 원', '정승엽, 박유진, 신효주'],
    ['분석 자료', '교육부 대학알리미 중도탈락 학생 현황(대학, 학과별), 공공데이터포털 15164570'],
    ['Colab 노트북', '[팀 입력]'],
  ],
  date: '[팀 입력: 제출일]',
  team: '14조',
  mark: ASSET('hufs_watermark.png'),
};

const body = [
  // ── Ⅰ. 문제 정의 (15점) ─────────────────────────
  H(1, '문제 정의'),
  H(2, '의사결정과 질문'),
  B('TODO: 누가 / 무엇을 / 질문 (00_문제정의_가설.md에서 옮김)'),
  H(2, '가설과 판정 규칙(결과 확인 전 고정)'),
  B('TODO: H1~H4와 판정 규칙, 고정 일시와 git 태그 hypotheses-locked'),

  // ── Ⅱ. 수집과 정제 (20점) ───────────────────────
  H(1, '데이터 수집과 정제'),
  H(2, '수집 기록'),
  B('TODO: docs/수집_기록표.md'),
  H(2, '품질 진단'),
  B('TODO: docs/data_description.md 6대 기준 표'),
  H(2, '정제 로그'),
  B('TODO: logs/정제로그.md의 처리·건수·근거·영향 표와 단계별 추적표'),

  // ── Ⅲ. 분석과 예측 (25점) ───────────────────────
  H(1, '분석과 예측'),
  H(2, '분석 표본과 설계'),
  H(2, '기준선 대비 모델 성능'),
  H(2, '민감도'),

  // ── Ⅳ. 시각화 (15점) ────────────────────────────
  H(1, '시각화'),
  figurePlaceholder('(그림 1) 탈락 인원 × 탈락률 산점도'),
  figurePlaceholder('(그림 2) 계열, 설립유형, 지역별 고위험 비율'),
  figurePlaceholder('(그림 3) 모델 vs 기준선 적중률'),

  // ── Ⅴ. 해석과 한계 (15점) ───────────────────────
  H(1, '해석과 한계'),
  H(2, '가설 판정(H1~H4)'),
  H(2, '권고'),
  H(2, '한계'),
  B('테스트는 공시 2026 한 해뿐'),
  B('학과 단위 집계라 개인 이탈 요인을 담지 못하고, 결과는 상관이지 인과가 아님'),
  B('폐지, 통폐합, 신설 학과가 연결에서 빠지는 생존 편향과 공시 정의, 결측 패턴 변화'),

  // ── 부록 ────────────────────────────────────────
  H(1, '부록'),
  H(2, '부록 A. 재현성 확인'),
  H(2, '부록 B. 기여표'),
  H(2, '부록 C. AI 활용 기록 요약'),
];

const doc = new Document({
  creator: '14조',
  title: '빅데이터분석 팀 프로젝트2 보고서',
  styles: S.styles,
  numbering: S.numbering,
  features: { updateFields: true },
  sections: [S.frontSection([...cover(COVER), ...toc()]), S.bodySection(body)],
});

const out = path.resolve(__dirname, '..', process.argv[2] || '팀프로젝트2_14조_보고서.docx');
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(out, buf); console.log('written', out); });
