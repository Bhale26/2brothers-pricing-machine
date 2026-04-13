import streamlit as st
import pandas as pd
from dataclasses import dataclass
from typing import Optional, Dict, List

st.set_page_config(page_title="2 Brothers Pricing Machine", layout="wide")

# =========================================================
# LOGIN / ACCESS CONTROL
# =========================================================

ALLOWED_EMAILS = {
    "braxton@2brotherswindows.com",
    "ben@2brotherswindows.com",
    "karsen@2brotherswindows.com",
}

def login_gate() -> None:
    user_email = str(st.user.get("email", "")).lower().strip()

    if not user_email:
        st.title("2 Brothers Pricing Machine")
        st.subheader("Employee Login")

        if st.button("Login with Microsoft", use_container_width=True):
            st.login("microsoft")

        st.stop()

    allowed = {email.lower().strip() for email in ALLOWED_EMAILS}
    if user_email not in allowed:
        st.error("You do not have access to this app.")
        if st.button("Log out", use_container_width=True):
            st.logout()
        st.stop()

    left, right = st.columns([5, 1])
    with left:
        st.caption(f"Logged in as: {user_email}")
    with right:
        if st.button("Log out", use_container_width=True):
            st.logout()

login_gate()

# =========================================================
# CONSTANTS
# =========================================================

GM = 0.60
FINANCING_MULTIPLIER = 1.15
INBOUND_MULTIPLIER = 1.30
D2D_MULTIPLIER = 1.50
STUCCO_PER_WINDOW = 500
FREIGHT_CHARGE = 350

COLOR_OPTIONS = [
    "White",
    "Taupe",
    "Black (Ext) / White (Int)",
    "Bronze (Ext) / White (Int)",
    "Black (Ext & Int)",
    "Bronze (Ext & Int)",
]

WINDOW_TYPES = [
    "Horizontal Slider",
    "Double Vent",
    "Single Hung",
    "Fixed",
    "Half Circle",
    "Specialty Shape",
    "Casement",
    "Awning",
    "Sliding Glass Door",
]

SIZE_OPTIONS = ["<25", ">25"]
DOOR_PANEL_OPTIONS = ["2 Panel", "3 Panel", "4 Panel"]

BRANDS = [
    "AMSCO Studio",
    "AMSCO Hampton",
    "Andersen 100",
    "Marvin Essential",
]

# =========================================================
# DATA MODEL
# =========================================================

@dataclass
class LineItem:
    window_type: str
    size_bucket: str
    color_config: str
    glass_package: str
    tempered: bool
    privacy: bool
    grids: bool
    stucco: bool
    qty: int
    door_panels: Optional[str] = None

# =========================================================
# PRICING DATA
# =========================================================

BASE_PRICES: Dict[str, Dict[str, float]] = {
    "AMSCO Studio": {
        "Horizontal Slider|<25": 195,
        "Horizontal Slider|>25": 245,
        "Double Vent": 450,
        "Single Hung": 200,
        "Fixed|<25": 140,
        "Fixed|>25": 205,
        "Half Circle": 200,
        "Specialty Shape": 500,
        "Sliding Glass Door|2 Panel": 760,
        "Sliding Glass Door|3 Panel": 1085,
        "Sliding Glass Door|4 Panel": 1730,
    },
    "AMSCO Hampton": {
        "Horizontal Slider|<25": 305,
        "Horizontal Slider|>25": 380,
        "Double Vent": 645,
        "Single Hung": 300,
        "Fixed|<25": 240,
        "Fixed|>25": 365,
        "Half Circle": 260,
        "Specialty Shape": 560,
        "Casement": 480,
        "Awning": 453,
        "Sliding Glass Door|2 Panel": 760,
        "Sliding Glass Door|3 Panel": 1085,
        "Sliding Glass Door|4 Panel": 1730,
    },
    "Marvin Essential": {
        "Horizontal Slider|<25": 750,
        "Horizontal Slider|>25": 900,
        "Double Vent": 2500,
        "Single Hung": 650,
        "Fixed|<25": 1000,
        "Fixed|>25": 1000,
        "Half Circle": 1100,
        "Specialty Shape": 1200,
        "Casement": 890,
        "Awning": 890,
        "Sliding Glass Door|2 Panel": 2300,
    },
}

COLOR_MULTIPLIERS: Dict[str, Dict[str, float]] = {
    "AMSCO Studio": {
        "White": 1.00,
        "Taupe": 1.00,
        "Black (Ext) / White (Int)": 1.94,
        "Bronze (Ext) / White (Int)": 1.94,
        "Black (Ext & Int)": 2.50,
        "Bronze (Ext & Int)": 3.19,
    },
    "AMSCO Hampton": {
        "White": 1.00,
        "Taupe": 1.05,
        "Black (Ext) / White (Int)": 1.62,
        "Bronze (Ext) / White (Int)": 1.74,
        "Black (Ext & Int)": 2.42,
        "Bronze (Ext & Int)": 2.42,
    },
    "Marvin Essential": {
        "White": 1.00,
        "Taupe": 1.08,
        "Black (Ext) / White (Int)": 1.18,
        "Bronze (Ext) / White (Int)": 1.18,
        "Black (Ext & Int)": 1.05,
        "Bronze (Ext & Int)": 1.05,
    },
}

ANDERSEN_COLOR_TABLES: Dict[str, Dict[str, float]] = {
    "White": {
        "Horizontal Slider|<25": 495,
        "Horizontal Slider|>25": 670,
        "Single Hung|<25": 450,
        "Single Hung|>25": 550,
        "Double Vent": 1200,
        "Fixed|<25": 440,
        "Fixed|>25": 550,
        "Half Circle|<25": 530,
        "Half Circle|>25": 640,
        "Specialty Shape": 1800,
        "Casement": 700,
        "Awning": 630,
        "Sliding Glass Door|2 Panel": 1500,
        "Sliding Glass Door|3 Panel": 4000,
        "Sliding Glass Door|4 Panel": 5000,
    },
    "Black (Ext) / White (Int)": {
        "Horizontal Slider|<25": 570,
        "Horizontal Slider|>25": 750,
        "Single Hung|<25": 520,
        "Single Hung|>25": 640,
        "Double Vent": 1250,
        "Fixed|<25": 510,
        "Fixed|>25": 630,
        "Half Circle|<25": 590,
        "Half Circle|>25": 710,
        "Specialty Shape": 1900,
        "Casement": 750,
        "Awning": 700,
        "Sliding Glass Door|2 Panel": 1650,
        "Sliding Glass Door|3 Panel": 4000,
        "Sliding Glass Door|4 Panel": 5000,
    },
    "Black (Ext & Int)": {
        "Horizontal Slider|<25": 630,
        "Horizontal Slider|>25": 810,
        "Single Hung|<25": 570,
        "Single Hung|>25": 690,
        "Double Vent": 1300,
        "Fixed|<25": 570,
        "Fixed|>25": 690,
        "Half Circle|<25": 650,
        "Half Circle|>25": 760,
        "Specialty Shape": 1900,
        "Casement": 810,
        "Awning": 760,
        "Sliding Glass Door|2 Panel": 1800,
        "Sliding Glass Door|3 Panel": 4000,
        "Sliding Glass Door|4 Panel": 5000,
    },
}

OPTION_ADDERS: Dict[str, float] = {
    "Tempered": 100,
    "Privacy": 75,
    "Grids": 100,
    "Glass270": 0,
    "Glass366": 60,
    "Glass340": 100,
}

# =========================================================
# HELPERS
# =========================================================

def money(x: float) -> str:
    return f"${x:,.2f}"

def product_sell_from_gm(product_cost: float) -> float:
    return round(product_cost / (1 - GM), 2)

def labor_for_item(brand: str, window_type: str) -> float:
    if brand == "Marvin Essential":
        return 825 if window_type == "Sliding Glass Door" else 375
    return 750 if window_type == "Sliding Glass Door" else 300

def normalize_andersen_color(color_config: str) -> str:
    if color_config == "Bronze (Ext) / White (Int)":
        return "Black (Ext) / White (Int)"
    if color_config == "Bronze (Ext & Int)":
        return "Black (Ext & Int)"
    if color_config == "Taupe":
        return "White"
    return color_config

def get_base_key(item: LineItem, brand: Optional[str] = None) -> str:
    if item.window_type == "Sliding Glass Door":
        return f"Sliding Glass Door|{item.door_panels}"

    if brand == "Andersen 100" and item.window_type in ["Horizontal Slider", "Fixed", "Single Hung", "Half Circle"]:
        return f"{item.window_type}|{item.size_bucket}"

    if brand != "Andersen 100" and item.window_type in ["Horizontal Slider", "Fixed"]:
        return f"{item.window_type}|{item.size_bucket}"

    return item.window_type

def brand_supports_item(brand: str, item: LineItem) -> bool:
    key = get_base_key(item, brand)
    if brand == "Andersen 100":
        color = normalize_andersen_color(item.color_config)
        return key in ANDERSEN_COLOR_TABLES.get(color, {})
    return key in BASE_PRICES.get(brand, {})

def item_is_window(item: LineItem) -> bool:
    return item.window_type != "Sliding Glass Door"

def compute_unit_product_cost(brand: str, item: LineItem) -> float:
    key = get_base_key(item, brand)

    if brand == "Andersen 100":
        color = normalize_andersen_color(item.color_config)
        product = ANDERSEN_COLOR_TABLES[color][key]
    else:
        base_price = BASE_PRICES[brand][key]
        color_mult = COLOR_MULTIPLIERS[brand][item.color_config]
        product = base_price * color_mult

    if item.tempered and item.window_type != "Sliding Glass Door":
        product += OPTION_ADDERS["Tempered"]
    if item.privacy:
        product += OPTION_ADDERS["Privacy"]
    if item.grids:
        product += OPTION_ADDERS["Grids"]

    product += OPTION_ADDERS[f"Glass{item.glass_package}"]

    return round(product, 2)

def compute_unit_final_price(brand: str, item: LineItem) -> Dict[str, float]:
    product_cost = compute_unit_product_cost(brand, item)
    product_sell = product_sell_from_gm(product_cost)
    labor = labor_for_item(brand, item.window_type)
    final_unit = round(product_sell + labor, 2)

    return {
        "product_cost": round(product_cost, 2),
        "product_sell": round(product_sell, 2),
        "labor": round(labor, 2),
        "final_unit": round(final_unit, 2),
    }

def compute_quote_totals(items: List[LineItem], financing: bool, inbound: bool, d2d: bool) -> Dict[str, Dict[str, float]]:
    results = {}

    for brand in BRANDS:
        product_sell_total = 0.0
        labor_total = 0.0
        unavailable = False
        stucco_count = 0

        for item in items:
            if not brand_supports_item(brand, item):
                unavailable = True
                continue

            unit = compute_unit_final_price(brand, item)
            product_sell_total += unit["product_sell"] * item.qty
            labor_total += unit["labor"] * item.qty

            if item.stucco and item_is_window(item):
                stucco_count += item.qty

        stucco_total = stucco_count * STUCCO_PER_WINDOW
        freight = FREIGHT_CHARGE if (product_sell_total + labor_total + stucco_total) > 0 else 0

        subtotal = product_sell_total + labor_total + stucco_total + freight
        final_total = subtotal

        if financing:
            final_total *= FINANCING_MULTIPLIER

        if d2d:
            final_total *= D2D_MULTIPLIER
        elif inbound:
            final_total *= INBOUND_MULTIPLIER

        results[brand] = {
            "product_sell_total": round(product_sell_total, 2),
            "labor_total": round(labor_total, 2),
            "stucco_total": round(stucco_total, 2),
            "freight": round(freight, 2),
            "subtotal_before_financing": round(subtotal, 2),
            "final_total": round(final_total, 2),
            "has_unavailable_items": unavailable,
        }

    return results

def items_to_editor_df(items: List[LineItem]) -> pd.DataFrame:
    rows = []
    for idx, item in enumerate(items, start=1):
        rows.append({
            "Type": item.window_type,
            "Size": item.size_bucket,
            "Panels": item.door_panels if item.door_panels else "",
            "Color": item.color_config,
            "Glass": item.glass_package,
            "Tempered": True if item.window_type == "Sliding Glass Door" else item.tempered,
            "Privacy": item.privacy,
            "Grids": item.grids,
            "Stucco": item.stucco,
            "Qty": item.qty,
            "Line #": idx,
        })
    return pd.DataFrame(rows)

def editor_df_to_items(df: pd.DataFrame) -> List[LineItem]:
    items: List[LineItem] = []

    for _, row in df.iterrows():
        window_type = str(row["Type"])
        size_bucket = str(row["Size"]) if pd.notna(row["Size"]) and str(row["Size"]).strip() else "<25"
        panels = str(row["Panels"]) if pd.notna(row["Panels"]) and str(row["Panels"]).strip() else None
        color = str(row["Color"])
        glass = str(row["Glass"])
        tempered = True if str(row["Type"]) == "Sliding Glass Door" else bool(row["Tempered"])
        privacy = bool(row["Privacy"])
        grids = bool(row["Grids"])
        stucco = bool(row["Stucco"])
        qty = int(row["Qty"])

        if window_type not in ["Horizontal Slider", "Fixed", "Single Hung", "Half Circle"]:
            size_bucket = "<25"

        if window_type != "Sliding Glass Door":
            panels = None

        items.append(
            LineItem(
                window_type=window_type,
                size_bucket=size_bucket,
                color_config=color,
                glass_package=glass,
                tempered=tempered,
                privacy=privacy,
                grids=grids,
                stucco=stucco,
                qty=qty,
                door_panels=panels,
            )
        )

    return items

def brand_breakdown_dataframe(items: List[LineItem], brand: str) -> pd.DataFrame:
    rows = []
    for idx, item in enumerate(items, start=1):
        if not brand_supports_item(brand, item):
            rows.append({
                "Line #": idx,
                "Type": item.window_type,
                "Qty": item.qty,
                "Status": "Unavailable",
                "Product Sell": None,
                "Labor": None,
                "Unit Total": None,
                "Line Total": None,
            })
            continue

        unit = compute_unit_final_price(brand, item)
        rows.append({
            "Line #": idx,
            "Type": item.window_type,
            "Qty": item.qty,
            "Status": "OK",
            "Product Sell": unit["product_sell"],
            "Labor": unit["labor"],
            "Unit Total": unit["final_unit"],
            "Line Total": round(unit["final_unit"] * item.qty, 2),
        })
    return pd.DataFrame(rows)

# =========================================================
# SESSION STATE
# =========================================================

if "quote_items" not in st.session_state:
    st.session_state["quote_items"] = []

if "financing" not in st.session_state:
    st.session_state["financing"] = False

if "inbound" not in st.session_state:
    st.session_state["inbound"] = False

if "d2d" not in st.session_state:
    st.session_state["d2d"] = False

# =========================================================
# UI
# =========================================================

st.title("2 Brothers Window Pricing Machine")

st.subheader("Quote Options")
opt1, opt2, opt3 = st.columns(3)
with opt1:
    st.checkbox("Financing", key="financing")
with opt2:
    st.checkbox("Inbound", key="inbound")
with opt3:
    st.checkbox("D2D", key="d2d")

st.divider()

left, right = st.columns([1.0, 1.5], gap="large")

with left:
    st.subheader("Add Line Item")

    window_type = st.selectbox("Type", WINDOW_TYPES, key="form_window_type")

    show_size = window_type in ["Horizontal Slider", "Fixed", "Single Hung", "Half Circle"]
    show_panels = window_type == "Sliding Glass Door"

    if show_size:
        size_bucket = st.selectbox("Size Bucket", SIZE_OPTIONS, key="form_size_bucket")
    else:
        size_bucket = "<25"

    if show_panels:
        door_panels = st.selectbox("Door Panels", DOOR_PANEL_OPTIONS, key="form_door_panels")
    else:
        door_panels = None

    color_config = st.selectbox("Color Configuration", COLOR_OPTIONS, key="form_color_config")
    glass_package = st.selectbox("Glass Package", ["270", "366", "340"], key="form_glass_package")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        tempered = st.checkbox(
            "Tempered",
            value=True if window_type == "Sliding Glass Door" else False,
            key="form_tempered",
        )
    with c2:
        privacy = st.checkbox("Privacy", key="form_privacy")
    with c3:
        grids = st.checkbox("Grids", key="form_grids")
    with c4:
        stucco = st.checkbox("Stucco", key="form_stucco")

    qty = st.number_input("Qty", min_value=1, step=1, value=1, key="form_qty")

    new_item = LineItem(
        window_type=window_type,
        size_bucket=size_bucket,
        color_config=color_config,
        glass_package=glass_package,
        tempered=True if window_type == "Sliding Glass Door" else tempered,
        privacy=privacy,
        grids=grids,
        stucco=stucco,
        qty=int(qty),
        door_panels=door_panels,
    )

    st.markdown("**Unit Price Preview**")
    preview_cols = st.columns(4)
    for i, brand in enumerate(BRANDS):
        if brand_supports_item(brand, new_item):
            unit = compute_unit_final_price(brand, new_item)
            preview_cols[i].metric(brand, money(unit["final_unit"]))
        else:
            preview_cols[i].metric(brand, "N/A")

    if st.button("Add Line Item", type="primary", use_container_width=True):
        st.session_state["quote_items"].append(new_item)
        st.rerun()

with right:
    st.subheader("Quote Line Items")

    if not st.session_state["quote_items"]:
        st.info("No line items yet.")
    else:
        st.markdown("**Edit line items directly below**")

        editor_df = items_to_editor_df(st.session_state["quote_items"])

        edited_df = st.data_editor(
            editor_df,
            use_container_width=True,
            hide_index=True,
            num_rows="fixed",
            column_config={
                "Type": st.column_config.SelectboxColumn("Type", options=WINDOW_TYPES, required=True),
                "Size": st.column_config.SelectboxColumn("Size", options=SIZE_OPTIONS),
                "Panels": st.column_config.SelectboxColumn("Panels", options=["", *DOOR_PANEL_OPTIONS]),
                "Color": st.column_config.SelectboxColumn("Color", options=COLOR_OPTIONS, required=True),
                "Glass": st.column_config.SelectboxColumn("Glass", options=["270", "366", "340"], required=True),
                "Tempered": st.column_config.CheckboxColumn("Tempered"),
                "Privacy": st.column_config.CheckboxColumn("Privacy"),
                "Grids": st.column_config.CheckboxColumn("Grids"),
                "Stucco": st.column_config.CheckboxColumn("Stucco"),
                "Qty": st.column_config.NumberColumn("Qty", min_value=1, step=1, required=True),
                "Line #": st.column_config.NumberColumn("Line #", disabled=True),
            },
            key="quote_items_editor",
        )

        col_apply, col_remove, col_clear = st.columns(3)

        with col_apply:
            if st.button("Apply Line Item Changes", type="primary", use_container_width=True):
                st.session_state["quote_items"] = editor_df_to_items(edited_df)
                st.rerun()

        with col_remove:
            remove_line = st.number_input(
                "Delete line #",
                min_value=1,
                max_value=len(st.session_state["quote_items"]),
                value=1,
                step=1,
                key="delete_line_num_inline",
            )
            if st.button("Delete Selected Line", use_container_width=True):
                idx = int(remove_line) - 1
                st.session_state["quote_items"].pop(idx)
                st.rerun()

        with col_clear:
            if st.button("Clear Entire Quote", use_container_width=True):
                st.session_state["quote_items"] = []
                st.rerun()

        st.divider()

        totals = compute_quote_totals(
            st.session_state["quote_items"],
            financing=st.session_state["financing"],
            inbound=st.session_state["inbound"],
            d2d=st.session_state["d2d"],
        )

        st.subheader("All 4 Prices At Once")
        total_cols = st.columns(4)
        for i, brand in enumerate(BRANDS):
            total_cols[i].metric(brand, money(totals[brand]["final_total"]))

        st.divider()

        st.subheader("Brand Breakdown")
        selected_brand = st.selectbox("Show breakdown for", BRANDS)

        breakdown = totals[selected_brand]

        if st.session_state["d2d"]:
            lead_label = "D2D"
        elif st.session_state["inbound"]:
            lead_label = "Inbound"
        else:
            lead_label = "None"

        bc1, bc2, bc3, bc4, bc5, bc6 = st.columns(6)
        bc1.metric("Product Total", money(breakdown["product_sell_total"]))
        bc2.metric("Labor Total", money(breakdown["labor_total"]))
        bc3.metric("Stucco Total", money(breakdown["stucco_total"]))
        bc4.metric("Freight", money(breakdown["freight"]))
        bc5.metric("Financing", "On" if st.session_state["financing"] else "Off")
        bc6.metric("Lead Type", lead_label)

        st.metric("Final Total", money(breakdown["final_total"]))

        if breakdown["has_unavailable_items"]:
            st.warning(f"{selected_brand} has one or more unavailable items in this quote.")

        st.dataframe(
            brand_breakdown_dataframe(st.session_state["quote_items"], selected_brand),
            use_container_width=True,
            hide_index=True,
        )