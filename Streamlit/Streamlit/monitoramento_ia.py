import streamlit as st
import pandas as pd
import random
import datetime
from openai import OpenAI

# CONFIGURAÇÃO DA PÁGINA

st.set_page_config(
    page_title="Monitoramento de IA", 
    layout="wide",
    page_icon="🤖"
)

# SIDEBAR - CONTROLES E INFORMAÇÕES
with st.sidebar:
    st.title("Configurações")
    openai_api_key = st.text_input(
        "🔑 Chave da API OpenAI:", 
        type="password",
        help="Obtenha em platform.openai.com"
    )
    
    # Status da API
    api_status = st.empty()
    
    st.markdown("---")
    st.caption("ℹ️ Tokens são calculados automaticamente")
    st.caption("💡 Modelo padrão: gpt-3.5-turbo")

# DASHBOARD DE MONITORAMENTO

st.title("📊 Monitoramento de Modelos de IA")

@st.cache_data
def gerar_dados_modelo():
    """Gera dados simulados de performance de modelo"""
    data = []
    for i in range(10):
        data.append({
            "Data": (datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%d/%m/%Y"),
            "Modelo": f"Modelo {random.choice(['A', 'B'])}",
            "Acurácia": round(random.uniform(0.85, 0.99), 2),
            "Latência (ms)": round(random.uniform(80, 200), 1),
            "Chamadas": random.randint(100, 1000),
        })
    return pd.DataFrame(data[::-1])

# Gerar e mostrar dados
df = gerar_dados_modelo()

# Métricas rápidas
col1, col2, col3 = st.columns(3)
col1.metric("Acurácia Média", f"{df['Acurácia'].mean():.2%}")
col2.metric("Latência Média", f"{df['Latência (ms)'].mean():.1f} ms")
col3.metric("Total Chamadas", df['Chamadas'].sum())

# Tabela e gráficos
tab1, tab2 = st.tabs(["📊 Dados Detalhados", "📈 Visualizações"])
with tab1:
    st.dataframe(df, use_container_width=True)
with tab2:
    st.line_chart(df, x="Data", y=["Acurácia", "Latência (ms)"], color=["#4CAF50", "#FF5722"])


st.markdown("---")
st.header("🤖 Assistente de IA")

# Inicialização do historico
if "historico" not in st.session_state:
    st.session_state.historico = []

# Mostrar historico existente
for msg in st.session_state.historico:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Interação do usuário
if prompt := st.chat_input("Como posso ajudar com seu modelo de IA?"):
    # Atualiza status da API
    with st.sidebar:
        if openai_api_key:
            api_status.success("✅ API Conectada", icon="🔌")
    
    # Adiciona pergunta ao histórico
    st.session_state.historico.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    
    with st.chat_message("assistant"):
        with st.spinner("Analisando sua consulta..."):
            try:
                # Configura cliente openAI
                client = OpenAI(api_key=openai_api_key)
                
                # API
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo", # pode mudar pro modelo que quiser.
                    messages=[
                        {
                            "role": "system", 
                            "content": """
                            Você é um especialista em machine learning. Responda de forma:
                            - Técnica mas acessível
                            - Com exemplos práticos quando relevante
                            - Máximo 300 tokens
                            """
                        },
                        *[{"role": m["role"], "content": m["content"]} for m in st.session_state.historico]
                    ],
                    temperature=0.7,
                    max_tokens=300
                )
                
                resposta = response.choices[0].message.content
                st.markdown(resposta)
                st.session_state.historico.append({"role": "assistant", "content": resposta})
                
                # Mostra estatísticas de uso
                tokens = response.usage.total_tokens
                with st.sidebar:
                    st.info(f"🔢 Tokens usados: {tokens} (≈ ${tokens*0.000002:.4f})")
            
            except Exception as e:
                erro = f"""
                ⚠️ **Erro na API**  
                {str(e)}  
                ∙ Verifique sua [chave e quota](https://platform.openai.com/usage)  
                ∙ Modelo alternativo: `gpt-3.5-turbo`
                """
                st.error(erro)
                st.session_state.historico.append({"role": "assistant", "content": erro})
    
    # Limita histórico (3 últimas conversas)
    # VVocê pode limitar o número de mensagens enviadas à API (isso afeta custo e performance).
    if len(st.session_state.historico) > 6:
        st.session_state.historico = st.session_state.historico[-6:]


# RODAPÉ
st.markdown("---")
st.caption("📌 Monitoramento em tempo real - Atualizado em " + 
          datetime.datetime.now().strftime("%d/%m/%Y %H:%M"))