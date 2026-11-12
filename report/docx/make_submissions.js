// 제출 문서 생성: 정제 로그 / AI 활용 로그(1~2쪽 요약) / 기여도표 + 합본
// 실행: node make_submissions.js  →  ../../submission/*.docx
// 이어서: powershell -ExecutionPolicy Bypass -File finalize.ps1 <docx 절대경로> <pdf 절대경로>  (필드·글꼴 포함·PDF)
// 양식: 주제계획서와 같은 표지(cover.js)와 본문 스타일(styles.js). 제목 자동 번호는 쓰지 않는다(정제로그 '표 n' 번호를 출처로 쓰기 때문).
// 내용 원본: logs/정제로그.md, logs/기여도표.md (그대로 변환), AI 활용 로그는 logs/AI활용기록.md를 1~2쪽으로 요약한 아래 AI_ROWS.
const fs = require('fs');
const path = require('path');
const { Document, Packer, ExternalHyperlink, TextRun, ImageRun, Paragraph, PageBreak, AlignmentType, ShadingType } = require('docx');
const S = require('./styles');
const { cover, toc } = require('./cover');

const ROOT = path.resolve(__dirname, '..', '..');
const OUT = path.join(ROOT, 'submission');
fs.mkdirSync(OUT, { recursive: true });

const COLAB = 'https://colab.research.google.com/drive/1JCE1qZSWkixXybo86cDwFJpl4_n-Tbmc?usp=sharing';
const REPO = 'https://github.com/202103116-stack/university-dropout-risk-analysis';
const ASSET = (f) => fs.readFileSync(path.join(__dirname, 'assets', f));
const icon = (f, mm = 4.2) => new ImageRun({ type: 'png', data: ASSET(f), transformation: { width: Math.round(mm * 3.78), height: Math.round(mm * 3.78) } });
const link = (text, url, size = 20) => new ExternalHyperlink({ link: url, children: [new TextRun({ text, font: S.font(S.SANS), size, color: '0563C1', underline: {} })] });
const iconFor = (url) => (url.includes('colab.research') ? 'colab.png' : url.includes('github.com') ? 'github.png' : null);
const iconLink = (text, url, size) => {
  const f = iconFor(url);
  return f ? [icon(f), new TextRun({ text: ' ' }), link(text, url, size)] : [link(text, url, size)];
};
const repoFile = (rel) => encodeURI(`${REPO}/blob/main/${rel}`);

// **굵게**·`코드`·[글](주소) 를 런으로
function runsX(text, opts = {}) {
  const out = [];
  String(text).split(/(\[[^\]]+\]\([^)]+\))/g).filter(Boolean).forEach((part) => {
    const m = part.match(/^\[([^\]]+)\]\(([^)]+)\)$/);
    if (m) out.push(...iconLink(m[1], m[2], opts.size));
    else out.push(...S.runs(part, opts));
  });
  return out;
}
const Para = (text, o = {}) => new Paragraph({ children: runsX(text), ...o });
const Bul = (text, level = 0) => new Paragraph({ numbering: { reference: 'bullet', level }, children: runsX(text), alignment: AlignmentType.LEFT });
const Note = (text) => new Paragraph({ style: 'Note', children: runsX(text) });

// 표 칸 폭: 글자 수에 비례(최소·최대 제한)
function widthsFor(rows, total = S.CONTENT_WIDTH) {
  const n = rows[0].length;
  const w = Array.from({ length: n }, (_, i) => Math.min(Math.max(...rows.map((r) => String(r[i] || '').replace(/\*\*|`/g, '').length)), 46) + 5);
  const sum = w.reduce((a, b) => a + b, 0);
  const out = w.map((x) => Math.round((x / sum) * total));
  out[n - 1] += total - out.reduce((a, b) => a + b, 0);
  return out;
}
function mdTable(lines) {
  const rows = lines.map((l) => l.trim().replace(/^\||\|$/g, '').split('|').map((c) => c.trim()));
  const head = rows[0];
  const body = rows.slice(2);
  const size = head.length >= 7 ? 15 : head.length >= 5 ? 17 : 19;
  const cell = (c) => c.split(/<br\s*\/?>/).map((ln) => runsX(ln, { size }));
  return S.table(head.map(cell), body.map((r) => r.map(cell)), widthsFor([head, ...body]), { size });
}

// 마크다운 → 문단 배열. shift: '##' 을 몇 수준 제목으로 둘지(단독 문서 1, 합본 2)
function md2docx(file, shift = 1) {
  const lines = fs.readFileSync(path.join(ROOT, file), 'utf-8').replace(/\r/g, '').split('\n');
  const out = [];
  let i = 0;
  while (i < lines.length) {
    const l = lines[i];
    if (/^# /.test(l) || /^---\s*$/.test(l) || !l.trim()) { i += 1; continue; }
    const h = l.match(/^(#{2,4}) (.*)/);
    if (h) { out.push(S.H(Math.min(h[1].length - 2 + shift, 4), h[2].replace(/`/g, ''))); i += 1; continue; }
    if (l.trim().startsWith('|')) {
      const block = [];
      while (i < lines.length && lines[i].trim().startsWith('|')) block.push(lines[i++]);
      out.push(mdTable(block), S.GAP());
      continue;
    }
    if (l.startsWith('```')) {
      i += 1;
      while (i < lines.length && !lines[i].startsWith('```')) {
        out.push(new Paragraph({ style: 'TableText', shading: { type: ShadingType.CLEAR, color: 'auto', fill: 'F2F2F2' }, children: [new TextRun({ text: lines[i], font: { ascii: 'Consolas', hAnsi: 'Consolas', eastAsia: S.SANS, cs: 'Consolas' }, size: 19 })] }));
        i += 1;
      }
      i += 1; continue;
    }
    if (l.startsWith('>')) {
      while (i < lines.length && lines[i].startsWith('>')) {
        const t = lines[i].replace(/^>\s?/, '').replace(/^- /, '').trim();
        if (t) out.push(Note(t));
        i += 1;
      }
      continue;
    }
    const b = l.match(/^(\s*)[-*] (.*)/);
    if (b) { out.push(Bul(b[2], Math.min(Math.floor(b[1].length / 2), 3))); i += 1; continue; }
    const n = l.match(/^(\s*)\d+\. (.*)/);
    if (n) { out.push(Bul(n[2], Math.min(Math.floor(n[1].length / 2), 3))); i += 1; continue; }
    out.push(Para(l.trim()));
    i += 1;
  }
  return out;
}

// ── AI 활용 로그 (제출용 1~2쪽 요약; 원본 전체는 저장소 logs/AI활용기록.md) ──
const AI_ROWS = [
  ['11/08', '① 문제 정의', '공개 데이터로 답할 의사결정 질문을 누가·무엇을·질문 형식으로 강화', '의사결정자, 분류 설계, 가설 초안·판정 규칙', '수정: 수치 기준을 팀 기준으로 명시하고 민감도로 보완'],
  ['11/08', '② 수집', '행·열, 중복, 결측, 정합성, 연결 가능성을 pandas로 세기', '사전 점검 수치(56,340×32, 결측 6,372 등)', '채택: 노트북 재실행으로 같은 값 확인(s2-02~s3-06)'],
  ['11/08', '① 문제 정의', '안내문 분량 요구 확인', 'AI가 "제안서 1쪽 요구"라고 진술', '**수정**: 원문 확인 결과 분량 제한 없음 → AI 진술 정정'],
  ['11/11', '② 수집', '일반 대학만 쓸지, 학교 유형이 섞인 구조 보여 주기', '학교종류·주야간·학과특성 분포, 일반 대학 주간 범위', '채택: 범위 50,081행(88.9%), 전체 표본은 민감도로'],
  ['11/11', '③ 정제', '표준분류가 학과명 단위로 일관된지 재기', '중계열 27%·소계열 46% 갈림, N.C.E. 9.4%', '채택: 수작업 매핑 없이 데이터 컬럼만 사용'],
  ['11/11', '① 문제 정의', 'B 대상군 정의(국제지역학 포함 여부)', '처음엔 국제지역학 포함 제안', '**수정**: AI가 측정 해석을 잘못 말했다가 재측정 → 국제지역학은 민감도로'],
  ['11/11', '① 문제 정의', '의사결정자에 맞춘 가설 v2 설계', '가설 A·B, 예측 절, R1·R2 후보', '**수정**: AI가 전국 비교 방향을 근거 없이 가정 → 사용자 지적으로 판정에서 제외. 태그로 결과 전 고정'],
  ['11/11', '① 문제 정의', 'k와 오차 비용을 청중이 이해할 만큼 단순하게', 'k = 작년 고위험 학과 수, 정밀도·재현율 2개', '채택: 태그 hypotheses-locked-v3'],
  ['11/11', '③ 정제', '공시 비율 vs 계÷재적 차이가 큰지', '최대 0.005%p(반올림 수준)', '채택: 공시값 사용. AI가 인용한 "68행"은 재현 안 됨 → [확인 필요]로 기록'],
  ['11/11', '③ 정제', '노트북 ③을 실제 코드로, 기대값 assert', '정제 코드·로그·추적표', '채택: assert 전부 통과. 새 함정(재적 0인데 비율 0% 1,697행) 발견'],
  ['11/11', '④ 분석', '가설 A·B, 예측 절, 민감도, R1 구현', 'A 맞음, B 기각, +1.7%p, 교집합 0', '채택: 누수 assert, 시드 4개 재현, 의학계열 완전 분리 진단. 사전 문서에 없던 세부 7개는 공개 후 팀 검토'],
  ['11/11', '⑤ 발표', '가능한 차트를 다 그리고 베스트 3종 선택', '후보 14개, 5개 기준 점수표', '채택: 그림을 직접 보고 눈금·라벨 겹침 4건 수정'],
  ['11/12', '⑤ 발표', '졸업논문 수업 PPT 양식으로 발표 자료 제작', '슬라이드 생성 코드, 슬라이드용 그림', '[팀 입력]: 팀원 검토 후 채택 여부 기록'],
  ['11/12', '④ 분석', '재적 1명·탈락 1명 같은 순위를 근거와 함께 해석 보정', '개편 전 잔류·신설 초기 추정, R1 보정판(교집합 0→1)', '채택: 원판정은 유지하고 보정판을 나란히 공개'],
  ['11/12', '④ 분석', '1학년 단위 탈락이 소속 이동 때문인지, 비율 비교가 공정한지', '소속 이동 아님 근거 3개, 1학년 탈락률 범위 비교', '채택: 문구를 "1학년 초기 이탈이 모여 보인다"로 수정'],
  ['11/12', '⑤ 발표', '분량 안에서 이해하기 쉬운 발표 대본', '대본(노트와 같은 원본), 예상 질문 14개', '[팀 입력]: 리허설 후 시간 확인'],
  ['11/12', '④ 분석', '가설 B 반대 결과를 설명하는 문장', '대안 설명 3개, ①을 가장 강한 설명으로 제시', '**수정**: 연도별 확인 결과 ①은 2026 공시부터라 부분 설명 → 확인/추정 구분'],
];
const aiDoc = (lvl = 1) => [
  S.H(lvl, 'AI 활용 원칙'),
  Bul('**허용**: 정제·집계 코드 생성, 에러 해석, 개념 설명, 문장 다듬기'),
  Bul('**기록 필수**: 무엇을 물었는가, 무엇을 받았는가, 어떻게 검증했는가, 채택/수정/기각'),
  Bul('**금지**: 검증 없는 채택, 실행하지 않은 수치 기재, AI가 만들거나 조작한 데이터 사용'),
  Bul('**검증 방법**: 모든 수치는 노트북 셀 출력과 대조(셀 ID 표기), 가설·판정 규칙은 결과 전에 git 태그로 고정'),
  S.H(lvl, '단계별 기록 (내가 지시한 것 / AI가 제안한 것 / 채택·수정·기각한 것)'),
  S.table(['날짜', '단계', '내가 지시한 것', 'AI가 제안한 것', '채택·수정·기각과 검증'],
    AI_ROWS.map((r) => r.map((c) => [runsX(c, { size: 16 })])), [700, 1000, 2650, 2350, 2938], { size: 16 }),
  S.GAP(),
  S.H(lvl, 'AI 진술을 바로잡은 사례'),
  Bul('안내문 분량: AI가 "1쪽 요구"라고 했으나 원문에는 분량 제한이 없었음(원문 직접 확인)'),
  Bul('국제지역학 분류: AI가 측정 해석을 잘못 말했다가 재측정으로 정정, 주 분석에서 제외'),
  Bul('전국 비교 방향: AI가 근거 없이 방향을 가정 → 판정에서 빼고 결과 문구만 미리 고정'),
  Bul('계획서 기준값 2개(재계산 불일치 68행, 국제지역학 28/22)는 노트북에서 재현되지 않아 [확인 필요]로 공개'),
  Bul('반대 결과 설명: AI가 "이탈이 앞 단계로 옮겨 갔다"를 가장 강한 설명이라 했으나, 그 단위는 2026 공시부터라 부분 설명임을 연도별 재계산으로 확인해 정정'),
  Note(`전체 원본 기록: [logs/AI활용기록.md](${repoFile('logs/AI활용기록.md')})  ·  사용 프롬프트: [docs/프롬프트_모음.md](${repoFile('docs/프롬프트_모음.md')})`),
];

// ── 표지 ──
const COVER = (kicker, title, subtitle) => ({
  kicker, title, subtitle,
  info: [
    ['과 목', '빅데이터분석 (AI 기반 비즈니스 데이터 분석)'],
    ['담당교수', '박주원'],
    ['조', '14조'],
    ['팀 원', '정승엽, 박유진, 신효주'],
    ['자료 저장소', iconLink('github.com/202103116-stack/university-dropout-risk-analysis', REPO)],
    ['Colab 노트북', iconLink('Colab(팀 정본)', COLAB)],
  ],
  date: '2026. 11. 12.',
  team: '14조',
  mark: ASSET('hufs_watermark.png'),
});
const MAIN = '다음 학년도 중도탈락 고위험 학과는 어디인가';

const DOCS = [
  { file: '14조_정제로그', title: '정제 로그', sub: '처리 · 건수 · 근거 · 영향 (노트북 §③ 정제 출력 기준)', body: (l) => md2docx('logs/정제로그.md', l) },
  { file: '14조_AI활용로그', title: 'AI 활용 로그', sub: '내가 지시한 것 / AI가 제안한 것 / 채택 · 수정 · 기각한 것', body: (l) => aiDoc(l) },
  { file: '14조_기여도표', title: '기여도표', sub: '안내문 5단계별 담당자 · 검토자', body: (l) => md2docx('logs/기여도표.md', l) },
];

const build = (name, front, body) => {
  const doc = new Document({
    creator: '14조', title: name, styles: S.styles, numbering: S.numbering, features: { updateFields: true },
    sections: [S.frontSection(front), S.bodySection(body)],
  });
  return Packer.toBuffer(doc).then((buf) => { const f = path.join(OUT, `${name}.docx`); fs.writeFileSync(f, buf); console.log('written', f); });
};

(async () => {
  for (const d of DOCS) {
    const c = cover(COVER('빅데이터분석 팀 프로젝트2 제출물', d.title, `${MAIN}  |  ${d.sub}`));
    await build(d.file, c, d.body(1));
  }
  // 합본: 표지 + 목차 + 문서 3개(각각 제목 1)
  const parts = [];
  DOCS.forEach((d, i) => {
    if (i) parts.push(new Paragraph({ children: [new PageBreak()] }));
    parts.push(S.H(1, d.title));
    parts.push(...d.body(2));
  });
  await build('14조_제출물_합본', [...cover(COVER('빅데이터분석 팀 프로젝트2 제출물 합본', '제출물 합본', `${MAIN}  |  정제 로그 · AI 활용 로그 · 기여도표`)), ...toc()], parts);
})();
