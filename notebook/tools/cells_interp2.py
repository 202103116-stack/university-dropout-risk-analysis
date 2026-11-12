S4_12B = r'''# s4-12b 반대 결과 수용 (가설 B 기각): 왜 반대로 나왔는가 — 데이터로 확인되는 것과 추정을 나눈다
# [출처 규칙] '(출처: 노트북 §④ 셀 s4-12b)'
# 조항(00_문제정의_가설.md 7절): 반대 결과를 그대로 받아들이고, '비주류 외국어 학과라서 많이 떠난다'는 설명을 기각한 뒤 대안 설명을 적는다.
yr_b = pd.DataFrame({
    '비주류 외국어 학과군': H[H['target']].groupby('공시연도').apply(pooled, include_groups=False),
    '교내 다른 학과': H[~H['target']].groupby('공시연도').apply(pooled, include_groups=False),
    '전국 같은 소계열': NAT.groupby('공시연도').apply(pooled, include_groups=False),
})
yr_b['대상군이 더 낮음'] = yr_b['비주류 외국어 학과군'] < yr_b['교내 다른 학과']
display(yr_b.round(2))
# 후보 ①: 외국어 계열 통합모집 단위(전공 배정 전)가 언제 생겼고, 그 탈락은 어떤 성격인가
allH_b = df[df['in_scope'] & df['학교코드'].eq(HUFS_CODE)]
LANG_UNIT = '외국어계열|언어계열|외국어\\(.*\\)계열'
lu = allH_b[allH_b['학과명'].str.contains(LANG_UNIT)].groupby('학과명').agg(첫공시=('공시연도', 'min'), 재적=('재적학생', 'sum'), 탈락=('계', 'sum'), 자퇴=('자퇴', 'sum'))
display(lu)
first_lu = int(lu['첫공시'].min())
n_low_years = int(yr_b['대상군이 더 낮음'].sum())
print(f'외국어 계열 통합모집 단위 첫 공시: {first_lu}년 ({len(lu)}개 단위)')
print(f'대상군이 교내 다른 학과보다 낮은 해: {n_low_years}/{len(yr_b)}개 연도')
print('후보 ① 이탈이 전공 배정 전 단위로 옮겨 갔을 가능성 — 데이터로 일부 확인:'
      f" {first_lu} 공시부터 생긴 외국어 계열 단위가 있고 전공 배정 전 단위 탈락의 {RSN.loc['전공 배정 전 단위', '자퇴 비중(%)']:.0f}%가 자퇴(s4-13b).")
if first_lu > min(YRS_B):
    print(f'  단, 이 단위는 {first_lu} 공시부터라 그 이전 해에도 대상군이 낮았던 것({n_low_years}/{len(yr_b)}개 연도)은 설명하지 못한다 → 부분 설명')
print('후보 ② 스스로 지망한 학생이 많을 가능성 — 결과 전 가설 문서(v2, 태그 hypotheses-locked-v2)의 B 참고 해석에 이미 적어 둔 가능성과 일치. 지망 동기는 데이터에 없어 확인 불가')
print('후보 ③ 학교를 떠나지 않고 전공을 바꾸는 길(이중전공, 전과) — 추정, 제도 운영 실태 [확인 필요]')
'''
