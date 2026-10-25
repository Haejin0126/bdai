import pandas as pd

COLORS = {
    "Primary Indigo": "#1501A5",
    "Royal Violet": "#584CCE",
    "Soft Lavender": "#B7AEF9",
    "Periwinkle": "#A4B3F9",
    "Muted Violet": "#7C7AA4",
    "Light Gray": "#D8D9E1",
    "Canvas Gray": "#F3F5F8",
    "Charcoal": "#0E0D12",
    "White": "#FFFFFF",
    "Text Gray": "#474747",
}

SEASON_COLORS = {
    "성수기": COLORS["Primary Indigo"],
    "비수기": COLORS["Periwinkle"],
}

SEGMENT_COLORS = {
    "챔피언": COLORS["Primary Indigo"],
    "충성 고객": COLORS["Royal Violet"],
    "신규 고객": COLORS["Muted Violet"],
    "이탈 위험": COLORS["Periwinkle"],
    "휴면": COLORS["Soft Lavender"],
    "관심 필요": "#9588D8",
}

SEGMENT_ORDER = [
    "챔피언",
    "충성 고객",
    "신규 고객",
    "이탈 위험",
    "휴면",
    "관심 필요",
]

D1_KPI = pd.DataFrame([
    {"metric": "방문자당 매출(NSM)", "성수기": 116.44, "비수기": 6.77, "unit": "currency"},
    {"metric": "구매 전환율", "성수기": 12.27, "비수기": 1.44, "unit": "percent"},
    {"metric": "구매자당 매출", "성수기": 948.97, "비수기": 470.05, "unit": "currency"},
    {"metric": "30일 내 재구매 고객 수", "성수기": 133320, "비수기": 1992, "unit": "count"},
    {"metric": "조회→장바구니 전환율", "성수기": 19.2, "비수기": 3.0, "unit": "percent"},
    {"metric": "장바구니→구매 전환율", "성수기": 54.5, "비수기": 47.1, "unit": "percent"},
])

D2_FUNNEL = pd.DataFrame([
    {"season": "성수기", "stage": "조회→장바구니", "start_users": 2875055, "reach_users": 550984, "conversion_pct": 19.2, "drop_users": 2324071, "drop_pct": 80.8},
    {"season": "성수기", "stage": "장바구니→구매", "start_users": 550984, "reach_users": 300050, "conversion_pct": 54.5, "drop_users": 250934, "drop_pct": 45.5},
    {"season": "비수기", "stage": "조회→장바구니", "start_users": 678603, "reach_users": 20446, "conversion_pct": 3.0, "drop_users": 658157, "drop_pct": 97.0},
    {"season": "비수기", "stage": "장바구니→구매", "start_users": 20446, "reach_users": 9639, "conversion_pct": 47.1, "drop_users": 10807, "drop_pct": 52.9},
])

D3_MONTHLY = pd.DataFrame([
    {"month": "2019-10", "조회": 1300070, "장바구니": 198219, "구매": 121900, "조회→장바구니(%)": 15.2, "장바구니→구매(%)": 61.5, "장바구니 없이 구매": 38537},
    {"month": "2019-11", "조회": 1574985, "장바구니": 352765, "구매": 178150, "조회→장바구니(%)": 22.4, "장바구니→구매(%)": 50.5, "장바구니 없이 구매": 14275},
    {"month": "2019-12", "조회": 292102, "장바구니": 13002, "구매": 6511, "조회→장바구니(%)": 4.5, "장바구니→구매(%)": 50.1, "장바구니 없이 구매": 56},
    {"month": "2020-01", "조회": 185557, "장바구니": 5604, "구매": 2465, "조회→장바구니(%)": 3.0, "장바구니→구매(%)": 44.0, "장바구니 없이 구매": 45},
    {"month": "2020-02", "조회": 65990, "장바구니": 803, "구매": 197, "조회→장바구니(%)": 1.2, "장바구니→구매(%)": 24.5, "장바구니 없이 구매": 79},
    {"month": "2020-03", "조회": 69961, "장바구니": 496, "구매": 228, "조회→장바구니(%)": 0.7, "장바구니→구매(%)": 46.0, "장바구니 없이 구매": 7},
    {"month": "2020-04", "조회": 64993, "장바구니": 541, "구매": 238, "조회→장바구니(%)": 0.8, "장바구니→구매(%)": 44.0, "장바구니 없이 구매": 1},
])

D4_REPURCHASE = pd.DataFrame([
    {"season": "성수기", "stage": "첫 구매", "reach_users": 322110, "prior_step_conversion_pct": None, "first_purchase_pct": 100.0},
    {"season": "성수기", "stage": "2회 이상", "reach_users": 98315, "prior_step_conversion_pct": 30.5, "first_purchase_pct": 30.5},
    {"season": "성수기", "stage": "3회 이상", "reach_users": 44452, "prior_step_conversion_pct": 45.2, "first_purchase_pct": 13.8},
    {"season": "성수기", "stage": "4회 이상", "reach_users": 25018, "prior_step_conversion_pct": 56.3, "first_purchase_pct": 7.8},
    {"season": "비수기", "stage": "첫 구매", "reach_users": 7030, "prior_step_conversion_pct": None, "first_purchase_pct": 100.0},
    {"season": "비수기", "stage": "2회 이상", "reach_users": 916, "prior_step_conversion_pct": 13.0, "first_purchase_pct": 13.0},
    {"season": "비수기", "stage": "3회 이상", "reach_users": 277, "prior_step_conversion_pct": 30.2, "first_purchase_pct": 3.9},
    {"season": "비수기", "stage": "4회 이상", "reach_users": 120, "prior_step_conversion_pct": 43.3, "first_purchase_pct": 1.7},
])

SEGMENT_SUMMARY = {
    "성수기": pd.DataFrame([
        {"segment": "챔피언", "customer_count": 11819, "customer_share_pct": 3.7, "sales_share_pct": 20.6, "ppc": 5848.77, "prior_purchase_rate": None},
        {"segment": "충성 고객", "customer_count": 58932, "customer_share_pct": 18.3, "sales_share_pct": 31.7, "ppc": 1802.11, "prior_purchase_rate": None},
        {"segment": "신규 고객", "customer_count": 79775, "customer_share_pct": 24.8, "sales_share_pct": 11.7, "ppc": 492.36, "prior_purchase_rate": None},
        {"segment": "이탈 위험", "customer_count": 12908, "customer_share_pct": 4.0, "sales_share_pct": 11.2, "ppc": 1736.35, "prior_purchase_rate": None},
        {"segment": "휴면", "customer_count": 116777, "customer_share_pct": 36.3, "sales_share_pct": 19.0, "ppc": 543.81, "prior_purchase_rate": None},
        {"segment": "관심 필요", "customer_count": 41899, "customer_share_pct": 13.0, "sales_share_pct": 5.8, "ppc": 462.91, "prior_purchase_rate": None},
    ]),
    "비수기": pd.DataFrame([
        {"segment": "챔피언", "customer_count": 226, "customer_share_pct": 2.4, "sales_share_pct": 7.2, "ppc": 1465.81, "prior_purchase_rate_pct": 30.5},
        {"segment": "충성 고객", "customer_count": 755, "customer_share_pct": 7.9, "sales_share_pct": 17.9, "ppc": 1095.39, "prior_purchase_rate_pct": 28.2},
        {"segment": "신규 고객", "customer_count": 3135, "customer_share_pct": 32.7, "sales_share_pct": 23.3, "ppc": 343.58, "prior_purchase_rate_pct": 17.7},
        {"segment": "이탈 위험", "customer_count": 143, "customer_share_pct": 1.5, "sales_share_pct": 5.0, "ppc": 1616.55, "prior_purchase_rate_pct": 54.5},
        {"segment": "휴면", "customer_count": 3747, "customer_share_pct": 39.1, "sales_share_pct": 33.8, "ppc": 416.66, "prior_purchase_rate_pct": 29.6},
        {"segment": "관심 필요", "customer_count": 1573, "customer_share_pct": 16.4, "sales_share_pct": 12.8, "ppc": 375.96, "prior_purchase_rate_pct": 19.2},
    ]),
}

D6_KPI = pd.DataFrame([
    {"metric": "분석 고객 수", "성수기": 322110, "비수기": 9579, "unit": "count"},
    {"metric": "단골 고객 비중", "성수기": 22.0, "비수기": 10.3, "unit": "percent"},
    {"metric": "매출 1위 세그먼트", "성수기": "충성 고객", "비수기": "휴면", "unit": "text"},
    {"metric": "매출 1위 매출 비중", "성수기": 31.7, "비수기": 33.8, "unit": "percent"},
    {"metric": "이탈 위험 구매자당 매출", "성수기": 1736, "비수기": 1617, "unit": "currency"},
])

D7_MATRIX = {
    "챔피언": {
        "성수기": {"priority": "●", "action": "VIP 선예약권, 전용 사은품 패키지", "badge": "최우선"},
        "비수기": {"priority": "○", "action": "프리미엄 선공개, 번들·업셀로 씀씀이 유지", "badge": "보조"},
    },
    "충성 고객": {
        "성수기": {"priority": "●", "action": "연계 기기·액세서리 패키지, 금액 구간 적립", "badge": "최우선"},
        "비수기": {"priority": "○", "action": "추천인 프로그램, 재구매 유도로 고객 수 이탈 방지", "badge": "보조"},
    },
    "신규 고객": {
        "성수기": {"priority": "○", "action": "웰컴 쿠폰, 저비용 채널 온보딩", "badge": "보조"},
        "비수기": {"priority": "●", "action": "첫 구매 후 액세서리 쿠폰으로 두 번째 구매 유도", "badge": "최우선"},
    },
    "이탈 위험": {
        "성수기": {"priority": "●", "action": "관심 행동이 확인된 고객부터 소규모 재활성화 파일럿", "badge": "공통 재활성화 검토"},
        "비수기": {"priority": "●", "action": "최소 구매금액·할인 한도를 둔 윈백 쿠폰", "badge": "공통 재활성화 검토"},
    },
    "휴면": {
        "성수기": {"priority": "○", "action": "신제품 소식 중심 저비용 푸시", "badge": "보조"},
        "비수기": {"priority": "●", "action": "저비용 리마인드, 세트 구매 혜택으로 객단가 상승 유도", "badge": "최우선"},
    },
    "관심 필요": {
        "성수기": {"priority": "○", "action": "자동화 프로모션 노출", "badge": "보조"},
        "비수기": {"priority": "○", "action": "A/B 테스트로 두 번째 구매 유도 메시지 탐색", "badge": "보조"},
    },
}

D7_METRICS = {
    "챔피언": "재구매 고객 수",
    "충성 고객": "재구매 고객 수",
    "신규 고객": "첫 구매→재구매 전환율",
    "이탈 위험": "재구매 고객 수",
    "휴면": "전체 고객 수",
    "관심 필요": "전환율, 재구매 고객",
}

D7_STRATEGY_SUMMARY = pd.DataFrame([
    {"season": "성수기", "priority_segments": "챔피언, 충성 고객", "strategy": "단골 유지와 구매자당 매출 확대", "metrics": "재구매 고객 수, 구매자당 매출"},
    {"season": "비수기", "priority_segments": "신규, 휴면 고객", "strategy": "재구매 유도, 휴면 리마인드, 장바구니 리마인드(보조)", "metrics": "첫 구매→재구매 전환율, 전체 고객 수"},
])

D7_COMMON_INSIGHT = (
    "두 시즌 모두 구매자당 매출이 높은 이탈 위험 고객은 관심 행동이 확인된 고객부터 "
    "소규모 재활성화를 시험합니다."
)

D7_EXECUTION_NOTICE = "전략 초안 · 팀 확정 필요"

D8_RFM_CUTOFFS = {
    "성수기": "2019-11-30",
    "비수기": "2020-04-30",
}

RFM_DEFINITIONS = [
    ("챔피언", "R≥5, F≥5, M≥5"),
    ("충성", "F≥4, R≥3"),
    ("신규", "R≥4, 구매 1회"),
    ("이탈 위험", "R≤2, F≥3"),
    ("휴면", "R≤2"),
    ("관심 필요", "나머지"),
]

FOOTNOTES = [
    "장바구니 없이 구매한 사용자는 퍼널에서 제외합니다.",
    "퍼널 판정 단위는 사용자-월이며, 같은 달 안의 이벤트만 인정합니다.",
    "시즌 값은 월별 도달 인원의 합산입니다.",
    "12월 이후 이벤트 급감은 데이터 수집 영향 가능성이 있으므로 비수기 값을 경향으로 해석합니다.",
    "세그먼트는 시즌별 RFM 5분위와 기준일로 나누므로 시즌 간 직접 비교에 한계가 있습니다.",
    "RFM 기준일: 성수기 2019-11-30, 비수기 2020-04-30.",
    "신규는 시즌 내 첫 구매 기준입니다.",
    "비수기 신규 고객의 17.7%는 이전 시즌 구매 경험이 있습니다.",
    "비수기 이탈 위험 143명은 소표본으로 참고용입니다.",
    "수량, 비용, 채널, 캠페인 반응률 데이터는 제공되지 않았습니다.",
]

MONTHS = ["2019-10", "2019-11", "2019-12", "2020-01", "2020-02", "2020-03", "2020-04"]
SEASON_MONTHS = {
    "성수기": MONTHS[:2],
    "비수기": MONTHS[2:],
}
SEASON_PERIODS = {
    season: (months[0], months[-1])
    for season, months in SEASON_MONTHS.items()
}
