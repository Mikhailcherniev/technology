import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Page configuration with better theme and favicon
st.set_page_config(
    page_title='Dashboard ESG - Análise Avançada',
    page_icon='🌍',
    layout='wide',
    initial_sidebar_state='expanded'
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { border-radius: 0.5rem; padding: 1rem; }
    .stMetric label { font-size: 1rem !important; font-weight: 600 !important; }
    .stMetric div { font-size: 1.5rem !important; }
    .css-1aumxhk { background-color: #ffffff; border-radius: 0.5rem; padding: 1rem; }
    .stPlotlyChart { border-radius: 0.5rem; }
    .stDataFrame { border-radius: 0.5rem; }
    </style>
    """, unsafe_allow_html=True)

# Cache data with improved error handling
@st.cache_data(ttl=3600)
def load_data():
    try:
        df = pd.read_excel('dataset_esg_sem_2015.xlsx')
        # Data cleaning and preprocessing
        df['Ano'] = df['Ano'].astype(int)
        df['Receita'] = pd.to_numeric(df['Receita'], errors='coerce')
        df['MargemLucro'] = pd.to_numeric(df['MargemLucro'], errors='coerce')
        df['Emissao_Carbono'] = pd.to_numeric(df['Emissao_Carbono'], errors='coerce')
        return df.dropna(subset=['ESG_Geral', 'Receita'])
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return pd.DataFrame()

df = load_data()

# Reset control with improved state management
if 'reset' not in st.session_state:
    st.session_state.reset = {
        'year_range': (df['Ano'].min(), df['Ano'].max()),
        'regions': sorted(df['Regiao'].unique()),
        'revenue_range': (float(df['Receita'].min()), float(df['Receita'].max())),
        'margin_range': (float(df['MargemLucro'].min()), float(df['MargemLucro'].max()))
    }


# Sidebar with improved layout
with st.sidebar:
    st.title('🌍 Filtros de Análise')
    
    # Reset button with confirmation
    if st.button('🔄 Resetar Todos os Filtros', use_container_width=True):
        for key in st.session_state.reset:
            st.session_state[key] = st.session_state.reset[key]
        st.rerun()
    
    # Year range slider with marks
    year_range = st.slider(
        'Selecione o intervalo de anos:',
        min_value=df['Ano'].min(),
        max_value=df['Ano'].max(),
        value=st.session_state.get('year_range', st.session_state.reset['year_range']),
        step=1,
        key='year_range'
    )
    
    # Region selector with search
    regions = st.multiselect(
        'Selecione as regiões:',
        options=sorted(df['Regiao'].unique()),
        default=st.session_state.get('regions', st.session_state.reset['regions']),
        key='regions'
    )
    
    # Revenue range with logarithmic option
    revenue_range = st.slider(
        'Faixa de Receita (em milhões):',
        min_value=float(df['Receita'].min()),
        max_value=float(df['Receita'].max()),
        value=st.session_state.get('revenue_range', st.session_state.reset['revenue_range']),
        key='revenue_range'
    )
    
    # Margin range with better formatting
    margin_range = st.slider(
        'Faixa de Margem de Lucro (%):',
        min_value=float(df['MargemLucro'].min()),
        max_value=float(df['MargemLucro'].max()),
        value=st.session_state.get('margin_range', st.session_state.reset['margin_range']),
        format='%.1f%%',
        key='margin_range'
    )

# Apply filters with error handling
try:
    df_filtered = df[
        (df['Ano'] >= year_range[0]) & 
        (df['Ano'] <= year_range[1]) &
        (df['Regiao'].isin(regions)) &
        (df['Receita'] >= revenue_range[0]) &
        (df['Receita'] <= revenue_range[1]) &
        (df['MargemLucro'] >= margin_range[0]) &
        (df['MargemLucro'] <= margin_range[1])
    ].copy()
    
    # Add calculated metrics
    df_filtered['Emissao_por_Receita'] = df_filtered['Emissao_Carbono'] / df_filtered['Receita']
except Exception as e:
    st.error(f"Erro ao filtrar dados: {str(e)}")
    df_filtered = pd.DataFrame()

# Main layout with improved structure
st.title('📊 Dashboard ESG - Análise Avançada')
st.markdown("""
    <div style=' padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;'>
    <p style='margin: 0;'>Explore as métricas ESG, financeiras e ambientais das empresas filtradas.</p>
    </div>
    """, unsafe_allow_html=True)

# Enhanced KPIs with delta indicators
col1, col2, col3, col4 = st.columns(4)
with col1:
    delta = len(df_filtered) - len(df) if len(df_filtered) != len(df) else None
    st.metric(
        label="📈 Empresas Analisadas", 
        value=f"{len(df_filtered):,}",
        delta=f"{delta:,}" if delta else None
    )

with col2:
    avg_esg = df_filtered['ESG_Geral'].mean()
    delta_esg = avg_esg - df['ESG_Geral'].mean() if not df_filtered.empty else None
    st.metric(
        label="🌱 Média ESG Geral", 
        value=f"{avg_esg:.1f}",
        delta=f"{delta_esg:.1f}" if delta_esg else None
    )

with col3:
    avg_revenue = df_filtered['Receita'].mean()
    delta_revenue = avg_revenue - df['Receita'].mean() if not df_filtered.empty else None
    st.metric(
        label="💸 Receita Média", 
        value=f"${avg_revenue:,.2f}M",
        delta=f"${delta_revenue:,.2f}M" if delta_revenue else None
    )

with col4:
    total_emissions = df_filtered['Emissao_Carbono'].sum()
    delta_emissions = total_emissions - df['Emissao_Carbono'].sum() if not df_filtered.empty else None
    st.metric(
        label="🏭 Emissões Totais", 
        value=f"{total_emissions:,.0f} tCO2",
        delta=f"{delta_emissions:,.0f} tCO2" if delta_emissions else None
    )

# Improved visualization functions
def plot_top_companies():
    st.subheader('🔝 Empresas com Melhor e Pior Desempenho')
    
    tab1, tab2, tab3 = st.tabs(["🏆 Melhores em ESG", "⚠️ Maiores Emissoras", "💰 Maiores Receitas"])
    
    with tab1:
        top_esg = df_filtered.nlargest(5, 'ESG_Geral')
        fig = px.bar(
            top_esg,
            x='Nome_Compania',
            y='ESG_Geral',
            color='Regiao',
            title='Empresas com Melhor ESG',
            labels={'ESG_Geral': 'Score ESG', 'Nome_Compania': 'Empresa'},
            text='ESG_Geral'
        )
        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        top_emitters = df_filtered.nlargest(5, 'Emissao_Carbono')
        fig = px.bar(
            top_emitters,
            x='Nome_Compania',
            y='Emissao_Carbono',
            color='Regiao',
            title='Empresas com Maiores Emissões',
            labels={'Emissao_Carbono': 'Emissões (tCO2)', 'Nome_Compania': 'Empresa'},
            text='Emissao_Carbono'
        )
        fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        top_revenue = df_filtered.nlargest(5, 'Receita')
        fig = px.bar(
            top_revenue,
            x='Nome_Compania',
            y='Receita',
            color='Regiao',
            title='Empresas com Maiores Receitas',
            labels={'Receita': 'Receita (US$ milhões)', 'Nome_Compania': 'Empresa'},
            text='Receita'
        )
        fig.update_traces(texttemplate='US$ %{text:,.0f}M', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

def plot_trend_analysis():
    st.subheader('📈 Análise Temporal de Indicadores')
    
    # Aggregate data by year and region
    df_trend = df_filtered.groupby(['Ano', 'Regiao']).agg({
        'ESG_Geral': 'mean',
        'Receita': 'mean',
        'Emissao_Carbono': 'sum',
        'Emissao_por_Receita': 'mean'
    }).reset_index()
    
    tab1, tab2 = st.tabs(["📊 ESG e Receita", "🌍 Emissões"])
    
    with tab1:
        fig = px.line(
            df_trend,
            x='Ano',
            y=['ESG_Geral', 'Receita'],
            color='Regiao',
            facet_col='variable',
            facet_col_spacing=0.1,
            labels={'value': 'Valor', 'variable': 'Métrica'},
            title='Evolução do ESG e Receita por Região'
        )
        fig.update_yaxes(matches=None)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        fig = px.area(
            df_trend,
            x='Ano',
            y='Emissao_Carbono',
            color='Regiao',
            title='Emissões de Carbono ao Longo do Tempo',
            labels={'Emissao_Carbono': 'Emissões (tCO2)'}
        )
        st.plotly_chart(fig, use_container_width=True)

def plot_correlation_analysis():
    st.subheader('🔗 Correlações entre Indicadores')

# Main tabs with improved content
tab1, tab2 = st.tabs(["📊 Visão Geral", "🌱 Análise ESG"])

with tab1:
    if not df_filtered.empty:
        plot_top_companies()
        plot_trend_analysis()
    else:
        st.warning("Nenhum dado encontrado com os filtros atuais.")

with tab2:
    if not df_filtered.empty:
        plot_correlation_analysis()
        
        # Radar chart for ESG components
        st.subheader('📡 Componentes do ESG por Região')
        esg_components = ['ESG_Ambiental', 'ESG_Social', 'ESG_Governanca']
        
        for region in df_filtered['Regiao'].unique():
            region_data = df_filtered[df_filtered['Regiao'] == region][esg_components].mean()
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=region_data.tolist() + [region_data.iloc[0]],
                theta=esg_components + [esg_components[0]],
                fill='toself',
                name=region
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True)),
                title=f'Desempenho ESG - {region}'
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhum dado encontrado com os filtros atuais.")