import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Configuración de página
st.set_page_config(page_title="Comparador de Activos Financieros", layout="wide")

st.title("📈 Comparador de Activos Financieros")
st.markdown("Compara el rendimiento y métricas clave de acciones, ETFs, fondos indexados y fondos monetarios utilizando Yahoo Finance.")

# Diccionario con activos frecuentes organizados por categoría para facilitar la selección inicial
POPULAR_ASSETS = {
    "--- Selección rápida o escribe abajo ---": "",
    "Apple Inc. (Acción)": "AAPL",
    "Microsoft Corp. (Acción)": "MSFT",
    "NVIDIA Corp. (Acción)": "NVDA",
    "iShares Core S&P 500 UCITS ETF (ETF)": "CSPX.L",
    "Vanguard FTSE All-World UCITS ETF (ETF)": "VWCE.DE",
    "iShares Core MSCI World UCITS ETF (ETF)": "IWDA.AS",
    "Vanguard S&P 500 Index Fund (Fondo Indexado)": "VFINX",
    "Fidelity US Dollar Cash Fund (Fondo Monetario)": "FUCAP.L"
}

# Selección de período temporal
st.sidebar.header("⚙️ Configuración del Análisis")
periodo = st.sidebar.selectbox(
    "Período de tiempo:",
    options=["1M", "3M", "6M", "YTD", "1Y", "3Y", "5Y", "MAX"],
    index=4
)

# Función para obtener datos de un activo
@st.cache_data(ttl=3600)
def cargar_datos_activo(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        hist = ticker.history(period=periodo)
        
        # Validar si Yahoo devolvió datos
        if hist.empty:
            return None, None
            
        return info, hist
    except Exception:
        return None, None

# Interfaz principal: 2 Columnas
col1, col2 = st.columns(2)

def selector_activo(col_name, default_preset):
    st.subheader(col_name)
    
    # 1. Lista desplegable con sugerencias
    preset = st.selectbox(
        "Seleccionar de lista predefinida:",
        options=list(POPULAR_ASSETS.keys()),
        key=f"preset_{col_name}"
    )
    
    # 2. Búsqueda directa por Ticker o ISIN
    ticker_input = st.text_input(
        "O introduce directamente Ticker / ISIN (Yahoo Finance):",
        value=POPULAR_ASSETS[preset] if preset != "--- Selección rápida o escribe abajo ---" else default_preset,
        key=f"input_{col_name}"
    ).strip().upper()
    
    return ticker_input

# Configurar selectores en las dos columnas
with col1:
    ticker_1 = selector_activo("Activo A", "AAPL")

with col2:
    ticker_2 = selector_activo("Activo B", "MSFT")

# Botón para ejecutar la comparación
st.divider()

if ticker_1 and ticker_2:
    info1, hist1 = cargar_datos_activo(ticker_1)
    info2, hist2 = cargar_datos_activo(ticker_2)

    if hist1 is None or hist2 is None:
        st.error("⚠️ No se pudieron obtener datos para alguno de los tickers introducidos. Por favor, verifica el símbolo en Yahoo Finance.")
    else:
        # --- SECCIÓN 1: Gráfico comparativo porcentual ---
        st.subheader("📊 Rendimiento Comparativo (%)")
        
        # Normalizar precios base 100 / Cambio Porcentual acumulado
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

        # --- SECCIÓN 2: Tabla de Métricas Clave ---
        st.subheader("📋 Métricas y Datos Fundamentales")

        def obtener_metricas(info, hist):
            precio_actual = hist['Close'].iloc[-1]
            precio_inicio = hist['Close'].iloc[0]
            rendimiento = ((precio_actual - precio_inicio) / precio_inicio) * 100
            
            moneda = info.get('currency', 'USD')
            return {
                "Nombre": info.get('longName', info.get('shortName', 'N/D')),
                "Categoría / Tipo": info.get('quoteType', 'N/D'),
                "Precio Actual": f"{precio_actual:.2f} {moneda}",
                "Rendimiento Periodo": f"{rendimiento:+.2f}%",
                "Máximo 52 Semanas": f"{info.get('fiftyTwoWeekHigh', 'N/D')} {moneda}",
                "Mínimo 52 Semanas": f"{info.get('fiftyTwoWeekLow', 'N/D')} {moneda}",
                "Divisa": moneda,
                "Ratio PER (P/E)": info.get('trailingPE', 'N/D'),
                "Capitalización / Patrimonio": f"{info.get('marketCap', info.get('totalAssets', 'N/D')):,}" if isinstance(info.get('marketCap') or info.get('totalAssets'), (int, float)) else "N/D"
            }

        datos_m1 = obtener_metricas(info1, hist1)
        datos_m2 = obtener_metricas(info2, hist2)

        df_comparativo = pd.DataFrame([datos_m1, datos_m2], index=[f"Activo A ({ticker_1})", f"Activo B ({ticker_2})"]).T
        st.dataframe(df_comparativo, use_container_width=True)

else:
    st.info("Introduce o selecciona un ticker en cada columna para generar la comparación.")
