// 팀 프로젝트2 보고서 생성 골격: node make_report.js → ../팀프로젝트2_14조_보고서.docx
// 이어서 python postprocess.py ../팀프로젝트2_14조_보고서.docx (제목 번호 연결)
//       powershell -ExecutionPolicy Bypass -File finalize.ps1 <docx 절대경로> <pdf 절대경로> (목차·필드 갱신, PDF)
//
// 구성: 안내문 5단계 기준 — Ⅰ 문제 정의 / Ⅱ 수집 / Ⅲ 정제 / Ⅳ 분석 / Ⅴ 시각화·해석·한계
//       부록 A 재현성 / B 기여도표 / C AI 활용 로그 / D 정제 로그 전체 / E 보조 분석 R1
//
// 규칙(CLAUDE.md, docs/기준_정리.md):
//  - 본문의 모든 수치는 노트북 셀 출력에서 옮기고 출처를 함께 적는다. 실행 결과가 없는 숫자는 쓰지 않는다.
//  - 결론은 가설 A·B별로 "맞았다/부분 맞았다/틀렸다"를 명시하고 한계 3종을 빠뜨리지 않는다.
//
// ★ 출처 줄 헬퍼 규칙 (출처 없는 수치는 건당 −2점)
//  - 표는 반드시 srcTable(...)로, 그림은 반드시 srcFigure(...)로 넣는다. table()/figure()를 직접 body에 넣지 않는다.
//  - 두 헬퍼는 표·그림 바로 아래에 S.SOURCE 출처 줄을 붙인다. source 인자가 비어 있으면 '출처: [팀 입력]'을 넣어
//    빈칸이 눈에 띄게 한다(제출 전 '[팀 입력]' 검색으로 0건 확인).
//  - 출처 형식: '출처: 노트북 §③ 셀 s3-16 / 정제로그 표 4' 처럼 셀 ID와 파일·표 번호를 함께.
const fs = require('fs');
const path = require('path');
const { Document, Packer } = require('docx');
const S = require('./styles');
const { cover, toc } = require('./cover');
const { H, B, SOURCE, tableCaption, figureCaption, table, figure, figurePlaceholder } = S;

const ASSET = (f) => fs.readFileSync(path.join(__dirname, 'assets', f));
const FIG = (f) => path.join(__dirname, '..', '..', 'notebook', 'figures', f); // 노트북이 저장한 그림

// 표 = 캡션 + 표 + 출처 줄
const srcTable = (caption, headers, rows, widths, source, opts) => [
  tableCaption(caption),
  table(headers, rows, widths, opts),
  SOURCE(source || '출처: [팀 입력]'),
];
// 그림 = 그림(파일이 없으면 자리 표시) + 캡션 + 출처 줄
const srcFigure = (file, caption, source, widthMm = 150) => [
  fs.existsSync(FIG(file)) ? figure(fs.readFileSync(FIG(file)), widthMm) : figurePlaceholder(`${caption} (figures/${file} 생성 전)`),
  figureCaption(caption),
  SOURCE(source || '출처: [팀 입력]'),
];

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
    ['자료 저장소', 'github.com/202103116-stack/university-dropout-risk-analysis'],
    ['Colab 노트북', 'https://colab.research.google.com/drive/1JCE1qZSWkixXybo86cDwFJpl4_n-Tbmc?usp=sharing'],
  ],
  date: '2026. 11. 12.',
  team: '14조',
  mark: ASSET('hufs_watermark.png'),
};

const body = [
  // ── Ⅰ. 문제 정의 (15점) ─────────────────────────
  H(1, '문제 정의'),
  H(2, '의사결정과 질문'),
  B('TODO: 누가(한국외대 학사종합지원센터, 보조 입학처) / 무엇을 / 질문 ①② — 00_문제정의_가설.md 1절'),
  H(2, '가설과 판정 규칙(결과 확인 전 고정)'),
  B('TODO: 가설 A·B 판정 규칙, 예측 절, 고정 일시와 태그(hypotheses-locked, hypotheses-locked-v2), v1→v2 변경 이력'),
  H(2, '반대 결과 처리'),
  B('TODO: 기각 시 행동(A: 해당 기준 미사용 / B: 모집(입학처)으로 재정의)'),

  // ── Ⅱ. 수집 (수집·정제 20점) ────────────────────
  H(1, '수집'),
  H(2, '수집 기록과 이용 조건'),
  B('TODO: docs/수집_기록표.md (출처, URL, 수집일, 공공누리 제1유형)'),
  H(2, '분석 범위와 측정 척도'),
  ...srcTable('(표 1) 분석 범위 적용 전후 행 수', ['단계', '행 수'], [['원본', 'TODO'], ['일반 대학 주간', 'TODO']], [60, 40], ''),

  // ── Ⅲ. 정제 (수집·정제 20점) ────────────────────
  H(1, '정제'),
  H(2, '품질 6대 기준 진단'),
  B('TODO: docs/data_description.md 3절, 3-2 표준분류 일관성'),
  H(2, '정제 로그와 단계별 추적'),
  ...srcTable('(표 2) 정제 처리 로그 (처리, 건수, 근거, 영향)', ['처리', '건수', '근거', '영향'], [['TODO', '', '', '']], [30, 15, 30, 25], ''),
  H(2, '손대지 않은 것'),
  B('TODO: logs/정제로그.md 표 8'),

  // ── Ⅳ. 분석 (25점) ──────────────────────────────
  H(1, '분석'),
  H(2, 'EDA와 기술통계'),
  H(2, '분석 표본과 설계(시간 분리, 누수 방지)'),
  H(2, '가설 A: 전국 구조'),
  ...srcTable('(표 3) 가설 A 오즈비와 95% 신뢰구간', ['변수', '오즈비', '95% CI'], [['TODO', '', '']], [40, 30, 30], ''),
  H(2, '예측 절: 모델 vs 기준선'),
  ...srcTable('(표 4) 같은 k에서의 정밀도: 모델 2개와 기준선 2개', ['방법', '정밀도', '재현율', 'AUC'], [['TODO', '', '', '']], [40, 20, 20, 20], ''),
  H(2, '가설 B: 한국외대'),
  H(2, '민감도'),

  // ── Ⅴ. 시각화·해석·한계 (시각화 15점, 해석·한계 15점) ──
  H(1, '시각화, 해석, 한계'),
  H(2, '필수 차트 3종'),
  ...srcFigure('fig1_scatter.png', '(그림 1) 탈락 인원(명) × 탈락률(%) 교차 산점도', ''),
  ...srcFigure('fig2_hufs_groups.png', '(그림 2) 한국외대 학과군별 탈락률 비교 (가설 B)', ''),
  ...srcFigure('fig3_model_vs_baseline.png', '(그림 3) 모델 vs 기준선 정밀도 (같은 k)', ''),
  H(2, '가설 판정과 권고'),
  B('TODO: 가설 A·B별 맞았다/부분 맞았다/틀렸다, 근거 수치(출처), 권고'),
  H(2, '한계와 믿기 어려운 이유'),
  B('테스트는 공시 2026 한 해뿐'),
  B('학과 단위 집계라 개인 이탈 요인을 담지 못하고, 결과는 상관이지 인과가 아님'),
  B('폐지, 통폐합, 신설 학과가 연결에서 빠지는 생존 편향과 공시 정의, 결측 패턴 변화'),
  B('표준분류는 학교별 신고에 의존해 같은 이름의 학과가 학교마다 다르게 분류될 수 있다. 우리는 학과를 재분류하지 않고 데이터가 준 분류를 그대로 쓴다.'),
  B('TODO: 말할 수 없는 것, 믿기 어려운 이유'),

  // ── 부록 ────────────────────────────────────────
  H(1, '부록'),
  H(2, '부록 A. 재현성 확인'),
  B('TODO: logs/재현성_확인표.md'),
  H(2, '부록 B. 기여도표'),
  B('TODO: logs/기여도표.md (단계별 담당자, 검토자)'),
  H(2, '부록 C. AI 활용 로그'),
  B('TODO: logs/AI활용기록.md 1~2쪽 요약 (내가 지시한 것 / AI가 제안한 것 / 채택, 수정, 기각한 것)'),
  H(2, '부록 D. 정제 로그 전체'),
  B('TODO: logs/정제로그.md 표 1~8'),
  H(2, '부록 E. 보조 분석 R1: 인원과 비율 순위'),
  B('TODO: 한국외대 탈락 비율 상위 10 vs 인원 상위 10 교집합 (00_문제정의_가설.md 10절, 가설 판정 아님)'),
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
