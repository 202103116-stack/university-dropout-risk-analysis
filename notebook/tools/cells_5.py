# 노트북 ⑤ 후보 차트 갤러리 실제 코드

S5_SETUP = r'''# s5-00 차트 공통 설정 (한글 글꼴, 색, 출처 줄)
# [출처 규칙] 그림 아래 출처 줄에 셀 ID를 자동으로 넣는다.
import matplotlib
import matplotlib.pyplot as plt
try:
    import koreanize_matplotlib  # noqa: F401  (Colab: !pip install koreanize-matplotlib)
except ImportError:
    import subprocess, sys
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'koreanize-matplotlib'], check=False)
    import koreanize_matplotlib  # noqa: F401
plt.rcParams.update({'axes.spines.top': False, 'axes.spines.right': False, 'axes.grid': True, 'grid.color': '#e6e5e1',
                     'grid.linewidth': 0.8, 'axes.edgecolor': '#8a8984', 'axes.labelcolor': '#52514e', 'xtick.color': '#52514e',
                     'ytick.color': '#52514e', 'figure.dpi': 110, 'savefig.dpi': 200, 'axes.axisbelow': True,
                     'axes.titleweight': 'bold', 'axes.titlesize': 13, 'axes.titlelocation': 'left', 'axes.unicode_minus': False})
from matplotlib.ticker import FixedLocator, FuncFormatter
PLAIN = FuncFormatter(lambda v, _: f'{v:g}')
# 범주 색(검증된 기본 팔레트 앞 3칸) + 맥락용 회색
C1, C2, C3, GRAY, INK = '#2a78d6', '#eb6834', '#1baf7a', '#b9b8b2', '#0b0b0b'
SRC_TXT = '출처: 교육부 대학알리미 중도탈락 학생 현황(공공데이터포털 15164570, 공공누리 제1유형), 노트북 §⑤ 셀 {cid}'
SO_WHAT = {}

def finish(fig, cid, name, so_what):
    fig.text(0.01, 0.005, SRC_TXT.format(cid=cid), fontsize=8, color='#7a7974', ha='left', va='bottom')
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    path = f'{FIG_DIR}/cand_{cid[-3:]}_{name}.png'
    fig.savefig(path, bbox_inches='tight')
    plt.show()
    SO_WHAT[cid] = so_what
    print('저장:', path); print('그래서 무엇:', so_what)
'''

S5 = [
r'''# s5-c01 [단독, 베스트 후보·필수 교차] 탈락 인원(명) × 탈락률(%) 산점도 — 분석 표본 t=2026, 한국외대 강조
te = TE.copy()
fig, ax = plt.subplots(figsize=(8.5, 5.6))
oth = te[~te['학교코드'].eq(HUFS_CODE)]
ax.scatter(oth['계'], oth['중도탈락학생비율'], s=9, color=GRAY, alpha=0.45, linewidths=0, label='전국 학과 (일반 대학 주간)')
hu = te[te['학교코드'].eq(HUFS_CODE)]
ax.scatter(hu['계'], hu['중도탈락학생비율'], s=34, color=C1, edgecolor='white', linewidth=0.8, label='한국외대 학과', zorder=3)
ax.axhline(CUT, color=C2, lw=2, ls='--')
ax.annotate(f'고위험 컷 {CUT:.1f}%', xy=(0.99, CUT), xycoords=('axes fraction', 'data'), xytext=(0, 4), textcoords='offset points', ha='right', fontsize=9, color=INK)
ax.set_yscale('symlog', linthresh=10); ax.set_ylim(-0.5, 150)
ax.yaxis.set_major_locator(FixedLocator([0, 5, 10, 20, 50, 100])); ax.yaxis.set_major_formatter(PLAIN); ax.yaxis.set_minor_locator(FixedLocator([]))
ax.set_xlabel('당해 탈락 인원 (명, 절대)'); ax.set_ylabel('당해 탈락률 (%, 비중, 10% 이상은 로그 눈금)')
ax.set_title('탈락 인원과 탈락률은 다른 학과를 가리킨다 (공시 2026)')
ax.legend(frameon=False, loc='upper right')
hi_rate_small = int(((te['중도탈락학생비율'] >= CUT) & (te['계'] <= 5)).sum())
finish(fig, 's5-c01', 'count_x_rate',
       f"고위험(탈락률 ≥ {CUT:.1f}%) 학과 중 {hi_rate_small}개는 탈락 인원 5명 이하 — 비율만 보면 작은 학과가, 인원만 보면 큰 학과가 앞에 선다(부록 E R1: 한국외대 교집합 0곳)")
''',
r'''# s5-c02 [단독] 전년도 재적 구간별 당해 탈락률 분포 — 소규모 학과의 비율 변동
fig, ax = plt.subplots(figsize=(7.5, 4.8))
groups = [M.loc[M['size_q'].eq(q), '중도탈락학생비율'] for q in ['Q1', 'Q2', 'Q3', 'Q4']]
bp = ax.boxplot(groups, widths=0.5, showfliers=False, patch_artist=True, medianprops={'color': INK, 'lw': 2})
for b_ in bp['boxes']:
    b_.set_facecolor('#dbe8f8'); b_.set_edgecolor(C1)
lab = [f'Q1 (≤{QB[0]:.0f}명)', f'Q2 ({QB[0]:.0f}~{QB[1]:.0f})', f'Q3 ({QB[1]:.0f}~{QB[2]:.0f})', f'Q4 (>{QB[2]:.0f}명)']
ax.set_xticks([1, 2, 3, 4], lab); ax.set_ylabel('당해 탈락률 (%)'); ax.set_xlabel('전년도 재적 구간 (학습 기준 4분위)')
ax.axhline(CUT, color=C2, lw=2, ls='--'); ax.set_title('작은 학과일수록 탈락률이 높고 크게 흔들린다 (분석 표본)')
iqr = [g.quantile(.75) - g.quantile(.25) for g in groups]
finish(fig, 's5-c02', 'size_box', f'사분위 범위(IQR)가 Q1 {iqr[0]:.1f}%p → Q4 {iqr[3]:.1f}%p — 소규모 학과는 비율이 크게 흔들려 최소 재적 기준(30명)과 인원 병기가 필요')
''',
r'''# s5-c03 [서브플롯] 공시연도별 비율 결측률과 재적 0 건수 — 함정(공시 정의·결측 패턴 변화)
yy = df.groupby('공시연도').agg(결측률=('중도탈락학생비율', lambda v: v.isna().mean() * 100), 재적0=('재적학생', lambda v: v.eq(0).sum()))
fig, axs = plt.subplots(1, 2, figsize=(9, 3.8))
axs[0].bar(yy.index.astype(str), yy['결측률'], color=C1, width=0.55); axs[0].set_title('탈락률 결측 비율 (%)')
axs[1].bar(yy.index.astype(str), yy['재적0'], color=C1, width=0.55); axs[1].set_title('재적 0명인 행 (건)')
for a_, col in zip(axs, ['결측률', '재적0']):
    for x_, v_ in zip(yy.index.astype(str), yy[col]):
        a_.text(x_, v_, f'{v_:.1f}' if col == '결측률' else f'{int(v_)}', ha='center', va='bottom', fontsize=9, color=INK)
fig.suptitle('2024 공시부터 탈락률 결측이 약 15%로 늘었다 (원본 전체)', x=0.01, ha='left', fontweight='bold')
finish(fig, 's5-c03', 'missing_year', f"결측률 2023 {yy['결측률'].iloc[0]:.1f}% → 2024~2026 약 15% — 공시 방식 변화로 보이며 결측은 보정하지 않고 표본에서 제외")
''',
r'''# s5-c04 [단독, 베스트 후보] 정제 추적: 원본 → 범위 → 연결 쌍 → 분석 표본 (행 수)
st = [('원본 전체', len(df_raw)), ('범위 안\n(일반 대학 주간)', int(df['in_scope'].sum())), ('연결 쌍\n(두 해 모두 범위 안)', n_link),
      ('두 해 비율 유효', int((pairs['both_in_scope'] & pairs['rate_ok'] & pairs['prev_rate_ok']).sum())), (f'분석 표본\n(전년도 재적≥{MIN_ENROLL})', len(sample))]
fig, ax = plt.subplots(figsize=(8.5, 4.2))
ys = np.arange(len(st))[::-1]
ax.barh(ys, [v for _, v in st], color=[GRAY, GRAY, GRAY, GRAY, C1], height=0.6)
for y_, (n_, v_) in zip(ys, st):
    ax.text(v_ + 500, y_, f'{v_:,}', va='center', fontsize=10, color=INK)
ax.set_yticks(ys, [n_ for n_, _ in st]); ax.set_xlim(0, len(df_raw) * 1.15); ax.grid(axis='y', visible=False)
ax.set_xlabel('행 수 (연결 이후는 전년→당해 쌍 수)'); ax.set_title('행은 지우지 않고 표시만 — 단계별로 남은 표본')
finish(fig, 's5-c04', 'funnel', f'원본 {len(df_raw):,}행 중 분석 표본 {len(sample):,}쌍 — 각 단계의 제외 사유와 건수는 정제로그 표 4·5')
''',
r'''# s5-c05 [단독, 베스트 후보] 전년도 탈락률 × 당해 탈락률 — 지속성(기준선 ②의 근거), 테스트 t=2026
fig, ax = plt.subplots(figsize=(6.2, 5.6))
ax.scatter(TE['prev_rate'].clip(upper=40), TE['중도탈락학생비율'].clip(upper=40), s=7, color=C1, alpha=0.25, linewidths=0)
ax.axvline(CUT, color=C2, lw=2, ls='--'); ax.axhline(CUT, color=C2, lw=2, ls='--')
ax.set_xlim(0, 40); ax.set_ylim(0, 40)
ax.set_xlabel('전년도 탈락률 (%, 40% 이상은 40에 표시)'); ax.set_ylabel('당해 탈락률 (%)')
stay = TE.loc[TE['prev_high'].eq(1), 'y'].mean() * 100
ax.set_title('작년에 높던 학과는 올해도 높은 편이다')
rho = TE['prev_rate'].corr(TE['중도탈락학생비율'], method='spearman')
finish(fig, 's5-c05', 'persistence', f'작년 고위험 학과의 {stay:.1f}%가 올해도 고위험(스피어만 {rho:.2f}) — 그래서 "작년 명단 그대로"가 강한 기준선')
''',
r'''# s5-c06 [단독] 설립유형 × 수도권 4칸 고위험 비율 (가설 A 기술통계)
fig, ax = plt.subplots(figsize=(6, 4.2))
cats = [('국공립', '수도권'), ('국공립', '비수도권'), ('사립', '수도권'), ('사립', '비수도권')]
vals = [four_pct.loc[a, b] for a, b in cats]; ns = [four_n.loc[a, b] for a, b in cats]
cols = [GRAY, GRAY, GRAY, C2]
xs = np.arange(4)
ax.bar(xs, vals, color=cols, width=0.6)
for x_, v_, n_ in zip(xs, vals, ns):
    ax.text(x_, v_ + 0.8, f'{v_:.1f}%\n({n_:,}쌍)', ha='center', fontsize=9, color=INK)
ax.set_xticks(xs, [f'{a}\n{b}' for a, b in cats]); ax.set_ylabel('고위험 학과 비율 (%)'); ax.set_ylim(0, max(vals) * 1.25)
ax.axhline(25, color='#8a8984', lw=1, ls=':'); ax.text(-0.42, 25.6, '전체 기준 25%', fontsize=8, color='#52514e', ha='left')
ax.set_title('사립 + 비수도권 학과의 고위험 비율이 가장 높다'); ax.grid(axis='x', visible=False)
finish(fig, 's5-c06', 'sector_region', f'사립·비수도권 {vals[3]:.1f}% vs 국공립·수도권 {vals[0]:.1f}% — 두 요인이 겹치므로 회귀(s4-05)로 각각의 효과를 분리')
''',
r'''# s5-c07 [단독] 시·도별 고위험 비율 (가설 A 기술통계)
sd = sido.sort_values('고위험비율')
fig, ax = plt.subplots(figsize=(7, 5.6))
colors_ = [C1 if r in ('서울', '인천', '경기') else GRAY for r in sd.index]
ax.barh(sd.index, sd['고위험비율'], color=colors_, height=0.65)
for y_, (v_, n_) in enumerate(zip(sd['고위험비율'], sd['학교수'])):
    ax.text(v_ + 0.6, y_, f'{v_:.1f}% ({n_}개교)', va='center', fontsize=8.5, color=INK)
ax.set_xlabel('고위험 학과 비율 (%)'); ax.set_xlim(0, sd['고위험비율'].max() * 1.25); ax.grid(axis='y', visible=False)
ax.set_title('시·도별 고위험 학과 비율 (파랑 = 수도권)')
finish(fig, 's5-c07', 'sido', f"{sd.index[-1]} {sd['고위험비율'].iloc[-1]:.1f}% ~ {sd.index[0]} {sd['고위험비율'].iloc[0]:.1f}% — 수도권 3곳이 하위권(학교 수가 적은 시·도는 해석 주의)")
''',
r'''# s5-c08 [단독, 베스트 후보] 가설 A 오즈비 포레스트 플롯 (95% CI, 학교 군집 SE)
rows_ = [('사립 (vs 국공립)', 'priv'), ('비수도권 (vs 수도권)', 'nonmetro'),
         (f'재적 Q1 ≤{QB[0]:.0f}명 (vs Q4)', "C(size_q, Treatment('Q4'))[T.Q1]"), ('재적 Q2 (vs Q4)', "C(size_q, Treatment('Q4'))[T.Q2]"),
         ('재적 Q3 (vs Q4)', "C(size_q, Treatment('Q4'))[T.Q3]"), ('공학 (vs 인문사회)', "C(field, Treatment('인문사회계열'))[T.공학계열]"),
         ('자연과학 (vs 인문사회)', "C(field, Treatment('인문사회계열'))[T.자연과학계열]"), ('예체능 (vs 인문사회)', "C(field, Treatment('인문사회계열'))[T.예체능계열]")]
fig, ax = plt.subplots(figsize=(7.5, 4.6))
for i, (lab_, key) in enumerate(rows_[::-1]):
    o, lo_, hi_ = tabA.loc[key, ['오즈비', 'CI 하한', 'CI 상한']]
    c_ = C2 if key in ('priv', 'nonmetro') else C1
    ax.plot([lo_, hi_], [i, i], color=c_, lw=2); ax.plot(o, i, 'o', color=c_, ms=8, mec='white', mew=1.2)
    ax.text(hi_ * 1.08, i, f'{o:.2f}', va='center', fontsize=9, color=INK)
ax.axvline(1, color='#52514e', lw=1.2)
ax.set_xscale('log'); ax.xaxis.set_major_locator(FixedLocator([0.5, 1, 2, 4, 8])); ax.xaxis.set_major_formatter(PLAIN); ax.xaxis.set_minor_locator(FixedLocator([]))
ax.set_yticks(range(len(rows_)), [r[0] for r in rows_[::-1]]); ax.grid(axis='y', visible=False)
ax.set_xlabel('오즈비 (로그 눈금, 1 = 차이 없음)'); ax.set_title(f'가설 A: 사립·비수도권 모두 1보다 크다 → {verdict_A}')
finish(fig, 's5-c08', 'forest_A', f"대계열·규모를 통제해도 사립 {tabA.loc['priv', '오즈비']:.1f}배, 비수도권 {tabA.loc['nonmetro', '오즈비']:.1f}배 — 다만 소규모(Q1) 효과가 {tabA.loc[rows_[2][1], '오즈비']:.1f}배로 가장 크다")
''',
r'''# s5-c09 [단독, 베스트 후보·필수 B] 한국외대 학과군별 2024~2026 합산 탈락률 + 학과코드 부트스트랩 95% 구간
def boot_one(d, n=2000, seed=RANDOM_STATE):
    rng = np.random.default_rng(seed)
    g = d.groupby('학과코드')[['계', '재적학생']].sum().values
    s_ = np.array([g[rng.integers(0, len(g), len(g))].sum(0) for _ in range(n)])
    return np.percentile(s_[:, 0] / s_[:, 1] * 100, [2.5, 97.5])
grp = [('한국외대\n비주류 외국어 학과군', H[H['target']], C1), ('한국외대\n다른 학과', H[~H['target']], GRAY),
       ('전국(한국외대 제외)\n같은 소계열 (참고)', NAT, '#d9d8d3')]
fig, ax = plt.subplots(figsize=(7.2, 4.6))
for i, (lab_, d_, c_) in enumerate(grp):
    v_ = pooled(d_); lo_, hi_ = boot_one(d_)
    ax.bar(i, v_, color=c_, width=0.58)
    ax.errorbar(i, v_, yerr=[[v_ - lo_], [hi_ - v_]], color=INK, capsize=6, lw=1.5)
    ax.text(i + 0.31, v_, f'{v_:.2f}%', va='center', fontsize=10, color=INK)
ax.set_xticks(range(3), [g_[0] for g_ in grp]); ax.set_ylabel('합산 탈락률 (%, 공시 2024~2026)'); ax.grid(axis='x', visible=False)
ax.set_title(f'가설 B: 비주류 외국어 학과군이 오히려 낮다 → {verdict_B}')
finish(fig, 's5-c09', 'hufs_groups', f"교내 다른 학과보다 {abs(resB['차이(%p)']):.2f}%p 낮고(구간 [{resB['95% 하한']:.2f}, {resB['95% 상한']:.2f}]), 전국 같은 소계열보다도 낮다 — 어문 학과군을 이탈 지원 우선 대상으로 볼 근거 없음 → '모집(입학처)' 관점으로 재정의")
''',
r'''# s5-c10 [단독] 한국외대 학과별 인원(명) × 비율(%) — 2024~2026 합산, 비주류 외국어 학과군 강조
r1p = H.groupby('학과코드').agg(탈락합=('계', 'sum'), 재적합=('재적학생', 'sum'), 대상=('target', 'max'), 학과명=('학과명', 'last'))
r1p['비율'] = r1p['탈락합'] / r1p['재적합'] * 100
fig, ax = plt.subplots(figsize=(8, 5.2))
for flag, c_, lab_ in [(False, GRAY, '다른 학과'), (True, C1, '비주류 외국어 학과군')]:
    d_ = r1p[r1p['대상'].eq(flag)]
    ax.scatter(d_['탈락합'], d_['비율'], s=np.clip(d_['재적합'] / 8, 10, 200), color=c_, alpha=0.8, edgecolor='white', linewidth=0.8, label=lab_)
lab_pts = pd.concat([r1p.nlargest(3, '탈락합'), r1p.nlargest(3, '비율')]).drop_duplicates(subset=['탈락합', '비율'])
for _, r_ in lab_pts.iterrows():
    ax.annotate(r_['학과명'], (r_['탈락합'], r_['비율']), xytext=(5, 4), textcoords='offset points', fontsize=8, color='#52514e')
ax.set_yscale('symlog', linthresh=10); ax.yaxis.set_major_locator(FixedLocator([0, 5, 10, 20, 50, 100])); ax.yaxis.set_major_formatter(PLAIN); ax.yaxis.set_minor_locator(FixedLocator([]))
ax.set_xlabel('합산 탈락 인원 (명)'); ax.set_ylabel('합산 탈락률 (%, 10% 이상 로그 눈금)')
ax.set_title('한국외대: 비율 상위와 인원 상위는 다른 학과 (점 크기 = 재적)'); ax.legend(frameon=False)
inter10 = set(r1p.sort_values(['비율', '탈락합'], ascending=False).head(10).index) & set(r1p.sort_values(['탈락합', '비율'], ascending=False).head(10).index)
finish(fig, 's5-c10', 'hufs_count_rate', f'비율 상위 10과 인원 상위 10의 교집합 {len(inter10)}곳 — 비율 1위권은 재적 1~5명 학과(부록 E)')
''',
r'''# s5-c11 [단독] 한국외대 대상군 vs 전국 같은 소계열 — 연도별 합산 비율 (B 참고 해석)
yr = pd.DataFrame({'한국외대 대상군': HT.groupby('공시연도').apply(pooled, include_groups=False),
                   '전국 같은 소계열': NAT.groupby('공시연도').apply(pooled, include_groups=False),
                   '한국외대 다른 학과': H[~H['target']].groupby('공시연도').apply(pooled, include_groups=False)})
fig, ax = plt.subplots(figsize=(7, 4.4))
for col, c_ in zip(yr.columns, [C1, C2, GRAY]):
    ax.plot(yr.index.astype(str), yr[col], marker='o', ms=8, lw=2, color=c_)
    ax.text(len(yr) - 1 + 0.08, yr[col].iloc[-1], col, va='center', fontsize=9, color=INK)
ax.set_ylabel('합산 탈락률 (%)'); ax.set_xlim(-0.2, len(yr) + 0.9); ax.set_title('연도별로 봐도 한국외대 어문 학과군이 가장 낮다')
order_ok = int(((yr['한국외대 대상군'] < yr['한국외대 다른 학과']) & (yr['한국외대 다른 학과'] < yr['전국 같은 소계열'])).sum())
finish(fig, 's5-c11', 'hufs_vs_nat_year', f'3개 연도 중 {order_ok}개 연도에서 한국외대 대상군 < 교내 다른 학과 < 전국 같은 소계열 — 결론이 특정 해에만 의존하는지 확인')
''',
r'''# s5-c12 [단독, 베스트 후보·필수 예측] 같은 k에서 모델 vs 기준선 정밀도 (테스트 t=2026)
ev = EVAL.iloc[:3].copy()
labs = ['모델 1\n구조 변수', '모델 2\n구조 + 전년도 탈락률', '기준선 ②\n작년 고위험 그대로']
fig, ax = plt.subplots(figsize=(7.2, 4.5))
cols = [GRAY, C1, C2]
ax.bar(range(3), ev['정밀도(%)'], color=cols, width=0.58)
for i, (p_, h_) in enumerate(zip(ev['정밀도(%)'], ev['맞힌 학과 수'])):
    ax.text(i, p_ + 1, f'{p_:.1f}%\n({int(h_):,}개 적중)', ha='center', fontsize=9.5, color=INK)
ax.axhline(TE['y'].mean() * 100, color='#8a8984', lw=1, ls=':'); ax.text(-0.45, TE['y'].mean() * 100 + 0.8, f"무작위로 고르면 {TE['y'].mean() * 100:.1f}%", fontsize=8, ha='left', color='#52514e')
ax.set_xticks(range(3), labs); ax.set_ylabel(f'정밀도 (%) — 지원한 {K:,}개 학과 중 실제 고위험'); ax.set_ylim(0, 80); ax.grid(axis='x', visible=False)
ax.set_title(f'작년 고위험 학과 수(k={K:,})만큼 지원한다면')
finish(fig, 's5-c12', 'model_vs_baseline', f"모델 2가 작년 명단보다 {EVAL.loc[1, '정밀도(%)'] - EVAL.loc[2, '정밀도(%)']:+.1f}%p(적중 {int(EVAL.loc[1, '맞힌 학과 수'] - EVAL.loc[2, '맞힌 학과 수']):+d}개) — 개선은 작고, 구조 정보만으로는 작년 명단보다 못하다")
''',
r'''# s5-c13 [단독, 베스트 후보] k(지원 학과 수)에 따른 정밀도 — 모델 vs 기준선 ②
fig, ax = plt.subplots(figsize=(7.5, 4.5))
for col, c_ in [('모델 1', GRAY), ('모델 2', C1), ('기준선 ② (전년도 탈락률 순)', C2)]:
    ax.plot(KCURVE['k'], KCURVE[col], marker='o', ms=8, lw=2, color=c_, label=col)
ax.axvline(K, color='#8a8984', lw=1, ls=':'); ax.text(K, 92, f' k={K:,}', fontsize=8, color='#52514e')
ax.set_xlabel('지원 학과 수 k'); ax.set_ylabel('정밀도 (%)'); ax.set_ylim(40, 95); ax.legend(frameon=False, loc='lower left')
ax.set_title('지원 학과 수를 바꿔도 모델 2 ≈ 작년 명단')
finish(fig, 's5-c13', 'k_curve', '적게 지원할수록 정밀도는 높지만, 어떤 k에서도 모델 2와 작년 명단의 차이는 ±2%p 안팎 — 결론이 k 선택에 좌우되지 않음')
''',
r'''# s5-c14 [단독] 민감도 요약 — 조건별 사립·비수도권 오즈비 하한과 정밀도 차이
sv = SENS_T.copy()
sv['정밀도 차이'] = sv['모델2 정밀도'].astype(float) - sv['기준선② 정밀도'].astype(float)
fig, axs = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
ys = np.arange(len(sv))[::-1]
axs[0].plot(sv['사립 CI하한'].astype(float), ys, 'o', ms=8, color=C2, label='사립')
axs[0].plot(sv['비수도권 CI하한'].astype(float), ys, 's', ms=8, color=C1, label='비수도권')
axs[0].axvline(1, color='#52514e', lw=1.2); axs[0].set_title('A 오즈비 95% 하한 (1보다 크면 충족)'); axs[0].legend(frameon=False)
axs[0].set_yticks(ys, sv.index)
axs[1].barh(ys, sv['정밀도 차이'], color=C1, height=0.5); axs[1].axvline(0, color='#52514e', lw=1.2)
axs[1].set_title('모델 2 - 작년 명단 정밀도 (%p)')
for a_ in axs:
    a_.grid(axis='y', visible=False)
finish(fig, 's5-c14', 'sensitivity', '6개 조건 모두 A 맞음(하한 > 1), 모델 2가 작년 명단보다 +1.5~3%p — 결론이 기준 선택에 뒤집히지 않음')
''',
]

S5_SELECT = r"""# s5-sel ⑤-2 베스트 3종 선택 결과 → 보고서·슬라이드용 파일 이름으로 저장
# [출처 규칙] '(출처: 노트북 §⑤ 셀 s5-sel)' — 점수는 아래 마크다운 표(⑤-2)의 팀 기준
import shutil
BEST = {'fig1_scatter.png': 'cand_c10_hufs_count_rate.png',        # 필수 ① 교차 산점도
        'fig2_hufs_groups.png': 'cand_c09_hufs_groups.png',         # 필수 ② 가설 B 비교
        'fig3_model_vs_baseline.png': 'cand_c12_model_vs_baseline.png'}  # 필수 ③ 모델 vs 기준선
for dst, src in BEST.items():
    shutil.copyfile(f'{FIG_DIR}/{src}', f'{FIG_DIR}/{dst}')
    print(f'{dst:<28} ← {src}')
print('\n그래서 무엇 (슬라이드에 그대로 옮김):')
for cid in ['s5-c10', 's5-c09', 's5-c12']:
    print(f'- {cid}: {SO_WHAT[cid]}')
"""
