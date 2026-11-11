S_EXPORT = r'''# sZ-01 발표·제출 문서용 수치 내보내기 (슬라이드는 이 파일의 숫자만 쓴다 — 손으로 옮긴 수치 없음)
# [출처 규칙] 슬라이드 각 수치의 출처 셀은 아래 키 이름 옆 주석과 같다.
import json
def _f(x):
    return float(x) if x is not None else None
fl_scope = FL[df['in_scope']]
r1p_out = r1p.reset_index()[['학과명', '탈락합', '재적합', '비율', '대상']].rename(columns={'대상': 'target'})
grp_ci = {}
for key_, d_ in [('hufs_target', H[H['target']]), ('hufs_other', H[~H['target']]), ('national_same', NAT)]:
    lo_, hi_ = boot_one(d_)
    grp_ci[key_] = {'rate': pooled(d_), 'lo': lo_, 'hi': hi_, 'n_dept': int(d_['학과코드'].nunique()), 'n_school': int(d_['학교코드'].nunique())}
EXPORT = {
    'run_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
    'versions': {'python': platform.python_version(), 'pandas': pd.__version__, 'numpy': np.__version__},
    # ② 수집 (s2-02, s2-03)
    'n_raw': len(df_raw), 'n_cols': df_raw.shape[1], 'raw_by_year': {int(k): int(v) for k, v in year_n.items()},
    # ③ 정제 (s3-01 ~ s3-19)
    'miss_by_year': {int(k): float(v) for k, v in miss_by_year.items()},
    'n_rate_na': int(n_rate_na), 'n_zero_enr': int(f0['재적 = 0'].sum()), 'n_zero_rate_recorded': int(f0['재적 = 0 인데 비율 기록됨(0%)'].sum()),
    'n_over100': int(f0['계 > 재적 (재적 > 0)'].sum()), 'over100_small_pct': float((over['재적학생'] <= 5).mean() * 100),
    'max_gap': float(gap.max()), 'g5': int(len(g5)), 'g5_mid_split': int((g5['중계열수'] > 1).sum()), 'g5_sub_split': int((g5['소계열수'] > 1).sum()),
    'nce_sub_pct': float(f0['소계열 N.C.E.'].mean() * 100), 'hufs_nce26': int(h[(h['공시연도'] == 2026) & (h['표준분류_소계열'] == 'N.C.E.')]['학과코드'].nunique()),
    'hufs_new': len(c26 - c25), 'hufs_gone': len(c25 - c26),
    'n_scope': n_scope, 'scope_pct': n_scope / len(df) * 100, 'n_school_scope': int(n_sch), 'scope_by_year': {int(k): int(v) for k, v in by_year.items()},
    'excluded': [{'조건': r['조건'], '단독': r['단독 기준 제외'], '순차': r['순차 적용 시 추가 제외']} for r in scope_tbl.to_dict('records')],
    'funnel': [{'단계': r['단계'], 'n': int(r['쌍 수'])} for r in steps.to_dict('records')],
    'n_link': n_link, 'n_unlinked': len(cur_scope) - n_link, 'hufs_unlinked': int(n_h_un),
    'n_sample': len(sample), 'n_train': int(split.loc[TRAIN_T].sum()), 'n_test': int(split.loc[TEST_T]),
    # ④ 분석 (s4-02 ~ s4-15)
    'cut': float(CUT), 'size_q': [float(x) for x in QB], 'pos_train': float(TR['y'].mean() * 100), 'pos_test': float(TE['y'].mean() * 100), 'K': K,
    'four': {f'{a}|{b}': {'pct': float(four_pct.loc[a, b]), 'n': int(four_n.loc[a, b])} for a in four_pct.index for b in four_pct.columns},
    'sido': [{'지역': i_, '비율': float(r_['고위험비율']), '쌍': int(r_['쌍수']), '학교': int(r_['학교수'])} for i_, r_ in sido.iterrows()],
    'tabA': {k_: {'or': float(tabA.loc[k_, '오즈비']), 'lo': float(tabA.loc[k_, 'CI 하한']), 'hi': float(tabA.loc[k_, 'CI 상한'])} for k_ in tabA.index if k_ != 'Intercept'},
    'verdict_A': verdict_A, 'n_school_A': int(M['school'].nunique()), 'med_pairs': int(med.sum()),
    'eval': [{k_: (_f(v_) if isinstance(v_, (int, float, np.floating, np.integer)) else v_) for k_, v_ in r_.items()} for r_ in EVAL.to_dict('records')],
    'confusion': {},
    'resB': {k_: (float(v_) if isinstance(v_, (np.floating, float)) else (int(v_) if isinstance(v_, (np.integer, int)) else v_)) for k_, v_ in resB.items()},
    'verdict_B': verdict_B, 'groups_ci': grp_ci, 'nat_phrase': phrase, 'nat_diff': float(d_nat), 'nat_lo': float(lo), 'nat_hi': float(hi),
    'small_b': {str(k_): {'n': int(r_['쌍 수']), 'rate': float(r_['합산 비율(%)'])} for k_, r_ in sm.iterrows()},
    'hufs_eval': [{k_: (_f(v_) if isinstance(v_, (int, float, np.floating, np.integer)) else v_) for k_, v_ in r_.items()} for r_ in EVAL_H.to_dict('records')] if EVAL_H is not None else [],
    'hufs_test_n': len(TE_H), 'k_h': k_h, 'k_next': k_next, 'cand_unit': int(unit.sum()), 'cand_target': int(CAND['비주류 외국어 학과군'].sum()),
    'cand': [{'학과명': r_['학과명'], '소계열': r_['표준분류_소계열'], '재적': int(r_['재적학생']), '탈락': int(r_['계']), '비율': float(r_['중도탈락학생비율']), '점수': float(r_['고위험 점수'])} for _, r_ in CAND.iterrows()],
    'sens': [{'조건': i_, **{k_: (v_ if isinstance(v_, str) else float(v_)) for k_, v_ in r_.items()}} for i_, r_ in SENS_T.iterrows()],
    'b_sens': {'diff': float(b_sens['차이(%p)']), 'lo': float(b_sens['95% 하한']), 'hi': float(b_sens['95% 상한']), 'verdict': b_sens['판정']},
    'thr05': {'n': int((p2 >= 0.5).sum()), 'precision': float(TE['y'].values[p2 >= 0.5].mean() * 100)},
    'kcurve': KCURVE.to_dict('records'),
    # 부록 E (sE-01)
    'r1': {'top_rate': [{'학과명': r_['학과명'], '탈락합': int(r_['탈락합']), '재적합': int(r_['재적합']), '비율': float(r_['합산 비율(%)'])} for _, r_ in top_rate.iterrows()],
           'top_cnt': [{'학과명': r_['학과명'], '탈락합': int(r_['탈락합']), '재적합': int(r_['재적합']), '비율': float(r_['합산 비율(%)'])} for _, r_ in top_cnt.iterrows()],
           'inter': len(inter)},
    'hufs_depts': r1p_out.to_dict('records'),
    'so_what': SO_WHAT,
}
for name_, pred_ in [('model2_k', sel_k), ('model2_05', (p2 >= 0.5).astype(int)), ('baseline2', TE['prev_high'].values)]:
    tn_, fp_, fn_, tp_ = confusion_matrix(TE['y'], pred_, labels=[0, 1]).ravel()
    EXPORT['confusion'][name_] = {'tp': int(tp_), 'fp': int(fp_), 'fn': int(fn_), 'tn': int(tn_)}
out_json = f'{PROC_DIR}/slides_data.json'
txt = json.dumps(EXPORT, ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
txt = txt.replace(': NaN', ': null')   # 기준선 ① 정밀도처럼 정의되지 않는 값은 null
with open(out_json, 'w', encoding='utf-8') as fh:
    fh.write(txt)
print('저장:', out_json, f'({os.path.getsize(out_json) // 1024} KB, 키 {len(EXPORT)}개)')
'''
