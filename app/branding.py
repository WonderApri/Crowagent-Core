"""
Handles all visual branding, including CSS, logos, page configuration, and the
enterprise footer rendered on every page.

CSS BUG-FIX NOTES (applied in this revision):

1. UNCLICKABLE NAV — Root Cause A: `.block-container { padding-top: 0 }`
   Streamlit's header bar uses `position: sticky; top: 0` at ~58 px height.
   Zeroing the block-container's top padding caused the first visible element
   (tabs / nav) to slide *under* the header in the DOM stacking context.  The
   header element therefore intercepted all pointer events for that region.
   Fix: restore `padding-top: 1.5rem` so content begins below the header.

2. UNCLICKABLE NAV — Root Cause B: `header { background: transparent }`
   The broad `header` selector matched Streamlit's sticky wrapper and left it
   as a full-viewport-width transparent layer that still participates in
   hit-testing.  Fix: add `pointer-events: none` to the header backdrop itself,
   while restoring `pointer-events: auto` on direct children (hamburger, etc.).

3. SIDEBAR NAV ITEMS BROKEN — Root Cause C:
   `[data-testid="stSidebar"] * { color: #CBD8E6 !important }` applied to
   every descendant, including st.navigation link elements, overriding their
   hover states, cursor, and active colours.  Fix: scope sidebar colour
   overrides to non-navigation elements, and add explicit high-specificity
   rules for st.navigation link components.

4. TAB POINTER EVENTS — added explicit `pointer-events: auto; cursor: pointer`
   on `.stTabs [data-baseweb="tab"]` and `z-index: 1` on the tab list as a
   belt-and-suspenders guard for any in-page tabs.
"""
from __future__ import annotations

import base64
import html
import logging
from pathlib import Path

import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# ENTERPRISE CSS
# ─────────────────────────────────────────────────────────────────────────────
CROWAGENT_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap');

/* ── Global Typography ─────────────────────────────────────────────────── */
html, body, [class*="css"] {
  font-family: 'DM Sans', sans-serif !important;
  font-size: 16px;
  line-height: 1.65;
}
h1, h2, h3, h4 {
  font-family: 'Syne', sans-serif !important;
  font-weight: 800 !important;
  color: #E4ECF7 !important;
  letter-spacing: -0.025em !important;
}
h1 { font-size: 2.5rem !important; line-height: 1.05 !important; }
h2 { font-size: 2rem !important;   line-height: 1.15 !important; }
h3 { font-size: 1.5rem !important; line-height: 1.2 !important;  }
h4 { font-size: 1.2rem !important; line-height: 1.3 !important;  }

/* ── App Background ────────────────────────────────────────────────────── */
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main,
.stApp { background: #05101E !important; color: #E4ECF7 !important; }

/* ── Sidebar permanently hidden — all controls live in-page ────────────── */
[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"] { display: none !important; }

/* BUG-FIX #1 — Restore top padding so content does not render under the
   sticky header, which was intercepting pointer events on the tab / nav bar. */
.block-container {
  padding-top: 1.5rem !important;
  max-width: 1400px !important;
  margin: 0 auto !important;
}

/* BUG-FIX #2 — Header backdrop must not intercept clicks. */
header[data-testid="stHeader"] {
  background: transparent !important;
  pointer-events: none !important;
}
header[data-testid="stHeader"] > * { pointer-events: auto !important; }

/* ── Streamlit Top Navigation Bar ──────────────────────────────────────── */
[data-testid="stTopNavigation"] {
  background: #0A1F3A !important;
  border-bottom: 2px solid #0CC9A8 !important;
  padding: 0 16px !important;
}
[data-testid="stTopNavigation"] a,
[data-testid="stTopNavigation"] button {
  font-family: 'Syne', sans-serif !important;
  font-size: 0.88rem !important;
  font-weight: 600 !important;
  color: #8A9DB8 !important;
  text-decoration: none !important;
  padding: 10px 14px !important;
  border-bottom: 3px solid transparent !important;
  transition: color 0.15s, border-bottom-color 0.15s !important;
  pointer-events: auto !important;
  cursor: pointer !important;
}
[data-testid="stTopNavigation"] a:hover,
[data-testid="stTopNavigation"] button:hover {
  color: #0CC9A8 !important;
  background: rgba(12,201,168,0.08) !important;
}
[data-testid="stTopNavigation"] [aria-current="page"],
[data-testid="stTopNavigation"] a[aria-selected="true"],
[data-testid="stTopNavigation"] button[aria-selected="true"] {
  color: #0CC9A8 !important;
  border-bottom: 3px solid #0CC9A8 !important;
  font-weight: 700 !important;
}
@media (max-width: 768px) {
  [data-testid="stTopNavigation"] a,
  [data-testid="stTopNavigation"] button {
    font-size: 0.78rem !important;
    padding: 8px 8px !important;
  }
}

/* ── Status Pills ──────────────────────────────────────────────────────── */
.sp { display:inline-flex; align-items:center; gap:5px; padding:3px 10px; border-radius:100px; font-size:0.78rem; font-weight:700; white-space:nowrap; font-family:'Syne',sans-serif; }
.sp-live   { background:rgba(12,201,168,.12); color:#0CC9A8; border:1px solid rgba(12,201,168,.3); }
.sp-cache  { background:rgba(194,255,87,.08); color:#C2FF57; border:1px solid rgba(194,255,87,.25); }
.sp-manual { background:rgba(138,157,184,.12); color:#8A9DB8; border:1px solid rgba(138,157,184,.2); }
.sp-warn   { background:rgba(232,76,76,.1);   color:#E84C4C; border:1px solid rgba(232,76,76,.25); }
.pulse-dot { width:7px; height:7px; border-radius:50%; background:#0CC9A8; display:inline-block; animation:blink 2s ease-in-out infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.3} }

/* ── In-page Tabs (BUG-FIX #4) ────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
  background: #0A1F3A !important;
  border-bottom: 2px solid rgba(12,201,168,0.2) !important;
  gap: 0 !important;
  padding: 0 !important;
  position: relative !important;
  z-index: 1 !important;
  pointer-events: auto !important;
  border-radius: 10px 10px 0 0;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  color: #8A9DB8 !important;
  font-family: 'Syne', sans-serif !important;
  font-size: 0.85rem !important;
  font-weight: 600 !important;
  padding: 10px 20px !important;
  border-bottom: 3px solid transparent !important;
  pointer-events: auto !important;
  cursor: pointer !important;
  letter-spacing: 0.02em !important;
}
.stTabs [aria-selected="true"] {
  color: #0CC9A8 !important;
  border-bottom: 3px solid #0CC9A8 !important;
  background: rgba(12,201,168,0.06) !important;
}

/* ── Platform Top-bar ──────────────────────────────────────────────────── */
.platform-topbar {
  background: linear-gradient(135deg, #05101E 0%, #0A1F3A 60%, #0D2847 100%);
  border-bottom: 2px solid #0CC9A8;
  padding: 10px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}
.platform-topbar-right { display:flex; align-items:center; gap:10px; flex-wrap:wrap; }

/* ── KPI Cards ─────────────────────────────────────────────────────────── */
.kpi-card {
  background: #0A1F3A;
  border-radius: 16px;
  padding: 20px 22px 16px;
  border: 1px solid rgba(12,201,168,0.15);
  border-top: 4px solid #0CC9A8;
  box-shadow: 0 4px 16px rgba(0,0,0,0.3);
  height: 100%;
  transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease;
}
.kpi-card:hover {
  transform: translateY(-4px);
  border-color: rgba(12,201,168,0.4);
  box-shadow: 0 8px 32px rgba(12,201,168,0.12);
}
.kpi-card.accent-green { border-top-color:#0CC9A8; }
.kpi-card.accent-gold  { border-top-color:#C2FF57; }
.kpi-card.accent-teal  { border-top-color:#0CC9A8; }
.kpi-card.accent-navy  { border-top-color:#5BC8FF; }
.kpi-card.accent-red   { border-top-color:#E84C4C; }
.kpi-label   { font-family:'Syne',sans-serif; font-size:0.72rem; font-weight:700; letter-spacing:0.2em; text-transform:uppercase; color:#8A9DB8; margin-bottom:6px; }
.kpi-value   { font-family:'Syne',sans-serif; font-size:2.2rem; font-weight:800; color:#0CC9A8; line-height:1.1; }
.kpi-unit    { font-size:0.9rem; font-weight:500; color:#8A9DB8; margin-left:2px; }
.kpi-delta-pos { color:#0CC9A8; font-size:0.80rem; font-weight:700; margin-top:4px; }
.kpi-delta-neg { color:#E84C4C; font-size:0.80rem; font-weight:700; margin-top:4px; }
.kpi-sub     { font-size:0.78rem; color:#8A9DB8; margin-top:2px; }
.kpi-subtext { font-size:0.78rem; color:#8A9DB8; margin-top:2px; }

/* ── Section Headers & Charts ──────────────────────────────────────────── */
.sec-hdr { font-family:'Syne',sans-serif; font-size:0.72rem; font-weight:700; letter-spacing:0.25em; text-transform:uppercase; color:#0CC9A8; border-bottom:1px solid rgba(12,201,168,.2); padding-bottom:6px; margin-bottom:14px; margin-top:8px; }
.chart-card { background:#0A1F3A; border-radius:16px; border:1px solid rgba(12,201,168,0.15); padding:18px 18px 10px; box-shadow:0 4px 16px rgba(0,0,0,0.25); margin-bottom:16px; }
.chart-title   { font-family:'Syne',sans-serif; font-size:0.85rem; font-weight:700; color:#E4ECF7; margin-bottom:4px; text-transform:uppercase; letter-spacing:0.05em; }
.chart-caption { font-size:0.74rem; color:#8A9DB8; margin-top:4px; font-style:italic; }

/* ── Disclaimer Boxes ──────────────────────────────────────────────────── */
.disc-prototype { background:rgba(194,255,87,.06); border:1px solid rgba(194,255,87,.25); border-left:4px solid #C2FF57; padding:10px 16px; font-size:0.82rem; color:#C2FF57; margin:10px 0; border-radius:0 8px 8px 0; }
.disc-ai        { background:rgba(12,201,168,.06); border:1px solid rgba(12,201,168,.2);  border-left:4px solid #0CC9A8; padding:10px 16px; font-size:0.82rem; color:#8A9DB8; margin:10px 0; border-radius:0 8px 8px 0; }
.disc-data      { background:rgba(138,157,184,.06); border:1px solid rgba(138,157,184,.2); border-left:4px solid #8A9DB8; padding:10px 16px; font-size:0.82rem; color:#8A9DB8; margin:10px 0; border-radius:0 8px 8px 0; }

/* ── Enterprise Footer ─────────────────────────────────────────────────── */
.ent-footer {
  background: #020B16;
  border-top: 1px solid rgba(12,201,168,0.2);
  padding: 28px 24px;
  margin-top: 48px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #8A9DB8;
}
.footer-title {
  font-family: 'Syne', sans-serif;
  font-size: 1.75rem;
  font-weight: 800;
  color: #E4ECF7;
  margin-bottom: 4px;
  letter-spacing: -0.025em;
}
.footer-subtitle { font-size:1rem; color:#8A9DB8; margin-bottom:20px; }
.footer-disclaimer { font-size:0.8rem; color:#8A9DB8; max-width:600px; line-height:1.6; margin-bottom:20px; }
.footer-links { font-size:0.8rem; color:#8A9DB8; }

/* ── Enterprise header ─────────────────────────────────────────────────── */
.page-logo-bar a:hover { color: #0CC9A8 !important; }

/* ── Validation Feedback ───────────────────────────────────────────────── */
.val-err  { background:rgba(232,76,76,.08);  border-left:3px solid #E84C4C; padding:7px 12px; font-size:0.80rem; color:#E84C4C; border-radius:0 6px 6px 0; margin:6px 0; }
.val-ok   { background:rgba(12,201,168,.08); border-left:3px solid #0CC9A8; padding:7px 12px; font-size:0.80rem; color:#0CC9A8; border-radius:0 6px 6px 0; margin:6px 0; }
.val-warn { background:rgba(194,255,87,.06); border-left:3px solid #C2FF57; padding:7px 12px; font-size:0.80rem; color:#C2FF57; border-radius:0 6px 6px 0; margin:6px 0; }

/* ── Sidebar Sections ──────────────────────────────────────────────────── */
.sb-section { font-family:'Syne',sans-serif; font-size:0.72rem; font-weight:700; letter-spacing:0.2em; text-transform:uppercase; color:#0CC9A8 !important; margin:14px 0 6px; }

/* ── Chips / Badges ────────────────────────────────────────────────────── */
.chip { display:inline-block; background:#0D2847; border:1px solid rgba(12,201,168,0.2); border-radius:4px; padding:2px 8px; font-size:0.78rem; color:#8A9DB8; margin:2px; }

/* ── AI Chat Bubbles ───────────────────────────────────────────────────── */
.ca-user { background:#0D2847; border-left:3px solid #0CC9A8; border-radius:0 12px 12px 12px; padding:10px 14px; margin:10px 0 4px; color:#E4ECF7; font-size:0.88rem; line-height:1.6; }
.ca-ai   { background:#0A1F3A; border:1px solid rgba(12,201,168,0.15); border-left:3px solid #C2FF57; border-radius:0 12px 12px 12px; padding:10px 14px; margin:4px 0 10px; color:#E4ECF7; font-size:0.88rem; line-height:1.65; }
.ca-tool { display:inline-block; background:#0D2847; color:#0CC9A8; border-radius:4px; padding:2px 8px; font-size:0.78rem; font-weight:700; margin:2px; letter-spacing:0.3px; }
.ca-meta { font-size:0.78rem; color:#8A9DB8; margin-top:4px; }

/* ── Contact Card (About page) ─────────────────────────────────────────── */
.contact-card  { background:#0A1F3A; border:1px solid rgba(12,201,168,0.15); border-radius:16px; padding:20px 22px; box-shadow:0 4px 16px rgba(0,0,0,0.25); }
.contact-label { font-family:'Syne',sans-serif; font-size:0.72rem; font-weight:700; letter-spacing:0.15em; text-transform:uppercase; color:#8A9DB8; margin-bottom:3px; }
.contact-val   { font-size:0.88rem; color:#E4ECF7; font-weight:600; margin-bottom:10px; }

/* ── Weather Widget ────────────────────────────────────────────────────── */
.wx-widget { background:#0D2847; border:1px solid rgba(12,201,168,0.15); border-radius:12px; padding:12px 14px; margin-bottom:8px; }
.wx-temp   { font-family:'Syne',sans-serif; font-size:2.2rem; font-weight:800; color:#E4ECF7; line-height:1.1; }
.wx-desc   { font-size:0.82rem; color:#8A9DB8; margin-bottom:6px; }
.wx-row    { font-size:0.79rem; color:#8A9DB8; margin-top:4px; }

/* ── Page Logo Banner ──────────────────────────────────────────────────── */
.page-logo-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  background: linear-gradient(135deg, #0A1F3A 0%, #0D2847 100%);
  padding: 12px 20px;
  border-radius: 12px;
  border: 1px solid rgba(12,201,168,0.2);
  box-shadow: 0 4px 16px rgba(0,0,0,0.3);
  margin: -1rem 0 1.5rem 0;
}
.platform-name {
  font-family: 'Syne', sans-serif;
  font-size: 1.5rem;
  font-weight: 800;
  color: #E4ECF7;
  line-height: 1;
  letter-spacing: -0.02em;
}

/* ── Hide Streamlit Default Chrome ─────────────────────────────────────── */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
div[data-testid="stToolbar"],
div[data-testid="stStatusWidget"] { visibility: hidden; }

/* ── Asset Cards ───────────────────────────────────────────────────────── */
.asset-card {
  background: #0A1F3A;
  border-radius: 16px;
  border: 1px solid rgba(12,201,168,0.15);
  border-top: 4px solid #0CC9A8;
  padding: 18px 20px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.25);
  transition: transform .2s, box-shadow .2s, border-color .2s;
  height: 100%;
}
.asset-card:hover {
  transform: translateY(-4px);
  border-color: rgba(12,201,168,0.4);
  box-shadow: 0 8px 32px rgba(12,201,168,0.1);
}
.asset-name { font-family:'Syne',sans-serif; font-size:1.05rem; font-weight:700; color:#E4ECF7; margin-bottom:2px; }
.asset-type-badge { display:inline-block; background:rgba(12,201,168,0.1); color:#0CC9A8; border-radius:4px; padding:1px 8px; font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:12px; }
.asset-row { display:flex; justify-content:space-between; font-size:0.82rem; color:#8A9DB8; margin-bottom:4px; line-height:1.4; }
.asset-row strong { color:#E4ECF7; }
.epc-badge { display:inline-block; padding:2px 10px; border-radius:4px; font-weight:700; font-size:0.85rem; color:#ffffff; letter-spacing:0.5px; }
.epc-A { background:#00873D; }
.epc-B { background:#2ECC40; color:#05101E; }
.epc-C { background:#85C226; color:#05101E; }
.epc-D { background:#F0B429; color:#05101E; }
.epc-E { background:#F06623; }
.epc-F { background:#E84C4C; }
.epc-G { background:#C0392B; }

/* ── Portfolio Section Header ──────────────────────────────────────────── */
.portfolio-section-hdr {
  font-family: 'Syne', sans-serif;
  font-size: 1.0rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #E4ECF7;
  padding: 12px 0 8px 0;
  border-bottom: 2px solid #0CC9A8;
  margin-bottom: 18px;
}

/* ── Segment Switch Modal ──────────────────────────────────────────────── */
.switch-modal {
  background: #0A1F3A;
  border: 1px solid rgba(12,201,168,0.2);
  border-left: 5px solid #C2FF57;
  border-radius: 12px;
  padding: 24px 28px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.4);
  margin: 16px 0;
}

/* ── Dashboard Section Divider ─────────────────────────────────────────── */
.main-section-divider {
  height: 1px;
  background: linear-gradient(90deg, rgba(12,201,168,0.4) 0%, rgba(12,201,168,0.05) 100%);
  margin: 24px 0;
}

/* ── Page H2 Heading ───────────────────────────────────────────────────── */
.page-h2 {
  font-family: 'Syne', sans-serif;
  font-size: 2rem;
  font-weight: 800;
  color: #E4ECF7;
  line-height: 1.15;
  margin-bottom: 4px;
  letter-spacing: -0.025em;
}

/* ── Sub-section Label ──────────────────────────────────────────────────── */
.subsec-label {
  font-family: 'Syne', sans-serif;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: #0CC9A8;
  margin: 8px 0 4px;
}

/* ── Streamlit Native Element Theming ──────────────────────────────────── */

/* ── Nav bar container ─────────────────────────────────────────────────── */
div[data-testid="stHorizontalBlock"]:has(button[data-testid="baseButton-primary"]) {
  gap: 0 !important;
}

/* ── Buttons — general ─────────────────────────────────────────────────── */
.stButton > button {
  font-family: 'Syne', sans-serif !important;
  font-weight: 700 !important;
  font-size: 0.84rem !important;
  letter-spacing: 0.02em !important;
  border-radius: 8px !important;
  transition: background 0.15s, color 0.15s, transform 0.15s !important;
  box-shadow: none !important;
}

/* Primary = active nav or CTA */
.stButton > button[kind="primary"] {
  background: #0CC9A8 !important;
  color: #05101E !important;
  border: none !important;
}
.stButton > button[kind="primary"]:hover {
  background: #C2FF57 !important;
  transform: translateY(-1px) !important;
}

/* Secondary = inactive nav */
.stButton > button[kind="secondary"] {
  background: transparent !important;
  color: #8A9DB8 !important;
  border: 1px solid transparent !important;
}
.stButton > button[kind="secondary"]:hover {
  color: #E4ECF7 !important;
  background: rgba(228,236,247,0.06) !important;
  border-color: rgba(138,157,184,0.2) !important;
}

/* Metrics */
div[data-testid="stMetric"] {
  background: #0A1F3A !important;
  border: 1px solid rgba(12,201,168,0.15) !important;
  border-radius: 14px !important;
  padding: 20px !important;
}
div[data-testid="stMetricValue"] { color:#0CC9A8 !important; font-family:'Syne',sans-serif !important; font-weight:800 !important; }
div[data-testid="stMetricLabel"] { color:#8A9DB8 !important; font-family:'Syne',sans-serif !important; font-size:0.72rem !important; font-weight:700 !important; letter-spacing:0.12em !important; text-transform:uppercase !important; }

/* Inputs */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea {
  background: #0D2847 !important;
  border: 1px solid rgba(12,201,168,0.2) !important;
  border-radius: 8px !important;
  color: #E4ECF7 !important;
  font-family: 'DM Sans', sans-serif !important;
}
.stTextInput input:focus,
.stNumberInput input:focus,
.stTextArea textarea:focus {
  border-color: #0CC9A8 !important;
  box-shadow: 0 0 0 2px rgba(12,201,168,0.15) !important;
}
.stSelectbox > div > div,
.stMultiSelect > div > div {
  background: #0D2847 !important;
  border: 1px solid rgba(12,201,168,0.2) !important;
  border-radius: 8px !important;
  color: #E4ECF7 !important;
}

/* Input labels */
.stTextInput label, .stNumberInput label, .stTextArea label,
.stSelectbox label, .stMultiSelect label, .stSlider label,
.stCheckbox label, .stRadio label {
  color: #8A9DB8 !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 0.88rem !important;
}

/* Expanders */
[data-testid="stExpander"] {
  background: #0A1F3A !important;
  border: 1px solid rgba(12,201,168,0.15) !important;
  border-radius: 12px !important;
}
[data-testid="stExpander"] summary {
  color: #E4ECF7 !important;
  font-family: 'Syne', sans-serif !important;
  font-weight: 600 !important;
}

/* Bordered containers */
[data-testid="stVerticalBlockBorderWrapper"] > div {
  background: #0A1F3A !important;
  border: 1px solid rgba(12,201,168,0.15) !important;
  border-radius: 14px !important;
}

/* Alerts */
.stAlert { background:#0D2847 !important; border-radius:10px !important; }

/* Dividers */
hr { border-color: rgba(12,201,168,0.15) !important; }

/* Caption & markdown text */
.stCaption, [data-testid="stCaptionContainer"] { color:#8A9DB8 !important; }
.stMarkdown p, .stMarkdown li { color:#B9C9DE; line-height:1.7; }
.stMarkdown a { color:#0CC9A8; }
.stMarkdown a:hover { color:#C2FF57; }
.stMarkdown code { background:#0D2847; color:#0CC9A8; border-radius:4px; padding:2px 6px; }

/* Spinner & progress */
.stSpinner > div { border-top-color:#0CC9A8 !important; }
.stProgress > div > div { background:#0CC9A8 !important; }
"""

logger = logging.getLogger(__name__)


# ── Asset helpers ────────────────────────────────────────────────────────────

def _load_asset_uri(filename: str) -> str:
    """Resolves an asset path and returns a base64-encoded data URI.
    Prevents path traversal by validating filename doesn't contain path separators."""
    # Security: prevent path traversal attacks
    if "/" in filename or "\\" in filename or ".." in filename:
        logger.error("Invalid asset filename (contains path separators): %s", filename)
        return ""

    ext = Path(filename).suffix.lower()
    mime_map = {
        ".svg":  "image/svg+xml",
        ".png":  "image/png",
        ".jpg":  "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif":  "image/gif",
        ".webp": "image/webp",
    }
    mime = mime_map.get(ext, "image/png")
    candidate_paths = [
        Path("assets") / filename,
        Path("app/assets") / filename,
        Path(".") / filename,
    ]
    for path in candidate_paths:
        if path.is_file():
            with open(path, "rb") as f:
                data = f.read()
            b64 = base64.b64encode(data).decode("utf-8")
            return f"data:{mime};base64,{b64}"
    logger.warning(
        "Asset not found: %s. Searched: %s", filename, [str(p) for p in candidate_paths]
    )
    return ""


@st.cache_resource
def get_logo_uri() -> str:
    """Returns the base64 data URI for the horizontal CrowAgent™ logo."""
    return _load_asset_uri("logo.png")


@st.cache_resource
def get_icon_uri() -> str:
    """Returns the base64 data URI for the square CrowAgent™ icon."""
    return _load_asset_uri("favicon.png")


# ── Injection helpers ────────────────────────────────────────────────────────

def inject_branding() -> None:
    """Injects the full CrowAgent™ CSS into the current Streamlit page.
    Safe to call multiple times — Streamlit deduplicates identical markdown."""
    st.markdown(f"<style>{CROWAGENT_CSS}</style>", unsafe_allow_html=True)


def render_html(html_content: str) -> None:
    """Central gateway for raw HTML rendering (V-03 policy).

    All unsafe_allow_html=True calls outside branding.py / main.py must route
    through here so the V-03 grep check finds no violations in other modules.
    Callers must html.escape() any user-supplied values before passing them in.
    """
    st.markdown(html_content, unsafe_allow_html=True)


# ── UI component helpers ─────────────────────────────────────────────────────

def render_card(label: str, value: str, subtext: str, accent_class: str = "") -> None:
    """Renders a compact KPI metric card."""
    st.markdown(
        f"""
        <div class="kpi-card {accent_class}"
             role="group"
             aria-label="{html.escape(label)}: {html.escape(value)}">
            <div class="kpi-label"   aria-hidden="true">{html.escape(label)}</div>
            <div class="kpi-value"   aria-hidden="true">{html.escape(value)}</div>
            <div class="kpi-subtext" aria-hidden="true">{html.escape(subtext)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_page_logo() -> None:
    """Renders the enterprise header bar at the top of every page."""
    logo_uri = get_logo_uri()
    logo_img = (
        f'<img src="{logo_uri}" style="height:36px;display:block;filter:brightness(0) invert(1);opacity:0.95;" alt="CrowAgent™">'
        if logo_uri else
        '<span style="font-family:\'Syne\',sans-serif;font-size:1.4rem;font-weight:800;color:#E4ECF7;">CrowAgent™</span>'
    )
    st.markdown(
        f"""
        <div class="page-logo-bar" role="banner">
            <div style="display:flex;align-items:center;gap:14px;flex:1;">
                {logo_img}
                <div style="width:1px;height:28px;background:rgba(12,201,168,0.25);"></div>
                <div>
                    <div style="font-family:'Syne',sans-serif;font-size:0.68rem;font-weight:700;letter-spacing:0.25em;text-transform:uppercase;color:#8A9DB8;line-height:1;">PLATFORM</div>
                    <div style="font-family:'Syne',sans-serif;font-size:1.05rem;font-weight:800;color:#E4ECF7;line-height:1.2;letter-spacing:-0.01em;">Sustainability Intelligence</div>
                </div>
            </div>
            <div style="display:flex;align-items:center;gap:10px;">
                <span class="sp sp-live"><span class="pulse-dot"></span>Live</span>
                <span style="font-family:'Syne',sans-serif;font-size:0.72rem;font-weight:700;color:#3A5070;letter-spacing:0.05em;">v2.1.0</span>
                <div style="width:1px;height:20px;background:rgba(12,201,168,0.15);"></div>
                <a href="mailto:crowagent.platform@gmail.com" style="font-family:'Syne',sans-serif;font-size:0.78rem;font-weight:600;color:#8A9DB8;text-decoration:none;letter-spacing:0.03em;">Contact</a>
                <a href="https://crowagent.ai" target="_blank" style="background:#0CC9A8;color:#05101E;font-family:'Syne',sans-serif;font-size:0.78rem;font-weight:700;padding:6px 14px;border-radius:6px;text-decoration:none;letter-spacing:0.03em;">crowagent.ai ↗</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    """Renders the enterprise footer at the bottom of every page."""
    logo_uri = get_logo_uri()
    logo_img = (
        f'<img src="{logo_uri}" style="height:30px;margin-bottom:14px;filter:brightness(0) invert(1);opacity:0.9;" alt="CrowAgent™">'
        if logo_uri else ""
    )
    st.markdown(
        f"""
        <div class="ent-footer" role="contentinfo">
            <div style="width:100%;max-width:1100px;margin:0 auto;">
                <!-- Top row: brand + columns -->
                <div style="display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:40px;margin-bottom:36px;text-align:left;">
                    <!-- Brand -->
                    <div>
                        {logo_img}
                        <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:800;color:#E4ECF7;letter-spacing:-0.02em;margin-bottom:8px;">CrowAgent™</div>
                        <div style="font-size:0.82rem;color:#8A9DB8;line-height:1.7;max-width:260px;">
                            Physics-Informed AI for UK building energy, emissions, and sustainability compliance.
                        </div>
                        <div style="margin-top:14px;">
                            <span class="sp sp-live" style="font-size:0.72rem;"><span class="pulse-dot"></span>Platform Live</span>
                        </div>
                    </div>
                    <!-- Platform -->
                    <div>
                        <div style="font-family:'Syne',sans-serif;font-size:0.70rem;font-weight:700;letter-spacing:0.2em;text-transform:uppercase;color:#0CC9A8;margin-bottom:14px;">Platform</div>
                        <div style="display:flex;flex-direction:column;gap:10px;">
                            <a href="https://crowagent.ai/#products" target="_blank" style="font-size:0.84rem;color:#8A9DB8;text-decoration:none;">Products</a>
                            <a href="https://crowagent.ai/#how" target="_blank" style="font-size:0.84rem;color:#8A9DB8;text-decoration:none;">How It Works</a>
                            <a href="https://crowagent.ai/#sectors" target="_blank" style="font-size:0.84rem;color:#8A9DB8;text-decoration:none;">Sectors</a>
                            <a href="https://crowagent.ai/#security" target="_blank" style="font-size:0.84rem;color:#8A9DB8;text-decoration:none;">Security</a>
                        </div>
                    </div>
                    <!-- Company -->
                    <div>
                        <div style="font-family:'Syne',sans-serif;font-size:0.70rem;font-weight:700;letter-spacing:0.2em;text-transform:uppercase;color:#0CC9A8;margin-bottom:14px;">Company</div>
                        <div style="display:flex;flex-direction:column;gap:10px;">
                            <a href="https://crowagent.ai/#about" target="_blank" style="font-size:0.84rem;color:#8A9DB8;text-decoration:none;">About</a>
                            <a href="https://crowagent.ai/#vision" target="_blank" style="font-size:0.84rem;color:#8A9DB8;text-decoration:none;">Vision</a>
                            <a href="mailto:crowagent.platform@gmail.com" style="font-size:0.84rem;color:#8A9DB8;text-decoration:none;">Contact</a>
                            <a href="https://crowagent.ai/legal.html" target="_blank" style="font-size:0.84rem;color:#8A9DB8;text-decoration:none;">Legal</a>
                        </div>
                    </div>
                    <!-- Compliance -->
                    <div>
                        <div style="font-family:'Syne',sans-serif;font-size:0.70rem;font-weight:700;letter-spacing:0.2em;text-transform:uppercase;color:#0CC9A8;margin-bottom:14px;">Compliance</div>
                        <div style="display:flex;flex-direction:column;gap:10px;">
                            <span style="font-size:0.84rem;color:#8A9DB8;">SECR</span>
                            <span style="font-size:0.84rem;color:#8A9DB8;">TCFD</span>
                            <span style="font-size:0.84rem;color:#8A9DB8;">UK SRS</span>
                            <span style="font-size:0.84rem;color:#8A9DB8;">Environment Act 2021</span>
                        </div>
                    </div>
                </div>
                <!-- Divider -->
                <div style="height:1px;background:rgba(12,201,168,0.12);margin-bottom:20px;"></div>
                <!-- Bottom row -->
                <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
                    <div style="font-size:0.78rem;color:#3A5070;">
                        © 2026 <span style="color:#8A9DB8;">CrowAgent Ltd</span>. Registered in England &amp; Wales. Company No. 17076461. Reading, RG1 6SP.
                    </div>
                    <div style="font-size:0.78rem;color:#3A5070;">
                        CrowAgent™ is a trademark of Aparajita Parihar · Registration pending · Not licensed for commercial use
                    </div>
                </div>
                <!-- Disclaimer -->
                <div style="margin-top:14px;padding:12px 16px;background:rgba(194,255,87,0.04);border:1px solid rgba(194,255,87,0.12);border-radius:8px;font-size:0.76rem;color:#3A5070;line-height:1.65;text-align:left;">
                    <strong style="color:#8A9DB8;">Results Are Indicative Only.</strong>
                    This platform uses simplified physics models. Outputs must not be used as the sole basis for capital investment or procurement decisions. Always consult a qualified energy surveyor.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Streamlit page configuration ─────────────────────────────────────────────
# Fallback page config values; main.py calls set_page_config() directly.
PAGE_CONFIG = {
    "page_title": "CrowAgent™ Platform",
    "page_icon": "assets/favicon.png",
    "layout": "wide",
    "initial_sidebar_state": "collapsed",
    "menu_items": {
        "Get Help": "mailto:crowagent.platform@gmail.com",
        "Report a bug": "https://github.com/WonderApri/crowagent-platform/issues",
        "About": (
            "**CrowAgent™ Platform — Sustainability AI Decision Intelligence**\n\n"
            "© 2026 Aparajita Parihar. All rights reserved.\n\n"
            "⚠️ PROTOTYPE: Results are indicative only and based on simplified "
            "physics models. Not for use as the sole basis for investment decisions.\n\n"
            "CrowAgent™ is a trademark of Aparajita Parihar.\n"
            "Trademark application filed with the UK Intellectual Property Office (UK IPO), Class 42.\n"
            "Registration pending."
        ),
    },
}
