"""주제계획서 docx 수정: 하이라이트 제거, 탈락 후보 작성, 회색 글자→검정, 중간점 교체, 표지 추가.
사용: python edit_proposal.py <입력.docx> <출력.docx> <watermark.png>
"""
import difflib
import re
import shutil
import sys
import zipfile
from xml.sax.saxutils import escape

SRC, DST, MARK = sys.argv[1], sys.argv[2], sys.argv[3]

with zipfile.ZipFile(SRC) as z:
    files = {n: z.read(n) for n in z.namelist()}
doc = files['word/document.xml'].decode('utf-8')

# ── 1. 문단 텍스트 치환(런 서식 유지: diff로 런에 다시 나눠 담음) ──────────
SECOM = ("UCI SECOM(반도체 제조 공정 센서 데이터, 공정 합격/불합격 분류). "
         "도메인 지식이 부족한 비전공자라도 4차 산업 시대에 AI를 활용하면 해당 분야의 전문가가 아니어도 "
         "높은 수준의 분석 결과를 제시할 수 있고, 이를 발판으로 더 깊이 파고들어 도메인 전문가로 성장할 수 있다는 "
         "가능성을 보여 주고 싶었다. 그러나 기업의 반도체 공정 데이터는 기밀이 많아 공개 자료로는 현장의 맥락을 얻기 어렵고, "
         "SECOM 역시 각 센서가 무엇을 측정하는지에 대한 정보 없이 익명화된 측정값만 담고 있어 변수 해석과 공정 개선 제안으로 "
         "이어 가기 어렵다는 한계가 있어 제외했다.")

REPL = [
    ('팀 프로젝트 · 주제 계획서', '팀 프로젝트 | 주제 계획서'),
    ('분석·예측', '분석 및 예측'),
    ('조 · 팀원', '조 / 팀원'),
    ('14조 · 정승엽 [202103116] , 박유진 [202004229], 신효주 [202404341]',
     '14조: 정승엽(202103116), 박유진(202004229), 신효주(202404341)'),
    ('(상담·학습지원·복학 안내)', '(상담, 학습지원, 복학 안내)'),
    ('설립유형·지역·계열·규모를', '설립유형, 지역, 계열, 규모를'),
    ('비수도권·사립·소규모', '비수도권, 사립, 소규모'),
    ("'기타유럽어·문학'·'기타아시아어·문학'인", "'기타유럽어 문학', '기타아시아어 문학'인"),
    ('지역·설립유형 중심', '지역 및 설립유형 중심'),
    ('계열·규모 중심', '계열과 규모 중심'),
    ('56,340행 × 32열 · 공시연도 2023~2026 · 공공누리 제1유형(출처 표시) · 포털 등록·수정일 2026-09-10 · 다운로드일 [2026-11-08]',
     '56,340행 × 32열 / 공시연도 2023~2026 / 공공누리 제1유형(출처 표시) / 포털 등록일(수정일) 2026-09-10 / 다운로드일 2026-11-08'),
    ('지난 · 이번 발표자', '지난 / 이번 발표자'),
    ('지난 발표자: [박유진]   이번 발표자: [신효주 또는 정승엽]', '지난 발표자: 박유진   이번 발표자: 신효주 또는 정승엽'),
    ('[팀 입력] 실제로 열어 본 후보 주제·데이터 1개와 뺀 이유', SECOM),
    (' 노란 칸은 팀 확인·입력 필요.', ''),
    ('규모·구조', '규모와 구조'),
    ('(공시연도·학교·학과) 키', '(공시연도, 학교, 학과) 키'),
    ('건수·근거 로그', '건수와 근거 로그'),
    ('10·50명으로 민감도', '10명, 50명으로 민감도'),
    ('분석 단위·범위', '분석 단위와 범위'),
    ('(학교·학과) × 공시연도', '(학교, 학과) × 공시연도'),
    ('폐교·신설 제외', '폐교 및 신설 제외'),
    ('계·사유·비율은', '계, 사유, 비율은'),
    ('학습·테스트', '학습/테스트'),
    ('t=2024·2025', 't=2024, 2025'),
    ('모델·판정', '모델과 판정'),
    ('정확도·정밀도·재현율·AUC·혼동행렬을', '정확도, 정밀도, 재현율, AUC, 혼동행렬을'),
    ('10·30·50명', '10, 30, 50명'),
    ('계열·설립유형·지역별', '계열, 설립유형, 지역별'),
    ('적중률·임계값 비교', '적중률과 임계값 비교'),
    ('자퇴·미등록·미복학이다', '자퇴, 미등록, 미복학이다'),
    ('(전체·계열별)', '(전체 및 계열별)'),
    ('(상담·복학 안내)', '(상담, 복학 안내)'),
    ('(기타유럽어·기타아시아어 문학 소계열)', '(기타유럽어, 기타아시아어 문학 소계열)'),
    ('다른 학과·전국 동일', '다른 학과와 전국 동일'),
    ('(최소 재적·임계값별', '(최소 재적, 임계값별'),
    ('(경제·정서·진로)', '(경제, 정서, 진로)'),
    ('폐지·통폐합·신설', '폐지, 통폐합, 신설'),
    ('학부·전공 개편', '학부 및 전공 개편'),
    ('신규 38·소멸 24개', '신규 38개, 소멸 24개'),
    ('서울·글로벌 캠퍼스', '서울캠퍼스와 글로벌캠퍼스'),
    ('미등록·미복학 등', '미등록, 미복학 등'),
    ('(주제·데이터 조정)', '(주제, 데이터 조정)'),
    ('질문·가설', '질문과 가설'),
    ('수집·정제', '수집 및 정제'),
    ('재다운로드·행/열', '재다운로드, 행/열'),
    ('(처리·건수·근거·영향)', '(처리, 건수, 근거, 영향)'),
    ('기준선·민감도 비교', '기준선 및 민감도 비교'),
]
used = set()

T_RE = re.compile(r'(<w:t(?: [^>]*)?>)([^<]*)(</w:t>)')


def unesc(s):
    return s.replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&apos;', "'").replace('&amp;', '&')


def fix_para(p):
    nodes = list(T_RE.finditer(p))
    if not nodes:
        return p
    texts = [unesc(m.group(2)) for m in nodes]
    old = ''.join(texts)
    new = old
    for i, (a, b) in enumerate(REPL):
        if a in new:
            new = new.replace(a, b)
            used.add(i)
    if new == old:
        return p
    owner = [k for k, t in enumerate(texts) for _ in t]  # 원문 글자 → 런 번호
    out = [''] * len(texts)
    sm = difflib.SequenceMatcher(None, old, new, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            for k in range(i2 - i1):
                out[owner[i1 + k]] += new[j1 + k]
        elif j2 > j1:  # replace/insert: 바뀐 앞 글자의 런에 붙임
            run = owner[i1] if i1 < len(owner) else owner[-1]
            if tag == 'insert' and i1 > 0:
                run = owner[i1 - 1]
            out[run] += new[j1:j2]
    res, last = [], 0
    for m, t in zip(nodes, out):
        open_tag = m.group(1)
        if 'xml:space' not in open_tag:
            open_tag = '<w:t xml:space="preserve">'
        res.append(p[last:m.start()] + open_tag + escape(t) + m.group(3))
        last = m.end()
    res.append(p[last:])
    return ''.join(res)


doc = re.sub(r'<w:p[ >].*?</w:p>', lambda m: fix_para(m.group(0)), doc, flags=re.S)
missing = [REPL[i][0] for i in range(len(REPL)) if i not in used]
assert not missing, missing

# ── 2. 노란 하이라이트 제거 ──
doc = re.sub(r'<w:highlight w:val="[^"]*"/>', '', doc)

# ── 3. 회색·청색 글자 → 검정 ──
GRAYS = ['595959', '404040', '7F7F7F', '808080', '2E74B5', '1F4D78']


def blacken(x):
    for g in GRAYS:
        x = x.replace('<w:color w:val="%s"/>' % g, '<w:color w:val="000000"/>')
    return x


doc = blacken(doc)
for n in ['word/styles.xml', 'word/header1.xml', 'word/footer1.xml']:
    files[n] = blacken(files[n].decode('utf-8')).encode('utf-8')

# ── 4. 표지(프로젝트1 cover.js 양식을 XML로 옮김) ──
HB, HM, HL, SANS = '한국외대체 B', '한국외대체 M', '한국외대체 L', '맑은 고딕'


def rpr(font, sz, bold=False):
    f = '<w:rFonts w:ascii="{0}" w:eastAsia="{0}" w:hAnsi="{0}" w:cs="{0}"/>'.format(font)
    b = '<w:b/><w:bCs/>' if bold else ''
    return '<w:rPr>%s%s<w:color w:val="000000"/><w:sz w:val="%d"/><w:szCs w:val="%d"/></w:rPr>' % (f, b, sz, sz)


def para(text='', font=SANS, sz=22, jc='center', before=0, after=0, line=240, extra_ppr='', bold=False, runs_xml=None):
    ppr = '<w:pPr>%s<w:spacing w:before="%d" w:after="%d" w:line="%d" w:lineRule="auto"/><w:jc w:val="%s"/></w:pPr>' % (
        extra_ppr, before, after, line, jc)
    if runs_xml is None:
        parts = text.split('\n') if text else []
        runs_xml = ''
        for i, t in enumerate(parts):
            if i:
                runs_xml += '<w:r>%s<w:br/></w:r>' % rpr(font, sz, bold)
            runs_xml += '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % (rpr(font, sz, bold), escape(t))
    return '<w:p>%s%s</w:p>' % (ppr, runs_xml)


def blank(n):
    return ''.join(para(line=360) for _ in range(n))


def rule(pos):
    return para(line=120, extra_ppr='<w:pBdr><w:%s w:val="thickThinMediumGap" w:sz="24" w:space="1" w:color="1F3864"/></w:pBdr>' % pos)


EMU_MM = 36000
size = 125 * EMU_MM
watermark = (
    '<w:p><w:pPr><w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/></w:pPr><w:r><w:drawing>'
    '<wp:anchor distT="0" distB="0" distL="0" distR="0" simplePos="0" relativeHeight="0" behindDoc="1" locked="0" layoutInCell="1" allowOverlap="1">'
    '<wp:simplePos x="0" y="0"/>'
    '<wp:positionH relativeFrom="page"><wp:align>center</wp:align></wp:positionH>'
    '<wp:positionV relativeFrom="page"><wp:posOffset>%d</wp:posOffset></wp:positionV>'
    '<wp:extent cx="%d" cy="%d"/><wp:effectExtent l="0" t="0" r="0" b="0"/><wp:wrapNone/>'
    '<wp:docPr id="9001" name="HUFS watermark"/><wp:cNvGraphicFramePr/>'
    '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
    '<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
    '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
    '<pic:nvPicPr><pic:cNvPr id="9001" name="hufs_watermark.png"/><pic:cNvPicPr/></pic:nvPicPr>'
    '<pic:blipFill><a:blip r:embed="rIdCoverMark"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
    '<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="%d" cy="%d"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
    '</pic:pic></a:graphicData></a:graphic></wp:anchor></w:drawing></w:r></w:p>'
) % (112 * EMU_MM, size, size, size, size)

INFO = [
    ('과 목', '빅데이터분석 (AI 기반 비즈니스 데이터 분석)'),
    ('담당교수', '박주원'),
    ('조', '14조'),
    ('팀 원', '정승엽(202103116), 박유진(202004229), 신효주(202404341)'),
    ('분석 자료', '교육부 대학알리미 중도탈락 학생 현황(대학, 학과별), 공공데이터포털 15164570'),
]
W1, W2 = 1700, 6900


def cell(w, text, head):
    shd = '<w:shd w:val="clear" w:color="auto" w:fill="D9E2F3"/>' if head else ''
    mar = '<w:tcMar><w:top w:w="80" w:type="dxa"/><w:left w:w="%d" w:type="dxa"/><w:bottom w:w="80" w:type="dxa"/><w:right w:w="100" w:type="dxa"/></w:tcMar>' % (100 if head else 160)
    p = para(text, font=SANS, sz=20, jc='center' if head else 'left', line=276, bold=head)
    return '<w:tc><w:tcPr><w:tcW w:w="%d" w:type="dxa"/>%s%s<w:vAlign w:val="center"/></w:tcPr>%s</w:tc>' % (w, shd, mar, p)


rows = ''.join('<w:tr><w:trPr><w:cantSplit/></w:trPr>%s%s</w:tr>' % (cell(W1, k, True), cell(W2, v, False)) for k, v in INFO)
table = (
    '<w:tbl><w:tblPr><w:tblW w:w="%d" w:type="dxa"/><w:jc w:val="center"/>'
    '<w:tblBorders><w:top w:val="single" w:sz="12" w:space="0" w:color="000000"/><w:left w:val="nil"/>'
    '<w:bottom w:val="single" w:sz="12" w:space="0" w:color="000000"/><w:right w:val="nil"/>'
    '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="808080"/><w:insideV w:val="single" w:sz="4" w:space="0" w:color="808080"/></w:tblBorders>'
    '<w:tblLayout w:type="fixed"/><w:tblLook w:val="0000" w:firstRow="0" w:lastRow="0" w:firstColumn="0" w:lastColumn="0" w:noHBand="0" w:noVBand="0"/></w:tblPr>'
    '<w:tblGrid><w:gridCol w:w="%d"/><w:gridCol w:w="%d"/></w:tblGrid>%s</w:tbl>'
) % (W1 + W2, W1, W2, rows)

body_sect = re.search(r'<w:sectPr\b.*?</w:sectPr>', doc, re.S).group(0)
pg = re.search(r'<w:pgSz [^>]*/><w:pgMar [^>]*/>', body_sect).group(0)
cover_sect = ('<w:sectPr><w:headerReference w:type="default" r:id="rIdCoverHdr"/>'
              '<w:footerReference w:type="default" r:id="rIdCoverFtr"/>%s<w:cols w:space="720"/><w:docGrid w:linePitch="360"/></w:sectPr>') % pg

cover = ''.join([
    watermark,
    blank(2),
    para('빅데이터분석 팀 프로젝트 주제 계획서', font=HM, sz=28, after=240, line=300),
    rule('top'),
    para('다음 학년도 중도탈락\n고위험 학과는 어디인가', font=HB, sz=56, before=360, after=200, line=360),
    para('학업지속 지원 대상 학과 선정을 위한\n대학알리미 학과별 중도탈락 패널(2023~2026) 분석 및 예측', font=HL, sz=28, before=60, after=360, line=300),
    rule('bottom'),
    blank(3),
    table,
    blank(2),
    para('2026. 11. 8.', font=HL, sz=26, after=120),
    # 마지막 문단에 표지 구역 나누기(sectPr)를 둠
    '<w:p><w:pPr><w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/><w:jc w:val="center"/>%s</w:pPr>'
    '<w:r>%s<w:t>14조</w:t></w:r></w:p>' % (cover_sect, rpr(HB, 34)),
])
doc = doc.replace('<w:body>', '<w:body>' + cover, 1)
# 마지막 표 뒤 빈 문단이 다음 쪽으로 넘어가 빈 쪽이 생기지 않도록 아주 작게(내용 변경 없음)
doc, n_tail = re.subn(r'(</w:tbl>)<w:p ([^>]*)/>(<w:sectPr)',
                      r'\1<w:p \2><w:pPr><w:spacing w:before="0" w:after="0" w:line="20" w:lineRule="exact"/>'
                      r'<w:rPr><w:sz w:val="2"/><w:szCs w:val="2"/></w:rPr></w:pPr></w:p>\3', doc)
assert n_tail == 1
assert '·' not in doc, '중간점 남음'

# 표지용 빈 머리글·바닥글, 그림 관계
ns = re.search(r'<w:hdr ([^>]*)>', files['word/header1.xml'].decode('utf-8')).group(1)
files['word/header_cover.xml'] = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:hdr %s><w:p/></w:hdr>' % ns).encode('utf-8')
files['word/footer_cover.xml'] = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:ftr %s><w:p/></w:ftr>' % ns).encode('utf-8')
files['word/media/hufs_watermark.png'] = open(MARK, 'rb').read()
rels = files['word/_rels/document.xml.rels'].decode('utf-8')
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/'
rels = rels.replace('</Relationships>',
                    '<Relationship Id="rIdCoverHdr" Type="%sheader" Target="header_cover.xml"/>'
                    '<Relationship Id="rIdCoverFtr" Type="%sfooter" Target="footer_cover.xml"/>'
                    '<Relationship Id="rIdCoverMark" Type="%simage" Target="media/hufs_watermark.png"/></Relationships>' % (R, R, R))
files['word/_rels/document.xml.rels'] = rels.encode('utf-8')
ct = files['[Content_Types].xml'].decode('utf-8')
if 'Extension="png"' not in ct:
    ct = ct.replace('<Types ', '<Types ', 1).replace('<Default ', '<Default Extension="png" ContentType="image/png"/><Default ', 1)
ct = ct.replace('</Types>',
                '<Override PartName="/word/header_cover.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/>'
                '<Override PartName="/word/footer_cover.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/></Types>')
files['[Content_Types].xml'] = ct.encode('utf-8')
files['word/document.xml'] = doc.encode('utf-8')

with zipfile.ZipFile(DST, 'w', zipfile.ZIP_DEFLATED) as z:
    order = ['[Content_Types].xml'] + [n for n in files if n != '[Content_Types].xml']
    for n in order:
        z.writestr(n, files[n])
print('written', DST, '| replacements', len(used))
