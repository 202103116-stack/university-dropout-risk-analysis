"""발표용 그림(브랜드 색, 큰 글씨, 제목 없음 — 제목은 슬라이드가 단다).

실행: .venv\\Scripts\\python slides/make_slide_figures.py   (노트북을 끝까지 실행해 data/processed/slides_data.json이 있어야 함)
수치: data/processed/slides_data.json (노트북 부록 F 셀 sZ-01이 저장) — 손으로 옮긴 수치 없음.
원본 그림(노트북 figures/fig1~3)과 같은 데이터를 슬라이드 판형(20×11.25in)에 맞게 다시 그린다.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FuncFormatter

ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / "data" / "processed" / "slides_data.json").read_text(encoding="utf-8"))
OUT = ROOT / "slides" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

BRAND, RISK, INK, MUTED, RULE, SOFT = "#3A59D1", "#E8603C", "#222222", "#222222", "#C9CED6", "#B9BEC8"
plt.rcParams.update({
    "font.family": "NanumGothic", "axes.unicode_minus": False, "font.size": 15,
    "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": RULE, "axes.labelcolor": MUTED,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True, "grid.color": "#E6E9F0", "grid.linewidth": 0.9,
    "axes.axisbelow": True, "savefig.dpi": 220, "figure.facecolor": "white", "axes.facecolor": "white",
})
PLAIN = FuncFormatter(lambda v, _: f"{v:g}")


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / name, bbox_inches="tight")
    plt.close(fig)
    print("saved", OUT / name)


# ① 한국외대 학과별 탈락 인원 × 탈락률 (슬라이드 5)
deps = [d for d in D["hufs_depts"] if not d["flag"]]   # 비율 해석 불가 단위(연평균 재적 < 30명, 노트북 sE-02)는 그림에서 뺀다
fig, ax = plt.subplots(figsize=(11.5, 7.0))
for tgt, col, lab in [(False, SOFT, "교내 다른 학과"), (True, BRAND, "비주류 외국어 학과군")]:
    sel = [d for d in deps if d["target"] == tgt]
    ax.scatter([d["탈락합"] for d in sel], [d["비율"] for d in sel], s=[max(18, min(320, d["재적합"] / 6)) for d in sel],
               color=col, alpha=0.85, edgecolor="white", linewidth=1.0, label=lab, zorder=3 if tgt else 2)
top_rate = sorted(deps, key=lambda d: (-d["비율"], -d["탈락합"]))[:3]
top_cnt = sorted(deps, key=lambda d: (-d["탈락합"], -d["비율"]))[:3]
for d in top_rate + [x for x in top_cnt if x not in top_rate]:
    col = RISK if d in top_rate else INK
    ax.annotate(f"{d['학과명'].replace('[통합모집]', '')} (재적 {d['재적합']:,}명)", (d["탈락합"], d["비율"]), xytext=(8, 6), textcoords="offset points", fontsize=13, color=col)
ax.set_ylim(0, max(d["비율"] for d in deps) * 1.12)
ax.set_xlabel("합산 탈락 인원 (명, 공시 2024~2026)", fontsize=15)
ax.set_ylabel("합산 탈락률 (%)", fontsize=15)
ax.legend(frameon=True, facecolor="white", edgecolor="white", framealpha=1, loc="upper right", fontsize=13, markerscale=0.8)
save(fig, "s05_hufs_count_rate.png")

# ② 가설 A 오즈비 (슬라이드 6)
A = D["tabA"]
rows = [("사립 (vs 국공립)", "priv", RISK), ("비수도권 (vs 수도권)", "nonmetro", RISK),
        (f"소규모 Q1 ≤{D['size_q'][0]:.0f}명 (vs Q4)", "C(size_q, Treatment('Q4'))[T.Q1]", BRAND),
        ("Q2 (vs Q4)", "C(size_q, Treatment('Q4'))[T.Q2]", BRAND), ("Q3 (vs Q4)", "C(size_q, Treatment('Q4'))[T.Q3]", BRAND),
        ("공학 (vs 인문사회)", "C(field, Treatment('인문사회계열'))[T.공학계열]", SOFT),
        ("자연과학 (vs 인문사회)", "C(field, Treatment('인문사회계열'))[T.자연과학계열]", SOFT),
        ("예체능 (vs 인문사회)", "C(field, Treatment('인문사회계열'))[T.예체능계열]", SOFT)]
fig, ax = plt.subplots(figsize=(10.5, 6.6))
for i, (lab, key, col) in enumerate(rows[::-1]):
    r = A[key]
    ax.plot([r["lo"], r["hi"]], [i, i], color=col, lw=3.2, solid_capstyle="round")
    ax.plot(r["or"], i, "o", color=col, ms=12, mec="white", mew=1.5)
    ax.text(r["hi"] * 1.07, i, f"{r['or']:.2f}", va="center", fontsize=14, color=INK)
ax.axvline(1, color=MUTED, lw=1.4)
ax.set_xscale("log"); ax.xaxis.set_major_locator(FixedLocator([0.5, 1, 2, 4, 8])); ax.xaxis.set_major_formatter(PLAIN); ax.xaxis.set_minor_locator(FixedLocator([]))
ax.set_yticks(range(len(rows)), [r[0] for r in rows[::-1]], fontsize=15); ax.grid(axis="y", visible=False)
ax.set_xlabel("오즈비 (로그 눈금, 1 = 차이 없음, 95% 구간)", fontsize=14)
save(fig, "s06_forest_A.png")

# ③ 가설 B: 한국외대 학과군 비교 + 95% 구간 (슬라이드 8)
G = D["groups_ci"]
bars = [("한국외대\n비주류 외국어 학과군", G["hufs_target"], BRAND), ("한국외대\n교내 다른 학과", G["hufs_other"], SOFT),
        ("전국(한국외대 제외)\n같은 소계열, 참고", G["national_same"], "#DDE1E8")]
fig, ax = plt.subplots(figsize=(10.0, 6.6))
for i, (lab, g, col) in enumerate(bars):
    ax.bar(i, g["rate"], color=col, width=0.6)
    ax.errorbar(i, g["rate"], yerr=[[g["rate"] - g["lo"]], [g["hi"] - g["rate"]]], color=INK, capsize=9, lw=2)
    ax.text(i + 0.33, g["rate"], f"{g['rate']:.2f}%", va="center", fontsize=17, color=INK, fontweight="bold")
ax.set_xticks(range(3), [b[0] for b in bars], fontsize=15); ax.grid(axis="x", visible=False)
ax.set_ylabel("합산 탈락률 (%, 공시 2024~2026)", fontsize=15)
save(fig, "s08_hufs_groups.png")
