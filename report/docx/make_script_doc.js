// 발표 대본 문서: slides/발표대본.md → slides/14조_발표대본.docx (표지 + 본문, 제출 문서와 같은 양식)
// 실행: node report/docx/make_script_doc.js → finalize.ps1로 PDF
const fs = require('fs');
const path = require('path');
const os = require('os');
const { md2docx, COVER, MAIN, build, cover } = require('./make_submissions');

const ROOT = path.resolve(__dirname, '..', '..');
const SRC = path.join(ROOT, 'slides', '발표대본.md');
// Word 글꼴에서 깨지는 그림 문자(💡)는 '팁:'으로, 첫 제목은 표지가 대신하므로 그대로 두고 md2docx가 건너뛴다
const text = fs.readFileSync(SRC, 'utf-8').replace(/💡\s*/g, '팁: ');
const tmp = path.join(os.tmpdir(), 'tp2_script.md');
fs.writeFileSync(tmp, text, 'utf-8');
const rel = path.relative(ROOT, tmp);

(async () => {
  const front = cover(COVER('빅데이터분석 팀 프로젝트2 발표 자료', '발표 대본', MAIN));
  await build('14조_발표대본', front, md2docx(rel, 1), path.join(ROOT, 'slides'));
})();
