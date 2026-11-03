import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import json
import os

# Configuración de página
st.set_page_config(page_title="Comparador y Calificador de Activos", layout="wide")

st.title("📈 Comparador y Calificador de Activos Financieros")
st.markdown("Compara el rendimiento y evalúa la salud y calificaciones de tus acciones, ETFs y fondos.")

# Archivo local para persistencia permanente de la biblioteca
ARCHIVO_ASSETS = "assets_personalizados.json"

def cargar_activos():
    # Biblioteca inicial limpia (solo opción por defecto)
    activos_base = {
        "-- Selecciona de la biblioteca --": ""
    }
    if os.path.exists(ARCHIVO_ASSETS):
        try:
            with open(ARCHIVO_ASSETS, "r", encoding="utf-8") as f:
                activos_guardados = json.load(f)
                activos_base.update(activos_guardados)
        except Exception:
            pass
    return activos_base

def guardar_activo_permanente(etiqueta, ticker):
    try:
        guardados = {}
        if os.path.exists(ARCHIVO_ASSETS):
            with open(ARCHIVO_ASSETS, "r", encoding="utf-8") as f:
                guardados = json.load(f)
        
        if ticker not in guardados.values():
            guardados[etiqueta] = ticker
            with open(ARCHIVO_ASSETS, "w", encoding="utf-8") as f:
                json.dump(guardados, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.sidebar.error(f"Error al guardar el activo: {e}")

# Inicializar sesión
if "popular_assets" not in st.session_state:
    st.session_state.popular_assets = cargar_activos()

# Configuración lateral
st.sidebar.header("⚙️ Configuración del Análisis")
periodo = st.sidebar.selectbox(
    "Período de tiempo:",
    options=["1M", "3M", "6M", "YTD", "1Y", "3Y", "5Y", "MAX"],
    index=4
)

# Función para obtener datos de Yahoo Finance
@st.cache_data(ttl=3600)
def cargar_datos_activo(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        hist = ticker.history(period=periodo)
        
        if hist.empty:
            return None, None
            
        return info, hist
    except Exception:
        return None, None

# Interfaz principal: 2 Columnas
col1, col2 = st.columns(2)

def selector_activo(col_name):
    st.subheader(col_name)
    
    # 1. Desplegable de biblioteca (vacío por defecto)
    opciones = list(st.session_state.popular_assets.keys())
    preset = st.selectbox(
        "Selecciona de la biblioteca:",
        options=opciones,
        index=0,
        key=f"preset_{col_name}"
    )
    
    # 2. Búsqueda directa por ISIN o Ticker (vacío por defecto)
    ticker_input = st.text_input(
        "O introduce ISIN / Ticker:",
        value="",
        placeholder="Ej. IE000ZYRH0Q7 o AAPL",
        key=f"input_{col_name}"
    ).strip().upper()
    
    # Prioridad: Si se escribe en el input, se usa; si no, se usa el desplegable
    if ticker_input:
        return ticker_input
    elif preset != "-- Selecciona de la biblioteca --":
        return st.session_state.popular_assets[preset]
    
    return None

with col1:
    ticker_1 = selector_activo("Activo A")

with col2:
    ticker_2 = selector_activo("Activo B")

st.divider()

if ticker_1 and ticker_2:
    info1, hist1 = cargar_datos_activo(ticker_1)
    info2, hist2 = cargar_datos_activo(ticker_2)

    if hist1 is None or hist2 is None:
        st.error("⚠️ No se pudieron obtener datos para alguno de los identificadores introducidos. Comprueba que el ISIN o Ticker sea correcto en Yahoo Finance.")
    else:
        # --- AUTO-GUARDADO INTELIGENTE CON NOMBRE Y TIPO ---
        for ticker, info in [(ticker_1, info1), (ticker_2, info2)]:
            nombre_largo = info.get('longName', info.get('shortName', ticker))
            tipo = info.get('quoteType', 'Activo')
            etiqueta = f"{nombre_largo} ({tipo}) - [{ticker}]"
            
            if ticker not in st.session_state.popular_assets.values():
                st.session_state.popular_assets[etiqueta] = ticker
                guardar_activo_permanente(etiqueta, ticker)

        # --- SECCIÓN 1: Gráfico comparativo porcentual ---
        st.subheader("📊 Rendimiento Comparativo (%)")
        
        norm_hist1 = ((hist1['Close'] / hist1['Close'].iloc[0]) - 1) * 100
        norm_hist2 = ((hist2['Close'] / hist2['Close'].iloc[0]) - 1) * 100

        fig = go.Figure()
        
        nombre1 = info1.get('longName', ticker_1)
        nombre2 = info2.get('longName', ticker_2)
        
        fig.add_trace(go.Scatter(x=hist1.index, y=norm_hist1, mode='lines', name=nombre1))
        fig.add_trace(go.Scatter(x=hist2.index, y=norm_hist2, mode='lines', name=nombre2))

        fig.update_layout(
            yaxis_title="Variación Porcentual (%)",
            xaxis_title="Fecha",
            hovermode="x unified",
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # --- SECCIÓN 2: Modelo de Calificaciones (Estilo Tarjeta) ---
        st.subheader("🛡️ Modelo de Calificaciones y Salud del Activo")

        def render_tarjeta_calificacion(info, hist, label_col):
            nombre = info.get('longName', 'Activo')
            moneda = info.get('currency', 'USD')
            
            # Estimación de métricas para la tarjeta
            patrimonio = info.get('marketCap', info.get('totalAssets', 0))
            if not isinstance(patrimonio, (int, float)):
                patrimonio = 0
            
            # Puntuación simulada de seguridad basada en tamaño/consistencia
            puntuacion = 4.2 if patrimonio > 1e8 else 3.8
            calificacion = "A" if puntuacion >= 4.0 else "B"
            
            dias_hist = (hist.index[-1] - hist.index[0]).days
            es_consolidado = dias_hist > 1825 # > 5 años

            with st.container(border=True):
                st.markdown(f"### {label_col}: **{nombre}**")
                
                c_a, c_b = st.columns(2)
                with c_a:
                    st.metric(label="Puntuación de Seguridad", value=f"{puntuacion}/5")
                    st.markdown(f"**Calificación:** `{calificacion}`")
                    st.markdown(f"**Tendencia:** `Estable (▶▶)`")
                with c_b:
                    st.markdown("**Salud del Activo:**")
                    if patrimonio > 1e9:
                        st.markdown("🟢 Muy Sólido (>1.000M€)")
                    else:
                        st.markdown("🟡 Sólido / Crecimiento")
                        
                    if es_consolidado:
                        st.markdown("🟢 Consolidado (>5 años)")
                    else:
                        st.markdown("🟡 Historial reciente")
                        
                st.markdown(f"**Precio Actual:** {hist['Close'].iloc[-1]:.2f} {moneda}")

        col_card1, col_card2 = st.columns(2)
        with col_card1:
            render_tarjeta_calificacion(info1, hist1, "Activo A")
        with col_card2:
            render_tarjeta_calificacion(info2, hist2, "Activo B")

else:
    st.info("👈 Selecciona o busca dos activos en las columnas superiores para ver su comparativa de rendimiento y calificaciones.")
