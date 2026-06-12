import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from io import BytesIO
import json
import os
import shutil
import uuid

# ═══════════════════════════════════════════════════════════════════
# CAMINHOS DO DATABASE
# ═══════════════════════════════════════════════════════════════════
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "database")
ANEXOS_DIR = os.path.join(DB_DIR, "anexos")
DESPESAS_FILE = os.path.join(DB_DIR, "despesas.json")
ANEXOS_META_FILE = os.path.join(DB_DIR, "anexos_meta.json")

# Garantir que as pastas existem
os.makedirs(ANEXOS_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════════════════════
# FUNÇÕES DE PERSISTÊNCIA (JSON + Filesystem)
# ═══════════════════════════════════════════════════════════════════
DADOS_INICIAIS = [
    {"id": "d001", "Empreendimento": "Reserva Alta Vista", "Fornecedor": "Gráfica Nacional Ltda", "Descrição": "Pastas, folders e flyers (Zera Lotes)", "Valor": 7460.00, "Status": "Pendente", "Categoria": "Marketing", "Data": "2025-01-15"},
    {"id": "d002", "Empreendimento": "Reserva Alta Vista", "Fornecedor": "Ápice Eventos Ltda", "Descrição": "Locação de tenda 03x09", "Valor": 4000.00, "Pix": "57.172.337/0001-01", "DadosBancarios": "Banco Cooperativo do Brasil | Ag: 3137 | CC: 486540", "Status": "Pendente", "Categoria": "Eventos", "Data": "2025-01-18"},
    {"id": "d003", "Empreendimento": "Reserva Alta Vista", "Fornecedor": "Rovênia Oliveira", "Descrição": "Decoração da tenda e mobiliário", "Valor": 6600.00, "Pix": "31.110.860/0001-01", "DadosBancarios": "Credileste | Ag: 4346 | CC: 9.386-6", "Status": "Pendente", "Categoria": "Eventos", "Data": "2025-01-20"},
    {"id": "d004", "Empreendimento": "Reserva Alta Vista", "Fornecedor": "Márcio", "Descrição": "Aluguel de pergolado", "Valor": 2000.00, "Pix": "", "DadosBancarios": "Necessário solicitar chave PIX", "Status": "Pendente", "Categoria": "Eventos", "Data": "2025-01-22"},
    {"id": "d005", "Empreendimento": "Reserva Alta Vista", "Fornecedor": "Distribuidora Água Cristalina", "Descrição": "Fornecimento de água", "Valor": 3332.92, "Pix": "(33) 99953-4544", "DadosBancarios": "Banco 756 | Ag: 4346 | CC: 1891-0", "Status": "Pendente", "Categoria": "Suprimentos", "Data": "2025-02-01"},
    {"id": "d006", "Empreendimento": "Reserva Alta Vista", "Fornecedor": "Artpanific Ltda", "Descrição": "Fornecimento de lanches", "Valor": 1996.62, "Pix": "54.390.926/0001-60", "DadosBancarios": "Sicoob Credileste (756) | Ag: 4356 | CC: 31.403-0", "Status": "Pendente", "Categoria": "Alimentação", "Data": "2025-02-05"},
    {"id": "d007", "Empreendimento": "Reserva Alta Vista", "Fornecedor": "Ângela Todeschini", "Descrição": "Pedras Brancas 15kg", "Valor": 250.00, "Status": "Pendente", "Categoria": "Materiais", "Data": "2025-02-10"},
    {"id": "d008", "Empreendimento": "Reserva Alta Vista", "Fornecedor": "Ângela Todeschini", "Descrição": "Cesto Fechado com Tampa 30L", "Valor": 70.00, "Status": "Pendente", "Categoria": "Materiais", "Data": "2025-02-10"},
    {"id": "d009", "Empreendimento": "Manancial", "Fornecedor": "Emília Festas", "Descrição": "Locação de mesas e cadeiras", "Valor": 80.00, "Status": "Pendente", "Categoria": "Eventos", "Data": "2025-02-15"},
    {"id": "d010", "Empreendimento": "Manancial", "Fornecedor": "Marcelo Marques", "Descrição": "Corrente, cadeado e caixa de isopor", "Valor": 327.00, "Status": "Pendente", "Categoria": "Materiais", "Data": "2025-02-18"},
]

def carregar_despesas():
    """Carrega despesas do arquivo JSON. Cria com dados iniciais se não existe."""
    if os.path.exists(DESPESAS_FILE):
        with open(DESPESAS_FILE, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        return dados
    else:
        salvar_despesas(DADOS_INICIAIS)
        return DADOS_INICIAIS.copy()

def salvar_despesas(lista):
    """Salva lista de despesas no arquivo JSON."""
    with open(DESPESAS_FILE, 'w', encoding='utf-8') as f:
        json.dump(lista, f, ensure_ascii=False, indent=2)

def carregar_meta_anexos():
    """Carrega metadados dos anexos do JSON."""
    if os.path.exists(ANEXOS_META_FILE):
        with open(ANEXOS_META_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def salvar_meta_anexos(meta):
    """Salva metadados dos anexos no JSON."""
    with open(ANEXOS_META_FILE, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

def salvar_arquivo_anexo(despesa_id, uploaded_file):
    """Salva arquivo no disco e retorna metadados."""
    pasta_despesa = os.path.join(ANEXOS_DIR, despesa_id)
    os.makedirs(pasta_despesa, exist_ok=True)
    
    file_id = str(uuid.uuid4())[:8]
    nome_seguro = f"{file_id}_{uploaded_file.name}"
    caminho = os.path.join(pasta_despesa, nome_seguro)
    
    with open(caminho, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    
    return {
        "file_id": file_id,
        "nome_original": uploaded_file.name,
        "nome_salvo": nome_seguro,
        "tipo": uploaded_file.type,
        "tamanho": uploaded_file.size,
        "data_upload": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "caminho": caminho
    }

def ler_arquivo_anexo(caminho):
    """Lê arquivo do disco e retorna bytes."""
    if os.path.exists(caminho):
        with open(caminho, 'rb') as f:
            return f.read()
    return None

def excluir_arquivo_anexo(caminho):
    """Remove arquivo do disco."""
    if os.path.exists(caminho):
        os.remove(caminho)

def excluir_despesa(despesa_id):
    """Exclui despesa e todos os anexos associados."""
    despesas = carregar_despesas()
    despesas = [d for d in despesas if d["id"] != despesa_id]
    salvar_despesas(despesas)
    
    # Excluir pasta de anexos
    pasta = os.path.join(ANEXOS_DIR, despesa_id)
    if os.path.exists(pasta):
        shutil.rmtree(pasta)
    
    # Limpar metadados
    meta = carregar_meta_anexos()
    if despesa_id in meta:
        del meta[despesa_id]
        salvar_meta_anexos(meta)

# ═══════════════════════════════════════════════════════════════════
# 1. CONFIGURAÇÃO DA PÁGINA
# ═══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Vale Construtora - Controle Financeiro",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════
# 2. CSS PREMIUM + SIDEBAR
# ═══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    *, *::before, *::after { box-sizing: border-box; }
    .main {
        background: linear-gradient(135deg, #0a1628 0%, #0f2035 40%, #132d4a 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        padding-top: 0 !important;
    }
    .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; max-width: 1400px !important; }
    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none; }
    h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown { font-family: 'Inter', sans-serif !important; }
    h1 { color: #ffffff !important; font-weight: 800 !important; }
    h2, h3 { color: #e2e8f0 !important; font-weight: 600 !important; }
    p, span, label { color: #cbd5e1 !important; }

    /* ── SIDEBAR ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0B2545 0%, #0a1e3d 50%, #081630 100%) !important;
        border-right: 1px solid rgba(238,185,2,0.1);
    }
    [data-testid="stSidebar"] .block-container { padding-top: 0 !important; }
    [data-testid="stSidebar"] [data-testid="stMarkdown"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdown"] span,
    [data-testid="stSidebar"] label {
        color: #94a3b8 !important;
    }

    /* Sidebar radio buttons as menu items */
    [data-testid="stSidebar"] .stRadio > div {
        gap: 2px !important;
    }
    [data-testid="stSidebar"] .stRadio > div > label {
        background: rgba(255,255,255,0.02) !important;
        border: 1px solid rgba(255,255,255,0.04) !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
        margin: 2px 0 !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        color: #94a3b8 !important;
        font-size: 14px !important;
        font-weight: 500 !important;
    }
    [data-testid="stSidebar"] .stRadio > div > label:hover {
        background: rgba(19,64,116,0.3) !important;
        border-color: rgba(19,64,116,0.4) !important;
        color: #e2e8f0 !important;
    }
    [data-testid="stSidebar"] .stRadio > div > label[data-checked="true"],
    [data-testid="stSidebar"] .stRadio > div > label:has(input:checked) {
        background: linear-gradient(135deg, #134074, #1a5298) !important;
        border-color: rgba(26,82,152,0.5) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(19,64,116,0.4) !important;
    }
    [data-testid="stSidebar"] .stRadio > div > label > div:first-child {
        display: none !important;  /* Hide radio circle */
    }
    [data-testid="stSidebar"] .stRadio > label {
        display: none !important;  /* Hide radio group label */
    }

    /* ── HEADER ── */
    .header-container {
        background: linear-gradient(135deg, #0B2545 0%, #134074 50%, #1a5298 100%);
        border-radius: 16px; padding: 20px 28px; margin-bottom: 20px;
        display: flex; align-items: center; justify-content: space-between;
        box-shadow: 0 8px 32px rgba(0,0,0,0.4); border: 1px solid rgba(238,185,2,0.15);
        position: relative; overflow: hidden;
    }
    .header-container::before {
        content:''; position:absolute; top:-50%; right:-20%; width:400px; height:400px;
        background: radial-gradient(circle, rgba(238,185,2,0.08) 0%, transparent 70%); border-radius:50%;
    }
    .header-left { display:flex; align-items:center; gap:16px; z-index:1; }
    .header-title { font-size:22px; font-weight:800; color:#ffffff; letter-spacing:-0.5px; }
    .header-subtitle { font-size:11px; color:rgba(255,255,255,0.5); letter-spacing:2px; text-transform:uppercase; margin-top:2px; }
    .header-right { display:flex; align-items:center; gap:10px; z-index:1; }
    .header-badge {
        background:rgba(238,185,2,0.15); border:1px solid rgba(238,185,2,0.3);
        border-radius:20px; padding:6px 14px; font-size:11px; color:#EEB902; font-weight:600;
    }
    .db-badge {
        background:rgba(5,150,105,0.15); border:1px solid rgba(5,150,105,0.3);
        border-radius:20px; padding:6px 14px; font-size:11px; color:#6ee7b7; font-weight:600;
    }

    .kpi-card {
        border-radius:16px; padding:22px 24px; position:relative; overflow:hidden;
        transition: all 0.3s cubic-bezier(0.4,0,0.2,1); min-height:130px;
    }
    .kpi-card:hover { transform:translateY(-3px); box-shadow:0 16px 36px rgba(0,0,0,0.3); }
    .kpi-card::after {
        content:''; position:absolute; top:0; right:0; width:100px; height:100px;
        border-radius:50%; opacity:0.1; transform:translate(30%,-30%); background:#fff;
    }
    .kpi-card-blue { background: linear-gradient(135deg, #134074, #1a5298); border:1px solid rgba(26,82,152,0.3); box-shadow:0 8px 24px rgba(19,64,116,0.3); }
    .kpi-card-gold { background: linear-gradient(135deg, #b8860b, #EEB902); border:1px solid rgba(238,185,2,0.3); box-shadow:0 8px 24px rgba(238,185,2,0.2); }
    .kpi-card-dark { background: linear-gradient(135deg, #0B2545, #134074); border:1px solid rgba(19,64,116,0.4); box-shadow:0 8px 24px rgba(11,37,69,0.4); }
    .kpi-card-success { background: linear-gradient(135deg, #065f46, #059669); border:1px solid rgba(5,150,105,0.3); box-shadow:0 8px 24px rgba(5,150,105,0.2); }
    .kpi-icon { font-size:20px; margin-bottom:10px; display:inline-block; }
    .kpi-label { font-size:11px; font-weight:500; color:rgba(255,255,255,0.7); text-transform:uppercase; letter-spacing:1.5px; margin-bottom:6px; }
    .kpi-value { font-size:26px; font-weight:800; color:#ffffff; letter-spacing:-1px; line-height:1; }
    .kpi-change { font-size:11px; font-weight:500; margin-top:6px; color:rgba(255,255,255,0.6); }

    .section-card {
        background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06);
        border-radius:16px; padding:20px 24px; margin-bottom:16px; backdrop-filter:blur(10px);
    }
    .section-title { font-size:15px !important; font-weight:700 !important; color:#e2e8f0 !important; margin-bottom:2px !important; display:flex; align-items:center; gap:10px; }
    .section-subtitle { font-size:11px; color:rgba(255,255,255,0.4); margin-bottom:12px; }
    .gold-accent { width:4px; height:18px; background: linear-gradient(180deg, #EEB902, #d4a302); border-radius:2px; display:inline-block; }

    .stSelectbox > div > div { background:rgba(255,255,255,0.05) !important; border:1px solid rgba(255,255,255,0.1) !important; border-radius:10px !important; color:#e2e8f0 !important; }
    .stSelectbox label, .stTextInput label, .stNumberInput label, .stFileUploader label, .stDateInput label { color:#94a3b8 !important; font-weight:500 !important; font-size:13px !important; }
    .stTextInput > div > div > input, .stNumberInput > div > div > input { background:rgba(255,255,255,0.05) !important; border:1px solid rgba(255,255,255,0.1) !important; border-radius:10px !important; color:#e2e8f0 !important; }

    .stFormSubmitButton > button {
        background: linear-gradient(135deg, #EEB902, #d4a302) !important; color:#0B2545 !important;
        font-weight:700 !important; border:none !important; border-radius:10px !important;
        padding:10px 24px !important; font-size:13px !important;
        box-shadow:0 4px 16px rgba(238,185,2,0.3) !important; transition:all 0.3s ease !important;
    }
    .stFormSubmitButton > button:hover { transform:translateY(-2px) !important; box-shadow:0 8px 24px rgba(238,185,2,0.4) !important; }

    .stDownloadButton > button {
        background:rgba(5,150,105,0.15) !important; border:1px solid rgba(5,150,105,0.3) !important;
        color:#6ee7b7 !important; border-radius:10px !important; font-weight:600 !important; font-size:13px !important;
        transition:all 0.3s ease !important;
    }
    .stDownloadButton > button:hover { background:rgba(5,150,105,0.25) !important; transform:translateY(-1px) !important; }

    [data-testid="stFileUploader"] { background:rgba(255,255,255,0.02) !important; border:1px dashed rgba(255,255,255,0.1) !important; border-radius:12px !important; padding:10px !important; }
    [data-testid="stFileUploader"] button { background:rgba(19,64,116,0.3) !important; border:1px solid rgba(19,64,116,0.5) !important; color:#93c5fd !important; border-radius:8px !important; }

    .streamlit-expanderHeader { background:rgba(255,255,255,0.03) !important; border:1px solid rgba(255,255,255,0.08) !important; border-radius:12px !important; color:#e2e8f0 !important; font-weight:600 !important; }

    .badge-pendente { background:rgba(239,68,68,0.15); color:#fca5a5; border:1px solid rgba(239,68,68,0.3); padding:3px 12px; border-radius:20px; font-size:11px; font-weight:600; }
    .badge-pago { background:rgba(5,150,105,0.15); color:#6ee7b7; border:1px solid rgba(5,150,105,0.3); padding:3px 12px; border-radius:20px; font-size:11px; font-weight:600; }

    hr { border-color:rgba(255,255,255,0.06) !important; margin:16px 0 !important; }
    [data-testid="stMetric"] { display:none; }

    ::-webkit-scrollbar { width:6px; height:6px; }
    ::-webkit-scrollbar-track { background:rgba(255,255,255,0.02); }
    ::-webkit-scrollbar-thumb { background:rgba(255,255,255,0.1); border-radius:3px; }

    @keyframes fadeInUp { from { opacity:0; transform:translateY(16px); } to { opacity:1; transform:translateY(0); } }
    .animate-in { animation: fadeInUp 0.5s ease forwards; }
    .delay-1 { animation-delay:0.1s; } .delay-2 { animation-delay:0.15s; } .delay-3 { animation-delay:0.2s; } .delay-4 { animation-delay:0.25s; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# 3. CARREGAR DADOS DO DISCO
# ═══════════════════════════════════════════════════════════════════
despesas_lista = carregar_despesas()
anexos_meta = carregar_meta_anexos()

if 'confirmando_exclusao' not in st.session_state:
    st.session_state.confirmando_exclusao = None

# ═══════════════════════════════════════════════════════════════════
# FUNÇÕES AUXILIARES
# ═══════════════════════════════════════════════════════════════════
def format_brl(value):
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def get_csv_download(dataframe):
    return dataframe.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')

def get_excel_download(dataframe):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        dataframe.to_excel(writer, index=False, sheet_name='Despesas')
    return output.getvalue()

# Converter para DataFrame
df = pd.DataFrame(despesas_lista)

# ═══════════════════════════════════════════════════════════════════
# 4. SIDEBAR — MENU LATERAL COM LOGO
# ═══════════════════════════════════════════════════════════════════
import base64

LOGO_PATH = os.path.join(DB_DIR, "logo.png")
logo_b64 = ""
if os.path.exists(LOGO_PATH):
    with open(LOGO_PATH, "rb") as img_file:
        logo_b64 = base64.b64encode(img_file.read()).decode()

with st.sidebar:
    # Logo
    if logo_b64:
        st.markdown(f"""
        <div style="text-align:center; padding:20px 10px 10px 10px;">
            <img src="data:image/png;base64,{logo_b64}" style="width:140px; height:auto; border-radius:12px; margin-bottom:8px;" />
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center; padding:20px 10px 10px 10px;">
            <div style="width:80px; height:80px; background:linear-gradient(135deg, #EEB902, #d4a302); border-radius:16px; display:flex; align-items:center; justify-content:center; font-size:36px; margin:0 auto 8px auto; box-shadow:0 4px 16px rgba(238,185,2,0.3);">🏗️</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center; margin-bottom:24px;">
        <div style="font-size:18px; font-weight:800; color:#ffffff; letter-spacing:-0.3px;">Vale Construtora</div>
        <div style="font-size:10px; color:rgba(255,255,255,0.4); letter-spacing:2px; text-transform:uppercase; margin-top:2px;">Sistema Financeiro</div>
    </div>
    """, unsafe_allow_html=True)

    # Separador
    st.markdown("<hr style='border-color:rgba(255,255,255,0.08) !important; margin:0 0 12px 0 !important;'>", unsafe_allow_html=True)

    # Navegação
    st.markdown("<div style='font-size:10px; font-weight:600; color:#EEB902; text-transform:uppercase; letter-spacing:2px; padding:0 8px; margin-bottom:8px;'>Navegação</div>", unsafe_allow_html=True)

    pagina = st.radio(
        "nav",
        ["📊  Dashboard", "➕  Novo Lançamento", "📋  Histórico Completo", "📎  Documentos & Anexos", "📈  Relatórios"],
        label_visibility="collapsed",
        key="nav_page"
    )

    # Stats no rodapé da sidebar
    st.markdown("<hr style='border-color:rgba(255,255,255,0.08) !important; margin:20px 0 12px 0 !important;'>", unsafe_allow_html=True)

    n_arquivos = sum(len(v) for v in anexos_meta.values())
    n_pend = len([d for d in despesas_lista if d["Status"] == "Pendente"])
    n_pago = len([d for d in despesas_lista if d["Status"] == "Pago"])

    st.markdown(f"""
    <div style="padding:8px 12px;">
        <div style="font-size:10px; font-weight:600; color:#EEB902; text-transform:uppercase; letter-spacing:2px; margin-bottom:12px;">Status do Banco</div>
        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
            <span style="font-size:12px; color:#94a3b8;">📦 Registros</span>
            <span style="font-size:12px; color:#e2e8f0; font-weight:600;">{len(despesas_lista)}</span>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
            <span style="font-size:12px; color:#94a3b8;">🔴 Pendentes</span>
            <span style="font-size:12px; color:#fca5a5; font-weight:600;">{n_pend}</span>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
            <span style="font-size:12px; color:#94a3b8;">🟢 Pagos</span>
            <span style="font-size:12px; color:#6ee7b7; font-weight:600;">{n_pago}</span>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
            <span style="font-size:12px; color:#94a3b8;">📎 Anexos</span>
            <span style="font-size:12px; color:#93c5fd; font-weight:600;">{n_arquivos}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center; padding:16px 0 8px 0; border-top:1px solid rgba(255,255,255,0.06); margin-top:12px;">
        <span style="font-size:10px; color:rgba(255,255,255,0.2);">💾 database/ · v1.0</span>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# 5. HEADER PRINCIPAL (área de conteúdo)
# ═══════════════════════════════════════════════════════════════════
n_arquivos = sum(len(v) for v in anexos_meta.values())
if logo_b64:
    logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="width:44px; height:44px; border-radius:10px; object-fit:cover;" />'
else:
    logo_html = '<div style="width:44px; height:44px; background:linear-gradient(135deg, #EEB902, #d4a302); border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:22px;">🏗️</div>'

st.markdown(f"""
<div class="header-container">
    <div class="header-left">
        {logo_html}
        <div>
            <div class="header-title">Vale Construtora</div>
            <div class="header-subtitle">Sistema de Gestão Financeira</div>
        </div>
    </div>
    <div class="header-right">
        <div class="db-badge">💾 {len(despesas_lista)} registros · {n_arquivos} anexos</div>
        <div class="header-badge">● Online</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# ROTEAMENTO DE PÁGINAS
# ═══════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════
# TAB 1 — DASHBOARD
# ═══════════════════════════════════════════════════════════════════
if "Dashboard" in pagina:
    total_pendente = df[df["Status"] == "Pendente"]["Valor"].sum() if len(df) > 0 else 0
    total_pago = df[df["Status"] == "Pago"]["Valor"].sum() if len(df) > 0 else 0
    total_geral = df["Valor"].sum() if len(df) > 0 else 0
    qtd = len(df)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="kpi-card kpi-card-dark animate-in delay-1"><div class="kpi-icon">💰</div><div class="kpi-label">Volume Total</div><div class="kpi-value">{format_brl(total_geral)}</div><div class="kpi-change">📊 {qtd} lançamentos</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="kpi-card kpi-card-blue animate-in delay-2"><div class="kpi-icon">⏳</div><div class="kpi-label">Total Pendente</div><div class="kpi-value">{format_brl(total_pendente)}</div><div class="kpi-change">🔴 {len(df[df["Status"]=="Pendente"]) if len(df)>0 else 0} itens</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="kpi-card kpi-card-success animate-in delay-3"><div class="kpi-icon">✅</div><div class="kpi-label">Total Pago</div><div class="kpi-value">{format_brl(total_pago)}</div><div class="kpi-change">🟢 {len(df[df["Status"]=="Pago"]) if len(df)>0 else 0} itens</div></div>""", unsafe_allow_html=True)
    with c4:
        pct = (total_pago / total_geral * 100) if total_geral > 0 else 0
        st.markdown(f"""<div class="kpi-card kpi-card-gold animate-in delay-4"><div class="kpi-icon">📈</div><div class="kpi-label">% Realizado</div><div class="kpi-value">{pct:.1f}%</div><div class="kpi-change">Meta: 100%</div></div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    if len(df) > 0:
        ch1, ch2, ch3 = st.columns([2, 1.5, 1.5])

        with ch1:
            st.markdown("""<div class="section-card"><div class="section-title"><span class="gold-accent"></span> Custos por Fornecedor</div><div class="section-subtitle">Distribuição de despesas</div></div>""", unsafe_allow_html=True)
            df_forn = df.groupby("Fornecedor")["Valor"].sum().sort_values(ascending=True).reset_index()
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(y=df_forn["Fornecedor"], x=df_forn["Valor"], orientation='h',
                marker=dict(color=df_forn["Valor"], colorscale=[[0,'#134074'],[0.5,'#1a5298'],[1,'#EEB902']], cornerradius=6),
                text=[format_brl(v) for v in df_forn["Valor"]], textposition='outside',
                textfont=dict(color='#94a3b8', size=11, family='Inter'),
                hovertemplate='<b>%{y}</b><br>R$ %{x:,.2f}<extra></extra>'))
            fig_bar.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Inter', color='#94a3b8'), margin=dict(l=10,r=80,t=10,b=10), height=320,
                xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.04)', zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, tickfont=dict(size=11, color='#cbd5e1')), bargap=0.35)
            st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})

        with ch2:
            st.markdown("""<div class="section-card"><div class="section-title"><span class="gold-accent"></span> Custos por Obra</div><div class="section-subtitle">Proporção entre empreendimentos</div></div>""", unsafe_allow_html=True)
            df_emp = df.groupby("Empreendimento")["Valor"].sum().reset_index()
            fig_donut = go.Figure()
            fig_donut.add_trace(go.Pie(labels=df_emp["Empreendimento"], values=df_emp["Valor"], hole=0.65,
                marker=dict(colors=['#134074','#EEB902','#1a5298'], line=dict(color='#0a1628', width=3)),
                textinfo='percent', textfont=dict(size=14, color='#ffffff', family='Inter'),
                hovertemplate='<b>%{label}</b><br>R$ %{value:,.2f}<extra></extra>'
            ))
            fig_donut.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Inter', color='#94a3b8'), margin=dict(l=20,r=20,t=10,b=10), height=320,
                showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5, font=dict(size=11, color='#cbd5e1')),
                annotations=[dict(text=f'<b>{format_brl(total_geral)}</b>', x=0.5, y=0.5, font_size=15, font_color='#ffffff', font_family='Inter', showarrow=False)])
            st.plotly_chart(fig_donut, use_container_width=True, config={'displayModeBar': False})

        with ch3:
            st.markdown("""<div class="section-card"><div class="section-title"><span class="gold-accent"></span> Status Financeiro</div><div class="section-subtitle">Pendente vs. Pago</div></div>""", unsafe_allow_html=True)
            fig_st = go.Figure()
            fig_st.add_trace(go.Pie(labels=['Pendente','Pago'], values=[total_pendente, total_pago], hole=0.7,
                marker=dict(colors=['#1a5298','#059669'], line=dict(color='#0a1628', width=3)),
                textinfo='percent', textfont=dict(size=14, color='#ffffff', family='Inter'),
                hovertemplate='<b>%{label}</b><br>R$ %{value:,.2f}<extra></extra>'))
            fig_st.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Inter', color='#94a3b8'), margin=dict(l=20,r=20,t=10,b=10), height=320,
                showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5, font=dict(size=11, color='#cbd5e1')),
                annotations=[dict(text=f'<b>{pct:.0f}%</b>', x=0.5, y=0.5, font_size=22, font_color='#059669', font_family='Inter', showarrow=False)])
            st.plotly_chart(fig_st, use_container_width=True, config={'displayModeBar': False})


# ═══════════════════════════════════════════════════════════════════
# TAB 2 — NOVO LANÇAMENTO
# ═══════════════════════════════════════════════════════════════════
elif "Novo Lançamento" in pagina:
    st.markdown("""<div class="section-card"><div class="section-title"><span class="gold-accent"></span> Registrar Novo Lançamento</div><div class="section-subtitle">Preencha os dados — o registro será salvo automaticamente no banco local</div></div>""", unsafe_allow_html=True)

    with st.form("novo_lancamento", clear_on_submit=True):
        fc1, fc2 = st.columns(2)
        with fc1:
            novo_emp = st.selectbox("🏗️ Empreendimento", ["Reserva Alta Vista", "Manancial"])
            novo_forn = st.text_input("🏢 Fornecedor *")
            nova_cat = st.selectbox("🏷️ Categoria", ["Marketing", "Eventos", "Suprimentos", "Alimentação", "Materiais", "Outros"])
            nova_data = st.date_input("📅 Data", value=datetime.now())
        with fc2:
            nova_desc = st.text_input("📝 Descrição do Produto/Serviço *")
            novo_valor = st.number_input("💰 Valor (R$) *", min_value=0.0, step=10.0, format="%.2f")
            novo_pix = st.text_input("🔑 Chave PIX (opcional)")
            novo_banco = st.text_input("🏦 Dados Bancários (Agência, Conta, Favorecido)")
            novo_status = st.selectbox("📌 Status", ["Pendente", "Pago"])
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

        # Upload de documento junto com o lançamento
        st.markdown("---")
        st.markdown("<span style='color:#94a3b8; font-size:13px; font-weight:500;'>📎 Anexar documento ao lançamento (opcional)</span>", unsafe_allow_html=True)
        arquivo_lancamento = st.file_uploader("Arraste PDF ou foto", type=["pdf","jpg","jpeg","png","webp"], accept_multiple_files=True, key="upload_novo")

        submit = st.form_submit_button("🚀 Registrar e Salvar no Banco", use_container_width=True)

        if submit:
            if novo_forn and nova_desc and novo_valor > 0:
                novo_id = f"d{str(uuid.uuid4())[:6]}"
                novo_dado = {
                    "id": novo_id,
                    "Empreendimento": novo_emp,
                    "Fornecedor": novo_forn,
                    "Descrição": nova_desc,
                    "Valor": novo_valor,
                    "Pix": novo_pix,
                    "DadosBancarios": novo_banco,
                    "Status": novo_status,
                    "Categoria": nova_cat,
                    "Data": str(nova_data),
                }
                despesas_lista.append(novo_dado)
                salvar_despesas(despesas_lista)

                # Salvar anexos se houver
                if arquivo_lancamento:
                    meta = carregar_meta_anexos()
                    if novo_id not in meta:
                        meta[novo_id] = []
                    for f_up in arquivo_lancamento:
                        info = salvar_arquivo_anexo(novo_id, f_up)
                        meta[novo_id].append(info)
                    salvar_meta_anexos(meta)

                st.success(f"✅ Lançamento salvo no banco! ID: {novo_id}")
                st.rerun()
            else:
                st.warning("⚠️ Preencha Fornecedor, Descrição e Valor.")


# ═══════════════════════════════════════════════════════════════════
# TAB 3 — HISTÓRICO COMPLETO (REDESENHADO)
# ═══════════════════════════════════════════════════════════════════
elif "Histórico Completo" in pagina:
    despesas_lista = carregar_despesas()
    df = pd.DataFrame(despesas_lista) if despesas_lista else pd.DataFrame()

    # ── Header da seção com visual aprimorado ──
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0B2545 0%, #134074 100%); border-radius:16px; padding:28px 32px; margin-bottom:20px; border:1px solid rgba(238,185,2,0.2); position:relative; overflow:hidden;">
        <div style="position:absolute; top:-40px; right:-40px; width:200px; height:200px; background:radial-gradient(circle, rgba(238,185,2,0.1) 0%, transparent 70%); border-radius:50%;"></div>
        <div style="display:flex; align-items:center; gap:14px; margin-bottom:6px;">
            <span style="font-size:28px;">📋</span>
            <span style="font-size:22px; font-weight:800; color:#ffffff; letter-spacing:-0.5px;">Histórico Completo de Despesas</span>
        </div>
        <span style="font-size:13px; color:rgba(255,255,255,0.5);">Todos os débitos a pagar e pagos · Filtre, altere status, exclua ou exporte · 💾 Dados persistidos em disco</span>
    </div>
    """, unsafe_allow_html=True)

    if len(df) == 0:
        st.info("📭 Nenhuma despesa cadastrada. Vá em '➕ Novo Lançamento' para adicionar.")
    else:
        # ── Filtros em caixas estilizadas ──
        st.markdown("""
        <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06); border-radius:12px; padding:16px 20px; margin-bottom:16px;">
            <span style="font-size:13px; font-weight:600; color:#EEB902; letter-spacing:1px; text-transform:uppercase;">🔍 Filtros Rápidos</span>
        </div>
        """, unsafe_allow_html=True)

        hf1, hf2, hf3, hf4 = st.columns(4)
        with hf1:
            h_emp = st.selectbox("🏗️ Empreendimento", ["Todos"] + list(df["Empreendimento"].unique()), key="h_emp")
        with hf2:
            h_status = st.selectbox("📌 Status", ["Todos", "Pendente", "Pago"], key="h_status")
        with hf3:
            h_cat = st.selectbox("🏷️ Categoria", ["Todas"] + list(df["Categoria"].unique()), key="h_cat")
        with hf4:
            h_forn = st.selectbox("🏢 Fornecedor", ["Todos"] + sorted(df["Fornecedor"].unique().tolist()), key="h_forn")

        df_hist = df.copy()
        if h_emp != "Todos": df_hist = df_hist[df_hist["Empreendimento"] == h_emp]
        if h_status != "Todos": df_hist = df_hist[df_hist["Status"] == h_status]
        if h_cat != "Todas": df_hist = df_hist[df_hist["Categoria"] == h_cat]
        if h_forn != "Todos": df_hist = df_hist[df_hist["Fornecedor"] == h_forn]

        # Ordenar em ordem alfabética pelo Fornecedor e corrigir nulos
        df_hist = df_hist.sort_values(by="Fornecedor", ascending=True).fillna('')

        total_f = df_hist["Valor"].sum()
        pend_f = df_hist[df_hist["Status"] == "Pendente"]["Valor"].sum()
        pago_f = df_hist[df_hist["Status"] == "Pago"]["Valor"].sum()

        # ── KPI resumo em caixas coloridas ──
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        kc1, kc2, kc3, kc4 = st.columns(4)
        with kc1:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg, #0B2545, #134074); border:1px solid rgba(19,64,116,0.4); border-radius:12px; padding:16px 20px; text-align:center;">
                <div style="font-size:12px; color:rgba(255,255,255,0.6); text-transform:uppercase; letter-spacing:1px; font-weight:600;">📊 Registros</div>
                <div style="font-size:28px; font-weight:800; color:#ffffff; margin-top:4px;">{len(df_hist)}</div>
            </div>""", unsafe_allow_html=True)
        with kc2:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg, #134074, #1a5298); border:1px solid rgba(26,82,152,0.4); border-radius:12px; padding:16px 20px; text-align:center;">
                <div style="font-size:12px; color:rgba(255,255,255,0.6); text-transform:uppercase; letter-spacing:1px; font-weight:600;">💰 Total</div>
                <div style="font-size:22px; font-weight:800; color:#ffffff; margin-top:4px;">{format_brl(total_f)}</div>
            </div>""", unsafe_allow_html=True)
        with kc3:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg, #7f1d1d, #991b1b); border:1px solid rgba(239,68,68,0.3); border-radius:12px; padding:16px 20px; text-align:center;">
                <div style="font-size:12px; color:rgba(255,255,255,0.6); text-transform:uppercase; letter-spacing:1px; font-weight:600;">🔴 Pendente</div>
                <div style="font-size:22px; font-weight:800; color:#fca5a5; margin-top:4px;">{format_brl(pend_f)}</div>
            </div>""", unsafe_allow_html=True)
        with kc4:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg, #065f46, #059669); border:1px solid rgba(5,150,105,0.3); border-radius:12px; padding:16px 20px; text-align:center;">
                <div style="font-size:12px; color:rgba(255,255,255,0.6); text-transform:uppercase; letter-spacing:1px; font-weight:600;">🟢 Pago</div>
                <div style="font-size:22px; font-weight:800; color:#6ee7b7; margin-top:4px;">{format_brl(pago_f)}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        # ── Barra de ações: Ver Tudo, Impressora, Download ──
        st.markdown("""
        <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06); border-radius:12px; padding:12px 20px; margin-bottom:16px;">
            <span style="font-size:13px; font-weight:600; color:#EEB902; letter-spacing:1px; text-transform:uppercase;">⚡ Ações Rápidas</span>
        </div>
        """, unsafe_allow_html=True)

        act1, act2, act3, act4, act5 = st.columns([1.2, 1.2, 1.2, 1.2, 2])
        with act1:
            if st.button("👁️ Ver Tudo", key="ver_tudo", help="Limpar filtros e mostrar todos os registros", use_container_width=True):
                for k in ["h_emp", "h_status", "h_cat", "h_forn"]:
                    if k in st.session_state:
                        if k == "h_cat":
                            st.session_state[k] = "Todas"
                        else:
                            st.session_state[k] = "Todos"
                st.rerun()
        with act2:
            # Botão de Relatório para Impressão
            relatorio_html = f"""
<html><head><meta charset="utf-8"><title>Relatório Vale Construtora</title>
<style>
body {{ font-family: Arial, sans-serif; padding: 30px; color: #333; }}
h1 {{ color: #0B2545; border-bottom: 3px solid #EEB902; padding-bottom: 10px; }}
h2 {{ color: #134074; margin-top: 30px; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 13px; }}
th {{ background: #0B2545; color: white; padding: 12px 10px; text-align: left; font-size: 12px; text-transform: uppercase; }}
td {{ padding: 10px; border-bottom: 1px solid #e0e0e0; }}
tr:nth-child(even) {{ background: #f8f9fa; }}
.pendente {{ color: #dc2626; font-weight: 700; }}
.pago {{ color: #059669; font-weight: 700; }}
.total-box {{ background: #0B2545; color: white; padding: 20px; border-radius: 8px; margin: 20px 0; display:inline-block; margin-right:15px; }}
.total-box .label {{ font-size: 11px; text-transform: uppercase; opacity: 0.7; }}
.total-box .value {{ font-size: 24px; font-weight: 800; }}
.footer {{ margin-top: 40px; padding-top: 15px; border-top: 2px solid #EEB902; font-size: 11px; color: #666; }}
@media print {{ body {{ padding: 15px; }} }}
</style></head><body>
<h1>📊 Vale Construtora e Engenharia</h1>
<p style="color:#666;">Relatório de Despesas — Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
<div>
<div class="total-box"><div class="label">Total Geral</div><div class="value">{format_brl(total_f)}</div></div>
<div class="total-box" style="background:#991b1b;"><div class="label">Pendente</div><div class="value">{format_brl(pend_f)}</div></div>
<div class="total-box" style="background:#059669;"><div class="label">Pago</div><div class="value">{format_brl(pago_f)}</div></div>
</div>
<h2>Detalhamento de Despesas ({len(df_hist)} registros)</h2>
<table><thead><tr><th>#</th><th>Empreendimento</th><th>Fornecedor</th><th>Descrição</th><th>Valor</th><th>Status</th><th>Categoria</th><th>Data</th></tr></thead><tbody>
"""
            for i, (_, row) in enumerate(df_hist.iterrows()):
                cls = 'pendente' if row['Status'] == 'Pendente' else 'pago'
                relatorio_html += f"<tr><td>{i+1}</td><td>{row['Empreendimento']}</td><td>{row['Fornecedor']}</td><td>{row['Descrição']}</td><td><b>{format_brl(row['Valor'])}</b></td><td class='{cls}'>{row['Status']}</td><td>{row.get('Categoria','—')}</td><td>{row.get('Data','—')}</td></tr>\n"
            relatorio_html += f"""</tbody></table>
<div class="footer"><b>Vale Construtora e Engenharia</b> · Sistema de Gestão Financeira · {datetime.now().strftime('%d/%m/%Y')}</div>
<script>window.onload=function(){{window.print();}}</script></body></html>"""
            st.download_button("🖨️ Imprimir Relatório", relatorio_html.encode('utf-8'),
                f"relatorio_vale_{datetime.now().strftime('%Y%m%d_%H%M')}.html", "text/html", key="print_rel", use_container_width=True)
        with act3:
            st.download_button("⬇️ Baixar CSV", get_csv_download(df_hist),
                f"vale_despesas_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", "text/csv", key="dl_csv", use_container_width=True)
        with act4:
            try:
                st.download_button("⬇️ Baixar Excel", get_excel_download(df_hist),
                    f"vale_despesas_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_excel", use_container_width=True)
            except Exception:
                st.info("📦 Instale openpyxl")

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        # ── Cards das Despesas ──
        anexos_meta_atual = carregar_meta_anexos()
        for idx_num, (_, row) in enumerate(df_hist.iterrows()):
            rid = row.get("id", "")
            n_anx = len(anexos_meta_atual.get(rid, []))
            is_pendente = row['Status'] == "Pendente"

            # Cor do card baseada no status
            if is_pendente:
                card_bg = "linear-gradient(135deg, rgba(127,29,29,0.15) 0%, rgba(153,27,27,0.08) 100%)"
                card_border = "rgba(239,68,68,0.2)"
                border_left = "#ef4444"
            else:
                card_bg = "linear-gradient(135deg, rgba(6,95,70,0.15) 0%, rgba(5,150,105,0.08) 100%)"
                card_border = "rgba(5,150,105,0.2)"
                border_left = "#059669"

            # Card principal
            btn_pix_html = ""
            if row.get('Pix'):
                btn_pix_html = f"""<button onclick="var copyText = document.getElementById('pix_{rid}'); copyText.select(); document.execCommand('copy');" style="background:#065f46; color:white; border:none; border-radius:6px; padding:4px 10px; cursor:pointer; font-size:13px; font-weight:bold;">Copiar</button>"""

            html_card = f"""
<div style="background:{card_bg}; border:1px solid {card_border}; border-left:5px solid {border_left}; border-radius:12px; padding:24px 28px; margin-bottom:14px; transition:all 0.2s ease;">
<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:20px;">
<div style="flex:1; min-width:300px;">
<div style="display:flex; align-items:center; gap:12px; margin-bottom:12px;">
<span style="background:rgba(238,185,2,0.2); color:#EEB902; font-weight:700; font-size:14px; padding:6px 14px; border-radius:8px;">#{idx_num+1}</span>
<span style="color:#EEB902; font-size:18px; font-weight:600;">🏗️ {row['Empreendimento']}</span>
</div>
<div style="font-size:26px; font-weight:700; color:#ffffff; margin-bottom:10px;">{row['Fornecedor']}</div>
<div style="font-size:18px; color:#cbd5e1; margin-bottom:12px; line-height:1.4;">📝 {row['Descrição']}</div>
<div style="font-size:16px; color:#93c5fd; margin-bottom:12px; font-weight:600; background:rgba(147,197,253,0.1); padding:6px 12px; border-radius:6px; display:inline-block;">🏦 Banco/Dados: {row.get("DadosBancarios") if row.get("DadosBancarios") else "Não informado"}</div><br>
<div style="font-size:16px; color:#6ee7b7; margin-bottom:14px; display:flex; align-items:center; gap:8px;">
    🔑 PIX: 
    <input type="text" value="{row.get('Pix', '')}" id="pix_{rid}" style="background:transparent; border:none; color:#6ee7b7; font-weight:bold; width:220px; outline:none; font-size:16px;" readonly>
    {btn_pix_html}
</div>
<div style="display:flex; gap:20px; flex-wrap:wrap;">
<span style="font-size:14px; color:#94a3b8;">🏷️ {row.get('Categoria','—')}</span>
<span style="font-size:14px; color:#94a3b8;">📅 {row.get('Data','—')}</span>
{"<span style='font-size:14px; color:#93c5fd; font-weight:500;'>📎 " + str(n_anx) + " anexo(s)</span>" if n_anx > 0 else ""}
</div>
</div>
<div style="text-align:right; min-width:200px; display:flex; flex-direction:column; align-items:flex-end; gap:12px;">
<div style="font-size:32px; font-weight:800; color:#ffffff;">{format_brl(row['Valor'])}</div>
<span class="{'badge-pendente' if is_pendente else 'badge-pago'}" style="font-size:15px; padding:8px 24px;">{row['Status']}</span>
</div>
</div>
</div>
"""
            st.markdown(html_card, unsafe_allow_html=True)

            # Botões de ação para cada card
            btn1, btn2, btn3, btn4, btn5, _ = st.columns([1.2, 1, 1.2, 1, 1, 1.5])
            with btn1:
                if is_pendente:
                    if st.button("✅ Marcar Pago", key=f"pago_{rid}", help="Alterar status para Pago", use_container_width=True):
                        lista_atualizada = carregar_despesas()
                        for d in lista_atualizada:
                            if d["id"] == rid:
                                d["Status"] = "Pago"
                                break
                        salvar_despesas(lista_atualizada)
                        st.rerun()
                else:
                    if st.button("↩️ Desfazer", key=f"pendente_{rid}", help="Voltar status para Pendente", use_container_width=True):
                        lista_atualizada = carregar_despesas()
                        for d in lista_atualizada:
                            if d["id"] == rid:
                                d["Status"] = "Pendente"
                                break
                        salvar_despesas(lista_atualizada)
                        st.rerun()
            with btn2:
                if st.button("🗑️ Excluir", key=f"del_{rid}", help="Excluir lançamento", use_container_width=True):
                    st.session_state.confirmando_exclusao = rid
                    st.rerun()
            with btn3:
                # Download individual do registro como CSV
                row_df = pd.DataFrame([row.to_dict()])
                st.download_button("⬇️ Exportar", get_csv_download(row_df), f"despesa_{rid}.csv", "text/csv",
                    key=f"dl_row_{rid}", use_container_width=True)
            with btn4:
                if st.button("✏️ Editar", key=f"btn_edit_{rid}", use_container_width=True):
                    st.session_state[f"show_edit_{rid}"] = not st.session_state.get(f"show_edit_{rid}", False)
                    if st.session_state.get(f"show_up_{rid}", False): st.session_state[f"show_up_{rid}"] = False
                    st.rerun()
            with btn5:
                if st.button("📎 Anexar", key=f"btn_up_{rid}", use_container_width=True):
                    st.session_state[f"show_up_{rid}"] = not st.session_state.get(f"show_up_{rid}", False)
                    if st.session_state.get(f"show_edit_{rid}", False): st.session_state[f"show_edit_{rid}"] = False
                    st.rerun()

            # Área de edição inline
            if st.session_state.get(f"show_edit_{rid}", False):
                with st.container():
                    st.markdown("""<div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.1); border-radius:10px; padding:16px; margin-top:8px;">""", unsafe_allow_html=True)
                    st.markdown("<span style='color:#EEB902; font-weight:600; font-size:14px;'>✏️ Editar Lançamento</span>", unsafe_allow_html=True)
                    with st.form(f"form_edit_{rid}"):
                        ce1, ce2 = st.columns(2)
                        with ce1:
                            emp_list = ["Reserva Alta Vista", "Manancial"]
                            e_emp = st.selectbox("Empreendimento", emp_list, index=emp_list.index(row.get("Empreendimento")) if row.get("Empreendimento") in emp_list else 0)
                            e_forn = st.text_input("Fornecedor", value=row.get("Fornecedor", ""))
                            cat_list = ["Marketing", "Eventos", "Suprimentos", "Alimentação", "Materiais", "Outros"]
                            e_cat = st.selectbox("Categoria", cat_list, index=cat_list.index(row.get("Categoria", "Outros")) if row.get("Categoria", "Outros") in cat_list else 5)
                        with ce2:
                            e_desc = st.text_input("Descrição", value=row.get("Descrição", ""))
                            e_val = st.number_input("Valor", value=float(row.get("Valor", 0.0)), format="%.2f")
                            e_pix = st.text_input("Chave PIX", value=row.get("Pix", ""))
                            e_banco = st.text_input("Dados Bancários", value=row.get("DadosBancarios", ""))
                            e_stat = st.selectbox("Status", ["Pendente", "Pago"], index=0 if row.get("Status")=="Pendente" else 1)
                        if st.form_submit_button("Salvar Alterações", use_container_width=True):
                            lista_atualizada = carregar_despesas()
                            for d in lista_atualizada:
                                if d["id"] == rid:
                                    d["Empreendimento"] = e_emp
                                    d["Fornecedor"] = e_forn
                                    d["Categoria"] = e_cat
                                    d["Descrição"] = e_desc
                                    d["Valor"] = e_val
                                    d["Pix"] = e_pix
                                    d["DadosBancarios"] = e_banco
                                    d["Status"] = e_stat
                                    break
                            salvar_despesas(lista_atualizada)
                            st.session_state[f"show_edit_{rid}"] = False
                            st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

            # Área de upload inline
            if st.session_state.get(f"show_up_{rid}", False):
                with st.container():
                    st.markdown("""<div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.1); border-radius:10px; padding:16px; margin-top:8px;">""", unsafe_allow_html=True)
                    st.markdown("<span style='color:#EEB902; font-weight:600; font-size:14px;'>📎 Anexar Documentos</span>", unsafe_allow_html=True)
                    upl = st.file_uploader("Selecione os arquivos", type=["pdf", "jpg", "jpeg", "png", "webp"], accept_multiple_files=True, key=f"upfile_{rid}")
                    if st.button("Salvar Anexos", key=f"saveup_{rid}", use_container_width=True):
                        if upl:
                            meta = carregar_meta_anexos()
                            if rid not in meta:
                                meta[rid] = []
                            for f in upl:
                                info = salvar_arquivo_anexo(rid, f)
                                meta[rid].append(info)
                            salvar_meta_anexos(meta)
                            st.session_state[f"show_up_{rid}"] = False
                            st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        # ── Confirmação de exclusão ──
        if st.session_state.confirmando_exclusao:
            exc_id = st.session_state.confirmando_exclusao
            exc_item = next((d for d in despesas_lista if d["id"] == exc_id), None)
            if exc_item:
                st.markdown("---")
                st.markdown(f"""
                <div style="background:rgba(239,68,68,0.12); border:1px solid rgba(239,68,68,0.4); border-radius:14px; padding:20px 24px;">
                    <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
                        <span style="font-size:24px;">⚠️</span>
                        <span style="color:#fca5a5; font-weight:800; font-size:18px;">Confirmar Exclusão</span>
                    </div>
                    <div style="font-size:15px; color:#e2e8f0; margin-bottom:6px;">
                        <b>{exc_item['Fornecedor']}</b> — {exc_item['Descrição']}
                    </div>
                    <div style="font-size:20px; font-weight:800; color:#fca5a5; margin-bottom:8px;">{format_brl(exc_item['Valor'])}</div>
                    <div style="font-size:12px; color:#94a3b8;">⚠️ Todos os anexos deste lançamento serão excluídos permanentemente do disco.</div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                cc1, cc2, cc3 = st.columns([1, 1, 4])
                with cc1:
                    if st.button("✅ Sim, excluir", key="confirm_del", type="primary", use_container_width=True):
                        excluir_despesa(exc_id)
                        st.session_state.confirmando_exclusao = None
                        st.rerun()
                with cc2:
                    if st.button("❌ Cancelar", key="cancel_del", use_container_width=True):
                        st.session_state.confirmando_exclusao = None
                        st.rerun()


# ═══════════════════════════════════════════════════════════════════
# TAB 4 — DOCUMENTOS & ANEXOS
# ═══════════════════════════════════════════════════════════════════
elif "Documentos & Anexos" in pagina:
    despesas_lista = carregar_despesas()
    anexos_meta = carregar_meta_anexos()

    st.markdown("""<div class="section-card"><div class="section-title"><span class="gold-accent"></span> Central de Documentos</div><div class="section-subtitle">Anexe PDFs, fotos e documentos fiscais · Arquivos salvos em <code style="color:#EEB902">database/anexos/</code></div></div>""", unsafe_allow_html=True)

    if not despesas_lista:
        st.info("📭 Nenhuma despesa cadastrada.")
    else:
        # Seletor
        opcoes = []
        for d in despesas_lista:
            n_anx = len(anexos_meta.get(d["id"], []))
            tag = f" (📎 {n_anx})" if n_anx > 0 else ""
            opcoes.append(f"{d['Fornecedor']} — {d['Descrição'][:40]}{tag}")

        selected_idx = st.selectbox("Selecione o lançamento:", range(len(opcoes)), format_func=lambda i: opcoes[i], key="doc_select")
        sel = despesas_lista[selected_idx]
        sel_id = sel["id"]

        # Card detalhes
        badge_class = 'badge-pendente' if sel['Status'] == 'Pendente' else 'badge-pago'
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06); border-radius:12px; padding:16px 20px; margin:12px 0;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                <div>
                    <span style="color:#EEB902; font-weight:700; font-size:13px;">🏗️ {sel['Empreendimento']}</span>
                    <span style="color:rgba(255,255,255,0.3); margin:0 8px;">|</span>
                    <span style="color:#e2e8f0; font-weight:600; font-size:14px;">{sel['Fornecedor']}</span>
                </div>
                <div>
                    <span style="color:#ffffff; font-weight:800; font-size:16px;">{format_brl(sel['Valor'])}</span>
                    <span style="margin-left:12px;" class="{badge_class}">{sel['Status']}</span>
                </div>
            </div>
            <div style="margin-top:8px; color:#94a3b8; font-size:12px;">📝 {sel['Descrição']} &nbsp;|&nbsp; 📅 {sel.get('Data','—')}</div>
        </div>
        """, unsafe_allow_html=True)

        # Upload
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "📤 Arraste ou clique para anexar (PDF, JPG, PNG)",
            type=["pdf", "jpg", "jpeg", "png", "webp"],
            accept_multiple_files=True,
            key=f"upload_{sel_id}"
        )

        if uploaded_files:
            if st.button("💾 Salvar Anexos no Banco", key="save_anexos", type="primary"):
                if sel_id not in anexos_meta:
                    anexos_meta[sel_id] = []
                for f_up in uploaded_files:
                    info = salvar_arquivo_anexo(sel_id, f_up)
                    anexos_meta[sel_id].append(info)
                salvar_meta_anexos(anexos_meta)
                st.success(f"✅ {len(uploaded_files)} arquivo(s) salvo(s) em database/anexos/{sel_id}/")
                st.rerun()

        # Listar anexos existentes
        lista_anexos = anexos_meta.get(sel_id, [])

        if lista_anexos:
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
            st.markdown(f"""<div class="section-card"><div class="section-title"><span class="gold-accent"></span> Arquivos Anexados ({len(lista_anexos)})</div><div class="section-subtitle">Salvos em database/anexos/{sel_id}/</div></div>""", unsafe_allow_html=True)

            for i, anx in enumerate(lista_anexos):
                icon = "📄" if "pdf" in anx.get("tipo", "") else "🖼️"
                tamanho_kb = anx.get("tamanho", 0) / 1024

                ac1, ac2, ac3, ac4 = st.columns([0.4, 3, 1.2, 0.6])

                with ac1:
                    st.markdown(f"<span style='font-size:24px;'>{icon}</span>", unsafe_allow_html=True)
                with ac2:
                    st.markdown(f"""
                    <div>
                        <span style='color:#e2e8f0; font-weight:600; font-size:13px;'>{anx['nome_original']}</span><br>
                        <span style='color:#64748b; font-size:10px;'>📅 {anx.get('data_upload','—')} &nbsp;·&nbsp; 📦 {tamanho_kb:.1f} KB</span>
                    </div>
                    """, unsafe_allow_html=True)
                with ac3:
                    dados_arquivo = ler_arquivo_anexo(anx["caminho"])
                    if dados_arquivo:
                        st.download_button("⬇️ Baixar", dados_arquivo, anx["nome_original"], anx["tipo"], key=f"dl_anx_{sel_id}_{i}")
                    else:
                        st.markdown("<span style='color:#fca5a5; font-size:11px;'>Arquivo não encontrado</span>", unsafe_allow_html=True)
                with ac4:
                    if st.button("🗑️", key=f"del_anx_{sel_id}_{i}", help="Excluir anexo"):
                        excluir_arquivo_anexo(anx["caminho"])
                        anexos_meta[sel_id].pop(i)
                        salvar_meta_anexos(anexos_meta)
                        st.rerun()

                st.markdown("<hr style='margin:4px 0 !important; border-color:rgba(255,255,255,0.03) !important;'>", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align:center; padding:40px; color:rgba(255,255,255,0.2); font-size:14px;">
                📎 Nenhum documento anexado<br>
                <span style="font-size:11px;">Use o campo acima para enviar PDFs e fotos</span>
            </div>
            """, unsafe_allow_html=True)

        # Resumo geral
        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
        st.markdown("""<div class="section-card"><div class="section-title"><span class="gold-accent"></span> Resumo de Documentos por Fornecedor</div><div class="section-subtitle">Visão geral de todos os anexos salvos no banco</div></div>""", unsafe_allow_html=True)

        for d in despesas_lista:
            n = len(anexos_meta.get(d["id"], []))
            icon_s = "🟢" if n > 0 else "🔴"
            text_s = f"{n} arquivo(s)" if n > 0 else "Sem documentos"
            st.markdown(f"""
            <div style="display:flex; align-items:center; justify-content:space-between; padding:8px 16px; border-bottom:1px solid rgba(255,255,255,0.03);">
                <div><span style="color:#e2e8f0; font-size:12px; font-weight:500;">{d['Fornecedor']}</span>
                <span style="color:#64748b; font-size:11px; margin-left:8px;">— {d['Descrição'][:35]}</span></div>
                <span style="color:{'#6ee7b7' if n>0 else '#fca5a5'}; font-size:11px; font-weight:500;">{icon_s} {text_s}</span>
            </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# TAB 5 — RELATÓRIOS
# ═══════════════════════════════════════════════════════════════════
elif "Relatórios" in pagina:
    despesas_lista = carregar_despesas()
    df = pd.DataFrame(despesas_lista) if despesas_lista else pd.DataFrame()

    st.markdown("""<div class="section-card"><div class="section-title"><span class="gold-accent"></span> Relatórios Analíticos</div><div class="section-subtitle">Análises detalhadas por categoria, empreendimento e fornecedor</div></div>""", unsafe_allow_html=True)

    if len(df) == 0:
        st.info("📭 Sem dados para relatórios.")
    else:
        rc1, rc2 = st.columns(2)

        with rc1:
            st.markdown("""<div class="section-card"><div class="section-title"><span class="gold-accent"></span> Despesas por Categoria</div></div>""", unsafe_allow_html=True)
            df_cat = df.groupby("Categoria")["Valor"].sum().sort_values(ascending=False).reset_index()
            colors_cat = ['#EEB902', '#134074', '#1a5298', '#059669', '#d4a302', '#64748b']
            fig_cat = go.Figure()
            fig_cat.add_trace(go.Bar(x=df_cat["Categoria"], y=df_cat["Valor"],
                marker=dict(color=colors_cat[:len(df_cat)], cornerradius=8),
                text=[format_brl(v) for v in df_cat["Valor"]], textposition='outside',
                textfont=dict(color='#94a3b8', size=11, family='Inter'),
                hovertemplate='<b>%{x}</b><br>R$ %{y:,.2f}<extra></extra>'))
            fig_cat.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Inter', color='#94a3b8'), margin=dict(l=10,r=10,t=10,b=10), height=340,
                xaxis=dict(showgrid=False, tickfont=dict(size=11, color='#cbd5e1')),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.04)', zeroline=False, showticklabels=False), bargap=0.4)
            st.plotly_chart(fig_cat, use_container_width=True, config={'displayModeBar': False})

        with rc2:
            st.markdown("""<div class="section-card"><div class="section-title"><span class="gold-accent"></span> Comparativo: Pendente vs Pago</div></div>""", unsafe_allow_html=True)
            df_comp = df.groupby(["Empreendimento", "Status"])["Valor"].sum().reset_index()
            fig_comp = go.Figure()
            for status, color in [("Pendente", "#1a5298"), ("Pago", "#059669")]:
                df_s = df_comp[df_comp["Status"] == status]
                fig_comp.add_trace(go.Bar(name=status, x=df_s["Empreendimento"], y=df_s["Valor"],
                    marker=dict(color=color, cornerradius=8),
                    text=[format_brl(v) for v in df_s["Valor"]], textposition='outside',
                    textfont=dict(color='#94a3b8', size=11, family='Inter'),
                    hovertemplate='<b>%{x}</b><br>%{fullData.name}: R$ %{y:,.2f}<extra></extra>'))
            fig_comp.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Inter', color='#94a3b8'), margin=dict(l=10,r=10,t=10,b=10), height=340,
                barmode='group', bargap=0.3, bargroupgap=0.1,
                xaxis=dict(showgrid=False, tickfont=dict(size=11, color='#cbd5e1')),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.04)', zeroline=False, showticklabels=False),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11, color='#cbd5e1')))
            st.plotly_chart(fig_comp, use_container_width=True, config={'displayModeBar': False})

        # Tabela resumo
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.markdown("""<div class="section-card"><div class="section-title"><span class="gold-accent"></span> Ranking de Fornecedores</div><div class="section-subtitle">Maiores fornecedores por volume</div></div>""", unsafe_allow_html=True)

        df_resumo = df.groupby("Fornecedor").agg(
            Total=("Valor", "sum"), Qtd=("Valor", "count"),
            Pendente=("Status", lambda x: (x == "Pendente").sum()),
            Pago=("Status", lambda x: (x == "Pago").sum()),
        ).sort_values("Total", ascending=False).reset_index()

        rh = st.columns([0.5, 3, 2, 1, 1, 1])
        for col, h in zip(rh, ["#", "Fornecedor", "💰 Total", "📦 Qtd", "🔴 Pend.", "🟢 Pago"]):
            col.markdown(f"<span style='font-size:10px; font-weight:700; color:#EEB902; text-transform:uppercase; letter-spacing:1px;'>{h}</span>", unsafe_allow_html=True)
        st.markdown("<hr style='margin:6px 0 !important; border-color:rgba(238,185,2,0.2) !important;'>", unsafe_allow_html=True)

        for i, row in df_resumo.iterrows():
            rc = st.columns([0.5, 3, 2, 1, 1, 1])
            with rc[0]: st.markdown(f"<span style='color:#64748b; font-size:12px; font-weight:600;'>{i+1}</span>", unsafe_allow_html=True)
            with rc[1]: st.markdown(f"<span style='color:#e2e8f0; font-size:13px; font-weight:500;'>{row['Fornecedor']}</span>", unsafe_allow_html=True)
            with rc[2]: st.markdown(f"<span style='color:#ffffff; font-size:13px; font-weight:700;'>{format_brl(row['Total'])}</span>", unsafe_allow_html=True)
            with rc[3]: st.markdown(f"<span style='color:#94a3b8; font-size:12px;'>{row['Qtd']}</span>", unsafe_allow_html=True)
            with rc[4]: st.markdown(f"<span style='color:#fca5a5; font-size:12px; font-weight:600;'>{row['Pendente']}</span>", unsafe_allow_html=True)
            with rc[5]: st.markdown(f"<span style='color:#6ee7b7; font-size:12px; font-weight:600;'>{row['Pago']}</span>", unsafe_allow_html=True)
            st.markdown("<hr style='margin:2px 0 !important; border-color:rgba(255,255,255,0.03) !important;'>", unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        dl_r1, dl_r2, dl_r3 = st.columns([1, 1, 4])
        with dl_r1:
            st.download_button("⬇️ Exportar Despesas (CSV)", get_csv_download(df),
                f"relatorio_vale_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv", key="rel_csv")
        with dl_r2:
            st.download_button("⬇️ Exportar Resumo (CSV)", get_csv_download(df_resumo),
                f"resumo_fornecedores_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv", key="rel_resumo_csv")


# ═══════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════
st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
st.markdown(f"""
<div style="text-align:center; padding:20px; border-top:1px solid rgba(255,255,255,0.06); color:rgba(255,255,255,0.25); font-size:11px; font-family:'Inter',sans-serif;">
    <span style="color:#EEB902; font-weight:600;">Vale Construtora e Engenharia</span> &nbsp;·&nbsp;
    Sistema de Gestão Financeira &nbsp;·&nbsp; 💾 Banco: database/ &nbsp;·&nbsp; 2025
</div>
""", unsafe_allow_html=True)
