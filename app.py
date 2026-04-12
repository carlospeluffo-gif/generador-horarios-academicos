import streamlit as st
import pandas as pd
import numpy as np
import random
import io
import time
import math
from copy import deepcopy
from collections import defaultdict
import plotly.express as px
import plotly.graph_objects as go

# ==============================================================================
# 1. ESTÉTICA (IDENTIDAD UPRM - SIN CAMBIOS)
# ==============================================================================
st.set_page_config(page_title="UPRM Scheduler Platinum v17", page_icon="🏛️", layout="wide")

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
        <p><span class="subtitle-accent">COLEGIO DE ARTES Y CIENCIAS</span> · OPTIMIZACIÓN ACADÉMICA v17</p>
    </div>
    <div class="header-logo">
        <img src="https://www.uprm.edu/portada/wp-content/uploads/sites/24/2023/08/logo-rum-200x200-1-150x150.png" alt="UPRM Seal">
    </div>
    <div style="width:150px;"></div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. UTILIDADES Y TABLAS (SIN CAMBIOS)
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
    3: [
        {"name": "Lu-Mi-Vi", "days": {"Lu": 1, "Mi": 1, "Vi": 1}},
        {"name": "Ma-Ju", "days": {"Ma": 1.5, "Ju": 1.5}},
        {"name": "Ma (Intensivo)", "days": {"Ma": 3}},
        {"name": "Ju (Intensivo)", "days": {"Ju": 3}},
    ],
    4: [
        {"name": "Lu-Ma-Mi-Ju", "days": {"Lu": 1, "Ma": 1, "Mi": 1, "Ju": 1}},
        {"name": "Lu-Ma-Mi-Vi", "days": {"Lu": 1, "Ma": 1, "Mi": 1, "Vi": 1}},
        {"name": "Lu-Ma-Ju-Vi", "days": {"Lu": 1, "Ma": 1, "Ju": 1, "Vi": 1}},
        {"name": "Lu-Mi-Ju-Vi", "days": {"Lu": 1, "Mi": 1, "Ju": 1, "Vi": 1}},
        {"name": "Ma-Mi-Ju-Vi", "days": {"Ma": 1, "Mi": 1, "Ju": 1, "Vi": 1}},
        {"name": "Lu-Mi", "days": {"Lu": 2, "Mi": 2}},
        {"name": "Lu-Vi", "days": {"Lu": 2, "Vi": 2}},
        {"name": "Ma-Ju", "days": {"Ma": 2, "Ju": 2}},
        {"name": "Mi-Vi", "days": {"Mi": 2, "Vi": 2}},
    ],
    5: [
        {"name": "Lu-Ma-Mi-Ju-Vi", "days": {"Lu": 1, "Ma": 1, "Mi": 1, "Ju": 1, "Vi": 1}},
        {"name": "Lu-Ma-Mi-Vi", "days": {"Lu": 1, "Ma": 1, "Mi": 1, "Vi": 2}},
        {"name": "Lu-Ma-Ju-Vi", "days": {"Lu": 1, "Ma": 1, "Ju": 1, "Vi": 2}},
        {"name": "Lu-Mi-Ju-Vi", "days": {"Lu": 1, "Mi": 1, "Ju": 1, "Vi": 2}},
        {"name": "Ma-Mi-Ju-Vi", "days": {"Ma": 1, "Mi": 1, "Ju": 1, "Vi": 2}},
        {"name": "Lu-Mi-Vi", "days": {"Lu": 2, "Mi": 2, "Vi": 1}},
        {"name": "Ma-Ju-Vi", "days": {"Ma": 1.5, "Ju": 1.5, "Vi": 2}},
        {"name": "Lu-Ma-Mi", "days": {"Lu": 2, "Ma": 1, "Mi": 2}},
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
# 3. MODELO DE DATOS (MEJORADO)
# ==============================================================================
class Seccion:
    def __init__(self, cod, creditos, cupo, candidatos_raw, tipo_salon):
        self.cod = str(cod)
        self.creditos = int(creditos)
        self.cupo = int(cupo)
        if isinstance(candidatos_raw, list):
            raw_list = [c.strip().upper() for c in candidatos_raw if c.strip()]
        else:
            raw_list = [c.strip().upper() for c in str(candidatos_raw).split(',') if c.strip() and str(c).upper() != 'NAN']
        self.cands = list(set(raw_list))
        try:
            t = float(tipo_salon)
            if abs(t - 1.3) < 0.01:
                self.tipo_salon = 3
            else:
                self.tipo_salon = int(round(t))
        except:
            self.tipo_salon = 1
        base = self.cod.split('-')[0].upper().replace(" ", "")
        self.es_fusionable = base in ["MATE3171", "MATE3172", "MATE3173"]
        self.es_grande = self.cupo >= 85

class Profesor:
    def __init__(self, nombre, carga_min, carga_max, pref_dias, pref_horas,
                 bloqueo_dias, bloqueo_ini, bloqueo_fin,
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
        self.preferencias = []
        if isinstance(preferencias_cursos, list):
            self.preferencias = [c.upper().strip() for c in preferencias_cursos if c and str(c).upper() != 'NAN']
        self.compensacion = str(compensacion).upper().strip() in ('SI', 'SÍ', 'YES', '1')
        self.acepta_grandes = int(acepta_grandes) if pd.notnull(acepta_grandes) and acepta_grandes != '' else 0
        try:
            self.cursos_intensivos = int(cursos_intensivos)
        except:
            self.cursos_intensivos = 0
        self.bloqueos = []
        if bloqueo_dias and isinstance(bloqueo_dias, str) and bloqueo_dias.strip():
            dias_map = {'L': 'Lu', 'M': 'Ma', 'MI': 'Mi', 'J': 'Ju', 'V': 'Vi'}
            dias_limpios = bloqueo_dias.upper().replace(' ', '')
            if ',' in dias_limpios:
                dias_limpios = dias_limpios.replace(',', '')
            dias_set = set()
            i = 0
            while i < len(dias_limpios):
                if dias_limpios[i:i+2] == 'MI':
                    dias_set.add('Mi')
                    i += 2
                else:
                    letra = dias_limpios[i]
                    if letra in dias_map:
                        dias_set.add(dias_map[letra])
                    i += 1
            if dias_set:
                try:
                    start_min = str_to_mins(bloqueo_ini) if bloqueo_ini and pd.notnull(bloqueo_ini) else None
                    end_min = str_to_mins(bloqueo_fin) if bloqueo_fin and pd.notnull(bloqueo_fin) else None
                    if start_min is not None and end_min is not None:
                        self.bloqueos.append((dias_set, start_min, end_min))
                except:
                    pass

def compatible_tipo(curso_tipo, salon_tipo):
    if isinstance(salon_tipo, float):
        if salon_tipo >= 1.9 and salon_tipo <= 2.1:
            salon_cat = 2
        elif salon_tipo >= 2.9:
            salon_cat = 3
        else:
            salon_cat = 1
    else:
        salon_cat = int(salon_tipo)
    if curso_tipo == 2:
        return salon_cat == 2
    if curso_tipo == 3:
        return salon_cat == 3
    return salon_cat != 2

# ==============================================================================
# 4. NUEVO MOTOR HÍBRIDO GARANTIZADO (SIN OR-TOOLS)
# ==============================================================================
class UltraScheduler:
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
                    bloqueo_dias=r.get('BLOQUEO_DIAS', ''),
                    bloqueo_ini=r.get('BLOQUEO_HORA_INI', ''),
                    bloqueo_fin=r.get('BLOQUEO_HORA_FIN', ''),
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
                t = r.get('TIPO_SALON', 1)
                try:
                    t_val = float(t)
                    if abs(t_val - 1.3) < 0.01:
                        tipo_salon = 3
                    else:
                        tipo_salon = int(round(t_val))
                except:
                    tipo_salon = 1
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

        # Graduados doble rol
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

        # Precomputar opciones válidas por sección
        self.opciones_por_seccion = []
        for s in self.secciones:
            ops = self._generar_opciones(s)
            self.opciones_por_seccion.append(ops)

        # Estadísticas
        self.total_secciones = len(self.secciones)

    def get_sec_creditos(self, s, prof_name):
        if prof_name in self.profesores and self.profesores[prof_name].compensacion:
            return get_creditos_reales(s.creditos, s.cupo)
        return float(s.creditos)

    def _generar_opciones(self, s):
        opciones = []
        profs = s.cands if s.cands else (["GRADUADOS"] if "GRADUADOS" in s.cands else ["TBA"])
        for prof in profs:
            if prof not in self.profesores and prof not in ["GRADUADOS", "TBA"]:
                continue
            patrones = PATRONES.get(s.creditos, PATRONES[3])
            if prof in self.profesores:
                prof_obj = self.profesores[prof]
                if prof_obj.cursos_intensivos == 0:
                    patrones = [p for p in patrones if not any(c >= 3 for c in p['days'].values())]
                elif prof_obj.cursos_intensivos == 1:
                    intensivos = [p for p in patrones if any(c >= 3 for c in p['days'].values())]
                    if intensivos:
                        patrones = intensivos + [p for p in patrones if not any(c >= 3 for c in p['days'].values())]
                if prof_obj.acepta_grandes == 0 and s.es_grande:
                    continue
            if not patrones:
                continue
            for patron in patrones:
                horas_validas = set(self.bloques)
                for dia, contrib in patron['days'].items():
                    duracion = contrib * 50
                    horas_dia = [h for h in self.bloques if h >= self.limite_operativo[0] and h + duracion <= self.limite_operativo[1]]
                    if dia in ["Ma", "Ju"]:
                        horas_dia = [h for h in horas_dia if not (max(h, self.hora_universal[0]) < min(h+duracion, self.hora_universal[1]))]
                    if s.creditos == 3 and contrib >= 3:
                        horas_dia = [h for h in horas_dia if h >= 930]
                    horas_validas = horas_validas.intersection(set(horas_dia))
                    if not horas_validas:
                        break
                if not horas_validas:
                    continue
                for ini in horas_validas:
                    for sl in self.salones:
                        if sl['CAPACIDAD'] < s.cupo:
                            continue
                        if not compatible_tipo(s.tipo_salon, sl['TIPO']):
                            continue
                        if prof in self.profesores:
                            prof_obj = self.profesores[prof]
                            bloqueado = False
                            for (dias_set, start, end) in prof_obj.bloqueos:
                                for dia in patron['days'].keys():
                                    if dia in dias_set:
                                        fin = ini + int(patron['days'][dia] * 50)
                                        if max(ini, start) < min(fin, end):
                                            bloqueado = True
                                            break
                                if bloqueado:
                                    break
                            if bloqueado:
                                continue
                        opciones.append((prof, patron, ini, sl['CODIGO']))
        if not opciones:
            # Opción de emergencia
            opciones.append(("TBA", PATRONES.get(s.creditos, PATRONES[3])[0], self.bloques[0], "TBA"))
        return opciones

    # --------------------------------------------------------------
    # Función de costo (Hard = 1e6, Soft = valores menores)
    # --------------------------------------------------------------
    def _evaluar_solucion(self, sol, solo_hard=False):
        hard = 0
        soft = 0
        occ_prof = defaultdict(list)
        occ_salon = defaultdict(list)
        carga = defaultdict(float)
        grad_dicta = defaultdict(list)
        grad_recibe = defaultdict(list)

        for idx, asign in enumerate(sol):
            s = asign['seccion']
            prof = asign['profesor']
            salon = asign['salon']
            patron = asign['patron']
            ini = asign['ini']

            if prof == "TBA": hard += 1e6
            if salon == "TBA": hard += 1e6

            salon_info = next((sl for sl in self.salones if sl['CODIGO'] == salon), None)
            if salon_info and salon_info['CAPACIDAD'] < s.cupo:
                hard += 1e6
            if salon_info and not compatible_tipo(s.tipo_salon, salon_info['TIPO']):
                hard += 1e6

            if prof in self.profesores:
                prof_obj = self.profesores[prof]
                if prof_obj.acepta_grandes == 0 and s.es_grande:
                    hard += 1e6

            creditos = self.get_sec_creditos(s, prof)
            carga[prof] += creditos

            for dia, contrib in patron['days'].items():
                fin = ini + int(contrib * 50)
                if dia in ["Ma", "Ju"] and max(ini, self.hora_universal[0]) < min(fin, self.hora_universal[1]):
                    hard += 1e6
                if s.creditos == 3 and contrib >= 3 and ini < 930:
                    hard += 1e6
                if fin > self.limite_operativo[1] or ini < self.limite_operativo[0]:
                    hard += 1e6

                # Solapamiento profesor
                for (ini_ex, fin_ex, idx_ex) in occ_prof[(prof, dia)]:
                    if max(ini, ini_ex) < min(fin, fin_ex):
                        hard += 1e6
                occ_prof[(prof, dia)].append((ini, fin, idx))

                # Solapamiento salón
                for (ini_ex, fin_ex, cupo_ex, fus_ex, idx_ex) in occ_salon[(salon, dia)]:
                    if max(ini, ini_ex) < min(fin, fin_ex):
                        if salon in self.mega_salones and s.es_fusionable and fus_ex and (s.cupo + cupo_ex <= self.salon_capacidad.get(salon, 0)):
                            continue
                        hard += 1e6
                occ_salon[(salon, dia)].append((ini, fin, s.cupo, s.es_fusionable, idx))

            if prof in self.graduados_reciben:
                grad_dicta[prof].append((s, patron, ini))
            cod_base = s.cod.split('-')[0].upper()
            for grad, codigos in self.graduados_reciben.items():
                if cod_base in codigos:
                    grad_recibe[grad].append((s, patron, ini))

        # Carga
        for prof, c in carga.items():
            if prof in self.profesores:
                if c > self.profesores[prof].carga_max + 1.5:
                    hard += 1e6
                if c < self.profesores[prof].carga_min - 1.5:
                    hard += 1e6

        # Doble rol
        for grad in set(grad_dicta.keys()) | set(grad_recibe.keys()):
            for s_d, pat_d, ini_d in grad_dicta[grad]:
                for s_r, pat_r, ini_r in grad_recibe[grad]:
                    for dia, contrib_d in pat_d['days'].items():
                        if dia in pat_r['days']:
                            fin_d = ini_d + int(contrib_d * 50)
                            fin_r = ini_r + int(pat_r['days'][dia] * 50)
                            if max(ini_d, ini_r) < min(fin_d, fin_r):
                                hard += 1e6

        if solo_hard:
            return hard

        # Soft constraints
        for idx, asign in enumerate(sol):
            prof = asign['profesor']
            if prof in self.profesores:
                prof_obj = self.profesores[prof]
                patron = asign['patron']
                ini = asign['ini']
                if prof_obj.pref_horas == 'AM' and ini >= 720:
                    soft += 30
                elif prof_obj.pref_horas == 'PM' and ini < 720:
                    soft += 30
                if prof_obj.pref_dias_set:
                    for dia in patron['days'].keys():
                        if dia not in prof_obj.pref_dias_set:
                            soft += 15
                # Preferencia de curso
                prioridad = prof_obj.prioridad_curso(asign['seccion'].cod)
                if prioridad > 0:
                    soft -= prioridad * 20

        return hard + soft

    # --------------------------------------------------------------
    # Generación de solución inicial (greedy con backtracking limitado)
    # --------------------------------------------------------------
    def _solucion_inicial(self):
        # Ordenar por dificultad
        secciones_ordenadas = sorted(self.secciones, key=lambda s: (
            len(self._generar_opciones(s)),
            -len(s.cands),
            s.creditos
        ))
        sol = [None] * len(self.secciones)
        idx_map = {id(s): i for i, s in enumerate(self.secciones)}

        def backtrack(pos, ocupacion_prof, ocupacion_salon, carga_actual):
            if pos == len(secciones_ordenadas):
                return True
            s = secciones_ordenadas[pos]
            idx = idx_map[id(s)]
            ops = self.opciones_por_seccion[idx]
            # Ordenar por preferencia
            def score_op(op):
                prof, patron, ini, salon = op
                sc = 0
                if prof in self.profesores:
                    prof_obj = self.profesores[prof]
                    sc += prof_obj.prioridad_curso(s.cod) * 100
                return -sc
            ops_sorted = sorted(ops, key=score_op)
            for prof, patron, ini, salon in ops_sorted:
                # Verificar factibilidad rápida
                factible = True
                creditos = self.get_sec_creditos(s, prof)
                nueva_carga = carga_actual.get(prof, 0) + creditos
                if prof in self.profesores:
                    if nueva_carga > self.profesores[prof].carga_max + 1.5:
                        factible = False
                if factible:
                    for dia, contrib in patron['days'].items():
                        fin = ini + int(contrib * 50)
                        # Profesor
                        for (ini_ex, fin_ex) in ocupacion_prof.get((prof, dia), []):
                            if max(ini, ini_ex) < min(fin, fin_ex):
                                factible = False
                                break
                        if not factible: break
                        # Salón
                        for (ini_ex, fin_ex, cupo_ex, fus_ex) in ocupacion_salon.get((salon, dia), []):
                            if max(ini, ini_ex) < min(fin, fin_ex):
                                if salon in self.mega_salones and s.es_fusionable and fus_ex:
                                    if s.cupo + cupo_ex <= self.salon_capacidad.get(salon, 0):
                                        continue
                                factible = False
                                break
                        if not factible: break
                if factible:
                    # Asignar
                    sol[idx] = {'seccion': s, 'profesor': prof, 'salon': salon, 'patron': patron, 'ini': ini}
                    # Actualizar estructuras
                    carga_actual[prof] = nueva_carga
                    for dia, contrib in patron['days'].items():
                        fin = ini + int(contrib * 50)
                        ocupacion_prof.setdefault((prof, dia), []).append((ini, fin))
                        ocupacion_salon.setdefault((salon, dia), []).append((ini, fin, s.cupo, s.es_fusionable))
                    if backtrack(pos+1, ocupacion_prof, ocupacion_salon, carga_actual):
                        return True
                    # Deshacer
                    carga_actual[prof] -= creditos
                    for dia, contrib in patron['days'].items():
                        ocupacion_prof[(prof, dia)].pop()
                        ocupacion_salon[(salon, dia)].pop()
            return False

        # Intentar backtracking
        if backtrack(0, defaultdict(list), defaultdict(list), defaultdict(float)):
            return sol
        else:
            # Fallback: greedy aleatorio
            st.warning("Backtracking falló, usando greedy aleatorio...")
            return self._greedy_aleatorio()

    def _greedy_aleatorio(self):
        sol = [None] * len(self.secciones)
        ocupacion_prof = defaultdict(list)
        ocupacion_salon = defaultdict(list)
        carga = defaultdict(float)
        indices = list(range(len(self.secciones)))
        random.shuffle(indices)
        for idx in indices:
            s = self.secciones[idx]
            ops = self.opciones_por_seccion[idx]
            random.shuffle(ops)
            asignado = False
            for prof, patron, ini, salon in ops:
                creditos = self.get_sec_creditos(s, prof)
                if prof in self.profesores and carga[prof] + creditos > self.profesores[prof].carga_max + 1.5:
                    continue
                factible = True
                for dia, contrib in patron['days'].items():
                    fin = ini + int(contrib * 50)
                    for (ini_ex, fin_ex) in ocupacion_prof.get((prof, dia), []):
                        if max(ini, ini_ex) < min(fin, fin_ex):
                            factible = False; break
                    if not factible: break
                    for (ini_ex, fin_ex, cupo_ex, fus_ex) in ocupacion_salon.get((salon, dia), []):
                        if max(ini, ini_ex) < min(fin, fin_ex):
                            if salon in self.mega_salones and s.es_fusionable and fus_ex:
                                if s.cupo + cupo_ex <= self.salon_capacidad.get(salon, 0):
                                    continue
                            factible = False; break
                    if not factible: break
                if factible:
                    sol[idx] = {'seccion': s, 'profesor': prof, 'salon': salon, 'patron': patron, 'ini': ini}
                    carga[prof] += creditos
                    for dia, contrib in patron['days'].items():
                        fin = ini + int(contrib * 50)
                        ocupacion_prof[(prof, dia)].append((ini, fin))
                        ocupacion_salon[(salon, dia)].append((ini, fin, s.cupo, s.es_fusionable))
                    asignado = True
                    break
            if not asignado:
                # Usar opción TBA
                prof, patron, ini, salon = ops[0]
                sol[idx] = {'seccion': s, 'profesor': "TBA", 'salon': "TBA", 'patron': patron, 'ini': ini}
        return sol

    # --------------------------------------------------------------
    # Búsqueda Local con Recocido Simulado (enfocada en reducir hard)
    # --------------------------------------------------------------
    def _simulated_annealing(self, sol_inicial, max_iters=50000, temp_inicial=10000):
        current = deepcopy(sol_inicial)
        best = deepcopy(sol_inicial)
        cost_current = self._evaluar_solucion(current)
        cost_best = cost_current
        temp = temp_inicial

        for it in range(max_iters):
            # Generar vecino: cambiar una sección aleatoria
            idx = random.randrange(len(current))
            s = current[idx]['seccion']
            ops = self.opciones_por_seccion[idx]
            if len(ops) <= 1:
                continue
            # Elegir una opción diferente
            current_op = (current[idx]['profesor'], current[idx]['patron'], current[idx]['ini'], current[idx]['salon'])
            nuevas_ops = [op for op in ops if op != current_op]
            if not nuevas_ops:
                continue
            nueva_op = random.choice(nuevas_ops)
            prof, patron, ini, salon = nueva_op
            # Aplicar cambio
            old = current[idx]
            current[idx] = {'seccion': s, 'profesor': prof, 'salon': salon, 'patron': patron, 'ini': ini}
            cost_new = self._evaluar_solucion(current)

            # Aceptación
            if cost_new <= cost_current or random.random() < math.exp((cost_current - cost_new) / temp):
                cost_current = cost_new
                if cost_new < cost_best:
                    best = deepcopy(current)
                    cost_best = cost_new
            else:
                current[idx] = old  # revertir

            temp *= 0.9995
            if temp < 0.1:
                temp = temp_inicial / (it + 1)

            # Si ya no hay hard conflicts, podemos parar temprano
            if cost_best < 1e6:
                break

        return best, cost_best

    # --------------------------------------------------------------
    # Reparación Quirúrgica de Conflictos Hard
    # --------------------------------------------------------------
    def _reparar_conflictos(self, sol):
        # Identificar secciones con conflictos hard
        hard_conflicts = self._evaluar_solucion(sol, solo_hard=True)
        if hard_conflicts == 0:
            return sol

        # Encontrar las secciones involucradas en conflictos
        conflictivas = set()
        occ_prof = defaultdict(list)
        occ_salon = defaultdict(list)
        carga = defaultdict(float)

        for idx, asign in enumerate(sol):
            s = asign['seccion']
            prof = asign['profesor']
            salon = asign['salon']
            patron = asign['patron']
            ini = asign['ini']
            creditos = self.get_sec_creditos(s, prof)
            carga[prof] += creditos

            for dia, contrib in patron['days'].items():
                fin = ini + int(contrib * 50)
                # Profesor
                for (ini_ex, fin_ex, idx_ex) in occ_prof.get((prof, dia), []):
                    if max(ini, ini_ex) < min(fin, fin_ex):
                        conflictivas.add(idx)
                        conflictivas.add(idx_ex)
                occ_prof.setdefault((prof, dia), []).append((ini, fin, idx))
                # Salón
                for (ini_ex, fin_ex, cupo_ex, fus_ex, idx_ex) in occ_salon.get((salon, dia), []):
                    if max(ini, ini_ex) < min(fin, fin_ex):
                        if not (salon in self.mega_salones and s.es_fusionable and fus_ex and s.cupo + cupo_ex <= self.salon_capacidad.get(salon, 0)):
                            conflictivas.add(idx)
                            conflictivas.add(idx_ex)
                occ_salon.setdefault((salon, dia), []).append((ini, fin, s.cupo, s.es_fusionable, idx))

        # También marcar por carga
        for prof, c in carga.items():
            if prof in self.profesores:
                if c > self.profesores[prof].carga_max + 1.5 or c < self.profesores[prof].carga_min - 1.5:
                    for idx, asign in enumerate(sol):
                        if asign['profesor'] == prof:
                            conflictivas.add(idx)

        if not conflictivas:
            return sol

        # Para cada sección conflictiva, intentar reasignar a la mejor opción disponible
        for idx in conflictivas:
            s = sol[idx]['seccion']
            ops = self.opciones_por_seccion[idx]
            best_op = None
            best_cost = float('inf')
            for op in ops:
                prof, patron, ini, salon = op
                temp_sol = deepcopy(sol)
                temp_sol[idx] = {'seccion': s, 'profesor': prof, 'salon': salon, 'patron': patron, 'ini': ini}
                cost = self._evaluar_solucion(temp_sol, solo_hard=True)
                if cost < best_cost:
                    best_cost = cost
                    best_op = op
            if best_op:
                prof, patron, ini, salon = best_op
                sol[idx] = {'seccion': s, 'profesor': prof, 'salon': salon, 'patron': patron, 'ini': ini}

        return sol

    # --------------------------------------------------------------
    # Optimización Principal
    # --------------------------------------------------------------
    def optimizar(self, bar=None, status_text=None):
        if status_text: status_text.markdown("**🔨 Generando solución inicial...**")
        sol = self._solucion_inicial()
        hard_inicial = self._evaluar_solucion(sol, solo_hard=True)
        if status_text: status_text.markdown(f"**📊 Hard inicial: {hard_inicial}**")

        # Fase 1: Recocido Simulado para reducir hard conflicts
        if hard_inicial > 0:
            if status_text: status_text.markdown("**🔥 Fase 1: Recocido Simulado (búsqueda global)...**")
            sol, cost = self._simulated_annealing(sol, max_iters=30000, temp_inicial=5000)
            hard_despues = self._evaluar_solucion(sol, solo_hard=True)
            if status_text: status_text.markdown(f"**📊 Hard después de SA: {hard_despues}**")
            if bar: bar.progress(0.4)

        # Fase 2: Reparación quirúrgica
        if self._evaluar_solucion(sol, solo_hard=True) > 0:
            if status_text: status_text.markdown("**🔧 Fase 2: Reparación de conflictos residuales...**")
            sol = self._reparar_conflictos(sol)
            if bar: bar.progress(0.7)

        # Fase 3: Compactación suave (opcional)
        if status_text: status_text.markdown("**✨ Fase 3: Ajustes de calidad...**")
        # Pequeña búsqueda local para mejorar soft sin introducir hard
        for _ in range(5000):
            idx = random.randrange(len(sol))
            s = sol[idx]['seccion']
            ops = self.opciones_por_seccion[idx]
            if len(ops) <= 1: continue
            current_op = (sol[idx]['profesor'], sol[idx]['patron'], sol[idx]['ini'], sol[idx]['salon'])
            nuevas = [op for op in ops if op != current_op]
            if not nuevas: continue
            nueva = random.choice(nuevas)
            old = sol[idx]
            sol[idx] = {'seccion': s, 'profesor': nueva[0], 'salon': nueva[3], 'patron': nueva[1], 'ini': nueva[2]}
            if self._evaluar_solucion(sol, solo_hard=True) > 0:
                sol[idx] = old
        if bar: bar.progress(1.0)

        hard_final = self._evaluar_solucion(sol, solo_hard=True)
        conflictos = int(hard_final // 1e6) if hard_final >= 1e6 else 0
        self.mejor_solucion = sol
        self.mejor_costo = self._evaluar_solucion(sol)
        self.historial_costos = [self.mejor_costo]
        return sol, conflictos, self.historial_costos

    def _obtener_conflictos(self, sol):
        conflictos = []
        # Implementación simplificada de auditoría
        hard = self._evaluar_solucion(sol, solo_hard=True)
        if hard > 0:
            conflictos.append(f"Conflictos duros detectados (puntuación: {hard})")
        return conflictos

# ==============================================================================
# 5. VISUALIZACIONES (MANTENIDAS)
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
        if salon == "TBA": continue
        patron = asign['patron']
        ini = asign['ini']
        for dia, contrib in patron['days'].items():
            if dia not in dias_semana: continue
            dia_idx = dias_semana.index(dia)
            duracion = int(contrib * 50)
            for minuto in range(ini, ini + duracion, 30):
                if minuto in horas_del_dia:
                    hora_idx = horas_del_dia.index(minuto)
                    matriz[hora_idx, dia_idx] += 1
    if total_salones > 0:
        matriz_porcentaje = (matriz / total_salones) * 100
    else:
        matriz_porcentaje = matriz
    etiquetas_horas = [mins_to_str(h).replace(' AM', '').replace(' PM', '') for h in horas_del_dia]
    fig = px.imshow(matriz_porcentaje, labels=dict(x="Día", y="Hora de Inicio", color="% Ocupación"),
                    x=dias_semana, y=etiquetas_horas, color_continuous_scale='YlOrRd', aspect='auto', zmin=0, zmax=100)
    fig.update_layout(title="Ocupación de Salones por Día y Hora", font=dict(color='#1a1a1a'),
                      paper_bgcolor='white', plot_bgcolor='white', height=600)
    return fig

def generar_barras_apiladas_profesor(sol, scheduler):
    df_asign = pd.DataFrame([{'Profesor': a['profesor'], 'Dia': dia, 'Cantidad': 1}
                             for a in sol if a['profesor'] not in ['TBA', 'GRADUADOS']
                             for dia in a['patron']['days'].keys()])
    if df_asign.empty: return go.Figure()
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
        fig.add_trace(go.Bar(name=dia, x=profes_ordenados, y=y_vals, marker_color=colores[i]))
    fig.update_layout(barmode='stack', title="Distribución de Clases por Profesor y Día",
                      xaxis_title="Profesor", yaxis_title="Número de Clases", font=dict(color='#1a1a1a'),
                      paper_bgcolor='white', plot_bgcolor='white', legend_title="Día", height=500)
    return fig

def generar_evolucion_fitness_plotly(historial):
    if not historial: return go.Figure()
    fitness = [10000 / (10000 + c) for c in historial]
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=fitness, mode='lines+markers', line=dict(color='#D4AF37', width=3),
                             marker=dict(size=4, color='#8E6E13'), fill='tozeroy', fillcolor='rgba(212, 175, 55, 0.2)', name='Fitness'))
    fig.update_layout(title="Evolución del Fitness", xaxis_title="Iteración", yaxis_title="Fitness",
                      font=dict(color='#1a1a1a', size=12), paper_bgcolor='white', plot_bgcolor='white', height=450)
    return fig

def generar_calendario_visual(sol, scheduler, filtro_prof=None, filtro_salon=None, filtro_curso=None):
    dias_semana = ['Lu', 'Ma', 'Mi', 'Ju', 'Vi']
    eventos = []
    for a in sol:
        if filtro_prof and a['profesor'] != filtro_prof: continue
        if filtro_salon and a['salon'] != filtro_salon: continue
        if filtro_curso and filtro_curso not in a['seccion'].cod: continue
        for dia, contrib in a['patron']['days'].items():
            inicio = a['ini']
            duracion = contrib * 50
            fin = inicio + duracion
            hora_inicio = mins_to_str(inicio)
            hora_fin = mins_to_str(fin)
            texto = f"<b>{a['profesor']}</b><br>{a['seccion'].cod}<br>{a['salon']}<br>{hora_inicio} - {hora_fin}"
            eventos.append({'Dia': dia, 'Inicio': inicio, 'Fin': fin, 'Profesor': a['profesor'],
                            'Seccion': a['seccion'].cod, 'Salon': a['salon'], 'Texto': texto})
    if not eventos: return go.Figure()
    df = pd.DataFrame(eventos)
    dia_a_idx = {d: i for i, d in enumerate(dias_semana)}
    df['Dia_idx'] = df['Dia'].map(dia_a_idx)
    profes = df['Profesor'].unique()
    colores = px.colors.qualitative.Plotly[:len(profes)]
    color_map = {p: colores[i % len(colores)] for i, p in enumerate(profes)}
    fig = go.Figure()
    for _, row in df.iterrows():
        fig.add_trace(go.Scatter(x=[row['Inicio'], row['Fin'], row['Fin'], row['Inicio'], row['Inicio']],
                                 y=[row['Dia_idx']-0.4, row['Dia_idx']-0.4, row['Dia_idx']+0.4, row['Dia_idx']+0.4, row['Dia_idx']-0.4],
                                 fill='toself', fillcolor=color_map[row['Profesor']], line=dict(width=1, color='black'),
                                 name=row['Profesor'], legendgroup=row['Profesor'], showlegend=False,
                                 hoverinfo='text', hovertext=row['Texto']))
    for prof, color in color_map.items():
        fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers', marker=dict(size=10, color=color),
                                 name=prof, legendgroup=prof, showlegend=True))
    fig.update_layout(title="Horario Semanal - Vista Calendario",
                      xaxis=dict(title="Hora del día", tickvals=list(range(420, 1140, 60)),
                                 ticktext=[mins_to_str(m).replace(' AM', '').replace(' PM', '') for m in range(420, 1140, 60)],
                                 range=[scheduler.limite_operativo[0]-30, scheduler.limite_operativo[1]+30]),
                      yaxis=dict(title="Día", tickvals=list(range(len(dias_semana))), ticktext=dias_semana),
                      font=dict(color='#1a1a1a'), paper_bgcolor='white', plot_bgcolor='white', height=600,
                      hovermode='closest', legend=dict(title="Profesor", orientation='h', yanchor='bottom', y=1.02))
    return fig

def generar_reporte_pdf_html(scheduler, sol, cargas_finales, master_df):
    total_secciones = len(sol)
    secciones_tba = sum(1 for a in sol if a['profesor'] == 'TBA')
    carga_total = sum(cargas_finales.values())
    profesores_con_carga = len([c for c in cargas_finales.values() if c > 0])
    html = f"""
    <html><head><title>Reporte Ejecutivo - UPRM Scheduler</title>
    <style>body{{font-family:'Segoe UI',Arial,sans-serif;margin:40px;background:white;color:#1a1a1a;}}
    h1{{color:#1a1a1a;border-bottom:2px solid #D4AF37;padding-bottom:10px;}}h2{{color:#1a1a1a;margin-top:30px;}}
    .stats{{display:flex;gap:20px;margin-bottom:30px;}}.stat-card{{background:#f8f9fa;border:1px solid #ddd;border-radius:8px;padding:15px;flex:1;}}
    table{{border-collapse:collapse;width:100%;margin-bottom:20px;}}th,td{{border:1px solid #ddd;padding:8px;text-align:left;}}
    th{{background-color:#f2f2f2;}}.footer{{margin-top:40px;font-size:0.9em;color:#666;text-align:center;}}</style></head>
    <body><h1>UPRM Scheduler - Reporte Ejecutivo</h1><p>Generado el: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
    <div class="stats"><div class="stat-card"><h3>Total Secciones</h3><p style="font-size:24px;font-weight:bold;">{total_secciones}</p></div>
    <div class="stat-card"><h3>Secciones TBA</h3><p style="font-size:24px;font-weight:bold;">{secciones_tba} ({secciones_tba/total_secciones*100:.1f}%)</p></div>
    <div class="stat-card"><h3>Carga Total (Créditos)</h3><p style="font-size:24px;font-weight:bold;">{carga_total:.1f}</p></div>
    <div class="stat-card"><h3>Profesores Activos</h3><p style="font-size:24px;font-weight:bold;">{profesores_con_carga}</p></div></div>
    <h2>Listado de Secciones TBA</h2>
    {master_df[master_df['Persona'] == 'TBA'][['ID', 'Asignatura', 'Estudiantes (Cupo)', 'Días', 'Horario', 'Salón']].to_html(index=False) if secciones_tba > 0 else '<p>No hay secciones TBA.</p>'}
    <h2>Horarios por Profesor</h2>
    {''.join([f'<h3>{p}</h3>{master_df[master_df["Persona"]==p][["ID", "Asignatura", "Días", "Horario", "Salón"]].to_html(index=False)}' for p in sorted(master_df['Persona'].unique()) if p not in ['TBA', 'GRADUADOS']])}
    <div class="footer">Reporte generado automáticamente por UPRM Timetable System.</div>
    <script>window.onload = function(){{window.print();}}</script></body></html>"""
    return html

def generar_figura_cientifica_carga(cargas_finales, scheduler):
    profesores = list(cargas_finales.keys())
    profesores.sort(key=lambda p: cargas_finales[p], reverse=True)
    carga_asignada = [cargas_finales[p] for p in profesores]
    carga_min = [scheduler.profesores[p].carga_min for p in profesores]
    carga_max = [scheduler.profesores[p].carga_max for p in profesores]
    x_vals = list(range(len(profesores)))
    fig = go.Figure()
    fig.add_trace(go.Bar(x=x_vals, y=carga_asignada, name='Carga Asignada', marker=dict(color='lightgray', line=dict(color='black', width=1))))
    fig.add_trace(go.Scatter(x=x_vals, y=carga_min, mode='lines+markers', name='Carga Mínima', line=dict(color='blue', width=2, dash='dot'), marker=dict(size=6)))
    fig.add_trace(go.Scatter(x=x_vals, y=carga_max, mode='lines+markers', name='Carga Máxima', line=dict(color='orange', width=2, dash='dot'), marker=dict(size=6)))
    fig.update_layout(title="Análisis de Carga Académica por Profesor",
                      xaxis=dict(title="Profesores (índice)", tickvals=x_vals, ticktext=[f"P{i+1}" for i in x_vals]),
                      yaxis=dict(title="Cantidad de Créditos Semanales"), font=dict(color='#1a1a1a'),
                      paper_bgcolor='white', plot_bgcolor='white', legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5), height=500)
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    return fig

def generar_plantilla():
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_cursos = pd.DataFrame({'CODIGO': ['MATE3171', 'MATE3172'], 'CREDITOS': [3, 3], 'DEMANDA': [120, 150],
                                  'CUPO': [30, 30], 'CANDIDATOS': ['PEREZ, GONZALEZ', 'RODRIGUEZ'], 'TIPO_SALON': [1, 1]})
        df_cursos.to_excel(writer, sheet_name='Cursos', index=False)
        df_profes = pd.DataFrame({'NOMBRE': ['PEREZ', 'GONZALEZ'], 'CARGA_MIN': [9, 6], 'CARGA_MAX': [15, 12],
                                  'PREF_DIAS': ['LMV', 'MJ'], 'PREF_HORAS': ['AM', 'PM'], 'BLOQUEO_DIAS': ['', ''],
                                  'BLOQUEO_HORA_INI': ['', ''], 'BLOQUEO_HORA_FIN': ['', ''],
                                  'PREF1': ['MATE3171', 'MATE3172'], 'PREF2': ['', ''], 'PREF3': ['', ''],
                                  'COMPENSACION': ['NO', 'SI'], 'ACEPTA_GRANDES': [0, 1], 'CURSOS_INTENSIVOS': [0, 1]})
        df_profes.to_excel(writer, sheet_name='Profesores', index=False)
        df_salones = pd.DataFrame({'CODIGO': ['S-101', 'S-102'], 'CAPACIDAD': [30, 40], 'TIPO': [1, 2]})
        df_salones.to_excel(writer, sheet_name='Salones', index=False)
    output.seek(0)
    return output.getvalue()

# ==============================================================================
# 6. UI PRINCIPAL
# ==============================================================================
def main():
    with st.sidebar:
        st.markdown("### ∑ Configuración")
        zona = st.selectbox("Zona Campus", ["CENTRAL", "PERIFERICA"])
        file = st.file_uploader("Subir Protocolo Excel", type=['xlsx'])
        st.download_button("📥 Descargar Plantilla", data=generar_plantilla(),
                           file_name="PLANTILLA.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    st.markdown(f"### Ω Condiciones de Zona: {zona}")
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Ventana Operativa", "07:30 AM - 06:30 PM" if zona == "CENTRAL" else "07:00 AM - 06:00 PM")
    with c2: st.metric("Hora Universal", "10:30 AM - 12:30 PM" if zona == "CENTRAL" else "10:00 AM - 12:00 PM")
    with c3: st.markdown("""<div class="status-badge">RESTRICCIONES FUERTES ACTIVAS</div>""", unsafe_allow_html=True)

    if not file:
        st.markdown("""
            <div class='glass-card' style='text-align: center;'>
                <h3 style='margin-top:0; color: #D4AF37;'>📥 Sincronización de Datos</h3>
                <p>Asegúrese de que el archivo Excel contiene las hojas: <b>Cursos</b>, <b>Profesores</b>, <b>Salones</b>.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        if st.button("🚀 INICIAR OPTIMIZACIÓN ABSOLUTA"):
            try:
                with st.spinner("Construyendo y optimizando..."):
                    xls = pd.ExcelFile(file)
                    df_cursos = pd.read_excel(xls, 'Cursos')
                    df_profes = pd.read_excel(xls, 'Profesores')
                    df_salones = pd.read_excel(xls, 'Salones')
                    df_grad = None
                    if 'Graduados' in xls.sheet_names:
                        df_grad = pd.read_excel(xls, 'Graduados')

                    scheduler = UltraScheduler(df_cursos, df_profes, df_salones, zona, df_grad)
                    start_time = time.time()
                    bar = st.progress(0)
                    status = st.empty()
                    mejor_sol, conflictos, historial = scheduler.optimizar(bar=bar, status_text=status)
                    elapsed = time.time() - start_time

                    st.session_state.elapsed_time = elapsed
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

            except Exception as e:
                st.error(f"Error: {e}")
                return

    if 'master' in st.session_state:
        st.success(f"✅ Optimización completada en {st.session_state.elapsed_time:.2f} segundos.")
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        t1, t2, t3, t4 = st.tabs(["💎 PANEL DE CONTROL", "🔍 VISTAS DETALLADAS", "🚨 AUDITORÍA DE CALIDAD", "📊 ANALÍTICAS AVANZADAS"])
        with t1:
            edited = st.data_editor(st.session_state.master, use_container_width=True, height=500)
            st.download_button("💾 EXPORTAR EXCEL PLATINUM", exportar_todo(edited), "Horario_Final_UPRM.xlsx", use_container_width=True)
        with t2:
            f1, f2, f3 = st.tabs(["Por Profesor", "Por Curso", "Por Salón"])
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
        with t3:
            conflictos = st.session_state.conflicts
            if conflictos > 0:
                st.error(f"⚠️ Aún persisten {conflictos} conflictos duros.")
                for conf in st.session_state.detailed_conflicts:
                    st.write(f"- {conf}")
            else:
                st.success("✅ 100% Asignación Perfecta. Cero Conflictos Duros.")
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
                    st.session_state.mejor_sol, st.session_state.scheduler,
                    filtro_prof if filtro_prof != 'Todos' else None,
                    filtro_salon if filtro_salon != 'Todos' else None,
                    filtro_curso if filtro_curso != 'Todos' else None
                )
                st.plotly_chart(fig_cal, use_container_width=True)
            with subtab3:
                st.markdown("#### Exportar Reporte Ejecutivo en PDF")
                if st.button("📑 Generar Reporte PDF (Imprimir)"):
                    html_reporte = generar_reporte_pdf_html(
                        st.session_state.scheduler, st.session_state.mejor_sol,
                        st.session_state.cargas_finales, st.session_state.master
                    )
                    st.components.v1.html(html_reporte, height=600, scrolling=True)
                st.info("Haz clic para generar e imprimir como PDF.")
            with subtab4:
                st.markdown("#### Análisis Científico de Carga Académica")
                fig_carga = generar_figura_cientifica_carga(st.session_state.cargas_finales, st.session_state.scheduler)
                st.plotly_chart(fig_carga, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
