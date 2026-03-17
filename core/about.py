import streamlit as st
import app.branding as branding


def render():
    # ── Hero ────────────────────────────────────────────────────────────────
    branding.render_html("""
    <div style="padding:48px 0 36px;">
        <div style="display:inline-flex;align-items:center;gap:8px;background:rgba(12,201,168,0.1);border:1px solid rgba(12,201,168,0.3);border-radius:100px;padding:6px 18px;margin-bottom:24px;">
            <span style="width:7px;height:7px;border-radius:50%;background:#0CC9A8;display:inline-block;animation:blink 2s infinite;flex-shrink:0;"></span>
            <span style="font-family:'Syne',sans-serif;font-size:0.72rem;font-weight:700;letter-spacing:0.25em;text-transform:uppercase;color:#0CC9A8;">Physics-Informed AI · UK Regulated Sectors</span>
        </div>
        <h1 style="font-family:'Syne',sans-serif;font-size:2.8rem;font-weight:800;color:#E4ECF7;letter-spacing:-0.03em;margin-bottom:18px;line-height:1.05;">
            Digital Twins for<br>Building Energy &amp; Compliance
        </h1>
        <p style="font-size:1.05rem;color:#8A9DB8;max-width:660px;line-height:1.8;margin:0;">
            CrowAgent™ delivers auditable Physics-Informed Neural Network technology to UK public sector
            organisations navigating mandatory energy, carbon, and sustainability reporting obligations.
            Built for SECR, TCFD, UK SRS, and the Environment Act 2021.
        </p>
    </div>
    """)

    branding.render_html('<div class="main-section-divider"></div>')

    # ── Company Stat Cards ───────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    for col, val, label in zip(
        [c1, c2, c3, c4],
        ["2026", "PINNs", "UK-Only", "17076461"],
        ["Incorporated England & Wales", "Core Physics Engine", "Regulation-First Design", "Companies House No."],
    ):
        with col:
            branding.render_html(f"""
            <div class="kpi-card accent-teal" style="text-align:center;padding:20px 16px;">
                <div class="kpi-value" style="font-size:1.45rem;margin-bottom:6px;">{val}</div>
                <div class="kpi-label" style="line-height:1.4;">{label}</div>
            </div>
            """)

    branding.render_html('<div class="main-section-divider" style="margin-top:24px;"></div>')

    # ── Main Content ─────────────────────────────────────────────────────────
    left, right = st.columns([3, 2], gap="large")

    with left:
        # Platform Overview
        branding.render_html('<div class="sec-hdr">Platform Overview</div>')
        branding.render_html("""
        <p style="color:#B9C9DE;line-height:1.85;margin-bottom:14px;font-size:0.95rem;">
            CrowAgent™ is a Physics-Informed Digital Twin platform purpose-built for UK organisations
            with mandatory energy, carbon, and sustainability reporting obligations. Unlike generic AI
            tools, every calculation is grounded in thermodynamic laws — making outputs auditable and
            defensible for regulatory submission.
        </p>
        <p style="color:#B9C9DE;line-height:1.85;margin-bottom:28px;font-size:0.95rem;">
            The platform integrates real operational data with PINN-based scenario modelling to generate
            costed, prioritised net zero roadmaps. Designed from the ground up for SECR, TCFD, UK SRS,
            PPN 02/21, and the Environment Act 2021 — no translation layers required.
        </p>
        """)

        # Capabilities
        branding.render_html('<div class="sec-hdr">Core Capabilities</div>')
        caps = [
            ("Digital Twins", "Physics-based building models constrained by thermodynamic laws"),
            ("Scenario Simulation", "What-if modelling for retrofits, renewables, and electrification"),
            ("Compliance Reporting", "SECR, TCFD, UK SRS, and Environment Act 2021 aligned outputs"),
            ("Retrofit Economics", "Costed, prioritised interventions with IRR and payback analysis"),
            ("AI Advisor", "Segment-aware guidance powered by large language models"),
            ("Portfolio Management", "Multi-asset tracking with EPC, energy, and carbon baselines"),
        ]
        for i in range(0, len(caps), 2):
            ca, cb = st.columns(2)
            for col, (title, desc) in zip([ca, cb], caps[i:i+2]):
                with col:
                    branding.render_html(f"""
                    <div style="background:#0D2847;border:1px solid rgba(12,201,168,0.12);border-radius:12px;padding:16px 18px;margin-bottom:10px;height:90px;display:flex;flex-direction:column;justify-content:center;">
                        <div style="font-family:'Syne',sans-serif;font-size:0.82rem;font-weight:700;color:#0CC9A8;margin-bottom:5px;letter-spacing:0.02em;">{title}</div>
                        <div style="font-size:0.80rem;color:#8A9DB8;line-height:1.5;">{desc}</div>
                    </div>
                    """)

        # Sectors
        branding.render_html('<div class="sec-hdr" style="margin-top:8px;">Target Sectors</div>')
        sectors = ["Local Councils", "NHS Trusts", "Housing Associations", "UK Universities", "Public Sector Bodies", "Energy & Utilities"]
        chips = "".join(f'<span class="chip" style="padding:5px 12px;font-size:0.80rem;">{s}</span>' for s in sectors)
        branding.render_html(f'<div style="margin-bottom:24px;">{chips}</div>')

        # Technology Stack
        branding.render_html('<div class="sec-hdr">Technology Stack</div>')
        tech = ["Python 3.11", "Streamlit", "Plotly", "PINN Thermal Model", "Google Gemini", "Open-Meteo API", "Met Office DataPoint", "Streamlit Cloud"]
        chips2 = "".join(f'<span class="chip">{t}</span>' for t in tech)
        branding.render_html(f'<div style="margin-bottom:28px;">{chips2}</div>')

        # Legal & Disclaimers
        branding.render_html('<div class="sec-hdr">Legal & Compliance Notices</div>')

        with st.expander("Platform Disclaimer — Results Are Indicative Only"):
            branding.render_html("""
            <div class="disc-prototype">
                <strong>Working Prototype — Indicative Results Only.</strong> All energy, carbon, and financial
                results are based on simplified steady-state physics models calibrated against published UK sector
                averages (HESA 2022–23, CIBSE Guide A). They do not reflect the specific characteristics of any
                real building or institution.
            </div>
            <p style="color:#8A9DB8;font-size:0.85rem;line-height:1.75;margin-top:12px;">
                Results must not be used as the sole basis for any capital investment, procurement, or planning
                decision. Organisations should commission a site-specific energy assessment by a suitably qualified
                energy surveyor in accordance with BS EN ISO 52000 and relevant CIBSE guidance before undertaking
                any retrofit programme.
            </p>
            <p style="color:#8A9DB8;font-size:0.85rem;line-height:1.75;">
                To the maximum extent permitted by law, the author and platform owner shall not be liable for any
                direct, indirect, incidental, or consequential damages arising from use of this platform.
            </p>
            """)

        with st.expander("AI Advisor — Model Limitations"):
            branding.render_html("""
            <p style="color:#8A9DB8;font-size:0.85rem;line-height:1.75;">
                The AI Advisor is powered by large language models (LLMs). LLM-based systems may produce
                plausible but factually incorrect outputs, misinterpret ambiguous queries, or provide information
                beyond their training cutoff. All AI-generated recommendations must be independently verified by a
                qualified professional before any action is taken. The AI Advisor is not a substitute for
                professional engineering, financial, or legal advice.
            </p>
            <p style="color:#8A9DB8;font-size:0.85rem;line-height:1.75;">
                User queries may be processed by third-party AI services. Avoid submitting confidential or
                commercially sensitive information.
            </p>
            """)

        with st.expander("Data Sources & Assumptions"):
            branding.render_html("""
            <ul style="color:#8A9DB8;font-size:0.85rem;line-height:2.0;padding-left:18px;">
                <li><strong style="color:#E4ECF7;">BEIS Greenhouse Gas Conversion Factors 2023</strong> — carbon intensity 0.20482 kgCO₂e/kWh</li>
                <li><strong style="color:#E4ECF7;">HESA Estates Management Statistics 2022–23</strong> — electricity cost £0.28/kWh</li>
                <li><strong style="color:#E4ECF7;">CIBSE Guide A Environmental Design</strong> — U-values, heating season 5,800 hrs/yr</li>
                <li><strong style="color:#E4ECF7;">PVGIS EC Joint Research Centre</strong> — Reading solar irradiance 950 kWh/m²/yr</li>
                <li><strong style="color:#E4ECF7;">US DoE EnergyPlus</strong> — cross-validation reference</li>
                <li><strong style="color:#E4ECF7;">Raissi, Perdikaris & Karniadakis (2019)</strong> — PINN methodology</li>
            </ul>
            """)

        with st.expander("Intellectual Property & Copyright"):
            branding.render_html("""
            <p style="color:#8A9DB8;font-size:0.85rem;line-height:1.75;">
                CrowAgent™ Platform, including all source code, physics models, UI design, and brand assets,
                is the original work of <strong style="color:#E4ECF7;">Aparajita Parihar</strong> and is
                protected by UK and international copyright law.
            </p>
            <p style="color:#8A9DB8;font-size:0.85rem;line-height:1.75;">
                <strong style="color:#E4ECF7;">CrowAgent™</strong> is a trademark of Aparajita Parihar.
                Trademark application filed with the UK Intellectual Property Office (UK IPO), Class 42.
                Registration pending.
            </p>
            <p style="color:#8A9DB8;font-size:0.85rem;line-height:1.75;">
                © 2026 Aparajita Parihar. All rights reserved. Not licensed for commercial use without
                prior written permission of the author.
            </p>
            """)

    with right:
        # Company Registration
        branding.render_html('<div class="sec-hdr">Company Details</div>')
        reg_rows = [
            ("Legal Name", "CrowAgent Ltd"),
            ("Entity Type", "Private Limited Company"),
            ("Registered In", "England & Wales"),
            ("Company Number", "17076461"),
            ("Registered Office", "Reading, RG1 6SP, United Kingdom"),
            ("Core Technology", "Physics-Informed Neural Networks"),
            ("Platform Status", "Active Pilot — Free Access"),
            ("Compliance Focus", "SECR · TCFD · UK SRS · Env Act 2021"),
        ]
        rows_html = "".join(f"""
        <div style="display:flex;justify-content:space-between;align-items:flex-start;padding:11px 0;border-bottom:1px solid rgba(12,201,168,0.1);">
            <span style="font-size:0.72rem;color:#8A9DB8;font-family:'Syne',sans-serif;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;flex-shrink:0;padding-right:12px;">{k}</span>
            <span style="font-size:0.84rem;color:#E4ECF7;font-weight:600;text-align:right;">{v}</span>
        </div>
        """ for k, v in reg_rows)
        branding.render_html(f"""
        <div style="background:#0A1F3A;border:1px solid rgba(12,201,168,0.15);border-radius:14px;padding:4px 22px 8px;margin-bottom:24px;">
            {rows_html}
        </div>
        """)

        # Contact Cards
        branding.render_html('<div class="sec-hdr">Get In Touch</div>')
        contacts = [
            ("General Enquiries", "crowagent.platform@gmail.com"),
            ("Pilot Access & Onboarding", "crowagent.platform@gmail.com"),
            ("Research & Partnerships", "crowagent.platform@gmail.com"),
        ]
        for label, email in contacts:
            branding.render_html(f"""
            <div style="background:#0D2847;border:1px solid rgba(12,201,168,0.12);border-radius:10px;padding:14px 18px;margin-bottom:10px;">
                <div style="font-family:'Syne',sans-serif;font-size:0.70rem;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;color:#8A9DB8;margin-bottom:5px;">{label}</div>
                <a href="mailto:{email}" style="font-size:0.88rem;color:#0CC9A8;font-weight:600;text-decoration:none;">{email}</a>
            </div>
            """)

        branding.render_html("""
        <div class="disc-ai" style="margin-top:4px;margin-bottom:24px;">
            We aim to respond to all enquiries within 2–3 business days.
        </div>
        """)

        # Platform Release
        branding.render_html('<div class="sec-hdr">Platform Release</div>')
        release_rows = [
            ("Version", "v2.1.0"),
            ("Released", "7 March 2026"),
            ("Weather Data", "● Live — Open-Meteo API", "#0CC9A8"),
            ("Cache TTL", "60 minutes (weather)"),
            ("Physics Engine", "PINN (Raissi et al., 2019)"),
            ("Deployment", "Streamlit Community Cloud"),
        ]
        release_html = ""
        for item in release_rows:
            k, v = item[0], item[1]
            color = item[2] if len(item) > 2 else "#E4ECF7"
            border = "border-bottom:1px solid rgba(12,201,168,0.1);" if item != release_rows[-1] else ""
            release_html += f"""
            <div style="display:flex;justify-content:space-between;padding:10px 0;{border}">
                <span style="font-size:0.72rem;color:#8A9DB8;font-family:'Syne',sans-serif;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;">{k}</span>
                <span style="font-size:0.84rem;color:{color};font-weight:600;">{v}</span>
            </div>
            """
        branding.render_html(f"""
        <div style="background:#0A1F3A;border:1px solid rgba(12,201,168,0.15);border-radius:14px;padding:4px 22px 8px;">
            {release_html}
        </div>
        """)
