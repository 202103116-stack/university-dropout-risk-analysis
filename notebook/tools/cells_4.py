# 노트북 ④ 분석 + 부록 E 실제 코드 셀

S4_COMMON = r'''# s4-00 분석 공통 도구
# [출처 규칙] 이 절의 수치는 '(출처: 노트북 §④ 셀 s4-NN)'으로 옮긴다.
# 규칙: 무작위 분할 금지(학습 t=2024·2025, 테스트 t=2026), 고위험 컷은 학습 데이터로만, 당해 계·사유·비율은 설명 변수 금지,
#       설명 변수는 전년도(prev_) 값만 사용. 소계열은 설명 변수로 쓰지 않음(B 대상군 정의 전용).
import warnings
import statsmodels.formula.api as smf
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, confusion_matrix
warnings.filterwarnings('ignore', category=FutureWarning)

FIELD_REF = '인문사회계열'

def prep(s, pct=HIGH_PCT):
    """분석 표본 → 모델용 표. y 컷과 재적 구간 경계는 학습 데이터(t=2024·2025)로만 정한다."""
    s = s.copy()
    tr = s['공시연도'].isin(TRAIN_T)
    cut = np.percentile(s.loc[tr, '중도탈락학생비율'], pct)
    q = np.quantile(s.loc[tr, 'prev_재적학생'], [0.25, 0.5, 0.75])
    s['y'] = (s['중도탈락학생비율'] >= cut).astype(int)
    s['prev_high'] = (s['prev_중도탈락학생비율'] >= cut).astype(int)          # 기준선 ②
    s['priv'] = s['prev_설립유형'].eq('사립').astype(int)
    s['nonmetro'] = s['prev_소재지유형'].eq('비수도권').astype(int)
    s['field'] = s['prev_표준분류_대계열']
    s['size_q'] = pd.cut(s['prev_재적학생'], [-np.inf, *q, np.inf], labels=['Q1', 'Q2', 'Q3', 'Q4'])
    s['prev_rate'] = s['prev_중도탈락학생비율']
    s['school'] = s['학교코드']
    return s, cut, q

FORMULA_A = f"y ~ priv + nonmetro + C(field, Treatment('{FIELD_REF}')) + C(size_q, Treatment('Q4'))"

def fit_A(m):
    """가설 A 판정 모델: 구조 변수만(전년도 탈락률 제외). 학교 단위 군집 표준오차(같은 학교 학과는 독립이 아님)."""
    # 의학계열은 고위험 쌍이 0이라 계수가 −∞로 가는 '완전 분리'가 생긴다 → 수렴 경고는 s4-05의 진단 추정으로 대신 확인
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        res = smf.logit(FORMULA_A, data=m).fit(disp=0, maxiter=200, cov_type='cluster', cov_kwds={'groups': m['school']})
    with np.errstate(over='ignore'):
        ci = np.exp(res.conf_int())
        tab = pd.DataFrame({'오즈비': np.exp(res.params), 'CI 하한': ci[0], 'CI 상한': ci[1], 'p': res.pvalues})
    return res, tab

def judge_A(tab):
    ok = {v: (tab.loc[v, '오즈비'] > 1) and (tab.loc[v, 'CI 하한'] > 1) for v in ['priv', 'nonmetro']}
    return {2: '맞음', 1: '부분 맞음', 0: '기각'}[sum(ok.values())], ok

def X_of(m, with_prev, cols=None):
    X = pd.get_dummies(m[['field', 'size_q']].astype(str), drop_first=False).astype(float)
    X['priv'], X['nonmetro'] = m['priv'], m['nonmetro']
    if with_prev:
        X['prev_rate'] = m['prev_rate']
    return X if cols is None else X.reindex(columns=cols, fill_value=0.0)

def fit_pred(m_tr, with_prev):
    X = X_of(m_tr, with_prev)
    clf = LogisticRegression(max_iter=5000, random_state=RANDOM_STATE).fit(X, m_tr['y'])
    return clf, list(X.columns)

def at_k(y, score, k):
    """점수 상위 k개를 지원했을 때: 맞힌 수, 정밀도(%), 재현율(%)"""
    order = np.argsort(-np.asarray(score, dtype=float), kind='stable')[:k]
    hits = int(np.asarray(y)[order].sum())
    return hits, hits / k * 100 if k else np.nan, hits / max(int(np.sum(y)), 1) * 100

def evaluate(m, cols_by_model, models, k=None):
    """테스트 표에서 모델 2개 + 기준선 2개를 같은 k로 비교"""
    y = m['y'].values
    k = int(m['prev_high'].sum()) if k is None else k        # k = 기준선 ②가 고른 학과 수
    rows = []
    for name, (clf, cols, with_prev) in models.items():
        p = clf.predict_proba(X_of(m, with_prev, cols))[:, 1]
        h, pr, rc = at_k(y, p, k)
        rows.append({'방법': name, 'k': k, '맞힌 학과 수': h, '정밀도(%)': pr, '재현율(%)': rc, 'AUC': roc_auc_score(y, p) if len(set(y)) > 1 else np.nan})
    h = int((m['prev_high'].values * y).sum())
    rows.append({'방법': '기준선 ② 전년도 고위험 지속', 'k': k, '맞힌 학과 수': h, '정밀도(%)': h / k * 100 if k else np.nan,
                 '재현율(%)': h / max(y.sum(), 1) * 100, 'AUC': roc_auc_score(y, m['prev_high']) if len(set(y)) > 1 else np.nan})
    rows.append({'방법': "기준선 ① 전원 '고위험 아님'", 'k': 0, '맞힌 학과 수': 0, '정밀도(%)': np.nan, '재현율(%)': 0.0, 'AUC': 0.5})
    return pd.DataFrame(rows)

print('공통 도구 준비 완료')
'''

S4 = [
r'''# s4-01 EDA: 분석 표본의 재적·탈락 분포 (절대 = 인원(명), 비중 = 비율(%))
# [출처 규칙] '(출처: 노트북 §④ 셀 s4-01)'
eda = sample[['재적학생', '계', '중도탈락학생비율', 'prev_재적학생']].describe(percentiles=[.25, .5, .75, .9]).T.round(2)
eda.index = ['당해 재적(명)', '당해 탈락 인원(명)', '당해 탈락률(%)', '전년도 재적(명)']
display(eda)
print('탈락 인원(명)과 탈락률(%)의 스피어만 상관:', round(sample['계'].corr(sample['중도탈락학생비율'], method='spearman'), 3))
print('공시연도별 표본 쌍 수:', sample.groupby('공시연도').size().to_dict())
''',
r'''# s4-02 y 정의: 고위험 = 당해 탈락률이 학습기간 75백분위 이상 (컷은 학습 데이터로만)
# [출처 규칙] '(출처: 노트북 §④ 셀 s4-02)'
M, CUT, QB = prep(sample)
TR, TE = M[M['공시연도'].isin(TRAIN_T)], M[M['공시연도'].eq(TEST_T)]
print(f'고위험 컷 = {CUT:.2f}% (학습 t=2024·2025, {HIGH_PCT}백분위)')
print('전년도 재적 구간 경계(명, 학습 기준 25·50·75%):', np.round(QB, 1).tolist(), '→ Q1이 소규모(하위 25%)')
print(f"고위험 비율: 학습 {TR['y'].mean() * 100:.1f}% | 테스트 {TE['y'].mean() * 100:.1f}%")
print(f"전년도 고위험(기준선 ②) 학과 수: 테스트 {int(TE['prev_high'].sum())}개 → 이것이 k")
''',
r'''# s4-03 기술통계 (가설 A, 예측 아님): 설립유형 × 수도권 4칸, 시·도 순위 — 분석 표본 전체(t=2024~2026)
# [출처 규칙] '(출처: 노트북 §④ 셀 s4-03)'
four = M.pivot_table(index='prev_설립유형', columns='prev_소재지유형', values='y', aggfunc=['mean', 'size'])
four_pct = (four['mean'] * 100).round(1); four_n = four['size']
print('고위험 비율(%)'); display(four_pct)
print('쌍 수'); display(four_n)
sido = M.groupby('prev_지역').agg(고위험비율=('y', lambda v: v.mean() * 100), 쌍수=('y', 'size'), 학교수=('school', 'nunique')).sort_values('고위험비율', ascending=False).round(1)
display(sido)
''',
r'''# s4-04 설명 변수 목록과 누수 점검
# [출처 규칙] '(출처: 노트북 §④ 셀 s4-04)'
FEATURES = {'priv': '전년도 설립유형 == 사립', 'nonmetro': '전년도 소재지유형 == 비수도권', 'field': '전년도 표준분류 대계열',
            'size_q': '전년도 재적 구간(학습 기준 4분위)', 'prev_rate': '전년도 탈락률(예측 성능용 모델에만)'}
for k_, v_ in FEATURES.items():
    print(f'{k_:>9}: {v_}')
src_cols = ['prev_설립유형', 'prev_소재지유형', 'prev_표준분류_대계열', 'prev_재적학생', 'prev_중도탈락학생비율']
LEAK = ['계', '중도탈락학생비율', '재적학생'] + REASONS          # 당해(t) 값
assert all(c.startswith('prev_') for c in src_cols) and not set(src_cols) & set(LEAK)
Xchk = X_of(TR, True)
assert not any(c in LEAK for c in Xchk.columns), '당해 변수가 설명 변수에 들어감'
print('\n누수 점검 통과: 설명 변수는 모두 전년도(t−1) 값. 당해 계·사유·비율·재적 미사용')
''',
r'''# s4-05 가설 A 판정: 구조 변수 로지스틱 회귀 (분석 표본 t=2024~2026, 학교 군집 표준오차)
# [출처 규칙] '(출처: 노트북 §④ 셀 s4-05)'
resA, tabA = fit_A(M)
verdict_A, okA = judge_A(tabA)
show = tabA.rename(index={'priv': '사립 (vs 국공립)', 'nonmetro': '비수도권 (vs 수도권)'}).round(3)
# 대계열 기준 = 인문사회계열, 재적 구간 기준 = Q4(대규모). Q1 오즈비 = 소규모 학과의 고위험 오즈 배수
display(show)
print(f"쌍 {int(resA.nobs):,}개, 학교 {M['school'].nunique()}개 군집")
print(f"사립 OR {tabA.loc['priv', '오즈비']:.2f} [{tabA.loc['priv', 'CI 하한']:.2f}, {tabA.loc['priv', 'CI 상한']:.2f}] → {'충족' if okA['priv'] else '미충족'}")
print(f"비수도권 OR {tabA.loc['nonmetro', '오즈비']:.2f} [{tabA.loc['nonmetro', 'CI 하한']:.2f}, {tabA.loc['nonmetro', 'CI 상한']:.2f}] → {'충족' if okA['nonmetro'] else '미충족'}")
print(f'▶ 가설 A 판정: {verdict_A}')
# 진단: 의학계열 완전 분리 — 고위험 쌍이 0개라 오즈비가 0으로 수렴. 의학계열 행을 뺀 추정과 사립·비수도권 오즈비를 비교한다.
med = M['field'].eq('의학계열')
print(f"\n[진단] 의학계열 쌍 {int(med.sum())}개 중 고위험 {int(M.loc[med, 'y'].sum())}개 → 완전 분리(수렴 경고 원인)")
_, tab_nomed = fit_A(M[~med])
print('[진단] 의학계열 제외 시 — 사립 OR', round(tab_nomed.loc['priv', '오즈비'], 2), np.round(tab_nomed.loc['priv', ['CI 하한', 'CI 상한']].values.astype(float), 2),
      '/ 비수도권 OR', round(tab_nomed.loc['nonmetro', '오즈비'], 2), np.round(tab_nomed.loc['nonmetro', ['CI 하한', 'CI 상한']].values.astype(float), 2),
      '→ 판정', judge_A(tab_nomed)[0])
# 참고: 군집을 무시한 일반 표준오차로 보면 구간이 얼마나 좁아지는가 (학교 단위 변수라 과신 위험)
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    naive = smf.logit(FORMULA_A, data=M).fit(disp=0, maxiter=200)
    nci = np.exp(naive.conf_int())
print('\n[참고] 군집 무시 시 95% CI — 사립', np.round(nci.loc['priv'].values, 2), '/ 비수도권', np.round(nci.loc['nonmetro'].values, 2))
resA_tr, tabA_tr = fit_A(TR)
print('[참고] 학습 기간(t=2024·2025)만으로 추정 — 판정:', judge_A(tabA_tr)[0],
      '| 사립 OR', round(tabA_tr.loc['priv', '오즈비'], 2), '/ 비수도권 OR', round(tabA_tr.loc['nonmetro', '오즈비'], 2))
''',
r'''# s4-06 예측 절: 모델 2개 학습 (학습 t=2024·2025)
# [출처 규칙] '(출처: 노트북 §④ 셀 s4-06)'
clf_s, cols_s = fit_pred(TR, with_prev=False)
clf_p, cols_p = fit_pred(TR, with_prev=True)
MODELS = {'모델 1 구조 변수': (clf_s, cols_s, False), '모델 2 구조 + 전년도 탈락률': (clf_p, cols_p, True)}
coef = pd.Series(clf_p.coef_[0], index=cols_p).round(3)
print('모델 2 계수(참고, 정규화 로지스틱):'); print(coef.to_string())
''',
r'''# s4-07 예측 절 평가표: 같은 k(= 기준선 ②가 고른 학과 수)에서 정밀도·재현율 (테스트 t=2026)
# [출처 규칙] '(출처: 노트북 §④ 셀 s4-07)'
EVAL = evaluate(TE, None, MODELS)
K = int(EVAL.loc[0, 'k'])
display(EVAL.round(2))
best = EVAL.iloc[:2].sort_values('정밀도(%)', ascending=False).iloc[0]
b2 = EVAL.iloc[2]
print(f"k = {K}개 학과를 지원할 때: {best['방법']} 정밀도 {best['정밀도(%)']:.1f}% vs 기준선 ② {b2['정밀도(%)']:.1f}% "
      f"(차이 {best['정밀도(%)'] - b2['정밀도(%)']:+.1f}%p, 맞힌 학과 {int(best['맞힌 학과 수']) - int(b2['맞힌 학과 수']):+d}개)")
print(f"테스트 고위험 학과 {int(TE['y'].sum())}개, 기준선 ① 정확도 {(1 - TE['y'].mean()) * 100:.1f}% (아무도 지원하지 않음 — 재현율 0%)")
''',
r'''# s4-08 오차 확인: 혼동행렬 (k 기준, 임계값 0.5 기준)
# [출처 규칙] '(출처: 노트북 §④ 셀 s4-08)'
p2 = clf_p.predict_proba(X_of(TE, True, cols_p))[:, 1]
sel_k = np.zeros(len(TE), int); sel_k[np.argsort(-p2, kind='stable')[:K]] = 1
for name, pred in [('모델 2 · 상위 k', sel_k), ('모델 2 · 임계값 0.5', (p2 >= 0.5).astype(int)), ('기준선 ②', TE['prev_high'].values)]:
    tn, fp, fn, tp = confusion_matrix(TE['y'], pred, labels=[0, 1]).ravel()
    print(f'{name:>14}: 지원 {tp + fp:>5} | 맞힘(TP) {tp:>5} | 헛지원(FP) {fp:>5} | 놓침(FN) {fn:>5} | 정확도 {(tp + tn) / len(pred) * 100:.1f}%')
''',
r'''# s4-09 가설 B 대상군 정의와 집계 표 (한국외대, 범위 안, 공시 2024~2026, 비율 유효 행)
# [출처 규칙] '(출처: 노트북 §④ 셀 s4-09)'
YRS_B = [2024, 2025, 2026]
base_rows = df[df['in_scope'] & df['공시연도'].isin(YRS_B) & rate_valid(df)].copy()
H = base_rows[base_rows['학교코드'].eq(HUFS_CODE)].copy()
H['target'] = H['표준분류_소계열'].isin(B_SUBFIELDS)
cnt_tbl = H.groupby(['공시연도', 'target']).agg(학과수=('학과코드', 'nunique'), 재적합=('재적학생', 'sum'), 탈락합=('계', 'sum')).unstack('target')
display(cnt_tbl)
print('대상군 학과 수(연도별):', H[H['target']].groupby('공시연도')['학과코드'].nunique().to_dict())
''',
r'''# s4-10 가설 B 판정: 대상군 vs 교내 다른 학과, 합산 비율 차이와 학과코드 부트스트랩 95% 구간
# [출처 규칙] '(출처: 노트북 §④ 셀 s4-10)'
def pooled(d):
    return d['계'].sum() / d['재적학생'].sum() * 100

def boot_diff(a, b, n=2000, seed=RANDOM_STATE):
    """학과코드 단위로 각 군을 따로 복원추출해 (합산 비율 a − b)의 분포를 만든다"""
    rng = np.random.default_rng(seed)
    ga = {k: v[['계', '재적학생']].sum().values for k, v in a.groupby('학과코드')}
    gb = {k: v[['계', '재적학생']].sum().values for k, v in b.groupby('학과코드')}
    A_, B_ = np.array(list(ga.values())), np.array(list(gb.values()))
    out = np.empty(n)
    for i in range(n):
        sa = A_[rng.integers(0, len(A_), len(A_))].sum(0); sb = B_[rng.integers(0, len(B_), len(B_))].sum(0)
        out[i] = sa[0] / sa[1] * 100 - sb[0] / sb[1] * 100
    return np.percentile(out, [2.5, 97.5])

def run_B(H_, subfields):
    t_ = H_['표준분류_소계열'].isin(subfields)
    a, b = H_[t_], H_[~t_]
    lo, hi = boot_diff(a, b)
    d_ = pooled(a) - pooled(b)
    return {'대상군 합산 비율(%)': pooled(a), '교내 다른 학과(%)': pooled(b), '차이(%p)': d_, '95% 하한': lo, '95% 상한': hi,
            '대상군 학과코드 수': a['학과코드'].nunique(), '다른 학과코드 수': b['학과코드'].nunique(),
            '판정': '맞음' if (d_ > 0 and lo > 0) else '기각'}

resB = run_B(H, B_SUBFIELDS)
display(pd.Series(resB).to_frame('가설 B'))
verdict_B = resB['판정']
print(f"▶ 가설 B 판정: {verdict_B} (차이 {resB['차이(%p)']:+.2f}%p, 95% 구간 [{resB['95% 하한']:.2f}, {resB['95% 상한']:.2f}])")
seeds = {s_: np.round(boot_diff(H[H['target']], H[~H['target']], seed=s_), 2).tolist() for s_ in [42, 1, 2, 3]}
print('시드별 95% 구간(재현성 확인):', seeds)
''',
r'''# s4-11 B 보조 분석: 대상군 안에서 소규모(전년도 재적 하위 25%)가 더 높은가 — 재적 대리 지표, 판정 없음
# [출처 규칙] '(출처: 노트북 §④ 셀 s4-11)'
hp = pairs[pairs['both_in_scope'] & pairs['학교코드'].eq(HUFS_CODE) & pairs['공시연도'].isin(YRS_B) & pairs['rate_ok']
           & pairs['표준분류_소계열'].isin(B_SUBFIELDS)].copy()
q25 = hp['prev_재적학생'].quantile(0.25)
hp['small'] = hp['prev_재적학생'] <= q25
sm = hp.groupby('small').apply(lambda g: pd.Series({'쌍 수': len(g), '학과코드 수': g['학과코드'].nunique(), '합산 비율(%)': pooled(g)}), include_groups=False)
sm.index = sm.index.map({True: f'소규모(전년도 재적 ≤ {q25:.0f}명)', False: '나머지'})
display(sm.round(2))
''',
r'''# s4-12 B 참고 해석 (가설 아님): 한국외대 대상군 vs 전국(한국외대 제외) 같은 소계열
# [출처 규칙] '(출처: 노트북 §④ 셀 s4-12)'
NAT = base_rows[~base_rows['학교코드'].eq(HUFS_CODE) & base_rows['표준분류_소계열'].isin(B_SUBFIELDS)]
HT = H[H['target']]
lo, hi = boot_diff(HT, NAT)
d_nat = pooled(HT) - pooled(NAT)
phrase = ('비슷함 → 학교 고유 문제가 아니라 분야 전반의 구조' if lo <= 0 <= hi else
          ('한국외대가 더 높음 → 학교 고유 요인이 있음' if lo > 0 else '한국외대가 더 낮음 → 교내에선 높아도 전국 수준보다는 양호함'))
print(f"한국외대 대상군 {pooled(HT):.2f}% vs 전국 같은 소계열 {pooled(NAT):.2f}% "
      f"(비교군 {NAT['학교코드'].nunique()}개교, 학과코드 {NAT['학과코드'].nunique()}개)")
print(f'차이 {d_nat:+.2f}%p, 95% 구간 [{lo:.2f}, {hi:.2f}] → 미리 고정한 문구: {phrase}')
''',
r'''# s4-13 B 안의 예측 절 (보조 참고): ① t=2026 테스트의 한국외대 학과 검증 ② 2026 공시로 다음 해 우선 지원 후보
# [출처 규칙] '(출처: 노트북 §④ 셀 s4-13)'
TE_H = TE[TE['학교코드'].eq(HUFS_CODE)]
k_h = int(TE_H['prev_high'].sum())
print(f'한국외대 테스트 학과 {len(TE_H)}개(연결·표본 조건 충족), 미연결로 평가 제외 {len(hufs_cur[hufs_cur["공시연도"] == 2026]) - len(TE_H)}개, k = {k_h}')
EVAL_H = evaluate(TE_H, None, MODELS, k=k_h) if k_h > 0 else None
if EVAL_H is not None:
    display(EVAL_H.round(2))

# 다음 해(공시 2027) 후보: 모델 2를 분석 표본 전체(t=2024~2026)로 다시 학습하고, 2026 공시 행을 '전년도'로 넣어 점수를 낸다.
clf_all, cols_all = fit_pred(M, with_prev=True)
cur26 = df[df['in_scope'] & df['공시연도'].eq(2026) & df['학교코드'].eq(HUFS_CODE) & rate_valid(df) & df['재적학생'].ge(MIN_ENROLL)].copy()
nx = pd.DataFrame({'priv': cur26['설립유형'].eq('사립').astype(int), 'nonmetro': cur26['소재지유형'].eq('비수도권').astype(int),
                   'field': cur26['표준분류_대계열'], 'prev_rate': cur26['중도탈락학생비율'],
                   'size_q': pd.cut(cur26['재적학생'], [-np.inf, *QB, np.inf], labels=['Q1', 'Q2', 'Q3', 'Q4'])})
cur26['고위험 점수'] = clf_all.predict_proba(X_of(nx, True, cols_all))[:, 1]
cur26['2026 고위험'] = cur26['중도탈락학생비율'] >= CUT
cur26['비주류 외국어 학과군'] = cur26['표준분류_소계열'].isin(B_SUBFIELDS)
k_next = int(cur26['2026 고위험'].sum())
CAND = cur26.sort_values('고위험 점수', ascending=False).head(k_next)
print(f'\n공시 2027 우선 지원 후보 상위 k = {k_next}개 (k = 2026 공시 고위험 학과 수, 재적 ≥ {MIN_ENROLL}명)')
display(CAND[['학과명', '표준분류_소계열', '재적학생', '계', '중도탈락학생비율', '고위험 점수', '비주류 외국어 학과군']].round(3).reset_index(drop=True))
unit = CAND['학과명'].str.contains('통합모집|계열|자유전공|융합대학') | CAND['표준분류_소계열'].eq('N.C.E.')
print(f"후보 {k_next}개 중 통합모집·계열·자유전공 등 전공 배정 전 단위 또는 소계열 N.C.E.: {int(unit.sum())}개 | 비주류 외국어 학과군: {int(CAND['비주류 외국어 학과군'].sum())}개")
''',
r'''# s4-14 민감도 ①~⑤ (사전 고정) — 결론이 뒤집히는지 한 표로
# [출처 규칙] '(출처: 노트북 §④ 셀 s4-14)'
def run_all(s, pct=HIGH_PCT):
    m, cut, _ = prep(s, pct)
    tr, te = m[m['공시연도'].isin(TRAIN_T)], m[m['공시연도'].eq(TEST_T)]
    _, tab = fit_A(m)
    v, _ = judge_A(tab)
    cs, ccs = fit_pred(tr, False); cp, ccp = fit_pred(tr, True)
    ev = evaluate(te, None, {'s': (cs, ccs, False), 'p': (cp, ccp, True)})
    return {'쌍 수': len(m), '컷(%)': cut, 'A 판정': v, '사립 OR': tab.loc['priv', '오즈비'], '사립 CI하한': tab.loc['priv', 'CI 하한'],
            '비수도권 OR': tab.loc['nonmetro', '오즈비'], '비수도권 CI하한': tab.loc['nonmetro', 'CI 하한'], 'k': int(ev.loc[0, 'k']),
            '모델1 정밀도': ev.loc[0, '정밀도(%)'], '모델2 정밀도': ev.loc[1, '정밀도(%)'], '기준선② 정밀도': ev.loc[2, '정밀도(%)']}

SENS = {'기본 (재적≥30, 상위 25%)': run_all(sample)}
SENS['③ 재적≥10'] = run_all(sens['재적≥10'])
SENS['③ 재적≥50'] = run_all(sens['재적≥50'])
SENS['④ 고위험 상위 20%'] = run_all(sample, 80)
SENS['④ 고위험 상위 30%'] = run_all(sample, 70)
SENS['② 전체 표본(사이버·산업·야간 등 포함)'] = run_all(sens['전체 표본(재적≥30)'])
SENS_T = pd.DataFrame(SENS).T
display(SENS_T.round(2))

b_sens = run_B(H, B_SUBFIELDS_SENS)
print(f"① B 대상군 + 국제지역학: 차이 {b_sens['차이(%p)']:+.2f}%p [{b_sens['95% 하한']:.2f}, {b_sens['95% 상한']:.2f}] → {b_sens['판정']} (기본: {verdict_B})")

# ⑤ k 기준 vs 임계값 0.5 / k를 바꿔 가며 정밀도 (차트 s5-c13 데이터)
p1 = clf_s.predict_proba(X_of(TE, False, cols_s))[:, 1]
print(f"⑤ 임계값 0.5: 모델 2가 고른 학과 {int((p2 >= 0.5).sum())}개, 정밀도 {TE['y'].values[p2 >= 0.5].mean() * 100:.1f}% "
      f"/ k 기준({K}개): {EVAL.loc[1, '정밀도(%)']:.1f}%")
KS = sorted(set([50, 100, 200, 400, 600, 800, 1000, 1500, 2000, K]))
KCURVE = pd.DataFrame({'k': KS,
                       '모델 1': [at_k(TE['y'], p1, k)[1] for k in KS],
                       '모델 2': [at_k(TE['y'], p2, k)[1] for k in KS],
                       '기준선 ② (전년도 탈락률 순)': [at_k(TE['y'], TE['prev_rate'], k)[1] for k in KS]}).round(1)
display(KCURVE)
''',
r'''# s4-15 가설 판정 요약 (판정 규칙: 00_문제정의_가설.md 5·7절)
# [출처 규칙] '(출처: 노트북 §④ 셀 s4-15)'
ACTION_A = {'맞음': '사립·비수도권을 지원 배분 근거로 쓸 수 있음', '부분 맞음': '충족한 기준만 지원 배분 근거로 사용',
            '기각': '설립유형·지역을 지원 배분 근거로 쓰지 않음'}
ACTION_B = {'맞음': '비주류 외국어 학과군을 학업지속 지원의 우선 대상으로', '기각': "지원 근거 약함 → 문제를 '모집(입학처)'으로 재정의"}
gap_pred = EVAL.loc[1, '정밀도(%)'] - EVAL.loc[2, '정밀도(%)']
SUMMARY = pd.DataFrame([
    {'가설': 'A 전국 구조', '판정': verdict_A,
     '근거': f"사립 OR {tabA.loc['priv', '오즈비']:.2f} [{tabA.loc['priv', 'CI 하한']:.2f}, {tabA.loc['priv', 'CI 상한']:.2f}], 비수도권 OR {tabA.loc['nonmetro', '오즈비']:.2f} [{tabA.loc['nonmetro', 'CI 하한']:.2f}, {tabA.loc['nonmetro', 'CI 상한']:.2f}]",
     '셀': 's4-05', '행동': ACTION_A[verdict_A]},
    {'가설': 'A 예측 절', '판정': '보고(임계값 없음)',
     '근거': f"k={K}: 모델 2 정밀도 {EVAL.loc[1, '정밀도(%)']:.1f}% vs 기준선 ② {EVAL.loc[2, '정밀도(%)']:.1f}% ({gap_pred:+.1f}%p)",
     '셀': 's4-07', '행동': '모델 선별 권고' if gap_pred > 0 else '전년도 고위험 학과 그대로 지원 권고'},
    {'가설': 'B 한국외대', '판정': verdict_B,
     '근거': f"차이 {resB['차이(%p)']:+.2f}%p [{resB['95% 하한']:.2f}, {resB['95% 상한']:.2f}]", '셀': 's4-10', '행동': ACTION_B[verdict_B]},
])
display(SUMMARY)
''',
]

S_E = r'''# sE-01 R1 두 상위 10 목록과 교집합 (한국외대, 공시 2024~2026 합산, 학과코드 단위)
# [출처 규칙] '(출처: 노트북 §부록 E 셀 sE-01)'
r1 = H.groupby('학과코드').agg(학과명=('학과명', 'last'), 탈락합=('계', 'sum'), 재적합=('재적학생', 'sum'))
r1['합산 비율(%)'] = r1['탈락합'] / r1['재적합'] * 100
top_rate = r1.sort_values(['합산 비율(%)', '탈락합'], ascending=False).head(10)
top_cnt = r1.sort_values(['탈락합', '합산 비율(%)'], ascending=False).head(10)
inter = sorted(set(top_rate.index) & set(top_cnt.index))
print('비율 상위 10:'); display(top_rate.round(2))
print('인원 상위 10:'); display(top_cnt.round(2))
print(f'교집합 {len(inter)}곳:', r1.loc[inter, '학과명'].tolist())
print('▶ R1(부록):', '맞음 — 비율 하나로 우선순위를 정하면 안 되고 인원·비율을 함께 본다' if len(inter) < 5
      else '교집합 ≥ 5 — 비율 순위와 인원 순위가 대체로 같다')
'''
