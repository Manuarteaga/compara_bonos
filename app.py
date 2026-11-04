import streamlit as st
import plotly.graph_objects as go

# ---------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA Y ESTILOS
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI CapEx & Debt Risk Dashboard",
    page_icon="📈",
    layout="wide"
)

# Título y Subtítulo
st.title("📈 AI CapEx, Debt Risk & Portfolio Dashboard")
st.caption("Análisis de sostenibilidad de deuda Big Tech & Simulador de Reestructuración de Cartera")

# Métrica destacada del Bono a 10 años
col_header, _ = st.columns([1, 2])
with col_header:
    st.metric(label="EE.UU. 10Y Treasury Yield (Referencia)", value="4.50%")

st.divider()

# ---------------------------------------------------------
# DATOS INICIALES DE EJEMPLO
# ---------------------------------------------------------
companies_data = {
    "Oracle (ORCL)": {"capex": 24000, "fcf": -24000, "debt": 43000, "roi": 6.0},
    "Microsoft (MSFT)": {"capex": 55000, "fcf": 65000, "debt": 20000, "roi": 10.0},
    "Alphabet (GOOGL)": {"capex": 48000, "fcf": 60000, "debt": 15000, "roi": 9.0},
    "Meta (META)": {"capex": 38000, "fcf": 35000, "debt": 18000, "roi": 8.5},
    "Amazon (AMZN)": {"capex": 60000, "fcf": 30000, "debt": 25000, "roi": 7.5}
}

# ---------------------------------------------------------
# NAVEGACIÓN DE PESTAÑAS
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "💻 Estrés Deuda Big Tech", 
    "📊 Spreads de Crédito & Bonos", 
    "🧩 Simulador de Cartera Táctica"
])

# =========================================================
# TAB 1: ESTRÉS DEUDA BIG TECH
# =========================================================
with tab1:
    st.header("Evaluador de Sostenibilidad por Empresa")
    
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        st.subheader("Parámetros")
        selected_company = st.selectbox("Selecciona Empresa", list(companies_data.keys()))
        data = companies_data[selected_company]
        
        # Formulario interactivo
        capex = st.number_input("Gasto CapEx IA Anual (mUSD)", value=data["capex"], step=1000)
        fcf = st.number_input("Flujo de Caja Libre / FCF (mUSD)", value=data["fcf"], step=1000)
        debt = st.number_input("Deuda Emitida Reciente (mUSD)", value=data["debt"], step=1000)
        roi = st.slider("Retorno Esperado de IA (%)", min_value=0.0, max_value=20.0, value=data["roi"], step=0.5)

    with col_right:
        st.subheader("Métricas de Riesgo")
        
        # Cálculos de Cobertura e Indigestión
        fcf_coverage = round(fcf / capex, 2) if capex > 0 else 0
        
        m_col1, m_col2 = st.columns(2)
        
        with m_col1:
            st.metric(
                label="Cobertura FCF / CapEx", 
                value=f"{fcf_coverage}x", 
                delta="Caja Negativa" if fcf < 0 else ("Excelente" if fcf >= capex else "Ajustada"),
                delta_color="inverse" if fcf < 0 else "normal"
            )
        
        with m_col2:
            indigestion_status = "ELEVADO" if (fcf < 0 or capex > 40000) else "MODERADO"
            st.metric(
                label="Nivel de Indigestión de Deuda", 
                value=indigestion_status,
                delta="Riesgo Emisión" if indigestion_status == "ELEVADO" else "Sostenible",
                delta_color="inverse" if indigestion_status == "ELEVADO" else "normal"
            )

        # Gráfico Plotly: FCF vs CapEx
        fig_bar = go.Figure(data=[
            go.Bar(
                x=["Flujo Caja Libre (FCF)", "CapEx en IA"],
                y=[fcf, capex],
                marker_color=["#EF4444" if fcf < 0 else "#10B981", "#3B82F6"]
            )
        ])
        fig_bar.update_layout(
            title_text=f"Balance de Caja vs CapEx en IA ({selected_company})",
            yaxis_title="Millones de USD",
            template="plotly_dark",
            height=320
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# =========================================================
# TAB 2: SPREADS DE CRÉDITO Y BONOS
# =========================================================
with tab2:
    st.header("Competencia por el Dinero: Tesoro EE.UU. vs Big Tech")
    st.write(
        """
        Las Big Tech (Microsoft, Apple, Alphabet) tienen máxima solvencia financiera y un riesgo de impago (*default*) ínfimo. 
        Sin embargo, al emitir grandes volúmenes de deuda compiten con el Tesoro de EE.UU., lo que incrementa los **cupones/intereses** 
        que deben ofrecer a los inversores.
        """
    )
    
    col_s1, col_s2, col_s3 = st.columns(3)
    col_s1.metric("Bono EE.UU. 10Y (Sin Riesgo)", "4.50%")
    col_s2.metric("Rendimiento Medio Bono Big Tech", "5.35%")
    col_s3.metric("Diferencial de Crédito (Spread)", "+85 bps (0.85%)")

    st.info(
        """
        **💡 Matiz Clave para la Renta Fija:**  
        Si mantienes el bono hasta su vencimiento, cobras el 100% de tu capital e intereses. 
        El ajuste de precio solo afecta a las cotizaciones secundarias si vendes el fondo antes de tiempo.
        """
    )

# =========================================================
# TAB 3: SIMULADOR DE CARTERA TÁCTICA
# =========================================================
with tab3:
    st.header("Simulador de Reestructuración de Cartera")
    
    col_p_left, col_p_right = st.columns([1, 2])
    
    with col_p_left:
        scenario = st.radio(
            "Selecciona Escenario de Mercado:",
            ("Ajuste de Valoración IA / Tensión de Deuda", "Escenario Moderado / Transición", "Boom Tecnológico Continuado en EE.UU.")
        )
        
        st.markdown("---")
        st.markdown("**Composición de Tu Cartera Defensiva:**")
        st.write("• S&P 500 (EE.UU.): **10%**")
        st.write("• Fondos Europeos (Stoxx 600): **20%**")
        st.write("• Nikkei / Japón: **10%**")
        st.write("• Oro: **10%**")
        st.write("• Renta Fija (Tesoro / Tech): **50%**")
        
        st.success(
            "Estrategia táctica: Si la IA confirma retornos sólidos, mantienes el 50% en Renta Fija como pólvora seca para rotar paulatinamente de vuelta al S&P 500."
        )

    with col_p_right:
        # Lógica de rendimiento según escenario
        if scenario == "Ajuste de Valoración IA / Tensión de Deuda":
            trad_ret, def_ret = -8.5, 4.2
        elif scenario == "Escenario Moderado / Transición":
            trad_ret, def_ret = 6.0, 5.5
        else:
            trad_ret, def_ret = 15.0, 8.0

        p_m1, p_m2 = st.columns(2)
        p_m1.metric("Cartera Tradicional (50% S&P 500)", f"{trad_ret}% / año")
        p_m2.metric("Tu Cartera Defensiva", f"{def_ret}% / año")

        # Gráfico comparativo de carteras
        fig_port = go.Figure(data=[
            go.Bar(
                x=["Cartera Tradicional (50% S&P 500)", "Tu Cartera Defensiva"],
                y=[trad_ret, def_ret],
                marker_color=["#EF4444" if trad_ret < 0 else "#6366F1", "#10B981"]
            )
        ])
        fig_port.update_layout(
            title_text="Rentabilidad Estimada Anualizada por Cartera (%)",
            yaxis_title="Rentabilidad %",
            template="plotly_dark",
            height=320
        )
        st.plotly_chart(fig_port, use_container_width=True)
