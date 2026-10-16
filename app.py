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
from itertools import combinations

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

def normalizar_codigo_curso(codigo):
    """Compara el código completo, ignorando mayúsculas y espacios."""
    return re.sub(r"\s+", "", str(codigo)).upper()


def parsear_cursos_intensivos(valor, nombre="Profesor"):
    """Lee 0/vacío o 1,DIA,CURSO; devuelve {codigo_curso: dia_interno}.

    Ejemplo: 1,W,MATE6026 -> {'MATE6026': 'Mi'}.
    Para varias materias: 1,W,MATE6026;1,J,MATE6000.
    Un 1 sin día y curso se rechaza para no afectar todas las materias.
    """
    if valor is None or pd.isna(valor):
        return {}
    texto = str(valor).strip().upper()
    if texto in {"", "0", "0.0", "NO", "FALSE", "FALSO"}:
        return {}

    mapa_dias = {
        'L': 'Lu', 'LU': 'Lu', 'LUNES': 'Lu',
        'M': 'Ma', 'MA': 'Ma', 'MARTES': 'Ma',
        'W': 'Mi', 'MI': 'Mi', 'MIERCOLES': 'Mi', 'MIÉRCOLES': 'Mi',
        'J': 'Ju', 'JU': 'Ju', 'JUEVES': 'Ju',
        'V': 'Vi', 'VI': 'Vi', 'VIERNES': 'Vi',
    }
    solicitudes = {}
    for entrada in re.split(r"[;\r\n]+", texto):
        if not entrada.strip():
            continue
        partes = [parte.strip() for parte in entrada.split(',')]
        if len(partes) != 3 or partes[0] != '1' or not partes[2]:
            raise ValueError(
                f"{nombre}: CURSOS_INTENSIVOS inválido: {entrada!r}. "
                "Usa 0 o 1,DIA,CURSO, por ejemplo 1,W,MATE6026. "
                "El valor 1 solo ya no basta; indica el día y el curso."
            )
        dia = mapa_dias.get(partes[1])
        if dia is None:
            raise ValueError(
                f"{nombre}: día inválido en CURSOS_INTENSIVOS: {partes[1]!r}. "
                "Usa L (lunes), M (martes), W (miércoles), J (jueves) o V (viernes)."
            )
        curso = normalizar_codigo_curso(partes[2])
        if not curso:
            raise ValueError(f"{nombre}: falta el código del curso en CURSOS_INTENSIVOS.")
        if curso in solicitudes and solicitudes[curso] != dia:
            raise ValueError(
                f"{nombre}: {curso} tiene dos días intensivos distintos. "
                "Indica un solo día por curso."
            )
        solicitudes[curso] = dia
    if not solicitudes:
        raise ValueError(f"{nombre}: CURSOS_INTENSIVOS debe ser 0 o 1,DIA,CURSO.")
    return solicitudes


def es_patron_intensivo(patron):
    """Una sesión semanal de más de un bloque (incluye cursos de 2 créditos)."""
    return len(patron['days']) == 1 and any(c > 1 for c in patron['days'].values())


def mins_to_str(m):
    h, mins = divmod(int(m), 60)
    am_pm = "AM" if h < 12 else "PM"
    h_disp = h if h <= 12 else h - 12
    if h_disp == 0: h_disp = 12
    return f"{h_disp:02d}:{mins:02d} {am_pm}"

def str_to_mins(t_str):
    if isinstance(t_str, dtime):
        if t_str.second or t_str.microsecond:
            raise ValueError("La hora debe tener precisión de minutos.")
        return t_str.hour * 60 + t_str.minute
    if isinstance(t_str, (int, float, np.integer, np.floating)):
        valor = float(t_str)
        minutos = valor * 1440
        if not 0 <= valor < 1 or abs(minutos - round(minutos)) > 1e-6:
            raise ValueError("La hora numérica debe ser una fracción de día de Excel, sin segundos.")
        return int(round(minutos))
    texto = str(t_str).strip().upper()
    match = re.fullmatch(r"(\d{1,2}):(\d{2})(?::00)?\s*(AM|PM)?", texto)
    if not match:
        raise ValueError(f"Hora inválida: {t_str!r}. Usa HH:MM o HH:MM AM/PM.")
    h, m = int(match[1]), int(match[2])
    ampm = match[3]
    if m > 59 or (ampm and not 1 <= h <= 12) or (not ampm and not 0 <= h <= 23):
        raise ValueError(f"Hora fuera de rango: {t_str!r}.")
    if ampm:
        h = h % 12 + (12 if ampm == "PM" else 0)
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
        self.pref_horas = str(pref_horas).strip().upper() if pd.notna(pref_horas) else 'ANY'
        if self.pref_horas == '':
            self.pref_horas = 'ANY'
        if self.pref_horas not in {'AM', 'PM', 'ANY'}:
            raise ValueError(f"{self.nombre}: PREF_HORAS debe ser AM, PM, ANY o vacío.")

        # Disponibilidad obligatoria. Un dato inválido nunca se ignora.
        self.hora_entrada_min = None
        self.hora_salida_min = None
        for campo, valor, atributo in (
            ('HORA_ENTRADA', hora_entrada, 'hora_entrada_min'),
            ('HORA_SALIDA', hora_salida, 'hora_salida_min'),
        ):
            if pd.notna(valor) and str(valor).strip():
                try:
                    setattr(self, atributo, str_to_mins(valor))
                except ValueError as exc:
                    raise ValueError(f"{self.nombre}: {campo}: {exc}") from exc
        if (self.hora_entrada_min is not None and self.hora_salida_min is not None
                and self.hora_entrada_min >= self.hora_salida_min):
            raise ValueError(f"{self.nombre}: HORA_ENTRADA debe ser anterior a HORA_SALIDA.")

        self.preferencias = []
        if isinstance(preferencias_cursos, list):
            self.preferencias = [c.upper().strip() for c in preferencias_cursos if c and str(c).upper() != 'NAN']
            
        self.compensacion = excel_bool(compensacion)
        self.acepta_grandes = int(acepta_grandes) if pd.notnull(acepta_grandes) and acepta_grandes != '' else 0
        
        self.cursos_intensivos = parsear_cursos_intensivos(cursos_intensivos, self.nombre)

    def dia_intensivo_para(self, seccion_cod):
        # Quitar únicamente el sufijo de sección: MATE6026-01 -> MATE6026.
        curso = normalizar_codigo_curso(seccion_cod.rsplit('-', 1)[0])
        return self.cursos_intensivos.get(curso)

    def prioridad_curso(self, curso_cod):
        for idx, pref in enumerate(self.preferencias):
            if pref in curso_cod:
                return 1.0 / (idx + 1)
        return 0.0

    def _parse_pref_dias(self, pref_dias):
        if pref_dias is None or pd.isna(pref_dias) or not str(pref_dias).strip():
            return set()
        texto = str(pref_dias).strip().upper()
        mapa = {
            'L': 'Lu', 'LU': 'Lu', 'LUNES': 'Lu',
            'M': 'Ma', 'MA': 'Ma', 'MARTES': 'Ma',
            'W': 'Mi', 'MI': 'Mi', 'MIERCOLES': 'Mi', 'MIÉRCOLES': 'Mi',
            'J': 'Ju', 'JU': 'Ju', 'JUEVES': 'Ju',
            'V': 'Vi', 'VI': 'Vi', 'VIERNES': 'Vi',
        }
        dias = set()
        for token in re.split(r"[,;\s/-]+", texto):
            if token in mapa:
                dias.add(mapa[token])
            elif token and all(c in 'LMWJV' for c in token):
                dias.update(mapa[c] for c in token)
            else:
                raise ValueError(f"{self.nombre}: PREF_DIAS inválido: {pref_dias!r}. Usa L, M, W, J, V.")
        return dias

def compatible_tipo(tipos_permitidos_curso, salon_tipo):
    """Compara categorías exactas: los tipos 4, 5 y 6 no son tipo 3."""
    try:
        tipo_num = float(salon_tipo)
    except (TypeError, ValueError):
        return False
    if not math.isfinite(tipo_num) or not tipo_num.is_integer():
        return False
    return str(int(tipo_num)) in tipos_permitidos_curso

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
        self._planes_tipos_salones_cache = {}

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

        # Validar las referencias contra los cursos y candidatos reales del Excel.
        self._validar_solicitudes_intensivas(cursos_agrupados)
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

        # No gastar la búsqueda ni construir un horario publicable con datos incompatibles.
        self.problemas_factibilidad = self.validar_factibilidad_inicial()
        self.solucion = [] if self.problemas_factibilidad else self._construir_solucion_greedy()
        self.mejor_solucion = deepcopy(self.solucion)
        self.mejor_costo = self._costo_total(self.solucion)
        self.historial_costos = [self.mejor_costo]

    def _errores_estructura_y_aforo(self, sol):
        errores = []
        for a in sol:
            s, prof, salon = a['seccion'], a['profesor'], a['salon']
            if prof != 'TBA' and prof not in s.cands:
                errores.append(f'{s.cod}: {prof} no es un candidato autorizado.')
            if prof not in self.profesores and prof not in {'TBA', 'GRADUADOS'}:
                errores.append(f'{s.cod}: profesor desconocido: {prof}.')
            if salon != 'TBA' and salon not in self.salon_capacidad:
                errores.append(f'{s.cod}: salón desconocido: {salon}.')
            if a['patron'] not in PATRONES.get(s.creditos, []):
                errores.append(f'{s.cod}: patrón no definido para {s.creditos} créditos.')
            if a['ini'] not in self.bloques:
                errores.append(f'{s.cod}: inicio fuera de la grilla institucional.')
        for salon in self.mega_salones:
            for dia in ['Lu', 'Ma', 'Mi', 'Ju', 'Vi']:
                eventos = []
                for a in sol:
                    if a['salon'] == salon and dia in a['patron']['days']:
                        fin = a['ini'] + int(a['patron']['days'][dia] * 50)
                        eventos.extend([(a['ini'], a['seccion'].cupo), (fin, -a['seccion'].cupo)])
                ocupacion = 0
                for _, delta in sorted(eventos):
                    ocupacion += delta
                    if ocupacion > self.salon_capacidad[salon]:
                        errores.append(f'Salón {salon} el {dia}: cupo simultáneo total {ocupacion} excede su capacidad.')
                        break
        return errores

    def _validar_capacidad_salones(self):
        # Condición necesaria: las clases que solo pueden ir a un conjunto de
        # salones deben caber en sus minutos semanales. Se omiten los mega
        # salones, donde la política institucional permite fusionar secciones.
        opciones = {}
        for s in self.secciones:
            opciones[s.cod] = frozenset(sl['CODIGO'] for sl in self.salones
                if sl['CAPACIDAD'] >= s.cupo and compatible_tipo(s.tipos_permitidos, sl['TIPO']))
        minutos_salon = 5 * (self.limite_operativo[1] - self.limite_operativo[0])
        minutos_salon -= 2 * max(0, min(self.hora_universal[1], self.limite_operativo[1])
                                  - max(self.hora_universal[0], self.limite_operativo[0]))
        errores = []
        for grupo in sorted(set(opciones.values()), key=lambda g: (len(g), sorted(g))):
            if not grupo or grupo.intersection(self.mega_salones):
                continue
            obligadas = [s for s in self.secciones if opciones[s.cod] and opciones[s.cod].issubset(grupo)]
            necesarios = sum(s.creditos * 50 for s in obligadas)
            disponibles = len(grupo) * minutos_salon
            if necesarios > disponibles:
                cursos = ', '.join(sorted({s.cod.rsplit('-', 1)[0] for s in obligadas}))
                errores.append(f'Capacidad semanal insuficiente en {", ".join(sorted(grupo))}: '
                    f'{len(obligadas)} secciones ({cursos}) necesitan {necesarios} minutos-salón; '
                    f'solo hay {disponibles}, incluso antes de aplicar la grilla de inicios.')
        return errores

    def _asignacion_local_valida(self, idx, asign, sol):
        s, prof, salon = asign['seccion'], asign['profesor'], asign['salon']
        patron, ini = asign['patron'], asign['ini']
        if prof not in s.cands or (prof not in self.profesores and prof != 'GRADUADOS'):
            return False
        if salon not in self._salones_validos_para(s, prof, sol, idx):
            return False
        if prof in self.profesores and s.es_grande and not self.profesores[prof].acepta_grandes:
            return False
        if patron not in self._patrones_validos_para_profesor(s, prof):
            return False
        if ini not in self._horas_validas_para_profesor(s, prof, patron):
            return False
        otras = [a for j, a in enumerate(sol) if j != idx and a and a['profesor'] != 'TBA']
        if prof in self.profesores:
            carga = self.get_sec_creditos(s, prof) + sum(self.get_sec_creditos(a['seccion'], prof)
                for a in otras if a['profesor'] == prof)
            if carga > self.profesores[prof].carga_max + .5:
                return False
        for a in otras:
            for dia, contrib in patron['days'].items():
                if dia not in a['patron']['days']:
                    continue
                fin = ini + int(contrib * 50)
                fin_otro = a['ini'] + int(a['patron']['days'][dia] * 50)
                if max(ini, a['ini']) >= min(fin, fin_otro):
                    continue
                if a['profesor'] == prof and prof != 'GRADUADOS':
                    return False
                if a['salon'] == salon:
                    if not (salon in self.mega_salones and s.es_fusionable and a['seccion'].es_fusionable):
                        return False
                # Comprobar las dos direcciones del doble rol. No depende
                # del orden en que se insertan la clase dictada y la recibida.
                base = s.cod.rsplit('-', 1)[0]
                otra_base = a['seccion'].cod.rsplit('-', 1)[0]
                if otra_base in self.graduados_reciben.get(prof, []):
                    return False
                if base in self.graduados_reciben.get(a['profesor'], []):
                    return False
        if salon in self.mega_salones:
            grupo = [a for a in otras if a['salon'] == salon] + [asign]
            for dia in patron['days']:
                eventos = []
                for a in grupo:
                    if dia in a['patron']['days']:
                        eventos.extend([(a['ini'], a['seccion'].cupo),
                            (a['ini'] + int(a['patron']['days'][dia] * 50), -a['seccion'].cupo)])
                ocupacion = 0
                for _, delta in sorted(eventos):
                    ocupacion += delta
                    if ocupacion > self.salon_capacidad[salon]:
                        return False
        return True

    def get_sec_creditos(self, s, prof_name):
        if prof_name in self.profesores and self.profesores[prof_name].compensacion:
            return get_creditos_reales(s.creditos, s.cupo)
        return float(s.creditos)

    def _dividir_demanda_normal(self, demanda_total, cupo_tipico):
        """Cubre todo el remanente sin superar el cupo normal por sección.

        Un remanente pequeño también necesita plaza: nunca se descarta ni
        se crea una sección sin profesor permitido por defecto.
        """
        if demanda_total <= 0:
            return []
        if cupo_tipico <= 0:
            raise ValueError("CUPO debe ser mayor que cero.")
        llenas, sobrante = divmod(demanda_total, cupo_tipico)
        resultado = [(cupo_tipico, False) for _ in range(llenas)]
        if sobrante:
            resultado.append((sobrante, False))
        return resultado


    def _es_salon_especial(self, seccion):
        return set(seccion.tipos_permitidos) != {"1"}

    def _incumplimientos_disponibilidad(self, prof, patron, ini):
        """Las cuatro columnas limitan toda la clase, incluido su final."""
        obj = self.profesores.get(prof)
        if obj is None:
            return []
        errores = []
        for dia, contrib in patron['days'].items():
            fin = ini + int(contrib * 50)
            if obj.pref_dias_set and dia not in obj.pref_dias_set:
                errores.append(f"PREF_DIAS: {dia} no está permitido")
            if obj.pref_horas == 'AM' and fin > 720:
                errores.append(f"PREF_HORAS AM: la clase de {dia} termina después de las 12:00 PM")
            elif obj.pref_horas == 'PM' and ini < 720:
                errores.append(f"PREF_HORAS PM: la clase de {dia} comienza antes de las 12:00 PM")
            if obj.hora_entrada_min is not None and ini < obj.hora_entrada_min:
                errores.append(f"HORA_ENTRADA: inicio anticipado el {dia}")
            if obj.hora_salida_min is not None and fin > obj.hora_salida_min:
                errores.append(f"HORA_SALIDA: final tardío el {dia}")
        return errores

    def _penalidad_preferencias_horarias(self, prof, patron, ini):
        # Se conserva el nombre para limitar los cambios; ahora cuenta conflictos fuertes.
        return 10000 * len(self._incumplimientos_disponibilidad(prof, patron, ini))

    def _horas_validas_para_profesor(self, seccion, prof, patron):
        horas = []
        for ini in self.bloques:
            if self._incumplimientos_disponibilidad(prof, patron, ini):
                continue
            valido = True
            for dia, contrib in patron['days'].items():
                fin = ini + int(contrib * 50)
                if ini < self.limite_operativo[0] or fin > self.limite_operativo[1]:
                    valido = False
                if dia in ['Ma', 'Ju'] and max(ini, self.hora_universal[0]) < min(fin, self.hora_universal[1]):
                    valido = False
                if seccion.creditos == 3 and contrib >= 3 and ini < 930:
                    valido = False
            if valido:
                horas.append(ini)
        return horas

    def _caben_secciones_obligatorias(self, secciones, prof, max_nodos=10000):
        # Prueba local de imposibilidad. Ignora salones y otros docentes:
        # si ni siquiera así caben, tampoco cabe el horario completo.
        dominios = []
        for s in secciones:
            opciones = []
            for patron in self._patrones_validos_para_profesor(s, prof):
                for ini in self._horas_validas_para_profesor(s, prof, patron):
                    opciones.append([(dia, ini, ini + int(c * 50)) for dia, c in patron['days'].items()])
            if not opciones:
                return False
            dominios.append(opciones)
        dominios.sort(key=len)
        ocupados = {dia: [] for dia in ['Lu', 'Ma', 'Mi', 'Ju', 'Vi']}
        nodos = 0

        def buscar(i):
            nonlocal nodos
            nodos += 1
            if nodos > max_nodos:
                return None  # Límite de búsqueda: no demuestra imposibilidad.
            if i == len(dominios):
                return True
            for opcion in dominios[i]:
                if any(max(ini, a) < min(fin, b) for dia, ini, fin in opcion for a, b in ocupados[dia]):
                    continue
                for dia, ini, fin in opcion:
                    ocupados[dia].append((ini, fin))
                resultado = buscar(i + 1)
                for dia, _, _ in opcion:
                    ocupados[dia].pop()
                if resultado is not False:
                    return resultado
            return False

        return buscar(0)

    def _validar_solicitudes_intensivas(self, cursos_agrupados):
        cursos = {normalizar_codigo_curso(c): datos for c, datos in cursos_agrupados.items()}
        for nombre, obj in self.profesores.items():
            for curso, dia in obj.cursos_intensivos.items():
                contexto = f"{nombre}: CURSOS_INTENSIVOS ({curso}, {dia})"
                if curso not in cursos:
                    raise ValueError(f"{contexto}: el curso no existe en la hoja Cursos.")
                elegibles = [s for s in self.secciones
                    if normalizar_codigo_curso(s.cod.rsplit('-', 1)[0]) == curso
                    and nombre in s.cands]
                if not elegibles:
                    raise ValueError(
                        f"{contexto}: el profesor no figura entre los candidatos de ninguna "
                        "sección de ese curso. Revisa CANDIDATOS y DEMANDA."
                    )
                creditos = cursos[curso]['creditos']
                if not any(es_patron_intensivo(p) and set(p['days']) == {dia}
                           for p in PATRONES.get(creditos, [])):
                    raise ValueError(
                        f"{contexto}: no hay un patrón intensivo definido para "
                        f"un curso de {creditos} créditos en ese día."
                    )
                if obj.pref_dias_set and dia not in obj.pref_dias_set:
                    raise ValueError(f"{contexto}: el día solicitado no está permitido en PREF_DIAS.")

    def _incumplimientos_cursos_intensivos(self, seccion, prof, patron):
        """Regla compartida por generación, costo, auditoría y validación final."""
        obj = self.profesores.get(prof)
        if obj is None:
            return []
        dia = obj.dia_intensivo_para(seccion.cod)
        intensivo = es_patron_intensivo(patron)
        if dia is None:
            return ["curso no señalado en CURSOS_INTENSIVOS: debe usar horario normal"] if intensivo else []
        if not intensivo or set(patron['days']) != {dia}:
            return [f"CURSOS_INTENSIVOS exige este curso intensivo únicamente el {dia}"]
        return []

    def _patrones_validos_para_profesor(self, seccion, prof):
        patrones = PATRONES.get(seccion.creditos, PATRONES[3])
        if prof not in self.profesores:
            return patrones
        patrones = [p for p in patrones
                    if not self._incumplimientos_cursos_intensivos(seccion, prof, p)]
        prof_obj = self.profesores[prof]
        if prof_obj.pref_dias_set:
            patrones = [p for p in patrones if set(p['days']).issubset(prof_obj.pref_dias_set)]
        return patrones

    def _salones_compatibles_seccion(self, seccion):
        return [sl['CODIGO'] for sl in self.salones
                if sl['CAPACIDAD'] >= seccion.cupo
                and compatible_tipo(seccion.tipos_permitidos, sl['TIPO'])]

    def _planes_tipos_salones(self, secciones):
        """Conjuntos mínimos de tipos que cubren todas las clases y sus cupos.

        Si {1,3} y {1} pueden usar tipo 1, no se autoriza abrir un segundo tipo.
        Si un grupo grande solo cabe en tipo 3 y otro curso exige tipo 1,
        se permite la excepción {1,3}. Cada tipo conservará un solo salón.
        """
        dominios = {tuple(sorted({self.salon_tipo[sl]
                    for sl in self._salones_compatibles_seccion(s)})) for s in secciones}
        if not dominios or () in dominios:
            return ()
        clave = tuple(sorted(dominios))
        cache = self._planes_tipos_salones_cache
        if clave not in cache:
            tipos = sorted({tipo for dominio in dominios for tipo in dominio})
            planes = []
            for cantidad in range(1, len(tipos) + 1):
                planes = [frozenset(plan) for plan in combinations(tipos, cantidad)
                          if all(set(plan).intersection(d) for d in dominios)]
                if planes:
                    break
            cache[clave] = tuple(planes)
        return cache[clave]

    def _salones_validos_para(self, seccion, prof, sol=None, idx=None):
        salones_base = self._salones_compatibles_seccion(seccion)
        if prof not in self.profesores:
            return salones_base
        otras = [a for j, a in enumerate(sol or [])
                 if j != idx and a and a['profesor'] == prof and a['salon'] != 'TBA']
        # Incluir las clases obligatorias aún sin colocar evita escoger un
        # salón pequeño o un tipo opcional que bloquearía sus otras materias.
        requeridas = {s.cod: s for s in self.secciones if s.cands == [prof]}
        requeridas.update({a['seccion'].cod: a['seccion'] for a in otras})
        requeridas[seccion.cod] = seccion
        planes = self._planes_tipos_salones(requeridas.values())
        por_tipo = {}
        for a in otras:
            tipo = self.salon_tipo.get(a['salon'])
            if tipo is not None:
                por_tipo.setdefault(tipo, set()).add(a['salon'])
        if any(len(salones) > 1 for salones in por_tipo.values()):
            return []
        tipos_usados = set(por_tipo)
        dominios = [(s, set(self._salones_compatibles_seccion(s))) for s in requeridas.values()]
        validos = []
        for salon in salones_base:
            tipo = self.salon_tipo[salon]
            if tipo in por_tipo and por_tipo[tipo] != {salon}:
                continue
            for plan in planes:
                if tipo not in plan or not tipos_usados.issubset(plan):
                    continue
                # Reservar capacidad para todas las clases que necesariamente
                # usarán este tipo dentro del plan, no solo para la actual.
                obligadas_tipo = [opciones for s, opciones in dominios
                    if {self.salon_tipo[sl] for sl in opciones}.intersection(plan) == {tipo}]
                if all(salon in opciones for opciones in obligadas_tipo):
                    validos.append(salon)
                    break
        return validos

    def _evaluar_salon_por_profesor(self, sol):
        grupos = {}
        for a in sol:
            if a and a['profesor'] in self.profesores and a['salon'] in self.salon_tipo:
                grupos.setdefault(a['profesor'], []).append(a)
        conflictos, mensajes = 0, []
        for prof, asignaciones in grupos.items():
            por_tipo = {}
            for a in asignaciones:
                por_tipo.setdefault(self.salon_tipo[a['salon']], set()).add(a['salon'])
            for tipo, salones in por_tipo.items():
                if len(salones) > 1:
                    conflictos += len(salones) - 1
                    mensajes.append(f"Profesor {prof}: usa varios salones del tipo {tipo:g} "
                        f"({', '.join(sorted(salones))}); debe conservar uno por tipo necesario.")
            planes = self._planes_tipos_salones(a['seccion'] for a in asignaciones)
            if planes:
                necesarios = len(planes[0])
                if len(por_tipo) > necesarios:
                    conflictos += len(por_tipo) - necesarios
                    mensajes.append(f"Profesor {prof}: usa {len(por_tipo)} tipos de salón, "
                        f"pero sus clases y cupos solo requieren {necesarios}. "
                        "Las materias compatibles deben compartir salón.")
        return conflictos, mensajes

    def validar_factibilidad_inicial(self):
        problemas = []
        obligadas = {p: [] for p in self.profesores}
        posibles = {p: [] for p in self.profesores}
        for s in self.secciones:
            candidatos = [p for p in s.cands if p in self.profesores]
            for p in candidatos:
                posibles[p].append(s)
            if len(candidatos) == 1 and 'GRADUADOS' not in s.cands:
                obligadas[candidatos[0]].append(s)

        for p, obj in self.profesores.items():
            for curso, dia in obj.cursos_intensivos.items():
                secciones_curso = [s for s in posibles[p]
                    if normalizar_codigo_curso(s.cod.rsplit('-', 1)[0]) == curso]
                if not any(self._horas_validas_para_profesor(s, p, patron)
                           for s in secciones_curso
                           for patron in self._patrones_validos_para_profesor(s, p)):
                    problemas.append(
                        f"{p}: {curso} intensivo el {dia} no cabe con PREF_HORAS, "
                        "HORA_ENTRADA, HORA_SALIDA y la grilla institucional."
                    )
            carga_fija = sum(self.get_sec_creditos(s, p) for s in obligadas[p])
            carga_posible = sum(self.get_sec_creditos(s, p) for s in posibles[p])
            if carga_fija > obj.carga_max + 0.5:
                problemas.append(f"{p}: carga obligatoria {carga_fija:g} > CARGA_MAX {obj.carga_max:g} (tolerancia original 0.5).")
            if carga_posible < obj.carga_min - 0.5:
                problemas.append(f"{p}: carga candidata total {carga_posible:g} < CARGA_MIN {obj.carga_min:g} (tolerancia original 0.5).")
            if self._caben_secciones_obligatorias(obligadas[p], p) is False:
                codigos = ', '.join(s.cod for s in obligadas[p])
                problemas.append(f"{p}: sus secciones obligatorias no caben sin cruces con su disponibilidad, patrones y grilla institucional: {codigos}.")

        for s in self.secciones:
            if getattr(s, 'profesor_pendiente_permitido', False):
                continue
            candidatos = [p for p in s.cands if p in self.profesores or p == 'GRADUADOS']
            if not candidatos:
                problemas.append(f"{s.cod}: no tiene profesores candidatos válidos.")
                continue
            if not any(self._salones_validos_para(s, p) for p in candidatos):
                problemas.append(f"{s.cod}: no tiene salón compatible con cupo {s.cupo} y tipos {s.tipos_permitidos} según compatible_tipo().")
            if not any(
                self._horas_validas_para_profesor(s, p, patron)
                for p in candidatos
                for patron in self._patrones_validos_para_profesor(s, p)
                if p not in self.profesores or not s.es_grande or self.profesores[p].acepta_grandes
            ):
                problemas.append(f"{s.cod}: ningún candidato cumple simultáneamente PREF_DIAS, PREF_HORAS, HORA_ENTRADA, HORA_SALIDA e intensivos/horario institucional.")
        problemas.extend(self._validar_capacidad_salones())
        return problemas

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
            if s.es_grande and prof in capacidad_restante and capacidad_restante[prof] < creditos:
                s.prof_preasignado = "TBA"
                carga_actual["TBA"] += self.get_sec_creditos(s, "TBA")
                continue
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
                if s.es_grande:
                    s.prof_preasignado = "TBA"
                    carga_actual["TBA"] += self.get_sec_creditos(s, "TBA")
                    continue
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

    def _costo_total(self, sol, solo_duros=False, evaluar_carga_min=True):
        conflicts = 10000 * len(self._errores_estructura_y_aforo(sol))
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
            
            if (prof == "TBA" and not getattr(s, "profesor_pendiente_permitido", False)) or salon == "TBA":
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
            
            conflicts += 10000 * len(self._incumplimientos_cursos_intensivos(s, prof, patron))
            if prof in self.profesores:
                conflicts += self._penalidad_preferencias_horarias(prof, patron, ini)


            for dia, contrib in patron['days'].items():
                fin = ini + int(contrib * 50)
                if dia in ["Ma", "Ju"] and max(ini, self.hora_universal[0]) < min(fin, self.hora_universal[1]):
                    conflicts += 10000
                if s.creditos == 3 and contrib >= 3 and ini < 930:
                    conflicts += 10000
                if fin > self.limite_operativo[1] or ini < self.limite_operativo[0]:
                    conflicts += 10000
                
                if prof not in ["GRADUADOS", "TBA"]:
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
                if evaluar_carga_min and carga < prof_obj.carga_min - 0.5:
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

        # Regla fuerte para TODAS las materias, incluidas listas como 1,3 o 1,6.
        conflicts += 10000 * self._evaluar_salon_por_profesor(sol)[0]

        if solo_duros:
            return conflicts
        
        return conflicts + 2 * self._contar_conflictos_suaves(sol)

    def _contar_conflictos_suaves(self, sol):
        """Cada salón adicional del mismo tipo tiene una penalidad de dos puntos."""
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
        return sum(max(0, len(salones) - 1) for salones in salones_por_prof_tipo.values())

    def _obtener_conflictos(self, sol):
        conflictos_list = self._errores_estructura_y_aforo(sol)
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
            
            if prof == "TBA" and not getattr(s, "profesor_pendiente_permitido", False):
                conflictos_list.append(f"Sección {s.cod}: profesor TBA")
            if salon == "TBA": conflictos_list.append(f"Sección {s.cod}: salón TBA")
            
            salon_info = next((sl for sl in self.salones if sl['CODIGO'] == salon), None)
            if salon_info and salon_info['CAPACIDAD'] < s.cupo:
                conflictos_list.append(f"Sección {s.cod}: salón {salon} capacidad insuficiente")
            if salon_info and not compatible_tipo(s.tipos_permitidos, salon_info['TIPO']):
                conflictos_list.append(f"Sección {s.cod}: tipo de salón incompatible (requiere {s.tipos_permitidos})")
            
            if prof in carga_prof:
                carga_prof[prof] += self.get_sec_creditos(s, prof)
                
            for motivo in self._incumplimientos_cursos_intensivos(s, prof, patron):
                conflictos_list.append(f"Sección {s.cod}, Prof {prof}: {motivo}.")
            if prof in self.profesores:
                prof_obj = self.profesores[prof]
                if prof_obj.acepta_grandes == 0 and s.es_grande:
                    conflictos_list.append(f"Sección {s.cod}: Prof {prof} no acepta grandes.")
                for motivo in self._incumplimientos_disponibilidad(prof, patron, ini):
                    conflictos_list.append(f"Sección {s.cod}, Prof {prof}: {motivo}.")
            
            
            for dia, contrib in patron['days'].items():
                fin = ini + int(contrib * 50)
                if dia in ["Ma", "Ju"] and max(ini, self.hora_universal[0]) < min(fin, self.hora_universal[1]):
                    conflictos_list.append(f"Sección {s.cod}: violación de hora universal el {dia}")
                if s.creditos == 3 and contrib >= 3 and ini < 930:
                    conflictos_list.append(f"Sección {s.cod}: intensivo antes de las 15:30 el {dia}")
                if ini < self.limite_operativo[0] or fin > self.limite_operativo[1]:
                    conflictos_list.append(f"Sección {s.cod}: clase fuera de la ventana operativa el {dia}")
                
                if prof not in ["GRADUADOS", "TBA"]:
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
        conflictos_list.extend(self._evaluar_salon_por_profesor(sol)[1])

        return conflictos_list

    def _construir_solucion_greedy(self):
        # Construir juntas las clases de cada docente. Una elección válida para
        # una sección puede dejar sin espacio a sus otras clases obligatorias.
        grupos = {}
        for i, s in enumerate(self.secciones):
            grupos.setdefault(s.prof_preasignado, []).append(i)
        dificultad = {}
        for prof, indices in grupos.items():
            opciones = [sum(len(self._horas_validas_para_profesor(self.secciones[i], prof, p))
                           for p in self._patrones_validos_para_profesor(self.secciones[i], prof))
                        for i in indices]
            # Menos alternativas por clase y más clases: colocar antes.
            dificultad[prof] = math.prod(opciones) ** (1 / len(indices)) / len(indices)

        mejor, mejor_costo = None, float('inf')
        for _ in range(8):
            sol = [None] * len(self.secciones)
            orden = list(grupos)
            random.shuffle(orden)
            orden.sort(key=lambda p: dificultad[p])
            for prof in orden:
                indices = grupos[prof]
                nodos_grupo = 0

                def buscar_grupo(pendientes):
                    nonlocal nodos_grupo
                    if not pendientes:
                        return True
                    nodos_grupo += 1
                    if nodos_grupo > 2000:
                        return False  # Presupuesto local; la reparación podrá continuar.
                    dominios = []
                    for i in pendientes:
                        s = self.secciones[i]
                        opciones = []
                        patrones = list(self._patrones_validos_para_profesor(s, prof))
                        random.shuffle(patrones)
                        for patron in patrones:
                            horas = self._horas_validas_para_profesor(s, prof, patron)
                            random.shuffle(horas)
                            salones = self._salones_validos_para(s, prof, sol, i)
                            random.shuffle(salones)
                            salones.sort(key=lambda sl: self.salon_capacidad[sl])
                            for ini in horas:
                                for salon in salones:
                                    a = {'seccion': s, 'profesor': prof, 'salon': salon,
                                         'patron': patron, 'ini': ini}
                                    if self._asignacion_local_valida(i, a, sol):
                                        opciones.append(a)
                        # Si otra clase se quedó sin opciones, deshacer la
                        # elección anterior antes de seguir con otro docente.
                        if not opciones:
                            return False
                        dominios.append((i, opciones))
                    i, opciones = min(dominios,
                        key=lambda par: (len(par[1]), -self.secciones[par[0]].creditos))
                    restantes = [j for j in pendientes if j != i]
                    for a in opciones:
                        sol[i] = a
                        if buscar_grupo(restantes):
                            return True
                        sol[i] = None
                        if nodos_grupo > 2000:
                            break
                    return False

                if not buscar_grupo(indices):
                    for i in indices:
                        sol[i] = None
                    for i in indices:
                        self._asignar_seccion(i, prof, sol, [bool(a) for a in sol])

            # Solo si se agotó la construcción se conservan asignaciones
            # temporales para el reparador. Nunca pasan la validación si chocan.
            for i, a in enumerate(sol):
                if a is None:
                    sol[i] = self._crear_asignacion_temporal(self.secciones[i], prof=self.secciones[i].prof_preasignado)
            costo = self._costo_total(sol, solo_duros=True)
            if costo < mejor_costo:
                mejor, mejor_costo = sol, costo
            if costo == 0:
                break
        return mejor or []

    def _crear_asignacion_temporal(self, seccion, prof="TBA", salon="TBA", patron=None, ini=None):
        if patron is None:
            patrones = self._patrones_validos_para_profesor(seccion, prof)
            if not patrones:
                patrones = PATRONES.get(seccion.creditos, PATRONES[3])
            patron = random.choice(patrones)
        opciones = [(p, h) for p in self._patrones_validos_para_profesor(seccion, prof)
                    for h in self._horas_validas_para_profesor(seccion, prof, p)]
        if opciones:
            compatibles = [(p, h) for p, h in opciones if p == patron and (ini is None or h == ini)]
            patron, ini = random.choice(compatibles or opciones)
        elif ini is None:
            ini = random.choice(self.bloques)  # Temporal inviable; la auditoría impide publicarlo.
        if salon == "TBA":
            salones_posibles = self._salones_validos_para(seccion, prof)
            salon = random.choice(salones_posibles) if salones_posibles else "TBA"
        return {'seccion': seccion, 'profesor': prof, 'salon': salon, 'patron': patron, 'ini': ini}

    def _asignar_seccion(self, idx, prof, sol, asignado):
        s = self.secciones[idx]
        patrones = list(self._patrones_validos_para_profesor(s, prof))
        random.shuffle(patrones)
        for patron in patrones:
            horas = self._horas_validas_para_profesor(s, prof, patron)
            random.shuffle(horas)
            salones = self._salones_validos_para(s, prof, sol, idx)
            random.shuffle(salones)
            # Evitar ocupar el único salón de 40 con una clase pequeña si
            # existe otro adecuado. No se altera ninguna compatibilidad.
            salones.sort(key=lambda sl: self.salon_capacidad[sl])
            for hora in horas:
                for salon in salones:
                    a = {'seccion': s, 'profesor': prof, 'salon': salon, 'patron': patron, 'ini': hora}
                    if self._asignacion_local_valida(idx, a, sol):
                        sol[idx] = a
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
                if all(a['patron'] in self._patrones_validos_para_profesor(a['seccion'], a['profesor'])
                       and not self._incumplimientos_disponibilidad(a['profesor'], a['patron'], a['ini'])
                       for a in (a1, a2)):
                    return nuevo, self._costo_total(nuevo)
                nuevo = deepcopy(sol)
        
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
            patrones = self._patrones_validos_para_profesor(s, prof)
            if not patrones:
                continue

            patron = random.choice(patrones)
            horas_posibles = set(self._horas_validas_para_profesor(s, prof, patron))
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
            

            salones_cand = self._salones_validos_para(s, prof, sol, idx)
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
                                if max(hora, asign2['ini']) < min(fin_actual, fin_exist):
                                    if salon in self.mega_salones and s.es_fusionable and asign2['seccion'].es_fusionable:
                                        if s.cupo + asign2['seccion'].cupo <= self.salon_capacidad.get(salon, 0):
                                            continue
                                    conflicto = True
                                    break
                    if conflicto:
                        break
            if not conflicto:
                costo = 0
                mejores_opciones.append((costo, prof, patron, hora, salon))

        if not mejores_opciones:
            return nuevo, self._costo_total(nuevo)
        mejores_opciones.sort(key=lambda x: x[0])
        mejor = mejores_opciones[0]
        nuevo[idx] = {'seccion': s, 'profesor': mejor[1], 'salon': mejor[4], 'patron': mejor[2], 'ini': mejor[3]}
        return nuevo, self._costo_total(nuevo)

    def _costo_compactacion(self, sol):
        penalty = 0
        prof_asignaciones = {}
        for asign in sol:
            prof = asign['profesor']
            if prof not in ["TBA", "GRADUADOS"] and prof in self.profesores:
                if prof not in prof_asignaciones:
                    prof_asignaciones[prof] = []
                prof_asignaciones[prof].append(asign)
        
        for prof, asigns in prof_asignaciones.items():
            dias_presenciales = set()
            salones_usados = set()
            carga_total = 0.0
            for asign in asigns:
                s = asign['seccion']
                patron = asign['patron']
                dias_presenciales.update(patron['days'].keys())
                salones_usados.add(asign['salon'])
                carga_total += self.get_sec_creditos(s, prof)
            
            if carga_total <= 9:
                dias_ideal = 2
            elif carga_total <= 15:
                dias_ideal = 3
            else:
                dias_ideal = 4
            exceso = len(dias_presenciales) - dias_ideal
            if exceso > 0:
                penalty += exceso * 500
            
            if len(salones_usados) > 1:
                penalty += (len(salones_usados) - 1) * 400
            
            for dia in dias_presenciales:
                clases = []
                for asign in asigns:
                    if dia in asign['patron']['days']:
                        ini = asign['ini']
                        fin = ini + int(asign['patron']['days'][dia] * 50)
                        clases.append((ini, fin))
                clases.sort()
                for i in range(len(clases)-1):
                    brecha = clases[i+1][0] - clases[i][1]
                    if brecha > 30:
                        penalty += brecha * 2
        return penalty

    def _mutar_compactacion(self, sol):
        idx = random.randrange(len(sol))
        actual = sol[idx]
        s, prof = actual['seccion'], actual['profesor']
        if prof not in self.profesores:
            return sol, self._costo_compactacion(sol)
        patrones = self._patrones_validos_para_profesor(s, prof)
        salones = self._salones_validos_para(s, prof, sol, idx)
        mejor, costo_mejor = sol, self._costo_compactacion(sol)
        for _ in range(20):
            if not patrones or not salones:
                break
            patron = random.choice(patrones)
            horas = self._horas_validas_para_profesor(s, prof, patron)
            if not horas:
                continue
            a = {'seccion': s, 'profesor': prof, 'salon': random.choice(salones),
                 'patron': patron, 'ini': random.choice(horas)}
            if self._asignacion_local_valida(idx, a, sol):
                vecino = sol[:idx] + [a] + sol[idx+1:]
                costo = self._costo_compactacion(vecino)
                if costo < costo_mejor:
                    mejor, costo_mejor = vecino, costo
        return mejor, costo_mejor

    def _compactar_solucion(self, sol, iteraciones=2000, progreso=None):
        if self._costo_total(sol, solo_duros=True) > 0:
            return sol
        
        actual = deepcopy(sol)
        mejor = deepcopy(sol)
        costo_actual = self._costo_compactacion(actual)
        mejor_costo = costo_actual
        temp = 500.0
        
        for it in range(iteraciones):
            vecino, costo_vecino = self._mutar_compactacion(actual)
            if costo_vecino <= costo_actual or random.random() < math.exp((costo_actual - costo_vecino) / temp):
                actual = vecino
                costo_actual = costo_vecino
                if costo_actual < mejor_costo:
                    mejor = deepcopy(actual)
                    mejor_costo = costo_actual
            temp *= 0.995
            if progreso is not None and ((it + 1) % 10 == 0 or it == iteraciones - 1):
                progreso(it + 1, iteraciones, mejor)
        return mejor

    # --------------------------------------------------------------------------
    # FASE DE REPARACIÓN: BÚSQUEDA ACOTADA, SIN GARANTÍA DE FACTIBILIDAD
    # --------------------------------------------------------------------------
    def _reparar_solucion(self, sol, max_intentos=15, progreso=None):
        """
        Intenta reparar una solución con conflictos duros mediante:
        - Destrucción de secciones conflictivas + aleatorias.
        - Reinserción voraz buscando solo huecos con 0 conflictos.
        - Búsqueda local tabú enfocada en conflictos duros.
        """
        mejor_sol = deepcopy(sol)
        mejor_costo = self._costo_total(mejor_sol, solo_duros=True)
        if mejor_costo == 0:
            return mejor_sol

        # Parámetros para búsqueda tabú de reparación
        tabu_tenure = 7
        tabu_list = {}
        max_iter_rep = 2000
        temp_rep = 200.0

        for intento in range(max_intentos):
            if progreso is not None:
                progreso(intento, max_intentos, mejor_sol, f"Intento {intento + 1}/{max_intentos}")
            # Identificar secciones conflictivas
            conflictivas = set()
            for idx, asign in enumerate(mejor_sol):
                temp_sin = mejor_sol[:idx] + mejor_sol[idx+1:]
                if self._costo_total(temp_sin, solo_duros=True) < mejor_costo:
                    conflictivas.add(idx)
            # Añadir un 20% adicional aleatorio para romper bloqueos
            no_conflictivas = [i for i in range(len(mejor_sol)) if i not in conflictivas]
            extra_destruir = random.sample(no_conflictivas, min(int(len(no_conflictivas)*0.2), len(no_conflictivas)))
            a_destruir = list(conflictivas) + extra_destruir

            # Marcar como TBA
            nuevo = deepcopy(mejor_sol)
            for idx in a_destruir:
                nuevo[idx] = self._crear_asignacion_temporal(nuevo[idx]['seccion'], prof="TBA", salon="TBA")

            # Reinsertar greedy
            for idx in a_destruir:
                exito = self._asignar_seccion_greedy_cero(idx, nuevo)
                if not exito:
                    # Intentar con búsqueda tabú simple
                    self._reparar_asignacion_tabu(idx, nuevo, tabu_tenure)
            
            nuevo_costo = self._costo_total(nuevo, solo_duros=True)
            if nuevo_costo < mejor_costo:
                mejor_sol = nuevo
                mejor_costo = nuevo_costo
            if progreso is not None:
                progreso(intento, max_intentos, mejor_sol, f"Intento {intento + 1}/{max_intentos}: reinserción terminada")
            if mejor_costo == 0:
                break

            # Si aún no es factible, aplicar recocido simulado enfocado en duros
            if mejor_costo > 0:
                actual = deepcopy(mejor_sol)
                costo_actual = mejor_costo
                for it in range(max_iter_rep):
                    vecino, costo_vecino = self._mutar_solucion_solo_duros(actual)
                    if costo_vecino <= costo_actual or random.random() < math.exp((costo_actual - costo_vecino) / temp_rep):
                        actual = vecino
                        costo_actual = costo_vecino
                        if costo_actual < mejor_costo:
                            mejor_sol = deepcopy(actual)
                            mejor_costo = costo_actual
                            if mejor_costo == 0:
                                break
                    temp_rep *= 0.995
                    if progreso is not None and ((it + 1) % 10 == 0 or it == max_iter_rep - 1):
                        progreso(intento, max_intentos, mejor_sol,
                                 f"Intento {intento + 1}/{max_intentos} · iteración {it + 1}/{max_iter_rep}")
                if mejor_costo == 0:
                    break
        return mejor_sol

    def _mutar_solucion_solo_duros(self, sol):
        """Mutación que solo evalúa conflictos duros, ignorando preferencias suaves."""
        nuevo = deepcopy(sol)
        idx = random.randint(0, len(nuevo)-1)
        s = nuevo[idx]['seccion']
        prof_actual = nuevo[idx]['profesor']

        cand_profs = [p for p in s.cands if p in self.profesores]
        if not cand_profs:
            cand_profs = ["GRADUADOS"] if "GRADUADOS" in s.cands else ["TBA"]
        
        mejores_opciones = []
        for _ in range(30):
            prof = random.choice(cand_profs)
            patrones = self._patrones_validos_para_profesor(s, prof)
            if not patrones:
                continue

            patron = random.choice(patrones)
            horas_posibles = set(self._horas_validas_para_profesor(s, prof, patron))
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
            

            salones_cand = self._salones_validos_para(s, prof, sol, idx)
            if not salones_cand:
                continue
            salon = random.choice(salones_cand)

            # Solo evaluar conflictos duros
            temp_asign = {'seccion': s, 'profesor': prof, 'salon': salon, 'patron': patron, 'ini': hora}
            temp_sol = sol[:idx] + [temp_asign] + sol[idx+1:]
            costo_duros = self._costo_total(temp_sol, solo_duros=True)
            mejores_opciones.append((costo_duros, prof, patron, hora, salon))
        
        if not mejores_opciones:
            return nuevo, self._costo_total(nuevo, solo_duros=True)
        mejores_opciones.sort(key=lambda x: x[0])
        mejor = mejores_opciones[0]
        nuevo[idx] = {'seccion': s, 'profesor': mejor[1], 'salon': mejor[4], 'patron': mejor[2], 'ini': mejor[3]}
        return nuevo, mejor[0]

    def _asignar_seccion_greedy_cero(self, idx, sol):
        s = sol[idx]['seccion']
        candidatos = [p for p in s.cands if p in self.profesores or p == 'GRADUADOS']
        random.shuffle(candidatos)
        # Preferir la preasignación que ya balanceó las cargas.
        candidatos.sort(key=lambda p: p != s.prof_preasignado)
        for prof in candidatos:
            if self._asignar_seccion(idx, prof, sol, [bool(a) for a in sol]):
                return True
        return False

    def _reparar_asignacion_tabu(self, idx, sol, tenure):
        """Búsqueda tabú simple para una sola sección conflictiva."""
        s = sol[idx]['seccion']
        mejor_asign = None
        mejor_costo = float('inf')
        tabu = set()
        for _ in range(50):
            cand_profs = [p for p in s.cands if p in self.profesores]
            if not cand_profs:
                cand_profs = ["GRADUADOS"] if "GRADUADOS" in s.cands else ["TBA"]
            prof = random.choice(cand_profs)
            patrones = self._patrones_validos_para_profesor(s, prof)
            if not patrones:
                continue
            patron = random.choice(patrones)
            horas = self._horas_validas_para_profesor(s, prof, patron)
            if not horas:
                continue
            hora = random.choice(horas)

            salones_cand = self._salones_validos_para(s, prof, sol, idx)
            if not salones_cand:
                continue
            salon = random.choice(salones_cand)
            key = (prof, patron['name'], hora, salon)
            if key in tabu:
                continue
            temp_asign = {'seccion': s, 'profesor': prof, 'salon': salon, 'patron': patron, 'ini': hora}
            temp_sol = sol[:idx] + [temp_asign] + sol[idx+1:]
            costo = self._costo_total(temp_sol, solo_duros=True)
            if costo < mejor_costo:
                mejor_costo = costo
                mejor_asign = temp_asign
                if costo == 0:
                    break
            tabu.add(key)
            if len(tabu) > tenure:
                tabu.pop()
        if mejor_asign:
            sol[idx] = mejor_asign

    def validar_solucion_final(self, sol):
        errores = self._obtener_conflictos(sol)
        esperadas = {s.cod for s in self.secciones}
        codigos = [a['seccion'].cod for a in sol]
        if len(codigos) != len(esperadas) or set(codigos) != esperadas:
            errores.append("La solución debe incluir exactamente una vez cada sección requerida.")
        for a in sol:
            s, prof, patron, ini = a['seccion'], a['profesor'], a['patron'], a['ini']
            if prof not in s.cands:
                errores.append(f"{s.cod}: {prof} no es un candidato autorizado.")
            if prof not in self.profesores and prof != 'GRADUADOS':
                errores.append(f"{s.cod}: profesor sin datos de disponibilidad: {prof}.")
            if a['salon'] not in self.salon_capacidad:
                errores.append(f"{s.cod}: salón desconocido o pendiente.")
            if patron not in self._patrones_validos_para_profesor(s, prof) or ini not in self._horas_validas_para_profesor(s, prof, patron):
                errores.append(f"{s.cod}: patrón/inicio fuera del dominio permitido.")
        # La capacidad debe cumplirse para TODAS las secciones simultáneas,
        # incluso cuando la política existente permite fusionar grupos.
        for salon in self.mega_salones:
            for dia in ['Lu', 'Ma', 'Mi', 'Ju', 'Vi']:
                eventos = []
                for a in sol:
                    if a['salon'] == salon and dia in a['patron']['days']:
                        fin = a['ini'] + int(a['patron']['days'][dia] * 50)
                        eventos.extend([(a['ini'], a['seccion'].cupo), (fin, -a['seccion'].cupo)])
                ocupacion = 0
                for _, delta in sorted(eventos):
                    ocupacion += delta
                    if ocupacion > self.salon_capacidad[salon]:
                        errores.append(f"Salón {salon} el {dia}: cupo simultáneo total {ocupacion} excede su capacidad.")
                        break
        if self._costo_total(sol, solo_duros=True) > 0 and not errores:
            errores.append("La evaluación institucional todavía detecta conflictos fuertes.")
        return list(dict.fromkeys(errores))

    def _emitir_progreso(self, fase, iteracion, iteraciones, estado, sol,
                         inicio_fase, inicio_total, progreso=None, detalle=""):
        ahora = time.perf_counter()
        costo_total = self._costo_total(sol)
        suaves = self._contar_conflictos_suaves(sol)
        datos = {
            'fase': fase, 'iteracion': iteracion, 'iteraciones': iteraciones,
            'estado': estado, 'detalle': detalle,
            'fraccion': 1.0 if estado == 'completada' else min(1.0, iteracion / max(1, iteraciones)),
            'conflictos_fuertes': int(self._costo_total(sol, solo_duros=True) // 10000),
            'conflictos_suaves': suaves, 'costo_suave': 2 * suaves,
            'costo_total': costo_total, 'fitness': 10000 / (10000 + costo_total),
            'tiempo_fase': ahora - inicio_fase, 'tiempo_total': ahora - inicio_total,
        }
        if fase == 'fase2':
            datos['costo_compactacion'] = self._costo_compactacion(sol)
        self.progreso_fases[fase] = datos
        if progreso is not None:
            progreso(datos)
        return datos

    def optimizar(self, iteraciones=3000, bar=None, status_text=None, progreso=None,
                  iteraciones_compactacion=2000):
        inicio_total = time.perf_counter()
        self.progreso_fases = {}

        def notificar(fase, it, limite, estado, sol, inicio_fase, detalle=""):
            datos = self._emitir_progreso(fase, it, limite, estado, sol,
                inicio_fase, inicio_total, progreso, detalle)
            # Compatibilidad con llamadas anteriores que pasan bar y status_text.
            if status_text is not None:
                status_text.markdown(formatear_progreso_optimizacion(datos))
            if bar is not None:
                bar.progress(datos['fraccion'])

        inicio_fase1 = time.perf_counter()
        notificar('fase1', 0, iteraciones, 'en curso', self.mejor_solucion, inicio_fase1,
                  "Evaluando el horario inicial.")
        problemas = self.validar_factibilidad_inicial()
        if problemas:
            notificar('fase1', 0, iteraciones, 'error', self.mejor_solucion, inicio_fase1,
                      "Los datos tienen restricciones incompatibles.")
            raise ValueError("Datos incompatibles:\n" + "\n".join(problemas))
        temp_inicial = 5000.0
        self.historial_costos = [self.mejor_costo]
        costo_actual = self._costo_total(self.solucion)
        iteraciones_hechas = 0
        for it in range(iteraciones):
            if self._costo_total(self.mejor_solucion, solo_duros=True) == 0:
                break
            vecino, costo_vecino = self._mutar_solucion(self.solucion)
            if costo_vecino <= self.mejor_costo:
                self.solucion = vecino
                costo_actual = costo_vecino
                self.mejor_costo = costo_vecino
                self.mejor_solucion = deepcopy(self.solucion)
            else:
                temp = temp_inicial / (it + 1)
                try:
                    prob = min(1.0, math.exp(min(0.0, (costo_actual - costo_vecino) / temp)))
                except:
                    prob = 0
                if random.random() < prob:
                    self.solucion = vecino
                    costo_actual = costo_vecino
            self.historial_costos.append(self.mejor_costo)
            iteraciones_hechas = it + 1
            if it % 10 == 0 or it == iteraciones - 1 or self._costo_total(self.mejor_solucion, solo_duros=True) == 0:
                notificar('fase1', iteraciones_hechas, iteraciones, 'en curso',
                          self.mejor_solucion, inicio_fase1)

        if self._costo_total(self.mejor_solucion, solo_duros=True) == 0:
            detalle = ("El horario inicial ya tiene cero conflictos fuertes; no se necesitaron iteraciones."
                       if iteraciones_hechas == 0 else "Se alcanzaron cero conflictos fuertes.")
        else:
            detalle = "Se alcanzó el límite de iteraciones; continúa la reparación."
        notificar('fase1', iteraciones_hechas, iteraciones, 'completada',
                  self.mejor_solucion, inicio_fase1, detalle)
        
        # --- FASE DE REPARACIÓN AGRESIVA REFORZADA ---
        if self._costo_total(self.mejor_solucion, solo_duros=True) > 0:
            inicio_reparacion = time.perf_counter()
            notificar('reparacion', 0, 20, 'en curso', self.mejor_solucion, inicio_reparacion)
            def reportar_reparacion(it, limite, sol, detalle):
                notificar('reparacion', it, limite, 'en curso', sol, inicio_reparacion, detalle)
            self.mejor_solucion = self._reparar_solucion(
                self.mejor_solucion, max_intentos=20, progreso=reportar_reparacion)
            self.mejor_costo = self._costo_total(self.mejor_solucion)
            self.historial_costos.append(self.mejor_costo)
            reparada = self._costo_total(self.mejor_solucion, solo_duros=True) == 0
            intento = self.progreso_fases['reparacion']['iteracion'] + 1
            notificar('reparacion', intento, 20, 'completada' if reparada else 'error',
                      self.mejor_solucion, inicio_reparacion,
                      "Cero conflictos fuertes." if reparada else "Persisten conflictos fuertes; la fase 2 no se ejecutará.")
        
        # Fase de compactación
        if self._costo_total(self.mejor_solucion, solo_duros=True) == 0:
            inicio_fase2 = time.perf_counter()
            notificar('fase2', 0, iteraciones_compactacion, 'en curso',
                      self.mejor_solucion, inicio_fase2)
            def reportar_compactacion(it, limite, sol):
                notificar('fase2', it, limite, 'en curso', sol, inicio_fase2)
            self.mejor_solucion = self._compactar_solucion(self.mejor_solucion,
                iteraciones=iteraciones_compactacion, progreso=reportar_compactacion)
            self.mejor_costo = self._costo_total(self.mejor_solucion)
            notificar('fase2', iteraciones_compactacion, iteraciones_compactacion, 'validando',
                      self.mejor_solucion, inicio_fase2, "Comprobando todas las restricciones antes de publicar.")
        
        errores = self.validar_solucion_final(self.mejor_solucion)
        if errores:
            if 'fase2' in self.progreso_fases:
                notificar('fase2', iteraciones_compactacion, iteraciones_compactacion, 'error',
                          self.mejor_solucion, inicio_fase2, "La validación final detectó errores. Exportación bloqueada.")
            raise ValueError(
                "La búsqueda no encontró un horario válido. No se publica ni exporta. "
                "Esto no demuestra que el problema global sea imposible. Conflictos:\n"
                + "\n".join(errores[:50])
            )
        notificar('fase2', iteraciones_compactacion, iteraciones_compactacion, 'completada',
                  self.mejor_solucion, inicio_fase2, "Compactación y validación final terminadas.")
        return self.mejor_solucion, 0, self.historial_costos

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
            for minuto in range(ini, ini + duracion, 30):
                if minuto in horas_del_dia:
                    hora_idx = horas_del_dia.index(minuto)
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
        slot_starts = list(scheduler.bloques)
        if not slot_starts:
            slot_starts = list(range(scheduler.limite_operativo[0], scheduler.limite_operativo[1], 60))
        primer_slot = min(slot_starts)
        ultimo_slot = max(slot_starts)
        hora_inicio = primer_slot / 60
        hora_fin = (ultimo_slot + 60) / 60
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
            y1 = (inicio_mins + 50) / 60
            fig.add_shape(type="rect", x0=0, x1=1, y0=y0, y1=y1,
                          fillcolor=color_header_2, line=dict(color=color_linea, width=2))
            fig.add_annotation(x=0.5, y=(y0 + y1) / 2, text=f"{mins_to_str(inicio_mins).replace(' AM', '').replace(' PM', '')} - {mins_to_str(inicio_mins + 50).replace(' AM', '').replace(' PM', '')}",
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
            height=760,
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
        df_cursos = pd.DataFrame({
            'CODIGO': ['MATE6026', 'MATE3171', 'MATE3172', 'MATE4999'],
            'CREDITOS': [3, 3, 3, 3],
            'DEMANDA': [30, 60, 30, 60],
            'CUPO': [30, 30, 30, 30],
            'CANDIDATOS': ['PEREZ (1)', 'PEREZ (1), GONZALEZ (1)',
                           'GONZALEZ (1)', 'PEREZ (1), GONZALEZ (1)'],
            'TIPO_SALON': ['1', '1', '1,3', '1']
        })
        df_cursos.to_excel(writer, sheet_name='Cursos', index=False)
        
        df_profes = pd.DataFrame({
            'NOMBRE': ['PEREZ', 'GONZALEZ'],
            'CARGA_MIN': [9, 6],
            'CARGA_MAX': [15, 12],
            'PREF_DIAS': ['LMWJV', 'LMWJV'],
            'PREF_HORAS': ['ANY', 'PM'],
            'HORA_ENTRADA': ['08:00', '13:00'],
            'HORA_SALIDA': ['18:30', '18:30'],
            'PREF1': ['MATE6026', 'MATE3172'],
            'PREF2': ['', ''],
            'PREF3': ['', ''],
            'COMPENSACION': ['NO', 'SI'],
            'ACEPTA_GRANDES': [0, 1],
            'CURSOS_INTENSIVOS': ['1,W,MATE6026', 0]
        })
        df_profes.to_excel(writer, sheet_name='Profesores', index=False)
        
        df_salones = pd.DataFrame({
            'CODIGO': ['S-101', 'S-102', 'FA'],
            'CAPACIDAD': [30, 40, 150],
            'TIPO': [1, 2, 3]
        })
        df_salones.to_excel(writer, sheet_name='Salones', index=False)
        
        df_grad = pd.DataFrame({
            'NOMBRE': ['graduado1', 'graduado2'],
            'RECIBE': ['MATE3171', 'MATE3172']
        })
        df_grad.to_excel(writer, sheet_name='Graduados', index=False)
    
    output.seek(0)
    return output.getvalue()

# ==============================================================================
# 8. UI PRINCIPAL
# ==============================================================================
TITULOS_PROGRESO = {
    'fase1': '🔄 Fase 1: Factibilidad',
    'reparacion': '🔧 Reparación de conflictos fuertes',
    'fase2': '✨ Fase 2: Compactación de horarios',
}


def formatear_progreso_optimizacion(datos):
    titulo = TITULOS_PROGRESO[datos['fase']]
    texto = (
        f"**{titulo} · {datos['estado'].capitalize()}**  \n"
        f"**Iteración:** {datos['iteracion']}/{datos['iteraciones']} | "
        f"**Conflictos fuertes:** {datos['conflictos_fuertes']} | "
        f"**Conflictos suaves:** {datos['conflictos_suaves']}  \n"
        f"**Costo total:** {datos['costo_total']:.2f} | "
        f"**Penalidad suave:** {datos['costo_suave']:.2f} | "
        f"**Fitness:** {datos['fitness']:.5f}  \n"
        f"**Tiempo de fase:** {datos['tiempo_fase']:.1f} s | "
        f"**Tiempo total:** {datos['tiempo_total']:.1f} s"
    )
    if 'costo_compactacion' in datos:
        texto += f" | **Costo de compactación:** {datos['costo_compactacion']:.2f}"
    if datos['detalle']:
        texto += f"  \n{datos['detalle']}"
    return texto


def crear_paneles_progreso(resumenes=None, inicio_ejecucion=None):
    """Cada fase conserva su panel al empezar la siguiente y tras un rerun."""
    espacios = {fase: st.empty() for fase in TITULOS_PROGRESO}
    for fase in ('fase1', 'fase2'):
        with espacios[fase].container():
            st.markdown(f"**{TITULOS_PROGRESO[fase]} · Pendiente**")
            st.progress(0.0)

    def actualizar(datos):
        datos = dict(datos)
        if inicio_ejecucion is not None:
            datos['tiempo_total'] = time.perf_counter() - inicio_ejecucion
        st.session_state.setdefault('progreso_fases', {})[datos['fase']] = datos
        with espacios[datos['fase']].container():
            st.markdown(formatear_progreso_optimizacion(datos))
            st.progress(datos['fraccion'])

    for datos in (resumenes or {}).values():
        actualizar(datos)
    return actualizar


def main():
    progreso_dibujado = False
    with st.sidebar:
        st.markdown("### ∑ Configuración")
        zona = st.selectbox("Zona Campus", ["CENTRAL", "PERIFERICA"])
        iteraciones = st.slider("Iteraciones Fase 1 (Factibilidad)", 500, 5000, 3000)
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
    with c3: st.markdown(f"""<div class="status-badge">RESTRICCIONES FUERTES ACTIVAS</div>""", unsafe_allow_html=True)

    if not file:
        st.markdown("""
            <div class='glass-card' style='text-align: center;'>
                <h3 style='margin-top:0; color: #D4AF37;'>📥 Sincronización de Datos</h3>
                <p>Asegúrese de que el archivo Excel contiene las hojas: <b>Cursos</b>, <b>Profesores</b>, <b>Salones</b>.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        if st.button("🚀 INICIAR OPTIMIZACIÓN ABSOLUTA"):
            for clave in ('master', 'scheduler', 'mejor_sol', 'conflicts', 'historial',
                          'elapsed_time', 'cargas_finales', 'detailed_conflicts', 'progreso_fases'):
                st.session_state.pop(clave, None)
            start_time = time.perf_counter()
            preparacion = st.empty()
            preparacion.info("Preparación: leyendo el Excel y construyendo el horario inicial...")
            actualizar_progreso = crear_paneles_progreso(inicio_ejecucion=start_time)
            progreso_dibujado = True
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

                    preparacion.info("Preparación: balanceando cargas y comprobando disponibilidad y salones...")
                    scheduler = TabuScheduler(df_cursos, df_profes, df_salones, zona, df_grad)
                    problemas_factibilidad = scheduler.problemas_factibilidad
                    if problemas_factibilidad:
                        preparacion.error("Preparación detenida: revisa las restricciones indicadas.")
                        st.error("El archivo tiene restricciones imposibles antes de optimizar.")
                        for problema in problemas_factibilidad[:50]:
                            st.write(f"- {problema}")
                        if len(problemas_factibilidad) > 50:
                            st.write(f"... y {len(problemas_factibilidad) - 50} problemas adicionales.")
                        return
                    
                    preparacion.success(f"Preparación completada en {time.perf_counter() - start_time:.1f} s.")
                    mejor_sol, conflictos, historial = scheduler.optimizar(
                        iteraciones, progreso=actualizar_progreso)
                    
                    st.session_state.elapsed_time = time.perf_counter() - start_time
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
                preparacion.error("El proceso se detuvo. Revisa el detalle del error.")
                st.error(f"Error durante la optimización: {e}")
                return

    if not progreso_dibujado and st.session_state.get('progreso_fases'):
        crear_paneles_progreso(st.session_state.progreso_fases)

    if 'master' in st.session_state:
        errores_finales = st.session_state.scheduler.validar_solucion_final(st.session_state.mejor_sol)
        if errores_finales:
            st.error("El horario no supera la validación obligatoria. Exportación bloqueada.")
            for error in errores_finales[:50]:
                st.write(f"- {error}")
            return
        st.success(f"✅ Optimización completada en {st.session_state.elapsed_time:.2f} segundos.")
        pendientes = sum(a['profesor'] == 'POR ASIGNAR' for a in st.session_state.mejor_sol)
        if pendientes:
            st.warning(f"Hay {pendientes} secciones con el docente provisional POR ASIGNAR. "
                       "El horario no tiene conflictos con este identificador, pero falta asignar los docentes reales.")
        if (st.session_state.scheduler.graduados_reciben
                and not any(st.session_state.scheduler.graduados_reciben.values())):
            st.info("Graduados: todos los campos RECIBE están vacíos. "
                    "No hay cursos recibidos cargados para comprobar el doble rol.")
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        t1, t2, t3, t4 = st.tabs(["💎 PANEL DE CONTROL", "🔍 VISTAS DETALLADAS", "🚨 AUDITORÍA DE CALIDAD", "📊 ANALÍTICAS AVANZADAS"])
        
        with t1:
            edited = st.data_editor(st.session_state.master, use_container_width=True, height=500)
            if edited.equals(st.session_state.master):
                st.download_button("💾 EXPORTAR EXCEL PLATINUM", exportar_todo(edited), "Horario_Final_UPRM.xlsx", use_container_width=True)
            else:
                st.error("La tabla fue modificada manualmente y ya no coincide con el horario validado. Restablece los valores o genera un nuevo horario para exportar.")
            
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
                st.success("✅ Cero conflictos horarios según los datos y restricciones cargados.")
                
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
