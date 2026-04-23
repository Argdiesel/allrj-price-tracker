from __future__ import annotations
"""Price History — trend charts per brand/product."""
import streamlit as st
import pandas as pd

try:
    from utils.database import get_price_history, get_all_brand_trends, get_latest_price_per_url
    DB_OK = True
except Exception:
    DB_OK = False


def _safe_line_chart(df, height=300, label="Price ($)"):
    """Render a line chart with zero dependencies — pure Streamlit native."""
    try:
        st.line_chart(df, height=height)
    except Exception:
        # Ultimate fallback: just show the table
        st.dataframe(df, use_container_width=True)


def render():
    st.markdown("""
    <div class="page-header">
        <div>
            <div class="page-title">PRICE <span>HISTORY</span></div>
            <div class="page-sub">30-day trends · Brand comparison · Product deep dive</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not DB_OK:
        st.error("Database unavailable.")
        return

    history      = get_price_history(days=30)
    brand_trends = get_all_brand_trends(days=30)

    if not history:
        st.markdown("""
        <div class="empty-state">
          <div class="empty-icon">📈</div>
          <div class="empty-title">NO HISTORY YET</div>
          <div class="empty-sub">Run your first scan in Track Prices to start building price history</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("→ Go Track Prices"):
            st.session_state.page = "tracker"
            st.rerun()
        return

    df_history = pd.DataFrame(history)
    df_history["scraped_at"] = pd.to_datetime(df_history["scraped_at"])
    df_history["day"] = df_history["scraped_at"].dt.date

    tab1, tab2, tab3 = st.tabs([
        "📊  Brand Trends",
        "🔍  Product Deep Dive",
        "📋  Raw Data",
    ])

    # ─────────────────────────────────────────────────────
    # TAB 1: Brand Trends
    # ─────────────────────────────────────────────────────
    with tab1:
        st.markdown("**Average price per brand over the last 30 days.**")
        st.markdown("")

        if brand_trends:
            try:
                df_trends = pd.DataFrame(brand_trends)
                df_trends["day"] = pd.to_datetime(df_trends["day"])
                df_pivot = df_trends.pivot_table(
                    index="day", columns="brand",
                    values="avg_price", aggfunc="mean"
                ).reset_index().sort_values("day")

                brands_in_chart = [c for c in df_pivot.columns if c != "day"]
                if brands_in_chart and len(df_pivot) >= 2:
                    chart_df = df_pivot.set_index("day")
                    chart_df.index.name = "Date"
                    _safe_line_chart(chart_df, height=340)
                elif brands_in_chart:
                    st.info("💡 Run scans on different days to see trend lines build up.")
                else:
                    st.info("No brand data available yet.")
            except Exception as e:
                st.warning(f"Could not render trend chart: {e}")

        st.markdown("---")
        st.markdown("**Brand Price Summary — last 30 days**")

        df_valid = df_history[df_history["price_num"].notna()]
        if not df_valid.empty:
            summary = df_valid.groupby("brand")["price_num"].agg(
                Min="min", Max="max", Avg="mean", Scans="count"
            ).reset_index()
            summary.columns = ["Brand", "Min ($)", "Max ($)", "Avg ($)", "Scans"]
            for col in ["Min ($)", "Max ($)", "Avg ($)"]:
                summary[col] = summary[col].map("${:.2f}".format)
            st.dataframe(summary, use_container_width=True, hide_index=True)
        else:
            st.info("No valid price data yet.")

    # ─────────────────────────────────────────────────────
    # TAB 2: Product Deep Dive
    # ─────────────────────────────────────────────────────
    with tab2:
        st.markdown("**Track a specific product's price over time — see if it's trending up, down, or holding steady.**")
        st.markdown("")

        latest = get_latest_price_per_url()
        if not latest:
            st.info("No product data yet — run a scan first.")
            return

        df_latest = pd.DataFrame(latest)

        # ── Filters ──────────────────────────────────────
        col_brand, col_cat = st.columns(2)
        with col_brand:
            brands = sorted(df_latest["brand"].dropna().unique().tolist())
            sel_brand = st.selectbox("Filter by Brand", ["All"] + brands)
        with col_cat:
            cats = sorted(df_latest["category"].dropna().unique().tolist())
            sel_cat = st.selectbox("Filter by Category", ["All"] + cats)

        # Apply filters
        filtered = df_latest.copy()
        if sel_brand != "All":
            filtered = filtered[filtered["brand"] == sel_brand]
        if sel_cat != "All":
            filtered = filtered[filtered["category"] == sel_cat]

        if filtered.empty:
            st.warning("No products match the selected filters.")
            return

        # ── Product selector ──────────────────────────────
        st.markdown("")
        product_options = filtered["url"].tolist()
        product_labels  = {}
        for _, row in filtered.iterrows():
            name = str(row.get("product") or "").strip()
            name = name[:50] if name else row["url"][:50]
            label = f"{row.get('brand','?')} · {row.get('category','?')} · {name}"
            product_labels[row["url"]] = label

        sel_url = st.selectbox(
            "Select Product",
            options=product_options,
            format_func=lambda u: product_labels.get(u, u),
        )

        st.markdown("")

        # ── Actions row ───────────────────────────────────
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            show_chart   = st.button("📈  View Price Trend",   key="btn_chart",   use_container_width=True)
        with col_b:
            show_history = st.button("📋  View Full History",  key="btn_history", use_container_width=True)
        with col_c:
            export_csv   = st.button("📥  Export This Product", key="btn_export",  use_container_width=True)

        # Store which action is active in session state
        if show_chart:
            st.session_state.dive_action = "chart"
        if show_history:
            st.session_state.dive_action = "history"
        if export_csv:
            st.session_state.dive_action = "export"
        if "dive_action" not in st.session_state:
            st.session_state.dive_action = "chart"

        # ── Product data ──────────────────────────────────
        prod_hist = df_history[df_history["url"] == sel_url].sort_values("day")

        if prod_hist.empty:
            st.info("No historical data for this product yet. Run another scan tomorrow to start seeing trends.")
        else:
            prices = prod_hist["price_num"].dropna()

            # Always show key metrics
            if not prices.empty:
                st.markdown("")
                st.markdown('<div class="section-header">📊 KEY METRICS</div>', unsafe_allow_html=True)
                m1, m2, m3, m4, m5 = st.columns(5)
                current = prices.iloc[-1]
                avg_30  = prices.mean()
                low_30  = prices.min()
                high_30 = prices.max()
                pct_chg = ((current - prices.iloc[0]) / prices.iloc[0] * 100) if len(prices) > 1 else 0

                m1.metric("Current Price", f"${current:.2f}")
                m2.metric("30d Average",   f"${avg_30:.2f}")
                m3.metric("30d Low",       f"${low_30:.2f}")
                m4.metric("30d High",      f"${high_30:.2f}")
                m5.metric("30d Change",    f"{pct_chg:+.1f}%",
                           delta=f"{pct_chg:+.1f}%",
                           delta_color="inverse" if pct_chg > 0 else "normal")

                # Auto insight
                st.markdown("")
                if pct_chg <= -15:
                    insight = f"🔥 **Sale detected!** Price dropped {abs(pct_chg):.1f}% — this competitor is running a promo. Consider matching for 72hrs."
                    color = "var(--accent2)"
                elif pct_chg <= -5:
                    insight = f"📉 **Price dropped {abs(pct_chg):.1f}%** over 30 days. Could be a permanent reduction or slow-moving stock clearance."
                    color = "var(--green)"
                elif pct_chg >= 10:
                    insight = f"📈 **Price increased {pct_chg:.1f}%** — competitor raising margins. Opportunity to capture their price-sensitive customers."
                    color = "var(--yellow)"
                elif current < avg_30 * 0.95:
                    insight = f"💡 **Currently below their 30-day average** (${avg_30:.2f}). Likely a short-term promo — watch for it reverting."
                    color = "var(--accent-lt)"
                else:
                    insight = f"✅ **Price is holding steady** around ${avg_30:.2f}. No major movements — this competitor is price-stable right now."
                    color = "var(--text2)"

                st.markdown(f"""
                <div style="background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);
                            padding:14px 18px;font-size:0.84rem;color:var(--text2);line-height:1.6;">
                  <span style="color:{color};">{insight}</span>
                </div>
                """, unsafe_allow_html=True)

            # ── Action-driven content ─────────────────────
            action = st.session_state.dive_action

            if action == "chart":
                st.markdown("")
                st.markdown('<div class="section-header">📈 PRICE TREND CHART</div>', unsafe_allow_html=True)
                daily = prod_hist.groupby("day")["price_num"].mean().reset_index()
                daily.columns = ["Date", "Price ($)"]
                daily = daily.dropna().set_index("Date")
                if len(daily) >= 2:
                    _safe_line_chart(daily, height=280)
                else:
                    st.markdown("""
                    <div style="background:var(--surface);border:1px dashed var(--border2);border-radius:var(--radius);
                                padding:32px;text-align:center;">
                      <div style="font-size:1.5rem;margin-bottom:8px;">📅</div>
                      <div style="font-size:0.84rem;color:var(--text2);">Only 1 data point so far.</div>
                      <div style="font-size:0.75rem;color:var(--muted);margin-top:4px;">
                        Run another scan tomorrow — the trend line will appear after 2+ data points.
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

            elif action == "history":
                st.markdown("")
                st.markdown('<div class="section-header">📋 FULL SCAN HISTORY</div>', unsafe_allow_html=True)
                display = prod_hist[["day", "price_raw", "method", "status", "scraped_at"]].copy()
                display.columns = ["Date", "Price", "Method", "Status", "Scraped At"]
                display["Scraped At"] = display["Scraped At"].astype(str).str[:16].str.replace("T", " ")
                st.dataframe(display.sort_values("Date", ascending=False),
                             use_container_width=True, hide_index=True)

            elif action == "export":
                st.markdown("")
                st.markdown('<div class="section-header">📥 EXPORT PRODUCT DATA</div>', unsafe_allow_html=True)
                export_df = prod_hist.copy()
                export_df["scraped_at"] = export_df["scraped_at"].astype(str).str[:16].str.replace("T", " ")
                brand_name = prod_hist["brand"].iloc[0] if "brand" in prod_hist.columns else "product"
                filename = f"allrj_{brand_name.lower().replace(' ','_')}_history.csv"
                csv_data = export_df.to_csv(index=False).encode()
                st.download_button(
                    label=f"⬇️  Download {brand_name} price history CSV",
                    data=csv_data,
                    file_name=filename,
                    mime="text/csv",
                    use_container_width=True,
                )
                st.caption(f"{len(export_df)} price records · last 30 days")

    # ─────────────────────────────────────────────────────
    # TAB 3: Raw Data
    # ─────────────────────────────────────────────────────
    with tab3:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            brands_all = sorted(df_history["brand"].dropna().unique().tolist())
            brand_filter = st.multiselect("Filter by Brand", brands_all)
        with col_f2:
            days_filter = st.selectbox("Time range", [7, 14, 30, 90], index=2,
                                       format_func=lambda d: f"Last {d} days")

        df_filtered = pd.DataFrame(get_price_history(days=days_filter))
        if brand_filter and not df_filtered.empty:
            df_filtered = df_filtered[df_filtered["brand"].isin(brand_filter)]

        if not df_filtered.empty:
            display_cols = ["brand", "category", "product", "price_raw", "method", "status", "scraped_at"]
            available = [c for c in display_cols if c in df_filtered.columns]
            df_filtered["scraped_at"] = df_filtered["scraped_at"].astype(str).str[:16].str.replace("T", " ")
            st.dataframe(df_filtered[available], use_container_width=True, hide_index=True)
            st.caption(f"{len(df_filtered)} records")
            st.download_button(
                "📥 Export All",
                df_filtered.to_csv(index=False).encode(),
                "allrj_history.csv",
                "text/csv",
            )
        else:
            st.info("No data for selected filters.")
