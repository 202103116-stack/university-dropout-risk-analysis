S4_13C = r'''# s4-13c 전공 배정 전 단위 비교의 형평성 점검 — 순위와 판정은 바꾸지 않고 해석만 정한다
# [출처 규칙] '(출처: 노트북 §④ 셀 s4-13c)'
# 질문 1: 세부 전공으로 옮겨 간 학생이 '탈락'으로 잡힌 것은 아닌가?
#   - 중도탈락 사유 8개(미등록, 미복학, 자퇴, 학사경고, 학생활동, 유급제적, 재학연한초과, 기타)에 '교내 이동'은 없고, 사유 합 = 계(s3-05, 불일치 0)
ok_ = rate_valid(df) & df['in_scope'] & df['학교코드'].eq(HUFS_CODE)
Hy = df[ok_]
pr_ = lambda x: x['계'].sum() / x['재적학생'].sum() * 100
pm26 = Hy[Hy['공시연도'].eq(2026) & Hy['학과명'].str.contains(PREMAJOR)]
ot26 = Hy[Hy['공시연도'].eq(2026) & ~Hy['학과명'].str.contains(PREMAJOR)]
unit_ratio = (pm26['자퇴'] / pm26['재적학생'] * 100)
print(f'근거 ① 단위별 자퇴/재적: {unit_ratio.min():.0f}~{unit_ratio.max():.0f}% — 전공 배정(거의 전원 이동)이 자퇴로 잡혔다면 100%에 가까워야 한다')
school_tot = {y: pr_(Hy[Hy['공시연도'].eq(y)]) for y in YRS_B}
jatoe_tot = {y: int(Hy[Hy['공시연도'].eq(y)]['자퇴'].sum()) for y in YRS_B}
print('근거 ② 한국외대 전체 탈락률:', {y: round(v, 2) for y, v in school_tot.items()}, '/ 자퇴(명):', jatoe_tot, '— 단위가 생긴 2026에 늘지 않음')
print('근거 ③ 2026 공시 = 2025학년도(3.1~2.말) 집계. 전공 배정은 1년 뒤 다음 학년도에 일어나 집계 기간 밖 [확인 필요: 한국외대 배정 시기]')
# 질문 2: 1학년만 모인 단위와 1~4학년 학과를 비율로 비교해도 공정한가?
lo_1 = pr_(ot26)                                     # 다른 학과 탈락이 네 학년에 고르게 나왔다면
hi_1 = ot26['계'].sum() / (ot26['재적학생'].sum() / 4) * 100   # 다른 학과 탈락이 전부 1학년에서 나왔다면
print(f'\n전공 배정 전 단위 {pr_(pm26):.1f}% vs 다른 학과의 1학년 탈락률 가능 범위 {lo_1:.1f}% ~ {hi_1:.1f}% (학년별 탈락 자료 없음)')
peer = df[rate_valid(df) & df['in_scope'] & df['공시연도'].eq(2026) & ~df['학교코드'].eq(HUFS_CODE) & df['학과명'].str.contains(PREMAJOR)]
print(f'참고: 전국(한국외대 제외) 같은 성격 단위 {len(peer)}개({peer["학교코드"].nunique()}개교) {pr_(peer):.1f}% — 4년제 학과가 섞였을 수 있어 참고만')
FAIR = {'pm': pr_(pm26), 'other': lo_1, 'lo': lo_1, 'hi': hi_1, 'unit_min': float(unit_ratio.min()), 'unit_max': float(unit_ratio.max()),
        'school': school_tot, 'jatoe': jatoe_tot, 'peer': pr_(peer), 'peer_units': len(peer), 'peer_schools': int(peer['학교코드'].nunique())}
print('\n▶ 해석: 탈락은 실제 이탈(자퇴)이 맞다. 다만 1학년만 모인 단위라 비율을 다른 학과와 직접 비교할 수 없다(범위 안).'
      ' "이 단위가 위험하다"가 아니라 "1학년 초기 이탈이 이 단위에 모여 보인다"로 해석한다.')
'''
