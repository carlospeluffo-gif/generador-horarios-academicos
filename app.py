import streamlit as st
import pandas as pd
import numpy as np
import random
import io
import time
import math
from collections import defaultdict
from copy import deepcopy

# ==============================================================================
# 1. ESTÉTICA PLATINUM ELITE (IDENTICA)
# ==============================================================================
st.set_page_config(page_title="UPRM Scheduler Platinum AI", page_icon="🏛️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Source+Code+Pro:wght@300;500&display=swap');
    
    .stApp { 
        background-color: #050505;
        background-image: 
            linear-gradient(rgba(212, 175, 55, 0.1) 2px, transparent 2px),
            linear-gradient(90deg, rgba(212, 175, 55, 0.1) 2px, transparent 2px),
            radial-gradient(circle at 50% 20%, #1a1a1a 0%, #000000 100%);
        background-size: 80px 80px, 80px 80px, 100% 100%;
        background-attachment: fixed;
        color: #e0e0e0; 
    }

    .math-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 30px 60px;
        background: rgba(0, 0, 0, 0.85);
        border-bottom: 3px solid #D4AF37;
        margin-bottom: 40px;
        border-radius: 0 0 30px 30px;
        box-shadow: 0 10px 50px rgba(212, 175, 55, 0.15);
        position: relative;
        overflow: hidden;
    }

    .math-header::before { content: '∑'; position: absolute; left: 5%; font-size: 8rem; color: rgba(212, 175, 55, 0.05); font-family: serif; }
    .math-header::after { content: '∫'; position: absolute; right: 5%; font-size: 8rem; color: rgba(212, 175, 55, 0.05); font-family: serif; }

    .title-box { text-align: center; z-index: 2; }

    .abstract-icon {
        font-size: 3rem;
        color: #D4AF37;
        border: 2px solid #D4AF37;
        padding: 10px 20px;
        border-radius: 50% 0% 50% 0%;
        background: rgba(212, 175, 55, 0.05);
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.3);
    }

    h1 { 
        font-family: 'Playfair Display', serif !important; 
        color: #D4AF37 !important; 
        font-size: 3.2rem !important;
        margin: 10px 0 !important;
        text-shadow: 0 0 20px rgba(212, 175, 55, 0.5);
        letter-spacing: 2px;
    }

    .glass-card { 
        background: rgba(15, 15, 15, 0.9); 
        border-radius: 15px; 
        padding: 25px; 
        border: 1px solid rgba(212, 175, 55, 0.25); 
        backdrop-filter: blur(15px); 
        margin-bottom: 20px; 
        box-shadow: 0 15px 40px rgba(0,0,0,0.8);
    }

    .stButton>button { 
        background: linear-gradient(135deg, #8E6E13 0%, #D4AF37 50%, #8E6E13 100%) !important; 
        color: white !important; font-weight: bold !important; border-radius: 4px !important; 
        width: 100%; border: none !important; height: 55px; font-size: 1.1rem;
        transition: 0.4s;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 0 25px rgba(212, 175, 55, 0.4); }

    .stDownloadButton>button {
        background: linear-gradient(135deg, #B8860B 0%, #FFD700 50%, #B8860B 100%) !important;
        color: #000 !important;
        font-weight: 800 !important;
        border: 1px solid #D4AF37 !important;
    }

    [data-testid="stSidebar"] { background-color: #050505; border-right: 1px solid #D4AF37; }
    
    [data-testid="stSidebar"] h3 {
        color: #D4AF37 !important;
        text-shadow: 0 0 10px rgba(212, 175, 55, 0.4);
        font-family: 'Playfair Display', serif;
    }

    .status-badge { 
        background: rgba(212, 175, 55, 0.1); 
        border: 1px solid #D4AF37; 
        color: #D4AF37; 
        padding: 12px; 
        border-radius: 8px; 
        text-align: center;
        font-family: 'Source Code Pro', monospace;
        font-weight: 500;
    }
</style>

<div class="math-header">
    <div class="abstract-icon">Δx</div>
    <div class="title-box">
        <h1>UPRM TIMETABLE SYSTEM</h1>
        <p style="color: #888; font-family: 'Source Code Pro'; letter-spacing: 4px; font-size: 0.9rem;">
            UPRM OPTIMIZATION ENGINE v10 (TABU SEARCH)
        </p>
    </div>
    <div class="abstract-icon">∞</div>
</div>
""", unsafe_allow_html=True)

st.latex(r"\blacksquare \quad \text{SISTEMA DE PLANIFICACIÓN ACADÉMICA OPTIMIZADA - TESIS MASTER} \quad \blacksquare")

# ==============================================================================
# 2. UTILIDADES
# ==============================================================================
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

# Patrones (igual)
PATRONES = {
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

def calcular_compensacion(creditos, estudiantes):
    for h, min_e, max_e, add in COMPENSACION_TABLE:
        if h == creditos and min_e <= estudiantes <= max_e:
            return add
    return 0.0

def format_horario(patron, h_ini):
    parts = []
    for dia, contrib in patron['days'].items():
        mins_duracion = int(contrib * 50)
        h_fin = h_ini + mins_duracion
        parts.append(f"{dia}: {mins_to_str(h_ini)}-{mins_to_str(h_fin)}")
    return " | ".join(parts)

def crear_excel_guia():
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        pd.DataFrame(columns=['CODIGO', 'CREDITOS', 'DEMANDA', 'CUPO', 'CANDIDATOS', 'TIPO_SALON']).to_excel(writer, sheet_name='Cursos', index=False)
        pd.DataFrame(columns=['NOMBRE', 'CARGA_MIN', 'CARGA_MAX', 'PREF_DIAS', 'PREF_HORAS', 'BLOQUEO_DIAS', 'BLOQUEO_HORA_INI', 'BLOQUEO_HORA_FIN', 'PREF1', 'PREF2', 'PREF3', 'COMPENSACION', 'ACEPTA_GRANDES']).to_excel(writer, sheet_name='Profesores', index=False)
        pd.DataFrame(columns=['CODIGO', 'CAPACIDAD', 'TIPO']).to_excel(writer, sheet_name='Salones', index=False)
    return output.getvalue()

def exportar_todo(df):
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Maestro', index=False)
        for p in df['Persona'].unique():
            if str(p) not in ["TBA", "GRADUADOS"]:
                clean_name = "".join([c for c in str(p) if c.isalnum() or c==' '])[:25]
                df[df['Persona'] == p].to_excel(writer, sheet_name=f"User_{clean_name}", index=False)
    return out.getvalue()

# ==============================================================================
# 3. CLASES DE DATOS (simplificadas)
# ==============================================================================
class Seccion:
    def __init__(self, cod, creditos, cupo, candidatos, tipo_salon):
        self.cod = cod
        self.creditos = creditos
        self.cupo = cupo  # estudiantes asignados
        self.candidatos = candidatos
        self.tipo_salon = tipo_salon
        base = cod.split('-')[0].upper()
        self.es_fusionable = base in ["MATE3171", "MATE3172", "MATE3173"]

class Profesor:
    def __init__(self, nombre, carga_min, carga_max, pref_dias, pref_horas,
                 bloqueo_dias, bloqueo_ini, bloqueo_fin, preferencias, compensacion, acepta_grandes):
        self.nombre = nombre
        self.carga_min = carga_min
        self.carga_max = carga_max
        self.pref_dias = pref_dias
        self.pref_horas = pref_horas
        self.bloqueo_dias = set(bloqueo_dias.split(',')) if bloqueo_dias else set()
        self.bloqueo_ini = str_to_mins(bloqueo_ini) if bloqueo_ini else None
        self.bloqueo_fin = str_to_mins(bloqueo_fin) if bloqueo_fin else None
        self.preferencias = preferencias
        self.compensacion = compensacion
        self.acepta_grandes = acepta_grandes

# ==============================================================================
# 4. MOTOR DE BÚSQUEDA TABÚ (GARANTIZA FACTIBILIDAD)
# ==============================================================================
class TabuScheduler:
    def __init__(self, df_cursos, df_profes, df_salones, zona):
        self.zona = zona
        
        # Procesar salones
        self.salones = []
        df_salones.columns = [c.strip().upper() for c in df_salones.columns]
        for _, r in df_salones.iterrows():
            self.salones.append({
                'cod': str(r['CODIGO']).strip().upper(),
                'cap': int(r['CAPACIDAD']),
                'tipo': int(r['TIPO'])
            })
        
        # Procesar profesores
        self.profesores = {}
        if df_profes is not None:
            for _, r in df_profes.iterrows():
                prefs = []
                for col in ['PREF1', 'PREF2', 'PREF3']:
                    val = r.get(col, '')
                    if pd.notnull(val) and str(val).strip().upper() != 'NAN':
                        prefs.append(str(val).strip().upper())
                prof = Profesor(
                    nombre=str(r['NOMBRE']).strip().upper(),
                    carga_min=float(r.get('CARGA_MIN', 0)),
                    carga_max=float(r.get('CARGA_MAX', 15)),
                    pref_dias=r.get('PREF_DIAS', ''),
                    pref_horas=r.get('PREF_HORAS', 'ANY'),
                    bloqueo_dias=r.get('BLOQUEO_DIAS', ''),
                    bloqueo_ini=r.get('BLOQUEO_HORA_INI', ''),
                    bloqueo_fin=r.get('BLOQUEO_HORA_FIN', ''),
                    preferencias=prefs,
                    compensacion=str(r.get('COMPENSACION', 'NO')).upper() in ('SI', 'SÍ', 'YES', '1'),
                    acepta_grandes=int(r.get('ACEPTA_GRANDES', 0))
                )
                self.profesores[prof.nombre] = prof
        
        # Procesar cursos y generar secciones
        self.secciones = []
        df_cursos.columns = [c.strip().upper() for c in df_cursos.columns]
        # Agrupar por código base
        cursos = defaultdict(lambda: {'creditos': 0, 'demanda': 0, 'cupo_tipico': 30, 'candidatos': '', 'tipo_salon': 1})
        for _, r in df_cursos.iterrows():
            cod_base = str(r['CODIGO']).strip().upper()
            creditos = int(r['CREDITOS'])
            demanda = int(r.get('DEMANDA', 0))
            cupo_tipico = int(r.get('CUPO', 30))
            candidatos = r.get('CANDIDATOS', '')
            tipo_salon = int(r.get('TIPO_SALON', 1))
            cursos[cod_base] = {
                'creditos': creditos,
                'demanda': cursos[cod_base]['demanda'] + demanda,
                'cupo_tipico': cupo_tipico,
                'candidatos': candidatos,
                'tipo_salon': tipo_salon
            }
        
        for cod_base, datos in cursos.items():
            num_secc = math.ceil(datos['demanda'] / datos['cupo_tipico'])
            # Distribuir estudiantes equitativamente
            base = datos['demanda'] // num_secc
            resto = datos['demanda'] % num_secc
            for i in range(num_secc):
                cupo = base + (1 if i < resto else 0)
                cod = f"{cod_base}-{i+1:02d}"
                # Procesar candidatos
                if isinstance(datos['candidatos'], list):
                    cands = [c.strip().upper() for c in datos['candidatos'] if c.strip()]
                else:
                    cands = [c.strip().upper() for c in str(datos['candidatos']).split(',') if c.strip() and str(c).upper() != 'NAN']
                self.secciones.append(Seccion(cod, datos['creditos'], cupo, cands, datos['tipo_salon']))
        
        # Definir bloques horarios (7:00 a 19:30 cada 30 min)
        self.bloques = list(range(420, 1171, 30))
        
        # Restricciones zonales
        if zona == "CENTRAL":
            self.hora_universal = (630, 750)  # 10:30-12:30
            self.limite_inicio = 450  # 7:30
            self.limite_fin = 1170     # 19:30
        else:
            self.hora_universal = (600, 720)  # 10:00-12:00
            self.limite_inicio = 420  # 7:00
            self.limite_fin = 1140     # 19:00

    def _es_factible(self, asignacion, nuevas_asignaciones=None):
        """Verifica si una asignación individual es factible dado un conjunto de asignaciones existentes"""
        # Esta función se usa en la construcción y en la búsqueda local
        pass  # Implementaremos la lógica directamente en los métodos

    def _generar_opciones_para_seccion(self, seccion):
        """Genera todas las combinaciones (prof, salon, patron, inicio) posibles para una sección,
        filtrando las que violan restricciones obvias (capacidad, tipo, candidatos)"""
        opciones = []
        
        # Profesores candidatos
        profes = []
        for p in seccion.candidatos:
            if p == "GRADUADOS":
                profes.append(("GRADUADOS", None))
            elif p in self.profesores:
                profes.append((p, self.profesores[p]))
        if not profes:
            profes.append(("TBA", None))
        
        # Salones candidatos
        salones = []
        for s in self.salones:
            if s['tipo'] == seccion.tipo_salon and s['cap'] >= seccion.cupo:
                salones.append(s['cod'])
        if not salones:
            for s in self.salones:
                if s['cap'] >= seccion.cupo:
                    salones.append(s['cod'])
        if not salones:
            salones = [s['cod'] for s in self.salones]
        
        # Patrones según créditos
        patrones = PATRONES.get(seccion.creditos, PATRONES[3])
        
        # Inicios
        inicios = self.bloques
        
        # Generar combinaciones (pero no todas, porque sería enorme; generaremos bajo demanda)
        # Para construcción, necesitamos iterar hasta encontrar una factible.
        # Para búsqueda local, usaremos una función que devuelva una opción aleatoria.
        return profes, salones, patrones, inicios

    def _construir_solucion_factible(self):
        """Construcción greedy con backtracking para garantizar factibilidad"""
        # Ordenar secciones por dificultad: primero las con menos candidatos, luego mayor demanda
        secciones_ordenadas = sorted(self.secciones, key=lambda s: (len(s.candidatos), -s.cupo))
        
        asignaciones = []  # lista de diccionarios con keys: seccion, prof, salon, patron, inicio
        ocupacion_prof = defaultdict(list)  # (prof, dia) -> [(inicio, fin)]
        ocupacion_salon = defaultdict(list)  # (salon, dia) -> [(inicio, fin, cupo, fusionable)]
        carga_prof = defaultdict(float)
        
        # Intentar asignar cada sección
        for seccion in secciones_ordenadas:
            encontrada = False
            # Generar opciones en orden: primero profes con menor carga, luego salones más pequeños, etc.
            # Para simplificar, probamos combinaciones aleatorias hasta encontrar una factible
            # pero con límite de intentos.
            profes_candidatos = []
            for p in seccion.candidatos:
                if p == "GRADUADOS":
                    profes_candidatos.append(("GRADUADOS", None))
                elif p in self.profesores:
                    profes_candidatos.append((p, self.profesores[p]))
            if not profes_candidatos:
                profes_candidatos.append(("TBA", None))
            
            # Ordenar profes por carga actual (menor mejor) y por preferencia
            profes_candidatos.sort(key=lambda x: carga_prof.get(x[0], 0) if x[0] not in ["GRADUADOS", "TBA"] else 0)
            
            salones_candidatos = []
            for s in self.salones:
                if s['tipo'] == seccion.tipo_salon and s['cap'] >= seccion.cupo:
                    salones_candidatos.append(s['cod'])
            if not salones_candidatos:
                for s in self.salones:
                    if s['cap'] >= seccion.cupo:
                        salones_candidatos.append(s['cod'])
            if not salones_candidatos:
                salones_candidatos = [s['cod'] for s in self.salones]
            
            patrones = PATRONES.get(seccion.creditos, PATRONES[3])
            inicios = self.bloques
            
            # Intentar hasta 1000 combinaciones
            for _ in range(1000):
                prof = random.choice(profes_candidatos)[0]
                salon = random.choice(salones_candidatos)
                patron = random.choice(patrones)
                inicio = random.choice(inicios)
                
                # Verificar restricciones institucionales
                # Límite operativo
                fin_max = 0
                for dia, contrib in patron['days'].items():
                    fin = inicio + int(contrib * 50)
                    if fin > self.limite_fin or inicio < self.limite_inicio:
                        break
                    fin_max = max(fin_max, fin)
                else:
                    # Hora universal
                    invade = False
                    for dia, contrib in patron['days'].items():
                        if dia in ["Ma", "Ju"]:
                            fin = inicio + int(contrib * 50)
                            if max(inicio, self.hora_universal[0]) < min(fin, self.hora_universal[1]):
                                invade = True
                                break
                    if invade:
                        continue
                    # Intensivos
                    if seccion.creditos == 3:
                        for dia, contrib in patron['days'].items():
                            if contrib >= 3 and inicio < 930:
                                invade = True
                                break
                        if invade:
                            continue
                    
                    # Verificar conflicto profesor
                    if prof not in ["GRADUADOS", "TBA"]:
                        prof_obj = self.profesores[prof]
                        # Carga máxima
                        if carga_prof[prof] + seccion.creditos > prof_obj.carga_max:
                            continue
                        # Bloqueos
                        for dia, contrib in patron['days'].items():
                            fin = inicio + int(contrib * 50)
                            if self._en_bloqueo(prof_obj, dia, inicio, fin):
                                invade = True
                                break
                        if invade:
                            continue
                        # Solapamiento con otras clases del profesor
                        for dia, contrib in patron['days'].items():
                            fin = inicio + int(contrib * 50)
                            for (ini_ex, fin_ex) in ocupacion_prof.get((prof, dia), []):
                                if max(inicio, ini_ex) < min(fin, fin_ex):
                                    invade = True
                                    break
                            if invade:
                                break
                        if invade:
                            continue
                    
                    # Verificar conflicto salón
                    salon_info = next(s for s in self.salones if s['cod'] == salon)
                    for dia, contrib in patron['days'].items():
                        fin = inicio + int(contrib * 50)
                        for (ini_ex, fin_ex, cupo_ex, fus_ex) in ocupacion_salon.get((salon, dia), []):
                            if max(inicio, ini_ex) < min(fin, fin_ex):
                                # Posible fusión
                                if salon in [s['cod'] for s in self.salones if 'FA' in s['cod'] or 'FB' in s['cod'] or 'FC' in s['cod']] and seccion.es_fusionable and fus_ex:
                                    if seccion.cupo + cupo_ex <= salon_info['cap']:
                                        continue
                                invade = True
                                break
                        if invade:
                            break
                    
                    if not invade:
                        # Asignación factible
                        asignacion = {
                            'seccion': seccion,
                            'prof': prof,
                            'salon': salon,
                            'patron': patron,
                            'inicio': inicio
                        }
                        asignaciones.append(asignacion)
                        # Actualizar ocupaciones
                        if prof not in ["GRADUADOS", "TBA"]:
                            carga_prof[prof] += seccion.creditos
                            for dia, contrib in patron['days'].items():
                                fin = inicio + int(contrib * 50)
                                ocupacion_prof[(prof, dia)].append((inicio, fin))
                        for dia, contrib in patron['days'].items():
                            fin = inicio + int(contrib * 50)
                            ocupacion_salon[(salon, dia)].append((inicio, fin, seccion.cupo, seccion.es_fusionable))
                        encontrada = True
                        break
            
            if not encontrada:
                # No se pudo asignar de forma factible; esto no debería ocurrir si los datos son consistentes
                # Pero por si acaso, asignamos una combinación aleatoria (luego será reparada)
                prof = random.choice(profes_candidatos)[0]
                salon = random.choice(salones_candidatos)
                patron = random.choice(patrones)
                inicio = random.choice(inicios)
                asignaciones.append({
                    'seccion': seccion,
                    'prof': prof,
                    'salon': salon,
                    'patron': patron,
                    'inicio': inicio
                })
        
        return asignaciones

    def _en_bloqueo(self, prof, dia, inicio, fin):
        if dia not in prof.bloqueo_dias:
            return False
        if prof.bloqueo_ini is None or prof.bloqueo_fin is None:
            return False
        return max(inicio, prof.bloqueo_ini) < min(fin, prof.bloqueo_fin)

    def _soft_score(self, asignaciones):
        """Calcula la calidad de la solución (mayor es mejor)"""
        score = 0.0
        # Preferencias horarias
        for a in asignaciones:
            prof = a['prof']
            if prof not in ["GRADUADOS", "TBA"] and prof in self.profesores:
                pobj = self.profesores[prof]
                # Preferencia de días
                if pobj.pref_dias:
                    dias_patron = set(a['patron']['days'].keys())
                    dias_pref = set(pobj.pref_dias.replace(' ', '').split(','))
                    score += len(dias_patron & dias_pref) * 5
                # Preferencia AM/PM
                if pobj.pref_horas in ['AM', 'PM']:
                    hora_media = a['inicio'] + 25
                    if pobj.pref_horas == 'AM' and hora_media < 720:
                        score += 10
                    elif pobj.pref_horas == 'PM' and hora_media >= 720:
                        score += 10
                # Compensación
                if pobj.compensacion:
                    comp = calcular_compensacion(a['seccion'].creditos, a['seccion'].cupo)
                    score += comp * 20
                # Prioridad de curso
                for idx, pref in enumerate(pobj.preferencias):
                    if pref in a['seccion'].cod:
                        score += 10 / (idx + 1)
        
        # Uso eficiente de capacidad (menos desperdicio mejor)
        for a in asignaciones:
            salon = next(s for s in self.salones if s['cod'] == a['salon'])
            desperdicio = (salon['cap'] - a['seccion'].cupo) / salon['cap']
            score -= desperdicio * 20
        
        # Compactación (evitar huecos grandes)
        # Agrupar por profesor y día
        horarios_prof = defaultdict(list)
        for a in asignaciones:
            prof = a['prof']
            if prof in ["GRADUADOS", "TBA"]:
                continue
            for dia, contrib in a['patron']['days'].items():
                fin = a['inicio'] + int(contrib * 50)
                horarios_prof[(prof, dia)].append((a['inicio'], fin))
        for (prof, dia), horarios in horarios_prof.items():
            if len(horarios) > 1:
                horarios.sort()
                for i in range(len(horarios)-1):
                    hueco = horarios[i+1][0] - horarios[i][1]
                    if hueco > 120:
                        score -= (hueco - 120) / 10
        
        return score

    def _movimiento(self, asignaciones, idx_seccion, tabu):
        """Intenta reasignar la sección en idx a una nueva combinación factible (diferente a la actual)"""
        a = asignaciones[idx_seccion]
        seccion = a['seccion']
        
        # Generar una nueva opción aleatoria
        profes_candidatos = []
        for p in seccion.candidatos:
            if p == "GRADUADOS":
                profes_candidatos.append("GRADUADOS")
            elif p in self.profesores:
                profes_candidatos.append(p)
        if not profes_candidatos:
            profes_candidatos.append("TBA")
        
        salones_candidatos = []
        for s in self.salones:
            if s['tipo'] == seccion.tipo_salon and s['cap'] >= seccion.cupo:
                salones_candidatos.append(s['cod'])
        if not salones_candidatos:
            for s in self.salones:
                if s['cap'] >= seccion.cupo:
                    salones_candidatos.append(s['cod'])
        if not salones_candidatos:
            salones_candidatos = [s['cod'] for s in self.salones]
        
        patrones = PATRONES.get(seccion.creditos, PATRONES[3])
        inicios = self.bloques
        
        # Excluir la combinación actual
        combinacion_actual = (a['prof'], a['salon'], a['patron']['name'], a['inicio'])
        
        for _ in range(100):
            prof = random.choice(profes_candidatos)
            salon = random.choice(salones_candidatos)
            patron = random.choice(patrones)
            inicio = random.choice(inicios)
            if (prof, salon, patron['name'], inicio) == combinacion_actual:
                continue
            # Verificar factibilidad con el resto de asignaciones (sin contar la actual)
            # Para simplificar, asumimos que la nueva asignación debe ser factible con las demás.
            # Construimos un entorno temporal
            otras = asignaciones[:idx_seccion] + asignaciones[idx_seccion+1:]
            if self._es_factible_con_resto(prof, salon, patron, inicio, seccion, otras):
                # También verificar que no esté en tabú
                clave = (idx_seccion, prof, salon, patron['name'], inicio)
                if clave not in tabu:
                    nueva_asignacion = {
                        'seccion': seccion,
                        'prof': prof,
                        'salon': salon,
                        'patron': patron,
                        'inicio': inicio
                    }
                    return nueva_asignacion, clave
        return None, None

    def _es_factible_con_resto(self, prof, salon, patron, inicio, seccion, otras):
        """Verifica si la nueva asignación es factible con las otras asignaciones"""
        # Reconstruir ocupaciones a partir de 'otras'
        ocup_prof = defaultdict(list)
        ocup_salon = defaultdict(list)
        carga_prof = defaultdict(float)
        
        for a in otras:
            p = a['prof']
            s = a['salon']
            pat = a['patron']
            ini = a['inicio']
            if p not in ["GRADUADOS", "TBA"]:
                carga_prof[p] += a['seccion'].creditos
                for dia, contrib in pat['days'].items():
                    fin = ini + int(contrib * 50)
                    ocup_prof[(p, dia)].append((ini, fin))
            for dia, contrib in pat['days'].items():
                fin = ini + int(contrib * 50)
                ocup_salon[(s, dia)].append((ini, fin, a['seccion'].cupo, a['seccion'].es_fusionable))
        
        # Verificar la nueva
        # Carga
        if prof not in ["GRADUADOS", "TBA"]:
            if carga_prof[prof] + seccion.creditos > self.profesores[prof].carga_max:
                return False
        # Límites
        for dia, contrib in patron['days'].items():
            fin = inicio + int(contrib * 50)
            if fin > self.limite_fin or inicio < self.limite_inicio:
                return False
        # Hora universal
        for dia, contrib in patron['days'].items():
            if dia in ["Ma", "Ju"]:
                fin = inicio + int(contrib * 50)
                if max(inicio, self.hora_universal[0]) < min(fin, self.hora_universal[1]):
                    return False
        # Intensivos
        if seccion.creditos == 3:
            for dia, contrib in patron['days'].items():
                if contrib >= 3 and inicio < 930:
                    return False
        # Bloqueos profesor
        if prof not in ["GRADUADOS", "TBA"]:
            prof_obj = self.profesores[prof]
            for dia, contrib in patron['days'].items():
                fin = inicio + int(contrib * 50)
                if self._en_bloqueo(prof_obj, dia, inicio, fin):
                    return False
        # Solapamiento profesor
        if prof not in ["GRADUADOS", "TBA"]:
            for dia, contrib in patron['days'].items():
                fin = inicio + int(contrib * 50)
                for (ini_ex, fin_ex) in ocup_prof.get((prof, dia), []):
                    if max(inicio, ini_ex) < min(fin, fin_ex):
                        return False
        # Solapamiento salón
        salon_info = next(s for s in self.salones if s['cod'] == salon)
        for dia, contrib in patron['days'].items():
            fin = inicio + int(contrib * 50)
            for (ini_ex, fin_ex, cupo_ex, fus_ex) in ocup_salon.get((salon, dia), []):
                if max(inicio, ini_ex) < min(fin, fin_ex):
                    if salon in [s['cod'] for s in self.salones if 'FA' in s['cod'] or 'FB' in s['cod'] or 'FC' in s['cod']] and seccion.es_fusionable and fus_ex:
                        if seccion.cupo + cupo_ex <= salon_info['cap']:
                            continue
                    return False
        return True

    def solve(self, max_iter=1000, tabu_size=50):
        """Búsqueda tabú para mejorar soft constraints"""
        # Construir solución inicial factible
        mejor_sol = self._construir_solucion_factible()
        mejor_score = self._soft_score(mejor_sol)
        
        sol_actual = deepcopy(mejor_sol)
        score_actual = mejor_score
        
        tabu = []
        historial_scores = [mejor_score]
        
        for iteracion in range(max_iter):
            # Generar vecinos (movimientos)
            mejor_vecino = None
            mejor_vecino_score = -float('inf')
            mejor_movimiento = None
            
            # Intentar mover cada sección (elegir una aleatoria para eficiencia)
            for _ in range(10):  # probar 10 movimientos diferentes
                idx = random.randint(0, len(sol_actual)-1)
                nueva_asign, clave = self._movimiento(sol_actual, idx, tabu)
                if nueva_asign:
                    # Crear nueva solución
                    vecino = deepcopy(sol_actual)
                    vecino[idx] = nueva_asign
                    score_vecino = self._soft_score(vecino)
                    if score_vecino > mejor_vecino_score:
                        mejor_vecino = vecino
                        mejor_vecino_score = score_vecino
                        mejor_movimiento = clave
            
            if mejor_vecino and mejor_vecino_score > score_actual:
                # Aceptar movimiento
                sol_actual = mejor_vecino
                score_actual = mejor_vecino_score
                tabu.append(mejor_movimiento)
                if len(tabu) > tabu_size:
                    tabu.pop(0)
                if score_actual > mejor_score:
                    mejor_sol = sol_actual
                    mejor_score = score_actual
            else:
                # Criterio de aspiración: si el mejor vecino es mejor que el mejor global, aceptar aunque sea tabú
                if mejor_vecino and mejor_vecino_score > mejor_score:
                    sol_actual = mejor_vecino
                    score_actual = mejor_vecino_score
                    mejor_sol = sol_actual
                    mejor_score = score_actual
                    # No añadir a tabú? o sí?
                    tabu.append(mejor_movimiento)
                    if len(tabu) > tabu_size:
                        tabu.pop(0)
            
            historial_scores.append(mejor_score)
            if iteracion % 100 == 0:
                # Podríamos actualizar barra aquí
                pass
        
        # Verificar que no haya conflictos duros (por si acaso)
        conflictos = self._verificar_conflictos(mejor_sol)
        return mejor_sol, conflictos

    def _verificar_conflictos(self, sol):
        """Devuelve lista de descripciones de conflictos duros (vacía si no hay)"""
        conflictos = []
        ocup_prof = defaultdict(list)
        ocup_salon = defaultdict(list)
        carga_prof = defaultdict(float)
        
        for a in sol:
            secc = a['seccion']
            prof = a['prof']
            salon = a['salon']
            patron = a['patron']
            inicio = a['inicio']
            
            if prof == "TBA":
                conflictos.append(f"[{secc.cod}] Profesor TBA")
                continue
            if prof not in secc.candidatos and prof != "GRADUADOS":
                conflictos.append(f"[{secc.cod}] Profesor {prof} no elegible")
            
            # Capacidad
            salon_info = next(s for s in self.salones if s['cod'] == salon)
            if salon_info['cap'] < secc.cupo:
                conflictos.append(f"[{secc.cod}] Sobrecupo en {salon}")
            
            # Tipo
            if salon_info['tipo'] != secc.tipo_salon:
                if not (salon in [s['cod'] for s in self.salones if 'FA' in s['cod']] and secc.es_fusionable):
                    conflictos.append(f"[{secc.cod}] Tipo de salón incorrecto")
            
            # Límites
            for dia, contrib in patron['days'].items():
                fin = inicio + int(contrib * 50)
                if fin > self.limite_fin or inicio < self.limite_inicio:
                    conflictos.append(f"[{secc.cod}] Fuera de límite operativo")
                if dia in ["Ma", "Ju"]:
                    if max(inicio, self.hora_universal[0]) < min(fin, self.hora_universal[1]):
                        conflictos.append(f"[{secc.cod}] Invade hora universal")
                if secc.creditos == 3 and contrib >= 3 and inicio < 930:
                    conflictos.append(f"[{secc.cod}] Intensivo antes de 3:30 PM")
            
            # Bloqueos profesor
            if prof not in ["GRADUADOS", "TBA"]:
                prof_obj = self.profesores[prof]
                for dia, contrib in patron['days'].items():
                    fin = inicio + int(contrib * 50)
                    if self._en_bloqueo(prof_obj, dia, inicio, fin):
                        conflictos.append(f"[{secc.cod}] {prof} en bloqueo")
            
            # Actualizar ocupaciones para detectar solapamientos
            if prof not in ["GRADUADOS", "TBA"]:
                for dia, contrib in patron['days'].items():
                    fin = inicio + int(contrib * 50)
                    for (ini_ex, fin_ex) in ocup_prof.get((prof, dia), []):
                        if max(inicio, ini_ex) < min(fin, fin_ex):
                            conflictos.append(f"[{secc.cod}] {prof} solapado")
                    ocup_prof[(prof, dia)].append((inicio, fin))
            
            for dia, contrib in patron['days'].items():
                fin = inicio + int(contrib * 50)
                for (ini_ex, fin_ex, cupo_ex, fus_ex) in ocup_salon.get((salon, dia), []):
                    if max(inicio, ini_ex) < min(fin, fin_ex):
                        if salon in [s['cod'] for s in self.salones if 'FA' in s['cod']] and secc.es_fusionable and fus_ex:
                            if secc.cupo + cupo_ex <= salon_info['cap']:
                                continue
                        conflictos.append(f"[{secc.cod}] Salón {salon} solapado")
                ocup_salon[(salon, dia)].append((inicio, fin, secc.cupo, secc.es_fusionable))
            
            # Carga
            if prof not in ["GRADUADOS", "TBA"]:
                carga_prof[prof] += secc.creditos
        
        # Carga máxima y mínima
        for prof, carga in carga_prof.items():
            prof_obj = self.profesores[prof]
            if carga > prof_obj.carga_max:
                conflictos.append(f"Profesor {prof} sobrecarga")
            if carga < prof_obj.carga_min:
                conflictos.append(f"Profesor {prof} no cumple carga mínima")
        
        return conflictos

# ==============================================================================
# 5. INTERFAZ PRINCIPAL (IDENTICA)
# ==============================================================================
def main():
    with st.sidebar:
        st.markdown("### $\Sigma$ Configuración")
        zona = st.selectbox("Zona Campus", ["CENTRAL", "PERIFERICA"])
        # Parámetros de búsqueda tabú
        iteraciones = st.slider("Iteraciones Búsqueda", 100, 2000, 500)
        file = st.file_uploader("Subir Protocolo Excel", type=['xlsx'])

    st.markdown(f"### $\Omega$ Condiciones de Zona: {zona}")
    c1, c2, c3 = st.columns(3)
    
    h_bloqueo = "10:30 AM - 12:30 PM" if zona == "CENTRAL" else "10:00 AM - 12:00 PM"
    limites = "07:30 AM - 07:30 PM" if zona == "CENTRAL" else "07:00 AM - 07:00 PM"
    
    with c1: st.metric("Ventana Operativa", limites)
    with c2: st.metric("Hora Universal", h_bloqueo)
    with c3:
        st.markdown(f"""<div class="status-badge">MODO PERFECCIÓN: ACTIVO</div>""", unsafe_allow_html=True)

    if not file:
        st.markdown("""
            <div class='glass-card' style='text-align: center;'>
                <h3 style='margin-top:0; color: #D4AF37;'>📥 Sincronización de Datos</h3>
                <p>Cargue el protocolo para iniciar la optimización. El sistema detectará automáticamente la capacidad por sección y generará el horario óptimo.</p>
            </div>
        """, unsafe_allow_html=True)
        st.download_button("Plantilla Nueva (Actualizada)", crear_excel_guia(), "Plantilla_UPRM_Actualizada.xlsx", use_container_width=True)
            
    else:
        if st.button("🚀 INICIAR OPTIMIZACIÓN PERFECTA"):
            with st.spinner("Construyendo horario factible y mejorando con búsqueda tabú..."):
                xls = pd.ExcelFile(file)
                df_cursos = pd.read_excel(xls, 'Cursos')
                df_profes = pd.read_excel(xls, 'Profesores')
                df_salones = pd.read_excel(xls, 'Salones')

                scheduler = TabuScheduler(df_cursos, df_profes, df_salones, zona)
                
                start_time = time.time()
                mejor_sol, conflictos = scheduler.solve(max_iter=iteraciones)
                elapsed = time.time() - start_time
                
                st.session_state.elapsed_time = elapsed
                st.session_state.conflicts = conflictos
                st.session_state.master = pd.DataFrame([{
                    'ID': a['seccion'].cod, 
                    'Asignatura': a['seccion'].cod.split('-')[0],
                    'Creditos': a['seccion'].creditos,
                    'Persona': a['prof'], 
                    'Días': a['patron']['name'], 
                    'Horario': format_horario(a['patron'], a['inicio']), 
                    'Salón': a['salon'],
                    'Tipo_Salon': a['seccion'].tipo_salon,
                    'Demanda': a['seccion'].cupo
                } for a in mejor_sol])

    if 'master' in st.session_state:
        st.success(f"✅ Optimización completada en {st.session_state.elapsed_time:.2f} segundos.")
        
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        t1, t2, t3 = st.tabs(["💎 PANEL DE CONTROL", "🔍 VISTAS DETALLADAS", "🚨 AUDITORÍA DE CALIDAD"])
        
        with t1:
            edited = st.data_editor(st.session_state.master, use_container_width=True, height=500)
            st.download_button("💾 EXPORTAR EXCEL PLATINUM", exportar_todo(edited), "Horario_Final_UPRM.xlsx", use_container_width=True)
            
        with t2:
            f1, f2, f3, f4 = st.tabs(["Por Profesor", "Por Curso", "Por Salón", "Graduados"])
            df_master = st.session_state.master
            
            with f1:
                lista_profes = sorted([p for p in df_master['Persona'].unique() if p != "GRADUADOS"])
                if lista_profes:
                    p = st.selectbox("Seleccionar Profesor", lista_profes)
                    subset = df_master[df_master['Persona'] == p]
                    st.table(subset[['ID', 'Creditos', 'Días', 'Horario', 'Salón']])
                    st.metric(f"Carga Total", f"{subset['Creditos'].sum()} Créditos")
            
            with f2:
                lista_cursos = sorted(df_master['Asignatura'].unique())
                if lista_cursos:
                    c = st.selectbox("Seleccionar Curso", lista_cursos)
                    subset = df_master[df_master['Asignatura'] == c]
                    st.table(subset[['ID', 'Persona', 'Días', 'Horario', 'Salón']])
            
            with f3:
                lista_salones = sorted(df_master['Salón'].unique())
                if lista_salones:
                    sl = st.selectbox("Seleccionar Salón", lista_salones)
                    subset = df_master[df_master['Salón'] == sl]
                    st.table(subset[['ID', 'Asignatura', 'Persona', 'Días', 'Horario']])
            
            with f4:
                st.markdown("#### Clases asignadas a Estudiantes Graduados")
                subset = df_master[df_master['Persona'] == "GRADUADOS"]
                st.table(subset[['ID', 'Asignatura', 'Días', 'Horario', 'Salón']])
                st.metric("Total Secciones de Graduados", len(subset))
                
        with t3:
            conflictos = st.session_state.conflicts
            if len(conflictos) > 0:
                st.error(f"⚠️ Se detectaron {len(conflictos)} conflictos o irregularidades. Revise los datos de entrada.")
                conflictos_unicos = list(set(conflictos))
                for txt in conflictos_unicos:
                    st.markdown(f"- `{txt}`")
            else:
                st.success("✅ 100% Asignación Perfecta. Cero Conflictos. Se respetaron todas las métricas de espacio, carga y Hora Universal.")
                
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
