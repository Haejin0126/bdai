from __future__ import annotations

from html import escape

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data import (
    COLORS,
    D1_KPI,
    D2_FUNNEL,
    D3_MONTHLY,
    D4_REPURCHASE,
    D6_KPI,
    D7_COMMON_INSIGHT,
    D7_EXECUTION_NOTICE,
    D7_MATRIX,
    D7_METRICS,
    D7_STRATEGY_SUMMARY,
    D8_RFM_CUTOFFS,
    FOOTNOTES,
    MONTHS,
    RFM_DEFINITIONS,
    SEGMENT_COLORS,
    SEGMENT_ORDER,
    SEGMENT_SUMMARY,
    SEASON_COLORS,
    SEASON_MONTHS,
    SEASON_PERIODS,
)

st.set_page_config(
    page_title="스마트폰 카테고리 Executive BI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def init_state() -> None:
    for key in (
        "global_season",
        "page1_season",
        "page2_season",
        "page2_ribbon_season",
        "page2_table_season",
        "page3_season",
        "page2_segment",
    ):
        st.session_state.pop(key, None)
    defaults = {
        "funnel_evidence_season": "전체",
        "repeat_funnel_season": "전체",
        "monthly_reach_season": "전체",
        "page1_log_scale": False,
        "page1_reach_stages": [],
        "page1_reach_months": [],
        "conversion_month_pills": [],
        "positioning_season": "성수기",
        "ribbon_season": "성수기",
        "page2_ribbon_segments": [],
        "page2_ribbon_event_signature": "",
        "rfm_table_season": "전체",
        "page2_table_segments": [],
        "page2_table_sort": "기본 순서",
        "priority_season": "성수기",
        "opportunity_season": "성수기",
        "page3_segment": "충성 고객",
        "page3_matrix_segments": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_monthly_reach_filters() -> None:
    st.session_state.page1_reach_stages = []
    st.session_state.page1_reach_months = []


def reset_conversion_months() -> None:
    st.session_state.conversion_month_pills = []


def clear_ribbon_segments() -> None:
    st.session_state.page2_ribbon_segments = []


def clear_summary_segments() -> None:
    st.session_state.page2_table_segments = []


def safe_divide(numerator: float, denominator: float) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def validate_data() -> None:
    season_months = {
        season: D3_MONTHLY[D3_MONTHLY["month"].isin(months)]
        for season, months in SEASON_MONTHS.items()
    }
    for season, monthly in season_months.items():
        first_stage = D2_FUNNEL[
            (D2_FUNNEL["season"] == season) & (D2_FUNNEL["stage"] == "조회→장바구니")
        ].iloc[0]
        second_stage = D2_FUNNEL[
            (D2_FUNNEL["season"] == season) & (D2_FUNNEL["stage"] == "장바구니→구매")
        ].iloc[0]
        expected_counts = (
            (int(monthly["조회"].sum()), int(first_stage["start_users"]), "조회"),
            (int(monthly["장바구니"].sum()), int(first_stage["reach_users"]), "장바구니 도달"),
            (int(monthly["장바구니"].sum()), int(second_stage["start_users"]), "장바구니 시작"),
            (int(monthly["구매"].sum()), int(second_stage["reach_users"]), "구매 도달"),
        )
        for monthly_total, funnel_value, label in expected_counts:
            if monthly_total != funnel_value:
                raise ValueError(f"{season} D3 {label} 월 합계와 D2가 일치하지 않습니다")
        for stage in (first_stage, second_stage):
            if int(stage["start_users"]) - int(stage["reach_users"]) != int(stage["drop_users"]):
                raise ValueError(f"{season} D2 {stage['stage']} 이탈 인원이 일치하지 않습니다")
            calculated_rate = safe_divide(
                float(stage["reach_users"]), float(stage["start_users"])
            )
            if calculated_rate is None or abs(calculated_rate * 100 - float(stage["conversion_pct"])) >= 0.06:
                raise ValueError(f"{season} D2 {stage['stage']} 전환율이 원본 비율과 일치하지 않습니다")

    customer_totals = D6_KPI[D6_KPI["metric"] == "분석 고객 수"].iloc[0]
    for season in ("성수기", "비수기"):
        customer_total = int(customer_totals[season])
        actual = int(SEGMENT_SUMMARY[season]["customer_count"].sum())
        if actual != customer_total:
            raise ValueError(f"{season} D5 세그먼트 고객 수 합계가 일치하지 않습니다: {actual}")
        if SEGMENT_SUMMARY[season]["segment"].tolist() != SEGMENT_ORDER:
            raise ValueError(f"{season} D5 세그먼트 순서가 올바르지 않습니다")


init_state()
validate_data()

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        background: #FFFFFF;
        color: #0E0D12;
        font-family: 'Noto Sans KR', sans-serif;
    }
    .page-heading { margin: 4px 0 20px; }
    .eyebrow { color: #1501A5; font-size: 11px; font-weight: 800; letter-spacing: .13em; }
    .page-title { color: #0E0D12; font-size: 30px; font-weight: 800; line-height: 1.25; margin-top: 5px; }
    .page-subtitle { color: #474747; font-size: 16px; line-height: 1.55; margin-top: 7px; }
    .section-heading { color: #0E0D12; font-size: 18px; font-weight: 800; margin: 18px 0 4px; }
    .section-caption { color: #474747; font-size: 12px; margin: 0 0 10px; }
    .kpi-card {
        background: #FFFFFF; border: 1px solid #D8D9E1; border-radius: 14px;
        min-height: 158px; padding: 14px 14px 12px; margin-bottom: 8px;
    }
    .kpi-name { color: #474747; font-size: 12px; font-weight: 700; min-height: 34px; }
    .kpi-season { display: flex; align-items: center; justify-content: space-between; gap: 5px; margin-top: 7px; }
    .season-name {
        background: #1501A5; border-radius: 999px; color: #FFFFFF; font-size: 10px;
        font-weight: 700; padding: 4px 7px; white-space: nowrap;
    }
    .season-name.cold { background: #A4B3F9; color: #0E0D12; }
    .kpi-value { font-size: 19px; font-weight: 800; font-variant-numeric: tabular-nums; text-align: right; }
    .kpi-value.hot { color: #1501A5; }
    .kpi-value.cold { color: #584CCE; }
    .mini-track { display: flex; gap: 4px; height: 6px; margin-top: 11px; }
    .mini-season-track { background: #F3F5F8; border-radius: 5px; flex: 1; height: 6px; overflow: hidden; }
    .mini-hot { background: #1501A5; border-radius: 5px; display: block; height: 6px; }
    .mini-cold { background: #A4B3F9; border-radius: 5px; display: block; height: 6px; }
    .kpi-delta { color: #474747; font-size: 11px; font-weight: 700; margin-top: 6px; }
    .surface-card {
        background: #FFFFFF; border: 1px solid #D8D9E1; border-radius: 16px;
        padding: 14px 16px; margin: 12px 0;
    }
    .callout {
        background: #F3F5F8; border-left: 4px solid #584CCE; border-radius: 10px;
        color: #0E0D12; line-height: 1.55; margin: 8px 0; padding: 12px 14px;
    }
    .callout strong { color: #1501A5; }
    .funnel-wrap {
        background: #F3F5F8; border: 1px solid #D8D9E1; border-radius: 14px;
        margin: 8px 0 12px; padding: 16px;
    }
    .funnel-season { border-radius: 12px; background: #FFFFFF; margin: 8px 0; padding: 12px; }
    .funnel-season.dimmed { opacity: .28; }
    .funnel-season-title { font-weight: 800; margin-bottom: 10px; }
    .funnel-season-title.hot { color: #1501A5; }
    .funnel-season-title.cold { color: #584CCE; }
    .funnel-row { align-items: stretch; display: flex; gap: 8px; }
    .funnel-step {
        background: #FFFFFF; border: 1px solid #D8D9E1; border-radius: 10px;
        flex: 1; min-width: 0; padding: 10px 8px; text-align: center;
    }
    .funnel-step .step-name { color: #474747; font-size: 14px; font-weight: 700; }
    .funnel-step .step-count { font-size: 29px; font-weight: 800; margin: 5px 0; }
    .funnel-step .step-count.hot { color: #1501A5; }
    .funnel-step .step-count.cold { color: #584CCE; }
    .funnel-step .step-note { color: #474747; font-size: 10px; line-height: 1.5; }
    .funnel-arrow { align-self: center; color: #7C7AA4; font-size: 16px; font-weight: 700; }
    .reach-card, .comparison-card, .dashboard-card {
        background: #FFFFFF; border: 1px solid #D8D9E1; border-radius: 14px;
        box-shadow: 0 3px 12px rgba(21, 1, 165, .045); padding: 16px;
    }
    .comparison-table-wrap, .summary-table-wrap { overflow-x: auto; width: 100%; }
    .comparison-table, .summary-table { border-collapse: collapse; min-width: 720px; width: 100%; }
    .comparison-table th, .summary-table th {
        background: #F3F5F8; border: 1px solid #D8D9E1; color: #474747;
        font-size: 12px; padding: 10px 8px; text-align: right; white-space: nowrap;
    }
    .comparison-table td, .summary-table td {
        border: 1px solid #D8D9E1; color: #0E0D12; font-size: 13px;
        padding: 12px 8px; text-align: right; white-space: nowrap;
    }
    .comparison-table td { font-size: 17px; font-weight: 700; height: 56px; }
    .comparison-table th:first-child, .comparison-table td:first-child,
    .summary-table th:first-child, .summary-table td:first-child { text-align: left; }
    .comparison-table .hot-row td:first-child { color: #1501A5; }
    .comparison-table .cold-row td:first-child { color: #584CCE; }
    .comparison-table .conversion-cell { background: #F3F1FF; }
    .gap-card { background: #F3F5F8; border: 1px solid #D8D9E1; border-radius: 12px; margin-top: 12px; padding: 16px; }
    .gap-value { color: #1501A5; font-size: 27px; font-weight: 800; }
    .gap-copy { color: #474747; font-size: 12px; line-height: 1.5; margin-top: 5px; }
    .ribbon-label { font-size: 11px; }
    .summary-table { min-width: 900px; }
    .summary-table thead th { color: #FFFFFF; text-align: center; }
    .summary-table .group-hot { background: #1501A5; }
    .summary-table .group-cold { background: #584CCE; }
    .summary-table .metric-head { background: #F3F5F8; color: #474747; }
    .summary-table tbody tr { transition: opacity .15s ease; }
    .summary-table tbody td { height: 52px; }
    .summary-table .selected-row { background: #F3F1FF; }
    .summary-table .selected-row td:first-child { border-left: 3px solid #1501A5; font-weight: 800; }
    .summary-table .risk-badge { background: #F3F5F8; border-radius: 999px; color: #584CCE; display: inline-block; font-size: 9px; margin-left: 4px; padding: 2px 5px; }
    .mini-bar-cell { min-width: 85px; }
    .mini-bar-track { background: #F3F5F8; border-radius: 3px; height: 5px; margin-top: 4px; overflow: hidden; }
    .mini-bar-fill { border-radius: 3px; display: block; height: 5px; }
    .insight-card {
        border: 1px solid #D8D9E1; border-radius: 14px; height: 100%;
        line-height: 1.55; min-height: 218px; padding: 16px;
    }
    .insight-card.observation { background: #FFFFFF; }
    .insight-card.meaning { background: #F3F5F8; }
    .insight-card.action { background: #0E0D12; border-color: #0E0D12; color: #FFFFFF; }
    .insight-type { color: #584CCE; font-size: 10px; font-weight: 800; letter-spacing: .1em; }
    .insight-card.action .insight-type { color: #B7AEF9; }
    .insight-title { color: #0E0D12; font-size: 15px; font-weight: 800; margin: 7px 0; }
    .insight-card.action .insight-title { color: #FFFFFF; }
    .insight-metric { color: #1501A5; font-size: 22px; font-weight: 800; line-height: 1.3; }
    .insight-card.meaning .insight-metric { color: #584CCE; }
    .insight-card.action .insight-metric { color: #B7AEF9; font-size: 18px; }
    .insight-compare { color: #474747; font-size: 12px; margin-top: 4px; }
    .insight-card.action .insight-compare { color: #D8D9E1; }
    .insight-copy { color: #474747; font-size: 12px; margin-top: 9px; }
    .insight-card.action .insight-copy { color: #FFFFFF; }
    .insight-action { border-top: 1px solid #D8D9E1; font-size: 12px; font-weight: 700; margin-top: 10px; padding-top: 8px; }
    .insight-card.action .insight-action { border-color: #474747; }
    .source-chip {
        background: rgba(183,174,249,.22); border-radius: 999px; color: #1501A5;
        display: inline-block; font-size: 10px; font-weight: 800; margin-top: 10px; padding: 4px 8px;
    }
    .insight-card.action .source-chip { background: rgba(183,174,249,.18); color: #B7AEF9; }
    .conclusion-banner {
        align-items: center; background: #1501A5; border-radius: 16px; color: #FFFFFF;
        display: flex; gap: 16px; margin: 8px 0 18px; padding: 22px 24px;
    }
    .conclusion-tag { background: #FFFFFF; border-radius: 999px; color: #1501A5; font-size: 12px; font-weight: 800; padding: 8px 13px; white-space: nowrap; }
    .conclusion-copy { font-size: 21px; font-weight: 800; line-height: 1.4; }
    .conclusion-sub { color: #B7AEF9; font-size: 12px; margin-top: 5px; }
    .matrix-wrap { overflow-x: auto; }
    .priority-matrix { border-collapse: separate; border-spacing: 7px; min-width: 720px; width: 100%; }
    .priority-matrix th { background: transparent; border: 0; color: #474747; font-size: 12px; padding: 6px; text-align: left; }
    .priority-matrix td { border: 0; padding: 0; vertical-align: top; }
    .matrix-segment { color: #0E0D12; font-size: 13px; font-weight: 800; min-width: 104px; padding: 12px 8px !important; }
    .matrix-cell { border: 1px solid #D8D9E1; border-radius: 11px; min-height: 100px; padding: 10px; }
    .matrix-cell.high { background: rgba(183,174,249,.20); border: 2px solid #584CCE; }
    .matrix-cell.low { background: #F3F5F8; }
    .matrix-cell.focus { box-shadow: inset 0 0 0 2px #1501A5; }
    .matrix-priority { align-items: center; display: flex; gap: 7px; }
    .matrix-dot { color: #1501A5; font-size: 16px; font-weight: 800; }
    .matrix-cell.low .matrix-dot { color: #7C7AA4; }
    .matrix-badge { color: #1501A5; font-size: 10px; font-weight: 800; }
    .matrix-badge.common { background: #0E0D12; border-radius: 999px; color: #FFFFFF; padding: 3px 7px; }
    .matrix-action { color: #474747; font-size: 11px; line-height: 1.45; margin-top: 6px; }
    .detail-card { background: #FFFFFF; border: 1px solid #D8D9E1; border-radius: 16px; margin: 12px 0; padding: 16px; }
    .detail-heading { color: #0E0D12; font-size: 19px; font-weight: 800; }
    .detail-season { border-radius: 10px; height: 100%; padding: 12px; }
    .detail-season.hot { background: rgba(21,1,165,.06); border: 1px solid rgba(21,1,165,.25); }
    .detail-season.cold { background: rgba(164,179,249,.20); border: 1px solid #A4B3F9; }
    .detail-season-name { font-size: 11px; font-weight: 800; }
    .detail-season.hot .detail-season-name { color: #1501A5; }
    .detail-season.cold .detail-season-name { color: #584CCE; }
    .detail-count { font-size: 18px; font-weight: 800; margin: 4px 0; }
    .detail-action { color: #0E0D12; font-size: 12px; line-height: 1.5; margin-top: 7px; }
    .detail-block { background: #F3F5F8; border-radius: 10px; height: 100%; padding: 12px; }
    .detail-label { color: #584CCE; font-size: 10px; font-weight: 800; letter-spacing: .08em; }
    .detail-value { color: #0E0D12; font-size: 12px; line-height: 1.5; margin-top: 5px; }
    .strategy-card { background: #FFFFFF; border: 1px solid #D8D9E1; border-radius: 14px; height: 100%; padding: 16px; }
    .strategy-card.hot { border-top: 4px solid #1501A5; }
    .strategy-card.cold { border-top: 4px solid #A4B3F9; }
    .strategy-season { color: #1501A5; font-size: 12px; font-weight: 800; }
    .strategy-card.cold .strategy-season { color: #584CCE; }
    .strategy-segments { color: #0E0D12; font-size: 18px; font-weight: 800; margin: 6px 0 10px; }
    .strategy-line { color: #474747; font-size: 12px; line-height: 1.55; margin-top: 5px; }
    .roadmap-step { background: #F3F5F8; border: 1px solid #D8D9E1; border-radius: 12px; min-height: 142px; padding: 12px; }
    .roadmap-no { color: #584CCE; font-size: 10px; font-weight: 800; }
    .roadmap-title { color: #1501A5; font-size: 12px; font-weight: 800; margin: 5px 0; }
    .roadmap-text { color: #474747; font-size: 11px; line-height: 1.45; }
    .notice-panel { background: #F3F5F8; border: 1px solid #D8D9E1; border-radius: 12px; padding: 12px 15px; }
    .notice-panel p { color: #474747; font-size: 12px; line-height: 1.5; margin: 5px 0; }
    @media (max-width: 900px) {
        .page-title { font-size: 25px; }
        .page-subtitle { font-size: 14px; }
        .conclusion-copy { font-size: 17px; }
        .funnel-row { flex-wrap: wrap; }
        .funnel-step { min-width: 100px; }
        .funnel-step .step-count { font-size: 23px; }
        .comparison-table td { font-size: 14px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def fmt_count(value: float | int | None, suffix: str = "명") -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"{int(value):,}{suffix}"


def fmt_pct(value: float | None, digits: int = 1) -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"{value:.{digits}f}%"


def fmt_pctp(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"{value:+.1f}%p"


def fmt_money(value: float | int | None, decimals: int = 0) -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"${value:,.{decimals}f}"


def fmt_abbrev(value: float | int) -> str:
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if abs(value) >= 10_000:
        return f"{value / 1_000:.0f}K"
    if abs(value) >= 1_000:
        return f"{value / 1_000:.1f}K"
    return f"{value:,.0f}"


def rgba(hex_color: str, alpha: float) -> str:
    red = int(hex_color[1:3], 16)
    green = int(hex_color[3:5], 16)
    blue = int(hex_color[5:7], 16)
    return f"rgba({red},{green},{blue},{alpha:.2f})"


def metric_delta(first: float | int, second: float | int, unit: str) -> str:
    if unit == "percent":
        return fmt_pctp(float(second) - float(first))
    if unit == "currency":
        return f"{fmt_money(float(second) - float(first))} 차이"
    return f"{int(second) - int(first):+,}명 차이"


def render_header(section: str, title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="page-heading">
            <div class="eyebrow">{escape(section)}</div>
            <div class="page-title">{escape(title)}</div>
            <div class="page-subtitle">{escape(subtitle)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(row: dict[str, object]) -> None:
    metric = str(row["metric"])
    unit = str(row["unit"])
    hot = float(row["성수기"])
    cold = float(row["비수기"])
    maximum = max(abs(hot), abs(cold))
    hot_width = 50 if maximum == 0 else max(3, abs(hot) / maximum * 100)
    cold_width = 50 if maximum == 0 else max(3, abs(cold) / maximum * 100)
    hot_title = f"{metric}: 원본 {hot:.2f}" if unit == "currency" else metric
    cold_title = f"{metric}: 원본 {cold:.2f}" if unit == "currency" else metric
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-name">{escape(metric)}</div>
            <div class="kpi-season" title="{escape(hot_title)}">
                <span class="season-name">성수기</span>
                <span class="kpi-value hot">{fmt_money(hot) if unit == "currency" else fmt_pct(hot, 2 if metric == "구매 전환율" else 1) if unit == "percent" else fmt_count(hot)}</span>
            </div>
            <div class="kpi-season" title="{escape(cold_title)}">
                <span class="season-name cold">비수기</span>
                <span class="kpi-value cold">{fmt_money(cold) if unit == "currency" else fmt_pct(cold, 2 if metric == "구매 전환율" else 1) if unit == "percent" else fmt_count(cold)}</span>
            </div>
            <div class="mini-track" aria-label="두 시즌 값 비교">
                <span class="mini-season-track"><span class="mini-hot" style="width:{hot_width:.1f}%"></span></span>
                <span class="mini-season-track"><span class="mini-cold" style="width:{cold_width:.1f}%"></span></span>
            </div>
            <div class="kpi-delta">성수기 대비 비수기 {metric_delta(hot, cold, unit)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def chart_layout(fig: go.Figure, height: int = 360) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=18, r=18, t=28, b=42),
        paper_bgcolor=COLORS["White"],
        plot_bgcolor=COLORS["Canvas Gray"],
        font=dict(family="Noto Sans KR, sans-serif", color=COLORS["Charcoal"], size=11),
        hoverlabel=dict(bgcolor=COLORS["White"], font_color=COLORS["Charcoal"]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    fig.update_xaxes(gridcolor=COLORS["Light Gray"], zerolinecolor=COLORS["Light Gray"])
    fig.update_yaxes(gridcolor=COLORS["Light Gray"], zerolinecolor=COLORS["Light Gray"])
    return fig


def show_chart(fig: go.Figure, key: str) -> None:
    st.plotly_chart(
        fig,
        width="stretch",
        config={"displaylogo": False, "responsive": True},
        key=key,
    )


def render_insight_board(cards: list[dict[str, str]]) -> None:
    st.markdown('<div class="section-heading">Executive Insight Board</div>', unsafe_allow_html=True)
    columns = st.columns(3, gap="medium")
    styles = ["observation", "meaning", "action"]
    for col, card, style in zip(columns, cards, styles):
        with col:
            st.markdown(
                f"""
                <div class="insight-card {style}">
                    <div class="insight-type">{escape(card["type"])}</div>
                    <div class="insight-title">{escape(card["title"])}</div>
                    <div class="insight-metric">{escape(card["metric"])}</div>
                    <div class="insight-compare">{escape(card["compare"])}</div>
                    <div class="insight-copy">{escape(card["interpretation"])}</div>
                    <div class="insight-action">시사점 · {escape(card["action"])}</div>
                    <span class="source-chip">{escape(card["source"])}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_footnotes() -> None:
    with st.expander("데이터 기준 및 해석상 주의사항"):
        st.markdown(
            '<div class="notice-panel">'
            + "".join(f"<p>• {escape(note)}</p>" for note in FOOTNOTES)
            + f"<p>• 실행전략은 {escape(D7_EXECUTION_NOTICE)}.</p>"
            + "</div>",
            unsafe_allow_html=True,
        )


def selected_months(state_key: str) -> pd.DataFrame:
    selected = st.session_state[state_key]
    month_by_label = {
        month[2:].replace("-", "."): month
        for month in MONTHS
    }
    selected_month_values = [
        month_by_label.get(value, value)
        for value in selected
    ]
    months = selected_month_values if selected_month_values else MONTHS
    return D3_MONTHLY[D3_MONTHLY["month"].isin(months)].sort_values("month").copy()


def render_funnel_infographic(season_focus: str = "전체") -> None:
    html = ['<div class="funnel-wrap">']
    stages = [
        ("조회", "start_users", None, None),
        ("장바구니", "reach_users", "conversion_pct", "drop_pct"),
        ("구매", "reach_users", "conversion_pct", "drop_pct"),
    ]
    for season in ("성수기", "비수기"):
        color_class = "hot" if season == "성수기" else "cold"
        row_class = "dimmed" if season_focus not in ("전체", season) else ""
        first = D2_FUNNEL[(D2_FUNNEL["season"] == season) & (D2_FUNNEL["stage"] == "조회→장바구니")].iloc[0]
        second = D2_FUNNEL[(D2_FUNNEL["season"] == season) & (D2_FUNNEL["stage"] == "장바구니→구매")].iloc[0]
        counts = [int(first["start_users"]), int(first["reach_users"]), int(second["reach_users"])]
        rates = [None, float(first["conversion_pct"]), float(second["conversion_pct"])]
        drops = [None, float(first["drop_pct"]), float(second["drop_pct"])]
        html.append(f'<div class="funnel-season {row_class}"><div class="funnel-season-title {color_class}">{season} · 사용자-월 판정</div><div class="funnel-row">')
        for idx, (name, _, _, _) in enumerate(stages):
            if idx:
                html.append('<div class="funnel-arrow" aria-hidden="true">→</div>')
            rate_text = "시작 단계" if rates[idx] is None else f"단계 전환 {fmt_pct(rates[idx])}<br>이탈 {fmt_pct(drops[idx])}"
            html.append(
                f'<div class="funnel-step"><div class="step-name">{name}</div>'
                f'<div class="step-count {color_class}">{fmt_count(counts[idx])}</div>'
                f'<div class="step-note">{rate_text}</div></div>'
            )
        html.append("</div></div>")
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def build_page1_insights() -> list[dict[str, str]]:
    hot_cart = float(D1_KPI.loc[D1_KPI["metric"] == "장바구니→구매 전환율", "성수기"].iloc[0])
    cold_cart = float(D1_KPI.loc[D1_KPI["metric"] == "장바구니→구매 전환율", "비수기"].iloc[0])
    hot_view = float(D1_KPI.loc[D1_KPI["metric"] == "조회→장바구니 전환율", "성수기"].iloc[0])
    cold_view = float(D1_KPI.loc[D1_KPI["metric"] == "조회→장바구니 전환율", "비수기"].iloc[0])
    hot_repeat = float(D4_REPURCHASE.query("season == '성수기' and stage == '2회 이상'")["first_purchase_pct"].iloc[0])
    cold_repeat = float(D4_REPURCHASE.query("season == '비수기' and stage == '2회 이상'")["first_purchase_pct"].iloc[0])
    return [
        {
            "type": "① WHAT HAPPENED · 관찰",
            "title": "장바구니 후 구매 전환",
            "metric": f"성수기 {fmt_pct(hot_cart)}",
            "compare": f"비수기 {fmt_pct(cold_cart)} · 성수기 우위 {fmt_pctp(hot_cart - cold_cart)}",
            "interpretation": "장바구니에 도달한 고객의 구매 전환은 성수기가 더 높습니다.",
            "action": "고객-월 퍼널 기준으로 시즌별 전환 차이를 추적합니다.",
            "source": "근거 D2",
        },
        {
            "type": "② WHY IT MATTERS · 의미",
            "title": "가장 큰 퍼널 병목",
            "metric": f"조회→장바구니 {fmt_pct(hot_view)}",
            "compare": f"비수기 {fmt_pct(cold_view)} · 장바구니 전 이탈이 주요 구간",
            "interpretation": "장바구니 이후보다 조회에서 장바구니로 이동하는 단계의 격차가 큽니다.",
            "action": "상품 상세·장바구니 진입 경험 개선을 우선 검토합니다.",
            "source": "근거 D2",
        },
        {
            "type": "③ WHAT TO DO · 실행",
            "title": "비수기 재구매 과제",
            "metric": f"첫 구매→2회 이상 {fmt_pct(hot_repeat)}",
            "compare": f"비수기 {fmt_pct(cold_repeat)}",
            "interpretation": "비수기 신규 고객은 첫 구매 이후 재구매 유도가 중요한 과제입니다.",
            "action": D7_MATRIX["신규 고객"]["비수기"]["action"],
            "source": "근거 D4 · D7",
        },
    ]


def page1() -> None:
    render_header(
        "SEASONAL CUSTOMER BEHAVIOR",
        "시즌별 고객 행동",
        "핵심 질문 · 성수기와 비수기의 구매 전환과 재구매 행동은 어떻게 달라지는가?",
    )
    st.caption(
        f"분석 기간 {MONTHS[0]} – {MONTHS[-1]} · "
        f"성수기 {SEASON_PERIODS['성수기'][0]} – {SEASON_PERIODS['성수기'][1]} · "
        f"비수기 {SEASON_PERIODS['비수기'][0]} – {SEASON_PERIODS['비수기'][1]}"
    )
    st.markdown('<div class="section-heading">Executive KPI</div>', unsafe_allow_html=True)
    for start in (0, 3):
        columns = st.columns(3, gap="medium")
        for column, row in zip(columns, D1_KPI.to_dict("records")[start : start + 3]):
            with column:
                render_kpi_card(row)

    reach_column = st.container()
    rate_column = st.container()
    with reach_column:
        with st.container(border=True):
            st.markdown('<div class="section-heading">월별 도달 인원</div>', unsafe_allow_html=True)
            st.caption("D3 · 기본 표시 7개월 × 3단계 · 선택된 데이터만 축 범위에 반영")
            st.segmented_control(
                "월별 도달 인원 시즌 강조",
                ["전체", "성수기", "비수기"],
                key="monthly_reach_season",
                label_visibility="collapsed",
            )
            month_labels = [month[2:].replace("-", ".") for month in MONTHS]
            month_by_label = dict(zip(month_labels, MONTHS))
            st.pills(
                "퍼널 단계 선택",
                ["조회", "장바구니", "구매"],
                selection_mode="multi",
                key="page1_reach_stages",
                label_visibility="collapsed",
            )
            st.pills(
                "월 선택",
                month_labels,
                selection_mode="multi",
                key="page1_reach_months",
                label_visibility="collapsed",
            )
            control_columns = st.columns([1, 1], gap="small")
            with control_columns[0]:
                st.button(
                    "초기화",
                    key="page1_reach_reset",
                    on_click=reset_monthly_reach_filters,
                )
            with control_columns[1]:
                log_scale = st.toggle("로그 축", key="page1_log_scale")

            selected_labels = st.session_state.page1_reach_months
            visible_months = [
                month
                for month in MONTHS
                if not selected_labels or month in [month_by_label[label] for label in selected_labels]
            ]
            month_frame = (
                D3_MONTHLY[D3_MONTHLY["month"].isin(visible_months)]
                .sort_values("month")
                .reset_index(drop=True)
            )
            selected_stages = st.session_state.page1_reach_stages or [
                "조회",
                "장바구니",
                "구매",
            ]
            positions = {
                month: index for index, month in enumerate(month_frame["month"])
            }
            colors_by_season = {
                "성수기": {
                    "조회": COLORS["Soft Lavender"],
                    "장바구니": COLORS["Royal Violet"],
                    "구매": COLORS["Primary Indigo"],
                },
                "비수기": {
                    "조회": COLORS["Light Gray"],
                    "장바구니": COLORS["Periwinkle"],
                    "구매": COLORS["Muted Violet"],
                },
            }
            season_filter = st.session_state.monthly_reach_season
            fig = go.Figure()
            for stage in ("조회", "장바구니", "구매"):
                if stage not in selected_stages:
                    continue
                bar_x: list[int] = []
                bar_y: list[int] = []
                bar_months: list[str] = []
                bar_colors: list[str] = []
                for _, row in month_frame.iterrows():
                    month = str(row["month"])
                    count = int(row[stage])
                    if log_scale and count <= 0:
                        continue
                    season = (
                        "성수기"
                        if month in SEASON_MONTHS["성수기"]
                        else "비수기"
                    )
                    dimmed = (
                        season_filter in ("성수기", "비수기")
                        and season != season_filter
                        and not selected_labels
                    )
                    bar_x.append(positions[month])
                    bar_y.append(count)
                    bar_months.append(month)
                    bar_colors.append(
                        rgba(colors_by_season[season][stage], 0.3 if dimmed else 1)
                    )
                fig.add_trace(
                    go.Bar(
                        x=bar_x,
                        y=bar_y,
                        name=stage,
                        marker_color=bar_colors,
                        text=[fmt_abbrev(count) for count in bar_y],
                        textposition="outside",
                        cliponaxis=False,
                        customdata=[[month, count] for month, count in zip(bar_months, bar_y)],
                        hovertemplate="%{customdata[0]}<br>"
                        + stage
                        + " %{customdata[1]:,.0f}명<extra></extra>",
                    )
                )
            cold_positions = [
                positions[month]
                for month in month_frame["month"]
                if month in SEASON_MONTHS["비수기"]
            ]
            for position in cold_positions:
                fig.add_vrect(
                    x0=position - 0.48,
                    x1=position + 0.48,
                    fillcolor=COLORS["Soft Lavender"],
                    opacity=0.12,
                    line_width=0,
                    layer="below",
                )
            if cold_positions:
                fig.add_annotation(
                    x=cold_positions[0],
                    y=1,
                    xref="x",
                    yref="paper",
                    yshift=-8,
                    text="12월 이후 수집 영향 가능성",
                    showarrow=False,
                    font=dict(color=COLORS["Muted Violet"], size=10),
                )
            chart_layout(fig, 390).update_layout(
                barmode="group",
                bargap=0.25,
                xaxis=dict(
                    title="월",
                    tickmode="array",
                    tickvals=list(range(len(month_frame))),
                    ticktext=[
                        month[2:].replace("-", ".")
                        for month in month_frame["month"]
                    ],
                    range=[-0.5, max(0.5, len(month_frame) - 0.5)],
                    gridcolor=COLORS["White"],
                ),
                yaxis=dict(
                    title="도달 인원",
                    type="log" if log_scale else "linear",
                    autorange=True,
                    rangemode="tozero" if not log_scale else None,
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="left",
                    x=0,
                ),
            )
            show_chart(fig, "monthly-reach-users")
            st.caption("월 선택 시 시즌 색상 강조보다 월 필터를 우선 적용합니다.")

    with rate_column:
        with st.container(border=True):
            st.markdown(
                '<div class="section-heading">월별 장바구니→구매 전환율</div>',
                unsafe_allow_html=True,
            )
            st.caption("D3 도달 인원 재계산 · D1 원본 시즌 평균선")
            month_labels = [month[2:].replace("-", ".") for month in MONTHS]
            st.pills(
                "전환율 월 선택",
                month_labels,
                selection_mode="multi",
                key="conversion_month_pills",
                label_visibility="collapsed",
            )
            st.button(
                "전체 보기",
                key="conversion_months_clear",
                on_click=reset_conversion_months,
            )
            months_df = selected_months("conversion_month_pills")
            selected_conversion_months = set(months_df["month"].tolist())
            monthly_rate = months_df["구매"] / months_df["장바구니"] * 100
            month_indexes = {month: index for index, month in enumerate(MONTHS)}
            selected_indices = [
                month_indexes[month] for month in months_df["month"]
            ]
            plot_x: list[int | None] = []
            plot_rates: list[float | None] = []
            plot_text: list[str | None] = []
            plot_points: list[list[int | str] | None] = []
            previous_index: int | None = None
            for (_, row), rate, month_index in zip(
                months_df.iterrows(), monthly_rate, selected_indices
            ):
                if previous_index is not None and month_index - previous_index > 1:
                    plot_x.append(None)
                    plot_rates.append(None)
                    plot_text.append(None)
                    plot_points.append(None)
                plot_x.append(month_index)
                plot_rates.append(float(rate))
                plot_text.append(fmt_pct(float(rate)))
                plot_points.append([int(row["장바구니"]), str(row["month"])])
                previous_index = month_index
            plot_colors: list[str] = []
            previous_index = None
            for month in months_df["month"]:
                month_index = month_indexes[month]
                if previous_index is not None and month_index - previous_index > 1:
                    plot_colors.append("rgba(255,255,255,0)")
                season = (
                    "성수기"
                    if month in SEASON_MONTHS["성수기"]
                    else "비수기"
                )
                plot_colors.append(SEASON_COLORS[season])
                previous_index = month_index
            fig = go.Figure(
                go.Scatter(
                    x=plot_x,
                    y=plot_rates,
                    mode="lines+markers+text",
                    name="월별 전환율",
                    text=plot_text,
                    textposition="top center",
                    line=dict(color=COLORS["Muted Violet"], width=2),
                    marker=dict(
                        size=10,
                        color=plot_colors,
                        line=dict(color=COLORS["White"], width=2),
                    ),
                    customdata=plot_points,
                    hovertemplate="%{customdata[1]}<br>전환율 %{y:.1f}%"
                    "<br>장바구니 %{customdata[0]:,.0f}명<extra></extra>",
                    connectgaps=False,
                )
            )
            selected_peak_month = "2019-10"
            selected_low_month = "2020-02"
            if selected_peak_month in selected_conversion_months:
                peak_row = D3_MONTHLY.loc[
                    D3_MONTHLY["month"] == selected_peak_month
                ].iloc[0]
                peak_rate = float(peak_row["구매"]) / float(peak_row["장바구니"]) * 100
                fig.add_annotation(
                    x=month_indexes[selected_peak_month],
                    y=peak_rate,
                    text=f"최고 {fmt_pct(peak_rate)}",
                    showarrow=True,
                    arrowhead=2,
                    ax=0,
                    ay=-35,
                )
            if selected_low_month in selected_conversion_months:
                low_row = D3_MONTHLY.loc[
                    D3_MONTHLY["month"] == selected_low_month
                ].iloc[0]
                low_rate = float(low_row["구매"]) / float(low_row["장바구니"]) * 100
                fig.add_annotation(
                    x=month_indexes[selected_low_month],
                    y=low_rate,
                    text=f"저점 {fmt_pct(low_rate)}",
                    showarrow=True,
                    arrowhead=2,
                    ax=0,
                    ay=32,
                )
            for month in selected_conversion_months:
                if month in SEASON_MONTHS["성수기"]:
                    index = month_indexes[month]
                    fig.add_vrect(
                        x0=index - 0.45,
                        x1=index + 0.45,
                        fillcolor=COLORS["Soft Lavender"],
                        opacity=0.12,
                        line_width=0,
                        layer="below",
                    )
                elif month == "2019-12":
                    fig.add_annotation(
                        x=month_indexes[month],
                        y=1,
                        xref="x",
                        yref="paper",
                        yshift=-8,
                        text="12월 이후 수집 영향 가능성",
                        showarrow=False,
                        font=dict(color=COLORS["Muted Violet"], size=10),
                    )
            for season in ("성수기", "비수기"):
                season_rate = float(
                    D1_KPI.loc[
                        D1_KPI["metric"] == "장바구니→구매 전환율",
                        season,
                    ].iloc[0]
                )
                fig.add_hline(
                    y=season_rate,
                    line_dash="dot",
                    line_color=SEASON_COLORS[season],
                    annotation_text=f"{season} 평균 {fmt_pct(season_rate)}",
                )
            chart_layout(fig, 460).update_layout(
                margin=dict(l=45, r=28, t=58, b=52),
                showlegend=False,
                yaxis=dict(
                    title="전환율 (%)",
                    range=[0, 74],
                    gridcolor=COLORS["Light Gray"],
                ),
                xaxis=dict(
                    title="월",
                    tickmode="array",
                    tickvals=selected_indices,
                    ticktext=[
                        month[2:].replace("-", ".")
                        for month in months_df["month"]
                    ],
                    range=[
                        min(selected_indices) - 0.5,
                        max(selected_indices) + 0.5,
                    ],
                ),
            )
            show_chart(fig, "monthly-cart-purchase")
            st.caption(
                "선택 시점만 표시 · 선택하지 않은 월은 제외되며, 선택 월 사이의 비연속 구간은 선을 끊어 표시합니다. "
                "점선은 선택 기간 평균이 아닌 전체 시즌 기준 D1 원본입니다. "
                "12월 이후 이벤트 급감은 데이터 수집 영향 가능성이 있습니다."
            )

    with st.container(border=True):
        st.markdown('<div class="section-heading">퍼널 근거</div>', unsafe_allow_html=True)
        st.segmented_control(
            "퍼널 근거 시즌 강조",
            ["전체", "성수기", "비수기"],
            key="funnel_evidence_season",
            label_visibility="collapsed",
        )
        st.caption("사용자-월 판정 · 장바구니 없이 구매한 사용자는 퍼널에서 제외")
        render_funnel_infographic(st.session_state.funnel_evidence_season)

    comparison_column, repeat_column = st.columns([1.4, 1], gap="medium")
    with comparison_column:
        with st.container(border=True):
            st.markdown(
                '<div class="section-heading">장바구니→구매 시즌 비교</div>',
                unsafe_allow_html=True,
            )
            st.caption("D2 원본 · 시즌별 합산 사용자-월")
            cart_rows = D2_FUNNEL[D2_FUNNEL["stage"] == "장바구니→구매"]
            hot = cart_rows[cart_rows["season"] == "성수기"].iloc[0]
            cold = cart_rows[cart_rows["season"] == "비수기"].iloc[0]
            gap = float(hot["conversion_pct"]) - float(cold["conversion_pct"])
            comparison_html = (
                '<div class="comparison-table-wrap"><table class="comparison-table">'
                "<thead><tr><th>시즌</th><th>시작 인원<br>(장바구니 도달)</th>"
                "<th>구매 도달 인원</th><th>전환율</th><th>이탈 인원</th><th>이탈률</th></tr></thead><tbody>"
                f'<tr class="hot-row"><td>성수기</td><td>{fmt_count(int(hot["start_users"]))}</td>'
                f'<td>{fmt_count(int(hot["reach_users"]))}</td>'
                f'<td class="conversion-cell" style="color:{SEASON_COLORS["성수기"]}">{fmt_pct(float(hot["conversion_pct"]))}</td>'
                f'<td>{fmt_count(int(hot["drop_users"]))}</td><td>{fmt_pct(float(hot["drop_pct"]))}</td></tr>'
                f'<tr class="cold-row"><td>비수기</td><td>{fmt_count(int(cold["start_users"]))}</td>'
                f'<td>{fmt_count(int(cold["reach_users"]))}</td>'
                f'<td class="conversion-cell" style="color:{COLORS["Royal Violet"]}">{fmt_pct(float(cold["conversion_pct"]))}</td>'
                f'<td>{fmt_count(int(cold["drop_users"]))}</td><td>{fmt_pct(float(cold["drop_pct"]))}</td></tr>'
                "</tbody></table></div>"
            )
            st.markdown(comparison_html, unsafe_allow_html=True)
            st.markdown(
                f'<div class="gap-card"><div class="gap-value">성수기 구매 전환 우위 {fmt_pctp(gap)}</div>'
                '<div class="gap-copy">장바구니에 도달한 고객이 구매까지 이어지는 비율은 성수기가 더 높습니다.'
                f'<br>이탈률은 성수기 {fmt_pct(float(hot["drop_pct"]))}, 비수기 {fmt_pct(float(cold["drop_pct"]))}입니다.</div></div>',
                unsafe_allow_html=True,
            )

    with repeat_column:
        with st.container(border=True):
            st.markdown(
                '<div class="section-heading">구매 횟수 퍼널</div>',
                unsafe_allow_html=True,
            )
            st.segmented_control(
                "구매 횟수 퍼널 시즌 강조",
                ["전체", "성수기", "비수기"],
                key="repeat_funnel_season",
                label_visibility="collapsed",
            )
            st.caption("첫 구매 후 30일 이내 · 구매 세션 기준 · D4")
            fig = go.Figure()
            order = ["첫 구매", "2회 이상", "3회 이상", "4회 이상"]
            for season in ("성수기", "비수기"):
                subset = D4_REPURCHASE[D4_REPURCHASE["season"] == season].copy()
                subset["order"] = subset["stage"].map(
                    {stage: index for index, stage in enumerate(order)}
                )
                subset = subset.sort_values("order")
                opacity = (
                    1
                    if st.session_state.repeat_funnel_season in ("전체", season)
                    else 0.28
                )
                custom = [
                    [
                        int(row["reach_users"]),
                        "—"
                        if row["prior_step_conversion_pct"] is None
                        else fmt_pct(float(row["prior_step_conversion_pct"])),
                    ]
                    for _, row in subset.iterrows()
                ]
                fig.add_trace(
                    go.Scatter(
                        x=subset["stage"],
                        y=subset["first_purchase_pct"],
                        mode="lines+markers+text",
                        name=season,
                        line=dict(color=SEASON_COLORS[season], width=3),
                        marker=dict(
                            size=9,
                            color=SEASON_COLORS[season],
                            line=dict(color=COLORS["White"], width=2),
                        ),
                        opacity=opacity,
                        text=[
                            f"{fmt_pct(float(row['first_purchase_pct']))}<br>{fmt_count(int(row['reach_users']))}"
                            for _, row in subset.iterrows()
                        ],
                        textposition="top center",
                        customdata=custom,
                        hovertemplate="%{x}<br>첫 구매 대비 %{y:.1f}%"
                        "<br>도달 %{customdata[0]:,.0f}명"
                        "<br>직전 단계 전환 %{customdata[1]}<extra></extra>",
                    )
                )
            chart_layout(fig, 370).update_layout(
                yaxis=dict(
                    range=[0, 118],
                    title="첫 구매 대비 비율 (%)",
                )
            )
            show_chart(fig, "repurchase-funnel")
            cold_repeat = float(
                D4_REPURCHASE.query(
                    "season == '비수기' and stage == '2회 이상'"
                )["first_purchase_pct"].iloc[0]
            )
            st.markdown(
                f'<div class="callout">비수기 첫 구매 고객의 2회 이상 구매 도달은 <strong>{fmt_pct(cold_repeat)}</strong>입니다. '
                "첫 구매 이후 재구매 유도 실험을 우선 검토할 수 있습니다.</div>",
                unsafe_allow_html=True,
            )

    render_insight_board(build_page1_insights())
    render_footnotes()


def segment_row(season: str, segment: str) -> pd.Series:
    return SEGMENT_SUMMARY[season].loc[SEGMENT_SUMMARY[season]["segment"] == segment].iloc[0]


def revenue_leader(season: str) -> pd.Series:
    return SEGMENT_SUMMARY[season].sort_values("sales_share_pct", ascending=False).iloc[0]


def build_page2_insights() -> list[dict[str, str]]:
    hot_leader = revenue_leader("성수기")
    cold_leader = revenue_leader("비수기")
    hot_risk = float(segment_row("성수기", "이탈 위험")["ppc"])
    cold_risk = float(segment_row("비수기", "이탈 위험")["ppc"])
    cold_loyal = float(segment_row("비수기", "충성 고객")["ppc"])
    relative = safe_divide(cold_risk, cold_loyal)
    risk_count = int(segment_row("비수기", "이탈 위험")["customer_count"])
    hot_strategy = D7_STRATEGY_SUMMARY[D7_STRATEGY_SUMMARY["season"] == "성수기"].iloc[0]
    cold_strategy = D7_STRATEGY_SUMMARY[D7_STRATEGY_SUMMARY["season"] == "비수기"].iloc[0]
    return [
        {
            "type": "① WHAT HAPPENED · 관찰",
            "title": "시즌별 매출 주도층",
            "metric": f"성수기 {hot_leader['segment']} · {fmt_pct(float(hot_leader['sales_share_pct']))}",
            "compare": f"비수기 {cold_leader['segment']} · {fmt_pct(float(cold_leader['sales_share_pct']))}",
            "interpretation": "매출 기여 1위 고객군은 시즌에 따라 달라집니다.",
            "action": "시즌별 예산 우선순위를 분리해 검토합니다.",
            "source": "근거 D5 · D6",
        },
        {
            "type": "② WHY IT MATTERS · 의미",
            "title": "이탈 위험 고객 가치",
            "metric": f"성수기 {fmt_money(hot_risk)} · 비수기 {fmt_money(cold_risk)}",
            "compare": f"비수기 충성 고객 대비 {relative * 100:.1f}% · 이탈 위험 표본 {fmt_count(risk_count)}",
            "interpretation": "비수기 구매자당 매출은 충성 고객보다 높지만, 대상 고객 수는 소표본입니다.",
            "action": "규모 확대 판단보다 제한된 파일럿의 결과를 먼저 확인합니다.",
            "source": "근거 D5",
        },
        {
            "type": "③ WHAT TO DO · 실행",
            "title": "시즌별 타깃 전략",
            "metric": str(hot_strategy["priority_segments"]),
            "compare": str(cold_strategy["priority_segments"]),
            "interpretation": f"성수기 · {hot_strategy['strategy']} / 비수기 · {cold_strategy['strategy']}",
            "action": f"측정 지표 · {hot_strategy['metrics']} / {cold_strategy['metrics']}",
            "source": "근거 D7",
        },
    ]


RIBBON_ORDER = [
    "챔피언",
    "충성 고객",
    "이탈 위험",
    "신규 고객",
    "휴면",
    "관심 필요",
]
SUMMARY_ORDER = [
    "챔피언",
    "충성 고객",
    "이탈 위험",
    "신규 고객",
    "휴면",
    "관심 필요",
]


def label_positions(centers: list[float], gap: float = 5.2) -> list[float]:
    positions = sorted(centers)
    for index in range(1, len(positions)):
        positions[index] = max(positions[index], positions[index - 1] + gap)
    if positions and positions[-1] > 98:
        shift = positions[-1] - 98
        positions = [position - shift for position in positions]
    for index in range(len(positions) - 2, -1, -1):
        positions[index] = min(positions[index], positions[index + 1] - gap)
    if positions and positions[0] < 2:
        shift = 2 - positions[0]
        positions = [position + shift for position in positions]
    return positions


def build_ribbon_chart(season: str, selected: list[str]) -> go.Figure:
    frame = SEGMENT_SUMMARY[season].set_index("segment")
    customer_total = float(frame["customer_share_pct"].sum())
    sales_total = float(frame["sales_share_pct"].sum())
    cursor_customer = 0.0
    cursor_sales = 0.0
    intervals: dict[str, tuple[float, float, float, float]] = {}
    for segment in RIBBON_ORDER:
        row = frame.loc[segment]
        customer_height = float(row["customer_share_pct"]) / customer_total * 100
        sales_height = float(row["sales_share_pct"]) / sales_total * 100
        intervals[segment] = (
            cursor_customer,
            cursor_customer + customer_height,
            cursor_sales,
            cursor_sales + sales_height,
        )
        cursor_customer += customer_height
        cursor_sales += sales_height

    shapes = []
    traces = []
    left_centers: list[float] = []
    right_centers: list[float] = []
    for segment in RIBBON_ORDER:
        y0, y1, z0, z1 = intervals[segment]
        has_selection = bool(selected)
        alpha = 0.55 if segment in selected else 0.15 if has_selection else 0.42
        color = SEGMENT_COLORS[segment]
        path = (
            f"M 0.11,{y0:.3f} C 0.5,{y0:.3f} 0.5,{z0:.3f} 0.89,{z0:.3f} "
            f"L 0.89,{z1:.3f} C 0.5,{z1:.3f} 0.5,{y1:.3f} 0.11,{y1:.3f} Z"
        )
        shapes.append(
            dict(
                type="path",
                path=path,
                xref="x",
                yref="y",
                fillcolor=rgba(color, alpha),
                line=dict(color=rgba(color, alpha), width=0),
                layer="below",
            )
        )
        y_left = y1 - y0
        y_right = z1 - z0
        trace_alpha = 0.15 if has_selection and segment not in selected else 1.0
        traces.append(
            go.Bar(
                x=[0, 1],
                y=[y_left, y_right],
                base=[y0, z0],
                width=0.22,
                name=segment,
                marker=dict(
                    color=[rgba(color, trace_alpha), rgba(color, trace_alpha)],
                    line=dict(
                        color=[COLORS["White"], COLORS["White"]],
                        width=[0.5, 0.5],
                    ),
                ),
                customdata=[
                    [segment, float(row["customer_share_pct"])],
                    [segment, float(row["sales_share_pct"])],
                ],
                hovertemplate="%{customdata[0]}<br>비중 %{customdata[1]:.1f}%<extra></extra>",
                showlegend=False,
            )
        )
        left_centers.append((y0 + y1) / 2)
        right_centers.append((z0 + z1) / 2)

    left_labels = label_positions(left_centers)
    right_labels = label_positions(right_centers)
    annotations = [
        dict(
            x=0.11,
            y=center,
            ax=-0.18,
            ay=label_y,
            xref="x",
            yref="y",
            axref="x",
            ayref="y",
            text=(
                f"<b>{segment} {fmt_pct(float(frame.loc[segment, 'customer_share_pct']))}</b>"
                if not selected or segment in selected
                else f"{segment} {fmt_pct(float(frame.loc[segment, 'customer_share_pct']))}"
            ),
            showarrow=True,
            arrowhead=0,
            arrowwidth=1,
            arrowcolor=COLORS["Light Gray"],
            xanchor="right",
            align="right",
            font=dict(
                family="Noto Sans KR, sans-serif",
                size=10,
                color=COLORS["Charcoal"]
                if not selected or segment in selected
                else COLORS["Muted Violet"],
            ),
        )
        for segment, center, label_y in zip(RIBBON_ORDER, left_centers, left_labels)
    ]
    annotations.extend(
        dict(
            x=0.89,
            y=center,
            ax=1.18,
            ay=label_y,
            xref="x",
            yref="y",
            axref="x",
            ayref="y",
            text=(
                f"<b>{fmt_pct(float(frame.loc[segment, 'sales_share_pct']))} {segment}</b>"
                if not selected or segment in selected
                else f"{fmt_pct(float(frame.loc[segment, 'sales_share_pct']))} {segment}"
            ),
            showarrow=True,
            arrowhead=0,
            arrowwidth=1,
            arrowcolor=COLORS["Light Gray"],
            xanchor="left",
            align="left",
            font=dict(
                family="Noto Sans KR, sans-serif",
                size=10,
                color=COLORS["Charcoal"]
                if not selected or segment in selected
                else COLORS["Muted Violet"],
            ),
        )
        for segment, center, label_y in zip(RIBBON_ORDER, right_centers, right_labels)
    )
    fig = go.Figure(data=traces)
    chart_layout(fig, 500).update_layout(
        barmode="overlay",
        shapes=shapes,
        annotations=annotations,
        margin=dict(l=28, r=28, t=30, b=38),
        xaxis=dict(
            range=[-1.1, 2.1],
            tickvals=[0, 1],
            ticktext=["고객 비중", "매출 비중"],
            showgrid=False,
            zeroline=False,
            showline=False,
            fixedrange=True,
        ),
        yaxis=dict(
            range=[100, 0],
            tickvals=[],
            showgrid=False,
            zeroline=False,
            showline=False,
            fixedrange=True,
        ),
        showlegend=False,
    )
    return fig


def summary_table_html(
    season_selection: str,
    selected_segments: list[str],
    sort_order: str,
) -> str:
    seasons = (
        ("성수기", "비수기")
        if season_selection == "전체"
        else (season_selection,)
    )
    sort_season = "성수기" if season_selection == "전체" else season_selection
    frame = SEGMENT_SUMMARY[sort_season].copy()
    if sort_order == "고객 수 많은 순":
        ordered_segments = frame.sort_values(
            "customer_count", ascending=False, kind="stable"
        )["segment"].tolist()
    elif sort_order == "매출 비중 높은 순":
        ordered_segments = frame.sort_values(
            "sales_share_pct", ascending=False, kind="stable"
        )["segment"].tolist()
    else:
        ordered_segments = SUMMARY_ORDER

    total_counts = {
        season: int(
            D6_KPI.loc[D6_KPI["metric"] == "분석 고객 수", season].iloc[0]
        )
        for season in seasons
    }
    group_headers = []
    metric_headers = ["<th class='metric-head'>세그먼트</th>"]
    for season in seasons:
        season_class = "group-hot" if season == "성수기" else "group-cold"
        group_headers.append(
            f'<th class="{season_class}" colspan="{4 if season == "성수기" else 5}">'
            f'{season} {SEASON_PERIODS[season][0][5:]}~{SEASON_PERIODS[season][1][5:]} · '
            f'{fmt_count(total_counts[season])}</th>'
        )
        metric_headers.extend(
            [
                f'<th class="metric-head">{season} 고객 수</th>',
                f'<th class="metric-head">고객 비중</th>',
                f'<th class="metric-head">매출 비중</th>',
                f'<th class="metric-head">구매자당 매출</th>',
            ]
        )
        if season == "비수기":
            metric_headers.append('<th class="metric-head">이전 구매 경험</th>')

    rows = []
    for segment in ordered_segments:
        selected = not selected_segments or segment in selected_segments
        classes = "selected-row" if selected_segments and selected else ""
        opacity = "1" if not selected_segments or selected else "0.35"
        label = escape(segment)
        if segment == "이탈 위험":
            label += '<span class="risk-badge">재활성화 검토</span>'
        cells = [f'<td>{label}</td>']
        for season in seasons:
            row = segment_row(season, segment)
            count = int(row["customer_count"])
            customer_share = float(row["customer_share_pct"])
            sales_share = float(row["sales_share_pct"])
            customer_bar = max(0, min(100, customer_share))
            sales_bar = max(0, min(100, sales_share))
            customer_color = COLORS["Light Gray"]
            sales_color = (
                COLORS["Primary Indigo"]
                if season == "성수기"
                else COLORS["Periwinkle"]
            )
            display_sales = fmt_pct(sales_share)
            if season == "성수기" and segment == "이탈 위험":
                display_sales += "*"
            cells.extend(
                [
                    f'<td>{fmt_count(count)}</td>',
                    f'<td class="mini-bar-cell">{fmt_pct(customer_share)}'
                    f'<div class="mini-bar-track"><span class="mini-bar-fill" style="width:{customer_bar:.1f}%;background:{customer_color}"></span></div></td>',
                    f'<td class="mini-bar-cell">{display_sales}'
                    f'<div class="mini-bar-track"><span class="mini-bar-fill" style="width:{sales_bar:.1f}%;background:{sales_color}"></span></div></td>',
                    f'<td>{fmt_money(float(row["ppc"]))}</td>',
                ]
            )
            if season == "비수기":
                prior_rate = row["prior_purchase_rate_pct"]
                prior_display = fmt_pct(float(prior_rate)) if pd.notna(prior_rate) else "—"
                prior_width = (
                    max(0, min(100, float(prior_rate)))
                    if pd.notna(prior_rate)
                    else 0
                )
                cells.append(
                    f'<td class="mini-bar-cell">{prior_display}'
                    f'<div class="mini-bar-track"><span class="mini-bar-fill" style="width:{prior_width:.1f}%;background:{COLORS["Muted Violet"]}"></span></div></td>'
                )
        rows.append(
            f'<tr class="{classes}" style="opacity:{opacity}">{"".join(cells)}</tr>'
        )
    return (
        '<div class="summary-table-wrap"><table class="summary-table"><thead>'
        f'<tr><th class="metric-head" rowspan="2">세그먼트</th>{"".join(group_headers)}</tr>'
        f'<tr>{"".join(metric_headers[1:])}</tr></thead><tbody>'
        f'{"".join(rows)}</tbody></table></div>'
    )


def update_ribbon_selection_from_chart() -> None:
    chart_state = st.session_state.get("page2_ribbon_chart")
    if isinstance(chart_state, dict):
        selection = chart_state.get("selection", {})
        points = selection.get("points", []) if isinstance(selection, dict) else []
    else:
        selection = getattr(chart_state, "selection", None)
        points = getattr(selection, "points", []) if selection is not None else []
    selected: list[str] = []
    for point in points:
        custom = point.get("customdata") if isinstance(point, dict) else None
        if isinstance(custom, (list, tuple)) and custom:
            candidate = custom[0]
            if candidate in RIBBON_ORDER and candidate not in selected:
                selected.append(candidate)
    signature = repr(tuple(selected))
    if signature != st.session_state.page2_ribbon_event_signature:
        st.session_state.page2_ribbon_event_signature = signature
        st.session_state.page2_ribbon_segments = selected


def page2() -> None:
    update_ribbon_selection_from_chart()
    render_header(
        "RFM SEGMENT ANALYSIS",
        "RFM 세그먼트 분석",
        "핵심 질문 · 시즌마다 매출을 이끄는 고객군은 같은가?",
    )
    definition_html = "".join(
        f'<span class="source-chip">{escape(name)} · {escape(rule)}</span> '
        for name, rule in RFM_DEFINITIONS
    )
    st.markdown(
        f'<div class="notice-panel"><strong>RFM 세그먼트 적용 순서 · 시즌별 5분위</strong><br>{definition_html}'
        f'<p>성수기 기준일 {escape(D8_RFM_CUTOFFS["성수기"])} · 비수기 기준일 {escape(D8_RFM_CUTOFFS["비수기"])}. '
        "원시 고객별 점수가 없어 재산출하지 않습니다.</p></div>",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-heading">세그먼트 KPI</div>', unsafe_allow_html=True)
    kpi_rows = D6_KPI.to_dict("records")
    shown = [
        row
        for row in kpi_rows
        if row["metric"]
        in (
            "분석 고객 수",
            "단골 고객 비중",
            "매출 1위 매출 비중",
            "이탈 위험 구매자당 매출",
        )
    ]
    columns = st.columns(4, gap="medium")
    for column, row in zip(columns, shown):
        with column:
            render_kpi_card(row)
    leader_hot = D6_KPI.loc[
        D6_KPI["metric"] == "매출 1위 세그먼트", "성수기"
    ].iloc[0]
    leader_cold = D6_KPI.loc[
        D6_KPI["metric"] == "매출 1위 세그먼트", "비수기"
    ].iloc[0]
    st.markdown(
        f'<div class="callout">매출 1위 세그먼트 · 성수기 <strong>{escape(str(leader_hot))}</strong> / '
        f'비수기 <strong>{escape(str(leader_cold))}</strong></div>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown(
            '<div class="section-heading">고객 비중 vs 매출 비중</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<span class="source-chip">메인 · 가설 3 · 리본 차트</span>',
            unsafe_allow_html=True,
        )
        st.segmented_control(
            "리본 시즌",
            ["성수기", "비수기"],
            key="ribbon_season",
            label_visibility="collapsed",
        )
        ribbon_season = st.session_state.ribbon_season
        title = (
            "성수기에는 단골 고객의 매출 기여가 고객 비중보다 크게 나타납니다."
            if ribbon_season == "성수기"
            else "비수기에도 세그먼트별 고객 비중과 매출 비중의 차이가 존재합니다."
        )
        st.markdown(f"### {title}")
        st.caption(
            "세그먼트별 고객 비중 vs 매출 비중 · 시즌 합계 100% · 고객 단위"
        )
        st.pills(
            "리본 세그먼트 선택",
            RIBBON_ORDER,
            selection_mode="multi",
            key="page2_ribbon_segments",
            label_visibility="collapsed",
        )
        selected_ribbon = list(st.session_state.page2_ribbon_segments)
        controls = st.columns([1, 4], gap="small")
        with controls[0]:
            st.button(
                "선택 해제",
                key="page2_ribbon_clear",
                on_click=clear_ribbon_segments,
            )
        with controls[1]:
            st.caption(
                "선택이 없으면 전체 리본 표시 · 선택한 세그먼트는 강조됩니다."
            )
        ribbon_fig = build_ribbon_chart(ribbon_season, selected_ribbon)
        st.plotly_chart(
            ribbon_fig,
            on_select="rerun",
            selection_mode="points",
            width="stretch",
            config={"displaylogo": False, "responsive": True},
            key="page2_ribbon_chart",
        )
        st.caption(
            "* 성수기 이탈 위험 매출 비중 11.2%는 원본 검산 필요 · "
            "비수기 이탈 위험 143명 소표본"
        )

        if selected_ribbon:
            summary_groups = [(selected_ribbon, "선택 세그먼트 합계")]
        else:
            summary_groups = [
                (["챔피언", "충성 고객"], "챔피언 + 충성 고객"),
                (["신규 고객", "휴면", "관심 필요"], "신규 + 휴면 + 관심 필요"),
            ]
        summary_columns = st.columns(len(summary_groups), gap="medium")
        for column, (segments, heading) in zip(summary_columns, summary_groups):
            customer_share = sum(
                float(segment_row(ribbon_season, segment)["customer_share_pct"])
                for segment in segments
            )
            sales_share = sum(
                float(segment_row(ribbon_season, segment)["sales_share_pct"])
                for segment in segments
            )
            with column:
                st.markdown(
                    f'<div class="dashboard-card"><strong>{escape(heading)}</strong>'
                    f'<div class="section-caption">{escape(" + ".join(segments))}</div>'
                    f'<div class="insight-metric">{fmt_pct(customer_share)} 고객 비중</div>'
                    f'<div class="insight-compare">{fmt_pct(sales_share)} 매출 비중</div></div>',
                    unsafe_allow_html=True,
                )
        if not selected_ribbon:
            st.caption(
                "이탈 위험 세그먼트는 별도 확인 대상이며 매출 비중 변화 차트와 요약표에서 확인할 수 있습니다."
            )

    focus_segments = selected_ribbon
    delta_rows = []
    for segment in SUMMARY_ORDER:
        hot_share = float(segment_row("성수기", segment)["sales_share_pct"])
        cold_share = float(segment_row("비수기", segment)["sales_share_pct"])
        delta_rows.append((segment, cold_share - hot_share, hot_share, cold_share))
    delta_frame = pd.DataFrame(
        delta_rows,
        columns=["segment", "delta", "hot", "cold"],
    ).sort_values("delta", key=lambda values: values.abs(), ascending=False)
    position_column, change_column = st.columns([1.1, 1], gap="medium")

    with change_column:
        with st.container(border=True):
            st.markdown(
                '<div class="section-heading">세그먼트별 매출 비중 변화(%p)</div>',
                unsafe_allow_html=True,
            )
            st.caption("변화 = 비수기 매출 비중 − 성수기 매출 비중")
            positive = delta_frame[delta_frame["delta"] >= 0]
            negative = delta_frame[delta_frame["delta"] < 0]
            fig = go.Figure()
            for subset, label, color, outline, sign in (
                (
                    positive,
                    "양수 · 비수기 증가",
                    COLORS["Primary Indigo"],
                    COLORS["Primary Indigo"],
                    1,
                ),
                (
                    negative,
                    "음수 · 비수기 감소",
                    COLORS["Periwinkle"],
                    COLORS["Muted Violet"],
                    -1,
                ),
            ):
                values = subset["delta"].astype(float).tolist()
                fig.add_trace(
                    go.Bar(
                        x=values,
                        y=subset["segment"].tolist(),
                        orientation="h",
                        name=label,
                        marker=dict(
                            color=[
                                rgba(
                                    color,
                                        1
                                        if not focus_segments or segment in focus_segments
                                        else 0.28,
                                )
                                for segment in subset["segment"]
                            ],
                            line=dict(
                                color=outline,
                                width=1.5 if sign < 0 else 0,
                            ),
                        ),
                        text=[
                            f"+{value:.1f}%p"
                            if value >= 0
                            else f"−{abs(value):.1f}%p"
                            for value in values
                        ],
                        textposition="outside",
                        customdata=subset[["hot", "cold"]].to_numpy(),
                        hovertemplate="%{y}<br>변화 %{x:+.1f}%p"
                        "<br>성수기 %{customdata[0]:.1f}%"
                        "<br>비수기 %{customdata[1]:.1f}%<extra></extra>",
                    )
                )
            max_delta = float(delta_frame["delta"].abs().max()) * 1.35
            fig.add_vline(
                x=0,
                line_color=COLORS["Charcoal"],
                line_width=2,
            )
            chart_layout(fig, 390).update_layout(
                barmode="overlay",
                xaxis=dict(
                    title="비수기 − 성수기 (%p)",
                    range=[-max_delta, max_delta],
                    zeroline=False,
                ),
                yaxis=dict(
                    categoryorder="array",
                    categoryarray=delta_frame["segment"].tolist(),
                    autorange="reversed",
                    title=None,
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="left",
                    x=0,
                ),
            )
            show_chart(fig, "segment-sales-share-change")

    with position_column:
        with st.container(border=True):
            st.markdown(
                '<div class="section-heading">세그먼트 포지셔닝 맵</div>',
                unsafe_allow_html=True,
            )
            st.segmented_control(
                "포지셔닝 시즌",
                ["성수기", "비수기"],
                key="positioning_season",
                label_visibility="collapsed",
            )
            detail_season = st.session_state.positioning_season
            st.caption(
                "버블 크기 = 구매자당 매출 · y=x 위는 고객 비중보다 매출 비중이 높은 경우"
            )
            frame = SEGMENT_SUMMARY[detail_season].copy()
            max_ppc = float(frame["ppc"].max())
            size_ref = 2.0 * max_ppc / (42**2)
            fig = go.Figure()
            for _, row in frame.iterrows():
                segment = str(row["segment"])
                is_focus = segment in focus_segments
                marker_alpha = (
                    1
                    if is_focus or not selected_ribbon
                    else 0.3
                )
                fig.add_trace(
                    go.Scatter(
                        x=[row["customer_share_pct"]],
                        y=[row["sales_share_pct"]],
                        mode="markers+text",
                        name=segment,
                        text=[segment],
                        textposition="top center",
                        marker=dict(
                            size=[float(row["ppc"])],
                            sizemode="area",
                            sizeref=size_ref,
                            sizemin=9,
                            color=rgba(SEGMENT_COLORS[segment], marker_alpha),
                            line=dict(
                                color=COLORS["Charcoal"] if is_focus else COLORS["White"],
                                width=3 if is_focus else 1,
                            ),
                        ),
                        customdata=[[row["customer_count"], row["ppc"]]],
                        hovertemplate=(
                            f"{segment}<br>고객 비중 %{{x:.1f}}%"
                            "<br>매출 비중 %{y:.1f}%"
                            "<br>구매자당 매출 $%{customdata[1]:,.2f}"
                            "<br>고객 수 %{customdata[0]:,.0f}명<extra></extra>"
                        ),
                    )
                )
            bound = max(
                float(frame["customer_share_pct"].max()),
                float(frame["sales_share_pct"].max()),
            ) * 1.14
            fig.add_trace(
                go.Scatter(
                    x=[0, bound],
                    y=[0, bound],
                    mode="lines",
                    line=dict(
                        color=COLORS["Muted Violet"],
                        dash="dash",
                        width=1,
                    ),
                    name="고객 비중 = 매출 비중",
                    hoverinfo="skip",
                    showlegend=False,
                )
            )
            chart_layout(fig, 490).update_layout(
                margin=dict(l=42, r=24, t=28, b=118),
                xaxis=dict(
                    title="고객 비중 (%)",
                    range=[0, bound],
                    gridcolor=COLORS["Light Gray"],
                ),
                yaxis=dict(
                    title="매출 비중 (%)",
                    range=[0, bound],
                    gridcolor=COLORS["Light Gray"],
                ),
                legend=dict(
                    orientation="h",
                    x=0.5,
                    xanchor="center",
                    y=-0.27,
                    yanchor="top",
                    entrywidth=85,
                    font=dict(size=9),
                ),
            )
            show_chart(fig, "segment-positioning")
            st.caption(
                "구매자당 매출 버블은 비교용이며 ROI나 세그먼트 총매출을 뜻하지 않습니다."
            )

    with st.container(border=True):
        st.markdown(
            '<div class="section-heading">이탈 위험 vs 충성 고객</div>',
            unsafe_allow_html=True,
        )
        comparison = []
        for season in ("성수기", "비수기"):
            risk = float(segment_row(season, "이탈 위험")["ppc"])
            loyal = float(segment_row(season, "충성 고객")["ppc"])
            comparison.append((season, risk, loyal, safe_divide(risk, loyal)))
        fig = go.Figure()
        for label, field, color in (
            ("이탈 위험", 1, COLORS["Primary Indigo"]),
            ("충성 고객", 2, COLORS["Muted Violet"]),
        ):
            fig.add_trace(
                go.Bar(
                    x=[row[0] for row in comparison],
                    y=[row[field] for row in comparison],
                    name=label,
                    marker_color=color,
                    text=[fmt_money(row[field]) for row in comparison],
                    textposition="outside",
                    hovertemplate="%{x}<br>" + label + " $%{y:,.2f}<extra></extra>",
                )
            )
        chart_layout(fig, 320).update_layout(
            barmode="group",
            yaxis=dict(title="구매자당 매출 ($)"),
        )
        show_chart(fig, "risk-vs-loyal")
        risk_count = int(segment_row("비수기", "이탈 위험")["customer_count"])
        st.caption(
            f"비수기 이탈 위험 {fmt_count(risk_count)}는 소표본입니다. "
            "막대는 D5 구매자당 매출 원본 값입니다."
        )

    with st.expander("세그먼트 · 시즌별 요약표 펼치기", expanded=False):
        st.markdown(
            '<div class="section-heading">세그먼트 · 시즌별 요약표</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            "고객 수 · 고객 비중 · 매출 비중 · 구매자당 매출 · 이전 구매 경험"
        )
        st.segmented_control(
            "표 시즌",
            ["전체", "성수기", "비수기"],
            key="rfm_table_season",
            label_visibility="collapsed",
        )
        table_controls = st.columns([4, 1.2, 1.5], gap="small")
        with table_controls[0]:
            st.pills(
                "표 세그먼트 선택",
                SUMMARY_ORDER,
                selection_mode="multi",
                key="page2_table_segments",
                label_visibility="collapsed",
            )
        with table_controls[1]:
            st.button(
                "전체 보기",
                key="page2_table_clear",
                on_click=clear_summary_segments,
            )
        with table_controls[2]:
            st.selectbox(
                "정렬",
                ["기본 순서", "고객 수 많은 순", "매출 비중 높은 순"],
                key="page2_table_sort",
            )
        st.markdown(
            summary_table_html(
                st.session_state.rfm_table_season,
                list(st.session_state.page2_table_segments),
                st.session_state.page2_table_sort,
            ),
            unsafe_allow_html=True,
        )
        st.caption(
            "* 성수기 이탈 위험 매출 비중은 원본 자료 검산 필요 · "
            "비수기 이탈 위험 143명은 소표본 참고용"
        )

    render_insight_board(build_page2_insights())
    render_footnotes()


def render_priority_matrix(
    season_focus: str,
    selected_segments: list[str] | None = None,
) -> None:
    selected_segments = selected_segments or []
    headers = (
        '<table class="priority-matrix"><thead><tr><th>세그먼트</th>'
        f'<th class="{"active" if season_focus == "성수기" else ""}">성수기</th>'
        f'<th class="{"active" if season_focus == "비수기" else ""}">비수기</th>'
        "</tr></thead><tbody>"
    )
    html = [headers]
    for segment in SEGMENT_ORDER:
        selected = not selected_segments or segment in selected_segments
        opacity = "1" if selected else "0.25"
        html.append(
            f'<tr style="opacity:{opacity}"><td class="matrix-segment">'
            f'{escape(segment)}</td>'
        )
        for season in ("성수기", "비수기"):
            info = D7_MATRIX[segment][season]
            is_high = info["priority"] == "●"
            classes = ["matrix-cell", "high" if is_high else "low"]
            if season == season_focus:
                classes.append("focus")
            badge_class = "matrix-badge common" if segment == "이탈 위험" else "matrix-badge"
            badge = "공통 재활성화 검토" if segment == "이탈 위험" else info["badge"]
            html.append(
                f'<td><div class="{" ".join(classes)}">'
                f'<div class="matrix-priority"><span class="matrix-dot">{escape(info["priority"])}</span>'
                f'<span class="{badge_class}">{escape(badge)}</span></div>'
                f'<div class="matrix-action">{escape(info["action"])}</div></div></td>'
            )
        html.append("</tr>")
    html.append("</tbody></table>")
    st.markdown('<div class="matrix-wrap">' + "".join(html) + "</div>", unsafe_allow_html=True)


def render_segment_detail(segment: str) -> None:
    hot = segment_row("성수기", segment)
    cold = segment_row("비수기", segment)
    hot_info = D7_MATRIX[segment]["성수기"]
    cold_info = D7_MATRIX[segment]["비수기"]
    risk = segment == "이탈 위험"
    caution = (
        f"비수기 대상은 {fmt_count(int(cold['customer_count']))} 소표본이므로 참고용입니다."
        if risk
        else "대상 인원은 시즌별 분석 고객 수이며 캠페인 반응 인원이나 구매 예상치가 아닙니다."
    )
    st.markdown(
        f'<div class="detail-card"><div class="detail-heading">선택 세그먼트 · {escape(segment)}</div>'
        f'<div class="section-caption">{escape(caution)}</div></div>',
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns([1, 1, 1], gap="small")
    with c1:
        st.markdown(
            f'<div class="detail-block"><div class="detail-label">WHO · 대상</div>'
            f'<div class="detail-value">성수기 {fmt_count(int(hot["customer_count"]))}<br>'
            f'비수기 {fmt_count(int(cold["customer_count"]))}</div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div class="detail-block"><div class="detail-label">WHY · D5 근거</div>'
            f'<div class="detail-value">성수기 매출 비중 {fmt_pct(float(hot["sales_share_pct"]))} · 구매자당 {fmt_money(float(hot["ppc"]), 2)}<br>'
            f'비수기 매출 비중 {fmt_pct(float(cold["sales_share_pct"]))} · 구매자당 {fmt_money(float(cold["ppc"]), 2)}</div></div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f'<div class="detail-block"><div class="detail-label">MEASURE · D7 지표</div>'
            f'<div class="detail-value">{escape(D7_METRICS[segment])}</div>'
            f'<span class="source-chip">P1 · D4</span> '
            f'<span class="source-chip">P2 · D5</span> '
            f'<span class="source-chip">P3 · D7</span></div>',
            unsafe_allow_html=True,
        )
    c4, c5 = st.columns(2, gap="small")
    with c4:
        st.markdown(
            f'<div class="detail-season hot"><div class="detail-season-name">성수기 · {escape(hot_info["badge"])}</div>'
            f'<div class="detail-count">{escape(segment)}</div>'
            f'<div class="detail-action">{escape(hot_info["action"])}</div></div>',
            unsafe_allow_html=True,
        )
    with c5:
        st.markdown(
            f'<div class="detail-season cold"><div class="detail-season-name">비수기 · {escape(cold_info["badge"])}</div>'
            f'<div class="detail-count">{escape(segment)}</div>'
            f'<div class="detail-action">{escape(cold_info["action"])}</div></div>',
            unsafe_allow_html=True,
        )
    st.caption("실행 초안이며 팀 확정이 필요합니다.")


def build_page3_insights() -> list[dict[str, str]]:
    hot_priority = [
        segment for segment in SEGMENT_ORDER
        if D7_MATRIX[segment]["성수기"]["badge"] == "최우선"
    ]
    cold_priority = [
        segment for segment in SEGMENT_ORDER
        if D7_MATRIX[segment]["비수기"]["badge"] == "최우선"
    ]
    hot_risk = int(segment_row("성수기", "이탈 위험")["customer_count"])
    cold_risk = int(segment_row("비수기", "이탈 위험")["customer_count"])
    hot_summary = D7_STRATEGY_SUMMARY[D7_STRATEGY_SUMMARY["season"] == "성수기"].iloc[0]
    cold_summary = D7_STRATEGY_SUMMARY[D7_STRATEGY_SUMMARY["season"] == "비수기"].iloc[0]
    return [
        {
            "type": "① WHAT HAPPENED · 관찰",
            "title": "시즌별 최우선 타깃",
            "metric": f"성수기 · {' · '.join(hot_priority)}",
            "compare": f"비수기 · {' · '.join(cold_priority)}",
            "interpretation": "D7 우선순위에 따라 집중 고객군이 시즌별로 달라집니다.",
            "action": "선택 시즌의 매트릭스와 액션을 기준으로 실행안을 정렬합니다.",
            "source": "근거 D7",
        },
        {
            "type": "② WHY IT MATTERS · 의미",
            "title": "공통 검토 대상",
            "metric": f"성수기 {fmt_count(hot_risk)}",
            "compare": f"비수기 {fmt_count(cold_risk)} · 비수기는 소표본",
            "interpretation": "이탈 위험은 두 시즌 공통 재활성화 검토 대상이나, 비수기 결과 해석에 주의가 필요합니다.",
            "action": D7_COMMON_INSIGHT,
            "source": "근거 D5 · D7",
        },
        {
            "type": "③ WHAT TO DO · 실행",
            "title": "실행 원칙",
            "metric": str(hot_summary["strategy"]),
            "compare": str(cold_summary["strategy"]),
            "interpretation": D7_COMMON_INSIGHT,
            "action": D7_EXECUTION_NOTICE,
            "source": "근거 D7",
        },
    ]


def page3() -> None:
    render_header(
        "SEASON × SEGMENT PRIORITY",
        "시즌 × 세그먼트 우선순위 → 실행전략",
        "핵심 질문 · 어느 시즌에 어떤 세그먼트부터 자원을 투입할 것인가?",
    )
    st.markdown(
        f'<div class="conclusion-banner"><span class="conclusion-tag">결론</span>'
        f'<div><div class="conclusion-copy">성수기에는 단골 유지에, 비수기에는 재구매 유도와 휴면 리마인드에 자원을 우선 투입합니다.</div>'
        f'<div class="conclusion-sub">{escape(D7_EXECUTION_NOTICE)} · 비용·반응률 데이터 없이 ROI를 추정하지 않습니다.</div></div></div>',
        unsafe_allow_html=True,
    )
    st.segmented_control(
        "전략 시즌",
        ["성수기", "비수기"],
        key="priority_season",
        label_visibility="collapsed",
    )
    season = st.session_state.priority_season

    st.markdown('<div class="section-heading">시즌별 우선순위 매트릭스</div>', unsafe_allow_html=True)
    st.caption("셀은 D7의 정확한 우선순위와 핵심 액션을 표시합니다. ● 최우선 · ○ 보조.")
    st.pills(
        "매트릭스 세그먼트 선택",
        SEGMENT_ORDER,
        selection_mode="multi",
        key="page3_matrix_segments",
        label_visibility="collapsed",
    )
    matrix_segments = list(st.session_state.page3_matrix_segments)
    render_priority_matrix(season, matrix_segments)

    selected = (
        matrix_segments[0]
        if matrix_segments
        else st.session_state.page3_segment
    )
    st.markdown('<div class="section-heading">세그먼트 액션 상세</div>', unsafe_allow_html=True)
    st.caption("세그먼트를 선택하면 인라인 상세 카드가 갱신되고, 기존 상세 모달도 열립니다.")
    cols = st.columns(3, gap="small")
    for index, segment in enumerate(SEGMENT_ORDER):
        with cols[index % 3]:
            if st.button(
                segment,
                key=f"segment_action_{segment}",
                type="primary" if selected == segment else "secondary",
                width="stretch",
            ):
                st.session_state.page3_segment = segment
                show_segment_modal(segment)

    render_segment_detail(selected)

    left, right = st.columns([1.25, 1], gap="medium")
    with left:
        st.markdown('<div class="section-heading">비교용 기회 규모</div>', unsafe_allow_html=True)
        st.segmented_control(
            "기회 규모 시즌",
            ["성수기", "비수기"],
            key="opportunity_season",
            label_visibility="collapsed",
        )
        opportunity_season = st.session_state.opportunity_season
        st.caption(f"D5 고객 수 × 구매자당 매출 · {opportunity_season} · 비교용 규모 지표")
        rows = []
        for segment in SEGMENT_ORDER:
            row = segment_row(opportunity_season, segment)
            customer_count = int(row["customer_count"])
            ppc = float(row["ppc"])
            rows.append(
                {
                    "segment": segment,
                    "customer_count": customer_count,
                    "ppc": ppc,
                    "scale": customer_count * ppc,
                }
            )
        opportunity = pd.DataFrame(rows).sort_values("scale", ascending=False)
        fig = go.Figure(
            go.Bar(
                x=opportunity["scale"],
                y=opportunity["segment"],
                orientation="h",
                marker=dict(
                    color=[SEGMENT_COLORS[segment] for segment in opportunity["segment"]],
                    line=dict(
                        color=[COLORS["Charcoal"] if segment == selected else COLORS["White"] for segment in opportunity["segment"]],
                        width=[3 if segment == selected else 1 for segment in opportunity["segment"]],
                    ),
                ),
                text=[fmt_abbrev(float(value)) for value in opportunity["scale"]],
                textposition="outside",
                cliponaxis=False,
                customdata=opportunity[["customer_count", "ppc"]].to_numpy(),
                hovertemplate=(
                    "%{y}<br>고객 수 %{customdata[0]:,.0f}명"
                    "<br>구매자당 매출 $%{customdata[1]:,.2f}"
                    "<br>산식 고객 수 × 구매자당 매출"
                    "<br>계산 결과 $%{x:,.2f}<extra></extra>"
                ),
            )
        )
        chart_layout(fig, 380).update_layout(
            showlegend=False,
            xaxis=dict(title="고객 수 × 구매자당 매출 ($)", tickformat="~s"),
            yaxis=dict(autorange="reversed", title=None, gridcolor=COLORS["White"]),
        )
        show_chart(fig, "opportunity-scale")
        st.caption("구매자당 매출은 구매 고객 기준이므로 고객 수와 곱한 값은 실제 총매출이나 미래 매출 예측이 아닌 비교용 규모 지표입니다. ROI를 뜻하지 않습니다.")

    with right:
        st.markdown('<div class="section-heading">시즌별 전략 요약</div>', unsafe_allow_html=True)
        strategy_cols = st.columns(2, gap="small")
        for col, target_season, style in zip(strategy_cols, ("성수기", "비수기"), ("hot", "cold")):
            record = D7_STRATEGY_SUMMARY[D7_STRATEGY_SUMMARY["season"] == target_season].iloc[0]
            with col:
                segments = str(record["priority_segments"]).replace(", ", " + ")
                strategy_lines = str(record["strategy"]).replace("와 ", "와<br>")
                metric_lines = str(record["metrics"]).replace(", ", "<br>")
                st.markdown(
                    f'<div class="strategy-card {style}"><div class="strategy-season">{escape(target_season)}</div>'
                    f'<div class="strategy-segments">{escape(segments)}</div>'
                    f'<div class="strategy-line">{strategy_lines}</div>'
                    f'<div class="strategy-line"><strong>움직일 지표</strong><br>{metric_lines}</div></div>',
                    unsafe_allow_html=True,
                )
        st.markdown(
            f'<div class="insight-card action" style="margin-top:12px; min-height:0">'
            f'<div class="insight-type">공통 시사점</div><div class="insight-title">소규모 재활성화 검토</div>'
            f'<div class="insight-copy">{escape(D7_COMMON_INSIGHT)}</div>'
            f'<span class="source-chip">근거 D7</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-heading">실행 로드맵 · 실행 논리 구조</div>', unsafe_allow_html=True)
    st.caption("일정·예산·목표를 뜻하지 않으며 제공된 데이터로 구성한 의사결정 순서입니다.")
    selected_row = segment_row(season, selected)
    selected_action = D7_MATRIX[selected][season]["action"]
    roadmap = [
        ("01 · WHO", "대상 선정", f"{selected} · {fmt_count(int(selected_row['customer_count']))}"),
        ("02 · WHY", "데이터 근거", f"매출 비중 {fmt_pct(float(selected_row['sales_share_pct']))} · 구매자당 {fmt_money(float(selected_row['ppc']), 2)}"),
        ("03 · WHAT", "핵심 캠페인", selected_action),
        ("04 · MEASURE", "성과 지표", D7_METRICS[selected]),
    ]
    cols = st.columns(4, gap="small")
    for col, (step, title, body) in zip(cols, roadmap):
        with col:
            st.markdown(
                f'<div class="roadmap-step"><div class="roadmap-no">{escape(step)}</div>'
                f'<div class="roadmap-title">{escape(title)}</div><div class="roadmap-text">{escape(body)}</div></div>',
                unsafe_allow_html=True,
            )

    render_insight_board(build_page3_insights())
    render_footnotes()


@st.dialog("세그먼트 액션 상세")
def show_segment_modal(segment: str) -> None:
    st.markdown(f"### {segment}")
    columns = st.columns(2, gap="medium")
    for col, season in zip(columns, ("성수기", "비수기")):
        row = segment_row(season, segment)
        with col:
            st.metric(f"{season} 대상 고객", fmt_count(int(row["customer_count"])))
            st.metric("매출 비중", fmt_pct(float(row["sales_share_pct"])))
            st.metric("구매자당 매출", fmt_money(float(row["ppc"]), 2))
            st.write("우선순위", D7_MATRIX[segment][season]["badge"])
            st.write("핵심 액션", D7_MATRIX[segment][season]["action"])
    st.write("움직일 지표", D7_METRICS[segment])
    st.caption("근거 P2 · D5 / P3 · D7 · 전략 초안으로 팀 확정이 필요합니다.")
    st.info("전략 초안 · 팀 확정 필요")


tabs = st.tabs(
    [
        "시즌별 고객 행동",
        "RFM 세그먼트 분석",
        "시즌 × 세그먼트 우선순위 → 실행전략",
    ]
)
with tabs[0]:
    page1()
with tabs[1]:
    page2()
with tabs[2]:
    page3()
