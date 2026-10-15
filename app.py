import streamlit as st
import pandas as pd
import numpy as np
import random
import io
import time
import math
import re
from datetime import time as dtime
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from copy import deepcopy

# ==============================================================================
# 1. ESTÉTICA (IDENTIDAD UPRM - DISEÑO PREMIUM)
# ==============================================================================
st.set_page_config(page_title="UPRM Scheduler Platinum v15", page_icon="🏛️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;700;900&family=Source+Sans+Pro:wght@300;400;600&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e9f0e8 100%);
        background-attachment: fixed;
        color: #1a1a1a;
    }
    
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 20% 30%, rgba(0, 75, 35, 0.02) 0%, transparent 20%),
            radial-gradient(circle at 80% 70%, rgba(198, 146, 20, 0.02) 0%, transparent 25%),
            repeating-linear-gradient(45deg, rgba(0,75,35,0.01) 0px, rgba(0,75,35,0.01) 2px, transparent 2px, transparent 8px);
        pointer-events: none;
        z-index: 0;
    }
    
    .main > div {
        position: relative;
        z-index: 1;
    }

    .rum-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 25px 50px;
        background: linear-gradient(105deg, rgba(255,255,255,0.95) 0%, rgba(248,250,248,0.98) 100%);
        border-bottom: 6px solid #004B23;
        margin-bottom: 35px;
        border-radius: 0 0 30px 30px;
        box-shadow: 0 15px 30px -10px rgba(0, 75, 35, 0.15);
        position: relative;
        backdrop-filter: blur(5px);
        z-index: 10;
    }
    
    .rum-header::after {
        content: "";
        position: absolute;
        bottom: -8px;
        left: 10%;
        width: 80%;
        height: 3px;
        background: linear-gradient(90deg, transparent, #C69214, #E6B422, #C69214, transparent);
        border-radius: 50%;
    }

    .header-logo {
        display: flex;
        align-items: center;
        gap: 20px;
    }

    .header-logo img {
        height: 100px;
        width: auto;
        filter: drop-shadow(0 4px 6px rgba(0,0,0,0.05));
        transition: transform 0.3s ease;
    }
    .header-logo img:hover {
        transform: scale(1.02);
    }

    .title-box {
        text-align: center;
        z-index: 2;
    }

    .title-box h1 {
        font-family: 'Playfair Display', serif !important;
        background: linear-gradient(135deg, #004B23 0%, #0A6B3A 80%);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent !important;
        font-size: 3.2rem !important;
        margin: 5px 0 !important;
        letter-spacing: 3px;
        font-weight: 900;
        text-shadow: 0 2px 10px rgba(0, 75, 35, 0.1);
    }

    .title-box p {
        color: #2c3e50 !important;
        font-family: 'Source Sans Pro', sans-serif;
        letter-spacing: 4px;
        font-size: 0.9rem;
        font-weight: 400;
        text-transform: uppercase;
    }

    .subtitle-accent {
        color: #C69214;
        font-weight: 700;
    }

    .glass-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 24px;
        padding: 28px;
        border: 1px solid rgba(0, 75, 35, 0.15);
        box-shadow: 0 20px 35px -8px rgba(0, 75, 35, 0.1), 0 5px 10px -4px rgba(0,0,0,0.02);
        margin-bottom: 25px;
        transition: all 0.25s ease;
        color: #1a1a1a;
    }
    .glass-card:hover {
        box-shadow: 0 25px 40px -12px rgba(0, 75, 35, 0.18);
        border-color: rgba(198, 146, 20, 0.3);
        background: rgba(255, 255, 255, 0.75);
    }

    .stButton > button {
        background: linear-gradient(145deg, #004B23 0%, #0A6B3A 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 50px !important;
        width: 100%;
        border: none !important;
        height: 58px;
        font-size: 1.2rem;
        letter-spacing: 1px;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        box-shadow: 0 8px 15px rgba(0, 75, 35, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        text-transform: uppercase;
        font-family: 'Source Sans Pro', sans-serif;
    }
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 25px rgba(0, 75, 35, 0.35);
        background: linear-gradient(145deg, #0A6B3A 0%, #118B4A 100%) !important;
    }
    .stButton > button:active {
        transform: translateY(1px);
        box-shadow: 0 5px 10px rgba(0, 75, 35, 0.3);
    }

    .stDownloadButton > button {
        background: linear-gradient(145deg, #C69214 0%, #E6B422 100%) !important;
        color: #1a1a1a !important;
        font-weight: 700 !important;
        border-radius: 50px !important;
        border: 1px solid rgba(255, 215, 0, 0.5) !important;
        box-shadow: 0 8px 15px rgba(198, 146, 20, 0.25);
        transition: all 0.3s ease;
        height: 50px;
        text-transform: uppercase;
    }
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 20px rgba(198, 146, 20, 0.35);
        background: linear-gradient(145deg, #D4A017 0%, #F5C71A 100%) !important;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(255,255,255,0.95) 0%, rgba(240, 245, 240, 0.98) 100%);
        backdrop-filter: blur(8px);
        border-right: 2px solid #C69214;
        box-shadow: 5px 0 20px rgba(0, 0, 0, 0.03);
    }
    
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #004B23 !important;
        font-family: 'Playfair Display', serif;
        border-bottom: 2px solid #C69214;
        padding-bottom: 12px;
        margin-top: 20px;
        font-weight: 700;
    }
    
    [data-testid="stSidebar"] .stSelectbox label, 
    [data-testid="stSidebar"] .stSlider label {
        font-weight: 600 !important;
        color: #1a1a1a !important;
    }

    .status-badge {
        background: rgba(0, 75, 35, 0.08);
        border: 1.5px solid #004B23;
        color: #004B23;
        padding: 14px 18px;
        border-radius: 60px;
        text-align: center;
        font-family: 'Source Sans Pro', monospace;
        font-weight: 700;
        letter-spacing: 1px;
        backdrop-filter: blur(4px);
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
    }

    .stMetric {
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(5px);
        padding: 15px 20px;
        border-radius: 20px;
        border: 1px solid rgba(0, 75, 35, 0.1);
        box-shadow: 0 5px 12px rgba(0,0,0,0.02);
    }
    .stMetric label {
        font-weight: 600 !important;
        color: #2c3e50 !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #004B23 !important;
    }

    .stDataFrame, .stTable {
        border-radius: 20px !important;
        overflow: hidden;
        box-shadow: 0 10px 25px -5px rgba(0, 75, 35, 0.08);
        border: 1px solid rgba(0,0,0,0.05);
    }
    .stDataFrame table, .stTable table {
        background-color: rgba(255, 255, 255, 0.9);
        color: #1a1a1a;
    }
    .stDataFrame th, .stTable th {
        background-color: #004B23 !important;
        color: white !important;
        font-weight: 600;
        padding: 12px 8px !important;
    }
    .stDataFrame td, .stTable td {
        border-bottom: 1px solid rgba(0,0,0,0.05) !important;
    }

    h2, h3 {
        color: #004B23 !important;
        font-family: 'Playfair Display', serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.01em;
    }
    h2 {
        border-left: 6px solid #C69214;
        padding-left: 20px;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 40px 40px 0 0 !important;
        padding: 12px 24px !important;
        background-color: rgba(255,255,255,0.4);
        border: 1px solid rgba(0,75,35,0.1);
        font-weight: 600;
        color: #2c3e50;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(145deg, #ffffff, #f0f5f0) !important;
        border-bottom: 4px solid #C69214 !important;
        color: #004B23 !important;
        font-weight: 700;
    }

    .stSelectbox > div > div {
        border-radius: 40px !important;
        border: 1px solid rgba(0,75,35,0.2) !important;
        background-color: rgba(255,255,255,0.7) !important;
    }

    .js-plotly-plot .plotly .modebar {
        background: rgba(255,255,255,0.5) !important;
        border-radius: 30px;
    }
    
    footer {visibility: hidden;}
    
</style>

<div class="rum-header">
    <div class="header-logo">
        <img src="https://www.uprm.edu/portales/wp-content/uploads/sites/55/2022/05/Tarzan_7896.png" alt="UPRM Logo">
    </div>
    <div class="title-box">
        <h1>UPRM TIMETABLE SYSTEM</h1>
        <p><span class="subtitle-accent">COLEGIO DE ARTES Y CIENCIAS</span> · OPTIMIZACIÓN ACADÉMICA v15</p>
    </div>
    <div class="header-logo">
        <img src="https://www.uprm.edu/portada/wp-content/uploads/sites/24/2023/08/logo-rum-200x200-1-150x150.png" alt="UPRM Seal">
    </div>
    <div style="width:150px;"></div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. UTILIDADES Y TABLAS DE REFERENCIA
# ==============================================================================
COMPENSACION_TABLE = [
    (1, 1, 44, 0.0), (1, 45, 74, 0.5), (1, 75, 104, 1.0), (1, 105, 134, 1.5), (1, 135, 164, 2.0),
    (2, 1, 37, 0.0), (2, 38, 52, 0.5), (2, 53, 67, 1.0), (2, 68, 82, 1.5), (2, 83, 97, 2.0),
    (2, 98, 112, 2.5), (2, 113, 127, 3.0), (2, 128, 142, 3.5), (2, 143, 147, 4.0),
    (3, 1, 34, 0.0), (3, 35, 44, 0.5), (3, 45, 54, 1.0), (3, 55, 64, 1.5), (3, 65, 74, 2.0),
    (3, 75, 84, 2.5), (3, 85, 94, 3.0), (3, 95, 104, 3.5), (3, 105, 114, 4.0), (3, 115, 124, 4.5),
    (3, 125, 134, 5.0), (3, 135, 144, 5.5), (3, 145, 154, 6.0),
    (4, 1, 33, 0.0), (4, 34, 41, 0.5), (4, 42, 48, 1.0), (4, 49, 56, 1.5), (4, 57, 63, 2.0),
    (4, 64, 71, 2.5), (4, 72, 78, 3.0), (4, 79, 86, 3.5), (4, 87, 93, 4.0), (4, 94, 101, 4.5),
    (4, 102, 108, 5.0), (4, 109, 116, 5.5), (4, 117, 123, 6.0), (4, 124, 131, 6.5), (4, 132, 138, 7.0),
    (4, 139, 146, 7.5), (4, 147, 153, 8.0),
    (5, 1, 32, 0.0), (5, 33, 38, 0.5), (5, 39, 44, 1.0), (5, 45, 50, 1.5), (5, 51, 56, 2.0),
    (5, 57, 62, 2.5), (5, 63, 68, 3.0), (5, 69, 74, 3.5), (5, 75, 80, 4.0), (5, 81, 86, 4.5),
    (5, 87, 92, 5.0), (5, 93, 98, 5.5), (5, 99, 104, 6.0), (5, 105, 110, 6.5), (5, 111, 116, 7.0),
    (5, 117, 122, 7.5), (5, 123, 128, 8.0)
]

def get_creditos_reales(creditos_base, cupo):
    for (cb, min_est, max_est, extra) in COMPENSACION_TABLE:
        if cb == creditos_base and min_est <= cupo <= max_est:
            return float(creditos_base) + extra
    max_extra = 0
    for (cb, min_est, max_est, extra) in COMPENSACION_TABLE:
        if cb == creditos_base and cupo >= min_est:
            max_extra = max(max_extra, extra)
    return float(creditos_base) + max_extra

def excel_bool(valor):
    if valor is None or pd.isna(valor):
        return False
    texto = str(valor).strip().upper()
    if texto in ('SI', 'SÍ', 'YES', 'TRUE', 'VERDADERO', '1'):
        return True
    try:
        return float(valor) == 1.0
    except:
        return False

def mins_to_str(m):
    h, mins = divmod(int(m), 60)
    am_pm = "AM" if h < 12 else "PM"
    h_disp = h if h <= 12 else h - 12
    if h_disp == 0: h_disp = 12
    return f"{h_disp:02d}:{mins:02d} {am_pm}"

def str_to_mins(valor):
    if hasattr(valor, 'hour') and hasattr(valor, 'minute'):
        return int(valor.hour) * 60 + int(valor.minute)
    if isinstance(valor, (int, float, np.integer, np.floating)) and 0 <= valor < 1:
        return int(round(float(valor) * 1440)) % 1440
    texto = str(valor).strip().upper()
    match = re.fullmatch(r"(\d{1,2}):(\d{2})(?::(\d{2}))?\s*(AM|PM)?", texto)
    if not match:
        raise ValueError(f'Hora inválida: {valor}. Usa 08:30 AM, 02:00 PM o 14:00.')
    h, m = int(match[1]), int(match[2])
    if m > 59 or (match[3] is not None and int(match[3]) != 0):
        raise ValueError(f'Hora inválida: {valor}. Usa horas y minutos completos.')
    if match[4]:
        if not 1 <= h <= 12:
            raise ValueError(f'Hora inválida: {valor}.')
        h = (h % 12) + (12 if match[4] == 'PM' else 0)
    elif h > 23:
        raise ValueError(f'Hora inválida: {valor}.')
    return h * 60 + m


def parsear_candidatos_curso(candidatos_raw):
    """Devuelve candidatos y, si hay cantidades, sus instrucciones de sección.

    (n) y (nxcupo) son cantidades fijas. Un nombre sin cantidad conserva
    cantidad=None: solo podrá cubrir demanda restante, sin asignación mínima.
    También se acepta (n sec). Los nombres se comparan en mayúsculas.
    Un profesor puede repetirse con instrucciones fijas de distintos cupos:
    "PROFESOR (1), PROFESOR (1x60)" crea una sección con CUPO y otra de 60.
    Esas instrucciones van juntas en la misma celda de CANDIDATOS.
    """
    if isinstance(candidatos_raw, list):
        partes = candidatos_raw
    elif candidatos_raw is None or pd.isna(candidatos_raw):
        partes = []
    else:
        partes = re.split(r",|\r?\n|<br\s*/?>", str(candidatos_raw), flags=re.IGNORECASE)

    candidatos = []
    asignaciones = []
    tiene_cantidades = False
    for parte in partes:
        if parte is None or pd.isna(parte):
            continue
        texto = str(parte).strip()
        if not texto or texto.upper() == "NAN":
            continue
        match = re.fullmatch(
            r"(?P<nombre>.+?)\s*\(\s*(?P<cantidad>\d+)\s*"
            r"(?:sec(?:ciones?)?\.?\s*)?"
            r"(?:[xX*×]\s*(?P<cupo>\d+)\s*)?\)",
            texto, flags=re.IGNORECASE,
        )
        if match:
            nombre = match.group("nombre").strip().upper()
            cantidad = int(match.group("cantidad"))
            cupo = int(match.group("cupo")) if match.group("cupo") is not None else None
            if cupo is not None and cupo <= 0:
                raise ValueError(f"El cupo indicado para {nombre} debe ser positivo.")
            tiene_cantidades = True
        else:
            if re.search(r"\(\s*[+-]?\d", texto):
                raise ValueError(
                    f"Cantidad o cupo inválido en CANDIDATOS: {texto}. "
                    "Usa Nombre (3), Nombre (3 sec) o Nombre (3x30)."
                )
            nombre = texto.upper()
            cantidad = None
            cupo = None
        if nombre in candidatos:
            # Varias instrucciones fijas del mismo profesor pueden tener cupos
            # diferentes. La lista de candidatos sigue sin nombres duplicados.
            anteriores = [a for a in asignaciones if a["nombre"] == nombre]
            if cantidad is None or any(a["cantidad"] is None for a in anteriores):
                raise ValueError(
                    f"Candidato repetido sin cantidades claras: {nombre}. "
                    "Para fijar dos tamaños, usa por ejemplo "
                    f"{nombre} (1), {nombre} (1x60). "
                    "Cada aparición repetida debe indicar su cantidad."
                )
        else:
            candidatos.append(nombre)
        asignaciones.append({"nombre": nombre, "cantidad": cantidad, "cupo": cupo})

    return candidatos, asignaciones if tiene_cantidades else []


PATRONES = {
    1: [
        {"name": "Lu", "days": {"Lu": 1}},
        {"name": "Ma", "days": {"Ma": 1}},
        {"name": "Mi", "days": {"Mi": 1}},
        {"name": "Ju", "days": {"Ju": 1}},
        {"name": "Vi", "days": {"Vi": 1}},
    ],
    2: [
        {"name": "Lu-Mi", "days": {"Lu": 1, "Mi": 1}},
        {"name": "Ma-Ju", "days": {"Ma": 1, "Ju": 1}},
        {"name": "Lu (Intensivo)", "days": {"Lu": 2}},
        {"name": "Ma (Intensivo)", "days": {"Ma": 2}},
        {"name": "Mi (Intensivo)", "days": {"Mi": 2}},
        {"name": "Ju (Intensivo)", "days": {"Ju": 2}},
        {"name": "Vi (Intensivo)", "days": {"Vi": 2}},
    ],
    3: [
        {"name": "Lu-Mi-Vi", "days": {"Lu": 1, "Mi": 1, "Vi": 1}},
        {"name": "Ma-Ju", "days": {"Ma": 1.5, "Ju": 1.5}},
        {"name": "Lu-Mi", "days": {"Lu": 1.5, "Mi": 1.5}},
        {"name": "Lu (Intensivo)", "days": {"Lu": 3}},
        {"name": "Ma (Intensivo)", "days": {"Ma": 3}},
        {"name": "Mi (Intensivo)", "days": {"Mi": 3}},
        {"name": "Ju (Intensivo)", "days": {"Ju": 3}},
        {"name": "Vi (Intensivo)", "days": {"Vi": 3}},
        
    ],
    4: [
        {"name": "Lu-Ma-Mi-Ju", "days": {"Lu": 1, "Ma": 1, "Mi": 1, "Ju": 1}},
        {"name": "Lu-Ma-Mi-Vi", "days": {"Lu": 1, "Ma": 1, "Mi": 1, "Vi": 1}},
        {"name": "Lu-Ma-Ju-Vi", "days": {"Lu": 1, "Ma": 1, "Ju": 1, "Vi": 1}},
        {"name": "Lu-Mi-Ju-Vi", "days": {"Lu": 1, "Mi": 1, "Ju": 1, "Vi": 1}},
        {"name": "Ma-Mi-Ju-Vi", "days": {"Ma": 1, "Mi": 1, "Ju": 1, "Vi": 1}},
        {"name": "Lu-Mi", "days": {"Lu": 2, "Mi": 2}},
        {"name": "Ma-Ju", "days": {"Ma": 2, "Ju": 2}},
        {"name": "Mi-Vi", "days": {"Mi": 2, "Vi": 2}},
    ],
    5: [
        {"name": "Lu-Ma-Mi-Ju-Vi", "days": {"Lu": 1, "Ma": 1, "Mi": 1, "Ju": 1, "Vi": 1}},
        {"name": "Lu-Ma-Mi-Vi", "days": {"Lu": 1, "Ma": 1, "Mi": 1, "Vi": 2}},
        {"name": "Lu-Ma-Ju-Vi", "days": {"Lu": 1, "Ma": 1, "Ju": 1, "Vi": 2}},
        {"name": "Lu-Mi-Ju-Vi", "days": {"Lu": 1, "Mi": 1, "Ju": 1, "Vi": 2}},
        {"name": "Ma-Mi-Ju-Vi", "days": {"Ma": 1, "Mi": 1, "Ju": 1, "Vi": 2}},
    ]
}
def format_horario(patron, h_ini):
    parts = []
    for dia, contrib in patron['days'].items():
        mins_duracion = int(contrib * 50)
        h_fin = h_ini + mins_duracion
        parts.append(f"{dia}: {mins_to_str(h_ini)}-{mins_to_str(h_fin)}")
    return " | ".join(parts)

def exportar_todo(df):
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Maestro', index=False)
        for p in df['Persona'].unique():
            if str(p) != "TBA" and str(p) != "GRADUADOS":
                clean_name = "".join([c for c in str(p) if c.isalnum() or c==' '])[:25]
                df[df['Persona'] == p].to_excel(writer, sheet_name=f"User_{clean_name}", index=False)
    return out.getvalue()

# ==============================================================================
# 3. MODELO DE DATOS (CON TIPOS DE SALÓN COMO LISTA)
# ==============================================================================
class Seccion:
    def __init__(self, cod, creditos, cupo, candidatos_raw, tipo_salon_str, es_ayudantia=False):
        self.cod = str(cod)
        self.creditos = int(creditos)
        self.cupo = int(cupo)
        
        raw_list, _ = parsear_candidatos_curso(candidatos_raw)
        self.cands = list(dict.fromkeys(raw_list))
        
        # Procesar TIPO_SALON como lista de strings (ej: "1,3" -> ['1','3'])
        if isinstance(tipo_salon_str, (int, float)):
            tipo_str = str(int(tipo_salon_str))
        else:
            tipo_str = str(tipo_salon_str).strip()
        # Reemplazar punto por coma si es necesario (por si Excel puso 1.3)
        tipo_str = tipo_str.replace('.', ',')
        self.tipos_permitidos = [t.strip() for t in tipo_str.split(',') if t.strip()]
        if not self.tipos_permitidos:
            self.tipos_permitidos = ['1']   # valor por defecto
            
        self.es_ayudantia = es_ayudantia
        base = self.cod.split('-')[0].upper().replace(" ", "")
        self.es_fusionable = base in ["MATE3171", "MATE3172", "MATE3173"]
        self.prof_preasignado = None  
        self.es_grande = self.cupo >= 65

class Profesor:
    def __init__(self, nombre, carga_min, carga_max, pref_dias, pref_horas,
                 hora_entrada, hora_salida,
                 preferencias_cursos, compensacion, acepta_grandes, cursos_intensivos=0):
        self.nombre = nombre.upper().strip()
        self.carga_min = float(carga_min) if pd.notnull(carga_min) and carga_min != '' else 0.0
        self.carga_max = float(carga_max) if pd.notnull(carga_max) and carga_max != '' else 12.0
        
        self.pref_dias_set = self._parse_pref_dias(pref_dias)
        self.pref_horas = pref_horas.strip().upper() if isinstance(pref_horas, str) and pref_horas.strip() else 'ANY'
        
        # --- NUEVO: Parseo de HORA_ENTRADA y HORA_SALIDA a minutos ---
        self.hora_entrada_min = None
        self.hora_salida_min = None
        if pd.notnull(hora_entrada) and str(hora_entrada).strip():
            try:
                self.hora_entrada_min = str_to_mins(hora_entrada)
            except (TypeError, ValueError) as exc:
                raise ValueError(f'{self.nombre}: HORA_ENTRADA inválida: {hora_entrada}') from exc
        if pd.notnull(hora_salida) and str(hora_salida).strip():
            try:
                self.hora_salida_min = str_to_mins(hora_salida)
            except (TypeError, ValueError) as exc:
                raise ValueError(f'{self.nombre}: HORA_SALIDA inválida: {hora_salida}') from exc
        
        self.preferencias = []
        if isinstance(preferencias_cursos, list):
            self.preferencias = [c.upper().strip() for c in preferencias_cursos if c and str(c).upper() != 'NAN']
            
        self.compensacion = excel_bool(compensacion)
        self.acepta_grandes = int(acepta_grandes) if pd.notnull(acepta_grandes) and acepta_grandes != '' else 0
        
        try:
            self.cursos_intensivos = int(cursos_intensivos)
        except:
            self.cursos_intensivos = 0

    def prioridad_curso(self, curso_cod):
        for idx, pref in enumerate(self.preferencias):
            if pref in curso_cod:
                return 1.0 / (idx + 1)
        return 0.0

    def _parse_pref_dias(self, pref_dias):
        if pref_dias is None or pd.isna(pref_dias):
            return set()

        texto = str(pref_dias).strip().upper()
        if not texto or texto == "NAN":
            return set()

        mapa = {
            "L": "Lu", "LU": "Lu",
            "M": "Ma", "MA": "Ma",
            "W": "Mi", "MI": "Mi",
            "J": "Ju", "JU": "Ju",
            "V": "Vi", "VI": "Vi",
        }

        dias = set()
        for token in texto.replace(",", " ").replace("-", " ").split():
            if token in mapa:
                dias.add(mapa[token])

        if not dias:
            for char in texto:
                if char in mapa:
                    dias.add(mapa[char])

        return dias

def compatible_tipo(tipos_permitidos_curso, salon_tipo):
    """Verifica si el tipo de salón (entero o float) está permitido para el curso."""
    # Normalizar el tipo del salón a string (ej: 1.0 -> '1', 2.0 -> '2', 3.0 -> '3')
    if isinstance(salon_tipo, float):
        if salon_tipo >= 2.9:
            salon_cat = '3'
        elif salon_tipo >= 1.9:
            salon_cat = '2'
        else:
            salon_cat = '1'
    else:
        salon_cat = str(int(salon_tipo))
    
    # El curso permite el salón si su categoría está en la lista de permitidos
    return salon_cat in tipos_permitidos_curso

# ==============================================================================
# 4. MOTOR DE ASIGNACIÓN Y PREFERENCIAS
# ==============================================================================
class TabuScheduler:
    """Asigna cargas y busca horarios factibles antes de mejorar preferencias."""

    def __init__(self, df_cursos, df_profes, df_salones, zona, df_grad=None, config=None):
        self.config = {'peso_dia': 300, 'peso_minuto': 10, 'peso_turno': 30,
                       'dias_obligatorios': False, 'horario_obligatorio': False,
                       'paso_minutos': 30, 'segundos': 45, 'semilla': 42}
        if config:
            self.config.update(config)
        for key in ['peso_dia', 'peso_minuto', 'peso_turno']:
            if self.config[key] < 0:
                raise ValueError('Los pesos de preferencias no pueden ser negativos.')
        if self.config['paso_minutos'] not in (15, 30):
            raise ValueError('El paso horario debe ser 15 o 30 minutos.')
        self.rng = random.Random(self.config['semilla'])
        self.zona = zona
        self.problemas_iniciales = []
        self._cache_tiempos = {}
        self._cache_salones = {}
        self._leer_datos(df_cursos.copy(), df_profes.copy(), df_salones.copy(), df_grad)
        if zona == 'CENTRAL':
            self.hora_universal = (630, 750)
            self.limite_operativo = (450, 1110)
        else:
            self.hora_universal = (600, 720)
            self.limite_operativo = (420, 1080)
        self.bloques = list(range(self.limite_operativo[0], self.limite_operativo[1],
                                 self.config['paso_minutos']))
        # Cota de TODAS las preferencias: un conflicto fuerte siempre cuesta más.
        self.peso_duro = 1 + max(1, len(self.secciones)) * (
            5 * (self.config['peso_dia'] + 2880 * self.config['peso_minuto'])
            + self.config['peso_turno'])
        self._preasignar_profesores_robusto()
        self.solucion = []
        self.mejor_solucion = []
        self.mejor_costo = 0
        self.historial_costos = []

    def _leer_datos(self, df_cursos, df_profes, df_salones, df_grad):
        # Salones
        df_salones.columns = [c.strip().upper() for c in df_salones.columns]
        self.salones = []
        self.mega_salones = set()
        for _, r in df_salones.iterrows():
            codigo = str(r['CODIGO']).strip().upper()
            try: cap = int(r['CAPACIDAD'])
            except: cap = 25
            try: tipo = float(r['TIPO'])
            except: tipo = 1.0
            self.salones.append({'CODIGO': codigo, 'CAPACIDAD': cap, 'TIPO': tipo})
            if any(x in codigo.replace(" ", "").replace("-", "") for x in ["FA", "FB", "FC"]):
                self.mega_salones.add(codigo)
        
        self.salon_tipo = {s['CODIGO']: s['TIPO'] for s in self.salones}
        self.salon_capacidad = {s['CODIGO']: s['CAPACIDAD'] for s in self.salones}

        # Profesores
        self.profesores = {}
        if df_profes is not None and not df_profes.empty:
            df_profes.columns = [c.strip().upper() for c in df_profes.columns]
            for _, r in df_profes.iterrows():
                prefs = [str(r.get(col, '')).strip().upper() for col in ['PREF1', 'PREF2', 'PREF3'] if pd.notnull(r.get(col)) and str(r.get(col)).strip().upper() != 'NAN']
                prof = Profesor(
                    nombre=str(r['NOMBRE']).strip().upper(),
                    carga_min=r.get('CARGA_MIN', 0),
                    carga_max=r.get('CARGA_MAX', 15),
                    pref_dias=r.get('PREF_DIAS', ''),
                    pref_horas=r.get('PREF_HORAS', 'ANY'),
                    hora_entrada=r.get('HORA_ENTRADA', ''),
                    hora_salida=r.get('HORA_SALIDA', ''),
                    preferencias_cursos=prefs,
                    compensacion=r.get('COMPENSACION', 'NO'),
                    acepta_grandes=r.get('ACEPTA_GRANDES', 0),
                    cursos_intensivos=r.get('CURSOS_INTENSIVOS', 0)
                )
                for column, attribute in [('DIAS_OBLIGATORIOS', 'dias_obligatorios'),
                                          ('HORARIO_OBLIGATORIO', 'horario_obligatorio')]:
                    value = r.get(column)
                    setattr(prof, attribute, None if value is None or pd.isna(value) else excel_bool(value))
                self.profesores[prof.nombre] = prof

        # Cursos y Secciones
        self.secciones = []
        df_cursos.columns = [c.strip().upper() for c in df_cursos.columns]
        cursos_agrupados = {}
        for _, r in df_cursos.iterrows():
            cod_base = str(r['CODIGO']).strip().upper()
            if cod_base not in cursos_agrupados:
                # El tipo de salón se pasa como string (ya normalizado en main)
                tipo_salon = r.get('TIPO_SALON', '1')
                cursos_agrupados[cod_base] = {
                    'creditos': int(r['CREDITOS']),
                    'demanda': int(r.get('DEMANDA', 0)),
                    'cupo_tipico': int(r.get('CUPO', '30')),
                    'candidatos': r.get('CANDIDATOS', ''),
                    'tipo_salon': tipo_salon
                }
            else:
                cursos_agrupados[cod_base]['demanda'] += int(r.get('DEMANDA', 0))

        for cod_base, datos in cursos_agrupados.items():
            demanda_total = datos['demanda']
            cupo_tipico = datos['cupo_tipico']
            if demanda_total < 0:
                raise ValueError(f"{cod_base}: DEMANDA no puede ser negativa.")
            if cupo_tipico <= 0:
                raise ValueError(f"{cod_base}: CUPO debe ser mayor que cero.")

            candidatos_list, instrucciones = parsear_candidatos_curso(datos['candidatos'])
            fijas = [a for a in instrucciones if a['cantidad'] is not None]
            libres = (
                [a['nombre'] for a in instrucciones if a['cantidad'] is None]
                if instrucciones else candidatos_list
            )
            secciones_plan = []
            plazas_fijas = 0

            # Una cantidad entre paréntesis fija únicamente esas secciones.
            # Esa persona no entra en la bolsa de secciones adicionales.
            for asignacion in fijas:
                cupo_fijo = asignacion['cupo'] if asignacion['cupo'] is not None else cupo_tipico
                for _ in range(asignacion['cantidad']):
                    secciones_plan.append((cupo_fijo, asignacion['nombre'], True))
                    plazas_fijas += cupo_fijo

            demanda_restante = max(0, demanda_total - plazas_fijas)
            if demanda_restante > 0 and not libres:
                raise ValueError(
                    f"{cod_base}: las secciones fijas cubren {plazas_fijas} plazas "
                    f"de una demanda de {demanda_total}. Faltan {demanda_restante} "
                    "plazas y no hay candidatos sin cantidad para cubrirlas. "
                    "Agrega candidatos sin paréntesis o revisa las cantidades/cupos fijos."
                )

            # Se conserva la política existente de grupos grandes, pero solo
            # entre los candidatos libres y para la demanda aún no cubierta.
            if demanda_restante > 0:
                candidatos_grandes = [
                    c for c in libres
                    if c in self.profesores
                    and self.profesores[c].acepta_grandes == 1
                    and self.profesores[c].compensacion
                ]
                if candidatos_grandes and demanda_restante >= 65:
                    cupo_grande = min(demanda_restante, 85)
                    secciones_plan.append((cupo_grande, ", ".join(candidatos_grandes), False))
                    demanda_restante -= cupo_grande

                # Toda sección adicional conserva la bolsa completa de candidatos
                # libres. El motor elige quién la dicta; nadie recibe una por defecto.
                for cupo, _ in self._dividir_demanda_normal(demanda_restante, cupo_tipico):
                    secciones_plan.append((cupo, ", ".join(libres), False))

            for i, (cupo, candidatos_seccion, es_fija) in enumerate(secciones_plan):
                seccion = Seccion(
                    f"{cod_base}-{i+1:02d}", datos['creditos'], cupo,
                    candidatos_seccion, datos['tipo_salon']
                )
                seccion.profesor_pendiente_permitido = False
                seccion.asignacion_fija = es_fija
                seccion.profesor_fijo = candidatos_seccion if es_fija else None
                self.secciones.append(seccion)

        # --- Carga de Graduados (doble rol) ---
        self.graduados_reciben = {}
        if df_grad is not None and not df_grad.empty:
            df_grad.columns = [c.strip().upper() for c in df_grad.columns]
            for _, r in df_grad.iterrows():
                nombre = str(r['NOMBRE']).strip().upper()
                recibe_str = str(r['RECIBE']) if pd.notnull(r['RECIBE']) else ''
                codigos = [c.strip().upper() for c in recibe_str.split(',') if c.strip()]
                self.graduados_reciben[nombre] = codigos


    def _dias_duros(self, p):
        value = getattr(self.profesores.get(p), 'dias_obligatorios', None)
        return self.config['dias_obligatorios'] if value is None else value

    def _horario_duro(self, p):
        value = getattr(self.profesores.get(p), 'horario_obligatorio', None)
        return self.config['horario_obligatorio'] if value is None else value

    def get_sec_creditos(self, s, prof_name):
        if prof_name in self.profesores and self.profesores[prof_name].compensacion:
            return get_creditos_reales(s.creditos, s.cupo)
        return float(s.creditos)

    def _dividir_demanda_normal(self, demanda_total, cupo_tipico):
        if demanda_total <= 0:
            return []
        if cupo_tipico <= 0:
            raise ValueError('CUPO debe ser mayor que cero.')
        llenas, resto = divmod(demanda_total, cupo_tipico)
        return [(cupo_tipico, False)] * llenas + ([(resto, False)] if resto else [])

    def _es_salon_especial(self, seccion):
        return set(seccion.tipos_permitidos) != {'1'}

    def _patrones_validos_para_profesor(self, seccion, prof):
        patrones = list(PATRONES.get(seccion.creditos, PATRONES[3]))
        p = self.profesores.get(prof)
        if not p:
            return patrones
        if self._dias_duros(prof) and p.pref_dias_set:
            patrones = [x for x in patrones if set(x['days']).issubset(p.pref_dias_set)]
        intensivo_posible = any(any(v >= 3 for v in x['days'].values())
                               for x in PATRONES.get(seccion.creditos, PATRONES[3]))
        if p.cursos_intensivos == 0:
            patrones = [x for x in patrones if not any(v >= 3 for v in x['days'].values())]
        elif p.cursos_intensivos == 1 and intensivo_posible:
            patrones = [x for x in patrones if any(v >= 3 for v in x['days'].values())]
        return patrones

    def _salones_validos_para(self, seccion, prof=None, sol=None, idx=None):
        key = (seccion.cupo, tuple(seccion.tipos_permitidos))
        if key not in self._cache_salones:
            self._cache_salones[key] = [r['CODIGO'] for r in self.salones
                if r['CAPACIDAD'] >= seccion.cupo
                and compatible_tipo(seccion.tipos_permitidos, r['TIPO'])]
        return list(self._cache_salones[key])

    @staticmethod
    def _cruzan(a, b):
        return max(a[0], b[0]) < min(a[1], b[1])

    def _preferencias_asignacion(self, a):
        p = self.profesores.get(a['profesor'])
        if not p:
            return []
        rows = []
        for dia, factor in a['patron']['days'].items():
            ini, fin = a['ini'], a['ini'] + int(factor * 50)
            if not self._dias_duros(p.nombre) and p.pref_dias_set and dia not in p.pref_dias_set:
                rows.append({'Dia': dia, 'Preferencia': 'Día', 'Deseado': ', '.join(d for d in ('Lu', 'Ma', 'Mi', 'Ju', 'Vi') if d in p.pref_dias_set),
                             'Asignado': dia, 'Minutos fuera': 0, 'Penalización': self.config['peso_dia']})
            if not self._horario_duro(p.nombre):
                if p.hora_entrada_min is not None and ini < p.hora_entrada_min:
                    minutos = p.hora_entrada_min - ini
                    rows.append({'Dia': dia, 'Preferencia': 'Entrada', 'Deseado': mins_to_str(p.hora_entrada_min),
                                 'Asignado': mins_to_str(ini), 'Minutos fuera': minutos,
                                 'Penalización': minutos * self.config['peso_minuto']})
                if p.hora_salida_min is not None and fin > p.hora_salida_min:
                    minutos = fin - p.hora_salida_min
                    rows.append({'Dia': dia, 'Preferencia': 'Salida', 'Deseado': mins_to_str(p.hora_salida_min),
                                 'Asignado': mins_to_str(fin), 'Minutos fuera': minutos,
                                 'Penalización': minutos * self.config['peso_minuto']})
        if ((p.pref_horas == 'AM' and a['ini'] >= 720)
                or (p.pref_horas == 'PM' and a['ini'] < 720)):
            rows.append({'Dia': ', '.join(a['patron']['days']), 'Preferencia': 'AM/PM',
                         'Deseado': p.pref_horas, 'Asignado': mins_to_str(a['ini']),
                         'Minutos fuera': 0, 'Penalización': self.config['peso_turno']})
        for row in rows:
            row.update({'Profesor': p.nombre, 'Sección': a['seccion'].cod})
        return rows

    def _temporales(self, s, prof):
        key = (s.creditos, prof)
        if key in self._cache_tiempos:
            return self._cache_tiempos[key]
        p = self.profesores.get(prof)
        options = []
        for patron in self._patrones_validos_para_profesor(s, prof):
            for ini in self.bloques:
                intervals = [(d, ini, ini + int(v * 50)) for d, v in patron['days'].items()]
                if any(fin > self.limite_operativo[1] for d, start, fin in intervals):
                    continue
                if any(d in ('Ma', 'Ju') and self._cruzan((start, fin), self.hora_universal)
                       for d, start, fin in intervals):
                    continue
                if s.creditos == 3 and any(v >= 3 for v in patron['days'].values()) and ini < 930:
                    continue
                if p and self._horario_duro(prof):
                    if p.hora_entrada_min is not None and ini < p.hora_entrada_min:
                        continue
                    if p.hora_salida_min is not None and any(fin > p.hora_salida_min for _, _, fin in intervals):
                        continue
                a = {'seccion': s, 'profesor': prof, 'patron': patron, 'ini': ini, 'salon': ''}
                penalty = sum(r['Penalización'] for r in self._preferencias_asignacion(a))
                options.append((patron, ini, intervals, penalty))
        self._cache_tiempos[key] = options
        return options

    def _candidatos_validos(self, s):
        result = [p for p in s.cands if p in self.profesores
                  and not (s.es_grande and self.profesores[p].acepta_grandes == 0)
                  and self._temporales(s, p) and self._salones_validos_para(s, p)]
        if not result and 'GRADUADOS' in s.cands:
            result = ['GRADUADOS']
        return result

    def _preasignar_profesores_robusto(self):
        self.candidatos_validos = {i: self._candidatos_validos(s) for i, s in enumerate(self.secciones)}
        self.asignacion_profes = {}
        if any(not c for c in self.candidatos_validos.values()):
            return
        loads = {p: 0.0 for p in self.profesores}
        homes = {p: None for p in self.profesores}
        pending = set(range(len(self.secciones)))
        nodes = 0
        limit = time.monotonic() + 8
        exhausted = False

        def opciones(i):
            sec = self.secciones[i]
            result = []
            for p in self.candidatos_validos[i]:
                if p == 'GRADUADOS':
                    result.append(p)
                    continue
                if loads[p] + self.get_sec_creditos(sec, p) > self.profesores[p].carga_max + 0.5:
                    continue
                if not self._es_salon_especial(sec) and homes[p] is not None:
                    if not homes[p].intersection(self._salones_validos_para(sec, p)):
                        continue
                result.append(p)
            return result

        def search():
            nonlocal nodes, exhausted
            nodes += 1
            if nodes > 100000 or (nodes % 100 == 0 and time.monotonic() > limit):
                exhausted = True
                return False
            if not pending:
                return all(loads[p] >= obj.carga_min - 0.5 for p, obj in self.profesores.items())
            opts = {i: opciones(i) for i in pending}
            if any(not v for v in opts.values()):
                return False
            for p, obj in self.profesores.items():
                if loads[p] >= obj.carga_min - 0.5:
                    continue
                possible = sum(self.get_sec_creditos(self.secciones[i], p) for i in pending if p in opts[i])
                if loads[p] + possible < obj.carga_min - 0.5:
                    return False
            i = min(pending, key=lambda j: (len(opts[j]), -self.secciones[j].creditos, j))
            sec = self.secciones[i]
            candidates = sorted(opts[i], key=lambda p: (
                -(max(0, self.profesores[p].carga_min - loads[p]) if p in loads else 0),
                -(self.profesores[p].prioridad_curso(sec.cod) if p in loads else 0), p))
            pending.remove(i)
            for p in candidates:
                self.asignacion_profes[i] = p
                if p in loads:
                    credits = self.get_sec_creditos(sec, p)
                    loads[p] += credits
                    old_home = homes[p]
                    if not self._es_salon_especial(sec):
                        valid = set(self._salones_validos_para(sec, p))
                        homes[p] = valid if old_home is None else old_home.intersection(valid)
                if search():
                    return True
                if p in loads:
                    loads[p] -= credits
                    homes[p] = old_home
                self.asignacion_profes.pop(i, None)
                if exhausted:
                    break
            pending.add(i)
            return False

        if not search():
            message = ('No se encontró una distribución de profesores dentro del límite de búsqueda.' if exhausted
                       else 'Las secciones y candidatos actuales no permiten cumplir conjuntamente las cargas y el salón normal común.')
            self.problemas_iniciales.append(message)
            # Diagnóstico individual, sin confundir preferencias flexibles con imposibilidad.
            for p, obj in self.profesores.items():
                forced = sum(self.get_sec_creditos(s, p) for i, s in enumerate(self.secciones)
                             if self.candidatos_validos[i] == [p])
                available = sum(self.get_sec_creditos(s, p) for i, s in enumerate(self.secciones)
                                if p in self.candidatos_validos[i])
                if forced > obj.carga_max + 0.5:
                    self.problemas_iniciales.append(f'{p}: {forced:g} créditos obligatorios; máximo {obj.carga_max:g}.')
                if available < obj.carga_min - 0.5:
                    self.problemas_iniciales.append(f'{p}: solo {available:g} créditos disponibles; mínimo {obj.carga_min:g}.')
        else:
            for i, p in self.asignacion_profes.items():
                self.secciones[i].prof_preasignado = p

    def validar_factibilidad_inicial(self):
        issues = list(self.problemas_iniciales)
        for i, s in enumerate(self.secciones):
            if self.candidatos_validos[i]:
                continue
            known = [p for p in s.cands if p in self.profesores]
            if not known:
                issues.append(f'{s.cod}: no hay candidatos que figuren en Profesores.')
            elif not self._salones_validos_para(s):
                issues.append(f'{s.cod}: no hay salón con capacidad y tipo compatibles.')
            else:
                issues.append(f'{s.cod}: revisar ACEPTA_GRANDES, intensivos y disponibilidad marcada como obligatoria.')
        return issues

    def _compatible_local(self, a, others):
        p, sec = a['profesor'], a['seccion']
        for b in others:
            same_prof = p == b['profesor'] and p not in ('TBA', 'GRADUADOS')
            role_conflict = (b['seccion'].cod.split('-')[0] in self.graduados_reciben.get(p, [])
                             or sec.cod.split('-')[0] in self.graduados_reciben.get(b['profesor'], []))
            for dia, factor in a['patron']['days'].items():
                if dia not in b['patron']['days']:
                    continue
                ia = (a['ini'], a['ini'] + int(factor * 50))
                ib = (b['ini'], b['ini'] + int(b['patron']['days'][dia] * 50))
                if self._cruzan(ia, ib):
                    if same_prof or role_conflict:
                        return False
                    if a['salon'] == b['salon'] and not (
                            a['salon'] in self.mega_salones and sec.es_fusionable and b['seccion'].es_fusionable):
                        return False
        # En salones fusionables se comprueba el cupo conjunto, no solo por parejas.
        if a['salon'] in self.mega_salones:
            for dia, factor in a['patron']['days'].items():
                start, end = a['ini'], a['ini'] + int(factor * 50)
                active = [b for b in others if b['salon'] == a['salon'] and dia in b['patron']['days']
                          and self._cruzan((start, end), (b['ini'], b['ini'] + int(b['patron']['days'][dia] * 50)))]
                points = {start} | {max(start, b['ini']) for b in active}
                for point in points:
                    total = sec.cupo + sum(b['seccion'].cupo for b in active
                        if b['ini'] <= point < b['ini'] + int(b['patron']['days'][dia] * 50))
                    if total > self.salon_capacidad[a['salon']]:
                        return False
        return True

    def _indices_profesor(self, p):
        return [i for i, assigned in self.asignacion_profes.items() if assigned == p]

    def _planificar_profesor(self, p, others, explorar=False):
        indices = self._indices_profesor(p)
        normal = [i for i in indices if not self._es_salon_especial(self.secciones[i])]
        if normal:
            common = set(self._salones_validos_para(self.secciones[normal[0]], p))
            for i in normal[1:]:
                common.intersection_update(self._salones_validos_para(self.secciones[i], p))
            room_load = {r: sum(sum(b['patron']['days'].values()) * 50 for b in others if b['salon'] == r) for r in sorted(common)}
            homes = sorted(sorted(common), key=lambda r: (self.salon_capacidad[r], room_load[r], self.rng.random()))
        else:
            homes = [None]
        if not homes:
            return None
        indices.sort(key=lambda i: (len(self._salones_validos_para(self.secciones[i], p)),
                                    len(self._temporales(self.secciones[i], p)), -self.secciones[i].creditos))
        best, best_score = None, float('inf')
        tested_homes = 0
        for home in homes:
            planned, answer = [], None
            nodes = 0
            timed_options = {}
            for i in indices:
                options = list(self._temporales(self.secciones[i], p))
                options.sort(key=lambda x: (x[3], self.rng.random()))
                timed_options[i] = options

            def place(k):
                nonlocal nodes, answer
                nodes += 1
                if nodes > 3000:
                    return False
                if k == len(indices):
                    answer = list(planned)
                    return True
                i = indices[k]
                sec = self.secciones[i]
                rooms = [home] if i in normal else self._salones_validos_para(sec, p)
                rooms = sorted(rooms, key=lambda r: (self.salon_capacidad[r], self.rng.random()))
                for patron, ini, intervals, penalty in timed_options[i]:
                    for room in rooms:
                        a = {'seccion': sec, 'profesor': p, 'salon': room, 'patron': patron, 'ini': ini}
                        if self._compatible_local(a, others + planned):
                            planned.append(a)
                            if place(k + 1):
                                return True
                            planned.pop()
                return False

            if place(0):
                score = sum(r['Penalización'] for a in answer for r in self._preferencias_asignacion(a))
                if score < best_score:
                    best, best_score = answer, score
                tested_homes += 1
                if best_score == 0 or tested_homes >= (3 if explorar else 1):
                    break
        return best

    def _construir_solucion_greedy(self, intento=0):
        people = list(dict.fromkeys(self.asignacion_profes.values()))
        def priority(p):
            ids = self._indices_profesor(p)
            scarcity = min(len(self._salones_validos_para(self.secciones[i], p)) for i in ids)
            obj = self.profesores.get(p)
            preferences = 0 if not obj else bool(obj.pref_dias_set) + (obj.hora_entrada_min is not None) + (obj.hora_salida_min is not None) + (obj.pref_horas in ('AM', 'PM'))
            return (scarcity, -preferences, -len(ids), self.rng.random() if intento else p)
        people.sort(key=priority)
        placed = []
        for p in people:
            plan = self._planificar_profesor(p, placed)
            if plan is None:
                # Devolver el borrador con sus conflictos reales, nunca declararlo factible.
                for i in self._indices_profesor(p):
                    sec = self.secciones[i]
                    temporal = self._temporales(sec, p)[0]
                    placed.append({'seccion': sec, 'profesor': p, 'patron': temporal[0],
                                   'ini': temporal[1], 'salon': self._salones_validos_para(sec, p)[0]})
            else:
                placed.extend(plan)
        by_code = {a['seccion'].cod: a for a in placed}
        return [by_code[s.cod] for s in self.secciones]

    def _obtener_conflictos(self, sol, evaluar_carga_min=True):
        events = []
        loads = {p: 0.0 for p in self.profesores}
        codes = [a['seccion'].cod for a in sol]
        for sec in self.secciones:
            if codes.count(sec.cod) != 1:
                events.append(f'{sec.cod}: debe tener exactamente una asignación.')
        homes = {}
        for i, a in enumerate(sol):
            sec, p, room, pattern, start = a['seccion'], a['profesor'], a['salon'], a['patron'], a['ini']
            if p not in sec.cands or (p not in self.profesores and p != 'GRADUADOS'):
                events.append(f'{sec.cod}: profesor no permitido: {p}.')
            if room not in self._salones_validos_para(sec, p):
                events.append(f'{sec.cod}: salón sin capacidad o tipo compatible: {room}.')
            obj = self.profesores.get(p)
            if obj:
                loads[p] += self.get_sec_creditos(sec, p)
                if sec.es_grande and obj.acepta_grandes == 0:
                    events.append(f'{sec.cod}: {p} no acepta secciones grandes.')
                if pattern not in self._patrones_validos_para_profesor(sec, p):
                    events.append(f'{sec.cod}: patrón incompatible con intensivos o días obligatorios de {p}.')
                if not self._es_salon_especial(sec):
                    homes.setdefault(p, set()).add(room)
            for day, factor in pattern['days'].items():
                end = start + int(factor * 50)
                if start < self.limite_operativo[0] or end > self.limite_operativo[1]:
                    events.append(f'{sec.cod}: fuera de la ventana operativa en {day}.')
                if day in ('Ma', 'Ju') and self._cruzan((start, end), self.hora_universal):
                    events.append(f'{sec.cod}: hora universal en {day}.')
                if sec.creditos == 3 and factor >= 3 and start < 930:
                    events.append(f'{sec.cod}: intensivo anterior a las 15:30 en {day}.')
                if obj and self._horario_duro(p):
                    if obj.hora_entrada_min is not None and start < obj.hora_entrada_min:
                        events.append(f'{sec.cod}: antes de la entrada obligatoria en {day}.')
                    if obj.hora_salida_min is not None and end > obj.hora_salida_min:
                        events.append(f'{sec.cod}: después de la salida obligatoria en {day}.')
            for b in sol[:i]:
                for day in set(pattern['days']).intersection(b['patron']['days']):
                    end = start + int(pattern['days'][day] * 50)
                    other_end = b['ini'] + int(b['patron']['days'][day] * 50)
                    if not self._cruzan((start, end), (b['ini'], other_end)):
                        continue
                    if p == b['profesor'] and p not in ('TBA', 'GRADUADOS'):
                        events.append(f'Cruce de profesor {p}: {sec.cod} y {b["seccion"].cod}, {day}.')
                    if room == b['salon'] and not (room in self.mega_salones and sec.es_fusionable and b['seccion'].es_fusionable):
                        events.append(f'Cruce de salón {room}: {sec.cod} y {b["seccion"].cod}, {day}.')
                    if (b['seccion'].cod.split('-')[0] in self.graduados_reciben.get(p, [])
                            or sec.cod.split('-')[0] in self.graduados_reciben.get(b['profesor'], [])):
                        events.append(f'Doble rol: {sec.cod} y {b["seccion"].cod}, {day}.')
        for p, rooms in homes.items():
            if len(rooms) > 1:
                events.append(f'{p}: usa varios salones normales: {sorted(rooms)}.')
        for p, load in loads.items():
            obj = self.profesores[p]
            if load > obj.carga_max + 0.5:
                events.append(f'{p}: carga {load:g} superior al máximo {obj.carga_max:g}.')
            if evaluar_carga_min and load < obj.carga_min - 0.5:
                events.append(f'{p}: carga {load:g} inferior al mínimo {obj.carga_min:g}.')
        for room in self.mega_salones:
            for day in ('Lu', 'Ma', 'Mi', 'Ju', 'Vi'):
                assignments = [a for a in sol if a['salon'] == room and day in a['patron']['days']]
                for point in sorted(set(a['ini'] for a in assignments)):
                    active = [a for a in assignments if a['ini'] <= point < a['ini'] + int(a['patron']['days'][day] * 50)]
                    if sum(a['seccion'].cupo for a in active) > self.salon_capacidad[room]:
                        events.append(f'{room}: cupo conjunto excedido en {day}, {mins_to_str(point)}.')
        return events

    def _obtener_preferencias_incumplidas(self, sol):
        return [r for a in sol for r in self._preferencias_asignacion(a)]

    def _resumen_preferencias(self, sol):
        relevant = set()
        checks = 0
        for a in sol:
            p = self.profesores.get(a['profesor'])
            if not p:
                continue
            n = len(a['patron']['days'])
            current = int(p.pref_horas in ('AM', 'PM'))
            if not self._dias_duros(p.nombre) and p.pref_dias_set:
                current += n
            if not self._horario_duro(p.nombre):
                current += n * ((p.hora_entrada_min is not None) + (p.hora_salida_min is not None))
            if current:
                relevant.add(a['seccion'].cod)
                checks += current
        rows = self._obtener_preferencias_incumplidas(sol)
        bad = {r['Sección'] for r in rows}
        return {'secciones_con_preferencias': len(relevant),
                'secciones_todas_cumplidas': len(relevant - bad),
                'comprobaciones': checks, 'comprobaciones_cumplidas': checks - len(rows),
                'incumplimientos': len(rows), 'penalizacion': sum(r['Penalización'] for r in rows)}

    def _costo_total(self, sol, solo_duros=False, evaluar_carga_min=True):
        hard = len(self._obtener_conflictos(sol, evaluar_carga_min))
        if solo_duros:
            return hard * 10000
        soft = sum(r['Penalización'] for r in self._obtener_preferencias_incumplidas(sol))
        if soft >= self.peso_duro:
            raise AssertionError('El costo suave excedió su cota de prioridad.')
        return hard * self.peso_duro + soft

    def optimizar(self, iteraciones=3000, bar=None, status_text=None):
        issues = self.validar_factibilidad_inicial()
        if issues:
            raise ValueError('\n'.join(issues))
        self.historial_costos = []
        self.mejor_costo = float('inf')
        for attempt in range(min(25, max(5, iteraciones // 100))):
            sol = self._construir_solucion_greedy(attempt)
            cost = self._costo_total(sol)
            if cost < self.mejor_costo:
                self.mejor_solucion, self.mejor_costo = sol, cost
            self.historial_costos.append(self.mejor_costo)
            hard = len(self._obtener_conflictos(self.mejor_solucion))
            if status_text:
                status_text.markdown(f'**Construcción {attempt+1}** · Conflictos fuertes: {hard}')
            if bar:
                bar.progress(min(0.25, (attempt + 1) / 100))
            if hard == 0:
                break
        self.solucion = list(self.mejor_solucion)
        if not self._obtener_conflictos(self.solucion):
            deadline = time.monotonic() + self.config['segundos']
            current_cost = self.mejor_costo
            people = list(dict.fromkeys(self.asignacion_profes.values()))
            for it in range(iteraciones):
                if time.monotonic() > deadline or self.mejor_costo == 0:
                    break
                soft_rows = self._obtener_preferencias_incumplidas(self.solucion)
                bad = list(dict.fromkeys(r['Profesor'] for r in soft_rows))
                first = self.rng.choice(bad if bad and self.rng.random() < 0.85 else people)
                chosen = [first]
                if len(people) > 1 and self.rng.random() < 0.25:
                    chosen.append(self.rng.choice([p for p in people if p != first]))
                candidate = [a for a in self.solucion if a['profesor'] not in chosen]
                valid = True
                for p in chosen:
                    plan = self._planificar_profesor(p, candidate, explorar=True)
                    if plan is None:
                        valid = False
                        break
                    candidate.extend(plan)
                if valid:
                    by_code = {a['seccion'].cod: a for a in candidate}
                    candidate = [by_code[s.cod] for s in self.secciones]
                    cost = self._costo_total(candidate)
                    # La búsqueda de preferencias nunca acepta un conflicto fuerte.
                    if cost < self.peso_duro:
                        temp = max(1, 80 * (1 - it / max(1, iteraciones)))
                        if cost <= current_cost or self.rng.random() < math.exp(max(-700, (current_cost - cost) / temp)):
                            self.solucion, current_cost = candidate, cost
                        if cost < self.mejor_costo:
                            self.mejor_solucion, self.mejor_costo = list(candidate), cost
                self.historial_costos.append(self.mejor_costo)
                if it % 10 == 0:
                    if status_text:
                        rows = self._obtener_preferencias_incumplidas(self.mejor_solucion)
                        status_text.markdown(f'**Mejorando preferencias** · Conflictos fuertes: 0 · '
                                             f'Incumplimientos: {len(rows)} · Penalización: {self.mejor_costo:g}')
                    if bar:
                        bar.progress(0.25 + 0.74 * min(1, it / max(1, iteraciones)))
        self.solucion = list(self.mejor_solucion)
        self.mejor_costo = self._costo_total(self.mejor_solucion)
        if bar:
            bar.progress(1.0)
        return self.mejor_solucion, len(self._obtener_conflictos(self.mejor_solucion)), self.historial_costos



# ==============================================================================
# 5. FUNCIONES DE VISUALIZACIÓN
# ==============================================================================
def generar_heatmap_plotly(scheduler, solucion):
    dias_semana = ['Lu', 'Ma', 'Mi', 'Ju', 'Vi']
    inicio = scheduler.limite_operativo[0]
    fin = scheduler.limite_operativo[1]
    horas_del_dia = list(range(inicio, fin + 1, 30))
    
    matriz = np.zeros((len(horas_del_dia), len(dias_semana)))
    total_salones = len(scheduler.salones)
    
    for asign in solucion:
        salon = asign['salon']
        if salon == "TBA":
            continue
        patron = asign['patron']
        ini = asign['ini']
        for dia, contrib in patron['days'].items():
            if dia not in dias_semana:
                continue
            dia_idx = dias_semana.index(dia)
            duracion = int(contrib * 50)
            for hora_idx, minuto in enumerate(horas_del_dia):
                if max(minuto, ini) < min(minuto + 30, ini + duracion):
                    matriz[hora_idx, dia_idx] += 1
    
    if total_salones > 0:
        matriz_porcentaje = (matriz / total_salones) * 100
    else:
        matriz_porcentaje = matriz
    
    etiquetas_horas = [mins_to_str(h).replace(' AM', '').replace(' PM', '') for h in horas_del_dia]
    
    fig = px.imshow(
        matriz_porcentaje,
        labels=dict(x="Día", y="Hora de Inicio", color="% Ocupación"),
        x=dias_semana,
        y=etiquetas_horas,
        color_continuous_scale='YlOrRd',
        aspect='auto',
        zmin=0,
        zmax=100
    )
    fig.update_layout(
        title="Ocupación de Salones por Día y Hora",
        font=dict(color='#000000'),
        paper_bgcolor='white',
        plot_bgcolor='white',
        height=600
    )
    return fig

def generar_barras_apiladas_profesor(sol, scheduler):
    df_asign = pd.DataFrame([{
        'Profesor': a['profesor'],
        'Dia': dia,
        'Cantidad': 1
    } for a in sol if a['profesor'] not in ['TBA', 'GRADUADOS']
      for dia in a['patron']['days'].keys()])
    
    if df_asign.empty:
        return go.Figure()
    
    pivot = df_asign.groupby(['Profesor', 'Dia']).size().reset_index(name='Clases')
    carga_prof = {p: 0.0 for p in pivot['Profesor'].unique()}
    for a in sol:
        if a['profesor'] in carga_prof:
            carga_prof[a['profesor']] += scheduler.get_sec_creditos(a['seccion'], a['profesor'])
    profes_ordenados = sorted(carga_prof.keys(), key=lambda x: carga_prof[x], reverse=True)
    
    fig = go.Figure()
    dias_unicos = ['Lu', 'Ma', 'Mi', 'Ju', 'Vi']
    colores = px.colors.qualitative.Set2[:len(dias_unicos)]
    
    for i, dia in enumerate(dias_unicos):
        data_dia = pivot[pivot['Dia'] == dia]
        y_vals = [data_dia[data_dia['Profesor'] == p]['Clases'].sum() if p in data_dia['Profesor'].values else 0 for p in profes_ordenados]
        fig.add_trace(go.Bar(
            name=dia,
            x=profes_ordenados,
            y=y_vals,
            marker_color=colores[i]
        ))
    
    fig.update_layout(
        barmode='stack',
        title="Distribución de Clases por Profesor y Día",
        xaxis_title="Profesor",
        yaxis_title="Número de Clases",
        font=dict(color='#1a1a1a'),
        paper_bgcolor='white',
        plot_bgcolor='white',
        legend_title="Día",
        height=500
    )
    return fig

def generar_evolucion_fitness_plotly(historial):
    fitness = [10000 / (10000 + c) for c in historial]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=fitness,
        mode='lines+markers',
        line=dict(color='#D4AF37', width=3),
        marker=dict(size=4, color='#8E6E13'),
        fill='tozeroy',
        fillcolor='rgba(212, 175, 55, 0.2)',
        name='Fitness'
    ))
    fig.update_layout(
        title="Evolución del Fitness durante la Optimización",
        xaxis_title="Iteración",
        yaxis_title="Fitness (1.0 = Óptimo)",
        font=dict(color='#1a1a1a', size=12),
        paper_bgcolor='white',
        plot_bgcolor='white',
        height=450,
        hovermode='x unified'
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    return fig

def generar_calendario_visual(solucion, scheduler, filtro_prof=None, filtro_salon=None, filtro_curso=None):
    fig = go.Figure()
    dias_semana = ['Lu', 'Ma', 'Mi', 'Ju', 'Vi']
    nombres_dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
    
    # Colores Premium
    COLOR_FONDO_TARJETA = 'rgba(232, 245, 233, 0.95)'
    COLOR_BORDE_IZQ = '#2e7d32'
    
    # 1. Identificar si es Vista Global (Muchos datos) o Individual (Filtros)
    # Se considera global si no hay filtros activos
    es_vista_global = (filtro_prof is None or filtro_prof == 'Todos') and \
                      (filtro_salon is None or filtro_salon == 'Todos') and \
                      (filtro_curso is None or filtro_curso == 'Todos')

    # 2. Filtrar datos
    asignaciones_validas = []
    mapa_densidad = {} # Para el modo rápido

    for asign in solucion:
        if filtro_prof and filtro_prof != 'Todos' and asign['profesor'] != filtro_prof: continue
        if filtro_salon and filtro_salon != 'Todos' and asign['salon'] != filtro_salon: continue
        if filtro_curso and filtro_curso != 'Todos' and not asign['seccion'].cod.startswith(filtro_curso): continue
        
        asignaciones_validas.append(asign)
        
        # Llenar mapa de densidad para la vista rápida
        for dia_abr in asign['patron']['days']:
            if dia_abr in dias_semana:
                key = (dia_abr, asign['ini'])
                if key not in mapa_densidad: mapa_densidad[key] = []
                mapa_densidad[key].append(f"<b>{asign['seccion'].cod}</b> ({asign['salon']})")

    # --- MODO A: VISTA GLOBAL (MAPA DE CALOR) -> ULTRA RÁPIDO ---
    if es_vista_global and len(asignaciones_validas) > 40:
        for (dia_abr, h_ini_mins), cursos in mapa_densidad.items():
            dia_idx = dias_semana.index(dia_abr)
            y_pos = h_ini_mins / 60
            cantidad = len(cursos)
            
            intensidad = min(cantidad / 12, 1.0) 
            color_resalte = f'rgba(46, 125, 50, {0.2 + (intensidad * 0.8)})'

            fig.add_trace(go.Scatter(
                x=[dia_idx], y=[y_pos + 0.4],
                mode="markers+text",
                marker=dict(symbol="square", size=45, color=color_resalte, line=dict(width=1, color="white")),
                text=str(cantidad),
                textfont=dict(color="white" if intensidad > 0.4 else "black", size=13, family="Arial Black"),
                hoverinfo="text",
                hovertext=f"<b>{dia_abr} {mins_to_str(h_ini_mins)}</b><br>Cursos: {cantidad}<br><br>" + "<br>".join(cursos[:15]),
                showlegend=False
            ))

    # --- MODO B: VISTA INDIVIDUAL (TARJETAS PREMIUM) -> ESTÉTICA FOTO ---
    else:
        dias_individual = ['Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sa']
        nombres_individual = ['(L) Lunes', '(K) Martes', '(M) Miercoles', '(J) Jueves', '(V) Viernes', '(S) Sabado']
        grid_minutes = scheduler.config['paso_minutos']
        slot_starts = list(scheduler.bloques)
        if not slot_starts:
            slot_starts = list(range(scheduler.limite_operativo[0], scheduler.limite_operativo[1], 60))
        primer_slot = min(slot_starts)
        ultimo_slot = max(slot_starts)
        hora_inicio = primer_slot / 60
        hora_fin = scheduler.limite_operativo[1] / 60
        color_header = '#0f6f3a'
        color_header_2 = '#138044'
        color_celda = '#e9e9e9'
        color_linea = '#ffffff'
        color_clase = 'rgba(34, 139, 76, 0.92)'
        color_clase_borde = '#064f28'

        fig.add_shape(type="rect", x0=0, x1=1, y0=hora_inicio - 0.95, y1=hora_inicio,
                      fillcolor=color_header, line=dict(color=color_linea, width=2))
        fig.add_annotation(x=0.5, y=hora_inicio - 0.48, text="<b>Horas</b>",
                           showarrow=False, font=dict(color="white", size=14))
        for idx, nombre_dia in enumerate(nombres_individual):
            x0 = idx + 1
            fig.add_shape(type="rect", x0=x0, x1=x0 + 1, y0=hora_inicio - 0.95, y1=hora_inicio,
                          fillcolor=color_header, line=dict(color=color_linea, width=2))
            fig.add_annotation(x=x0 + 0.5, y=hora_inicio - 0.48, text=f"<b>{nombre_dia}</b>",
                               showarrow=False, font=dict(color="white", size=14))
        for inicio_mins in slot_starts:
            y0 = inicio_mins / 60
            y1 = (inicio_mins + grid_minutes) / 60
            fig.add_shape(type="rect", x0=0, x1=1, y0=y0, y1=y1,
                          fillcolor=color_header_2, line=dict(color=color_linea, width=2))
            fig.add_annotation(x=0.5, y=(y0 + y1) / 2, text=f"{mins_to_str(inicio_mins).replace(' AM', '').replace(' PM', '')} - {mins_to_str(inicio_mins + grid_minutes).replace(' AM', '').replace(' PM', '')}",
                               showarrow=False, font=dict(color="white", size=13))
            for dia_idx in range(len(dias_individual)):
                fig.add_shape(type="rect", x0=dia_idx + 1, x1=dia_idx + 2, y0=y0, y1=y1,
                              fillcolor=color_celda, line=dict(color=color_linea, width=2))

        posiciones_ocupadas_grid = {}
        for asign in asignaciones_validas:
            sec = asign['seccion']
            prof_nombre = asign['profesor']
            salon_nombre = asign['salon']
            patron = asign['patron']
            h_ini_mins = asign['ini']
            for dia_abr, duracion_bloques in patron['days'].items():
                if dia_abr not in dias_individual:
                    continue
                dia_idx = dias_individual.index(dia_abr)
                y_ini = h_ini_mins / 60
                y_fin = (h_ini_mins + int(duracion_bloques * 50)) / 60
                if y_fin <= hora_inicio or y_ini >= hora_fin:
                    continue
                key = (dia_abr, h_ini_mins)
                offset = posiciones_ocupadas_grid.get(key, 0)
                posiciones_ocupadas_grid[key] = offset + 1
                total_en_franja = sum(1 for a in asignaciones_validas if a['ini'] == h_ini_mins and dia_abr in a['patron']['days'])
                ancho = 0.94 / max(total_en_franja, 1)
                x0 = dia_idx + 1.03 + (offset * ancho)
                x1 = x0 + ancho - 0.02
                texto = (
                    f"<b>{sec.cod}</b><br>"
                    f"{salon_nombre}<br>{prof_nombre}"
                )
                fig.add_shape(type="rect", x0=x0, x1=x1, y0=y_ini + 0.03, y1=y_fin - 0.03,
                              fillcolor=color_clase, line=dict(color=color_clase_borde, width=2))
                fig.add_annotation(x=(x0 + x1) / 2, y=(y_ini + y_fin) / 2, text=texto,
                                   showarrow=False, align="center",
                                   font=dict(color="white", size=10))
                if int(duracion_bloques * 50) > 50:
                    fig.add_shape(type="line", x0=x0, x1=x1, y0=y_fin - 0.03, y1=y_fin - 0.03,
                                  line=dict(color="#ffffff", width=3))
                    fig.add_annotation(
                        x=(x0 + x1) / 2,
                        y=y_fin - 0.09,
                        text=f"fin {mins_to_str(int(y_fin * 60)).replace(' AM', '').replace(' PM', '')}",
                        showarrow=False,
                        align="center",
                        font=dict(color="white", size=9)
                    )
        fig.update_layout(
            xaxis=dict(range=[0, 7], visible=False, fixedrange=True),
            yaxis=dict(range=[hora_fin, hora_inicio - 0.95], visible=False, fixedrange=True),
            margin=dict(l=10, r=10, t=20, b=10),
            height=max(760, len(slot_starts) * 24 + 80),
            plot_bgcolor='white',
            paper_bgcolor='white',
            hoverlabel=dict(bgcolor="white", font_size=12),
            showlegend=False
        )
        return fig

        posiciones_ocupadas = {}
        for asign in asignaciones_validas:
            sec = asign['seccion']
            prof_nombre = asign['profesor']
            salon_nombre = asign['salon']
            patron = asign['patron']
            h_ini_mins = asign['ini']

            for dia_abr, duracion_bloques in patron['days'].items():
                if dia_abr not in dias_semana: continue
                dia_idx = dias_semana.index(dia_abr)
                
                # Gestión de colisiones por si hay solapes leves
                key = (dia_abr, h_ini_mins)
                offset = posiciones_ocupadas.get(key, 0)
                posiciones_ocupadas[key] = offset + 1
                
                total_en_franja = sum(1 for a in asignaciones_validas if a['ini'] == h_ini_mins and dia_abr in a['patron']['days'])
                ancho_card = 0.9 / max(total_en_franja, 1)
                x_start = (dia_idx - 0.45) + (offset * ancho_card)
                x_end = x_start + ancho_card

                y_ini = h_ini_mins / 60
                y_fin = (h_ini_mins + int(duracion_bloques * 50)) / 60

                # Dibujar Tarjeta
                fig.add_shape(type="rect", x0=x_start, x1=x_end, y0=y_ini, y1=y_fin,
                              fillcolor=COLOR_FONDO_TARJETA, line=dict(color="#c8e6c9", width=0.5))

                # Borde Verde Izquierdo
                borde_w = (x_end - x_start) * 0.12
                fig.add_shape(type="rect", x0=x_start, x1=x_start + borde_w, y0=y_ini, y1=y_fin,
                              fillcolor=COLOR_BORDE_IZQ, line=dict(width=0))

                # Texto detallado (como la foto)
                hora_label = f"{mins_to_str(h_ini_mins)} - {mins_to_str(int(y_fin*60))}"
                fig.add_annotation(
                    x=x_start + borde_w + 0.02, y=y_ini,
                    text=f"<b>{sec.cod}</b><br><span style='font-size:10px;'>🕒 {hora_label}<br>📍 {salon_nombre}<br>👤 {prof_nombre}</span>",
                    showarrow=False, xanchor="left", yanchor="top", align="left",
                    font=dict(size=11), yshift=-5
                )

    # Configuración de Layout común
    fig.update_layout(
        xaxis=dict(tickmode='array', tickvals=list(range(5)), ticktext=nombres_dias, side='top', range=[-0.6, 4.6]),
        yaxis=dict(range=[20, 7], tickvals=list(range(7, 21)), gridcolor="#f0f0f0", fixedrange=True),
        margin=dict(l=50, r=20, t=50, b=20),
        height=850,
        plot_bgcolor='white',
        hoverlabel=dict(bgcolor="white", font_size=12)
    )
    
    return fig

def generar_reporte_pdf_html(scheduler, sol, cargas_finales, master_df):
    total_secciones = len(sol)
    secciones_tba = sum(1 for a in sol if a['profesor'] == 'TBA')
    carga_total = sum(cargas_finales.values())
    profesores_con_carga = len([c for c in cargas_finales.values() if c > 0])
    
    html = f"""
    <html>
    <head>
        <title>Reporte Ejecutivo - UPRM Scheduler</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; background: white; color: #1a1a1a; }}
            h1 {{ color: #1a1a1a; border-bottom: 2px solid #D4AF37; padding-bottom: 10px; }}
            h2 {{ color: #1a1a1a; margin-top: 30px; }}
            .stats {{ display: flex; gap: 20px; margin-bottom: 30px; }}
            .stat-card {{ background: #f8f9fa; border: 1px solid #ddd; border-radius: 8px; padding: 15px; flex: 1; }}
            table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .footer {{ margin-top: 40px; font-size: 0.9em; color: #666; text-align: center; }}
        </style>
    </head>
    <body>
        <h1>UPRM Scheduler - Reporte Ejecutivo</h1>
        <p>Generado el: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="stats">
            <div class="stat-card">
                <h3>Total Secciones</h3>
                <p style="font-size: 24px; font-weight: bold;">{total_secciones}</p>
            </div>
            <div class="stat-card">
                <h3>Secciones TBA</h3>
                <p style="font-size: 24px; font-weight: bold;">{secciones_tba} ({secciones_tba/total_secciones*100:.1f}%)</p>
            </div>
            <div class="stat-card">
                <h3>Carga Total (Créditos)</h3>
                <p style="font-size: 24px; font-weight: bold;">{carga_total:.1f}</p>
            </div>
            <div class="stat-card">
                <h3>Profesores Activos</h3>
                <p style="font-size: 24px; font-weight: bold;">{profesores_con_carga}</p>
            </div>
        </div>
        
        <h2>Listado de Secciones TBA (Contrataciones Pendientes)</h2>
        {master_df[master_df['Persona'] == 'TBA'][['ID', 'Asignatura', 'Estudiantes (Cupo)', 'Días', 'Horario', 'Salón']].to_html(index=False) if secciones_tba > 0 else '<p>No hay secciones TBA.</p>'}
        
        <h2>Horarios por Profesor</h2>
        {''.join([f'<h3>{p}</h3>{master_df[master_df["Persona"]==p][["ID", "Asignatura", "Días", "Horario", "Salón"]].to_html(index=False)}' for p in sorted(master_df['Persona'].unique()) if p not in ['TBA', 'GRADUADOS']])}
        
        <div class="footer">
            Reporte generado automáticamente por UPRM Timetable System.
        </div>
        <script>
            window.onload = function() {{ window.print(); }}
        </script>
    </body>
    </html>
    """
    return html

def generar_figura_cientifica_carga(cargas_finales, scheduler):
    profesores = list(cargas_finales.keys())
    profesores.sort(key=lambda p: cargas_finales[p], reverse=True)
    carga_asignada = [cargas_finales[p] for p in profesores]
    carga_min = [scheduler.profesores[p].carga_min for p in profesores]
    carga_max = [scheduler.profesores[p].carga_max for p in profesores]
    
    x_vals = list(range(len(profesores)))
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=x_vals,
        y=carga_asignada,
        name='Carga Asignada',
        marker=dict(color='lightgray', line=dict(color='black', width=1))
    ))
    fig.add_trace(go.Scatter(
        x=x_vals,
        y=carga_min,
        mode='lines+markers',
        name='Carga Mínima',
        line=dict(color='blue', width=2, dash='dot'),
        marker=dict(size=6)
    ))
    fig.add_trace(go.Scatter(
        x=x_vals,
        y=carga_max,
        mode='lines+markers',
        name='Carga Máxima',
        line=dict(color='orange', width=2, dash='dot'),
        marker=dict(size=6)
    ))
    fig.update_layout(
        title="Análisis de Carga Académica por Profesor",
        xaxis=dict(
            title="Profesores (índice)",
            tickvals=x_vals,
            ticktext=[f"P{i+1}" for i in x_vals]
        ),
        yaxis=dict(title="Cantidad de Créditos Semanales"),
        font=dict(color='#1a1a1a'),
        paper_bgcolor='white',
        plot_bgcolor='white',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
        height=500
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    return fig

def generar_plantilla():
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        pd.DataFrame({
            'CODIGO': ['MATE3171', 'MATE3172', 'MATE4999'],
            'CREDITOS': [3, 3, 3], 'DEMANDA': [120, 120, 90], 'CUPO': [30, 30, 30],
            'CANDIDATOS': ['PEREZ (2), GONZALEZ', 'RODRIGUEZ (2), PEREZ',
                           'GONZALEZ (1x60), RODRIGUEZ (1)'],
            'TIPO_SALON': ['1', '1', '1,3']
        }).to_excel(writer, sheet_name='Cursos', index=False)
        pd.DataFrame({
            'NOMBRE': ['PEREZ', 'GONZALEZ', 'RODRIGUEZ'],
            'CARGA_MIN': [12, 10.5, 9], 'CARGA_MAX': [12, 10.5, 9],
            'PREF_DIAS': ['LWV', 'MJ', ''], 'PREF_HORAS': ['AM', 'PM', 'ANY'],
            'HORA_ENTRADA': ['08:00 AM', '12:00 PM', ''],
            'HORA_SALIDA': ['02:00 PM', '05:30 PM', ''],
            'PREF1': ['MATE3171', 'MATE4999', 'MATE3172'], 'PREF2': ['', '', ''], 'PREF3': ['', '', ''],
            'COMPENSACION': [0, 1, 0], 'ACEPTA_GRANDES': [0, 0, 0], 'CURSOS_INTENSIVOS': [0, 0, 0]
        }).to_excel(writer, sheet_name='Profesores', index=False)
        pd.DataFrame({'CODIGO': ['S-101', 'S-102', 'FA'], 'CAPACIDAD': [30, 40, 150],
                      'TIPO': [1, 1, 3]}).to_excel(writer, sheet_name='Salones', index=False)
        pd.DataFrame(columns=['NOMBRE', 'RECIBE']).to_excel(writer, sheet_name='Graduados', index=False)
    return output.getvalue()


# ==============================================================================
# 8. UI PRINCIPAL
# ==============================================================================
def main():
    with st.sidebar:
        st.markdown("### ∑ Configuración")
        zona = st.selectbox("Zona Campus", ["CENTRAL", "PERIFERICA"])
        iteraciones = st.slider("Intentos de mejora de preferencias", 100, 5000, 1500)
        with st.expander("Preferencias y búsqueda", expanded=True):
            dias_obligatorios = st.checkbox("PREF_DIAS obligatorio para todos", value=False)
            horario_obligatorio = st.checkbox("Entrada y salida obligatorias para todos", value=False)
            peso_dia = st.number_input("Peso por sesión fuera de los días preferidos", min_value=0, value=300, step=50)
            peso_minuto = st.number_input("Peso por minuto fuera de entrada/salida", min_value=0, value=10, step=1)
            peso_turno = st.number_input("Peso por sección fuera de AM/PM", min_value=0, value=30, step=10)
            paso = st.selectbox("Paso de inicio de clases (minutos)", [30, 15])
            segundos = st.slider("Tiempo máximo para mejorar preferencias (segundos)", 5, 180, 45)
            semilla = st.number_input("Semilla de búsqueda", min_value=0, value=42, step=1)
            st.caption("Los días y las horas son preferencias flexibles por defecto. Los conflictos fuertes siempre tienen prioridad.")
        config = dict(peso_dia=peso_dia, peso_minuto=peso_minuto, peso_turno=peso_turno,
                      dias_obligatorios=dias_obligatorios, horario_obligatorio=horario_obligatorio,
                      paso_minutos=paso, segundos=segundos, semilla=semilla)
        file = st.file_uploader("Subir Protocolo Excel", type=['xlsx'])
        st.download_button(
            label="📥 Descargar Plantilla",
            data=generar_plantilla(),
            file_name="PLANTILLA.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    st.markdown(f"### Ω Condiciones de Zona: {zona}")
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Ventana Operativa", "07:30 AM - 06:30 PM" if zona == "CENTRAL" else "07:00 AM - 06:00 PM")
    with c2: st.metric("Hora Universal", "10:30 AM - 12:30 PM" if zona == "CENTRAL" else "10:00 AM - 12:00 PM")
    with c3: st.markdown(f"""<div class="status-badge">CONDICIONES OBLIGATORIAS Y PREFERENCIAS</div>""", unsafe_allow_html=True)

    if not file:
        st.markdown("""
            <div class='glass-card' style='text-align: center;'>
                <h3 style='margin-top:0; color: #D4AF37;'>📥 Sincronización de Datos</h3>
                <p>Asegúrese de que el archivo Excel contiene las hojas: <b>Cursos</b>, <b>Profesores</b>, <b>Salones</b>.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        if st.button("🚀 GENERAR HORARIO"):
            try:
                with st.spinner("Balanceando cargas, consolidando secciones y resolviendo..."):
                    xls = pd.ExcelFile(file)
                    df_cursos = pd.read_excel(xls, 'Cursos')
                    # Normalizar TIPO_SALON: convertir a string y reemplazar punto por coma
                    df_cursos['TIPO_SALON'] = df_cursos['TIPO_SALON'].astype(str).str.replace('.', ',', regex=False)
                    
                    df_profes = pd.read_excel(xls, 'Profesores')
                    df_salones = pd.read_excel(xls, 'Salones')
                    
                    # Leer hoja Graduados si existe
                    df_grad = None
                    if 'Graduados' in xls.sheet_names:
                        df_grad = pd.read_excel(xls, 'Graduados')

                    scheduler = TabuScheduler(df_cursos, df_profes, df_salones, zona, df_grad, config=config)
                    problemas_factibilidad = scheduler.validar_factibilidad_inicial()
                    if problemas_factibilidad:
                        st.error("No se pudo preparar una asignación que cumpla las condiciones obligatorias:")
                        for problema in problemas_factibilidad[:50]:
                            st.write(f"- {problema}")
                        if len(problemas_factibilidad) > 50:
                            st.write(f"... y {len(problemas_factibilidad) - 50} problemas adicionales.")
                        return
                    
                    start_time = time.time()
                    bar = st.progress(0)
                    status = st.empty()
                    mejor_sol, conflictos, historial = scheduler.optimizar(iteraciones, bar, status)
                    
                    st.session_state.elapsed_time = time.time() - start_time
                    st.session_state.conflicts = conflictos
                    st.session_state.historial = historial
                    st.session_state.scheduler = scheduler
                    st.session_state.mejor_sol = mejor_sol
                    
                    cargas_finales = {}
                    for asign in mejor_sol:
                        p = asign['profesor']
                        if p != "GRADUADOS" and p != "TBA":
                            cargas_finales[p] = cargas_finales.get(p, 0) + scheduler.get_sec_creditos(asign['seccion'], p)
                    for p in scheduler.profesores:
                        if p not in cargas_finales:
                            cargas_finales[p] = 0.0
                    st.session_state.cargas_finales = cargas_finales

                    st.session_state.master = pd.DataFrame([{
                        'ID': a['seccion'].cod, 
                        'Asignatura': a['seccion'].cod.split('-')[0],
                        'Estudiantes (Cupo)': a['seccion'].cupo,
                        'Créditos Reales': scheduler.get_sec_creditos(a['seccion'], a['profesor']),
                        'Persona': a['profesor'], 
                        'Días': a['patron']['name'], 
                        'Horario': format_horario(a['patron'], a['ini']), 
                        'Salón': a['salon']
                    } for a in mejor_sol])
                    st.session_state.detailed_conflicts = scheduler._obtener_conflictos(mejor_sol)
                    st.session_state.soft_audit = pd.DataFrame(scheduler._obtener_preferencias_incumplidas(mejor_sol))

            except Exception as e:
                st.error(f"Error durante la optimización: {e}")
                return

    if 'master' in st.session_state:
        if st.session_state.conflicts == 0:
            st.success(f"Horario sin conflictos fuertes. Búsqueda completada en {st.session_state.elapsed_time:.2f} segundos.")
        else:
            st.warning(f"Borrador con {st.session_state.conflicts} conflictos fuertes. Revisa la auditoría antes de utilizarlo.")
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        t1, t2, t3, t4 = st.tabs(["💎 PANEL DE CONTROL", "🔍 VISTAS DETALLADAS", "🚨 AUDITORÍA DE CALIDAD", "📊 ANALÍTICAS AVANZADAS"])
        
        with t1:
            edited = st.session_state.master
            st.dataframe(edited, use_container_width=True, height=500)
            st.download_button("💾 EXPORTAR EXCEL PLATINUM", exportar_todo(edited), "Horario_Final_UPRM.xlsx", use_container_width=True)
            
        with t2:
            f1, f2, f3, f4 = st.tabs(["Por Profesor", "Por Curso", "Por Salón", "Por Graduados"])
            df_master = st.session_state.master
            with f1:
                lista_profes = sorted([p for p in df_master['Persona'].unique() if p != "GRADUADOS"])
                if lista_profes:
                    p = st.selectbox("Seleccionar Profesor", lista_profes)
                    subset = df_master[df_master['Persona'] == p]
                    st.table(subset[['ID', 'Estudiantes (Cupo)', 'Créditos Reales', 'Días', 'Horario', 'Salón']])
            with f2:
                lista_cursos = sorted(df_master['Asignatura'].unique())
                if lista_cursos:
                    c = st.selectbox("Seleccionar Curso", lista_cursos)
                    subset = df_master[df_master['Asignatura'] == c]
                    st.table(subset[['ID', 'Estudiantes (Cupo)', 'Persona', 'Días', 'Horario', 'Salón']])
            with f3:
                lista_salones = sorted(df_master['Salón'].unique())
                if lista_salones:
                    sl = st.selectbox("Seleccionar Salón", lista_salones)
                    subset = df_master[df_master['Salón'] == sl]
                    st.table(subset[['ID', 'Asignatura', 'Persona', 'Días', 'Horario']])
            with f4:
                lista_grads = sorted([p for p in df_master['Persona'].unique() if p.upper().startswith('GRADUADO')])
                if lista_grads:
                    g = st.selectbox("Seleccionar Graduado", lista_grads)
                    subset = df_master[df_master['Persona'] == g]
                    st.table(subset[['ID', 'Asignatura', 'Estudiantes (Cupo)', 'Créditos Reales', 'Días', 'Horario', 'Salón']])
                else:
                    st.info("No hay graduados con asignación de docencia en este horario.")
                
        with t3:
            conflictos = st.session_state.conflicts
            if conflictos > 0:
                st.error(f"⚠️ Aún persisten {conflictos} conflictos duros.")
                for conf in st.session_state.detailed_conflicts:
                    st.write(f"- {conf}")
            else:
                st.success("Cero conflictos fuertes en el horario generado.")
            soft = st.session_state.soft_audit
            summary = st.session_state.scheduler._resumen_preferencias(st.session_state.mejor_sol)
            m1, m2, m3 = st.columns(3)
            m1.metric("Conflictos fuertes", conflictos)
            m2.metric("Secciones que cumplen todas sus preferencias", f"{summary['secciones_todas_cumplidas']}/{summary['secciones_con_preferencias']}")
            m3.metric("Penalización de preferencias", int(soft['Penalización'].sum()) if not soft.empty else 0)
            st.caption(f"Se cuentan solo secciones con preferencias flexibles registradas. Comprobaciones cumplidas: {summary['comprobaciones_cumplidas']}/{summary['comprobaciones']}.")
            st.markdown("#### Preferencias incumplidas")
            if soft.empty:
                st.info("Todas las preferencias registradas se cumplen en este resultado.")
            else:
                st.dataframe(soft[['Profesor', 'Sección', 'Dia', 'Preferencia', 'Deseado', 'Asignado',
                                   'Minutos fuera', 'Penalización']], use_container_width=True)
                st.download_button("Descargar auditoría de preferencias (CSV)",
                                   soft.to_csv(index=False).encode('utf-8-sig'),
                                   "Preferencias_incumplidas.csv", "text/csv")
                
        with t4:
            st.markdown("### 📈 Analíticas Avanzadas")
            
            subtab1, subtab2, subtab3, subtab4 = st.tabs(["📊 Visualizaciones", "🗓️ Calendario", "📄 Reporte PDF", "📈 Carga Científica"])
            
            with subtab1:
                st.markdown("#### Mapa de Calor de Ocupación")
                fig_heat = generar_heatmap_plotly(st.session_state.scheduler, st.session_state.mejor_sol)
                st.plotly_chart(fig_heat, use_container_width=True)
                
                st.markdown("#### Distribución de Clases por Profesor y Día")
                fig_barras = generar_barras_apiladas_profesor(st.session_state.mejor_sol, st.session_state.scheduler)
                st.plotly_chart(fig_barras, use_container_width=True)
                
                st.markdown("#### Evolución del Fitness")
                fig_fitness = generar_evolucion_fitness_plotly(st.session_state.historial)
                st.plotly_chart(fig_fitness, use_container_width=True)
            
            with subtab2:
                st.markdown("#### Calendario Visual Interactivo")
                col1, col2, col3 = st.columns(3)
                with col1:
                    filtro_prof = st.selectbox("Filtrar por Profesor", ['Todos'] + sorted(st.session_state.master['Persona'].unique()))
                with col2:
                    filtro_salon = st.selectbox("Filtrar por Salón", ['Todos'] + sorted(st.session_state.master['Salón'].unique()))
                with col3:
                    filtro_curso = st.selectbox("Filtrar por Curso", ['Todos'] + sorted(st.session_state.master['Asignatura'].unique()))
                
                fig_cal = generar_calendario_visual(
                    st.session_state.mejor_sol,
                    st.session_state.scheduler,
                    filtro_prof if filtro_prof != 'Todos' else None,
                    filtro_salon if filtro_salon != 'Todos' else None,
                    filtro_curso if filtro_curso != 'Todos' else None
                )
                st.plotly_chart(fig_cal, use_container_width=True)
            
            with subtab3:
                st.markdown("#### Exportar Reporte Ejecutivo en PDF")
                if st.button("📑 Generar Reporte PDF (Imprimir)"):
                    html_reporte = generar_reporte_pdf_html(
                        st.session_state.scheduler,
                        st.session_state.mejor_sol,
                        st.session_state.cargas_finales,
                        st.session_state.master
                    )
                    st.components.v1.html(html_reporte, height=600, scrolling=True)
                st.info("Haz clic en el botón para generar el reporte y luego usa la opción 'Imprimir' de tu navegador para guardar como PDF.")
            
            with subtab4:
                st.markdown("#### Análisis Científico de Carga Académica")
                fig_carga = generar_figura_cientifica_carga(st.session_state.cargas_finales, st.session_state.scheduler)
                st.plotly_chart(fig_carga, use_container_width=True)
            
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
