import streamlit as st
import pandas as pd
import numpy as np
import random
import io
import time
import math
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

def mins_to_str(m):
    h, mins = divmod(int(m), 60)
    am_pm = "AM" if h < 12 else "PM"
    h_disp = h if h <= 12 else h - 12
    if h_disp == 0: h_disp = 12
    return f"{h_disp:02d}:{mins:02d} {am_pm}"

def str_to_mins(t_str):
    t_str = t_str.strip().upper()
    parts = t_str.split()
    time_part = parts[0]
    ampm = parts[1] if len(parts) > 1 else "AM"
    h, m = map(int, time_part.split(':'))
    if ampm == "PM" and h != 12: h += 12
    if ampm == "AM" and h == 12: h = 0
    return h * 60 + m

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
        
        if isinstance(candidatos_raw, list):
            raw_list = [c.strip().upper() for c in candidatos_raw if c.strip()]
        else:
            raw_list = [c.strip().upper() for c in str(candidatos_raw).split(',') if c.strip() and str(c).upper() != 'NAN']
        self.cands = list(set(raw_list))
        
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
        self.es_grande = self.cupo >= 85

class Profesor:
    def __init__(self, nombre, carga_min, carga_max, pref_dias, pref_horas,
                 hora_entrada, hora_salida,
                 preferencias_cursos, compensacion, acepta_grandes, cursos_intensivos=0):
        self.nombre = nombre.upper().strip()
        self.carga_min = float(carga_min) if pd.notnull(carga_min) and carga_min != '' else 0.0
        self.carga_max = float(carga_max) if pd.notnull(carga_max) and carga_max != '' else 12.0
        
        self.pref_dias_set = set()
        if pref_dias and isinstance(pref_dias, str):
            for token in pref_dias.replace(',', ' ').upper().split():
                if token in ('L', 'LU'): self.pref_dias_set.add('Lu')
                elif token in ('M', 'MA'): self.pref_dias_set.add('Ma')
                elif token in ('W', 'MI'): self.pref_dias_set.add('Mi')
                elif token in ('J', 'JU'): self.pref_dias_set.add('Ju')
                elif token in ('V', 'VI'): self.pref_dias_set.add('Vi')
                elif token in ('LU', 'MA', 'MI', 'JU', 'VI'): self.pref_dias_set.add(token)
        self.pref_horas = pref_horas if isinstance(pref_horas, str) else 'ANY'
        
        # --- NUEVO: Parseo de HORA_ENTRADA y HORA_SALIDA a minutos ---
        self.hora_entrada_min = None
        self.hora_salida_min = None
        if hora_entrada and pd.notnull(hora_entrada) and str(hora_entrada).strip():
            try:
                self.hora_entrada_min = str_to_mins(str(hora_entrada).strip())
            except:
                pass
        if hora_salida and pd.notnull(hora_salida) and str(hora_salida).strip():
            try:
                self.hora_salida_min = str_to_mins(str(hora_salida).strip())
            except:
                pass
        
        self.preferencias = []
        if isinstance(preferencias_cursos, list):
            self.preferencias = [c.upper().strip() for c in preferencias_cursos if c and str(c).upper() != 'NAN']
            
        self.compensacion = str(compensacion).upper().strip() in ('SI', 'SÍ', 'YES', '1')
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
# 4. MOTOR DE OPTIMIZACIÓN MEJORADO (CON REPARACIÓN AGRESIVA REFORZADA)
# ==============================================================================
class TabuScheduler:
    def __init__(self, df_cursos, df_profes, df_salones, zona, df_grad=None):
        self.zona = zona
        
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
            
            candidatos_list = [c.strip().upper() for c in str(datos['candidatos']).split(',') if c.strip() and str(c).upper() != 'NAN']
            acepta_comp = any(c in self.profesores and self.profesores[c].compensacion for c in candidatos_list)
            
            if acepta_comp and demanda_total > cupo_tipico:
                cupo_efectivo = min(demanda_total, 85)
            else:
                cupo_efectivo = cupo_tipico

            num_secciones = math.ceil(demanda_total / cupo_efectivo) if demanda_total > 0 else 1
            est_sec = [cupo_efectivo] * (num_secciones - 1)
            resto = demanda_total - sum(est_sec)
            est_sec.append(resto if resto > 0 else cupo_efectivo)
            
            for i, cupo in enumerate(est_sec):
                self.secciones.append(Seccion(f"{cod_base}-{i+1:02d}", datos['creditos'], cupo, datos['candidatos'], datos['tipo_salon']))

        self._preasignar_profesores_robusto()

        # --- Carga de Graduados (doble rol) ---
        self.graduados_reciben = {}
        if df_grad is not None and not df_grad.empty:
            df_grad.columns = [c.strip().upper() for c in df_grad.columns]
            for _, r in df_grad.iterrows():
                nombre = str(r['NOMBRE']).strip().upper()
                recibe_str = str(r['RECIBE']) if pd.notnull(r['RECIBE']) else ''
                codigos = [c.strip().upper() for c in recibe_str.split(',') if c.strip()]
                self.graduados_reciben[nombre] = codigos

        # Límites horarios
        if zona == "CENTRAL":
            self.hora_universal = (630, 750)
            self.limite_operativo = (450, 1110)
            self.bloques = list(range(450, 1051, 60))
        else:
            self.hora_universal = (600, 720)
            self.limite_operativo = (420, 1080)
            self.bloques = list(range(420, 1021, 60))

        self.solucion = self._construir_solucion_greedy()
        self.mejor_solucion = deepcopy(self.solucion)
        self.mejor_costo = self._costo_total(self.solucion)
        self.historial_costos = [self.mejor_costo]

    def get_sec_creditos(self, s, prof_name):
        if prof_name in self.profesores and self.profesores[prof_name].compensacion:
            return get_creditos_reales(s.creditos, s.cupo)
        return float(s.creditos)

    def _preasignar_profesores_robusto(self):
        carga_actual = {p: 0.0 for p in self.profesores}
        carga_actual["GRADUADOS"] = 0.0
        carga_actual["TBA"] = 0.0
        
        capacidad_restante = {}
        for p in self.profesores.values():
            capacidad_restante[p.nombre] = p.carga_max
        
        secciones_unicas = []
        secciones_multiple = []
        for s in self.secciones:
            cands_validos = [c for c in s.cands if c in self.profesores]
            if not cands_validos:
                if "GRADUADOS" in s.cands:
                    s.prof_preasignado = "GRADUADOS"
                    carga_actual["GRADUADOS"] += self.get_sec_creditos(s, "GRADUADOS")
                else:
                    s.prof_preasignado = "TBA"
                    carga_actual["TBA"] += self.get_sec_creditos(s, "TBA")
                continue
            if len(cands_validos) == 1:
                secciones_unicas.append(s)
            else:
                secciones_multiple.append(s)
        
        for s in secciones_unicas:
            prof = s.cands[0]
            creditos = self.get_sec_creditos(s, prof)
            s.prof_preasignado = prof
            carga_actual[prof] += creditos
            if prof in capacidad_restante:
                capacidad_restante[prof] -= creditos
        
        preferencias = {}
        for s in secciones_multiple:
            preferencias[s] = {}
            for prof in s.cands:
                if prof in self.profesores:
                    prioridad_base = self.profesores[prof].prioridad_curso(s.cod)
                    if s.es_grande and self.profesores[prof].acepta_grandes == 1:
                        prioridad_base += 0.5
                    preferencias[s][prof] = prioridad_base
                else:
                    preferencias[s][prof] = 0.0
        
        secciones_multiple.sort(key=lambda s: (len(s.cands), -max(preferencias[s].values())))
        
        for s in secciones_multiple:
            candidatos_ordenados = sorted(s.cands, key=lambda p: preferencias[s].get(p, 0), reverse=True)
            asignado = False
            for prof in candidatos_ordenados:
                if prof in capacidad_restante and capacidad_restante[prof] >= self.get_sec_creditos(s, prof):
                    s.prof_preasignado = prof
                    creditos = self.get_sec_creditos(s, prof)
                    carga_actual[prof] += creditos
                    capacidad_restante[prof] -= creditos
                    asignado = True
                    break
            if not asignado:
                prof = candidatos_ordenados[0]
                s.prof_preasignado = prof
                creditos = self.get_sec_creditos(s, prof)
                carga_actual[prof] += creditos
                if prof in capacidad_restante:
                    capacidad_restante[prof] -= creditos
        
        def calc_penalidad():
            pen = 0
            for p, c in carga_actual.items():
                if p in self.profesores:
                    if c < self.profesores[p].carga_min - 0.5:
                        pen += (self.profesores[p].carga_min - c) * 10
                    elif c > self.profesores[p].carga_max + 0.5:
                        pen += (c - self.profesores[p].carga_max) * 10
            return pen

        penalidad_actual = calc_penalidad()
        T = 100.0
        for _ in range(30000):
            if penalidad_actual == 0:
                break
            s = random.choice(self.secciones)
            prof_viejo = s.prof_preasignado
            if prof_viejo not in self.profesores:
                continue
            cands = [p for p in s.cands if p in self.profesores and p != prof_viejo]
            if not cands:
                continue
            nuevo_prof = random.choice(cands)
            creditos_viejos = self.get_sec_creditos(s, prof_viejo)
            creditos_nuevos = self.get_sec_creditos(s, nuevo_prof)
            carga_actual[prof_viejo] -= creditos_viejos
            carga_actual[nuevo_prof] += creditos_nuevos
            nueva_pen = calc_penalidad()
            if nueva_pen < penalidad_actual:
                penalidad_actual = nueva_pen
                s.prof_preasignado = nuevo_prof
            else:
                delta = nueva_pen - penalidad_actual
                if T > 0.01 and random.random() < math.exp(-delta / T):
                    penalidad_actual = nueva_pen
                    s.prof_preasignado = nuevo_prof
                else:
                    carga_actual[prof_viejo] += creditos_viejos
                    carga_actual[nuevo_prof] -= creditos_nuevos
            T *= 0.995

    def _costo_total(self, sol, solo_duros=False):
        conflicts = 0
        soft_penalty = 0
        occ_prof = {}
        occ_salon = {}
        carga_prof = {p: 0.0 for p in self.profesores}
        carga_prof["GRADUADOS"] = 0.0
        carga_prof["TBA"] = 0.0
        
        for i, asign in enumerate(sol):
            s = asign['seccion']
            prof = asign['profesor']
            salon = asign['salon']
            patron = asign['patron']
            ini = asign['ini']
            
            if prof == "TBA" or salon == "TBA":
                conflicts += 10000
                if solo_duros: continue
            
            salon_info = next((sl for sl in self.salones if sl['CODIGO'] == salon), None)
            if salon_info and salon_info['CAPACIDAD'] < s.cupo:
                conflicts += 10000
            if salon_info and not compatible_tipo(s.tipos_permitidos, salon_info['TIPO']):
                conflicts += 10000
            
            if prof in self.profesores:
                prof_obj = self.profesores[prof]
                if prof_obj.acepta_grandes == 0 and s.es_grande:
                    conflicts += 10000
            
            if prof in carga_prof:
                carga_prof[prof] += self.get_sec_creditos(s, prof)
            
            es_intensivo = any(c >= 3 for c in patron['days'].values())
            puede_ser_intensivo = any(any(c >= 3 for c in p['days'].values()) for p in PATRONES.get(s.creditos, PATRONES[3]))
            
            if prof != "GRADUADOS" and prof in self.profesores:
                prof_obj = self.profesores[prof]
                if prof_obj.cursos_intensivos == 0 and es_intensivo:
                    conflicts += 10000
                elif prof_obj.cursos_intensivos == 1 and puede_ser_intensivo and not es_intensivo:
                    conflicts += 10000

                if not solo_duros:
                    if prof_obj.pref_horas == 'AM' and ini >= 720:
                        soft_penalty += 30
                    elif prof_obj.pref_horas == 'PM' and ini < 720:
                        soft_penalty += 30
                    if prof_obj.pref_dias_set:
                        for dia in patron['days'].keys():
                            if dia not in prof_obj.pref_dias_set:
                                soft_penalty += 15

            # --- NUEVO: Restricción fuerte HORA_ENTRADA / HORA_SALIDA ---
            if prof != "GRADUADOS" and prof in self.profesores:
                prof_obj = self.profesores[prof]
                if prof_obj.hora_entrada_min is not None or prof_obj.hora_salida_min is not None:
                    for dia, contrib in patron['days'].items():
                        fin_bloque = ini + int(contrib * 50)
                        if prof_obj.hora_entrada_min is not None and ini < prof_obj.hora_entrada_min:
                            conflicts += 10000
                        if prof_obj.hora_salida_min is not None and fin_bloque > prof_obj.hora_salida_min:
                            conflicts += 10000
            # ------------------------------------------------------------

            for dia, contrib in patron['days'].items():
                fin = ini + int(contrib * 50)
                if dia in ["Ma", "Ju"] and max(ini, self.hora_universal[0]) < min(fin, self.hora_universal[1]):
                    conflicts += 10000
                if s.creditos == 3 and contrib >= 3 and ini < 930:
                    conflicts += 10000
                if fin > self.limite_operativo[1] or ini < self.limite_operativo[0]:
                    conflicts += 10000
                
                if prof != "GRADUADOS":
                    clave = (prof, dia)
                    if clave not in occ_prof: occ_prof[clave] = []
                    for (ini_ex, fin_ex) in occ_prof[clave]:
                        if max(ini, ini_ex) < min(fin, fin_ex):
                            conflicts += 10000
                    occ_prof[clave].append((ini, fin))
                
                clave_s = (salon, dia)
                if clave_s not in occ_salon: occ_salon[clave_s] = []
                for (ini_ex, fin_ex, cupo_ex, fus_ex) in occ_salon[clave_s]:
                    if max(ini, ini_ex) < min(fin, fin_ex):
                        if salon in self.mega_salones and s.es_fusionable and fus_ex:
                            if s.cupo + cupo_ex <= salon_info['CAPACIDAD']:
                                continue
                        conflicts += 10000
                occ_salon[clave_s].append((ini, fin, s.cupo, s.es_fusionable))
        
        for prof, carga in carga_prof.items():
            prof_obj = self.profesores.get(prof)
            if prof_obj:
                if carga > prof_obj.carga_max + 0.5:
                    conflicts += 10000
                if carga < prof_obj.carga_min - 0.5:
                    conflicts += 10000

        # --- RESTRICCIÓN FUERTE: DOBLE ROL DE GRADUADOS ---
        for grad, codigos_recibe in self.graduados_reciben.items():
            dicta = [asign for asign in sol if asign['profesor'] == grad]
            recibe = []
            for asign in sol:
                cod_base = asign['seccion'].cod.split('-')[0].upper()
                if cod_base in codigos_recibe:
                    recibe.append(asign)
            for d in dicta:
                for r in recibe:
                    for dia_d, contrib_d in d['patron']['days'].items():
                        ini_d = d['ini']
                        fin_d = ini_d + int(contrib_d * 50)
                        for dia_r, contrib_r in r['patron']['days'].items():
                            if dia_d == dia_r:
                                ini_r = r['ini']
                                fin_r = ini_r + int(contrib_r * 50)
                                if max(ini_d, ini_r) < min(fin_d, fin_r):
                                    conflicts += 10000
        # ------------------------------------------------------------

        if solo_duros:
            return conflicts
        
        salones_por_prof_tipo = {}
        for asign in sol:
            prof = asign['profesor']
            if prof not in ["GRADUADOS", "TBA"] and prof in self.profesores:
                salon = asign['salon']
                tipo = self.salon_tipo.get(salon, 1)
                key = (prof, tipo)
                if key not in salones_por_prof_tipo:
                    salones_por_prof_tipo[key] = set()
                salones_por_prof_tipo[key].add(salon)
        for (prof, tipo), salones in salones_por_prof_tipo.items():
            if len(salones) > 1:
                soft_penalty += (len(salones) - 1) * 2
        
        return conflicts + soft_penalty

    def _obtener_conflictos(self, sol):
        conflictos_list = []
        occ_prof = {}
        occ_salon = {}
        carga_prof = {p: 0.0 for p in self.profesores}
        carga_prof["GRADUADOS"] = 0.0
        carga_prof["TBA"] = 0.0
        
        for i, asign in enumerate(sol):
            s = asign['seccion']
            prof = asign['profesor']
            salon = asign['salon']
            patron = asign['patron']
            ini = asign['ini']
            
            if prof == "TBA": conflictos_list.append(f"Sección {s.cod}: profesor TBA")
            if salon == "TBA": conflictos_list.append(f"Sección {s.cod}: salón TBA")
            
            salon_info = next((sl for sl in self.salones if sl['CODIGO'] == salon), None)
            if salon_info and salon_info['CAPACIDAD'] < s.cupo:
                conflictos_list.append(f"Sección {s.cod}: salón {salon} capacidad insuficiente")
            if salon_info and not compatible_tipo(s.tipos_permitidos, salon_info['TIPO']):
                conflictos_list.append(f"Sección {s.cod}: tipo de salón incompatible (requiere {s.tipos_permitidos})")
            
            if prof in carga_prof:
                carga_prof[prof] += self.get_sec_creditos(s, prof)
                
            es_intensivo = any(c >= 3 for c in patron['days'].values())
            puede_ser_intensivo = any(any(c >= 3 for c in p['days'].values()) for p in PATRONES.get(s.creditos, PATRONES[3]))

            if prof != "GRADUADOS" and prof in self.profesores:
                prof_obj = self.profesores[prof]
                if prof_obj.cursos_intensivos == 0 and es_intensivo:
                    conflictos_list.append(f"Sección {s.cod}: Prof {prof} tiene clase intensiva pero solicitó NO intensivos.")
                elif prof_obj.cursos_intensivos == 1 and puede_ser_intensivo and not es_intensivo:
                    conflictos_list.append(f"Sección {s.cod}: Prof {prof} NO tiene clase intensiva pero solicitó SÍ intensivos.")
                if prof_obj.acepta_grandes == 0 and s.es_grande:
                    conflictos_list.append(f"Sección {s.cod}: Prof {prof} no acepta grandes.")
            
            # --- NUEVO: Reporte de violación horario laboral ---
            if prof != "GRADUADOS" and prof in self.profesores:
                prof_obj = self.profesores[prof]
                if prof_obj.hora_entrada_min is not None or prof_obj.hora_salida_min is not None:
                    for dia, contrib in patron['days'].items():
                        fin_bloque = ini + int(contrib * 50)
                        if prof_obj.hora_entrada_min is not None and ini < prof_obj.hora_entrada_min:
                            conflictos_list.append(f"Sección {s.cod}: Prof {prof} comienza antes de su hora de entrada ({mins_to_str(prof_obj.hora_entrada_min)})")
                        if prof_obj.hora_salida_min is not None and fin_bloque > prof_obj.hora_salida_min:
                            conflictos_list.append(f"Sección {s.cod}: Prof {prof} termina después de su hora de salida ({mins_to_str(prof_obj.hora_salida_min)})")
            # --------------------------------------------------------
            
            for dia, contrib in patron['days'].items():
                fin = ini + int(contrib * 50)
                if dia in ["Ma", "Ju"] and max(ini, self.hora_universal[0]) < min(fin, self.hora_universal[1]):
                    conflictos_list.append(f"Sección {s.cod}: violación de hora universal el {dia}")
                
                if prof != "GRADUADOS":
                    clave = (prof, dia)
                    if clave not in occ_prof: occ_prof[clave] = []
                    for (ini_ex, fin_ex) in occ_prof[clave]:
                        if max(ini, ini_ex) < min(fin, fin_ex):
                            conflictos_list.append(f"Cruce de profesor {prof} el {dia}")
                    occ_prof[clave].append((ini, fin))
                
                clave_s = (salon, dia)
                if clave_s not in occ_salon: occ_salon[clave_s] = []
                for (ini_ex, fin_ex, cupo_ex, fus_ex) in occ_salon[clave_s]:
                    if max(ini, ini_ex) < min(fin, fin_ex):
                        if not (salon in self.mega_salones and s.es_fusionable and fus_ex and s.cupo + cupo_ex <= salon_info['CAPACIDAD']):
                            conflictos_list.append(f"Cruce de salón {salon} el {dia}")
                occ_salon[clave_s].append((ini, fin, s.cupo, s.es_fusionable))
        
        for prof, carga in carga_prof.items():
            prof_obj = self.profesores.get(prof)
            if prof_obj:
                if carga > prof_obj.carga_max + 0.5:
                    conflictos_list.append(f"Profesor {prof} excede carga máxima ({carga:.1f} > {prof_obj.carga_max})")
                if carga < prof_obj.carga_min - 0.5:
                    conflictos_list.append(f"Profesor {prof} no alcanza carga mínima ({carga:.1f} < {prof_obj.carga_min})")

        # Conflictos de doble rol
        for grad, codigos_recibe in self.graduados_reciben.items():
            dicta = [asign for asign in sol if asign['profesor'] == grad]
            recibe = []
            for asign in sol:
                cod_base = asign['seccion'].cod.split('-')[0].upper()
                if cod_base in codigos_recibe:
                    recibe.append(asign)
            for d in dicta:
                for r in recibe:
                    for dia_d, contrib_d in d['patron']['days'].items():
                        ini_d = d['ini']
                        fin_d = ini_d + int(contrib_d * 50)
                        for dia_r, contrib_r in r['patron']['days'].items():
                            if dia_d == dia_r:
                                ini_r = r['ini']
                                fin_r = ini_r + int(contrib_r * 50)
                                if max(ini_d, ini_r) < min(fin_d, fin_r):
                                    conflictos_list.append(f"Graduado {grad}: conflicto de doble rol entre {d['seccion'].cod} y {r['seccion'].cod} el {dia_d}")
        return conflictos_list

    def _construir_solucion_greedy(self):
        sol = [None] * len(self.secciones)
        asignado = [False] * len(self.secciones)
        for i, s in enumerate(self.secciones):
            prof = getattr(s, 'prof_preasignado', 'TBA')
            exito = self._asignar_seccion(i, prof, sol, asignado)
            if not exito:
                sol[i] = self._crear_asignacion_temporal(s, prof=prof)
                asignado[i] = True
        return sol

    def _crear_asignacion_temporal(self, seccion, prof="TBA", salon="TBA", patron=None, ini=None):
        if patron is None: patron = random.choice(PATRONES.get(seccion.creditos, PATRONES[3]))
        if ini is None: ini = random.choice(self.bloques)
        if salon == "TBA":
            salones_posibles = [sl['CODIGO'] for sl in self.salones if sl['CAPACIDAD'] >= seccion.cupo and compatible_tipo(seccion.tipos_permitidos, sl['TIPO'])]
            salon = random.choice(salones_posibles) if salones_posibles else "TBA"
        return {'seccion': seccion, 'profesor': prof, 'salon': salon, 'patron': patron, 'ini': ini}

    def _asignar_seccion(self, idx, prof, sol, asignado):
        s = sol[idx]['seccion'] if sol[idx] else self.secciones[idx]
        patrones = PATRONES.get(s.creditos, PATRONES[3])
        
        puede_ser_intensivo = any(any(c >= 3 for c in p['days'].values()) for p in patrones)
        
        if prof in self.profesores:
            prof_obj = self.profesores[prof]
            if prof_obj.cursos_intensivos == 0:
                patrones = [p for p in patrones if not any(c >= 3 for c in p['days'].values())]
            elif prof_obj.cursos_intensivos == 1 and puede_ser_intensivo:
                patrones_int = [p for p in patrones if any(c >= 3 for c in p['days'].values())]
                if patrones_int: patrones = patrones_int
                
        if not patrones: patrones = PATRONES.get(s.creditos, PATRONES[3])

        random.shuffle(patrones)
        for patron in patrones:
            for dia, contrib in patron['days'].items():
                duracion = contrib * 50
                inicios_posibles = [ini for ini in self.bloques if ini >= self.limite_operativo[0] and ini + duracion <= self.limite_operativo[1]]
                if dia in ["Ma", "Ju"]:
                    inicios_posibles = [ini for ini in inicios_posibles if not (max(ini, self.hora_universal[0]) < min(ini+duracion, self.hora_universal[1]))]
                if s.creditos == 3 and contrib >= 3:
                    inicios_posibles = [ini for ini in inicios_posibles if ini >= 930]
                
                salones_posibles = [sl['CODIGO'] for sl in self.salones if sl['CAPACIDAD'] >= s.cupo]
                salones_posibles = [sl for sl in salones_posibles if compatible_tipo(s.tipos_permitidos, self.salon_tipo.get(sl, 1))]
                
                for ini in inicios_posibles:
                    for salon in salones_posibles:
                        # Verificar horario laboral del profesor
                        if prof in self.profesores:
                            prof_obj = self.profesores[prof]
                            if prof_obj.hora_entrada_min is not None and ini < prof_obj.hora_entrada_min:
                                continue
                            fin_bloque = ini + duracion
                            if prof_obj.hora_salida_min is not None and fin_bloque > prof_obj.hora_salida_min:
                                continue
                        
                        conflicto = False
                        for j, asign in enumerate(sol):
                            if asign and asignado[j] and j != idx:
                                if asign['profesor'] == prof:
                                    for dia2, contrib2 in asign['patron']['days'].items():
                                        if dia == dia2 and max(ini, asign['ini']) < min(ini + duracion, asign['ini'] + int(contrib2 * 50)):
                                            conflicto = True; break
                                if asign['salon'] == salon:
                                    for dia2, contrib2 in asign['patron']['days'].items():
                                        if dia == dia2 and max(ini, asign['ini']) < min(ini + duracion, asign['ini'] + int(contrib2 * 50)):
                                            if salon in self.mega_salones and s.es_fusionable and asign['seccion'].es_fusionable:
                                                if s.cupo + asign['seccion'].cupo <= self.salon_capacidad.get(salon, 0):
                                                    continue
                                            conflicto = True; break
                            if conflicto: break
                        if not conflicto:
                            sol[idx] = {'seccion': s, 'profesor': prof, 'salon': salon, 'patron': patron, 'ini': ini}
                            asignado[idx] = True
                            return True
        return False

    def _mutar_solucion(self, sol):
        nuevo = deepcopy(sol)
        if random.random() < 0.3 and len(sol) >= 2:
            idx1, idx2 = random.sample(range(len(sol)), 2)
            a1, a2 = nuevo[idx1], nuevo[idx2]
            if (a1['profesor'] in a2['seccion'].cands or a2['profesor'] == "GRADUADOS" or a1['profesor'] == "TBA") and \
               (a2['profesor'] in a1['seccion'].cands or a1['profesor'] == "GRADUADOS" or a2['profesor'] == "TBA"):
                a1['profesor'], a2['profesor'] = a2['profesor'], a1['profesor']
                a1['salon'], a2['salon'] = a2['salon'], a1['salon']
                return nuevo, self._costo_total(nuevo)
        
        idx = random.randint(0, len(nuevo)-1)
        s = nuevo[idx]['seccion']
        prof_actual = nuevo[idx]['profesor']

        cand_profs = [p for p in s.cands if p in self.profesores]
        if not cand_profs:
            cand_profs = ["GRADUADOS"] if "GRADUADOS" in s.cands else ["TBA"]
        cand_profs.sort(key=lambda p: (
            0 if (p in self.profesores and s.es_grande and self.profesores[p].acepta_grandes == 1) else 1,
            -(self.profesores[p].prioridad_curso(s.cod) if p in self.profesores else 0)
        ))

        mejores_opciones = []
        for _ in range(40):
            prof = random.choice(cand_profs)
            patrones = PATRONES.get(s.creditos, PATRONES[3])
            if prof in self.profesores:
                prof_obj = self.profesores[prof]
                patrones = [p for p in patrones if not (prof_obj.cursos_intensivos == 0 and any(c >= 3 for c in p['days'].values()))]
                if prof_obj.cursos_intensivos == 1:
                    intensivos = [p for p in PATRONES.get(s.creditos, PATRONES[3]) if any(c >= 3 for c in p['days'].values())]
                    if intensivos:
                        patrones = intensivos + [p for p in patrones if not any(c >= 3 for c in p['days'].values())]
            if not patrones:
                patrones = PATRONES.get(s.creditos, PATRONES[3])

            patron = random.choice(patrones)
            horas_posibles = set(self.bloques)
            for dia, contrib in patron['days'].items():
                duracion = contrib * 50
                horas_dia = [h for h in self.bloques if h >= self.limite_operativo[0] and h + duracion <= self.limite_operativo[1]]
                if dia in ["Ma", "Ju"]:
                    horas_dia = [h for h in horas_dia if not (max(h, self.hora_universal[0]) < min(h+duracion, self.hora_universal[1]))]
                if s.creditos == 3 and contrib >= 3:
                    horas_dia = [h for h in horas_dia if h >= 930]
                horas_posibles = horas_posibles.intersection(set(horas_dia))
                if not horas_posibles:
                    break
            if not horas_posibles:
                continue
            hora = random.choice(list(horas_posibles))
            
            # Filtrar horas que respeten horario laboral
            if prof in self.profesores:
                prof_obj = self.profesores[prof]
                if prof_obj.hora_entrada_min is not None and hora < prof_obj.hora_entrada_min:
                    continue
                fin_bloque = hora + max([contrib * 50 for contrib in patron['days'].values()])
                if prof_obj.hora_salida_min is not None and fin_bloque > prof_obj.hora_salida_min:
                    continue

            salones_cand = [sl['CODIGO'] for sl in self.salones
                            if compatible_tipo(s.tipos_permitidos, sl['TIPO']) and sl['CAPACIDAD'] >= s.cupo]
            if not salones_cand:
                continue
            salon = random.choice(salones_cand)

            conflicto = False
            for j, asign2 in enumerate(sol):
                if j != idx and asign2:
                    if asign2['profesor'] == prof:
                        for dia2, contrib2 in asign2['patron']['days'].items():
                            if dia2 in patron['days']:
                                fin_actual = hora + int(patron['days'][dia2] * 50)
                                fin_exist = asign2['ini'] + int(contrib2 * 50)
                                if max(hora, asign2['ini']) < min(fin_actual, fin_exist):
                                    conflicto = True
                                    break
                    if conflicto:
                        break
                    if asign2['salon'] == salon:
                        for dia2, contrib2 in asign2['patron']['days'].items():
                            if dia2 in patron['days']:
                                fin_actual = hora + int(patron['days'][dia2] * 50)
                                fin_exist = asign2['ini'] + int(contrib2 * 50)
                                if max(h max(hora,ora, asign2 asign2['ini'])['ini']) < min(f < min(finin_actual, fin_ex_actual, fin_existist):
                                    if salon in):
                                    if salon in self.m self.mega_sega_salonesalones and s and s.es_f.es_fusionableusionable and asign and asign2['2['seccionseccion'].es'].es_fusion_fusionableable:
                                        if:
                                        if s.c s.cupoupo + asign + asign2['2['seccionseccion'].cup'].cupo <=o <= self.s self.salon_calon_capacidadapacidad.get(s.get(salon,alon, 0 0):
                                            continue
                                    conflic):
                                            continue
                                    conflicto =to = True True
                                    break
                                    break
                   
                    if conflic if conflictoto:
                        break:
                        break
           
            if not conflicto if not conflicto:
                costo =:
                costo = 0 0
                if prof
                if prof in self in self.prof.profesoresesores:
                   :
                    prof_obj prof_obj = self = self.prof.profesores[profesores]
                   [prof]
                    if prof if prof_obj.p_obj.pref_href_horas ==oras == 'AM 'AM' and' and hora >=  hora >=720 720:
                        costo +=:
                        costo += 30 30
                   
                    elif prof elif prof_obj.pref_h_obj.pref_horas == 'PMoras == 'PM' and hora' and hora < 720 < 720:
                       :
                        costo += costo += 30 30
                   
                    if prof if prof_obj.p_obj.pref_dref_dias_set:
                       ias_set:
                        for dia for dia in patron in patron['days'].keys['days'].keys():
                           ():
                            if dia if dia not in not in prof_obj prof_obj.pref.pref_dias_set_dias_set:
                                costo:
                                costo +=  += 1515
                mejores
                mejores_opciones_opciones.append((costo.append((costo, prof, prof, patron, patron, hora, hora, salon, salon))

        if not mejores_op))

        if not mejores_opcionesciones:
            return:
            return nuevo, nuevo, self._ self._costo_total(nuevo)
        mejores_opciones.sortcosto_total(nuevo)
        mejores_opciones.sort(key=lambda x:(key=lambda x: x x[0[0])
        mejor])
        mejor = mejores_opciones = mejores_opciones[0[0]
       ]
        nuevo[idx nuevo[idx] =] = {'se {'seccion':ccion': s, 'prof s, 'profesor':esor': mejor mejor[1],[1], 'sal 'salon':on': mejor mejor[4],[4], 'pat 'patron': mejorron': mejor[2],[2], 'ini 'ini': mejor': mejor[3[3]}
        return nuevo]}
        return nuevo, self, self._c._costo_totalosto_total(nue(nuevo)

    defvo)

    def _c _costo_osto_compactacioncompactacion(self,(self, sol sol):
        penalty = ):
        penalty = 00
        prof
        prof_asign_asignaciones =aciones = {}
        for asign {}
        in sol for asign in sol:
           :
            prof = asign[' prof = asign['profesorprofesor']
           ']
            if prof not in ["TBA", "GRADU if prof not in ["TBA", "GRADUADOSADOS"] and"] and prof in prof in self.pro self.profesfesoresores:
                if:
                if prof not prof not in prof in prof_asign_asignacionesaciones:
                    prof:
                    prof_asign_asignacionesaciones[prof][prof] = []
                prof = []
                prof_asign_asignacionesaciones[prof].[prof].append(asign)
        
       append(asign)
        
        for prof for prof, asigns in, asigns in prof_as prof_asignaciones.itemsignaciones.items():
            dias_pres():
            dias_presencialesenciales = set()
            = set()
            salones salones_usados_usados = set = set()
           ()
            carga_total carga_total =  = 0.0
            for asign in asigns0.0
            for asign in asigns:
               :
                s = s = asign['seccion']
                patron = asign[' asign['seccion']
                patron = asign['patron']
                dias_presencialpatron']
                dias_presenciales.update(pates.update(patron['days'].keys())
                salones_usados.addron['days'].keys())
                salones_usados.add(asign['salon(asign['salon'])
                carga_total += self.get_sec_cred'])
                carga_total += self.get_sec_creditos(s, prof)
            
            ifitos(s, prof)
            
            if carga_total carga_total <= 9 <= 9:
                dias_ideal:
                dias_ideal = 2
            elif carga_total <= 15 = 2
            elif carga_total <= 15:
                dias:
                dias_ideal = 3_ideal = 3
            else:
                dias_
            else:
                dias_ideal = 4
           ideal = 4
            exceso = len(dias exceso = len(dias_pres_presencialesenciales) - dias_ideal
            if exceso) - dias_ideal
            if exceso > 0 > 0:
                penalty:
                penalty += ex += exceso *ceso * 500 500
            
           
            
            if len if len(sal(salones_usados)ones_usados) >  > 11:
                penalty:
                penalty += ( += (len(slen(salonesalones_usados_usados) -) - 1) * 1 400) * 400
            
           
            
            for dia for dia in dias in dias_pres_presencialesenciales:
               :
                clases = []
                for clases = []
                asign for asign in asigns:
                    if in asigns:
                    if dia in dia in asign[' asign['patronpatron']['days']['days']']:
                        ini:
                        ini = asign = asign['ini['ini']
                        fin =']
                        fin = ini + ini + int(as int(asign['ign['patronpatron']['days']['days'][dia] *'][dia] * 50)
                        clases.append 50)
                        clases.append((ini((ini, fin, fin))
               ))
                clases.sort clases.sort()
               ()
                for i for i in range in range(len(cl(len(clases)-1ases)-1):
                    bre):
                    brecha = clases[icha =+1 clases[i+1][0][0] -] - clases[i clases[i][1][1]
                   ]
                    if brecha > if brecha > 30 30:
                        penalty +=:
                        penalty += brecha brecha *  * 22
        return penalty
        return penalty

    def _mut

    def _mutar_ar_compactacioncompactacion(self, sol(self, sol):
       ):
        nuevo = deepcopy(sol)
        idx nuevo = deepcopy(sol)
        idx = random = random.randint(.randint(0,0, len(n len(nuevouevo)-1)-1)
       )
        s = s = nuevo[idx nuevo[idx]['se]['seccion']
        profccion']
        prof_actual_actual = nuevo = nuevo[idx]['[idx]['profesorprofesor']
']
        
        prof        
        prof = prof = prof_actual
       _actual
        if prof if prof not in self.pro not in self.profesfesoresores:
            return:
            return nuevo, self._ nuevo, self._costocosto_compact_compactacion(nacion(nuevouevo)
)
        
        patron        
        patrones =es = PATRON PATRONES.getES.get(s.creditos(s.creditos, PAT, PATRONESRONES[3])
       [3 prof_obj])
        prof_obj = self = self.prof.profesoresesores[prof[prof]
       ]
        if prof if prof_obj.c_obj.cursos_intursos_intensivosensivos ==  == 0:
            patron0:
            patrones =es = [p for p [p for p in patron in patrones ifes if not any not any(c >=(c >= 3 3 for c for c in p in p['days['days'].values'].values())())]
        elif prof_obj]
        elif prof_obj.cursos.cursos_intens_intensivos ==ivos == 1 1:
            intensivos = [p for:
            intensivos = [p for p in p in patron patroneses if any if any(c >=(c >= 3 3 for c for c in p in p['days['days'].values'].values())())]
]
            if intensivos            if intensivos:
               :
                patrones patrones = intensivos = intensivos
        
        if
        
        if not patron not patroneses:
            patrones =:
            patron PATRONes = PATRONES.getES.get(s.creditos(s.creditos, PATRONES, PATRONES[3[3])
])
        
        mejores_opciones        
        mejores_opciones = = []
        for []
        for _ in range( _ in range(2020):
            patron):
            patron = random = random.choice(.choice(patrones)
           patrones horas_pos)
           ibles = horas_posibles = set(self set(self.bloques.bloques)
            for)
            for dia, dia, contrib in contrib in patron['days']. patron['days'].itemsitems():
                du():
                duracionracion = contrib *  = contrib * 5050
                horas
                horas_dia_dia = = [h for [h for h in h in self.bl self.bloquesoques if h if h >= self >= self.lim.limite_ite_operativooperativo[0[0] and] and h + h + durac duracion <=ion <= self.l self.limite_operativoimite_operativo[1[1]]
                if]]
                if dia in dia in ["Ma ["Ma", "Ju", "Ju"]"]:
                   :
                    horas_d horas_dia =ia = [h [h for h in horas_dia if not for h in horas_dia if not (max (max(h,(h, self.h self.hora_unora_universaliversal[0[0])]) < min(h+du < min(hracion+duracion, self, self.hora.hora_universal_universal[1]))[1]))]
               ]
                if s if s.cred.creditos ==itos == 3 3 and contrib and contrib >=  >= 3:
                    horas3:
                    horas_dia_dia = = [h for h in [h for h in horas_d horas_dia ifia if h >= h >= 930 930]
               ]
                horas_pos horas_posibles =ibles = horas_posibles. horas_posibles.intersectionintersection(set(horas(set(horas_dia_dia))
               ))
                if not horas_pos if not horas_posiblesibles:
                    break:
                    break
           
            if not if not horas_pos horas_posibles:
                continueibles:
                continue
           
            hora = hora = random.choice(list( random.choice(list(horashoras_posibles_posibles))
            
            # Res))
            
            # Respetarpetar horario laboral horario laboral
           
            if prof if prof_obj.hora__obj.hora_entrada_min isentrada not None_min is not None and hora and hora < prof_obj.h < prof_obj.hora_ora_entradaentrada_min:
                continue_min:
                continue
            fin_bl
            fin_bloque = hora +oque = hora + max max([contrib * 50([contrib * 50 for contrib for contrib in patron in patron['days['days'].values'].values()()])
            if])
            if prof_obj prof_obj.hora.hora_sal_salida_minida_min is not is not None and None and fin_bl fin_bloque >oque > prof_obj.hora prof_obj.hora_salida_min_salida_min:
                continue:
                continue
            
            salones_c
            
            salones_cand = [sland = [sl['COD['CODIGOIGO'] for'] for sl in sl in self.sal self.salonesones
                            if compatible
                           _tipo if compatible_tipo(s.tipos(s.tipos_permit_permitidos,idos, sl[' sl['TIPO']) andTIPO']) and sl[' sl['CAPACIDAD'] >= sCAPACIDAD'].cup >= s.cupo]
            ifo]
            if not sal not salones_cones_candand:
                continue
           :
                continue
            salon = salon = random.choice(salones_c random.choice(salones_candand)
            
            conflic)
            
           to = False conflicto = False
           
            for j for j, asign, asign2 in enumerate(n2 in enumerate(nuevo):
               uevo):
                if j != idx if j != idx and asign and asign22:
                    if:
                    if asign2['prof asign2['profesor'] == profesor'] == prof:
                       :
                        for dia2, for dia2, contrib2 contrib2 in asign2[' in asignpatron2['']['dayspatron']['days'].items'].items():
                            if dia():
                            if dia2 in2 in patron[' patron['days']days']:
                               :
                                fin_ fin_actual =actual = hora + int( hora + int(patronpatron['days['days'][dia'][dia2]2] *  * 50)
                                fin50)
                                fin_exist_exist = asign2[' = asign2['ini'] + intini'] + int(contrib(contrib2 * 502 * 50)
                               )
                                if max(hora if max(hora, asign2['ini']) < min, asign2['ini']) < min(fin(fin_actual_actual, fin, fin_exist_exist):
                                   ):
                                    conflicto conflicto = True = True; break; break
                   
                    if asign if asign2['2['salon'] ==salon'] == salon salon:
                        for:
                        for dia2 dia2, contrib, contrib2 in2 in asign2 asign2['pat['patron']['ron']['days'].items():
                            if dia2days'].items():
                            if dia2 in patron['days']:
                                fin in patron['days']:
                                fin_actual_actual = hora + int(pat = hora + int(patron['days'][dia2ron['days'][dia2] *] * 50)
                                fin_ex 50)
                                fin_exist =ist = asign2['ini'] + asign2['ini'] + int(contrib2 * 50)
                                if int(contrib2 * 50)
                                if max(hora, asign2 max(hora, asign2['ini['ini']) < min(fin_actual,']) < min(fin_actual, fin_exist):
                                    if salon in fin_exist):
                                    if salon in self.mega_salones and s self.mega_salones and s.es_fusionable and asign2['.es_fusionable and asign2['seccion'].es_fusionseccion'].es_fusionableable:
                                        if s.c:
                                        if s.cupo + asign2['upo + asign2['seccionseccion'].cupo <='].cupo <= self.s self.salon_capacidadalon_capacidad.get(s.get(salon, 0):
                                           alon, 0):
                                            continue continue
                                    conflic
                                    conflicto = True;to = True; break break
                    if
                    if conflicto: break conflicto: break
           
            if not if not conflicto conflicto:
               :
                temp_s temp_sol =ol = deepcopy deepcopy(nue(nuevo)
                tempvo)
                temp_sol[idx]_sol[idx] = {'seccion = {'seccion': s, 'prof': s, 'esorprofesor': prof': prof, 'salon, 'salon': salon': salon, ', 'patronpatron': patron': patron, ', 'ini':ini': hora hora}
                if}
                if self._ self._costocosto_total(temp_total(temp_sol_sol, solo, solo_du_duros=Trueros=True) ==) == 0 0:
                   :
                    costo_ costo_comp =comp = self._ self._costo_compactcosto_compactacion(temp_sol)
                   acion(temp_sol)
                    mejores_opciones mejores_opciones.append.append((c((costo_osto_comp, patron,comp, patron, hora, hora, salon salon))
        
        if not))
        
        if not mejores_opciones mejores_opciones:
            return:
            return nuevo, nuevo, self._ self._costocosto_compact_compactacion(nacion(nuevouevo)
        mejores_op)
        mejores_opciones.sort(key=lambdaciones.sort(key=lambda x: x: x[0])
        _, x[0])
        _, patron, patron, hora, hora, salon salon = = mejores_op mejores_opciones[0ciones[0]
        nuevo]
        nuevo[idx][idx] = {' = {'seccionseccion': s': s, ', 'profesorprofesor': prof, '': prof, 'salonsalon': salon': salon, 'patron, 'patron': patron': patron, ', 'ini':ini': hora}
        return hora}
        return nuevo, self._ nuevo, self._costocosto_compact_compactacion(nacion(nuevo)

   uevo)

    def _ def _compactarcompactar_solucion(self_solucion, sol(self, sol, iter, iteraciones=aciones=20002000):
       ):
        if self._c if self._costo_totalosto_total(sol, solo(sol, solo_du_duros=Trueros=True) >) > 0 0:
           :
            return sol return sol
        
       
        
        actual = deepcopy(sol)
        actual = deepcopy(sol)
        mejor = mejor = deepcopy deepcopy(sol(sol)
       )
        costo_actual = costo_actual = self._ self._costocosto_compactacion(_compactacion(actualactual)
        mejor)
        mejor_costo = costo_costo = costo_actual_actual
       
        temp = 500 temp = 500.0.0
        
       
        
        for it for it in range in range(iter(iteracionesaciones):
            vec):
            vecino,ino, costo_vecino = costo_vecino = self._ self._mutar_compactmutar_compactacion(acion(actualactual)
            if costo_vec)
            ifino <= costo_ costo_vecino <= costo_actual oractual or random.random random.random()() < math.exp((c < math.exp((costo_osto_actual -actual - costo_vecino) costo_vecino) / temp / temp):
               ):
                actual actual = vecino = vecino
                costo_
                costo_actual =actual = costo_vec costo_vecinoino
                if costo_
                if costo_actualactual < mejor_c < mejor_costoosto:
                    mejor:
                    mejor = deepcopy( = deepcopy(actualactual)
                    mejor)
                    mejor_costo = costo_costo = costo_actual_actual
            temp *=
            temp *= 0 0.995.995
       
        return mejor return mejor

   

    # ----------------------------------------------------------------- # --------------------------------------------------------------------------
    #---------
    # FASE DE REP FASE DE REPARACIÓNARACIÓN AGR AGRESIVA REFORESIVA REFORZADAZADA (Gar (Garantizaantiza factibilidad factibilidad)
   )
    # ------------------------------------------------------------------------- # ------------------------------------------------------------------
    def---------
    def _re _reparar_solparar_solucion(selfucion(self, sol, sol, max, max_intentos_intentos=15=15):
        """
       ):
        """
        Intenta Intenta reparar reparar una solución una solución con conflict con conflictos duros mediante:
        - Destrucción de secciones conflictos duros mediante:
        - Destrucción de secciones conflictivas +ivas + aleator aleatoriasias.
        -.
        - Reins Reinserciónerción voraz voraz buscando solo hue buscando solo huecos concos con 0 0 conflictos.
        - B conflictos.
        - Búsquedaúsqueda local tab local tabú enfocadaú enfocada en conflict en conflictos dos durosuros.
        """
        mejor.
       _sol """
        mejor_sol = deepcopy(s = deepcopy(sol)
        mejorol)
        mejor_costo_costo = self = self._costo_total(me._costo_total(mejor_sjor_sol,ol, solo_ solo_durosduros=True=True)
        if)
        if mejor_costo == mejor_costo == 0 0:
            return mejor:
           _sol return mejor_sol

       

        # Par # Parámetros para bámetros para búsquedaúsqueda tabú tabú de repar de reparaciónación
        tabu_
        tabu_tenuretenure = 7 = 7
        tabu_list
        tab =u_list = {}
        max {}
        max_iter__iterrep =_rep = 2000 2000
        temp
        temp_rep_rep = 200. = 200.0

0

        for        for intento intento in range(max_int in range(max_intentosentos):
            #):
            # Identificar Identificar secciones secciones conflictivas conflictivas
            conflictivas
            conflictivas = set()
            = set()
            for idx, asign for idx in enumerate, asign in enumerate(me(mejor_sjor_sol):
ol):
                temp_sin                temp_sin = mejor = mejor_sol_sol[:idx] +[:idx] + mejor_s mejor_sol[idxol[idx+1+1:]
                if self._c:]
                if self._costo_totalosto_total(temp_s(temp_sin,in, solo_ solo_durosduros=True) < mejor_costo=True) < mejor:
                   _costo:
                    conflictivas conflictivas.add(idx.add(idx)
           )
            # Añadir un 20% # Añadir un 20% adicional ale adicional aleatorio paraatorio para romper romper bloqueos bloqueos
            no_conf
            no_conflictivaslictivas = = [i for i in [i for i in range(len range(len(mejor_s(mejor_sol))ol)) if i not in if i not in conflictivas conflictivas]
           ]
            extra_destru extra_destruir =ir = random.s random.sample(ample(no_confno_conflictivaslictivas, min(int(len, min(int(no(len(no_conflict_conflictivas)*0.ivas)*0.2),2), len( len(no_confno_conflictlictivas)))
           ivas)))
            a_destru a_destruir =ir = list( list(conflictconflictivas)ivas) + extra + extra_dest_destruir

           ruir

            # Mar # Marcar comocar como TBA
            TBA
            nuevo = nuevo = deepcopy deepcopy(mejor_s(mejor_solol)
            for)
            for idx in idx in a_destru a_direstruir:
                nuevo:
                nuevo[idx] = self[idx]._cre = self._crear_asignacionar_asignacion_temporal_temporal(nue(nuevo[idxvo[idx]['seccion'],]['seccion'], prof=" prof="TBATBA", salon", salon="T="TBA")

            #BA")

            # Reinsert Reinsertar greedyar greedy
           
            for idx for idx in a in a_destruir_destruir:
               :
                exito = self exito = self._as._asignar_seccionignar_seccion_greed_greedy_y_cero(idx,cero(idx, nuevo nuevo)
                if not ex)
                if not exitoito:
                    # Intentar:
                    # con búsqueda Intentar con búsqueda tabú tabú simple simple
                    self
                    self._re._repararparar_asign_asignacion_tabuacion_tabu(idx, nuevo, tab(idx, nuevo, tabu_u_tenuretenure)
)
            
            nuevo            
            nuevo_costo_costo = self._c = self._costo_totalosto_total(nuevo, solo_duros=True)
            if nuevo_c(nuevo, solo_duros=True)
            if nuevo_costoosto < mejor_costo:
                mejor < mejor_costo:
                mejor_sol = nuevo
                mejor_c_sol = nuevo
                mejor_costo =osto = nuevo_costo
                if nuevo_costo
                if mejor_costo == 0:
                    mejor_costo == 0:
                    break break

            # Si aún no es

            # Si aún no es factible factible, aplicar, aplicar recocido simulado enfocado en duros
            recocido simulado enfocado en duros
            if mejor_costo >  if mejor_costo > 00:
                actual = deepcopy(:
                actual = deepcopy(mejor_sol)
                costo_mejor_sol)
                costo_actual =actual = mejor_costo
                for mejor_costo
                for it in it in range(max_iter_ range(max_iter_reprep):
                    vecino,):
                    vecino, costo_vec costo_vecino = self._mutarino = self._mutar_solucion_solo__solucion_solo_duros(actual)
                    if costoduros(actual)
                    if costo_vecino <= costo_actual_vecino <= costo_actual or random.random() < math.exp(( or random.random() < math.exp((costo_actualcosto_actual - costo_vecino - costo_vecino) / temp_) /rep temp_rep):
                        actual):
                        actual = vec = vecinoino
                        costo
                        costo_actual = costo_actual_vecino = costo_vecino
                       
                        if costo if costo_actual_actual < mejor < mejor_costo_costo:
                            mejor_s:
                            mejor_sol =ol = deepcopy(actual deepcopy(actual)
                            mejor_c)
                           osto = mejor_costo = costo_ costo_actual
                            ifactual mejor_c
                            if mejor_costo ==osto == 0:
                                0:
                                break break
                    temp
                    temp_rep *= _rep *= 0.0.995995
                if mejor_c
                if mejor_costo ==osto == 0:
                    0:
                    break break
        return
        return mejor_s mejor_sol

    defol

    def _mut _mutar_sar_solucionolucion_solo_duros(self, sol_solo_duros(self, sol):
       ):
        """Mut """Mutación queación que solo eval solo evalúa conflictúaos d conflictos duros,uros, ignorando prefer ignorando preferenciasencias suaves suaves."""
       ."""
        nuevo = deepcopy nuevo = deepcopy(sol)
       (sol)
        idx = idx = random.randint random.randint(0(0, len, len(nue(nuevo)-vo)-11)
        s)
        s = nuevo = nuevo[idx]['[idx]['seccionseccion']
        prof_actual =']
        prof_actual = nuevo[idx nuevo[idx]['prof]['profesoresor']

        cand']

        cand_profs_profs = = [p for [p for p in p in s.c s.cands ifands if p in p in self.profes self.profesoresores]
        if not cand]
        if not cand_profs_profs:
           :
            cand_profs = cand_profs = ["GR ["GRADUADUADOS"] ifADOS"] if "GR "GRADUADOSADUADOS" in" in s.c s.cands elseands else ["T ["TBABA"]
        
       "]
        
 mejores_op        mejores_opciones =ciones = []
        []
        for _ in range for _ in range(30):
           (30):
            prof = prof = random.choice random.choice(cand_profs(cand_profs)
           )
            patrones patrones = PATRONES.get(s = PATRONES.get(s.cred.creditos,itos, PATRON PATRONESES[3])
            if[3])
            if prof in prof in self.pro self.profesfesoresores:
                prof:
                prof_obj =_obj = self.pro self.profesfesores[profores[prof]
                patron]
                patrones =es = [p [p for p in patron for p in patrones if not (es if not (prof_objprof_obj.cursos.cursos_intens_intensivos ==ivos == 0 0 and any and any(c >=(c >= 3 for c 3 for c in p['days in p['days'].values'].values()))]
                if()))]
                if prof_obj prof_obj.cursos_intens.cursos_intensivos ==ivos == 1:
                    1:
                    intensivos intensivos = = [p for [p for p in p in PATRON PATRONES.get(s.ES.get(s.creditoscreditos, PATRONES[3]) if any(c, PATRONES[3]) if any(c >=  >= 3 for3 for c in c in p['days']. p['days'].values())values())]
                   ]
                    if intens if intensivosivos:
                        patrones =:
                        patrones = intensivos intensivos + + [p for [p for p in p in patrones if not any(c >= 3 patrones if not any(c >= 3 for for c in c in p[' p['days'].values())days'].values())]
            if not]
            patrones if not patrones:
               :
                patrones = PAT patrones = PATRONESRONES.get(s.get(s.cred.creditos, PATRONitos, PATRONESES[3[3])

            patron = random])

            patron = random.choice(.choice(patrones)
           patrones)
            horas_pos horas_posibles =ibles = set(self set(self.bloques.bloques)
            for)
            for dia, contrib in dia, contrib in patron['days']. patron['days'].itemsitems():
                du():
                duracionracion = contrib = contrib *  * 50
                horas50
                horas_dia =_dia = [h for [h for h in h in self.bl self.bloquesoques if h >= self if h >= self.lim.limite_ite_operativo[0operativo[0] and] and h + h + duracion <= duracion <= self.l self.limiteimite_oper_operativoativo[1]]
                if[1]]
                if dia in dia in ["Ma ["Ma", "Ju"]", "Ju"]:
                    horas_d:
                    horas_dia =ia = [h for h [h for h in horas in horas_dia_dia if not if not (max (max(h,(h, self.hora_un self.hora_universaliversal[0])[0]) < min(h < min(h+du+duracion, selfracion, self.hora.hora_universal_universal[1]))[1]))]
               ]
                if s if s.cred.creditos ==itos == 3 3 and contrib and contrib >=  >= 33:
                    horas:
                    horas_dia_dia = = [h for h in [h for h in horas_d horas_dia ifia if h >= h >= 930 930]
                horas_pos]
                horas_posibles =ibles = horas_pos horas_posibles.intersection(set(horasibles.intersection(set(horas_dia_dia))
               ))
                if not horas_pos if not horas_posibles:
                    breakibles
           :
                    break
            if not if not horas_posibles horas_posibles:
                continue:
                continue
           
            hora = random.choice hora =(list( random.choice(list(horashoras_posibles))
_posibles))
            
            if            
            if prof in self.pro prof infesores self.profesores:
                prof:
                prof_obj = self.pro_obj = self.profesfesoresores[prof]
                if[prof prof_obj]
                if prof_obj.hora.hora_ent_entrada_min is notrada_min is not None and None and hora < prof_obj hora < prof_obj.hora_ent.hora_entrada_min:
                   rada_min:
                    continue continue
                fin
                fin_bloque_bloque = hora = hora + max([contrib + max * ([contrib * 50 for50 for contrib in contrib in patron['days']. patron['days'].values()values()])
               ])
                if prof if prof_obj.h_obj.hora_sora_salidaalida_min is_min is not None not None and fin_bloque and fin_bloque > prof > prof_obj.h_obj.hora_salidaora_salida_min_min:
                    continue:
                    continue

            salones

            salones_cand_cand = = [sl['CODIG [sl['CODIGO'] for slO'] for sl in self in self.salones.salones
                            if
                            if compatible_tipo(s compatible_tipo(s.tip.tipos_peros_permitidos, slmitidos, sl['T['TIPO']) and slIPO']) and sl['CAP['CAPACIDAD'] >=ACIDAD'] >= s.c s.cupo]
           upo]
            if not salones if not salones_cand_cand:
               :
                continue
            salon continue
            salon = random = random.choice(s.choice(salonesalones_cand_cand)

            # Solo)

            # Solo evaluar conflictos evaluar conflictos duros duros
           
            temp_asign = temp_asign = {'se {'seccion':ccion': s, s, 'prof 'profesor':esor': prof, prof, 'salon': 'salon': salon, salon, 'pat 'patron': patron,ron': patron, 'ini 'ini': hora': hora}
           }
            temp_s temp_sol = sol[:ol = sol[:idx]idx] + + [temp_as [temp_asign]ign] + sol[idx+ + sol[idx+11:]
            costo_du:]
            costo_duros =ros = self._costo self._costo_total(temp_total(temp_sol_sol, solo_du, solo_duros=Trueros=True)
            mejores_op)
            mejores_opciones.appendciones.append((c((costo_durososto_, profduros, prof, patron, hora, patron, salon, hora, salon))
        
        if))
 not mejores_opciones        
        if not mejores_opciones:
            return nuevo, self._costo_total:
            return nuevo, self._costo_total(nue(nuevo, solo_durosvo, solo_duros=True)
        mejores_opciones=True)
        mejores_opciones.sort(key=lambda x: x[0.sort(key=lambda x: x[0])
       ])
        mejor = mejores_opciones[0 mejor = mejores_opciones[0]
        nuevo[idx] = {'seccion]
        nuevo[idx] = {'seccion': s, 'profesor': mejor[1], 'salon': mejor': s, 'profesor': mejor[1], 'salon': mejor[4], 'patron': mejor[4], 'patron': mejor[2], 'ini': mejor[2], 'ini': mejor[3]}
        return nuevo, mejor[3]}
        return nuevo, mejor[0]

    def _asignar[0]

    def _asignar_seccion_seccion_greedy_cero_greedy_cero(self, idx, sol(self, idx, sol):
        """):
        """Intenta asignarIntenta asignar la se la sección idx a uncción idx a un slot que cause 0 conflict slot que cause 0 conflictos dos duros."""
        suros."""
        s = sol = sol[idx]['seccion']
       [idx]['seccion']
        cand_pro cand_profs =fs = [p [p for p for p in s.cands in s.cands if p if p in self.prof in selfesores.profesores]
       ]
        if not cand_pro if not cand_profs:
            candfs:
            cand_profs_profs = ["GRAD = ["GRADUADUADOS"]OS"] if " if "GRADGRADUADOS"UAD in sOS" in s.cands.cands else ["TBA"]
        cand_profs.sort else ["TBA"]
        cand_profs.sort(key=lambda(key=lambda p: (
             p: (
            0 if0 if (p in self (p in self.profes.proforesesores and s and s.es_g.es_grande andrande self.pro and self.profesfesores[p].aceores[p].acepta_grandespta_grandes ==  == 1)1) else  else 1,
            -(1,
            -(self.profesores[p].priorself.profesores[p].prioridad_idad_curso(scurso(s.cod) if.cod) if p in p in self.pro self.profesfesores elseores else 0 0)
       )
        ))
        ))
        for prof for prof in cand in cand_profs_profs:
           :
            patron patrones = PATes = PATRONESRONES.get(s.get(s.creditos,.creditos, PATRON PATRONES[3ES[3])
           ])
            if if prof in prof in self.profesores self.profesores:
                prof_obj =:
                prof_obj = self.pro self.profesfesoresores[prof]
                patron[prof]
                patrones =es = [p [p for p in patron for p in patrones ifes if not (prof_obj not (prof_obj.cursos_intens.cursos_intensivos ==ivos == 0 0 and any(c >= 3 and any(c >= 3 for c for c in p['days in p['days'].values()))'].values()))]
                if prof_obj]
                if prof_obj.cursos.cursos_intensivos ==_intensivos == 1 1:
                   :
                    intensivos = intensivos = [p for [p for p in PATRON p in PATRONES.getES.get(s.(s.creditoscreditos, PATRONES, PATRONES[3[3]) if any(c]) if any(c >=  >= 3 for3 for c in p[' c in p['days'].days'].values())values())]
                    if intens]
                    if intensivosivos:
                        patrones =:
                        patrones = intensivos intensivos + [p for + [p for p in p in patrones patrones if not if not any(c >= 3 for any(c >= 3 for c in c in p[' p['days'].days'].values())]
           values())]
            if not if not patrones patrones:
               :
                patrones patrones = PAT = PATRONESRONES.get(s.get(s.cred.creditos, PATRONESitos, PATRONES[3[3])
            random])
            random.shuffle(pat.shuffle(patronesrones)
            for patron in patrones)
            for patron in patrones:
               :
                horas_pos horas_posibles = list(selfibles = list(self.blo.bloquesques)
                for)
                for dia, dia, contrib in contrib in patron[' patron['days'].days'].items():
                    duitems():
                    duracionracion = contrib * 50 = contrib * 50
                    horas
                    horas_dia = [h for_dia = [h for h in h in self.bl self.bloques if hoques if h >= self >= self.limite_.limite_operativo[0operativo] and h +[0] and h + durac duracion <=ion <= self.l self.limiteimite_oper_operativoativo[1]]
                    if[1]]
                    if dia in dia in ["Ma ["Ma", "Ju"]", "Ju"]:
                        horas_d:
                        horas_dia = [ia =h [h for h for h in horas in horas_dia if not_dia (max if not (max(h, self.h(h, self.hora_unora_universal[0iversal[0])]) < min(h < min(h+du+duracion, self.horaracion, self.hora_universal_universal[1]))[1]))]
                   ]
                    if s if s.creditos ==.creditos == 3 3 and contrib and contrib >=  >= 33:
                        horas:
                        horas_dia_dia = = [h [h for for h in horas_dia if h in horas_dia if h >= h >= 930]
                    930]
                    horas_posibles = horas_posibles = [h [h for h for h in horas in horas_posibles_posibles if h in horas if h in horas_dia]
                   _dia]
                    if not if not horas_posibles horas_posibles:
                        break:
                        break
               
                if not horas_pos if not horas_posibles:
                    continueibles:
                    continue
                random.sh
                random.shuffle(uffle(horas_posibleshoras_posibles)
               )
                for hora in horas_posibles for hora in horas_posibles:
                   :
                    if prof in self if prof in self.profesores.profesores:
                       :
                        prof_obj prof_obj = self.prof = self.profesoresesores[prof]
                       [prof]
                        if prof if prof_obj.h_obj.hora_entradaora_entrada_min is_min is not None and hora not None and hora < prof < prof_obj.hora__obj.hentradaora_entrada_min:
                            continue_min:
                            continue
                        fin_bl
                        fin_bloque =oque = hora + hora + max([contrib * max([contrib * 50 for contrib 50 for contrib in patron in patron['days['days'].values()'].values()])
                        if])
                        if prof_obj.hora prof_obj.hora_sal_salida_minida_min is not is not None and None and fin_bloque > prof_obj fin_bloque >.hora prof_obj_sal.hora_salida_min:
                           ida_min:
                            continue continue
                    
                    salones_cand
                    
                    salones_cand = = [sl[' [sl['CODIGO']CODIGO'] for sl for sl in self.sal in self.salones
                                    ifones
                                    if compatible_t compatible_tipo(s.tipipo(s.tipos_peros_permitidosmitidos, sl, sl['TIPO']) and sl['CAP['TIPO']) and sl['CAPACIDAD'] >= s.cACIDAD'] >= s.cupoupo]
                    random.shuffle(s]
                    random.shuffle(salonesalones_cand)
                   _cand)
                    for salon for salon in in sal salones_cand:
                        conflicones_cand:
                        conflicto =to = False False
                        for j,
                        for j, asign2 asign2 in enumerate(sol):
                            in enumerate(sol):
                            if j if j != idx and asign != idx and asign2 and2 and asign2 asign2['prof['profesor']esor'] != " != "TBATBA":
                               ":
                                if asign2[' if asign2['profesor'] ==profesor'] == prof prof:
                                    for:
                                    for dia2, contrib dia2, contrib2 in2 in asign2['patron'][' asign2['patron']['days'].itemsdays'].items():
                                        if():
                                        if dia2 in patron dia2 in patron['days['days']']:
                                            fin_actual:
                                            fin_actual = hora + int = hora + int(pat(patron['daysron[''][dia2days'][dia2] *] * 50 50)
                                            fin_ex)
                                            fin_exist =ist = asign2 asign2['ini['ini'] +'] + int( int(contrib2 * contrib250)
                                            if * 50)
                                            if max(h max(hora,ora, asign2['ini asign2['ini'])']) < min(fin_ < min(fin_actual,actual, fin_ex fin_exist):
                                                conflicist):
                                                conflicto =to = True
                                                break True
                                                break
                               
                                if asign2[' if asign2['salon'] ==salon'] == salon:
                                    for salon:
                                    for dia2 dia2, contrib2 in, contrib2 in asign2 asign2['pat['patron']['days'].ron']['days'].items():
                                        ifitems():
                                        if dia2 in patron dia2 in patron['days['days']']:
                                            fin:
                                            fin_actual_actual = hora + int = hora(pat + int(patron['ron['daysdays'][dia2] * 50'][dia2] * 50)
                                            fin_ex)
                                            fin_exist = asign2ist = asign2['ini['ini'] + int(contrib2 * 50)
                                            if max(h'] + int(contrib2 * 50)
                                            if max(hora,ora, asign2['ini']) asign2['ini']) < min(fin_actual, < min(fin_actual, fin_exist):
                                                if salon in fin_exist):
                                                if salon in self.m self.mega_salones and sega_salones and s.es_f.es_fusionable and asign2['usionable and asign2['seccionseccion'].es_fusionable:
                                                    if s.cupo + asign'].es_fusionable:
                                                    if s.cupo + asign2['2['seccion'].cupo <=seccion'].cupo <= self.s self.salon_capacidad.get(salon_capacidad.get(salon,alon, 0):
                                                        continue 0):
                                                        continue
                                                conflicto = True
                                                conflicto = True
                                                break
                                if conflicto
                                                break
                                if conflicto:
                                    break
                        # Ver:
                                    break
                        # Verificar doble rol
                       ificar doble rol
                        if not conflicto and prof if not conflicto and prof in self in self.graduados_reciben.graduados_reciben:
                            for:
                            for r_asign in r_asign in sol sol:
                                if r_as:
                                if r_asign and r_asign and r_asign != asign2ign != and r_asign asign2 and r_asign['prof['profesor'] != "TBAesor'] != "TBA":
                                   ":
                                    cod_base cod_base_r =_r = r_asign[' r_asign['seccionseccion'].cod'].cod.split('-')[0.split('-')[0].upper].upper()
                                    if cod()
                                    if cod_base_r in self_base_r in self.gradu.graduados_recados_reciben[profiben[prof]:
                                        for]:
                                        for dia_d dia_d, contrib_d in, contrib_d in patron['days']. patron['days'].itemsitems():
                                            if dia_d():
                                            if dia_d in r in r_asign['pat_asign['patron']['days']ron']['days']:
                                               :
                                                ini_d = hora
                                                ini_d = hora
                                                fin_d fin_d = ini_d + = ini_d + int( int(contrib_d * 50)
                                                inicontrib_d * 50)
                                                ini_r =_r = r_as r_asign['iniign['ini']
                                               ']
                                                fin fin_r =_r = ini_r + int ini_r + int(r_as(r_asign['patronign['patron']['days']['days'][dia'][dia_d] * _d] * 5050)
                                                if max()
                                                if max(ini_d, iniini_d, ini_r)_r) < min(fin < min(fin_d,_d, fin_r):
                                                    fin_r):
                                                    conflicto conflicto = True
                                                    = True
                                                    break break
                                        if conflicto
                                        if conflicto:
                                            break:
                                           
                            if break
                            if conflicto:
                                conflicto:
                                continue continue
                        if
                        if not conflic not conflicto:
                            solto:
                            sol[idx][idx] = {' = {'seccionseccion': s': s, ', 'profesor': prof, 'profesor': profsalon, 'salon': salon': salon, 'patron': patron, ', 'patron': patron, 'ini': horaini': hora}
                            return}
                            return True True
        return
        return False False

    def _reparar

    def _reparar_asign_asignacion_tabu(selfacion_tabu(self, idx, idx, sol, tenure, sol):
       , tenure):
        """Búsqueda tabú """Búsqueda simple para tabú simple para una sola una sola sección conflictiva."""
        sección conflictiva."""
        s = sol[idx s =]['se sol[idx]['ccionse']
        mejor_asignccion']
        mejor_asign = None
        mejor_c = None
       osto = mejor_costo = float(' float('inf')
        tabinf')
        tabu = setu = set()
()
        for _ in        for range( _ in range(5050):
            cand_profs):
            cand_profs = = [p for [p for p in p in s.c s.cands ifands if p in p in self.pro self.profesfesores]ores] or ["GRAD or ["GRADUADUADOS"]OS"] if " if "GRADGRADUADOS" in s.cands else ["TBA"]
            prof =UADOS" in s.cands else ["TBA"]
            prof = random.choice random.choice(cand(cand_profs_profs)
            patrones)
            patrones = PAT = PATRONESRONES.get(s.cred.get(s.creditos,itos, PATRON PATRONESES[3[3])
            if prof in])
            if prof in self.pro self.profesoresfesores:
                prof_obj =:
                prof_obj = self.profes self.profesores[prof]
                patronores[prof]
                patrones =es = [p [p for p for p in patron in patrones if not (prof_objes if not (prof_obj.cursos.cursos_intensivos == 0_intensivos == 0 and any(c >= and any(c >= 3 3 for c for c in p['days'].values()))]
            if in p['days'].values()))]
            if not patron not patrones:
                patrones:
                patrones = PATRONes = PATRONES.get(s.creditosES.get(s.creditos, PAT, PATRONES[3])
           RONES[3])
            patron = patron = random.choice(pat random.choice(patrones)
            hora = randomrones)
            hora = random.choice(self.blo.choice(self.bloquesques)
            
            if prof)
            
            if prof in self in self.profesores:
               .profesores:
                prof_obj prof_obj = self = self.prof.profesores[profesores[prof]
               ]
                if prof_obj.h if prof_obj.hora_entradaora_entrada_min is not None and hora_min is not None and hora < prof_obj.h < prof_obj.hora_ora_entrada_minentrada_min:
                    continue:
                    continue
                fin_bloque =
                fin_bloque = hora + max hora + max([contrib *([contrib * 50 for contrib 50 for contrib in patron in patron['days['days'].values()'].values()])
                if])
                if prof_obj prof_obj.hora_salida_min.hora_salida_min is not is not None and None and fin_bloque > fin_bloque > prof_obj.hora prof_obj.hora_sal_salida_minida_min:
                   :
                    continue continue
            
            sal
            
            salones_cand = [slones_cand = [sl['CODIGO['CODIGO'] for'] for sl in sl in self.salones self.s if compatible_tipoalones if compatible_tipo(s(s.tipos.tipos_permit_permitidos, sl['TIPOidos, sl['']) and sl['TIPO']) and sl['CAPACCAPACIDAD']IDAD'] >= s >= s.cupo.cupo]
            if not salones_c]
            if not salones_candand:
                continue:
                continue
            salon =
            salon = random.choice(sal random.choiceones_c(salones_candand)
            key = ()
            key = (prof,prof, patron['name'], patron['name'], hora, hora, salon)
            if salon)
            if key in tabu key in tabu:
               :
                continue
            temp continue
            temp_asign = {'_asign = {'seccionseccion': s, 'profesor': s, 'profesor': prof': prof, 'salon, 'salon': salon': salon, ', 'patronpatron': patron, '': patron, 'ini':ini': hora hora}
            temp_sol}
            temp_sol = sol[:idx = sol[:idx] +] + [temp_asign [temp_asign] +] + sol[idx sol[idx+1+1:]
            costo =:]
            costo = self._costo self.__total(temp_solcosto_total(temp_sol, solo, solo_du_duros=Trueros=True)
            if costo)
            if costo < mejor < mejor_costo:
                mejor_c_costo:
                mejor_costo =osto = costo costo
                mejor_asign
                mejor_asign = temp = temp_asign_asign
                if costo == 
                if costo0 == 0:
                    break
            tabu:
                    break
            tabu.add(key.add(key)
            if len)
            if len(tabu) >(tabu) > tenure tenure:
                tab:
                tabu.popu.pop()
        if mejor_asign()
        if mejor_asign:
            sol[idx:
            sol[idx] = mejor_as] =ign mejor_asign



    def optimizar    def(self, optimizar(self, iteraciones=300 iteraciones=3000, bar=None0,, status_text=None bar=None, status):
        temp_in_text=None):
        temp_inicial = 500icial = 5000.0.00
        self
        self.hist.historial_costos =orial_cost [self.mejoros = [self.mejor_costo_costo]
        for it]
        for it in range in range(iter(iteraciones):
           aciones vecino, costo_vec):
            vecino,ino = self._ costo_vecino = self._mutar_solmutar_solucion(selfucion(self.solucion.solucion)
            if)
            if costo_vec costo_vecino <=ino <= self.mejor_costo self.mejor_costo:
                self:
                self.sol.solucion = vecinoucion = vecino
               
                self.mejor_c self.mejor_costo =osto = costo_vec costo_vecino
                selfino
                self.mejor_sol.mejor_solucion =ucion = deepcopy(self.solucion deepcopy(self.solucion)
           )
            else else:
                temp = temp_inicial:
                temp = temp_in / (icial / (it +it + 1)
                try 1)
               :
                    prob try:
                    prob = math.exp(( = math.exp((self.mejor_cself.mejor_costo - costo_vecosto - costo_vecino)ino) / temp)
                / temp)
                except:
                    prob except = 0:
                    prob = 0
                if random.random
                if random.random() < prob:
                    self() < prob:
                    self.sol.solucion = vecinoucion = vecino
           
            self.historial_costos self.historial_costos.append(self.mejor.append(self.mejor_costo_costo)
            if it % )
            if it % 10 == 0 or it10 == 0 or it == iteraciones - == iter 1:
               aciones - 1:
                if status_text if status:
                    d_text:
                    duros = int(selfuros = int(self.mejor_costo.mejor_costo //  // 1000010000)
                   )
                    costo_total costo_total = self = self.mejor.mejor_costo
                    fitness__costo
                   actual = 100 fitness_actual = 10000 / (10000 /00 + (10000 + costo_total costo_total)
                    costo_s)
                    costo_suaveuave = costo_total - = costo_total - (duros * (duros * 100 10000)
                    if00 costo_total > )
                    if costo_total > 0:
                        p0:
                        pct_suave = (ct_suave = (costocosto_suave /_suave / costo_total costo_total) *) * 100 100
                    else
                    else:
                        pct_s:
                        pct_suaveuave = 0.0 = 0.0
                    status
                    status_text.markdown(
                        f_text.markdown"**(
                        f"**🔄 Fase 1 Gen {🔄 Fase 1 Gen {it+it+1}/{iteraciones1}/{iteraciones}**}** | "
                        f"Conflict | "
                        f"Conflictos Dos Duros: {duros} | Costuros: {duros} | Costo Total: {costo_total:.o Total: {costo_total:.2f} | "
                        f"2f} | "
                        f"FitnessFitness: {fitness_actual:.5: {fitness_actual:.5f} | % Suave: {f} | % Suave: {pct_suave:.1fpct_suave:.1f}%"
                    )
                if bar:
                   }%"
                    )
                if bar:
                    bar.progress((it+1)/( bar.progress((it+1)/(iteracionesiteraciones+2000))
        
       +2000))
        
        # --- FASE DE REPARACIÓN # --- FASE DE REPARACIÓN AGR AGRESIVAESIVA REFOR REFORZADA ---
        ifZADA ---
        if self._ self._costo_total(self.mejorcosto_total(self.mejor_solucion, solo__solucion, solo_durosduros=True) > =True) > 00:
            if status_text:
            if status_text:
               :
                status_text.markdown status_text.markdown("**🔧("**🔧 Fase Fase de Rep de Reparaciónaración Intens Intensiva (iva (búsbúsqueda tabqueda tabú +ú + recocido)... recocido)...**")
            self**")
            self.mejor_sol.mejor_solucion =ucion = self._ self._reparar_sreparar_solucion(self.meolucion(self.mejor_sjor_solucion, maxolucion, max_intentos_intentos=20=20)
            self.me)
            self.mejor_costo =jor_costo = self._costo self._costo_total(self.mejor_total(self.mejor_sol_solucion)
            selfucion)
            self.hist.historial_costos.appendorial_costos.append(self.me(self.mejor_costojor_costo)
            if bar)
            if bar:
                bar.progress:
                bar.progress(0(0.95)
.95)
        
        #        
        # Fase de compact Fase de compactaciónación
        if self._
        if self._costocosto_total(self_total(self.mejor_sol.mejor_solucion, solo_ucion, solo_durosduros=True)=True) ==  == 00:
            if status_text:
               :
            if status_text:
                status_text status_text.markdown.markdown("**✨ Fase ("**✨ Fase 2: Compactación2: Compactación de horarios ( de horarios (mejormejorando organización)...**ando organización)...**")
           ")
            self.mejor_s self.mejor_solucion = selfolucion = self._compact._compactar_sar_solucion(self.meolucion(self.mejor_sjor_solucionolucion, iter, iteraciones=2000)
           aciones=2000)
            self.me self.mejor_cjor_costo =osto = self._costo self._costo_total(self_total(self.mejor.mejor_solucion_solucion)
            if bar)
            if bar:
                bar:
                bar.progress(1.progress(1.0.0)
)
        
        return self.mejor_s        
        return self.meolucionjor_solucion, int(self.me, int(self.mejor_cjor_costo //osto // 100 10000),00), self.historial self.historial_costos

#_costos

# ========================================================================= ==================================================================================
# =
# 5. FUNC5.IONES FUNCIONES DE VISUALIZ DE VISUALIZACIÓNACIÓN
# =============================================================================
# ==============================================================================
def generar_=
def generar_heatmapheatmap_plotly(s_plotly(scheduler,cheduler, solucion solucion):
   ):
    dias_s dias_semana = ['emana = ['Lu',Lu', 'Ma', ' 'Ma', 'Mi', 'JuMi', 'Ju', 'Vi', 'Vi']
    inicio']
    inicio = scheduler = scheduler.limite_operativo[0]
    fin = scheduler.l.limite_operativo[0]
    fin = scheduler.limiteimite_oper_operativoativo[1[1]
    horas_del]
    horas_del_dia = list_dia = list(range(inicio,(range(inicio, fin + fin + 1, 30 1, 30))
    
   ))
    
    matriz = np.zeros matriz = np.zeros((len(hor((lenas_d(horas_del_dia),el_dia), len(d len(dias_sias_semanaemana)))
   )))
    total_salones total_salones = len = len(scheduler.sal(scheduler.salones)
    
   ones for asign)
    
    for asign in solucion in sol:
        salon = asignucion:
        salon = asign['sal['salon']
        ifon salon ==']
        if salon == "T "TBA":
            continueBA":
            continue
       
        patron = patron = asign[' asign['patron']
       patron']
        ini = ini = asign[' asign['ini']
        forini']
        for dia, contrib dia, contrib in patron['days']. in patron['days'].itemsitems():
            if():
            if dia not dia not in dias in dias_semana_semana:
                continue:
                continue
            dia_idx
            dia_idx = dias_sem = diasana.index(dia_semana.index(dia)
            durac)
            duracion =ion = int( int(contrib *contrib * 50 50)
           )
            for minuto in for minuto in range(ini, range(ini, ini + durac ini + duracion,ion, 30 30):
                if min):
               uto in if minuto in horas_del_d horas_dia:
                    horael_dia:
                    hora_idx = horas_d_idx = horas_del_del_dia.index(minutoia.index(minuto)
                   )
                    matriz[hora_idx, dia matriz[hora_idx, dia_idx]_idx] += 1
    
    if += 1
    
    if total_s total_salones > 0alones > :
        matriz0:
        matriz_porcentaje = (_porcentaje = (matrizmatriz / total_s / totalalones) * 100
    else:
        matriz__salones) * 100
    else:
        matriz_porcentporcentaje =aje = matriz
    
    et matriz
    
    etiquetasiquetas_horas_horas = = [mins_to_str(h [mins_to_str(h).replace).replace(' AM', '').replace(' AM', ''(' PM).replace(' PM', '') for', '') for h in horas_d h in horas_del_del_diaia]
    
    fig =]
    
    fig = px.imshow px.imshow(
        matriz_por(
        matriz_porcentaje,
       centaje labels=dict(x,
        labels=dict(x="D="Día", y="ía", y="HoraHora de Inicio", de Inicio", color=" color="% Ocupación% Ocupación"),
        x=d"),
        x=dias_semana,
        y=ias_semana,
       etiqu y=etiquetas_hetas_horasoras,
        color,
        color_continuous_scale_continuous_scale='Y='YlOrlOrRd',
        aspect='autoRd',
        aspect='auto',
       ',
        zmin=0 zmin=0,
       ,
        zmax zmax=100
   =100
    )
    fig.update )
    fig.update_layout_layout(
        title(
        title="O="Ocupación de Salcupación de Salones porones por Día Día y Hora y H",
        fontora",
        font=dict=dict(color='(color='#000#000000'),
        paper000'),
        paper_bgcolor='_bgcolor='white',
        plot_bgwhite',
        plot_bgcolor='color='white',
        heightwhite=600
   ',
        height=600 )
   
    return fig

def )
    return fig generar_barras

def generar_b_aparras_apiladas_profiladas_profesor(sol,esor(sol, scheduler):
    df scheduler_asign):
    df_asign = pd = pd.DataFrame.DataFrame([{
        'Prof([{
        'Profesor':esor': a['profesor'],
        a['profesor 'D'],
        'Dia': diaia': dia,
        'Cantidad':,
        'Cantidad': 1 1
    } for
    } for a in a in sol if sol if a[' a['profesor'] not in ['profesor'] not in ['TBATBA', 'GRAD', 'GRADUADOSUADOS']
      for']
      for dia in dia in a['patron']['days a['patron']['days'].keys()])
    
    if df'].keys()])
    
    if df_asign_asign.empty:
        return.empty:
        return go. go.FigureFigure()
    
   ()
    
    pivot = df_as pivot = df_asign.groupby(['ign.groupby(['ProfesorProfesor', '', 'DiaDia']).']).size().reset_indexsize().reset_index(name='Clases(name='Clases')
    carga_pro')
    carga_prof = {pf = {p: 0.: 0.0 for0 for p in p in pivot[' pivot['ProfesorProfesor'].unique'].unique()()}
    for a in}
    for a in sol:
        if sol:
        a[' if a['profesorprofesor'] in'] in carga_prof carga_prof:
            carga:
            carga_prof[a['_prof[a['profesor']] += schedulerprofesor']] += scheduler.get_sec_.get_creditossec_creditos(a['(a['seccionseccion'], a['prof'], a['profesor'])
    profesesor'])
    profes_ordenados =_ordenados = sorted(c sorted(carga_prof.keysarga_prof.keys(), key(), key=lambda x: carga_prof[x], reverse=True=lambda x: carga_prof[x], reverse=True)
    
    fig = go)
    
    fig = go.Figure()
    dias_unicos.Figure()
    dias_unicos = ['Lu', 'Ma', ' = ['Lu', 'Ma', 'Mi', 'Ju', 'Mi', 'Ju', 'Vi']
    colores = px.colors.qualitative.Set2[:len(diasVi']
    colores = px.colors.qualitative.Set2[:len(dias_unicos)]
    
    for i, dia in enumerate(dias_unicos)]
    
    for i, dia in enumerate(dias_unicos):
        data_dia_unicos):
        data_dia = pivot = pivot[pivot['Dia'] == dia[pivot['Dia'] == dia]
        y_vals = [data_dia[data]
        y_vals = [data_dia[data_dia_dia['Prof['Profesor'] == pesor'] == p]['Clases'].sum() if p]['Clases'].sum() if p in data_dia in data_dia['Prof['Profesor'].esor'].values else 0 for pvalues else 0 in profes for p in profes_ordenados_ordenados]
        fig.add_t]
        fig.add_trace(go.Brace(go.Barar(
            name(
            name=dia=dia,
            x=,
            x=profes_ordenprofes_ordenados,
            yados,
            y=y_vals=y_vals,
            marker_color=,
            marker_color=colores[i]
       colores[i]
        ))
    
    fig.update ))
    
    fig.update_layout_layout(
        barmode(
        barmode='stack='stack',
       ',
        title="Distribución de title="Distribución de Clases Clases por Profesor y por Profesor y Día Día",
        xaxis",
        xaxis_title="Profesor_title="Profesor",
        yaxis",
        yaxis_title="Número_title="Número de Cl de Clases",
        font=dictases",
        font=dict(color='(color='#1#1a1a1a1a1aa'),
        paper'),
        paper_bgcolor='_bgcolor='white',
        plotwhite',
        plot_bgcolor='_bgcolor='whitewhite',
        legend_title="Día',
        legend_title="Día",
        height=",
       500
    height=500
    )
    return fig )
    return fig

def generar

def generar_ev_evolucionolucion_fitness_plotly(_fitness_plotly(historial):
   historial fitness =):
    fitness = [10000 / [10000 / (10000 + (10000 + c) for c c) for c in histor in historialial]
    fig]
    fig = go.Figure()
    = go.Figure()
    fig.add fig.add_trace_trace(go.Scatter(go.Scatter(
        y=f(
        y=fitness,
        modeitness,
        mode='lines+mark='lines+markersers',
        line=dict',
        line(color='=dict(color='#D4AF37', width=#D4AF37', width=3),
        marker3),
        marker=dict=dict(size=4,(size=4, color='#8 color='#8E6E13E6E13'),
       '),
        fill=' fill='tozertozeroyoy',
        fillcolor',
        fillcolor='rg='rgba(ba(212, 175, 212, 17555, 0, 55,.2 0.2))',
        name',
        name='F='Fitness'
   itness'
    ))
    fig.update_layout ))
    fig.update_layout(
        title="(
        title="Evolución delEvolución del Fitness durante Fitness durante la Optim la Optimización",
        xización",
        xaxis_titleaxis_title="Iteración="Iter",
        yaxis_titleación",
        y="Faxis_title="Fitness (itness (1.1.0 =0 = Ópt Óptimo)",
        fontimo)",
        font=dict(color='=dict#1(color='#1a1a1a', size=a1a1a', size=1212),
       ),
        paper_bg paper_bgcolor='color='white',
        plotwhite',
        plot_bgcolor='_bgcolor='whitewhite',
        height',
        height=450=450,
       ,
        hovermode hovermode='x unified='x unified'
    )
    fig'
    )
    fig.update_x.update_xaxes(showgridaxes(showgrid=True, gridwidth=True, gridwidth=1=1, gridcolor=', gridcolor='LightGrayLightGray')
    fig.update_yaxes')
    fig.update_yaxes(showgrid=True(showgrid=True, gridwidth=, gridwidth=1,1, gridcolor gridcolor='Light='LightGray')
    return figGray')
    return

def generar fig_calendario

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
def generar_reporte fig

def generar_reporte_pdf_pdf_html(s_html(scheduler, sol,cheduler, sol, cargas cargas_final_finales, master_dfes, master_df):
   ):
    total_secciones = total_secciones = len(s len(solol)
    se)
    secciones_tba =cciones_tba = sum( sum(1 for1 for a in a in sol if a[' sol if a['profesorprofesor'] == 'T'] == 'TBA')
    carga_total = sum(cargas_fBA')
    carga_total = sum(cargas_finales.valuesinales.values())
    profes())
    profesores_conores_con_carga_carga = len = len([c for c([c for c in cargas_f in cargas_finalesinales.values() if c.values() if c > 0 > 0])
    
    html =])
    
    html = f f"""
   """
    <html>
    <html>
    <head>
        <head>
        <title> <title>Reporte EjecReporte Ejecutivo -utivo - UPRM S UPRM Scheduler</cheduler</title>
       title>
        <style>
            body <style>
            body {{ font-family: {{ font-family: 'Segoe UI', A 'Segoe UI', Arial, sans-serifrial, sans-serif; margin: ; margin: 40px; background40px; background: white; color: white; color: #: #1a1a1a1a1a1a; }}
            h1 {{; }}
            h1 {{ color: #1a1 color: #1a1a1a; border-bottoma1a;:  border-bottom: 2px solid #D42px solid #AF37; paddingD4AF37; padding-bottom:-bottom: 10px; 10px; }}
            }}
            h2 {{ color h2 {{ color: #1a: #1a1a1a1a; margin1a; margin-top: 30-top: 30px; }}
            .stats {{ displaypx; }}
            .stats {{ display: flex: flex; gap: ; gap: 20px20px;; margin-bottom: 30 margin-bottom: 30px; }}
           px; }}
            .stat .stat-card {{-card {{ background: #f background: #f8f8f9fa; border9fa; border: : 1px1px solid #ddd; solid #ddd; border-radius:  border-radius: 8px; padding8px; padding: 15px: 15px; flex; flex: : 1; }}
           1; }}
            table {{ table {{ border-collapse: collapse; width: border-collapse: collapse; width:  100%; margin100%; margin-bottom:-bottom: 20px; 20px; }}
            }}
            th, th, td {{ border: 1 td {{ border: 1px solidpx solid #ddd; padding #ddd; padding: : 8px; text8px; text-align: left; }}
           -align: left; }}
            th {{ background-color th {{ background-color: #: #f2f2f2f2f2f2;; }}
            . }}
            .footer {{ margin-top: footer {{ margin-top: 40px40px; font-size:; font-size: 0.9 0.9em; color:em; color: #666; text #666; text-align: center;-align: center; }}
        </style>
    }}
        </style>
    </head </head>
    <body>
    <body>
       >
        <h1>UPR <h1>UPRM SM Scheduler -cheduler - Reporte Ejec Reporte Ejecutivo</h1utivo</h1>
        <p>
        <p>Gener>Generado el: {time.strado el: {ftime('%time.strftime('%Y-%Y-%m-%m-%d %dH:%M:% %H:%M:%S')S')}</p}</p>
        
       >
        
        <div class="stats">
            <div class="stats <div">
            <div class="stat-card">
                class="stat-card <h">
                <h3>3>Total Secciones</Total Seh3cciones</h3>
               >
                <p style=" <pfont-size style="font-size: 24px: ; font-weight:24px; font-weight: bold;">{total bold;">_secciones{total_secciones}</p>
           }</p>
            </div>
            <div </div>
            <div class="stat-card class="">
               stat-card">
                <h <h3>Secciones3> TBASecciones TBA</h</h3>
               3>
                <p style="font <p style="font-size: 24-size: 24px;px; font-weight: bold font-weight: bold;">{secciones;">{secciones_tba} ({_tbasecciones_tba} ({secciones_tba/total_secciones/total_secciones*100:.1f}*100:.1f}%)</p%)</p>
            </div>
           >
            </div>
            <div class="stat <div class="stat-card-card">
                <h3>Carga">
                <h3 Total (>Carga Total (Créditos)</h3Créditos)</h3>
               >
                <p style=" <p style="font-sizefont-size: : 24px24px; font-weight:; font-weight: bold;">{c bold;">{carga_total:.1f}</parga_total:.1f}</p>
            </>
            </div>
           div>
            <div class="stat <div class="stat-card">
                <h3-card">
                <h3>Profesores>Profesores Activos</h Activos</h33>
                <p style>
                <p style="font-size: 24px;="font-size: 24px; font-weight font-weight: bold: bold;">{profesores_con;">{profesores_con_carga}</p_carga}</p>
           >
            </div>
        </div </div>
        </div>
        
       >
 <h2>List        
        <h2>Listado de Seccionesado de Secciones TBA (Cont TBA (Contratacionesrataciones Pendientes Pendientes)</h2>
        {master_df)</h2>
        {master_df[master[master_df['_df['Persona'] ==Persona 'TBA'][['ID'] == 'TBA', 'Asign'][['ID', 'Asignatura',atura', 'Est 'Estudiantes (Cudiantes (Cupo)', 'upo)', 'Días', 'Días', 'Horario', 'Horario', 'Salón']].Salón']].to_html(index=Falseto_html) if(index=False) if secciones secciones_tba > _tba > 0 else '<p>No0 else '<p>No hay se hay secciones Tcciones TBA.</pBA.</p>'}
>'}
        
        <h2        
        <h2>Horarios>Horarios por Profesor por Profesor</h2</h2>
        {>
        {''.join([f'''.join([f'<h<h3>{p}</3>{p}</h3>{masterh3>{master_df_df[master_df["Person[master_df["Persona"]a"]==p][["==p][["ID", "AsID", "Asignaturaignatura", "Días", "Días", "Horario", "Salón"]].", "Horario", "Salón"]].to_htmlto_html(index=False)}' for p in sorted(master_df['(index=False)}' for p in sorted(master_df['Persona'].unique()) ifPersona'].unique()) if p not p not in ['TBA', ' in ['TBA', 'GRADGRADUADOS']])}
        
       UADOS']])}
        
        <div <div class="footer">
            Report class="footer">
            Reporte genere generado automáticamente porado automáticamente por UPR UPRM Timetable System.
       M Timetable System.
        </div </div>
        <script>
           >
        <script>
            window.on window.onload = function() {{ windowload = function() {{ window.print();.print(); }}
        </script>
    }}
        </script>
    </body </body>
    </>
    </htmlhtml>
   >
    """
    return html

def """
    generar_figura_cientific return html

def generar_figura_cientifica_carga(cargas_finalesa_carga(cargas_finales, scheduler):
    profesores, scheduler):
    profesores = list = list(cargas_finales.keys(cargas_finales.keys())
    profesores())
    profesores.sort(key=lambda p.sort(key=lambda p: cargas_f: cargas_finales[p],inales[p], reverse=True reverse=True)
   )
    carga_asignada = carga_asignada = [cargas [cargas_finales[p_final] for p ines[p] for p in profesores]
    profesores]
    carga_min carga_min = [scheduler = [scheduler.profesores.profesores[p].[p].carga_min forcarga_min for p in p in profesores]
    carga_max profesores]
    carga_max = = [scheduler [scheduler.profesores.profesores[p].[p].cargacarga_max for p in_max for p profesores in profesores]
    
]
    
    x_vals = list(range(len    x_vals = list(range(len(profesores(profesores)))
)))
    
    fig    
    fig = go.Figure = go.Figure()
   ()
    fig.add_trace fig.add_trace(go.Bar(go.Bar(
        x=x(
        x=x_vals,
       _vals,
        y=carga_as y=carga_asignadaignada,
        name='Carga,
        name='Carga Asignada Asignada',
        marker=dict',
        marker=dict(color='(color='lightgraylightgray', line=dict(color='', line=dict(color='black', width=black', width=1))
   1 ))
    fig.add_t))
    ))
    fig.add_trace(go.Scrace(go.Scatteratter(
        x=x_vals(
        x=x_,
        y=cargavals,
        y=carga_min,
        mode='_min,
        modelines+markers='lines+markers',
        name='C',
        name='Carga Mínimaarga Mínima',
        line=dict(color='blue', width=2',
        line=dict(color='blue', width, dash='dot=2, dash='dot'),
       '),
        marker=dict(size marker=dict(size=6=6)
    ))
    fig.add)
    ))
    fig.add_trace(go_trace(go.Scatter.Scatter(
        x=x_vals(
        x=x_vals,
        y=c,
        y=carga_max,
       arga_max,
        mode='lines+markers mode='lines+markers',
        name='Carga Máxima',
        line=',
        name='Carga Máxima',
        line=dict(colordict(color='orange', width=2='orange', width=2, dash, dash='dot='dot'),
        marker='),
        marker=dict(size=6dict(size=6)
    ))
   )
    ))
    fig.update_layout fig.update_layout(
        title(
        title="Análisis de Carga Acad="Análisis de Cémica por Profarga Académica por Profesor",
        xesoraxis=",
        xaxis=dictdict(
            title="Profesores(
            title="Profesores (índice (í)",
           ndice)",
            tickvals tickvals=x_vals=x_vals,
            ticktext,
            ticktext=[f"=[f"P{i+1}" for i inP{i+1}" for i in x_ x_vals]
        ),
        yvals]
        ),
        yaxis=axis=dict(title="Cantidaddict(title="C de Crantidad de Créditoséditos Seman Semanalesales"),
        font=dict(color='"),
        font=dict(color='#1#1a1a1a1a1aa'),
        paper_bgcolor=''),
        paper_bgcolor='white',
        plotwhite',
        plot_bgcolor='white_bgcolor='white',
        legend=dict(orientation',
        legend=dict='h(orientation='h', yanchor='', yanchor='bottom',bottom', y=1.02, y=1.02, xanchor='center xanchor='', x=0center', x=0.5),
       .5),
        height=500 height=500
    )
    fig.update_x
    )
    fig.update_xaxes(axes(showgrid=True,showgrid=True, gridwidth gridwidth=1, gridcolor='=1, gridcolor='LightGrayLightGray')
    fig.update_yaxes(show')
    fig.update_yaxes(showgrid=True, gridwidth=grid=True, grid1,width=1, gridcolor='Light gridcolor='LightGray')
    return figGray')
    return fig

def generar_plantilla

def generar_plantilla():
    output = io():
    output = io.BytesIO()
    with.BytesIO pd.()
    with pd.ExcelWriterExcelWriter(output,(output, engine='xlsxwriter') engine='xlsxwriter') as writer:
        as writer:
        df_c df_cursos =ursos = pd.DataFrame pd.DataFrame({
            'CODIGO': ['({
            'CODIGOMATE': ['MATE3171', '3171', 'MATE3172MATE'],
            'CR3172'],
            'CREDITOS':EDITOS': [3, 3 [3, 3],
            'DEMANDA],
            'DEM':ANDA': [120, [120, 150 150],
            'C],
            'CUPO':UPO [30,': [30, 30],
            'CANDID 30],
            'CANDIDATOS': ['ATOS': ['PEREZ,PEREZ, GON GONZALEZ',ZALEZ', 'RODRIGUEZ 'RODRIGUEZ'],
           '],
            'TIPO_S 'TIPO_SALON': ['1',ALON': [' '1,31', '1,3']  ']   # Ejemplo con # Ejemplo con múltiples tipos múltiples tipos
        })
        df_cursos
        })
        df_cursos.to_ex.to_excel(writer,cel(writer, sheet_name='Cursos', sheet_name='Cursos', index=False)
        
        df index=False)
        
        df_prof_profes = pd.DataFrame({
            'Nes = pd.DataFrame({
            'NOMBRE': ['OMBRE': ['PEREPEREZ', 'GONZALEZZ', 'GONZALEZ'],
           '],
            'CARGA_MIN': 'CARGA_MIN': [9, [9, 6],
            'CAR 6],
            'CARGA_MAX':GA_MAX': [15, 12 [15, 12],
           ],
            'P 'PREF_DIAS': ['LMREF_DIAS': ['LMV',V', 'MJ 'MJ'],
            'PREF_HORAS'],
            'PREF_HORAS': ['AM',': ['AM', 'PM'],
            'PM'],
            'HORA_ 'HORA_ENTRADA':ENTRADA': ['08:00 ['08:00', '13:00', '13:00'],
            'HORA'],
            '_SALHORA_SALIDA':IDA': ['17:00', '20: ['17:00', '00'],
            '20:00'],
            'PREF1': ['MPREF1':ATE3171', ['MATE3171', 'MATE317 'M2'],
            'ATE3172'],
            'PREF2':PREF ['', '2': ['', ''],
            'PREF3': ['','],
            'PREF3': ['', ''],
            ' ''],
            'COMPENSCOMPENSACION':ACION': ['NO', ' ['NO', 'SISI'],
            'ACEPTA_'],
            'ACEPTA_GRANDGRANDES': [0, ES': [0, 11],
            'CURS],
            'CURSOS_INTENSIVOS_INTOS':ENSIVOS': [0,  [0, 1]
        })
        df1]
        })
        df_prof_profes.toes.to_excel_excel(writer(writer, sheet_name='Profes, sheet_name='Profesores', indexores', index=False=False)
        
        df)
        
        df_salones = pd.DataFrame({
           _salones = pd.DataFrame({
            'COD 'CODIGO': ['IGO': ['S-101',S-101', 'S 'S-102', '-102', 'FA'],
            'CAPACIDAD': [30FA'],
            'CAPACIDAD': [30, 40,, 40, 150],
            150],
            'TIPO': 'TIPO': [1,  [1, 2, 32, 3]
        })
       ]
        })
        df_s df_salonesalones.to_ex.to_excel(wcel(writer, sheet_nameriter, sheet_name='Salones', index=False)
        
        df='Salones', index=False)
        
        df_grad = pd_grad = pd.DataFrame({
            '.DataFrame({
            'NOMBRE':NOMBRE': ['gradu ['graduado1ado1', 'graduado', 'graduado2'],
            '2'],
            'RECIBE':RECIBE': ['MATE3171', 'M ['MATE3171', 'MATE317ATE3172']
       2']
        })
        df_grad.to_excel(writer, })
        df_grad.to_excel(writer, sheet_name sheet_name='Graduados='Graduados', index', index=False)
    
    output.seek(=False)
    
    output.seek(0)
    return output.get0)
    return output.getvaluevalue()

# ==============================================================================
#()

# ==============================================================================
# 8. UI PRINCIPAL 8. UI PRINCIPAL
# =
# ==============================================================================
def main():
    with=============================================================================
def main():
    with st.sidebar:
        st.mark st.sidebar:
        st.markdown("### ∑ Configuradown("### ∑ Configuración")
        zona = st.selectbox("Zción")
        zona = st.selectbox("Zona Campus", ["CENTRAL", "ona Campus", ["CENTRAL", "PERIFERICA"])
       PERIFERICA"])
        iteraciones iteraciones = st.slider(" = st.slider("Iteraciones FIteraciones Fase 1 (Factibilidad)",ase 1 (Factibilidad)", 500 500, 5000, 3000, 5000, 3000)
       )
        file = file = st.file_upload st.file_uploader("Subir Protocoloer("Subir Protocolo Excel", Excel", type=['xlsx type=['xlsx'])
       '])
        st.d st.download_button(
            label="ownload_button(
            label="📥 Descarg📥ar Plantilla Descargar Plantilla",
            data",
            data=gener=generar_ar_plantillaplantilla(),
            file_name="PLANTILLA.x(),
            file_name="PLANTILLA.xlsxlsx",
            mime="application/v",
            mime="application/vnd.opennd.openxmlformats-oxmlformats-officedocument.spreadsheetml.sfficedocument.spreadsheetheetml.sheet"
       "
        )

    st.markdown )

    st.markdown(f"### Ω(f"### Ω Condiciones Condiciones de Z de Zona:ona: {z {zona}")
    cona}")
    c1,1, c2 c2, c3 =, c3 = st.columns(3 st.columns(3)
    with c)
    with c1: st.m1: st.metric("Ventetric("Ventana Operativa",ana Operativa", "07 "07:30:30 AM - AM - 06:30 06:30 PM" PM" if zona == " if zonaCENTRAL == "CENTRAL" else" else "07:00 "07 AM - 06:00 AM - 06:00 PM:00 PM")
    with")
    with c2 c2: st.metric: st.metric("Hora Universal("Hora Universal", "10:", "10:30 AM - 30 AM - 12:30 PM12:30 PM" if zona == "" if zona == "CENTCENTRAL" else "RAL" else "10:00 AM10:00 AM - 12: - 12:00 PM")
    with c00 PM")
    with c3: st.markdown(f3: st.markdown(f"""<div class"""<div class="status-badge="status-badge">RESTRIC">RESTRICCIONES FUCIONES FUERTES ACTIVAS</divERTES ACTIVAS</div>""", unsafe>""", unsafe_allow_allow_html=True_html=True)

    if not)

    if not file file:
:
        st.markdown("""
            <div class='glass        st.markdown("""
            <div class='glass-card' style='text-card' style='text-align: center;-align: center;'>
                <h'>
                <h3 style='margin3 style='margin-top:0; color: #D-top:0; color: #D4AF37;4AF37;'>📥 S'>📥 Sincronización de Datosincronización de Datos</h3</h3>
                <p>A>
                <p>Asegúrese desegúrese de que el que el archivo archivo Excel contiene Excel contiene las h las hojas: <bojas: <b>Cursos>Cursos</b>,</b>, <b>Profesores</ <b>Profesores</b>, <b>Salb>, <b>Salones</ones</b>.</pb>.</p>
            </div>
       >
            </div>
        """, """, unsafe_ unsafe_allow_html=Trueallow_html=True)
    else)
    else:
        if st:
        if st.button(".button("🚀 INICI🚀 INICIAR OPTIMIZACIÓN ABSAR OPTIMIZACIÓN ABSOLUTA"):
            try:
               OLUTA"):
            try:
                with st with st.spinner("Balanceando car.spinner("Balanceando cargas, consolidando seccionesgas, consolidando secciones y resolviendo..." y resolviendo..."):
                    x):
                    xls = pd.ExcelFilels = pd.(file)
                    df_cursosExcelFile(file)
                    df_cursos = pd.read_ex = pd.read_excel(xcel(xls, 'Cursosls, 'Cursos')
                    #')
                    # Normalizar TIPO_SALON: Normalizar TIPO_SAL convertir a string yON: convertir a string y reemplazar punto reemplazar punto por coma
                    por coma
                    df_cursos[' df_cTIPO_SALON']ursos[' = dfTIPO_SALON'] = df_cursos['T_cursos['TIPO_SALONIPO_SALON'].astype(str'].ast).str.replace('.', ',ype(str).str.replace('.', ',', regex', regex=False)
                    
                   =False)
                    
                    df_profes df_profes = pd.read_ex = pd.read_excel(xls,cel(xls, 'Profesores')
                    'Profesores')
                    df_s df_salones = pdalones = pd.read_excel(x.read_excel(xls,ls, 'Sal 'Salonesones')
                    
                    # Leer hoja Gradu')
                    
                    # Leer hoja Graduados si existeados si existe
                    df_grad
                    df_grad = None
                    = None
                    if 'Graduados' if 'Graduados' in xls.s in xls.sheet_names:
                        df_gheet_names:
                        df_grad = pd.read_excelrad = pd.read_excel(xls, '(xls, 'GraduGraduados')

                    scheduler = Tabados')

                    scheduler = TabuSuScheduler(df_cursos, dfcheduler(df_cursos, df_profes, df_s_profes, df_salones, zonaalones, zona, df_grad, df_grad)
                    
                    start)
                    
                    start_time =_time = time.time()
                    bar = st.pro time.time()
                    bar = st.progress(0)
                   gress(0)
                    status status = st.empty()
                    mejor = st.empty()
                    mejor_sol, conflict_sol, conflictos, historial = scheduleros, historial = scheduler.optimizar(.optimizar(iteraciones, bar, statusiteraciones, bar, status)
)
                    
                    st.session_state.elapsed                    
                    st.session_state.elapsed_time = time.time_time = time.time() - start_time
                    st.session() - start_time
                    st.session_state.conflicts =_state.conflicts = conflictos
                    st.session conflictos
                    st.session_state.historial_state.h = historialistorial = historial
                    st.session_state
                    st.session_state.scheduler = scheduler.scheduler = scheduler
                    st.session
                    st.session_state.me_state.mejor_sol = mejor_sjor_sol = mejor_sol
                    
                   ol
                    
                    cargas cargas_finales =_finales = {}
                    for asign {}
                    for asign in mejor_sol in mejor_sol:
                        p =:
                        p = asign[' asign['profesor']
                        if pprofesor']
                        != " if p != "GRADUADGRADUADOS" and p != "OS" and p != "TBA":
                           TBA":
                            cargas_finales[p] = cargas_finales[p] = cargas_final cargas_finales.get(p, 0es.get(p, 0) + scheduler.get) + scheduler.get_sec_cred_sec_creditos(asitos(asign['seccion'], p)
                    for pign['seccion'], p)
                    for p in scheduler.profesores in scheduler.profesores:
                       :
                        if p not in cargas if p not in_finales:
                            cargas_f cargas_finales:
                            cargas_finales[p]inales[p] = 0. = 0.0
                    st.session_state0
                    st.cargas_final.session_state.cargas_finales = cargas_finales = cargas_finaleses

                    st.session_state

                    st.session_state.master = pd.master = pd.DataFrame.DataFrame([{
                        'ID([{
                        'ID': a['seccion'].cod,': a['seccion'].cod, 
                        'As 
                        'Asignatura': aignatura': a['seccion'].cod.split('-['seccion'].cod.split('-')[0')[0],
                        'Estud],
                        'Estudiantes (iantes (Cupo)Cupo)': a['seccion'].': a['seccion'].cupocupo,
                        'Créditos,
                        'Créditos Reales Reales': scheduler.get_': scheduler.get_sec_creditossec_creditos(a['seccion(a['seccion'], a['prof'], a['profesor']),
                       esor']),
                        'Persona': a['profesor 'Persona': a[''], 
                        'profesor'], 
                        'DíasDías': a['pat': a['patron']['ron']['name'], 
                        'Horname'], 
                        'Horario': format_hario': format_horario(a['orario(a['patron'], a['ini']), 
                        'Salpatron'], a['ini']), 
                        'Salón': a['ón': a['salon']
                   salon']
                    } for a in } for a in mejor_s mejor_solol])
                    st.session_state])
                    st.detailed_conf.session_state.detailed_conflicts = scheduler._licts = scheduler._obtener_conflictos(mejor_solobtener_conflictos(mejor_sol)

            except Exception as e:
                st)

            except Exception as e:
                st.error(f"Error durante la optimización.error(f"Error durante la optimización: {e}")
                return: {e}")
                return

    if 'master' in st.session_state

    if 'master' in st.session_state:
        st.success:
        st.success(f"✅ Optimización completada en {st.session_state(f"✅ Optimización completada en {st.session_state.elapsed_time:.2f} segundos.elapsed_time:.2f} segundos.")
        st.markdown("<div.")
        st.markdown("<div class=' class='glass-card'>", unsafe_glass-card'>",allow unsafe_allow_html_html=True)
        t1, t2=True)
        t1, t2, t3,, t3, t4 = st.tabs(["💎 PAN t4 = st.tabs(["💎 PANEL DEEL DE CONTROL", "🔍 V CONTROL", "🔍 VISTAS DETALLADISTAS DETALLADAS",AS", " "🚨 AUDITORÍA DE CAL🚨 AUDITORÍA DE CALIDAD", "IDAD", "📊 ANALÍTICAS AVAN📊 ANALÍTICAS AVANZADAS"])
        
       ZADAS with t"])
        
        with t11:
            edited = st:
            edited.data_editor(st = st.data_editor(st.session_state.master, use.session_state.master, use_container_width_container_width=True,=True, height= height=500)
            st500)
            st.download_button(".download_button("💾 EXPORT💾 EXPORTAR EXCEL PLAR EXCEL PLATINUM",ATINUM", exportar_todo(edited exportar_todo(edited), "Horario), "Horario_Final_Final_UPRM.xlsx",_UPRM.xlsx", use_container use_container_width=True_width=True)
            
        with t2)
            
        with t2:
           :
            f1, f f1, f2, f32, f3, f4 =, f4 = st.tabs(["Por Prof st.tabs(["Por Profesor",esor", "Por "Por Curso", " Curso", "Por Salón", "PorPor Salón", Graduados"])
            df "Por Graduados"])
           _master = st.session df_master = st.session_state.master_state.m
            with f1aster
            with:
                lista_profes f1:
                lista_profes = sorted([p for p = sorted([p for p in df_master['Person in df_mastera'].unique()['Persona'].unique() if p != " if p != "GRADUADGRADUADOS"])
                if lista_proOS"])
                if lista_profes:
                   fes:
                    p = st.selectbox(" p = st.selectbox("SeleccionarSeleccionar Profesor", lista_prof Profesor", lista_proesfes)
                    subset = df_master)
                    subset = df_master[df[df_master['Person_master['Persona'] == p]
                   a'] == p]
                    st.table(subset st.table(subset[['ID',[['ID', 'Est 'Estudiantes (Cudiantesupo)', ' (Cupo)', 'Créditos ReCréditos Reales', 'Días',ales', 'Días', 'Hor 'Horario', 'Salón']])
           ario', 'Salón'] with f])
            with f2:
                lista_cursos2:
                lista = sorted_cursos = sorted(df_master['Asign(df_master['Asignatura'].uniqueatura'].unique())
                if())
                if lista_cursos:
                    c lista_cursos:
                    c = st.selectbox = st.selectbox("Seleccionar Cur("Seleccionso", lista_car Curso", lista_cursos)
                    subset = df_masterursos)
                    subset = df_master[df[df_master['Asignatura'] ==_master['Asignatura'] == c c]
                    st.table(subset]
                    st.table(subset[['ID', '[['ID', 'Estudiantes (Estudiantes (Cupo)',Cup 'Persona',o)', 'Persona', 'Días', 'Días', 'Hor 'Horario', 'Salón']ario', 'Salón']])
            with f3:
                lista])
            with f3:
                lista_salones = sorted(df_master['Sal_salones = sorted(df_master['Salón'].uniqueón'].())
                if lista_sunique())
                if lista_salones:
                    sl =alones st.selectbox(":
                    sl = st.selectbox("Seleccionar SalónSeleccionar", lista Salón", lista_salones_salones)
                    subset)
                    subset = df = df_master[df_master[df_master_master['Sal['Salón'] == sl]
                   ón'] == sl]
                    st.table st.table(subset(subset[['[['ID', 'AsID', 'Asignatura', 'ignatura', 'Persona',Persona', 'Días', 'Horario']])
            with f4 'Días', 'Horario']])
            with f4:
               :
                lista_grads = sorted lista_grads = sorted([p for p([p for p in df_master['Person in df_master['Persona'].a'].unique()unique() if p if p.upper().startswith('.upper().startswith('GRADUADOGRADUADO')])
                if')])
                if lista_g lista_gradsrads:
                    g =:
                    g = st.selectbox("Sele st.selectbox("Seleccionar Graduadoccionar Graduado", lista_grad", lista_grads)
                    subsets = df_master)
                    subset = df_master[df[df_master['Persona']_master['Persona'] == g]
                    == g st.table(subset[['ID',]
                    st.table(subset[['ID', 'As 'Asignatura', 'ignatura', 'Estudiantes (Estudiantes (CupCupo)',o)', 'Créditos Reales 'Créditos Reales', '', 'Días', 'HorarioDías', '', 'Horario', 'Salón']])
                elseSalón']:
                    st.info])
                else:
                    st.info("No hay graduados con("No hay gradu asignación de docados con asignación de docencia enencia en este horario este horario.")
                
       .")
                
        with t with t3:
            conflictos = st.session3:
            conflictos =_state.conf st.session_state.conflicts
            iflicts
            if conflictos > 0 conflictos > 0:
                st.error(f"⚠:
                st.error(f"⚠️ Aún pers️ Aún persisten {conflictos}isten {conflictos} conflictos duros.")
                conflictos duros for conf in st.session_state.")
                for conf in st.session_state.detailed_conf.detlicts:
                    stailed_conflicts.write(f:
                    st.write(f"- {conf}")
            else"- {conf:
                st.success("✅ 100}")
            else:
                st.success("✅ 100% Asignación% Asignación Perfecta. Cero Conflict Perfecta. Cero Conflictos Durosos Duros.")
                
        with t4.")
                
        with t4:
            st:
            st.markdown.markdown("### 📈 Analíticas Av("### 📈 Analíticas Avanzadas")
anzadas            
            subt")
            
            subtab1, subtab2ab1, subtab2, subtab3, subt, subtab3, subtab4 = st.tabsab4 = st.tabs(["📊 Visualizaciones", "🗓(["📊 Visualizaciones", "🗓️ Calendario", "️ Calendario", "📄📄 Reporte Reporte PDF", " PDF", "📈 C📈 Carga Carga Científicaientífica"])
            
            with subtab1:
               "])
            
            with subtab1:
                st.markdown(" st.markdown("#### Mapa de#### Mapa de Calor de Ocupación Calor de Ocupación")
                fig_")
                fig_heat = generar_heatmapheat = generar_heatmap_plotly(st_plotly(st.session_state.session_state.scheduler, st.scheduler, st.session_state.mejor.session_state.mejor_sol)
                st.plot_sol)
                st.plotly_chart(fly_chart(fig_ig_heat, use_containerheat,_width=True use_container_width=True)
                
                st.markdown)
                
                st.markdown("#### Distribución de Cl("#### Distribución de Clases por Profesorases por Profesor y Día")
                fig y Día")
                fig_barras =_barras = generar_barras generar_barras_apiladas_prof_apiladas_profesor(stesor(st.session_state.mejor.session_state.mejor_sol, st_sol, st.session_state.scheduler)
               .session_state.scheduler)
                st.plotly_ch st.plotly_chart(fig_bart(fig_barras, usearras, use_container_width=True_container_width=True)
                
                st.markdown("#### Evolución del Fitness)
                
                st.markdown("#### Evolución del Fitness")
                fig_fitness")
                fig_fitness = generar_evolucion = generar_evolucion_fitness_plot_fitness_plotly(st.session_stately(st.session_state.historial.historial)
                st)
                st.plotly.plotly_chart(fig_chart(fig_fitness_fitness, use, use_container_width=True_container_width=True)
            
            with subt)
            
            with subtab2:
                st.markab2:
                st.markdown("#### Caldown("#### Calendarioendario Visual Inter Visual Interactivo")
               activo")
                col1 col1, col, col2, col3 = st2, col3 = st.columns(3.columns(3)
                with)
                with col1:
                    filtro col1:
                    filtro_prof = st.selectbox("F_prof = st.selectboxiltrar por Profesor",("Filtrar por Prof ['Todosesor", ['Todos'] + sorted(st'] + sorted(st.session_state.master['Person.session_state.master['Persona'].uniquea'].unique()))
                with col2()))
                with col2:
                   :
                    filtro_salon filtro_salon = st.selectbox("Filtrar por Sal = st.selectbox("Filtrar por Salón",ón", ['Todos'] + sorted(st ['Todos'] + sorted(st.session_state.session_state.master['Salón']..master['Salón'].unique()))
                with col3:
                   unique()))
                with col3:
                    filtro filtro_curso = st.selectbox("F_curso = st.selectbox("Filtrariltrar por Cur por Curso", ['Todos'] + sorted(st.session_state.masterso", ['Todos'] + sorted(st.session_state.master['As['Asignatura'].unique()))
                
                fig_cal = generar_calendario_visual(
                    st.sessionignatura'].unique()))
                
                fig_cal = generar_calendario_visual(
                    st.session_state.me_state.mejor_sol,
                    st.session_statejor_sol,
                    st.session_state.scheduler,
                    filtro_prof.scheduler,
                    filtro_prof if filtro_prof != if filtro_prof != 'Todos 'Todos' else None,
                    filt' else None,
                    filtro_salon if filtroro_salon if filtro_salon_salon != 'Todos' else None != 'Todos' else None,
                   ,
                    filtro_curso if filt filtro_curso if filtro_curso != 'Todos' else None
                )
                st.plotly_chart(fig_cal, use_container_width=Truero_curso != 'Todos' else None
                )
                st.plotly_chart(fig_cal, use_container_width=True)
            
           )
            
            with subtab3 with subtab3:
                st.mark:
                st.markdown("#### Exportar Reporte Ejdown("#### Exportar Reportecutivo en PDFe Ejecutivo en PDF")
                if st")
                if st.button("📑.button("📑 Generar Generar Reporte PDF ( Reporte PDF (Imprimir)"Imprimir)"):
                   ):
                    html_reporte = html_reporte = generar_re generar_reporte_pdf_htmlporte_pdf_html(
                       (
                        st.session st.session_state.scheduler,
                        st.session_state_state.scheduler,
                        st.session_state.mejor_sol,
                       .mejor_sol,
                        st.session_state.c st.session_state.cargas_finalesargas_finales,
                       ,
                        st.session st.session_state.master_state.master
                    )
                    st
                    )
                    st.components.v1.components.v1.html(html_re.html(html_reporte,porte, height=600, height= scrolling=True)
                st.info600, scrolling=True)
               ("H st.info("Haz claz clic en el botón paraic en el botón para generar el reporte generar el reporte y luego y luego usa la opción 'Im usa la opción 'Imprimir' deprimir' de tu tu navegador para guard navegadorar como PDF para guardar como PDF.")
            
            with subtab4.")
            
            with subtab4:
               :
                st.markdown(" st.markdown("#### Análisis#### An Cientálisis Científicoífico de Carga Acad de Cémica")
               arga Académica")
                fig_c fig_carga = generar_figura_cientificarga = generar_figura_cientifica_carga(sta_carga(st.session_state.cargas_final.session_state.cargas_finales,es, st.session_state.scheduler st.session_state.scheduler)
                st.plotly_chart)
                st.plotly_chart(fig_carga(fig_carga, use_container_width, use_container_width=True)
            
        st.markdown("=True</div>",)
            
        st.markdown("</div>", unsafe_allow_html=True unsafe_allow_html=True)

if __name__)

if __name__ == "__main__":
    main == "__main__":
    main()
()
