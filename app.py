import streamlit as st
import pandas as pd
import numpy as np
import os
import base64
from datetime import datetime
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Copiloto Uber Estratégico",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

def carregar_imagem_fundo():
    imagem_encontrada = None
    for f in os.listdir("."):
        if any(ext in f.lower() for ext in [".jpg", ".jpeg", ".png"]):
            imagem_encontrada = f
            break
            
    if imagem_encontrada:
        with open(imagem_encontrada, "rb") as image_file:
            bytes_data = image_file.read()
            encoded_string = base64.b64encode(bytes_data).decode()
            
        return f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(10, 10, 12, 0.40), rgba(10, 10, 12, 0.65)), url("data:image/png;base64,{encoded_string}");
            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;
        }}
        div[data-testid="stForm"], div[data-testid="stMetricValue"], .stTabs {{
            background: rgba(18, 24, 38, 0.85) !important;
            backdrop-filter: blur(12px);
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            padding: 15px;
        }}
        h1, h2, h3, p, label, .stMarkdown {{
            color: #FFFFFF !important;
        }}
        .stButton>button {{
            background-color: #00D1B2 !important;
            color: #000000 !important;
            font-weight: bold;
            border-radius: 10px;
            width: 100%;
        }}
        </style>
        """
    return ""

css = carregar_imagem_fundo()
if css:
    st.markdown(css, unsafe_allow_html=True)

# Função para fazer o celular/navegador falar qualquer texto
def falar_texto_no_navegador(texto):
    js_code = f"""
    <script>
        var msg = new SpeechSynthesisUtterance("{texto}");
        msg.lang = "pt-BR";
        msg.rate = 1.0;
        window.speechSynthesis.speak(msg);
    </script>
    """
    components.html(js_code, height=0)

ARQUIVO_DADOS = "dados_uber.csv"

def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        df = pd.read_csv(ARQUIVO_DADOS)
        df['Data'] = pd.to_datetime(df['Data'])
        return df
    else:
        return pd.DataFrame(columns=[
            "Data", "Dia_Semana", "Turno_Horario", "Categoria", 
            "Regiao", "Horas_Rodadas", "KM_Rodados", "Faturamento_Bruto", 
            "Preco_Combustivel", "Consumo_KML", "Custo_Combustivel", "Lucro_Liquido", "Lucro_Por_Hora"
        ])

def salvar_dados(df):
    df.to_csv(ARQUIVO_DADOS, index=False)

df_uber = carregar_dados()

col_painel, col_espaco = st.columns([5, 7])

with col_painel:
    st.title("🚗 Copiloto Uber")
    st.caption("Painel Estratégico de Lucro")

    aba1, aba2, aba3 = st.tabs(["📝 Lançar", "🧠 Agente", "📈 Histórico"])

    with aba1:
        st.subheader("Lançamento do Dia")
        with st.form("form_turno", clear_on_submit=False):
            col1, col2 = st.columns(2)
            with col1:
                data = st.date_input("Data do Turno", datetime.now())
                categoria = st.selectbox("Categoria", ["Uber Black", "Uber Comfort", "Uber X", "Misto"])
                turno = st.selectbox("Horário", [
                    "05:00 - 09:00 (Pico Manhã)", "09:00 - 12:00 (Manhã)", 
                    "12:00 - 16:00 (Tarde)", "16:00 - 20:00 (Pico Tarde/Noite)", 
                    "20:00 - 00:00 (Noite)", "00:00 - 05:00 (Madrugada)"
                ])
                regiao = st.selectbox("Região", [
                    "Centro / Cidade Baixa", "Zona Norte / Aeroporto", "Zona Sul", 
                    "Moinhos / Bela Vista", "Canoas / Região Metr.", "Outras Regiões"
                ])

            with col2:
                faturamento = st.number_input("Faturamento (R$)", min_value=0.0, step=10.0, format="%.2f")
                horas = st.number_input("Horas Rodadas", min_value=0.5, max_value=24.0, step=0.5, value=4.0)
                km = st.number_input("KM Rodados", min_value=1.0, step=5.0, value=80.0)
                
            st.markdown("---")
            st.caption("⛽ Configuração do Carro")
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                preco_combustivel = st.number_input("Combustível (R$/L)", min_value=1.0, value=5.89, step=0.05)
            with col_c2:
                consumo_kml = st.number_input("Autonomia (KM/L)", min_value=1.0, value=10.0, step=0.5)

            btn_salvar = st.form_submit_button("💾 Salvar Turno")
            
            if btn_salvar:
                if faturamento > 0:
                    dias_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
                    dia_nome = dias_semana[data.weekday()]
                    
                    custo_gasolina = (km / consumo_kml) * preco_combustivel
                    lucro_liq = faturamento - custo_gasolina
                    lucro_hora = lucro_liq / horas if horas > 0 else 0
                    
                    novo_registro = pd.DataFrame([{
                        "Data": data, "Dia_Semana": dia_nome, "Turno_Horario": turno,
                        "Categoria": categoria, "Regiao": regiao, "Horas_Rodadas": horas,
                        "KM_Rodados": km, "Faturamento_Bruto": faturamento,
                        "Preco_Combustivel": preco_combustivel, "Consumo_KML": consumo_kml,
                        "Custo_Combustivel": custo_gasolina, "Lucro_Liquido": lucro_liq,
                        "Lucro_Por_Hora": lucro_hora
                    }])
                    
                    df_uber = pd.concat([df_uber, novo_registro], ignore_index=True)
                    salvar_dados(df_uber)
                    
                    st.success(f"Salvo! Lucro: R$ {lucro_liq:.2f} (R$ {lucro_hora:.2f}/h)")
                else:
                    st.error("Informe um faturamento válido.")

    with aba2:
        st.subheader("💡 Diagnóstico do Agente")
        if len(df_uber) == 0:
            st.info("Registre turnos para gerar estratégias com áudio.")
        else:
            total_faturado = df_uber["Faturamento_Bruto"].sum()
            total_lucro = df_uber["Lucro_Liquido"].sum()
            media_hora = df_uber["Lucro_Por_Hora"].mean()
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Faturado", f"R$ {total_faturado:.2f}")
            c2.metric("Lucro", f"R$ {total_lucro:.2f}")
            c3.metric("R$/Hora", f"R$ {media_hora:.2f}")

            st.markdown("---")
            if st.button("🔊 Ouvir Resumo em Áudio"):
                mensagem_voz = f"Diagnostico do copiloto: Voce faturou um total de {total_faturado:.0f} reais, resultando em um lucro liquido de {total_lucro:.0f} reais, com uma media de {media_hora:.0f} reais por hora rodada."
                falar_texto_no_navegador(mensagem_voz)

    with aba3:
        st.subheader("📊 Histórico")
        if len(df_uber) > 0:
            st.dataframe(df_uber[["Data", "Turno_Horario", "Lucro_Liquido", "Lucro_Por_Hora"]].sort_values(by="Data", ascending=False), use_container_width=True)
            st.line_chart(df_uber[["Data", "Faturamento_Bruto", "Lucro_Liquido"]].set_index("Data"))
