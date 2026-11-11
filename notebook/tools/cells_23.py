# 노트북 0·②·③ 실제 코드 셀 (make_nb_v2.py에서 import)

ENV = r'''# s0-01 환경·경로·스위치
import os, glob, platform, datetime
import numpy as np
import pandas as pd

pd.set_option('display.width', 200)
pd.set_option('display.max_columns', 60)
pd.set_option('display.max_rows', 200)

# 원자료 경로 후보: Colab 업로드(/content) → Drive → 로컬(notebook/ 기준 ../data/raw)
FNAME = '교육부_대학알리미_중도탈락 학생 현황 _대학_학과별_20260831.csv'
CANDIDATES = [f'/content/{FNAME}', f'/content/drive/MyDrive/{FNAME}', f'../data/raw/{FNAME}', f'data/raw/{FNAME}']
CANDIDATES += sorted(glob.glob('/content/*중도탈락*.csv')) + sorted(glob.glob('../data/raw/*중도탈락*.csv'))
CSV_PATH = next((p for p in CANDIDATES if os.path.exists(p)), None)
if CSV_PATH is None:
    raise FileNotFoundError('원자료 CSV를 찾지 못했습니다. Colab이면 왼쪽 파일 아이콘으로 CSV를 /content에 올려 주세요.')
if CSV_PATH.startswith('../'):
    PROC_DIR = '../data/processed'
elif CSV_PATH.startswith('data/'):
    PROC_DIR = 'data/processed'
else:
    PROC_DIR = '/content/processed'
FIG_DIR = 'figures'
os.makedirs(PROC_DIR, exist_ok=True)
os.makedirs(FIG_DIR, exist_ok=True)

# 고정값·되돌림 스위치 (logs/정제로그.md 표 6, 00_문제정의_가설.md와 이름 일치)
RANDOM_STATE = 42
SCOPE = 'general_day'            # 'general_day'(일반 대학 주간, 사전 고정) | 'all'(전체 표본, 민감도 ②)
MIN_ENROLL = 30                  # 직전연도 최소 재적(명), 민감도 10·50
MIN_ENROLL_SENS = [10, 30, 50]
HIGH_PCT = 75                    # 고위험 컷 백분위(상위 25%), 민감도 80·70
RATE_SOURCE = 'published'        # 공시 비율 사용(팀 결정 2026-11-11)
HUFS_CODE = 192                  # 한국외국어대학교 (사이버한국외국어대학교 332와 구분)
B_SUBFIELDS = ['기타유럽어・문학', '기타아시아어・문학']
B_SUBFIELDS_SENS = B_SUBFIELDS + ['국제지역학']   # 민감도 ①
TRAIN_T, TEST_T = [2024, 2025], 2026

print('실행 시각:', datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
print('Python', platform.python_version(), '| pandas', pd.__version__, '| numpy', np.__version__)
print('CSV_PATH =', CSV_PATH)
print('PROC_DIR =', PROC_DIR, '| FIG_DIR =', FIG_DIR)
'''

S2 = [
r'''# s2-01 출처 표기
# [출처 규칙] 이 셀의 수치를 보고서·발표에 옮길 때 '(출처: 노트북 §② 셀 s2-01)'를 붙인다.
SOURCE_INFO = {
    '데이터명': '교육부_대학알리미_중도탈락 학생 현황_대학_학과별',
    '제공처': '공공데이터포털 15164570 (https://www.data.go.kr/data/15164570/fileData.do)',
    '제공기관': '교육부 교육데이터정책과 (원 출처: 대학알리미 대학 정보공시)',
    '이용허락': '공공누리 제1유형 (출처 표시)',
    '포털 수정일 / 파일명 날짜': '2026-09-10 / 20260831',
    '다운로드일': '2026-11-08',
}
for k, v in SOURCE_INFO.items():
    print(f'{k:>16}: {v}')
''',
r'''# s2-02 원본 읽기
# [출처 규칙] '(출처: 노트북 §② 셀 s2-02)'
# 원본 df_raw는 이후 수정하지 않는다. 정제는 사본 df에서 한다.
df_raw = pd.read_csv(CSV_PATH, encoding='utf-8-sig')
print('행 × 열 =', df_raw.shape)
assert df_raw.shape == (56340, 32), '계획서 기준값(56,340×32)과 다름 → 원자료 버전을 확인'
''',
r'''# s2-03 공시연도별 행 수
# [출처 규칙] '(출처: 노트북 §② 셀 s2-03)'
year_n = df_raw['공시연도'].value_counts().sort_index()
print(year_n.to_string())
assert year_n.to_dict() == {2023: 14350, 2024: 13628, 2025: 13928, 2026: 14434}
print('\n공시연도 × 기준연도 (대부분 기준연도 = 공시연도 − 1, 일부 같은 해)')
print(pd.crosstab(df_raw['공시연도'], df_raw['기준연도']))
''',
r'''# s2-04 컬럼 개요와 측정 척도
# [출처 규칙] '(출처: 노트북 §② 셀 s2-04)'
SCALE = {'공시연도': '등간 또는 명목', '기준연도': '등간 또는 명목', '재적학생': '비율 척도(명)', '계': '비율 척도(명)',
         '중도탈락학생비율': '비율 척도(%)'}
REASONS = ['미등록', '미복학', '자퇴', '학사경고', '학생활동', '유급제적', '재학연한초과', '기타']
SCALE.update({c: '비율 척도(명)' for c in REASONS})
overview = pd.DataFrame({
    'dtype': df_raw.dtypes.astype(str),
    '고유값 수': df_raw.nunique(),
    '결측 수': df_raw.isna().sum(),
    '예시값': [df_raw[c].dropna().iloc[0] for c in df_raw.columns],
    '측정 척도': [SCALE.get(c, '명목') for c in df_raw.columns],
})
overview
''',
]

S3_TOOLS = r'''# s3-00 단계별 추적 도구
# [기준] 행 삭제 금지(표시 후 표본에서 제외), y(비율) 보정 금지, 건수는 코드 계산값만, 0행 필터는 멈춤(assert)
KEY = ['공시연도', '학교코드', '학과코드']
LOG = []          # 정제 처리 로그(정제로그 표 4): 처리·건수·근거·영향
TRACK = {}        # 단계별 추적표(정제로그 표 5)

def log(no, 처리, 건수, 근거, 영향):
    LOG.append({'#': no, '처리': 처리, '건수': 건수, '근거': 근거, '영향': 영향})

def make_flags(d):
    """이슈별 불리언 표. 값은 바꾸지 않는다."""
    f = pd.DataFrame(index=d.index)
    enr, cnt, rate = d['재적학생'], d['계'], d['중도탈락학생비율']
    recomputed = cnt / enr.where(enr > 0) * 100
    f['재적 = 0'] = enr.eq(0)
    f['재적 = 0 이면서 계 > 0'] = enr.eq(0) & cnt.gt(0)
    f['재적 = 0 인데 비율 기록됨(0%)'] = enr.eq(0) & rate.notna()
    f['계 > 재적 (재적 > 0)'] = enr.gt(0) & cnt.gt(enr)
    f['재계산 불일치 (> 0.01%p)'] = (rate - recomputed).abs().gt(0.01)
    f['사유합 ≠ 계'] = cnt.notna() & d[REASONS].sum(axis=1, min_count=1).ne(cnt)
    f['비율 결측'] = rate.isna()
    f['└ 계 결측'] = cnt.isna()
    f['└ 재적 0 (계 있음)'] = rate.isna() & cnt.notna() & enr.eq(0)
    f['폐교'] = d['학교상태'].eq('폐교')
    f['신설'] = d['학교상태'].eq('신설')
    f['소계열 N.C.E.'] = d['표준분류_소계열'].eq('N.C.E.')
    f['중계열 N.C.E'] = d['표준분류_중계열'].eq('N.C.E')
    return f

def rate_valid(d):
    """y로 쓸 수 있는 비율: 재적 > 0, 계·비율 존재 (공시값 그대로)"""
    return d['재적학생'].gt(0) & d['계'].notna() & d['중도탈락학생비율'].notna()

def track(stage, d):
    t = make_flags(d).sum().astype(int)
    TRACK[stage] = pd.concat([pd.Series({'(참고) 행 수': len(d)}), t])
    assert len(d) > 0, f'{stage}: 0행 — 조건을 의심할 것'
    return TRACK[stage]

df = df_raw.copy()     # 정제용 사본
track('① 원본 전체', df);
print('추적 도구 준비 완료. 이슈 항목 수:', len(TRACK['① 원본 전체']) - 1)
'''

S3_DIAG = [
r'''# s3-01 [완전성] 결측
# [출처 규칙] '(출처: 노트북 §③ 셀 s3-01)'
f0 = make_flags(df)
n_rate_na, n_cnt_na, n_z = f0['비율 결측'].sum(), f0['└ 계 결측'].sum(), f0['└ 재적 0 (계 있음)'].sum()
print(f'비율 결측 {n_rate_na:,} = 계 결측 {n_cnt_na:,} + 재적 0(계 있음) {n_z:,}')
assert (n_rate_na, n_cnt_na, n_z) == (6372, 5569, 803)
miss_by_year = (df.assign(비율결측=f0['비율 결측']).groupby('공시연도')['비율결측'].mean() * 100).round(1)
print('\n공시연도별 비율 결측률(%):'); print(miss_by_year.to_string())
''',
r'''# s3-02 [유일성] 중복
# [출처 규칙] '(출처: 노트북 §③ 셀 s3-02)'
n_full_dup = int(df.duplicated().sum())
n_key_dup = int(df.duplicated(KEY).sum())
print('완전 중복:', n_full_dup, '| 키(공시연도·학교코드·학과코드) 중복:', n_key_dup)
assert (n_full_dup, n_key_dup) == (0, 0)
''',
r'''# s3-03 [유효성] 재적 0, 계 > 재적
# [출처 규칙] '(출처: 노트북 §③ 셀 s3-03)'
cols = ['재적 = 0', '재적 = 0 이면서 계 > 0', '재적 = 0 인데 비율 기록됨(0%)', '계 > 재적 (재적 > 0)']
print(f0[cols].sum().to_string())
assert f0['재적 = 0'].sum() == 2500 and f0['재적 = 0 이면서 계 > 0'].sum() == 1497 and f0['계 > 재적 (재적 > 0)'].sum() == 172
over = df[f0['계 > 재적 (재적 > 0)']]
print(f"\n계 > 재적 172행 중 재적 5명 이하: {(over['재적학생'] <= 5).mean() * 100:.0f}%")
# 재적 0인데 비율이 0%로 기록된 행: 계 > 0인 행도 0%로 적혀 있어 y로 쓸 수 없다 → rate_valid()에서 제외
''',
r'''# s3-04 [정확성] 공시 비율 vs 계 ÷ 재적 × 100
# [출처 규칙] '(출처: 노트북 §③ 셀 s3-04)'
v = df[rate_valid(df)]
gap = (v['중도탈락학생비율'] - v['계'] / v['재적학생'] * 100).abs()
print(f'비교 가능 행: {len(v):,}')
print(f'최대 차이: {gap.max():.4f}%p | 0.01%p 초과: {(gap > 0.01).sum()}행 | 0.005%p 초과: {(gap > 0.005 + 1e-9).sum()}행')
assert gap.max() <= 0.0051, '반올림 수준을 넘는 차이 발견 → RATE_SOURCE 결정 재검토'
# 결론: 차이는 소수 둘째 자리 반올림 수준 → 공시값 사용(RATE_SOURCE='published').
# 계획서의 '68행'은 이 정의로 재현되지 않음(정의 차이로 추정) → 정제로그에 기록
''',
r'''# s3-05 [일관성] 사유합, 공백, 표준분류, 한국외대 코드 변동
# [출처 규칙] '(출처: 노트북 §③ 셀 s3-05)'
print('사유합 ≠ 계:', int(f0['사유합 ≠ 계'].sum()))
print('학과명 앞뒤 공백:', int((df['학과명'] != df['학과명'].str.strip()).sum()))

# 표준분류 일관성: 같은 학과명(공백 제거)이 5개교 이상에 있을 때 계열이 학교마다 갈리는가 (전체 원본 기준)
nm = df.assign(학과명s=df['학과명'].str.strip())
g = nm.groupby('학과명s').agg(학교수=('학교코드', 'nunique'), 중계열수=('표준분류_중계열', 'nunique'), 소계열수=('표준분류_소계열', 'nunique'))
g5 = g[g['학교수'] >= 5]
print(f"\n5개교 이상 학과명 {len(g5)}개 중 중계열 갈림 {(g5['중계열수'] > 1).sum()}개 ({(g5['중계열수'] > 1).mean() * 100:.0f}%), "
      f"소계열 갈림 {(g5['소계열수'] > 1).sum()}개 ({(g5['소계열수'] > 1).mean() * 100:.0f}%)")
n = len(df)
print(f"분류 불가 비율: 대계열 '광역계열' {df['표준분류_대계열'].eq('광역계열').mean() * 100:.1f}% (대계열에는 N.C.E. 값이 없음) | "
      f"중계열 N.C.E {f0['중계열 N.C.E'].mean() * 100:.1f}% | 소계열 N.C.E. {f0['소계열 N.C.E.'].mean() * 100:.1f}%")

# 국제지역학 포함 3개 소계열: 2개교 이상 학과명 중 소계열이 갈리는 것
names3 = nm.loc[nm['표준분류_소계열'].isin(B_SUBFIELDS_SENS), '학과명s'].unique()
g3 = nm[nm['학과명s'].isin(names3)].groupby('학과명s').agg(학교수=('학교코드', 'nunique'), 소계열수=('표준분류_소계열', 'nunique'))
g3 = g3[g3['학교수'] >= 2]
print(f"국제지역학 포함 3개 소계열: 2개교 이상 학과명 {len(g3)}개 중 소계열 갈림 {(g3['소계열수'] > 1).sum()}개")

# 한국외대
h = df[df['학교코드'] == HUFS_CODE]
print(f"\n한국외대 2026 공시 소계열 N.C.E.: {h[(h['공시연도'] == 2026) & (h['표준분류_소계열'] == 'N.C.E.')]['학과코드'].nunique()}개 학과")
c25 = set(h.loc[h['공시연도'] == 2025, '학과코드']); c26 = set(h.loc[h['공시연도'] == 2026, '학과코드'])
print(f'한국외대 학과코드 2025→2026: 신규 {len(c26 - c25)}, 소멸 {len(c25 - c26)}')
''',
r'''# s3-06 [적시성] 폐교·신설, 패널 연결 가능성 (전체 원본 기준)
# [출처 규칙] '(출처: 노트북 §③ 셀 s3-06)'
print('학교상태:', df['학교상태'].value_counts().to_dict())
yrs = df.groupby(['학교코드', '학과코드'])['공시연도'].nunique()
print('학과 수(학교코드·학과코드):', len(yrs), '| 4개년 모두 존재:', int((yrs == 4).sum()))
ok = df[rate_valid(df)][['공시연도', '학교코드', '학과코드']]
prev = ok.assign(공시연도=ok['공시연도'] + 1)
n_pairs = len(ok.merge(prev, on=KEY))
print('전년→당해 연결 쌍 (두 해 모두 재적 > 0, 비율 유효):', n_pairs)
'''
]

S3_STEPS = [
r'''# s3-11 ③-1 중복 (완전 중복 → 키 중복)
# [출처 규칙] '(출처: 노트북 §③ 셀 s3-11)'
assert df.duplicated().sum() == 0 and df.duplicated(KEY).sum() == 0
log(1, '완전 중복·키 중복 확인', '0 / 0', '안내문: 완전 중복 제거를 첫 단계로', '처리 없음 (제거할 행 없음)')
track('② 중복 확인 후', df);
print('중복 0건 → 처리 없음. 행 수', len(df))
''',
r'''# s3-12 ③-2 공백·표기
# [출처 규칙] '(출처: 노트북 §③ 셀 s3-12)'
df.columns = df.columns.str.strip()
str_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c]) or df[c].dtype == object]
changed = {c: int((df[c].notna() & (df[c] != df[c].str.strip())).sum()) for c in str_cols}
changed = {c: v for c, v in changed.items() if v}
for c in str_cols:
    df[c] = df[c].str.strip()
print('공백 제거한 셀:', changed)
assert len(df.columns) == 32
log(2, '컬럼명·문자열 공백 제거', sum(changed.values()), f'공백 셀 {changed}', '값 의미 변화 없음, groupby·필터 안정')
''',
r'''# s3-13 ③-3 타입 확인
# [출처 규칙] '(출처: 노트북 §③ 셀 s3-13)'
num_cols = ['공시연도', '기준연도', '학교코드', '학과코드', '재적학생', '계'] + REASONS + ['중도탈락학생비율']
before = df[num_cols].isna().sum().sum()
df[num_cols] = df[num_cols].apply(pd.to_numeric, errors='coerce')
after = df[num_cols].isna().sum().sum()
print('숫자 컬럼 결측 수: 변환 전', before, '→ 변환 후', after)
assert before == after, '변환으로 새 결측이 생김'
log(3, '숫자 타입 확인', f'{len(num_cols)}개 컬럼', '변환 전후 결측 수 동일', '처리 없음')
''',
r'''# s3-14 ③-4 논리 모순 표시 (삭제 금지)
# [출처 규칙] '(출처: 노트북 §③ 셀 s3-14)'
FL = make_flags(df)
for c in ['재적 = 0', '재적 = 0 이면서 계 > 0', '재적 = 0 인데 비율 기록됨(0%)', '계 > 재적 (재적 > 0)', '재계산 불일치 (> 0.01%p)', '사유합 ≠ 계']:
    df['flag_' + c] = FL[c]
print(FL[['재적 = 0', '재적 = 0 이면서 계 > 0', '재적 = 0 인데 비율 기록됨(0%)', '계 > 재적 (재적 > 0)', '재계산 불일치 (> 0.01%p)', '사유합 ≠ 계']].sum().to_string())
log(4, '재적 = 0 표시 → 표본 제외', int(FL['재적 = 0'].sum()), '비율 분모 0', '분석 표본에서 제외(행 유지)')
log(5, '재적 = 0 이면서 계 > 0 표시', int(FL['재적 = 0 이면서 계 > 0'].sum()), '분모·분자 모순. 이 중 비율이 0%로 기록된 행 포함', '재적 0 행은 모두 y로 쓰지 않음')
log(6, '계 > 재적(비율 100% 초과) 표시, 값 수정 안 함', int(FL['계 > 재적 (재적 > 0)'].sum()), '대부분 재적 5명 이하', '직전연도 최소 재적 30명으로 통제')
log(7, '공시 비율 vs 계÷재적 불일치 표시', int(FL['재계산 불일치 (> 0.01%p)'].sum()), '최대 차이 0.005%p(반올림). 계획서 68행은 재현 안 됨', '공시값 사용(팀 결정 2026-11-11)')
''',
r'''# s3-15 ③-5 결측 분해 (보정하지 않음)
# [출처 규칙] '(출처: 노트북 §③ 셀 s3-15)'
dec = pd.DataFrame({'비율 결측': FL['비율 결측'], '└ 계 결측': FL['└ 계 결측'], '└ 재적 0 (계 있음)': FL['└ 재적 0 (계 있음)']})
print(dec.groupby(df['공시연도']).sum().assign(행수=df.groupby('공시연도').size()).to_string())
assert FL['비율 결측'].sum() == FL['└ 계 결측'].sum() + FL['└ 재적 0 (계 있음)'].sum()
log(8, '비율 결측 분해 → 표본 제외', int(FL['비율 결측'].sum()), f"계 결측 {int(FL['└ 계 결측'].sum())} + 재적 0 {int(FL['└ 재적 0 (계 있음)'].sum())}", '보정 안 함(y 결측 대체 금지)')
''',
r'''# s3-16 ③-6 범위 확정 (일반 대학 주간)
# [출처 규칙] '(출처: 노트북 §③ 셀 s3-16)'
conds = [
    ("학교종류 == '대학교'", df['학교종류'].eq('대학교')),
    ("주야간구분 == '주간'", df['주야간구분'].eq('주간')),
    ("학과특성 == '일반과정'", df['학과특성'].eq('일반과정')),
    ("학교상태 != '폐교'", df['학교상태'].ne('폐교')),
]
rows, keep = [], pd.Series(True, index=df.index)
for name, c in conds:
    rows.append({'조건': name, '단독 기준 제외': int((~c).sum()), '순차 적용 시 추가 제외': int((keep & ~c).sum())})
    keep &= c
scope_tbl = pd.DataFrame(rows)
df['in_scope'] = keep
print(scope_tbl.to_string(index=False))
print('\n제외 값별 건수')
for col, val in [('학교종류', '대학교'), ('주야간구분', '주간'), ('학과특성', '일반과정')]:
    print(f'  {col}:', df.loc[df[col].ne(val), col].value_counts().to_dict())
n_scope = int(df['in_scope'].sum())
by_year = df[df['in_scope']].groupby('공시연도').size().to_dict()
n_sch = df.loc[df['in_scope'], '학교코드'].nunique()
print(f'\n범위 안: {n_scope:,}행 ({n_scope / len(df) * 100:.1f}%), {n_sch}개교, 연도별 {by_year}')
assert n_scope == 50081 and by_year == {2023: 12676, 2024: 12116, 2025: 12388, 2026: 12901} and n_sch == 210
log(9, '범위 확정: 일반 대학 주간 학과(in_scope 표시)', f'{len(df):,} → {n_scope:,}', '팀 결정 2026-11-11, 가설 문서 2절', '범위 밖은 민감도 ②에만 사용(행 유지)')
track('③ 범위 안 (일반 대학 주간)', df[df['in_scope']]);
''',
r'''# s3-17 ③-7 표준분류 N.C.E. 표시 (재분류 안 함)
# [출처 규칙] '(출처: 노트북 §③ 셀 s3-17)'
nce = pd.DataFrame({
    '범위 안': [int((df['in_scope'] & FL['중계열 N.C.E']).sum()), int((df['in_scope'] & FL['소계열 N.C.E.']).sum())],
    '범위 밖': [int((~df['in_scope'] & FL['중계열 N.C.E']).sum()), int((~df['in_scope'] & FL['소계열 N.C.E.']).sum())],
    '한국외대(범위 안)': [int((df['in_scope'] & FL['중계열 N.C.E'] & df['학교코드'].eq(HUFS_CODE)).sum()),
                     int((df['in_scope'] & FL['소계열 N.C.E.'] & df['학교코드'].eq(HUFS_CODE)).sum())],
}, index=['중계열 N.C.E', '소계열 N.C.E.'])
print(nce)
log(10, '표준분류 N.C.E.: 재분류 안 함', f"범위 안 소계열 {nce.loc['소계열 N.C.E.', '범위 안']}, 중계열 {nce.loc['중계열 N.C.E', '범위 안']}", '학교별 신고 의존(가설 문서 3절)', "'분류 불가' 범주로 유지, 소계열은 B 대상군 정의에만 사용")
''',
r'''# s3-18 ③-8 패널 연결 (범위 안, 전년 → 당해)
# [출처 규칙] '(출처: 노트북 §③ 셀 s3-18)'
# 두 해 모두 범위 안인 (학교코드, 학과코드)를 t−1 → t로 잇는다. 전년도 정보는 prev_ 접두어.
FEAT = ['학교명', '학교종류', '설립구분', '설립유형', '소재지유형', '지역', '학교상태', '학과명',
        '표준분류_대계열', '표준분류_중계열', '표준분류_소계열', '재적학생', '계', '중도탈락학생비율'] + REASONS

def build_pairs(d):
    d = d.assign(rate_ok=rate_valid(d))
    cur = d[['공시연도', '학교코드', '학과코드', 'in_scope', 'rate_ok'] + FEAT]
    prv = d[['공시연도', '학교코드', '학과코드', 'in_scope', 'rate_ok'] + FEAT].copy()
    prv['공시연도'] = prv['공시연도'] + 1
    prv = prv.rename(columns={c: 'prev_' + c for c in prv.columns if c not in KEY})
    return cur.merge(prv, on=KEY, how='inner')

pairs = build_pairs(df)                         # 전체 원본 기준 쌍 (민감도 ②용 포함)
pairs['both_in_scope'] = pairs['in_scope'] & pairs['prev_in_scope']
cur_scope = df[df['in_scope'] & df['공시연도'].ge(2024)]
n_link = int(pairs['both_in_scope'].sum())
print(f'결합 전: 범위 안 t=2024~2026 행 {len(cur_scope):,} → 결합 후(전년도도 범위 안): {n_link:,}쌍, 미연결 {len(cur_scope) - n_link:,}')
hufs_cur = cur_scope[cur_scope['학교코드'] == HUFS_CODE]
hufs_link = pairs[pairs['both_in_scope'] & pairs['학교코드'].eq(HUFS_CODE)]
print('한국외대 연도별 (당해 학과 수 / 연결된 학과 수):')
print(pd.DataFrame({'당해 학과': hufs_cur.groupby('공시연도').size(), '연결': hufs_link.groupby('공시연도').size()}).fillna(0).astype(int).to_string())
log(11, '패널 연결(두 해 모두 범위 안)', f'{len(cur_scope):,} → {n_link:,}쌍', '신설·코드 변경 학과는 전년도가 없어 자연 제외', '생존 편향을 한계로 명시')
n_h_un = len(hufs_cur) - len(hufs_link)
log(12, '한국외대 학과코드 미연결', n_h_un, '학부·전공 개편', 'B 예측 절 평가에서 제외하고 건수 공개, B 판정은 군 단위 풀링(연결 불필요)')
track('④ 연결 쌍 (당해 기준)', df.loc[df['in_scope']].merge(pairs.loc[pairs['both_in_scope'], KEY], on=KEY));
''',
r'''# s3-19 ③-9 분석 표본 확정 (+ 민감도 표본)
# [출처 규칙] '(출처: 노트북 §③ 셀 s3-19)'
def analysis_sample(p, min_enroll=MIN_ENROLL, scope=SCOPE):
    m = p['rate_ok'] & p['prev_rate_ok'] & p['prev_재적학생'].ge(min_enroll)
    if scope == 'general_day':
        m &= p['both_in_scope']
    return p[m].copy()

steps = pd.DataFrame([
    ('연결 쌍 (두 해 모두 범위 안)', int(pairs['both_in_scope'].sum())),
    ('+ 당해 비율 유효', int((pairs['both_in_scope'] & pairs['rate_ok']).sum())),
    ('+ 전년도 비율 유효', int((pairs['both_in_scope'] & pairs['rate_ok'] & pairs['prev_rate_ok']).sum())),
    (f'+ 전년도 재적 ≥ {MIN_ENROLL}명 = 분석 표본', len(analysis_sample(pairs))),
], columns=['단계', '쌍 수'])
print(steps.to_string(index=False))

sample = analysis_sample(pairs)
sens = {f'재적≥{k}': analysis_sample(pairs, k) for k in MIN_ENROLL_SENS}
sens['전체 표본(재적≥30)'] = analysis_sample(pairs, MIN_ENROLL, 'all')
split = sample.groupby('공시연도').size()
print('\n분석 표본 공시연도별:', split.to_dict(), f'| 학습(t=2024·2025) {split.loc[TRAIN_T].sum():,} / 테스트(t=2026) {split.loc[TEST_T]:,}')
print('민감도 표본 크기:', {k: len(v) for k, v in sens.items()})
for k, v in sens.items():
    assert len(v) > 0, k
log(13, f'직전연도 재적 ≥ {MIN_ENROLL}명, 두 해 비율 유효', f'{n_link:,} → {len(sample):,}쌍', '사전 고정 설계(소규모 비율 변동 통제)', '민감도: 재적 10·50, 전체 표본')
smp_rows = df.merge(sample[KEY], on=KEY)
track('⑤ 분석 표본 (재적≥30)', smp_rows)
track('민감도 (재적≥10)', df.merge(sens['재적≥10'][KEY], on=KEY))
track('민감도 (재적≥50)', df.merge(sens['재적≥50'][KEY], on=KEY));
''',
r'''# s3-20 ③-10 손대지 않는 것 · 최종 점검 · 추적표
# [출처 규칙] '(출처: 노트북 §③ 셀 s3-20 = 정제로그 표 4·5)'
assert len(df) == len(df_raw), '행이 지워졌음 — 표시 후 제외 원칙 위반'
assert (df['중도탈락학생비율'].fillna(-1) == df_raw['중도탈락학생비율'].fillna(-1)).all(), 'y 값이 바뀌었음 — 보정 금지 위반'
assert sample['prev_재적학생'].min() >= MIN_ENROLL and sample['both_in_scope'].all()
assert not sample[['중도탈락학생비율', 'prev_중도탈락학생비율']].isna().any().any()
print('최종 점검 통과: 원본 행 수 유지, y 값 무변경, 표본 조건 충족\n')
track_tbl = pd.DataFrame(TRACK)
print('■ 단계별 추적표 (정제로그 표 5)'); display(track_tbl)
print('■ 정제 처리 로그 (정제로그 표 4)'); display(pd.DataFrame(LOG))
''',
]

S3_SAVE = r'''# s3-21 정제 결과 저장 (코드로만 생성, 수동 편집 금지)
# [출처 규칙] '(출처: 노트북 §③ 셀 s3-21)'
df.to_csv(f'{PROC_DIR}/rows_flagged.csv', index=False, encoding='utf-8-sig')       # 전체 행 + 표시 컬럼 + in_scope
pairs.to_csv(f'{PROC_DIR}/pairs_all.csv', index=False, encoding='utf-8-sig')        # 전년→당해 쌍 (전체, 범위 표시)
pd.DataFrame(LOG).to_csv(f'{PROC_DIR}/cleaning_log.csv', index=False, encoding='utf-8-sig')
track_tbl.to_csv(f'{PROC_DIR}/cleaning_track.csv', encoding='utf-8-sig')
for f in sorted(os.listdir(PROC_DIR)):
    print(f, os.path.getsize(f'{PROC_DIR}/{f}') // 1024, 'KB')
'''
