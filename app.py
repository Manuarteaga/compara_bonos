import streamlit as st
import yfinance as yf
import pandas as pd

# ---------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="Comparador Global de Deuda y Carteras",
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ Evaluador & Comparador Financiero de Deuda y Carteras")
st.caption("Conexión con Yahoo Finance | Comparador Global de Renta Fija | Proyección de Carteras Ficticias")

st.divider()

# NAVEGACIÓN DE PESTAÑAS
tab1, tab2, tab3 = st.tabs([
    "🏢 Muestreo Big Tech (Yahoo Finance)", 
    "🌍 Comparador Global de Deuda", 
    "📊 Comparador de Carteras (1-10 años)"
])

# =========================================================
# PESTAÑA 1: DATOS REALES YAHOO FINANCE
# =========================================================
with tab1:
    st.header("🏢 Datos Financieros Oficiales (Sin modificación manual)")
    st.write("Los datos se extraen en tiempo real directamente desde Yahoo Finance a partir de los últimos balances publicados.")
    
    ticker_dict = {
        "Microsoft (MSFT)": "MSFT",
        "Alphabet / Google (GOOGL)": "GOOGL",
        "Meta (META)": "META",
        "Amazon (AMZN)": "AMZN",
        "Oracle (ORCL)": "ORCL"
    }
    
    selected_name = st.selectbox("Selecciona la empresa a consultar:", list(ticker_dict.keys()))
    ticker_symbol = ticker_dict[selected_name]
    
    with st.spinner(f"Obteniendo datos de {ticker_symbol} desde Yahoo Finance..."):
        try:
            ticker = yf.Ticker(ticker_symbol)
            cashflow = ticker.cashflow
            balance = ticker.balance_sheet
            
            # Extracción de valores clave
            fcf = None
            capex = None
            total_debt = None
            
            if cashflow is not None and not cashflow.empty:
                if 'Free Cash Flow' in cashflow.index:
                    fcf = cashflow.loc['Free Cash Flow'].iloc[0]
                if 'Capital Expenditure' in cashflow.index:
                    capex = abs(cashflow.loc['Capital Expenditure'].iloc[0])
                    
            if balance is not None and not balance.empty:
                if 'Total Debt' in balance.index:
                    total_debt = balance.loc['Total Debt'].iloc[0]

            # Mostrar métricas sin edición
            m1, m2, m3 = st.columns(3)
            
            fcf_m = f"${fcf / 1e9:.2f} B" if fcf is not None else "No disponible"
            capex_m = f"${capex / 1e9:.2f} B" if capex is not None else "No disponible"
            debt_m = f"${total_debt / 1e9:.2f} B" if total_debt is not None else "No disponible"
            
            m1.metric("Flujo de Caja Libre (FCF)", fcf_m)
            m2.metric("Gasto de Capital (CapEx)", capex_m)
            m3.metric("Deuda Total", debt_m)
            
            # Diagnóstico de Cobertura
            st.markdown("---")
            if fcf is not None and capex is not None and capex > 0:
                coverage = fcf / capex
                st.subheader(f"Ratio Cobertura FCF / CapEx: **{coverage:.2f}x**")
                if coverage < 0:
                    st.error("⚠️ **Caja Negativa:** El negocio no genera suficiente efectivo por sí mismo para cubrir su CapEx e infraestructuras. Requiere endeudamiento.")
                elif coverage < 1.0:
                    st.warning("⚡ **Cobertura Ajustada:** El CapEx supera la generación de flujo de caja libre.")
                else:
                    st.success("✅ **Cobertura Solvente:** La empresa genera suficiente flujo de caja libre para autofinanciar sus inversiones.")
                    
        except Exception as e:
            st.error(f"Error al conectar con Yahoo Finance: {e}")

# =========================================================
# PESTAÑA 2: COMPARADOR GLOBAL DE DEUDA
# =========================================================
with tab2:
    st.header("🌍 Comparador de Intereses de Deuda (Países y Empresas)")
    st.write("Compara el rendimiento (*yield*) de la deuda a 10 años entre distintas economías o bonos corporativos.")
    
    # Base de datos de rendimientos de referencia (Estimados / Actualizables)
    yields_db = {
        "EE.UU. (Tesoro 10Y)": 4.50,
        "España (Bono 10Y)": 3.15,
        "Alemania (Bund 10Y)": 2.30,
        "Francia (OAT 10Y)": 3.00,
        "Japón (JGB 10Y)": 0.95,
        "Microsoft (Deuda Corporativa Grado A)": 5.20,
        "Oracle (Deuda Corporativa)": 5.80,
        "ASML / Tech Europa (Deuda Corporativa)": 3.80,
        "Iberdrola / Utility Europa (Deuda Corporativa)": 4.10
    }
    
    col_d1, col_d2 = st.columns(2)
    
    with col_d1:
        emisor_a = st.selectbox("Selecciona Emisor / País A:", list(yields_db.keys()), index=0)
        yield_a = yields_db[emisor_a]
        st.metric(f"Interés / Rendimiento ({emisor_a})", f"{yield_a:.2f}%")
        
    with col_d2:
        emisor_b = st.selectbox("Selecciona Emisor / País B:", list(yields_db.keys()), index=1)
        yield_b = yields_db[emisor_b]
        st.metric(f"Interés / Rendimiento ({emisor_b})", f"{yield_b:.2f}%")
        
    st.markdown("---")
    diff = abs(yield_a - yield_b)
    bps = diff * 100
    
    if yield_a > yield_b:
        st.info(f"💡 **Diferencial (Spread):** **{emisor_a}** ofrece **{diff:.2f}% más de rendimiento** (+{bps:.0f} puntos básicos) que **{emisor_b}**.")
    elif yield_b > yield_a:
        st.info(f"💡 **Diferencial (Spread):** **{emisor_b}** ofrece **{diff:.2f}% más de rendimiento** (+{bps:.0f} puntos básicos) que **{emisor_a}**.")
    else:
        st.info("💡 Ambos emisores ofrecen exactamente el mismo rendimiento.")

# =========================================================
# PESTAÑA 3: COMPARADOR DE CARTERAS A TEMPORALIDAD
# =========================================================
with tab3:
    st.header("📊 Comparador de Carteras Ficticias")
    st.write("Configura dos carteras ficticias para comparar sus proyecciones acumuladas al horizonte temporal que elijas.")
    
    # Rendimientos medios estimados por activo (% anual)
    asset_returns = {
        "S&P 500 (EE.UU.)": 8.0,
        "Fondos Europeos": 5.5,
        "Japón (Nikkei)": 5.0,
        "Oro": 4.0,
        "Deuda Elegida en Pestaña 2": yield_a  # Usa el emisor A de la pestaña 2
    }
    
    years = st.slider("Selecciona el Horizonte Temporal (Años):", min_value=1, max_value=10, value=10)
    initial_capital = st.number_input("Inversión Inicial (€ / $):", value=10000, step=1000)
    
    c_col1, c_col2 = st.columns(2)
    
    with c_col1:
        st.subheader("Configuración Cartera A")
        p_sp500_a = st.slider("S&P 500 (%)", 0, 100, 50, key="sp_a")
        p_eur_a = st.slider("Fondos Europeos (%)", 0, 100, 20, key="eur_a")
        p_deuda_a = st.slider(f"Deuda ({emisor_a}) (%)", 0, 100, 30, key="deuda_a")
        
        tot_a = p_sp500_a + p_eur_a + p_deuda_a
        if tot_a != 100:
            st.caption(f"⚠️ La suma de porcentajes debe ser 100% (Actual: {tot_a}%)")
            
        ret_weighted_a = ((p_sp500_a * asset_returns["S&P 500 (EE.UU.)"]) + 
                          (p_eur_a * asset_returns["Fondos Europeos"]) + 
                          (p_deuda_a * yield_a)) / 100.0

    with c_col2:
        st.subheader("Configuración Cartera B")
        p_sp500_b = st.slider("S&P 500 (%)", 0, 100, 10, key="sp_b")
        p_eur_b = st.slider("Fondos Europeos (%)", 0, 100, 20, key="eur_b")
        p_deuda_b = st.slider(f"Deuda ({emisor_a}) (%)", 0, 100, 70, key="deuda_b")
        
        tot_b = p_sp500_b + p_eur_b + p_deuda_b
        if tot_b != 100:
            st.caption(f"⚠️ La suma de porcentajes debe ser 100% (Actual: {tot_b}%)")
            
        ret_weighted_b = ((p_sp500_b * asset_returns["S&P 500 (EE.UU.)"]) + 
                          (p_eur_b * asset_returns["Fondos Europeos"]) + 
                          (p_deuda_b * yield_a)) / 100.0

    st.markdown("---")
    st.subheader(f"📈 Resultados Proyectados a {years} Años (Capital Inicial: {initial_capital:,.0f}€)")
    
    final_val_a = initial_capital * ((1 + ret_weighted_a / 100) ** years)
    final_val_b = initial_capital * ((1 + ret_weighted_b / 100) ** years)
    
    profit_a = final_val_a - initial_capital
    profit_b = final_val_b - initial_capital
    
    res_col1, res_col2 = st.columns(2)
    
    with res_col1:
        st.markdown("### Cartera A")
        st.metric("Rendimiento Anual Medio", f"{ret_weighted_a:.2f}%")
        st.metric(f"Valor Final tras {years} Años", f"{final_val_a:,.2f} €", delta=f"+{profit_a:,.2f} € Ganancia")
        
    with res_col2:
        st.markdown("### Cartera B")
        st.metric("Rendimiento Anual Medio", f"{ret_weighted_b:.2f}%")
        st.metric(f"Valor Final tras {years} Años", f"{final_val_b:,.2f} €", delta=f"+{profit_b:,.2f} € Ganancia")
        
    st.markdown("---")
    diff_profit = abs(profit_a - profit_b)
    if profit_a > profit_b:
        st.success(f"🏆 **La Cartera A** genera **{diff_profit:,.2f} € más de beneficio** que la Cartera B en el horizonte de {years} años.")
    elif profit_b > profit_a:
        st.success(f"🏆 **La Cartera B** genera **{diff_profit:,.2f} € más de beneficio** que la Cartera A en el horizonte de {years} años.")
    else:
        st.info("Ambas carteras producen exactamente la misma ganancia proyectada.")
