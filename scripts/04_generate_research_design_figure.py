#!/usr/bin/env python3
"""
Publication-Quality Research Design & Methodological Framework Renderer
Figure 1 for ICES Journal of Marine Science (ICESJMS-2026-474)

Design Specifications:
- Compact, publication-balanced canvas (12.0 x 7.2 in at 300 DPI)
- Pure academic color palette (no heavy black backgrounds or text, refined journal tones)
- Zero mathematical equations (purely conceptual, structural, and descriptive)
- Strict text containment: generous padding, guaranteed inside bounding boxes
- Perfectly symmetrical 3-pillar structure with 3 balanced bullets per section
- Single authoritative diagram
"""

import os
import textwrap
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

def render_fig1():
    # Compact publication canvas
    fig, ax = plt.subplots(figsize=(12.0, 7.2), dpi=300)
    ax.set_xlim(0, 1200)
    ax.set_ylim(0, 720)
    ax.axis("off")

    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Helvetica", "Arial"]
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")

    # =========================================================================
    # 1. TOP HEADER BANNER (Refined Academic Navy & Slate, No Black)
    # =========================================================================
    header_box = FancyBboxPatch(
        (30, 652), 1140, 52,
        boxstyle="round,pad=0.2,rounding_size=8",
        facecolor="#F8FAFC",
        edgecolor="#CBD5E1",
        linewidth=1.1,
        zorder=2
    )
    ax.add_patch(header_box)

    # Accent top border
    ax.plot([35, 1165], [704, 704], color="#1E40AF", linewidth=2.8, zorder=3)

    ax.text(
        600, 681,
        "RESEARCH DESIGN, DATASETS & METHODOLOGICAL FRAMEWORK",
        ha="center", va="center",
        fontsize=11.2, fontweight="bold",
        color="#1E3A8A",
        zorder=4
    )
    ax.text(
        600, 664,
        "Integrated Bioeconomic Evaluation: Census Panel, Non-Parametric Frontiers, and Spatial-Temporal Econometrics",
        ha="center", va="center",
        fontsize=8.0, fontstyle="italic",
        color="#475569",
        zorder=4
    )

    # =========================================================================
    # 2. THREE METHODOLOGICAL PILLARS (Columns)
    # =========================================================================
    col_w = 366
    col_gap = 21
    col_y = 86
    col_h = 556

    pillars = [
        {
            "x": 30,
            "title": "PILLAR 1: DATASETS & EMPIRICAL PANEL",
            "subtitle": "TURKSTAT & SUBIS Census Panel (2000–2024, N = 125)",
            "primary": "#1E40AF",
            "border": "#93C5FD",
            "header_bg": "#EFF6FF",
            "sections": [
                {
                    "title": "Panel Structure & Regional Coverage",
                    "bullets": [
                        "Five maritime basins: Black Sea, Marmara, Aegean, Mediterranean, and Inland",
                        "25 consecutive annual observation periods (balanced panel of 125 units)",
                        "Consistent spatial administrative boundaries across all census survey waves"
                    ]
                },
                {
                    "title": "Physical Capital & Fleet Dimensions",
                    "bullets": [
                        "Active commercial vessel counts disaggregated across vessel length classes",
                        "Cumulative engine power in installed kilowatts and engine horsepower",
                        "Cumulative gross tonnage reflecting physical vessel volume and hold capacity"
                    ]
                },
                {
                    "title": "Capture Production & Economic Value",
                    "bullets": [
                        "Annual marine capture harvest disaggregated into pelagic and demersal fish",
                        "Landed catch revenue deflated to constant 2015 national currency levels",
                        "Controls for temporal price shifts, species mix variation, and inflation"
                    ]
                },
                {
                    "title": "Technology Adoption & Policy Interventions",
                    "bullets": [
                        "Equipment adoption rates: GPS, echo sounders, radar, sonar, and VHF radio",
                        "2002 National Commercial Fishing License Freeze (entry moratorium)",
                        "2012–2018 State Vessel Buyback Scheme (targeted fleet decommissioning)"
                    ]
                }
            ]
        },
        {
            "x": 30 + col_w + col_gap,
            "title": "PILLAR 2: FRONTIER MODELING & CAPACITY",
            "subtitle": "Unsupervised PCA, DEA Frontiers & Malmquist TFP",
            "primary": "#B45309",
            "border": "#FCD34D",
            "header_bg": "#FFFBEB",
            "sections": [
                {
                    "title": "Modernization Index Construction",
                    "bullets": [
                        "Unsupervised Principal Component Analysis on five gear technologies",
                        "First principal component extraction capturing dominant common variance",
                        "Min-max standardization providing orthogonal continuous technology index"
                    ]
                },
                {
                    "title": "Data Envelopment Analysis (DEA)",
                    "bullets": [
                        "Non-parametric output-oriented linear programming capacity frontiers",
                        "Dual benchmarking under Constant and Variable Returns to Scale assumptions",
                        "Capacity utilization defined as observed output relative to frontier potential"
                    ]
                },
                {
                    "title": "Scale Efficiency Decomposition",
                    "bullets": [
                        "Scale efficiency ratio derived from dual frontier benchmark specifications",
                        "Operational returns classification into optimal, increasing, or decreasing scale",
                        "Separates capacity gap into operational scale distortion versus inefficiency"
                    ]
                },
                {
                    "title": "Productivity & Finite-Sample Correction",
                    "bullets": [
                        "Dynamic Malmquist TFP index: technical efficiency change and frontier shifts",
                        "Homogeneous smoothed bootstrap resamples for finite-sample bias correction",
                        "Constructs robust confidence intervals for efficiency and productivity metrics"
                    ]
                }
            ]
        },
        {
            "x": 30 + 2 * (col_w + col_gap),
            "title": "PILLAR 3: ECONOMETRICS & IDENTIFICATION",
            "subtitle": "Spatial Diagnostics, Robust HAC & Sensitivity Suite",
            "primary": "#0F766E",
            "border": "#99F6E4",
            "header_bg": "#F0FDFA",
            "sections": [
                {
                    "title": "Pre-Estimation Diagnostic Protocol",
                    "bullets": [
                        "Cross-sectional dependence tests via Pesaran CD and Friedman procedures",
                        "Panel serial autocorrelation checks using Wooldridge and Durbin–Watson tests",
                        "Panel unit root and stationarity validation via Im–Pesaran–Shin tests"
                    ]
                },
                {
                    "title": "Spatial & Serial HAC Estimation",
                    "bullets": [
                        "Driscoll–Kraay non-parametric HAC standard error covariance estimator",
                        "Inference robust to arbitrary spatial dependence and serial correlation",
                        "Prais–Winsten panel generalized least squares with serial quasi-differencing"
                    ]
                },
                {
                    "title": "Two-Way Fixed Effects Specifications",
                    "bullets": [
                        "Panel specifications with maritime basin and annual observation fixed effects",
                        "Controls for time-invariant regional unobservables and aggregate macro shocks",
                        "Estimates modernization elasticity, capital responsiveness, and policy shifts"
                    ]
                },
                {
                    "title": "Alternative Estimators & Sensitivity Suite",
                    "bullets": [
                        "Censored Tobit and Fractional Logit QMLE for bounded capacity outcomes",
                        "Leave-one-basin-out Jackknife iterations verifying spatial parameter stability",
                        "Non-linear Machine Learning Random Forest and SHAP feature importance"
                    ]
                }
            ]
        }
    ]

    for p in pillars:
        # Outer column card
        col_card = FancyBboxPatch(
            (p["x"], col_y), col_w, col_h,
            boxstyle="round,pad=0.2,rounding_size=8",
            facecolor="#FFFFFF",
            edgecolor=p["border"],
            linewidth=1.2,
            zorder=2
        )
        ax.add_patch(col_card)

        # Pillar Header Box
        p_head = FancyBboxPatch(
            (p["x"] + 6, col_y + col_h - 44), col_w - 12, 38,
            boxstyle="round,pad=0.2,rounding_size=6",
            facecolor=p["header_bg"],
            edgecolor=p["border"],
            linewidth=0.9,
            zorder=3
        )
        ax.add_patch(p_head)

        ax.text(
            p["x"] + col_w / 2, col_y + col_h - 19,
            p["title"],
            ha="center", va="center",
            fontsize=8.5, fontweight="bold",
            color=p["primary"],
            zorder=4
        )
        ax.text(
            p["x"] + col_w / 2, col_y + col_h - 32,
            p["subtitle"],
            ha="center", va="center",
            fontsize=6.9, fontstyle="italic",
            color="#475569",
            zorder=4
        )

        # 4 Thematic Sections inside each pillar
        sec_y = col_y + col_h - 52
        sec_h = 118
        sec_gap = 7

        for sec in p["sections"]:
            sec_box = FancyBboxPatch(
                (p["x"] + 8, sec_y - sec_h), col_w - 16, sec_h,
                boxstyle="round,pad=0.2,rounding_size=5",
                facecolor="#F8FAFC",
                edgecolor="#E2E8F0",
                linewidth=0.8,
                zorder=3
            )
            ax.add_patch(sec_box)

            # Left vertical indicator bar
            left_bar = FancyBboxPatch(
                (p["x"] + 8, sec_y - sec_h), 3.5, sec_h,
                boxstyle="round,pad=0.0,rounding_size=1",
                facecolor=p["primary"],
                edgecolor=p["primary"],
                linewidth=0,
                zorder=4
            )
            ax.add_patch(left_bar)

            # Section Title
            ax.text(
                p["x"] + 20, sec_y - 13,
                sec["title"],
                ha="left", va="center",
                fontsize=7.7, fontweight="bold",
                color="#1E293B",
                zorder=4
            )

            # Thin divider under section title
            ax.plot(
                [p["x"] + 20, p["x"] + col_w - 16],
                [sec_y - 22, sec_y - 22],
                color="#E2E8F0", linewidth=0.7, zorder=4
            )

            # Bullet points with guaranteed padding
            bullet_y = sec_y - 32
            for bullet in sec["bullets"]:
                wrapped = textwrap.wrap(bullet, width=46)
                
                # Small circular bullet dot aligned with first line of text
                dot = patches.Circle(
                    (p["x"] + 22, bullet_y - 3.2), radius=1.6,
                    facecolor=p["primary"], edgecolor="none", zorder=4
                )
                ax.add_patch(dot)

                # Render wrapped text
                ax.text(
                    p["x"] + 29, bullet_y,
                    "\n".join(wrapped),
                    ha="left", va="top",
                    fontsize=6.6, color="#334155",
                    linespacing=1.12,
                    zorder=4
                )

                # Advance bullet_y based on line count with safety spacing
                bullet_y -= (len(wrapped) * 8.4 + 4.2)

            sec_y -= (sec_h + sec_gap)

    # Process Flow Arrows between Pillars
    for arrow_x in [30 + col_w, 30 + 2 * col_w + col_gap]:
        flow_arr = FancyArrowPatch(
            (arrow_x + 3, col_y + col_h / 2), (arrow_x + col_gap - 3, col_y + col_h / 2),
            arrowstyle="-|>,head_length=4.5,head_width=3.2",
            color="#94A3B8",
            linewidth=1.6,
            zorder=5
        )
        ax.add_patch(flow_arr)

    # =========================================================================
    # 3. BOTTOM WORKFLOW PROCESS RIBBON (Light, Clean Academic Styling)
    # =========================================================================
    ribbon_y = 26
    ribbon_h = 48
    ribbon_box = FancyBboxPatch(
        (30, ribbon_y), 1140, ribbon_h,
        boxstyle="round,pad=0.2,rounding_size=6",
        facecolor="#F8FAFC",
        edgecolor="#CBD5E1",
        linewidth=1.0,
        zorder=2
    )
    ax.add_patch(ribbon_box)

    # Left dedicated label badge (guaranteed inside bounding box)
    badge_x = 38
    badge_y = ribbon_y + 6
    badge_w = 86
    badge_h = ribbon_h - 12
    badge_box = FancyBboxPatch(
        (badge_x, badge_y), badge_w, badge_h,
        boxstyle="round,pad=0.2,rounding_size=4",
        facecolor="#EFF6FF",
        edgecolor="#93C5FD",
        linewidth=0.9,
        zorder=3
    )
    ax.add_patch(badge_box)

    ax.text(
        badge_x + badge_w / 2, badge_y + badge_h / 2 + 5,
        "SEQUENTIAL",
        ha="center", va="center",
        fontsize=6.7, fontweight="bold",
        color="#1E40AF",
        zorder=4
    )
    ax.text(
        badge_x + badge_w / 2, badge_y + badge_h / 2 - 5,
        "PIPELINE",
        ha="center", va="center",
        fontsize=6.4, fontweight="bold",
        color="#1E40AF",
        zorder=4
    )

    steps = [
        ("Step 1: Census Ingestion", "TURKSTAT & SUBIS (N = 125)"),
        ("Step 2: Technology Indexing", "PCA Modernization Index"),
        ("Step 3: Frontier Modeling", "DEA Frontiers & Malmquist TFP"),
        ("Step 4: Econometric ID", "Driscoll–Kraay & AR(1) FGLS"),
        ("Step 5: Robustness Suite", "Tobit, FracLogit, Jackknife & ML")
    ]

    pill_w = 176
    pill_gap = 21
    start_pill_x = 136
    pill_y = ribbon_y + 6
    pill_h = ribbon_h - 12

    for i, (stitle, ssub) in enumerate(steps):
        p_x = start_pill_x + i * (pill_w + pill_gap)
        p_box = FancyBboxPatch(
            (p_x, pill_y), pill_w, pill_h,
            boxstyle="round,pad=0.2,rounding_size=4",
            facecolor="#FFFFFF",
            edgecolor="#BFDBFE",
            linewidth=0.8,
            zorder=3
        )
        ax.add_patch(p_box)

        ax.text(
            p_x + pill_w / 2, pill_y + pill_h / 2 + 5,
            stitle,
            ha="center", va="center",
            fontsize=7.1, fontweight="bold",
            color="#1E40AF",
            zorder=4
        )
        ax.text(
            p_x + pill_w / 2, pill_y + pill_h / 2 - 5,
            ssub,
            ha="center", va="center",
            fontsize=6.2,
            color="#475569",
            zorder=4
        )

        if i < len(steps) - 1:
            arr = FancyArrowPatch(
                (p_x + pill_w + 3, pill_y + pill_h / 2),
                (p_x + pill_w + pill_gap - 3, pill_y + pill_h / 2),
                arrowstyle="-|>,head_length=3.8,head_width=2.5",
                color="#60A5FA",
                linewidth=1.2,
                zorder=5
            )
            ax.add_patch(arr)

    # =========================================================================
    # 4. CAPTION & CITATION FOOTER
    # =========================================================================
    ax.text(
        600, 11,
        "Figure 1. Systematic research design, datasets, and methodological framework. Open-access repository: https://github.com/SezginTunca/turkish-fleet-modernization-capacity",
        ha="center", va="center",
        fontsize=6.6, fontstyle="italic",
        color="#64748B",
        zorder=3
    )

    plt.tight_layout()

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(base_dir, "figures")
    os.makedirs(out_dir, exist_ok=True)
    png_path = os.path.join(out_dir, "Fig1_research_design_framework.png")
    pdf_path = os.path.join(out_dir, "Fig1_research_design_framework.pdf")

    fig.savefig(png_path, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor(), edgecolor="none")
    fig.savefig(pdf_path, format="pdf", bbox_inches="tight", facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    print(f"Generated Figure 1 successfully:\n  {png_path}\n  {pdf_path}")

if __name__ == "__main__":
    render_fig1()
