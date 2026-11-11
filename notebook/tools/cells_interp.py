# 해석 보정 셀 (결과 확인 뒤 추가, 2026-11-12). 원판정은 그대로 두고 해석 보정판을 나란히 제시한다.

S4_13B = r'''# s4-13b 해석 확인: 전공 배정 전 단위(통합모집·계열·자유전공)의 탈락 사유 구성 — 순위는 바꾸지 않음
# [출처 규칙] '(출처: 노트북 §④ 셀 s4-13b)'
# 왜: 2027 후보 상위가 전공 배정 전 단위에 몰렸다. 이 단위의 탈락이 어떤 성격인지 사유로 확인해 권고의 해석을 정한다.
PREMAJOR = '통합모집|계열|자유전공|융합대학'
h26 = df[df['in_scope'] & df['공시연도'].eq(2026) & df['학교코드'].eq(HUFS_CODE)]
pm = h26['학과명'].str.contains(PREMAJOR)
reason_cols = ['자퇴', '미복학', '미등록', '학사경고', '유급제적', '재학연한초과', '학생활동', '기타']
RSN = pd.DataFrame({'전공 배정 전 단위': h26.loc[pm, ['재적학생', '계'] + reason_cols].sum(), '그 밖의 학과': h26.loc[~pm, ['재적학생', '계'] + reason_cols].sum()}).T
RSN['합산 탈락률(%)'] = RSN['계'] / RSN['재적학생'] * 100
RSN['자퇴 비중(%)'] = RSN['자퇴'] / RSN['계'] * 100
display(RSN[['재적학생', '계', '자퇴', '미복학', '미등록', '합산 탈락률(%)', '자퇴 비중(%)']].round(1))
print(f"해석: 전공 배정 전 단위의 탈락은 {RSN.loc['전공 배정 전 단위', '자퇴 비중(%)']:.0f}%가 자퇴(그 밖의 학과 {RSN.loc['그 밖의 학과', '자퇴 비중(%)']:.0f}%)."
      " 1학년 통합모집 단위에서 자퇴가 몰린 것은 반수(다른 대학 재입학)나 입학 초기 부적응과 맞는 모습이다 — 개인 사유는 데이터에 없으므로 '추정'.")
'''

S_E2 = r'''# sE-02 R1 해석 보정판: 비율을 해석할 수 없는 단위를 근거와 함께 표시하고, 같은 규칙으로 다시 센다 (원판정 sE-01은 그대로 둔다)
# [출처 규칙] '(출처: 노트북 §부록 E 셀 sE-02)'
# 왜: 원판정의 탈락률 상위에 '재적 1명 · 탈락 1명(100%)' 같은 단위가 올랐다. 재적(학년도 학적 보유자)과 탈락(그 1년 동안 떠난 수)은
#     같은 사람을 세므로 1/1 = 남아 있던 한 명이 떠났다는 뜻이다. 이런 단위는 비율이 학과의 위험이 아니라 개편 과정을 반영한다.
# 규칙(사전 고정 설계의 최소 재적 30명과 같은 기준): 공시 2024~2026 연평균 재적 < 30명이면 '비율 해석 불가'로 표시하고 비율 순위에서만 뺀다.
#     인원 순위에는 그대로 둔다(인원은 규모와 무관하게 의미가 있다). 행은 지우지 않는다.
allH = df[df['in_scope'] & df['학교코드'].eq(HUFS_CODE)]
life = allH.groupby('학과코드').agg(첫공시=('공시연도', 'min'), 끝공시=('공시연도', 'max'))
r1x = r1.join(life)
r1x['공시연수'] = H.groupby('학과코드')['공시연도'].nunique()
r1x['연평균재적'] = r1x['재적합'] / r1x['공시연수']
yearly = allH.pivot_table(index='학과코드', columns='공시연도', values='재적학생', aggfunc='sum')
mirb = H.groupby('학과코드')[['미복학', '계']].sum()
def why(code, r):
    if r['연평균재적'] >= MIN_ENROLL:
        return ''
    if r['끝공시'] < 2026 or (yearly.loc[code].dropna().iloc[-1] <= 5 and yearly.loc[code].dropna().iloc[0] > yearly.loc[code].dropna().iloc[-1]):
        share = mirb.loc[code, '미복학'] / mirb.loc[code, '계'] * 100 if mirb.loc[code, '계'] > 0 else np.nan
        return f'개편 전 잔류 추정(재적 감소·소멸, 미복학 {share:.0f}%)' if share == share else '개편 전 잔류 추정(재적 감소·소멸)'
    if r['첫공시'] >= 2024:
        return '신설·개편 초기 추정(첫 공시 이후 재적이 적음)'
    return '소규모 단위(연평균 재적 < 30명)'
r1x['해석'] = [why(c, r) for c, r in r1x.iterrows()]
flag = r1x['해석'].ne('')
print(f'비율 해석 불가로 표시한 단위: {int(flag.sum())}개 (한국외대 학과코드 {len(r1x)}개 중) — 이 중 원판정 탈락률 상위 10에 든 것: {int(flag.loc[top_rate.index].sum())}개')
display(r1x.loc[top_rate.index, ['학과명', '탈락합', '재적합', '합산 비율(%)', '연평균재적', '해석']].round(2))
top_rate_adj = r1x[~flag].sort_values(['합산 비율(%)', '탈락합'], ascending=False).head(10)
inter_adj = sorted(set(top_rate_adj.index) & set(top_cnt.index))
print('\n해석 보정판 탈락률 상위 10 (연평균 재적 ≥ 30명):'); display(top_rate_adj[['학과명', '탈락합', '재적합', '합산 비율(%)', '연평균재적']].round(2))
print(f'해석 보정판 교집합 {len(inter_adj)}곳:', r1x.loc[inter_adj, '학과명'].tolist())
print('▶ 원판정(사전 규칙):', f'교집합 {len(inter)}곳', '/ 해석 보정판:', f'교집합 {len(inter_adj)}곳',
      '→', '보정 뒤에도 5곳 미만 — 비율과 인원은 다른 학과를 가리킨다는 결론 유지' if len(inter_adj) < 5 else '보정 뒤에는 5곳 이상 — 착시의 상당 부분은 개편 단위 때문')
'''
