import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from risk_engine import (
    EuropeanOption,
    AmericanOption,
    Portfolio,
    RiskEngine,
    MarketData,
    OptionType,
    PricingModel,
)
from risk_engine.market_data import MarketDataFetcher, get_market_data_fetcher

st.set_page_config(
    page_title="Risk Engine Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Quant Enthusiasts Risk Engine")
st.markdown("**Pure Python Options Pricing & Portfolio Risk Analysis**")

if "portfolio" not in st.session_state:
    st.session_state.portfolio = Portfolio()

if "market_data_map" not in st.session_state:
    st.session_state.market_data_map = {}

if "instruments_list" not in st.session_state:
    st.session_state.instruments_list = []

if "live_market_data" not in st.session_state:
    st.session_state.live_market_data = {}

st.sidebar.header("Navigation")
page = st.sidebar.radio(
    "Go to",
    [
        "Portfolio Builder",
        "Risk Analysis",
        "Market Data",
        "Visualizations",
        "Greeks Analysis",
    ],
)

if page == "Portfolio Builder":
    st.header("Portfolio Builder")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Add Option")

        opt_type = st.selectbox("Option Type", ["Call", "Put"])
        style = st.selectbox("Style", ["European", "American"])

        col_a, col_b = st.columns(2)
        with col_a:
            strike = st.number_input(
                "Strike Price", min_value=1.0, value=100.0, step=1.0
            )
            expiry = st.number_input(
                "Time to Expiry (years)", min_value=0.01, value=1.0, step=0.1
            )
        with col_b:
            quantity = st.number_input("Quantity", value=10, step=1)
            asset_id = st.text_input("Asset ID", value="AAPL").upper()

        pricing_model = "Black-Scholes"
        if style == "European":
            pricing_model = st.selectbox(
                "Pricing Model", ["Black-Scholes", "Binomial", "Merton Jump Diffusion"]
            )

        if st.button("Add to Portfolio", type="primary"):
            try:
                option_type = OptionType.CALL if opt_type == "Call" else OptionType.PUT

                if style == "American":
                    from risk_engine.core.binomial import OptionType as BinOptType

                    bin_opt_type = (
                        BinOptType.CALL if opt_type == "Call" else BinOptType.PUT
                    )
                    instrument = AmericanOption(bin_opt_type, strike, expiry, asset_id)
                else:
                    pr_model = PricingModel.BLACKSCHOLES
                    if pricing_model == "Binomial":
                        pr_model = PricingModel.BINOMIAL
                    elif pricing_model == "Merton Jump Diffusion":
                        pr_model = PricingModel.MERTON_JUMP_DIFFUSION

                    instrument = EuropeanOption(
                        option_type, strike, expiry, asset_id, pr_model
                    )

                st.session_state.portfolio.add_instrument(instrument, quantity)
                st.session_state.instruments_list.append(
                    {
                        "type": f"{style} {opt_type}",
                        "strike": strike,
                        "expiry": expiry,
                        "asset": asset_id,
                        "quantity": quantity,
                        "model": pricing_model,
                    }
                )
                st.success(f"Added {style} {opt_type} to portfolio")
            except Exception as e:
                st.error(f"Error: {e}")

    with col2:
        st.subheader("Current Portfolio")
        if st.session_state.instruments_list:
            df = pd.DataFrame(st.session_state.instruments_list)
            st.dataframe(df, hide_index=True, width="stretch")

            total_contracts = sum(
                inst["quantity"] for inst in st.session_state.instruments_list
            )
            st.metric("Total Contracts", total_contracts)

            if st.button("Clear Portfolio"):
                st.session_state.portfolio = Portfolio()
                st.session_state.instruments_list = []
                st.rerun()
        else:
            st.info("No instruments in portfolio")

    if st.session_state.instruments_list:
        st.divider()
        st.subheader("Portfolio Allocation")
        assets = [inst["asset"] for inst in st.session_state.instruments_list]
        quantities = [inst["quantity"] for inst in st.session_state.instruments_list]

        alloc_df = pd.DataFrame({"Asset": assets, "Quantity": quantities})
        alloc_agg = alloc_df.groupby("Asset")["Quantity"].sum().reset_index()

        fig_pie = px.pie(
            alloc_agg,
            values="Quantity",
            names="Asset",
            title="Portfolio by Asset",
            hole=0.4,
        )
        st.plotly_chart(fig_pie, width="stretch")

elif page == "Risk Analysis":
    st.header("Risk Analysis")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Market Data")

        assets = list(
            set([inst["asset"] for inst in st.session_state.instruments_list])
        )

        if not assets:
            st.warning("Add instruments to portfolio first")
        else:
            st.markdown("**Auto-populate from yfinance**")
            if st.button("Fetch Live Prices", key="fetch_prices"):
                try:
                    fetcher = get_market_data_fetcher()
                    live_data, failed = fetcher.fetch_multiple(
                        assets, force_refresh=True
                    )
                    if live_data:
                        for asset, data in live_data.items():
                            st.session_state.live_market_data[asset] = data
                        st.success(f"Fetched prices for {len(live_data)} assets")
                    if failed:
                        st.warning(f"Failed: {failed}")
                except Exception as e:
                    st.error(f"Error: {e}")

            for asset in assets:
                st.markdown(f"**{asset}**")
                c1, c2, c3, c4 = st.columns(4)

                default_spot = 100.0
                default_vol = 0.25
                default_rate = 0.05
                default_div = 0.0

                if asset in st.session_state.live_market_data:
                    live = st.session_state.live_market_data[asset]
                    default_spot = live.get("spot", 100.0)
                    default_vol = live.get("vol", 0.25)
                    default_rate = live.get("rate", 0.05)
                    default_div = live.get("dividend", 0.0)

                with c1:
                    spot = st.number_input(
                        f"{asset} Spot",
                        min_value=0.01,
                        value=float(default_spot),
                        key=f"spot_{asset}",
                    )
                with c2:
                    vol = st.number_input(
                        f"{asset} Vol",
                        min_value=0.01,
                        value=float(default_vol),
                        key=f"vol_{asset}",
                    )
                with c3:
                    rate = st.number_input(
                        f"{asset} Rate",
                        min_value=0.0,
                        value=float(default_rate),
                        key=f"rate_{asset}",
                    )
                with c4:
                    div = st.number_input(
                        f"{asset} Div",
                        min_value=0.0,
                        value=float(default_div),
                        key=f"div_{asset}",
                    )

                st.session_state.market_data_map[asset] = MarketData(
                    asset_id=asset, spot=spot, rate=rate, vol=vol, dividend=div
                )

    with col2:
        st.subheader("VaR Parameters")

        n_sims = st.slider("VaR Simulations", 1000, 100000, 10000, step=1000)
        time_horizon = st.slider("Time Horizon (days)", 1, 252, 1)

        if st.button("Calculate Risk", type="primary"):
            if st.session_state.portfolio.is_empty():
                st.error("Portfolio is empty")
            elif not st.session_state.market_data_map:
                st.error("No market data provided")
            else:
                try:
                    engine = RiskEngine(var_simulations=n_sims)
                    engine.set_var_time_horizon_days(time_horizon)

                    result = engine.calculate_portfolio_risk(
                        st.session_state.portfolio, st.session_state.market_data_map
                    )

                    st.session_state.risk_result = result
                    st.success("Risk calculation complete!")
                except Exception as e:
                    st.error(f"Error: {e}")

    if "risk_result" in st.session_state:
        result = st.session_state.risk_result

        st.divider()
        st.subheader("Risk Metrics")

        m1, m2, m3, m4, m5 = st.columns(5)

        m1.metric("Total PV", f"${result.total_pv:,.2f}")
        m2.metric("Delta", f"{result.total_delta:,.2f}")
        m3.metric("Gamma", f"{result.total_gamma:,.4f}")
        m4.metric("Vega", f"{result.total_vega:,.2f}")
        m5.metric("Theta", f"{result.total_theta:,.4f}")

        st.divider()

        v1, v2, v3, v4 = st.columns(4)

        v1.metric("VaR 95%", f"${result.value_at_risk_95:,.2f}")
        v2.metric("VaR 99%", f"${result.value_at_risk_99:,.2f}")
        v3.metric("ES 95%", f"${result.expected_shortfall_95:,.2f}")
        v4.metric("ES 99%", f"${result.expected_shortfall_99:,.2f}")

        st.info(f"Portfolio Size: {result.portfolio_size} positions")

        st.divider()
        st.subheader("VaR Distribution")

        st.info(
            "Monte Carlo VaR simulation data is available. View detailed risk metrics above."
        )

elif page == "Market Data":
    st.header("Market Data")

    st.subheader("Fetch Live Data")

    ticker_input = st.text_input(
        "Enter ticker symbols (comma separated)", value="AAPL,MSFT,GOOGL,AMZN,TSLA"
    )

    col_f1, col_f2 = st.columns([1, 2])
    with col_f1:
        if st.button("Fetch Data"):
            if not ticker_input.strip():
                st.error("Please enter at least one ticker")
            else:
                tickers = [t.strip().upper() for t in ticker_input.split(",")]

                try:
                    fetcher = get_market_data_fetcher()
                    successful, failed = fetcher.fetch_multiple(tickers)

                    if successful:
                        st.success(f"Fetched {len(successful)} tickers")
                        df_market = pd.DataFrame(successful).T
                        st.dataframe(df_market, width="stretch")
                    if failed:
                        st.warning(f"Failed to fetch {len(failed)} tickers: {failed}")
                except ImportError as e:
                    st.error(f"yfinance not installed: {e}")
                except Exception as e:
                    st.error(f"Error: {e}")

    st.divider()

    st.subheader("Historical Price Charts")

    chart_ticker = st.selectbox("Select ticker for chart", ticker_input.split(","))
    if chart_ticker:
        chart_ticker = chart_ticker.strip().upper()
        try:
            from risk_engine.market_data.fetcher import YFINANCE_AVAILABLE

            if YFINANCE_AVAILABLE:
                import yfinance as yf

                stock = yf.Ticker(chart_ticker)
                hist = stock.history(period="1y")

                if not hist.empty:
                    fig_hist = go.Figure()
                    fig_hist.add_trace(
                        go.Candlestick(
                            x=hist.index,
                            open=hist["Open"],
                            high=hist["High"],
                            low=hist["Low"],
                            close=hist["Close"],
                            name=chart_ticker,
                        )
                    )
                    fig_hist.update_layout(
                        title=f"{chart_ticker} - 1 Year Price History",
                        xaxis_title="Date",
                        yaxis_title="Price ($)",
                        height=400,
                    )
                    st.plotly_chart(fig_hist, width="stretch")
                else:
                    st.warning(f"No historical data for {chart_ticker}")
            else:
                st.warning("yfinance not available")
        except Exception as e:
            st.error(f"Error fetching chart: {e}")

    st.divider()

    st.subheader("Cached Data")

    try:
        fetcher = get_market_data_fetcher()
        cached = fetcher.cache.get_all()

        if cached:
            st.dataframe(pd.DataFrame(cached).T, width="stretch")
        else:
            st.info("No cached data")
    except Exception as e:
        st.info("No cache available")

elif page == "Visualizations":
    st.header("Visualizations")

    if not st.session_state.instruments_list:
        st.warning("Add instruments to portfolio first")
    else:
        st.subheader("Option Payoff Diagrams")

        selected_instrument = st.selectbox(
            "Select instrument",
            range(len(st.session_state.instruments_list)),
            format_func=lambda i: (
                f"{st.session_state.instruments_list[i]['type']} {st.session_state.instruments_list[i]['asset']} Strike: {st.session_state.instruments_list[i]['strike']}"
            ),
        )

        inst = st.session_state.instruments_list[selected_instrument]
        strike = inst["strike"]
        opt_type = inst["type"]
        is_call = "Call" in opt_type

        spot_price = 100.0
        if inst["asset"] in st.session_state.market_data_map:
            spot_price = st.session_state.market_data_map[inst["asset"]].spot

        price_range = np.linspace(spot_price * 0.5, spot_price * 1.5, 100)

        if is_call:
            payoffs = np.maximum(price_range - strike, 0)
        else:
            payoffs = np.maximum(strike - price_range, 0)

        fig_payoff = go.Figure()
        fig_payoff.add_trace(
            go.Scatter(
                x=price_range,
                y=payoffs,
                mode="lines",
                name="Payoff at Expiry",
                line=dict(color="#00CC96", width=2),
            )
        )
        fig_payoff.add_vline(
            x=spot_price,
            line_dash="dot",
            line_color="gray",
            annotation_text="Current Spot",
        )
        fig_payoff.add_vline(
            x=strike,
            line_dash="dash",
            line_color="blue",
            annotation_text="Strike",
        )

        fig_payoff.update_layout(
            title=f"Payoff Diagram - {opt_type}",
            xaxis_title="Underlying Price ($)",
            yaxis_title="Payoff ($)",
        )
        st.plotly_chart(fig_payoff, width="stretch")

        st.divider()

        st.subheader("Portfolio Greeks Exposure")

        assets = list(set([i["asset"] for i in st.session_state.instruments_list]))

        if assets and st.session_state.market_data_map:
            greeks_data = []

            for asset in assets:
                md = st.session_state.market_data_map.get(asset)
                if md:
                    for inst in st.session_state.instruments_list:
                        if inst["asset"] == asset:
                            strike = inst["strike"]
                            expiry = inst["expiry"]
                            quantity = inst["quantity"]

                            from risk_engine.core.blackscholes import (
                                call_delta,
                                put_delta,
                                gamma,
                                vega,
                                call_theta,
                                put_theta,
                            )

                            try:
                                is_call = "Call" in inst["type"]
                                bs_delta = (
                                    call_delta(md.spot, strike, md.rate, expiry, md.vol)
                                    if is_call
                                    else put_delta(
                                        md.spot, strike, md.rate, expiry, md.vol
                                    )
                                )
                                bs_gamma = gamma(
                                    md.spot, strike, md.rate, expiry, md.vol
                                )
                                bs_vega = vega(md.spot, strike, md.rate, expiry, md.vol)
                                bs_theta = (
                                    call_theta(md.spot, strike, md.rate, expiry, md.vol)
                                    if is_call
                                    else put_theta(
                                        md.spot, strike, md.rate, expiry, md.vol
                                    )
                                )

                                greeks_data.append(
                                    {
                                        "Asset": asset,
                                        "Type": inst["type"],
                                        "Delta": bs_delta * quantity,
                                        "Gamma": bs_gamma * quantity,
                                        "Vega": bs_vega * quantity,
                                        "Theta": bs_theta * quantity,
                                    }
                                )
                            except Exception:
                                pass

            if greeks_data:
                greeks_df = pd.DataFrame(greeks_data)

                c1, c2 = st.columns(2)

                with c1:
                    fig_delta = px.bar(
                        greeks_df,
                        x="Asset",
                        y="Delta",
                        color="Type",
                        title="Delta by Asset",
                    )
                    st.plotly_chart(fig_delta, width="stretch")

                with c2:
                    fig_gamma = px.bar(
                        greeks_df,
                        x="Asset",
                        y="Gamma",
                        color="Type",
                        title="Gamma by Asset",
                    )
                    st.plotly_chart(fig_gamma, width="stretch")

                c3, c4 = st.columns(2)
                with c3:
                    fig_vega = px.bar(
                        greeks_df,
                        x="Asset",
                        y="Vega",
                        color="Type",
                        title="Vega by Asset",
                    )
                    st.plotly_chart(fig_vega, width="stretch")

                with c4:
                    fig_theta = px.bar(
                        greeks_df,
                        x="Asset",
                        y="Theta",
                        color="Type",
                        title="Theta by Asset",
                    )
                    st.plotly_chart(fig_theta, width="stretch")

elif page == "Greeks Analysis":
    st.header("Greeks Analysis")

    if not st.session_state.instruments_list:
        st.warning("Add instruments to portfolio first")
    else:
        assets = list(set([i["asset"] for i in st.session_state.instruments_list]))

        if not assets:
            st.warning("No assets in portfolio")
        else:
            selected_asset = st.selectbox("Select Asset", assets)

            asset_instruments = [
                i
                for i in st.session_state.instruments_list
                if i["asset"] == selected_asset
            ]

            md = st.session_state.market_data_map.get(selected_asset)
            if not md:
                st.warning(
                    f"Set market data for {selected_asset} in Risk Analysis first"
                )
            else:
                st.subheader(f"Greeks Heatmap - {selected_asset}")

                strikes = np.linspace(md.spot * 0.5, md.spot * 1.5, 20)
                expiries = np.linspace(0.1, 2.0, 10)

                delta_grid = np.zeros((len(expiries), len(strikes)))
                gamma_grid = np.zeros((len(expiries), len(strikes)))
                vega_grid = np.zeros((len(expiries), len(strikes)))

                from risk_engine.core.blackscholes import call_delta, gamma, vega

                for i, exp in enumerate(expiries):
                    for j, strike in enumerate(strikes):
                        try:
                            bs_delta = call_delta(md.spot, strike, md.rate, exp, md.vol)
                            bs_gamma = gamma(md.spot, strike, md.rate, exp, md.vol)
                            bs_vega = vega(md.spot, strike, md.rate, exp, md.vol)

                            delta_grid[i, j] = bs_delta
                            gamma_grid[i, j] = bs_gamma
                            vega_grid[i, j] = bs_vega
                        except Exception:
                            pass

                tab1, tab2, tab3 = st.tabs(["Delta", "Gamma", "Vega"])

                with tab1:
                    fig_delta = go.Figure(
                        data=go.Heatmap(
                            z=delta_grid,
                            x=strikes,
                            y=expiries,
                            colorscale="RdBu",
                            colorbar_title="Delta",
                        )
                    )
                    fig_delta.update_layout(
                        title="Delta Heatmap",
                        xaxis_title="Strike Price",
                        yaxis_title="Time to Expiry (years)",
                    )
                    st.plotly_chart(fig_delta, width="stretch")

                with tab2:
                    fig_gamma = go.Figure(
                        data=go.Heatmap(
                            z=gamma_grid,
                            x=strikes,
                            y=expiries,
                            colorscale="Viridis",
                            colorbar_title="Gamma",
                        )
                    )
                    fig_gamma.update_layout(
                        title="Gamma Heatmap",
                        xaxis_title="Strike Price",
                        yaxis_title="Time to Expiry (years)",
                    )
                    st.plotly_chart(fig_gamma, width="stretch")

                with tab3:
                    fig_vega = go.Figure(
                        data=go.Heatmap(
                            z=vega_grid,
                            x=strikes,
                            y=expiries,
                            colorscale="Plasma",
                            colorbar_title="Vega",
                        )
                    )
                    fig_vega.update_layout(
                        title="Vega Heatmap",
                        xaxis_title="Strike Price",
                        yaxis_title="Time to Expiry (years)",
                    )
                    st.plotly_chart(fig_vega, width="stretch")

                st.divider()
                st.subheader("Implied Volatility Surface")

                vol_grid = np.zeros((len(expiries), len(strikes)))
                for i, exp in enumerate(expiries):
                    for j, strike in enumerate(strikes):
                        moneyness = strike / md.spot
                        vol_grid[i, j] = md.vol * (1 + 0.2 * (moneyness - 1))

                fig_3d = go.Figure(
                    data=go.Surface(
                        z=vol_grid,
                        x=strikes,
                        y=expiries,
                        colorscale="Viridis",
                        colorbar_title="IV",
                    )
                )
                fig_3d.update_layout(
                    title="Implied Volatility Surface",
                    scene=dict(
                        xaxis_title="Strike",
                        yaxis_title="Expiry (years)",
                        zaxis_title="Volatility",
                    ),
                    height=500,
                )
                st.plotly_chart(fig_3d, width="stretch")

st.sidebar.markdown("---")
st.sidebar.caption("Risk Engine v4.0 | Pure Python")
