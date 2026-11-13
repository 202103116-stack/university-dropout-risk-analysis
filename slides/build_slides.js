/**
 * 팀 프로젝트2 발표 자료 — 다음 학년도 중도탈락 고위험 학과는 어디인가
 * 실행: node slides/build_slides.js && python -X utf8 slides/embed_fonts.py
 * 산출: slides/14조_발표.pptx (PDF는 PowerPoint로 내보냄: slides/export_pdf.ps1)
 * 양식: 졸업논문 수업 중간발표(Depression_ActivityNetwork_Capstone/presentation/build_midterm.js)와 같은
 *       팀 Canva 틀(20×11.25in, 위, 아래 브랜드 띠, 진행 탭, ✓ 장 제목, 핵심 문장, 카드, 읽는 법 막대, PAGE 탭, 같은 글꼴).
 * 구성: slides/발표_구성.md (3막: 봤다 3분 / 했다 4분 / 그래서 3분, 본문 10장 + 부록)
 * 수치: data/processed/slides_data.json (노트북 부록 F 셀 sZ-01) — 손으로 옮긴 수치 없음. 슬라이드마다 아래쪽에 출처 줄.
 */
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");

const ROOT = path.resolve(__dirname, "..");
const D = JSON.parse(fs.readFileSync(path.join(ROOT, "data", "processed", "slides_data.json"), "utf-8"));
const OUT = path.join(__dirname, "14조_발표.pptx");
const SCRIPT = require("./script")(D);
const P = (...a) => path.join(__dirname, ...a);

// ---------------------------------------------------------------- 브랜드 토큰 (팀 Canva 틀과 같음)
const F = { disp: "강한놈소프트보일드", body: "210 디딤고딕", bodyB: "210 디딤고딕 Bold", small: "JASO Sans", page: "Poppins Medium", num: "Nanum Square Ultra-Bold" };
const C = {
  brand: "3A59D1", light: "5271FF", a: "0025CC", b: "00BF63", ink: "222222", muted: "222222", rule: "C9CED6",
  bg: "F5F5F5", white: "FFFFFF", tint: "EEF1FC", tintG: "E6F8EF", risk: "E8603C", tintR: "FDECE6", badge: "1D2430", soft: "A9B2C0",
};
const pres = new pptxgen();
pres.defineLayout({ name: "CANVA", width: 20, height: 11.25 });
pres.layout = "CANVA";
pres.theme = { headFontFace: F.disp, bodyFontFace: F.body };
pres.title = "다음 학년도 중도탈락 고위험 학과는 어디인가 — 빅데이터분석 14조";
pres.author = "빅데이터분석 14조";
const MX = 0.8, R = 19.2, CW = R - MX;

const f1 = (x) => Number(x).toFixed(1);
const f2 = (x) => Number(x).toFixed(2);
const n0 = (x) => Math.round(Number(x)).toLocaleString("en-US");
const sgn = (x, k = 1) => `${x > 0 ? "+" : "−"}${Math.abs(x).toFixed(k)}`;
const SRC = "출처: 교육부 대학알리미 중도탈락 학생 현황(공공데이터포털 15164570, 공공누리 제1유형)";

// ---------------------------------------------------------------- 틀
pres.defineSlideMaster({
  title: "BRAND", background: { color: C.bg },
  objects: [
    { rect: { x: 0, y: 0, w: 20, h: 0.1, fill: { color: C.brand }, line: { color: C.brand } } },
    { rect: { x: 0, y: 11.15, w: 20, h: 0.1, fill: { color: C.brand }, line: { color: C.brand } } },
  ],
});
let PAGE = 0;
// 위쪽 진행 탭: 3막(안내문 기준) + 부록. 지금 막만 강조
const TABS = [["봤다", "봤다  질문, 데이터, 함정  (3분)"], ["했다", "했다  정제, 분석, 검증  (4분)"], ["그래서", "그래서  권고, 근거, 한계  (3분)"], ["부록", "부록"]];
const tabs = (s, act) => {
  const widths = [5.6, 5.6, 5.6, CW - 16.8 - 0.3];
  let x = MX;
  TABS.forEach(([a, label], i) => {
    const on = a === act;
    s.addText(label, { isTextBox: true, shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: 0.08, x, y: 0.2, w: widths[i], h: 0.36, align: "center", valign: "middle", margin: 0,
      fontFace: on ? F.bodyB : F.body, bold: on, fontSize: 12.5, color: on ? C.white : C.ink, fill: { color: on ? C.brand : "E6E9F0" }, line: { color: on ? C.brand : "E6E9F0" } });
    x += widths[i] + 0.1;
  });
};
const slide = (act, notes) => {
  const s = pres.addSlide({ masterName: "BRAND", sectionTitle: act });
  PAGE += 1;
  if (act !== "표지") tabs(s, act);
  s.addShape(pres.shapes.RIGHT_TRIANGLE, { x: 17.75, y: 10.45, w: 0.7, h: 0.72, flipH: true, fill: { color: C.brand }, line: { color: C.brand } });
  s.addText(`PAGE ${String(PAGE).padStart(2, "0")}`, { isTextBox: true, shape: pres.shapes.RECTANGLE, x: 18.43, y: 10.45, w: 1.57, h: 0.72, fill: { color: C.brand }, line: { color: C.brand },
    fontFace: F.page, fontSize: 15, color: C.white, align: "center", valign: "middle", margin: 0 });
  // 발표자 노트: 본문은 slides/script.js(발표대본.md와 같은 원본), 부록은 각 장의 notes
  const sc = SCRIPT.find((x) => x.page === PAGE);
  if (sc) s.addNotes(`[${sc.act}, 목표 ${sc.time}] ${sc.text}\n\n💡 ${sc.tip}`);
  else if (notes) s.addNotes(notes);
  return s;
};
const T = (s, t, o = {}) => s.addText(t, { isTextBox: true, margin: 0, fontFace: F.body, fontSize: 16, color: C.ink, valign: "top", ...o });
const B = (t, o = {}) => ({ text: t, options: { fontFace: F.bodyB, bold: true, ...o } });
const N = (t, o = {}) => ({ text: t, options: { ...o } });
const box = (s, x, y, w, h, o = {}) => s.addShape(o.rect ? pres.shapes.RECTANGLE : pres.shapes.ROUNDED_RECTANGLE, {
  x, y, w, h, rectRadius: o.rect ? undefined : (o.r ?? 0.12), fill: { color: o.fill || C.white }, line: { color: o.line || o.fill || C.white, width: o.lw ?? 1.5, dashType: o.dash || "solid" } });
const card = (s, x, y, w, h, col = C.light, fill = C.white) => box(s, x, y, w, h, { fill, line: col, lw: 1.5 });
const line = (s, x1, y1, x2, y2, o = {}) => s.addShape(pres.shapes.LINE, {
  x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1) || 0.001, h: Math.abs(y2 - y1) || 0.001,
  flipV: (y2 < y1) !== (x2 < x1), line: { color: o.color || C.rule, width: o.w || 1, endArrowType: o.arrow, dashType: o.dash || "solid" } });
const arrow = (s, x1, y1, x2, y2, col = C.brand) => line(s, x1, y1, x2, y2, { color: col, w: 2.25, arrow: "triangle" });
const pill = (s, text, x, y, o = {}) => s.addText(text, { isTextBox: true, shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: 0.2,
  x, y, w: o.w || Math.max(1, text.length * 0.2 + 0.5), h: o.h || 0.42, align: "center", valign: "middle", margin: 0,
  fontFace: F.bodyB, bold: true, fontSize: o.size || 14, color: o.color || C.white, fill: { color: o.fill || C.brand }, line: { color: o.line || o.fill || C.brand, width: 1.25 } });
const num = (s, n, x, y, d = 0.5, fill = C.brand) => s.addText(String(n), { isTextBox: true, shape: pres.shapes.OVAL, x, y, w: d, h: d,
  align: "center", valign: "middle", margin: 0, fontFace: F.num, fontSize: d > 0.45 ? 18 : 14, color: C.white, fill: { color: fill }, line: { color: fill } });
const sub = (s, t, x, y, w, col = C.light, size = 24) => T(s, t, { x, y, w, h: 0.5, fontFace: F.disp, fontSize: size, color: col, valign: "middle" });
const readBar = (s, label, text, y = 9.75, x = MX, w = CW) => {
  box(s, x, y, w, 0.55, { fill: C.tint, line: C.tint });
  T(s, [B(`${label}   `, { color: C.brand }), N(text, { color: C.ink })], { x: x + 0.25, y, w: w - 0.5, h: 0.55, fontSize: 14, valign: "middle" });
};
const foot = (s, t, y = 10.62) => T(s, t, { x: MX, y, w: 16.6, h: 0.34, fontFace: F.small, fontSize: 11.5, color: C.muted, valign: "middle" });
const HYP = { A: ["가설 A  전국 구조", C.a], B: ["가설 B  한국외대", C.b], P: ["예측 절  모델 vs 기준선", C.brand] };
const title = (s, t, o = {}) => {
  s.addImage({ path: P("assets", "check.png"), x: MX, y: 1.0, w: 0.42, h: 0.32, altText: "체크 표시" });
  T(s, t, { x: 1.4, y: 0.68, w: o.w || 12, h: 0.95, fontFace: F.disp, fontSize: 40, valign: "middle" });
  if (o.hyp) {
    const [t2, col] = HYP[o.hyp];
    pill(s, t2, R - 3.6, 0.93, { w: 3.6, h: 0.45, fill: C.white, line: col, color: col, size: 14 });
  }
  if (o.verdict) {
    const [v, col] = o.verdict;
    pill(s, v, R - 3.6 - 2.1, 0.93, { w: 1.9, h: 0.45, fill: col, line: col, color: C.white, size: 15 });
  }
  line(s, MX, 1.7, R, 1.7, { color: C.rule, w: 1 });
};
// 핵심 문장 = 그 장의 '그래서 무엇' 한 줄
const headline = (s, t, y = 1.8, x = MX, w = CW, size = 24) => T(s, t, { x, y: y + 0.05, w, h: 0.6, fontFace: F.bodyB, bold: true, fontSize: size, valign: "middle" });
const pngSize = (file) => { const b = fs.readFileSync(file); return [b.readUInt32BE(16), b.readUInt32BE(20)]; };
const fig = (s, file, x, y, maxW, maxH, alt, align = "left") => {
  const [pw, ph] = pngSize(file), r = pw / ph;
  let w = maxW, h = w / r;
  if (h > maxH) { h = maxH; w = h * r; }
  const xx = align === "center" ? x + (maxW - w) / 2 : align === "right" ? x + maxW - w : x;
  box(s, xx - 0.12, y - 0.12, w + 0.24, h + 0.24, { fill: C.white, line: C.white, r: 0.08 });
  s.addImage({ path: file, x: xx, y, w, h, altText: alt });
  return { x: xx, y, w, h };
};
const TBL = { fontFace: F.body, fontSize: 13, color: C.ink, valign: "middle", border: { type: "solid", pt: 0.75, color: C.rule }, margin: [3, 6, 3, 6] };
const HD = (t, fill = C.brand, color = C.white, al = "center") => ({ text: t, options: { fontFace: F.bodyB, bold: true, fill: { color: fill }, color, align: al } });
const CELL = (t, o = {}) => ({ text: t, options: { fill: { color: o.fill || C.white }, fontFace: o.b ? F.bodyB : F.body, bold: !!o.b, color: o.color || C.ink, align: o.al || "left" } });
const bigNum = (s, value, label, x, y, w, col = C.brand, size = 44) => {
  T(s, value, { x, y, w, h: 0.85, fontFace: F.bodyB, bold: true, fontSize: size, color: col, valign: "middle" });
  T(s, label, { x, y: y + 0.85, w, h: 0.5, fontSize: 14.5, color: C.muted });
};

// ---------------------------------------------------------------- 자주 쓰는 수치
const E = Object.fromEntries(D.eval.map((r) => [r["방법"].slice(0, 4), r]));
const m1 = D.eval[0], m2 = D.eval[1], b2 = D.eval[2];
const gapP = m2["정밀도(%)"] - b2["정밀도(%)"];
const A = D.tabA, Bv = D.resB, G = D.groups_ci;
const Q1 = A["C(size_q, Treatment('Q4'))[T.Q1]"];
const four = (a, b) => D.four[`${a}|${b}`];
const sensRange = D.sens.map((r) => r["모델2 정밀도"] - r["기준선② 정밀도"]);
const hE = D.hufs_eval;

// ================================================================ 표지
pres.addSection({ title: "표지" });
{
  const s = slide("표지", "안녕하십니까, 빅데이터분석 14조입니다. 저희는 한국외대 학사종합지원센터가 내년 학업지속 지원을 어느 학과에 먼저 배치해야 하는지를, 대학알리미의 학과별 중도탈락 공시 4개년 자료로 분석하고 예측했습니다.");
  T(s, "다음 학년도 중도탈락 고위험 학과는 어디인가", { x: 0.7, y: 1.3, w: 18.6, h: 1.25, fontFace: F.disp, fontSize: 60, valign: "middle" });
  T(s, "학업지속 지원 대상 학과 선정을 위한 학과별 중도탈락 패널 분석, 예측", { x: 0.7, y: 2.65, w: 18.6, h: 1.0, fontFace: F.disp, fontSize: 38, color: C.brand, valign: "middle" });
  [["가설 A", "전국 구조", "사립, 비수도권 학과는 고위험이 많은가", C.a], ["가설 B", "한국외대", "비주류 외국어 학과군이 우선 지원 대상인가", C.b]].forEach(([a, b, c, col], i) => {
    const x = 0.9 + i * 6.3;
    card(s, x, 4.45, 5.7, 1.6, col);
    T(s, [B(`${a}  `, { color: col, fontSize: 21 }), B(b, { fontSize: 21 })], { x: x + 0.3, y: 4.62, w: 5.2, h: 0.5 });
    T(s, c, { x: x + 0.3, y: 5.22, w: 5.2, h: 0.6, fontSize: 15.5, color: C.muted });
  });
  arrow(s, 6.65, 5.25, 7.15, 5.25);
  // 오른쪽: 자료 규모 카드(사진 대신 이 연구의 자료를 보여 준다)
  card(s, 13.6, 4.45, 5.6, 4.15, C.light);
  T(s, "분석 자료", { x: 13.95, y: 4.62, w: 5, h: 0.45, fontFace: F.disp, fontSize: 21, color: C.light, valign: "middle" });
  [[`${n0(D.n_raw)}행`, "대학알리미 학과별 공시 2023~2026"], [`${D.n_school_scope}개교`, `일반 대학 주간 학과 ${n0(D.n_scope)}행`], [`${n0(D.n_sample)}쌍`, "전년 → 당해 분석 표본"]].forEach(([v, l], i) => {
    const y = 5.2 + i * 1.1;
    T(s, v, { x: 13.95, y, w: 2.75, h: 0.6, fontFace: F.bodyB, bold: true, fontSize: 28, color: C.brand, valign: "middle" });
    T(s, l, { x: 16.7, y, w: 2.4, h: 0.6, fontSize: 13, color: C.muted, valign: "middle" });
    if (i < 2) line(s, 13.95, y + 0.9, 18.9, y + 0.9, { color: C.rule });
  });
  T(s, "교육부 대학알리미 중도탈락 학생 현황 (공공데이터포털 15164570)", { x: 1.1, y: 7.05, w: 11.5, h: 0.45, fontSize: 18 });
  T(s, "빅데이터분석 14조   정승엽, 박유진, 신효주", { x: 1.1, y: 7.6, w: 11.5, h: 0.55, fontFace: F.bodyB, fontSize: 22 });
}

// ================================================================ 1. 봤다: 의사결정
pres.addSection({ title: "봤다" });
{
  const s = slide("봤다", "먼저 결정입니다. 결정하는 사람은 한국외대 학사종합지원센터이고, 결정하는 것은 내년에 상담, 학습지원, 복학 안내를 어느 학과에 먼저 배치할지입니다. 이를 위해 두 질문을 세웠습니다. 전국적으로 어떤 유형의 학과가 위험한지, 그리고 한국외대 안에서는 어떤 학과군이 위험한지입니다. 한국외대 질문의 답이 '아니다'로 나오면, 문제는 이탈이 아니라 모집일 수 있어 입학처로 넘기는 경로도 미리 정해 두었습니다.");
  title(s, "의사결정과 질문");
  headline(s, "학사종합지원센터는 내년 학업지속 지원을 어느 학과에 먼저 배치해야 하는가");
  const cols = [["누가", "한국외국어대학교 학사종합지원센터", "보조: 입학처"], ["무엇을", "다음 학년도 학업지속 지원의 우선 배치 학과", "상담, 학습지원, 복학 안내"], ["어떻게 판단", "중도탈락 고위험 = 탈락률 상위 25%", `학습기간 75백분위 ${f2(D.cut)}% 이상`]];
  cols.forEach(([h, a, b], i) => {
    const x = MX + i * 6.2;
    card(s, x, 2.7, 5.9, 2.35);
    num(s, i + 1, x + 0.3, 2.9); sub(s, h, x + 0.95, 2.9, 4.6);
    T(s, a, { x: x + 0.3, y: 3.55, w: 5.3, h: 0.9, fontFace: F.bodyB, fontSize: 19 });
    T(s, b, { x: x + 0.3, y: 4.45, w: 5.3, h: 0.45, fontSize: 15, color: C.muted });
  });
  const qs = [["질문 ①  구조", "전국 일반 대학 학과 중 어떤 설립유형, 지역에서 고위험이 많은가", "가설 A", C.a, C.tint], ["질문 ②  우선 지원 대상", "그중 한국외대에서는 어떤 학과군이 고위험인가", "가설 B", C.b, C.tintG]];
  qs.forEach(([h, q, tag, col, tint], i) => {
    const y = 5.4 + i * 1.55;
    box(s, MX, y, 12.3, 1.35, { fill: tint, line: tint, r: 0.08 });
    T(s, h, { x: MX + 0.3, y: y + 0.12, w: 6, h: 0.5, fontFace: F.disp, fontSize: 22, color: col, valign: "middle" });
    T(s, q, { x: MX + 0.3, y: y + 0.65, w: 10.2, h: 0.5, fontFace: F.bodyB, fontSize: 17 });
    pill(s, tag, MX + 10.7, y + 0.15, { w: 1.4, h: 0.42, fill: C.white, line: col, color: col, size: 14 });
  });
  card(s, 13.5, 5.4, 5.7, 2.9, C.risk, C.white);
  T(s, "미리 정한 다른 경로", { x: 13.8, y: 5.55, w: 5.2, h: 0.5, fontFace: F.disp, fontSize: 21, color: C.risk, valign: "middle" });
  T(s, [N("질문 ②의 답이 '아니다'이면", { breakLine: true }), B("이탈이 아니라 모집의 문제", { breakLine: true }), N("→ 입학처로 넘겨 다시 정의한다")], { x: 13.8, y: 6.15, w: 5.2, h: 1.9, fontSize: 17, paraSpaceAfter: 4 });
  readBar(s, "범위", `전국 일반 대학 주간 학과(사이버, 산업, 교육대, 야간, 계약학과 제외). 학습 t = 2024, 2025 공시, 테스트 t = 2026 공시`, 8.75);
  foot(s, `${SRC}, 판정 규칙: 00_문제정의_가설.md`);
}

// ================================================================ 2. 봤다: 가설
{
  const s = slide("봤다", `가설은 결과를 보기 전에 git 태그로 고정했습니다. 가설 A는 사립이거나 비수도권인 학과가 고위험일 가능성이 높다는 것이고, 대계열과 재적 규모를 통제한 로지스틱 회귀의 오즈비가 둘 다 1보다 크고 구간이 1을 넘으면 맞음입니다. 가설 B는 한국외대의 비주류 외국어 학과군이 교내 다른 학과보다 탈락률이 높다는 것이고, 차이의 95% 구간 하한이 0보다 크면 맞음입니다. 예측은 작년 고위험 학과 수만큼 지원했을 때 몇 곳을 맞히는지로 작년 명단과 비교합니다.`);
  title(s, "가설과 판정 규칙");
  headline(s, "결과를 보기 전에 판정 규칙과 반대 결과의 처리까지 정해 두었다");
  const H2 = [
    ["A", "전국 구조", "사립, 비수도권 학과는 국공립, 수도권 학과보다 고위험 가능성이 높다", ["대계열, 전년도 재적 규모를 통제한 로지스틱 회귀", "두 오즈비 > 1 이고 95% 구간이 1을 넘으면 맞음", "하나만이면 부분 맞음, 둘 다 아니면 기각"], "기각된 기준은 지원 배분 근거로 쓰지 않는다", C.a, C.tint],
    ["B", "한국외대", "비주류 외국어 학과군(기타유럽어, 기타아시아어 소계열)은 교내 다른 학과보다 탈락률이 높다", ["공시 2024~2026 합산 탈락률(탈락 합계 ÷ 재적 합계)", "학과 단위 부트스트랩으로 차이의 95% 구간", "구간 하한 > 0 이면 맞음, 아니면 기각"], "기각이면 '모집(입학처)' 문제로 재정의한다. 분석 전 예상: 한국외대는 이 분야 최상위 학교라 스스로 지망해 온 학생이 많아 탈락률이 높지만은 않을 것", C.b, C.tintG],
  ];
  H2.forEach(([k, n, hyp, rules, rev, col, tint], i) => {
    const x = MX + i * 9.3;
    card(s, x, 2.65, 9.0, 5.9, col);
    T(s, [B(`가설 ${k}  `, { color: col, fontSize: 24 }), B(n, { fontSize: 24 })], { x: x + 0.35, y: 2.85, w: 8.3, h: 0.55, fontFace: F.disp });
    T(s, hyp, { x: x + 0.35, y: 3.5, w: 8.3, h: 0.95, fontFace: F.bodyB, fontSize: 18 });
    T(s, "판정 규칙", { x: x + 0.35, y: 4.55, w: 3, h: 0.4, fontFace: F.bodyB, fontSize: 15, color: col });
    T(s, rules.map((t, j) => ({ text: t, options: { bullet: { indent: 18 }, breakLine: j < rules.length - 1 } })), { x: x + 0.35, y: 4.95, w: 8.3, h: 1.6, fontSize: 15.5, paraSpaceAfter: 4 });
    box(s, x + 0.35, 6.75, 8.3, 1.5, { fill: tint, line: tint, r: 0.08 });
    T(s, [B("반대 결과가 나오면  ", { color: col }), N(rev)], { x: x + 0.6, y: 6.85, w: 7.8, h: 1.3, fontSize: rev.length > 40 ? 14.5 : 16, valign: "middle" });
  });
  readBar(s, "예측 절", `두 가설 안에서 '작년 고위험 학과 수(k)만큼 지원하면 몇 곳을 맞히나'를 작년 명단과 비교한다 — 판정 임계값 없이 그대로 보고`, 8.85);
  foot(s, "고정: git 태그 hypotheses-locked(11/8) → hypotheses-locked-v2, v3(11/11, 결과 확인 전, 노트북 출력 0개 상태에서 커밋)");
}

// ================================================================ 3. 봤다: 데이터, 범위와 함정
{
  const s = slide("봤다", `자료는 교육부 대학알리미의 학과별 중도탈락 공시이고, 4개년 ${n0(D.n_raw)}행입니다. 사이버대, 산업대, 야간 같은 과정은 탈락의 성격이 달라 빼고, 일반 대학 주간 학과 ${n0(D.n_scope)}행, ${D.n_school_scope}개교를 봤습니다. 함정이 많았습니다. 2024년 공시부터 탈락률 결측이 약 15%로 늘었고, 재적이 0인데 탈락률이 0%로 적힌 행이 ${n0(D.n_zero_rate_recorded)}개 있었습니다. 탈락자가 있는데도 0%로 적혀 있어서 비율 칸만 보면 틀립니다. 같은 학과명도 학교마다 계열 분류가 갈렸습니다.`);
  title(s, "데이터와 범위, 함정");
  headline(s, "비율 칸만 믿으면 틀린다 — 분모(재적)와 분류부터 확인해야 하는 데이터");
  // 왼쪽: 자료와 범위
  card(s, MX, 2.65, 6.6, 6.85);
  sub(s, "자료와 범위", MX + 0.3, 2.82, 6);
  T(s, [B("교육부 대학알리미 중도탈락 학생 현황", { breakLine: true }), N("학과별, 공시 2023~2026, 32개 열", { color: C.muted, breakLine: true }), N("공공데이터포털 15164570, 공공누리 제1유형", { color: C.muted })], { x: MX + 0.3, y: 3.45, w: 6, h: 1.2, fontSize: 15.5 });
  bigNum(s, `${n0(D.n_raw)}행`, "원자료 전체 (학과 × 공시연도)", MX + 0.3, 4.75, 6, C.ink, 38);
  arrow(s, MX + 1.0, 6.15, MX + 1.0, 6.55);
  bigNum(s, `${n0(D.n_scope)}행`, `일반 대학 주간 학과, ${D.n_school_scope}개교 (${f1(D.scope_pct)}%)`, MX + 0.3, 6.55, 6, C.brand, 38);
  T(s, "제외: 사이버, 산업, 교육, 방송통신대, 야간, 원격, 계약학과, 산업체위탁, 폐교 → 민감도 분석에만 사용", { x: MX + 0.3, y: 8.15, w: 6, h: 1.1, fontSize: 13.5, color: C.muted });
  // 오른쪽: 함정 4가지
  const traps = [
    ["결측이 해마다 다르다", `탈락률 결측 2023년 ${f1(D.miss_by_year[2023])}% → 2024년 ${f1(D.miss_by_year[2024])}%, 2026년 ${f1(D.miss_by_year[2026])}%`, "보정하지 않고 표본에서 제외"],
    ["재적 0인데 탈락률 0%", `${n0(D.n_zero_rate_recorded)}행 — 탈락자가 있어도 0%로 기록`, "재적 > 0 인 행만 y로 사용"],
    ["탈락률 100% 초과", `${n0(D.n_over100)}행, 그중 ${f1(D.over100_small_pct)}%가 재적 5명 이하`, "값은 그대로, 전년도 재적 30명 이상만 분석"],
    ["분류가 학교마다 갈린다", `5개교 이상 같은 학과명 ${D.g5}개 중 ${D.g5_sub_split}개(${f1(D.g5_sub_split / D.g5 * 100)}%)가 소계열이 다름`, "재분류하지 않고 데이터 분류 그대로 + 한계로 공개"],
  ];
  traps.forEach(([h, v, act], i) => {
    const x = 7.75 + (i % 2) * 5.8, y = 2.65 + Math.floor(i / 2) * 3.48;
    card(s, x, y, 5.6, 3.25, C.risk);
    num(s, i + 1, x + 0.3, y + 0.2, 0.45, C.risk);
    T(s, h, { x: x + 0.9, y: y + 0.18, w: 4.5, h: 0.5, fontFace: F.disp, fontSize: 21, color: C.risk, valign: "middle" });
    T(s, v, { x: x + 0.3, y: y + 0.85, w: 5.0, h: 1.2, fontFace: F.bodyB, fontSize: 16.5 });
    box(s, x + 0.3, y + 2.2, 5.0, 0.8, { fill: C.tint, line: C.tint, r: 0.06 });
    T(s, [B("처리  ", { color: C.brand }), N(act)], { x: x + 0.45, y: y + 2.2, w: 4.75, h: 0.8, fontSize: 14, valign: "middle" });
  });
  foot(s, `${SRC}, 노트북 §③ 셀 s3-01, s3-03, s3-05, s3-16, 정제로그 표 4`);
}

// ================================================================ 4. 했다: 정제 추적
pres.addSection({ title: "했다" });
{
  const s = slide("했다", `정제에서는 행을 하나도 지우지 않았습니다. 문제가 있는 행은 표시만 하고 분석 표본에서 뺐고, 단계마다 남은 수를 기록했습니다. 범위 안 ${n0(D.n_scope)}행을 전년과 당해로 이으면 ${n0(D.n_link)}쌍이고, 두 해 모두 탈락률이 유효하고 전년도 재적이 30명 이상인 ${n0(D.n_sample)}쌍이 최종 표본입니다. 2024, 2025년 공시로 학습하고 2026년 공시로 시험했습니다. 계획서에 적은 사전 점검 값과 같은지 assert로 확인했고 모두 통과했습니다.`);
  title(s, "정제: 행은 지우지 않고 표시만");
  headline(s, `원본 ${n0(D.n_raw)}행에서 ${n0(D.n_sample)}쌍으로 — 단계마다 남은 수와 이유를 기록했다`);
  const steps = [["원본 전체", D.n_raw, "행"], ["범위 안 (일반 대학 주간)", D.n_scope, "행"], ...D.funnel.map((r, i) => [["연결 쌍 (두 해 모두 범위 안)", "+ 당해 탈락률 유효", "+ 전년도 탈락률 유효", "분석 표본 (전년도 재적 ≥ 30명)"][i], r.n, "쌍"])];
  const maxV = D.n_raw, x0 = MX + 4.6, wMax = 7.6;
  steps.forEach(([lab, v, unit], i) => {
    const y = 2.75 + i * 1.08, last = i === steps.length - 1;
    T(s, lab, { x: MX, y, w: 4.45, h: 0.8, fontSize: 15.5, fontFace: last ? F.bodyB : F.body, bold: last, valign: "middle", align: "right" });
    box(s, x0, y + 0.1, Math.max(0.2, (v / maxV) * wMax), 0.6, { fill: last ? C.brand : (i < 2 ? C.soft : "CBD3E6"), r: 0.06 });
    T(s, `${n0(v)}${unit}`, { x: x0 + (v / maxV) * wMax + 0.15, y, w: 2.2, h: 0.8, fontFace: F.bodyB, bold: true, fontSize: 17, color: last ? C.brand : C.ink, valign: "middle" });
  });
  // 오른쪽: 검증 흔적
  card(s, 14.75, 2.65, 4.45, 6.85);
  sub(s, "검증 흔적", 15.05, 2.82, 4);
  [[`${n0(D.n_raw - D.n_raw)}행`, "지운 행 (표시 후 제외)"], ["0건", "y(탈락률)에 한 보정"], [`${n0(D.n_train)} / ${n0(D.n_test)}`, "학습(2024, 25) / 테스트(2026) 쌍"], [`${f2(D.max_gap)}%p`, "공시 비율 vs 계÷재적 최대 차이"]].forEach(([v, l], i) => {
    const y = 3.5 + i * 1.45;
    T(s, v, { x: 15.05, y, w: 4, h: 0.65, fontFace: F.bodyB, bold: true, fontSize: 27, color: C.brand, valign: "middle" });
    T(s, l, { x: 15.05, y: y + 0.62, w: 4, h: 0.45, fontSize: 13.5, color: C.muted });
  });
  readBar(s, "읽는 법", "막대 = 단계별로 남은 수. 연결 이후는 '전년 → 당해' 쌍 단위. 빠진 행의 사유와 건수는 정제로그 표 4, 5에 모두 공개", 9.7);
  foot(s, `${SRC}, 노트북 §③ 셀 s3-16, s3-18, s3-19, s3-20, 정제로그 표 1, 4, 5`);
}

// ================================================================ 5. 했다: 차트 ① 교차 산점도
{
  const tr = D.r1.top_rate, tc = D.r1.top_cnt;
  const RA = D.r1_adj, ta = RA.top_rate;
  const nRes = RA.top_rate_flags.filter((r) => r["해석"].startsWith("개편 전")).length, nNew = RA.top_rate_flags.filter((r) => r["해석"].startsWith("신설")).length;
  const s = slide("했다", `한국외대 학과를 탈락 인원과 탈락률로 함께 찍었습니다. 처음 정한 규칙대로 세면 탈락률 상위 10곳과 탈락 인원 상위 10곳은 한 곳도 겹치지 않았습니다. 그런데 탈락률 상위 10곳 중 ${RA.flag_in_top}곳은 재적이 1명에서 10명 안팎인 단위였습니다. 일본어학전공처럼 재적 1명, 탈락 1명이면 남아 있던 한 명이 떠나 100%가 된 것입니다. 재적이 해마다 줄다가 공시에서 사라지고 탈락 사유가 모두 미복학이라, 학부 개편 전 옛 전공에 남은 학생으로 추정됩니다. 이런 단위는 비율이 학과의 위험을 뜻하지 않아, 본분석과 같은 연평균 재적 30명 기준으로 빼고 다시 셌습니다. 그래도 겹치는 곳은 경영학부 한 곳이었습니다. 그래서 지원 명단은 비율과 인원을 함께 봐야 합니다.`);
  title(s, "탈락 인원 × 탈락률: 비율만 보면 생기는 착시");
  headline(s, `탈락률 상위 10과 탈락 인원 상위 10은 거의 겹치지 않는다 (원판정 ${D.r1.inter}곳, 해석 보정 ${RA.inter}곳) → 인원과 비율을 함께 본다`);
  fig(s, P("figures", "s05_hufs_count_rate.png"), MX, 2.65, 12.3, 6.95, "한국외대 학과별 합산 탈락 인원과 탈락률 산점도");
  const x = 13.75;
  T(s, [B(`${D.r1.inter}곳`, { color: C.risk, fontSize: 44 }), N("  →  ", { color: C.muted, fontSize: 28 }), B(`${RA.inter}곳`, { color: C.brand, fontSize: 44 })], { x, y: 2.6, w: 5.45, h: 0.9, valign: "middle" });
  T(s, "비율 상위 10 ∩ 인원 상위 10  (원판정 → 해석 보정)", { x, y: 3.5, w: 5.45, h: 0.45, fontSize: 13.5, color: C.muted });
  line(s, x, 4.1, R, 4.1);
  T(s, [B("왜 보정했나  ", { color: C.risk }), N(`원판정 탈락률 상위 10 중 ${RA.flag_in_top}곳이 '재적 1명, 탈락 1명' 같은 단위. 재적이 줄다 사라지고 사유가 미복학 → 개편 전 잔류 ${nRes}곳, 신설 초기 ${nNew}곳으로 추정`)], { x, y: 4.2, w: 5.45, h: 1.75, fontSize: 13.5 });
  T(s, "해석 보정판 탈락률 상위 3 (연평균 재적 ≥ 30명)", { x, y: 6.0, w: 5.45, h: 0.4, fontFace: F.bodyB, fontSize: 14.5, color: C.brand });
  T(s, ta.slice(0, 3).map((r, i) => ({ text: `${r["학과명"].replace("[통합모집]", "")}  ${f1(r["비율"])}% (재적 ${r["재적합"]}명)`, options: { breakLine: i < 2 } })), { x, y: 6.42, w: 5.45, h: 1.15, fontSize: 13, paraSpaceAfter: 2 });
  box(s, x, 7.75, 5.45, 1.85, { fill: C.tint, line: C.tint, r: 0.08 });
  T(s, [B("그래서  ", { color: C.brand }), N(`지원 명단은 재적 30명 이상에서 고르고 탈락 인원(명)을 함께 표시한다. 보정판 상위는 통합모집, 계열 단위(→ 슬라이드 9)`)], { x: x + 0.2, y: 7.8, w: 5.1, h: 1.75, fontSize: 13.5, valign: "middle" });
  readBar(s, "읽는 법", `점 = 한국외대 학과(공시 2024~2026 합산), 크기 = 재적, 파랑 = 비주류 외국어 학과군. 비율 해석 불가 단위 ${RA.n_flag}개(연평균 재적 30명 미만)는 그림에서 뺐다 → 부록 E-2`, 9.75);
  foot(s, `${SRC}, 노트북 §⑤ 셀 s5-c10, 부록 E 셀 sE-01(원판정), sE-02(해석 보정) (필수 차트 ① 교차 산점도)`);
}

// ================================================================ 6. 했다: 가설 A
{
  const pv = four("사립", "비수도권"), pm = four("국공립", "수도권");
  const s = slide("했다", `가설 A입니다. 사립이면서 비수도권인 학과는 ${f1(pv.pct)}%가 고위험이었고, 국공립 수도권은 ${f1(pm.pct)}%였습니다. 두 요인이 겹쳐 있어 계열과 규모를 통제한 회귀로 따로 봤습니다. 사립의 오즈비는 ${f2(A.priv.or)}, 비수도권은 ${f2(A.nonmetro.or)}이고, 학교 단위로 구간을 넓게 잡아도 둘 다 1을 넘어 가설 A는 맞았습니다. 다만 가장 큰 차이는 규모였습니다. 재적이 작은 학과는 큰 학과보다 고위험 오즈가 ${f1(Q1.or)}배였습니다. 이 결과는 상관이지 원인이 아닙니다.`);
  title(s, "가설 A: 사립, 비수도권", { hyp: "A", verdict: [`판정 ${D.verdict_A}`, C.a] });
  headline(s, `계열, 규모를 통제해도 사립 ${f1(A.priv.or)}배, 비수도권 ${f1(A.nonmetro.or)}배 — 가장 큰 신호는 소규모(${f1(Q1.or)}배)`);
  fig(s, P("figures", "s06_forest_A.png"), MX, 2.65, 11.2, 6.95, "가설 A 로지스틱 회귀 오즈비와 95% 구간");
  const x = 12.65;
  sub(s, "설립유형 × 지역의 고위험 비율", x, 2.62, 6.6, C.a, 21);
  const cells = [["국공립", "수도권"], ["국공립", "비수도권"], ["사립", "수도권"], ["사립", "비수도권"]];
  cells.forEach(([a, b], i) => {
    const r = four(a, b), xx = x + (i % 2) * 3.3, yy = 3.25 + Math.floor(i / 2) * 1.75, hot = a === "사립" && b === "비수도권";
    box(s, xx, yy, 3.1, 1.55, { fill: hot ? C.tintR : C.white, line: hot ? C.risk : C.rule, lw: hot ? 1.5 : 1, r: 0.08 });
    T(s, `${a}, ${b}`, { x: xx + 0.2, y: yy + 0.12, w: 2.8, h: 0.4, fontSize: 14, color: C.muted });
    T(s, `${f1(r.pct)}%`, { x: xx + 0.2, y: yy + 0.5, w: 2.8, h: 0.6, fontFace: F.bodyB, bold: true, fontSize: 28, color: hot ? C.risk : C.ink, valign: "middle" });
    T(s, `${n0(r.n)}쌍`, { x: xx + 0.2, y: yy + 1.1, w: 2.8, h: 0.35, fontSize: 12, color: C.muted });
  });
  box(s, x, 6.95, 6.55, 2.65, { fill: C.tint, line: C.tint, r: 0.08 });
  T(s, [B("판정  ", { color: C.a }), N(`사립 ${f2(A.priv.or)} [${f2(A.priv.lo)}, ${f2(A.priv.hi)}], 비수도권 ${f2(A.nonmetro.or)} [${f2(A.nonmetro.lo)}, ${f2(A.nonmetro.hi)}] — 둘 다 1을 넘어 `), B(D.verdict_A, { color: C.a }), N(". 학습 기간만, 의학계열 제외로 다시 해도 같은 판정")], { x: x + 0.25, y: 7.05, w: 6.1, h: 2.45, fontSize: 15, valign: "middle" });
  readBar(s, "읽는 법", `오즈비 1 = 차이 없음. 구간은 같은 학교 학과끼리 묶은 95% 구간(학교 ${D.n_school_A}개 군집). 상관이지 인과가 아니다`, 9.75);
  foot(s, `${SRC}, 노트북 §④ 셀 s4-03, s4-05, 분석 표본 ${n0(D.n_sample)}쌍`);
}

// ================================================================ 7. 했다: 예측 절 (차트 ③)
{
  const s = slide("했다", `예측입니다. 2026년 공시에서 작년에 고위험이었던 학과는 ${n0(D.K)}개였습니다. 센터가 이만큼 지원할 수 있다고 보고, 모델이 고른 ${n0(D.K)}개와 작년 명단을 비교했습니다. 구조 정보만 쓴 모델 1은 ${f1(m1["정밀도(%)"])}%로 작년 명단보다 못했습니다. 전년도 탈락률을 더한 모델 2는 ${f1(m2["정밀도(%)"])}%로 작년 명단 ${f1(b2["정밀도(%)"])}%보다 ${f1(gapP)}%p, ${n0(m2["맞힌 학과 수"] - b2["맞힌 학과 수"])}곳 더 맞혔습니다. 개선은 작습니다. 지원 학과 수를 바꾸거나 기준을 바꿔도 차이는 비슷했습니다. 가장 강한 신호는 결국 작년의 탈락률입니다.`);
  title(s, "예측: 작년 명단보다 나은가", { hyp: "P" });
  headline(s, `작년 고위험 학과 수(${n0(D.K)}개)만큼 지원하면 모델 2가 ${sgn(gapP)}%p — 개선은 작고, 가장 강한 신호는 전년도 탈락률`);
  card(s, MX, 2.65, 9.2, 6.95);
  sub(s, `같은 ${n0(D.K)}개를 지원했을 때 정밀도`, MX + 0.3, 2.8, 8.6, C.brand, 21);
  s.addChart(pres.charts.BAR, [{ name: "정밀도(%)", labels: ["모델 1 구조 변수", "모델 2 구조 + 전년도 탈락률", "기준선 작년 고위험 그대로"], values: [m1["정밀도(%)"], m2["정밀도(%)"], b2["정밀도(%)"]] }], {
    x: MX + 0.2, y: 3.4, w: 8.8, h: 5.0, barDir: "col", chartColors: [C.soft, C.brand, C.risk], barGapWidthPct: 55, valAxisMinVal: 0, valAxisMaxVal: 80, valAxisHidden: true,
    valGridLine: { style: "none" }, catGridLine: { style: "none" }, showValue: true, dataLabelFormatCode: '0.0"%"', dataLabelFontFace: F.bodyB, dataLabelFontSize: 18, dataLabelColor: C.ink, dataLabelPosition: "outEnd",
    catAxisLabelFontFace: F.body, catAxisLabelFontSize: 14, catAxisLabelColor: C.ink, catAxisLineShow: false, showLegend: false, varyColors: true });
  T(s, `맞힌 학과: 모델 1 ${n0(m1["맞힌 학과 수"])}, 모델 2 ${n0(m2["맞힌 학과 수"])}, 작년 명단 ${n0(b2["맞힌 학과 수"])}   |   무작위로 고르면 ${f1(D.pos_test)}%`, { x: MX + 0.3, y: 8.5, w: 8.6, h: 0.9, fontSize: 14, color: C.muted, valign: "middle" });
  // 오른쪽 위: k 곡선
  card(s, 10.3, 2.65, 8.9, 3.75);
  sub(s, "지원 학과 수 k를 바꾸면", 10.6, 2.8, 8, C.brand, 19);
  const kc = D.kcurve;
  s.addChart(pres.charts.LINE, [
    { name: "모델 2", labels: kc.map((r) => String(r.k)), values: kc.map((r) => r["모델 2"]) },
    { name: "작년 명단", labels: kc.map((r) => String(r.k)), values: kc.map((r) => r["기준선 ② (전년도 탈락률 순)"]) },
    { name: "모델 1", labels: kc.map((r) => String(r.k)), values: kc.map((r) => r["모델 1"]) }], {
    x: 10.45, y: 3.3, w: 8.6, h: 3.0, chartColors: [C.brand, C.risk, C.soft], lineSize: 2.5, lineDataSymbolSize: 7, valAxisMinVal: 40, valAxisMaxVal: 90,
    valAxisLabelFontSize: 11, catAxisLabelFontSize: 11, valAxisLabelFontFace: F.body, catAxisLabelFontFace: F.body, valGridLine: { color: "E6E9F0", size: 0.75 }, catGridLine: { style: "none" },
    showLegend: true, legendPos: "r", legendFontFace: F.body, legendFontSize: 12, valAxisLabelFormatCode: '0"%"' });
  // 오른쪽 아래: 민감도
  card(s, 10.3, 6.6, 8.9, 3.0);
  sub(s, "기준을 바꿔도 결론은 같다 (민감도)", 10.6, 6.72, 8.3, C.brand, 19);
  const rows = [[HD("조건"), HD("가설 A"), HD("모델 2 − 작년 명단")]].concat(D.sens.map((r) => [CELL(r["조건"].replace(" (사이버, 산업, 야간 등 포함)", "")), CELL(r["A 판정"], { al: "center" }), CELL(`${sgn(r["모델2 정밀도"] - r["기준선② 정밀도"])}%p`, { al: "center" })]));
  s.addTable(rows, { ...TBL, x: 10.55, y: 7.25, w: 8.4, colW: [4.5, 1.6, 2.3], fontSize: 11.5, rowH: 0.29 });
  readBar(s, "읽는 법", `정밀도 = 지원한 학과 중 실제로 고위험이었던 비율. 재현율(실제 고위험 중 명단에 든 비율)은 모델 2 ${f1(m2["재현율(%)"])}% vs 작년 명단 ${f1(b2["재현율(%)"])}%`, 9.75);
  foot(s, `${SRC}, 노트북 §④ 셀 s4-07, s4-14, 테스트 = 공시 2026 ${n0(D.n_test)}쌍 (필수 차트 ③)`);
}

// ================================================================ 8. 그래서: 가설 B (차트 ②)
pres.addSection({ title: "그래서" });
{
  const s = slide("그래서", `가설 B입니다. 한국외대의 비주류 외국어 학과군은 3년 합산 탈락률이 ${f2(G.hufs_target.rate)}%로, 교내 다른 학과 ${f2(G.hufs_other.rate)}%보다 오히려 ${f2(Math.abs(Bv["차이(%p)"]))}%p 낮았습니다. 구간도 0을 넘지 않아 가설 B는 기각입니다. 전국 같은 분야 학과 ${f2(G.national_same.rate)}%보다도 낮았습니다. 미리 정한 규칙대로, 어문 학과군의 문제는 이탈이 아니라 모집 쪽으로 넘깁니다. 왜 반대로 나왔는지 세 가지로 설명해 봤습니다. 첫째, 이탈이 앞 단계로 옮겨 갔을 수 있습니다. ${D.lang_unit_first}년 공시부터 외국어 계열 통합모집 단위가 생겼고, 이런 전공 배정 전 단위의 탈락은 대부분 자퇴였습니다. 다만 그 이전 해에도 어문 학과군이 낮았기 때문에 일부만 설명합니다. 둘째, 학생들이 스스로 고른 전공이라서일 수 있고, 셋째, 이중전공이나 전과로 학교를 떠나지 않고 길을 바꿀 수 있어서일 수 있습니다. 이 두 가지는 데이터에 없어 추정입니다. 대신 모델로 내년 후보를 뽑아 보니 상위 ${D.k_next}곳 중 ${D.cand_unit}곳이 통합모집, 계열, 자유전공처럼 전공을 정하기 전 단위였습니다. 이 단위들의 탈락은 ${f1(D.premajor["전공 배정 전 단위"].jatoe_share)}%가 자퇴여서, 1학년 때 다른 대학으로 다시 입학하는 반수나 입학 초기 부적응으로 추정됩니다. 개인 사유는 데이터에 없어 추정으로만 말씀드립니다.`);
  title(s, "가설 B: 한국외대 비주류 외국어 학과군", { hyp: "B", verdict: [`판정 ${D.verdict_B}`, C.b], w: 11 });
  headline(s, `비주류 외국어 학과군은 오히려 ${f2(Math.abs(Bv["차이(%p)"]))}%p 낮다 — 높은 탈락은 1학년 단위(통합모집, 계열)에 모여 보인다`);
  fig(s, P("figures", "s08_hufs_groups.png"), MX, 2.65, 10.2, 5.95, "한국외대 학과군별 합산 탈락률과 95% 구간");
  const x = 11.55, PM = D.premajor["전공 배정 전 단위"], OT = D.premajor["그 밖의 학과"], BY = D.b_yearly;
  card(s, x, 2.65, 7.65, 2.85, C.b);
  T(s, [B("판정  ", { color: C.b }), N(`차이 ${f2(Bv["차이(%p)"])}%p, 95% 구간 [${f2(Bv["95% 하한"])}, ${f2(Bv["95% 상한"])}] — 하한이 0보다 작아 `), B(D.verdict_B, { color: C.b }), N(`. ${D.b_years}개 연도 모두 낮음`)], { x: x + 0.3, y: 2.78, w: 7.1, h: 0.95, fontSize: 14.5, valign: "middle" });
  T(s, [B("참고  ", { color: C.muted }), N(`전국 같은 소계열(${G.national_same.n_school}개교)보다도 ${f2(Math.abs(D.nat_diff))}%p 낮음 (가설 아님)`)], { x: x + 0.3, y: 3.75, w: 7.1, h: 0.6, fontSize: 14, valign: "middle" });
  T(s, [B("규칙대로  ", { color: C.risk }), N("이탈 지원의 우선 대상이 아니다 → '모집(입학처)' 관점으로 재정의")], { x: x + 0.3, y: 4.4, w: 7.1, h: 0.95, fontSize: 14.5, valign: "middle" });
  card(s, x, 5.7, 7.65, 2.9);
  sub(s, `공시 2027 우선 지원 후보 상위 ${D.k_next}곳 (모델 2)`, x + 0.3, 5.8, 7.2, C.brand, 18);
  T(s, [B(`${D.cand_unit}곳`, { color: C.brand, fontSize: 28 }), N(`  1학년 단위(통합모집, 계열, 자유전공)    `, { fontSize: 14 }), B(`${D.cand_target}곳`, { color: C.b, fontSize: 28 }), N("  비주류 외국어", { fontSize: 14 })], { x: x + 0.3, y: 6.3, w: 7.2, h: 0.65, valign: "middle" });
  const top = D.cand.slice(0, 3);
  const rows = [[HD("후보"), HD("재적"), HD("탈락률"), HD("점수")]].concat(top.map((r) => [CELL(r["학과명"]), CELL(`${r["재적"]}명`, { al: "center" }), CELL(`${f1(r["비율"])}%`, { al: "center" }), CELL(f2(r["점수"]), { al: "center" })]));
  s.addTable(rows, { ...TBL, x: x + 0.3, y: 7.0, w: 7.05, colW: [3.85, 1.0, 1.1, 1.1], fontSize: 12, rowH: 0.32 });
  // 반대 결과 수용 (가설 문서 7절 조항): 대안 설명 — 데이터로 확인되는 것과 추정을 나눔 (노트북 s4-12b)
  box(s, MX, 8.82, CW, 1.6, { fill: C.tint, line: C.tint, r: 0.08 });
  T(s, "반대 결과 수용 — 왜 낮게 나왔나", { x: MX + 0.25, y: 8.86, w: 9, h: 0.4, fontFace: F.bodyB, fontSize: 15, color: C.brand, valign: "middle" });
  T(s, [
    B("① 분석 전에 예상한 방향과 일치  ", { color: C.ink }),
    N(`"한국외대는 이 분야 최상위 학교라 자발적으로 지망한 학생이 많을 수 있다. 그래서 전국보다 낮거나 비슷할 가능성이 있다"(가설 문서 v2). 분석 전 노트에도 "한국외대는 비주류 외국어 학과라도 스스로 지망해 온 학생이 많아 탈락률이 높지만은 않을 것"이라고 적어 둠. 지망 여부는 데이터로 확인 불가`, { color: C.ink, breakLine: true }),
    B("② 이탈이 1학년 단위로 옮겨 감 (일부 확인)  ", { color: C.ink }),
    N(`${D.lang_unit_first} 공시부터 외국어 계열 통합모집 생김, 전공 배정 전 단위 탈락의 ${f1(PM.jatoe_share)}%가 자퇴. 그 전 해도 낮아 부분 설명      `),
    B("③ 이중전공, 전과 (추정)", { color: C.ink }),
  ], { x: MX + 0.25, y: 9.28, w: CW - 0.5, h: 1.1, fontSize: 13.5, valign: "top", paraSpaceAfter: 3 });
  foot(s, `${SRC}, 노트북 §④ 셀 s4-10, s4-12, s4-12b, s4-13, s4-13b, §⑤ 셀 s5-c09 (필수 차트 ②)`);
}

// ================================================================ 9. 그래서: 권고와 근거
{
  const s = slide("그래서", `권고는 세 가지입니다. 첫째, 학사종합지원센터는 내년 명단을 작년 고위험 학과로 시작하고 모델 점수로 보완합니다. 모델이 작년 명단보다 조금 낫지만 차이가 작아서, 작년 명단만으로도 큰 손해는 없습니다. 이때 재적 30명 이상에서 고르고 인원을 함께 봅니다. 둘째, 통합모집, 계열, 자유전공처럼 전공을 정하기 전 단위를 먼저 점검합니다. 셋째, 어문 학과군은 이탈 지원보다 입학처의 모집 관점에서 다시 봅니다. 전국 결과인 사립과 비수도권 효과는 한국외대 안에서는 모든 학과가 같은 조건이라 배분 기준으로 쓰지 않습니다.`);
  title(s, "권고와 근거");
  headline(s, "작년 명단을 기본으로, 1학년 초기 이탈을 먼저 — 어문 학과군은 입학처의 모집 문제로");
  const recs = [
    ["학사종합지원센터", "내년 지원 명단 = 작년 고위험 학과 + 모델 점수로 보완", `모델 2 ${f1(m2["정밀도(%)"])}% vs 작년 명단 ${f1(b2["정밀도(%)"])}% (${sgn(gapP)}%p) — 차이가 작아 작년 명단이 기본`, `재적 30명 이상에서 고르고, 탈락 인원(명)을 함께 표시 (비율 상위 10 ∩ 인원 상위 10 = 원판정 ${D.r1.inter}, 보정 ${D.r1_adj.inter}곳)`, "s4-07, sE-01", C.brand],
    ["학사종합지원센터", "1학년 초기 이탈 관리 — 통합모집, 계열, 자유전공 단위부터", `2027 후보 상위 ${D.k_next}곳 중 ${D.cand_unit}곳, 탈락의 ${f1(D.premajor["전공 배정 전 단위"].jatoe_share)}%가 자퇴. 단 1학년만 모인 단위라 비율 직접 비교는 불가(다른 학과 1학년 ${f1(D.fair.lo)}~${f1(D.fair.hi)}%)`, "1학년 1학기 적응 상담과 전공 안내를 앞당기고, 입학처와 반수 이탈 여부를 함께 확인", "s4-13, s4-13b, s4-13c", C.brand],
    ["입학처", "어문 학과군은 '이탈'이 아니라 '모집'으로 재정의", `가설 B ${D.verdict_B}: 교내보다 ${f2(Math.abs(Bv["차이(%p)"]))}%p 낮고 전국 같은 분야보다도 낮다`, "지원율, 충원율 자료로 다음 분석 (이 데이터에는 없음)", "s4-10, s4-12", C.b],
  ];
  recs.forEach(([who, what, ev, how, cell, col], i) => {
    const y = 2.65 + i * 2.3;
    card(s, MX, y, CW, 2.1, col);
    num(s, i + 1, MX + 0.3, y + 0.25, 0.5, col);
    pill(s, who, MX + 1.0, y + 0.27, { w: 2.7, h: 0.45, fill: C.white, line: col, color: col, size: 14 });
    T(s, what, { x: MX + 3.95, y: y + 0.2, w: 14.2, h: 0.6, fontFace: F.bodyB, fontSize: 20, valign: "middle" });
    T(s, [B("근거  ", { color: col }), N(ev)], { x: MX + 1.0, y: y + 0.9, w: 17.1, h: 0.5, fontSize: 15, valign: "middle" });
    T(s, [B("방법  ", { color: col }), N(how)], { x: MX + 1.0, y: y + 1.4, w: 11.0, h: 0.5, fontSize: 15, valign: "middle" });
    T(s, `출처 셀 ${cell}`, { x: R - 3.6, y: y + 1.45, w: 3.35, h: 0.45, fontFace: F.small, fontSize: 12, color: C.muted, align: "right", valign: "middle" });
  });
  readBar(s, "쓰지 않는 근거", `가설 A(사립, 비수도권)는 맞았지만, 한국외대 안에서는 모든 학과가 같은 설립유형, 지역이라 학과 배분 기준이 되지 못한다 — 전국 맥락으로만 쓴다`, 9.65);
  foot(s, `${SRC}, 노트북 §④ 셀 s4-15 (판정 요약)`);
}

// ================================================================ 10. 그래서: 한계와 믿기 어려운 이유
{
  const he2 = hE.find((r) => r["방법"].startsWith("모델 2")), hb = hE.find((r) => r["방법"].startsWith("기준선 ②"));
  const s = slide("그래서", `마지막으로 이 결과를 믿기 어려운 이유입니다. 시험은 2026년 공시 한 해뿐이라 내년에도 같은 차이가 난다는 보장이 없습니다. 학과 단위 집계라서 학생 한 명 한 명이 왜 떠났는지는 알 수 없고, 사립이나 비수도권 때문에 탈락한다고 말할 수도 없습니다. 학과가 폐지되거나 코드가 바뀌면 연결에서 빠져서, 한국외대는 2026년에만 ${D.hufs_unlinked}개가 빠졌습니다. 한국외대만 따로 예측을 검증하면 ${D.hufs_test_n}개 학과뿐이라, 오히려 작년 명단이 더 잘 맞았습니다. 감사합니다.`);
  title(s, "한계와 믿기 어려운 이유");
  headline(s, "이 결과로 말할 수 없는 것 — 원인, 내년의 성능, 학생 한 명의 이탈 이유");
  const L = [
    ["테스트는 공시 2026 한 해뿐", `${sgn(gapP)}%p가 내년에도 유지된다는 보장이 없다`],
    ["학과 단위 집계, 상관 ≠ 인과", "사립, 비수도권 '때문에' 탈락한다고 말할 수 없다. 학생 구성 등은 관측되지 않았다"],
    ["생존 편향과 공시 변화", `연결되지 않은 학과 ${n0(D.n_unlinked)}행(한국외대 ${D.hufs_unlinked}개)이 빠졌고, 2024년부터 결측이 늘었다`],
  ];
  card(s, MX, 2.65, 8.9, 6.85, C.risk);
  sub(s, "한계 3가지", MX + 0.3, 2.82, 8, C.risk);
  L.forEach(([h, b], i) => {
    const y = 3.55 + i * 1.95;
    num(s, i + 1, MX + 0.3, y, 0.45, C.risk);
    T(s, h, { x: MX + 0.95, y: y - 0.05, w: 7.7, h: 0.55, fontFace: F.bodyB, fontSize: 18.5, valign: "middle" });
    T(s, b, { x: MX + 0.95, y: y + 0.55, w: 7.7, h: 1.1, fontSize: 15, color: C.muted });
  });
  card(s, 10.0, 2.65, 9.2, 6.85);
  sub(s, "믿기 어려운 이유", 10.3, 2.82, 8.5);
  const W = [
    ["한국외대 예측은 작은 표본", `검증 학과 ${D.hufs_test_n}개, k = ${D.k_h}: 모델 2 ${f1(he2["정밀도(%)"])}% vs 작년 명단 ${f1(hb["정밀도(%)"])}% — 우연에 크게 흔들린다`],
    ["1학년 단위의 비율은 직접 비교 불가", `학년별 탈락 자료가 없어 다른 학과의 1학년 탈락률은 ${f1(D.fair.lo)}~${f1(D.fair.hi)}% 범위로만 안다. 통합모집, 계열 단위의 ${f1(D.fair.pm)}%는 그 안에 있다`],
    ["'비인기, 존폐 위기'는 판단 불가", "지원율, 충원율, 모집정원이 없다. 그래서 B 기각 뒤의 모집 문제는 이 자료로 답할 수 없다"],
    ["작은 단위의 비율은 개편의 흔적", `'재적 1명, 탈락 1명 = 100%'처럼 개편 중 단위는 비율이 위험을 뜻하지 않는다 → 연평균 재적 30명 미만 ${D.r1_adj.n_flag}개는 비율 순위에서 뺐다(추정 근거: 재적 감소, 소멸, 미복학)`],
  ];
  W.forEach(([h, b], i) => {
    const y = 3.5 + i * 1.5;
    T(s, h, { x: 10.3, y, w: 8.6, h: 0.5, fontFace: F.bodyB, fontSize: 17, valign: "middle" });
    T(s, b, { x: 10.3, y: y + 0.5, w: 8.6, h: 0.85, fontSize: 14.5, color: C.muted });
  });
  readBar(s, "그래도 쓸 수 있는 것", "기준 6가지를 바꿔도 A, B 판정과 '모델 ≈ 작년 명단' 결론은 뒤집히지 않았다(민감도). 노트북은 처음부터 다시 돌려 같은 숫자가 나온다", 9.7);
  foot(s, `${SRC}, 노트북 §④ 셀 s4-13, s4-13c, s4-14, 부록 E 셀 sE-02, 정제로그 표 4`);
}

// ================================================================ 부록
pres.addSection({ title: "부록" });
// A. 재현성
{
  const s = slide("부록");
  title(s, "부록 A. 재현성 확인");
  headline(s, "노트북을 새 커널에서 처음부터 실행해 같은 숫자가 나오는지 확인했다");
  const rows = [[HD("확인 항목"), HD("정승엽 (로컬)"), HD("박유진"), HD("신효주")],
    [CELL("에러 없이 완주"), CELL("O", { al: "center" }), CELL("O", { al: "center" }), CELL("O", { al: "center" })],
    [CELL("원본 행 × 열"), CELL(`${n0(D.n_raw)} × ${D.n_cols}`, { al: "center" }), CELL("56,340 × 32", { al: "center" }), CELL("56,340 × 32", { al: "center" })],
    [CELL("범위 안 행 수 / 분석 표본 쌍 수"), CELL(`${n0(D.n_scope)} / ${n0(D.n_sample)}`, { al: "center" }), CELL("50,081 / 23,114", { al: "center" }), CELL("50,081 / 23,114", { al: "center" })],
    [CELL("가설 A 사립, 비수도권 오즈비"), CELL(`${f2(A.priv.or)}, ${f2(A.nonmetro.or)}`, { al: "center" }), CELL("3.83, 3.36", { al: "center" }), CELL("3.83, 3.36", { al: "center" })],
    [CELL("가설 B 차이와 95% 구간"), CELL(`${f2(Bv["차이(%p)"])}%p [${f2(Bv["95% 하한"])}, ${f2(Bv["95% 상한"])}]`, { al: "center" }), CELL("-1.25%p [-1.92, -0.56]", { al: "center" }), CELL("-1.25%p [-1.92, -0.56]", { al: "center" })],
    [CELL("모델 2 정밀도 / 작년 명단"), CELL(`${f1(m2["정밀도(%)"])}% / ${f1(b2["정밀도(%)"])}%`, { al: "center" }), CELL("60.3% / 58.6%", { al: "center" }), CELL("60.3% / 58.6%", { al: "center" })],
    [CELL("실행 환경"), CELL(`로컬 Python ${D.versions.python}, pandas ${D.versions.pandas}`, { al: "center" }), CELL("Colab Python 3.13.18, pandas 2.2.3", { al: "center" }), CELL("최종 노트북 로컬 실행", { al: "center" })]];
  s.addTable(rows, { ...TBL, x: MX, y: 2.75, w: CW, colW: [5.6, 5.0, 3.9, 3.9], fontSize: 15, rowH: 0.62 });
  readBar(s, "링크", "Colab 정승엽(팀 정본) …/1JCE1qZSWkixXybo86cDwFJpl4_n-Tbmc, 박유진 …/1Tded6jGpKo6t-hRTiHinln37t0vluC7d, GitHub 202103116-stack/university-dropout-risk-analysis", 8.6);
  T(s, "pandas 주 버전이 달라도(2.2.3, 3.0.6) 모든 숫자가 같았다", { x: MX, y: 9.35, w: CW, h: 0.4, fontSize: 14, color: C.muted });
  foot(s, `logs/재현성_확인표.md, 실행 ${D.run_at}`);
}
// B. 기여도표
{
  const s = slide("부록");
  title(s, "부록 B. 기여도표");
  headline(s, "안내문 5단계별 담당자와 검토자");
  const st = [["① 문제 정의", "의사결정 질문, 가설 A, B, 판정 규칙 고정"], ["② 수집", "원자료, 출처, 이용 조건, 범위 정의, 측정 척도"], ["③ 정제", "품질 6대 기준 진단, 범위 확정, 정제 로그"], ["④ 분석", "EDA, 모델, 기준선, 민감도, 가설 판정"], ["⑤ 발표", "차트 3종, 권고, 근거, 한계, 슬라이드, 발표"], ["공통", "AI 활용 로그, 재현성 확인"]];
  const WHO = { "① 문제 정의": ["박유진", "신효주"], "② 수집": ["박유진", "정승엽"], "③ 정제": ["정승엽", "박유진"], "④ 분석": ["정승엽", "신효주"], "⑤ 발표": ["신효주", "정승엽"], "공통": ["전원", "전원"] };  // logs/기여도표.md와 같게
  const who = (v) => (v ? CELL(v, { al: "center" }) : CELL("[팀 입력]", { al: "center", color: C.muted }));
  const rows = [[HD("단계"), HD("세부 작업"), HD("담당자"), HD("검토자")]].concat(st.map(([a, b]) => [CELL(a, { b: true }), CELL(b), who(WHO[a][0]), who(WHO[a][1])]));
  s.addTable(rows, { ...TBL, x: MX, y: 2.75, w: CW, colW: [3.0, 9.4, 3.0, 3.0], fontSize: 15, rowH: 0.7 });
  foot(s, "logs/기여도표.md (제출물 6번)");
}
// C. AI 활용 요약
{
  const s = slide("부록");
  title(s, "부록 C. AI 활용 로그 요약");
  headline(s, "AI가 틀린 진술은 원문과 재측정으로 바로잡고, 모든 수치는 셀 출력과 대조했다");
  const rows = [[HD("AI 진술, 제안"), HD("검증 방법"), HD("결과")],
    [CELL("안내문이 '제안서 1쪽'을 요구한다"), CELL("안내 PDF 원문 직접 확인"), CELL("수정: 분량 제한 없음", { b: true })],
    [CELL("B 대상군에 국제지역학 포함"), CELL("학과명 단위로 소계열 갈림 재측정"), CELL("수정: 민감도로만 사용", { b: true })],
    [CELL("전국 같은 분야보다 한국외대가 높을 것"), CELL("근거 없는 방향 가정이라는 사용자 지적"), CELL("수정: 판정에서 빼고 결과 문구만 고정", { b: true })],
    [CELL("계획서 기준값 '재계산 불일치 68행'"), CELL("노트북 재계산(최대 차이 0.005%p)"), CELL("기록: 재현 안 됨 [확인 필요]", { b: true })],
    [CELL("정제, 분석, 시각화 코드"), CELL("assert, 누수 점검, 시드 4개, 그림 직접 확인"), CELL("채택", { b: true })]];
  s.addTable(rows, { ...TBL, x: MX, y: 2.75, w: CW, colW: [6.8, 6.6, 5.0], fontSize: 15, rowH: 0.7 });
  foot(s, "제출물: 14조_AI활용로그.pdf, 전체 기록 logs/AI활용기록.md");
}
// D. 정제 추적표와 민감도
{
  const s = slide("부록");
  title(s, "부록 D. 범위 제외 내역과 민감도");
  headline(s, "어떤 조건으로 몇 행이 빠졌는지, 기준을 바꾸면 결론이 어떻게 되는지");
  const ex = [[HD("범위 조건"), HD("단독 제외"), HD("순차 제외")]].concat(D.excluded.map((r) => [CELL(r["조건"]), CELL(n0(r["단독"]), { al: "right" }), CELL(n0(r["순차"]), { al: "right" })]));
  s.addTable(ex, { ...TBL, x: MX, y: 2.75, w: 7.6, colW: [3.8, 1.9, 1.9], fontSize: 14, rowH: 0.55 });
  const sv = [[HD("조건"), HD("쌍 수"), HD("A 판정"), HD("사립 OR"), HD("비수도권 OR"), HD("모델 2"), HD("작년 명단")]].concat(D.sens.map((r) => [CELL(r["조건"]), CELL(n0(r["쌍 수"]), { al: "right" }), CELL(r["A 판정"], { al: "center" }), CELL(f2(r["사립 OR"]), { al: "center" }), CELL(f2(r["비수도권 OR"]), { al: "center" }), CELL(`${f1(r["모델2 정밀도"])}%`, { al: "center" }), CELL(`${f1(r["기준선② 정밀도"])}%`, { al: "center" })]));
  s.addTable(sv, { ...TBL, x: 8.7, y: 2.75, w: 10.5, colW: [3.6, 1.1, 1.0, 1.15, 1.35, 1.15, 1.15], fontSize: 12.5, rowH: 0.55 });
  readBar(s, "민감도 ①", `B 대상군에 국제지역학 소계열을 더해도 차이 ${f2(D.b_sens.diff)}%p [${f2(D.b_sens.lo)}, ${f2(D.b_sens.hi)}] → ${D.b_sens.verdict}. 임계값 0.5로 고르면 ${n0(D.thr05.n)}곳, 정밀도 ${f1(D.thr05.precision)}%`, 7.4);
  foot(s, "노트북 §③ 셀 s3-16, §④ 셀 s4-14, 정제로그 표 4, 5, 6");
}
// E. R1 두 목록
{
  const s = slide("부록");
  title(s, "부록 E. 보조 분석 R1: 비율 상위 vs 인원 상위");
  headline(s, `한국외대 공시 2024~2026 합산 — 두 상위 10 목록의 교집합 ${D.r1.inter}곳 (가설 판정이 아닌 보조 분석)`);
  const mk = (list, key) => [[HD("학과"), HD("탈락(명)"), HD("재적(명)"), HD("탈락률")]].concat(list.map((r) => [CELL(r["학과명"]), CELL(n0(r["탈락합"]), { al: "right", b: key === "n" }), CELL(n0(r["재적합"]), { al: "right" }), CELL(`${f1(r["비율"])}%`, { al: "right", b: key === "r" })]));
  sub(s, "탈락률 상위 10", MX, 2.6, 8, C.risk, 20);
  s.addTable(mk(D.r1.top_rate, "r"), { ...TBL, x: MX, y: 3.15, w: 8.9, colW: [4.4, 1.5, 1.5, 1.5], fontSize: 13, rowH: 0.5 });
  sub(s, "탈락 인원 상위 10", 10.3, 2.6, 8, C.ink, 20);
  s.addTable(mk(D.r1.top_cnt, "n"), { ...TBL, x: 10.3, y: 3.15, w: 8.9, colW: [4.4, 1.5, 1.5, 1.5], fontSize: 13, rowH: 0.5 });
  foot(s, "노트북 부록 E 셀 sE-01, 판정 규칙: 00_문제정의_가설.md 10절 (사전 규칙 그대로 센 원판정)");
}
// E-2. R1 해석 보정판
{
  const RA = D.r1_adj;
  const s = slide("부록");
  title(s, "부록 E-2. R1 해석 보정: 비율을 해석할 수 없는 단위");
  headline(s, `원판정 탈락률 상위 10 중 ${RA.flag_in_top}곳은 개편, 신설 단위 — 같은 최소 재적 기준(연평균 30명)으로 다시 세면 교집합 ${RA.inter}곳`);
  const fr = [[HD("원판정 상위 10"), HD("연평균 재적"), HD("해석 (근거)")]].concat(RA.top_rate_flags.map((r) => [CELL(r["학과명"]), CELL(f1(r["연평균재적"]), { al: "right" }), CELL(r["해석"] || "해석 가능", { color: r["해석"] ? C.risk : C.muted })]));
  s.addTable(fr, { ...TBL, x: MX, y: 2.75, w: 9.6, colW: [3.6, 1.4, 4.6], fontSize: 12, rowH: 0.5 });
  const ad = [[HD("보정판 상위 10"), HD("탈락(명)"), HD("재적(명)"), HD("탈락률")]].concat(RA.top_rate.map((r) => [CELL(r["학과명"]), CELL(n0(r["탈락합"]), { al: "right" }), CELL(n0(r["재적합"]), { al: "right" }), CELL(`${f1(r["비율"])}%`, { al: "right", b: true })]));
  s.addTable(ad, { ...TBL, x: 10.7, y: 2.75, w: 8.5, colW: [4.4, 1.3, 1.4, 1.4], fontSize: 12, rowH: 0.5 });
  readBar(s, "규칙", "재적(학년도 학적 보유자)과 탈락(그 1년간 떠난 수)은 같은 사람을 센다 → 1/1 = 남은 한 명이 떠남. 연평균 재적 30명 미만은 비율 순위에서만 빼고 행, 인원 순위는 그대로 둔다", 8.55);
  foot(s, "노트북 부록 E 셀 sE-02, 원판정(sE-01)은 바꾸지 않음, 추정은 학과코드의 재적 추이, 소멸, 탈락 사유(미복학)에 근거");
}

pres.writeFile({ fileName: OUT }).then(() => console.log("written", OUT, "slides", PAGE));
