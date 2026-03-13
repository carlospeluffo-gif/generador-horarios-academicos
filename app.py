import streamlit as st
import pandas as pd
import numpy as np
import random
import io
import time
import math
from datetime import time as dtime

# ==============================================================================
# 1. ESTÉTICA PLATINUM ELITE (INTACTA)
# ==============================================================================
st.set_page_config(page_title="UPRM Scheduler Platinum AI v9", page_icon="🏛️", layout="wide")

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
            UPRM MATHEMATICAL OPTIMIZATION ENGINE v9.0 (RESTRICCIONES FORMALES)
        </p>
    </div>
    <div class="abstract-icon">∞</div>
</div>
""", unsafe_allow_html=True)

st.latex(r"\blacksquare \quad \text{SISTEMA DE PLANIFICACIÓN ACADÉMICA OPTIMIZADA - TESIS MASTER} \quad \blacksquare")

# ==============================================================================
# 2. UTILIDADES Y TABLA DE PATRONES
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

# Patrones actualizados para reflejar duraciones reales (en horas, 1 = 50 min)
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
    horas = creditos
    for h, min_e, max_e, add in COMPENSACION_TABLE:
        if h == horas and min_e <= estudiantes <= max_e:
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
            if str(p) != "TBA" and str(p) != "GRADUADOS":
                clean_name = "".join([c for c in str(p) if c.isalnum() or c==' '])[:25]
                df[df['Persona'] == p].to_excel(writer, sheet_name=f"User_{clean_name}", index=False)
    return out.getvalue()

# ==============================================================================
# 3. DEFINICIÓN DE RESTRICCIONES DURAS Y SUAVES
# ==============================================================================
class SeccionData:
    def __init__(self, cod, creditos, cupo, cands, tipo_salon, es_ayudantia=False):
        self.cod = str(cod)
        self.creditos = int(creditos)
        self.cupo = int(cupo)
        
        if isinstance(cands, list):
            self.cands = [c.strip().upper() for c in cands if c.strip()]
        else:
            self.cands = [c.strip().upper() for c in str(cands).split(',') if c.strip() and str(c).upper() != 'NAN']
        
        try: self.tipo_salon = int(float(str(tipo_salon)))
        except: self.tipo_salon = 1
            
        self.es_ayudantia = es_ayudantia
        base = self.cod.split('-')[0].upper().replace(" ", "")
        self.es_fusionable = base in ["MATE3171", "MATE3172", "MATE3173"]

class ProfesorData:
    def __init__(self, nombre, carga_min, carga_max, pref_dias, pref_horas,
                 bloqueo_dias, bloqueo_ini, bloqueo_fin,
                 preferencias_cursos, compensacion, acepta_grandes):
        self.nombre = nombre.upper().strip()
        self.carga_min = float(carga_min) if carga_min not in (None, '') else 0.0
        self.carga_max = float(carga_max) if carga_max not in (None, '') else 12.0
        self.pref_dias = pref_dias if isinstance(pref_dias, str) else ''
        self.pref_horas = pref_horas if isinstance(pref_horas, str) else 'ANY'
        self.bloqueo_dias = set()
        if isinstance(bloqueo_dias, str) and bloqueo_dias.strip():
            self.bloqueo_dias = {d.strip().title() for d in bloqueo_dias.split(',') if d.strip()}
        self.bloqueo_ini = str_to_mins(bloqueo_ini) if isinstance(bloqueo_ini, str) and bloqueo_ini else None
        self.bloqueo_fin = str_to_mins(bloqueo_fin) if isinstance(bloqueo_fin, str) and bloqueo_fin else None
        
        self.preferencias = []
        if isinstance(preferencias_cursos, list):
            self.preferencias = [c.upper().strip() for c in preferencias_cursos if c and str(c).upper() != 'NAN']
        self.compensacion = str(compensacion).upper().strip() in ('SI', 'SÍ', 'YES', '1')
        self.acepta_grandes = int(acepta_grandes) if acepta_grandes not in (None, '') else 0

    def prioridad_curso(self, curso_cod):
        for idx, pref in enumerate(self.preferencias):
            if pref in curso_cod:
                return 1.0 / (idx + 1)
        return 0.0

class PlatinumEliteEngine:
    def __init__(self, df_cursos, df_profes, df_salones, zona):
        self.zona = zona
        
        # ===== Salones =====
        df_salones.columns = [c.strip().upper() for c in df_salones.columns]
        self.salones = []
        self.mega_salones = set()
        for _, r in df_salones.iterrows():
            codigo = str(r['CODIGO']).strip().upper()
            try: cap = int(r['CAPACIDAD'])
            except: cap = 25
            try: tipo = int(r['TIPO'])
            except: tipo = 1
            self.salones.append({'CODIGO': codigo, 'CAPACIDAD': cap, 'TIPO': tipo})
            norm_cod = codigo.replace(" ", "").replace("-", "")
            if any(x in norm_cod for x in ["FA", "FB", "FC"]):
                self.mega_salones.add(codigo)

        # ===== Profesores =====
        self.profesores = {}
        if df_profes is not None and not df_profes.empty:
            for _, r in df_profes.iterrows():
                prefs = []
                for col in ['PREF1', 'PREF2', 'PREF3']:
                    val = r.get(col, '')
                    if pd.notnull(val) and str(val).strip().upper() != 'NAN':
                        prefs.append(str(val).strip().upper())
                prof = ProfesorData(
                    nombre=r['NOMBRE'],
                    carga_min=r.get('CARGA_MIN', 0),
                    carga_max=r.get('CARGA_MAX', 15),
                    pref_dias=r.get('PREF_DIAS', ''),
                    pref_horas=r.get('PREF_HORAS', 'ANY'),
                    bloqueo_dias=r.get('BLOQUEO_DIAS', ''),
                    bloqueo_ini=r.get('BLOQUEO_HORA_INI', ''),
                    bloqueo_fin=r.get('BLOQUEO_HORA_FIN', ''),
                    preferencias_cursos=prefs,
                    compensacion=r.get('COMPENSACION', 'NO'),
                    acepta_grandes=r.get('ACEPTA_GRANDES', 0)
                )
                self.profesores[prof.nombre] = prof

        # ===== Cursos =====
        self.oferta = []
        df_cursos.columns = [c.strip().upper() for c in df_cursos.columns]
        for _, r in df_cursos.iterrows():
            codigo_base = str(r['CODIGO']).strip().upper()
            creditos = int(r['CREDITOS'])
            demanda = int(r.get('DEMANDA', 0))
            cupo_raw = str(r.get('CUPO', '30')).strip()
            candidatos_raw = r.get('CANDIDATOS', '')
            tipo_salon = int(r.get('TIPO_SALON', 1))

            if ',' in cupo_raw:
                capacidades = [int(x.strip()) for x in cupo_raw.split(',') if x.strip().isdigit()]
            else:
                try: cap_unica = int(cupo_raw)
                except: cap_unica = 30
                num_secciones = math.ceil(demanda / cap_unica) if demanda > 0 else 1
                capacidades = [cap_unica] * num_secciones

            total_cupo = sum(capacidades)
            if total_cupo < demanda and demanda > 0:
                capacidades.append(capacidades[-1])

            for i, cap in enumerate(capacidades):
                if cap <= 0: continue
                self.oferta.append(SeccionData(f"{codigo_base}-{i+1:02d}", creditos, cap, candidatos_raw, tipo_salon))

        # Bloques de 30 minutos desde 7:00 AM hasta 7:30 PM (420 a 1170)
        self.bloques = list(range(420, 1171, 30))
        
        # Restricciones institucionales según zona
        if zona == "CENTRAL":
            self.hora_universal = (630, 750)  # 10:30 AM - 12:30 PM
            self.limite_operativo = (450, 1170)  # 7:30 AM - 7:30 PM (pero nuestro rango ya es 7:00-7:30, ajustamos)
        else:  # PERIFERICA
            self.hora_universal = (600, 720)  # 10:00 AM - 12:00 PM
            self.limite_operativo = (420, 1140)  # 7:00 AM - 7:00 PM

    def _es_bloqueo_activo(self, prof, dia, ini, fin):
        if not prof.bloqueo_dias or dia not in prof.bloqueo_dias: return False
        if prof.bloqueo_ini is None or prof.bloqueo_fin is None: return False
        return max(ini, prof.bloqueo_ini) < min(fin, prof.bloqueo_fin)

    def _suit_prof(self, prof, seccion):
        prioridad = prof.prioridad_curso(seccion.cod.split('-')[0])
        if seccion.cupo >= 85:
            return 2.0 * prioridad if prof.acepta_grandes == 1 else 0.0
        return prioridad

    # ==========================================================================
    # Construcción priorizada de individuos (asignación secuencial)
    # ==========================================================================
    def _build_individual_prioritized(self):
        """
        Construye un individuo asignando primero las secciones con un solo candidato,
        luego las de profesores con menor carga acumulada, etc.
        """
        # Copia de la oferta para ir asignando
        secciones_pendientes = self.oferta.copy()
        
        # Diccionarios para llevar control de ocupación
        occ_prof = {}   # (prof, dia) -> lista de (ini, fin)
        occ_salon = {}  # (salon, dia) -> lista de (ini, fin, cupo, fusionable)
        carga_prof = {} # prof -> creditos acumulados
        
        # Resultado: lista de genes
        individuo = []
        
        # Función auxiliar para verificar si un bloque es válido para una sección con un profesor y salón dados
        def bloque_valido(seccion, prof, salon, patron, ini):
            # Verificar límite operativo
            for dia, contrib in patron['days'].items():
                fin = ini + int(contrib * 50)
                if fin > self.limite_operativo[1] or ini < self.limite_operativo[0]:
                    return False
            
            # Verificar hora universal
            for dia, contrib in patron['days'].items():
                if dia in ["Ma", "Ju"]:
                    fin = ini + int(contrib * 50)
                    if max(ini, self.hora_universal[0]) < min(fin, self.hora_universal[1]):
                        return False
            
            # Verificar restricción de cursos de 3 horas (intensivos después de 3:30 PM)
            if seccion.creditos == 3:
                # Si el patrón tiene algún día con duración >=3 horas, verificar inicio
                for dia, contrib in patron['days'].items():
                    if contrib >= 3:
                        if ini < 930:  # 3:30 PM en minutos
                            return False
            
            # Verificar disponibilidad del profesor (bloqueos)
            if prof != "GRADUADOS" and prof != "TBA":
                prof_obj = self.profesores.get(prof)
                if prof_obj:
                    for dia, contrib in patron['days'].items():
                        fin = ini + int(contrib * 50)
                        if self._es_bloqueo_activo(prof_obj, dia, ini, fin):
                            return False
            
            # Verificar conflictos de profesor
            if prof != "GRADUADOS" and prof != "TBA":
                for dia, contrib in patron['days'].items():
                    fin = ini + int(contrib * 50)
                    clave = (prof, dia)
                    if clave in occ_prof:
                        for (ini_ex, fin_ex) in occ_prof[clave]:
                            if max(ini, ini_ex) < min(fin, fin_ex):
                                return False
            
            # Verificar conflictos de salón
            if salon != "TBA":
                salon_info = next((s for s in self.salones if s['CODIGO'] == salon), None)
                for dia, contrib in patron['days'].items():
                    fin = ini + int(contrib * 50)
                    clave = (salon, dia)
                    if clave in occ_salon:
                        for (ini_ex, fin_ex, cupo_ex, fusionable_ex) in occ_salon[clave]:
                            if max(ini, ini_ex) < min(fin, fin_ex):
                                # Si es salón mega y ambas son fusionables, permitir si no excede capacidad
                                if salon in self.mega_salones and seccion.es_fusionable and fusionable_ex:
                                    if salon_info and (seccion.cupo + cupo_ex) <= salon_info['CAPACIDAD']:
                                        continue  # fusión permitida
                                return False
            return True
        
        # Función para asignar una sección con un profesor dado (si es posible)
        def asignar_seccion(seccion, prof=None):
            nonlocal individuo, occ_prof, occ_salon, carga_prof
            
            # Determinar candidatos profesor
            if prof is None:
                # Si no se especifica, considerar todos los candidatos de la sección (incluyendo GRADUADOS y TBA como último recurso)
                candidatos_prof = seccion.cands.copy() if seccion.cands else []
                # Añadir TBA como opción de último recurso
                candidatos_prof.append("TBA")
            else:
                candidatos_prof = [prof]
            
            # Ordenar candidatos: primero GRADUADOS, luego profesores con menor carga, luego TBA
            def prioridad_prof(p):
                if p == "GRADUADOS":
                    return (0, 0)
                if p == "TBA":
                    return (2, 0)
                # Profesores reales: ordenar por carga actual (menor mejor) y luego por prioridad de curso
                carga_actual = carga_prof.get(p, 0)
                prof_obj = self.profesores.get(p)
                if prof_obj:
                    prior = -self._suit_prof(prof_obj, seccion)  # negativo para que mayor prioridad sea menor valor
                else:
                    prior = 0
                return (1, carga_actual, prior)
            
            candidatos_prof.sort(key=prioridad_prof)
            
            # Buscar combinación válida para algún profesor de la lista
            for prof_cand in candidatos_prof:
                # Si el profesor es TBA, no verificamos conflictos de profesor (pero luego se penalizará)
                # Si es GRADUADOS, tampoco verificamos conflictos (se asume que no hay restricción de disponibilidad)
                # Pero sí debemos verificar que si es un profesor real, exista y no exceda carga máxima
                if prof_cand not in ["GRADUADOS", "TBA"]:
                    prof_obj = self.profesores.get(prof_cand)
                    if not prof_obj:
                        continue
                    # Verificar carga máxima
                    if carga_prof.get(prof_cand, 0) + seccion.creditos > prof_obj.carga_max:
                        continue
                
                # Obtener patrones posibles para esta sección
                patrones_posibles = PATRONES.get(seccion.creditos, PATRONES[3])
                # Ordenar patrones de forma aleatoria para diversidad
                random.shuffle(patrones_posibles)
                
                # Posibles salones
                # Primero buscar salones que cumplan tipo y capacidad
                salones_posibles = [s['CODIGO'] for s in self.salones if s['TIPO'] == seccion.tipo_salon and s['CAPACIDAD'] >= seccion.cupo]
                if not salones_posibles and seccion.tipo_salon < 3:
                    # Si no hay, permitir cualquier salón con capacidad suficiente
                    salones_posibles = [s['CODIGO'] for s in self.salones if s['CAPACIDAD'] >= seccion.cupo]
                # Si aún así no hay, permitir cualquier salón (luego se penalizará)
                if not salones_posibles:
                    salones_posibles = [s['CODIGO'] for s in self.salones]
                
                # Mezclar para diversidad
                random.shuffle(salones_posibles)
                
                # Intentar todas las combinaciones de patrón, inicio y salón
                for patron in patrones_posibles:
                    # Mezclar bloques para diversidad
                    bloques_mezclados = self.bloques.copy()
                    random.shuffle(bloques_mezclados)
                    for ini in bloques_mezclados:
                        for salon in salones_posibles:
                            if bloque_valido(seccion, prof_cand, salon, patron, ini):
                                # Asignar
                                individuo.append({
                                    'sec': seccion,
                                    'prof': prof_cand,
                                    'salon': salon,
                                    'patron': patron,
                                    'ini': ini
                                })
                                # Actualizar ocupaciones
                                if prof_cand not in ["GRADUADOS", "TBA"]:
                                    carga_prof[prof_cand] = carga_prof.get(prof_cand, 0) + seccion.creditos
                                    for dia, contrib in patron['days'].items():
                                        fin = ini + int(contrib * 50)
                                        occ_prof.setdefault((prof_cand, dia), []).append((ini, fin))
                                if salon != "TBA":
                                    for dia, contrib in patron['days'].items():
                                        fin = ini + int(contrib * 50)
                                        occ_salon.setdefault((salon, dia), []).append((ini, fin, seccion.cupo, seccion.es_fusionable))
                                return True
            # Si no se pudo asignar, crear una asignación por defecto (con TBA y cualquier cosa)
            # Elegir cualquier patrón, cualquier inicio, cualquier salón (sin verificar)
            patron = random.choice(PATRONES.get(seccion.creditos, PATRONES[3]))
            ini = random.choice(self.bloques)
            salon = random.choice([s['CODIGO'] for s in self.salones]) if self.salones else "TBA"
            prof_final = candidatos_prof[0] if candidatos_prof else "TBA"
            individuo.append({
                'sec': seccion,
                'prof': prof_final,
                'salon': salon,
                'patron': patron,
                'ini': ini
            })
            # No actualizamos ocupaciones porque puede tener conflictos, se penalizarán
            return False
        
        # Paso 1: Secciones con un solo candidato (excluyendo TBA y GRADUADOS)
        unico_candidato = [s for s in secciones_pendientes if len(s.cands) == 1 and s.cands[0] not in ["TBA", "GRADUADOS"]]
        for s in unico_candidato:
            if asignar_seccion(s, prof=s.cands[0]):
                secciones_pendientes.remove(s)
        
        # Paso 2: Secciones con candidatos, pero ordenadas por número de candidatos (menos primero)
        secciones_con_cands = [s for s in secciones_pendientes if s.cands and s not in unico_candidato]
        secciones_con_cands.sort(key=lambda x: len(x.cands))
        for s in secciones_con_cands:
            if asignar_seccion(s):
                secciones_pendientes.remove(s)
        
        # Paso 3: Secciones sin candidatos (solo TBA como opción)
        secciones_sin_cands = [s for s in secciones_pendientes if not s.cands]
        for s in secciones_sin_cands:
            asignar_seccion(s, prof="TBA")
            # Las removemos igual aunque no hayamos verificado
            secciones_pendientes.remove(s)
        
        # Si quedan, asignar por defecto
        for s in secciones_pendientes:
            asignar_seccion(s)
        
        return individuo

    def _create_smart_individual(self):
        """Versión que usa la construcción priorizada"""
        return self._build_individual_prioritized()

    # ==========================================================================
    # Función de fitness con todas las restricciones
    # ==========================================================================
    def _fitness_detailed(self, ind):
        penalty = 0
        conflicts = 0
        conflict_details = []
        bad_indices = set()
        soft_score = 0.0

        occ_salon = {}   # (salon, dia) -> lista de (ini, fin, cupo, fusionable)
        occ_prof = {}    # (prof, dia) -> lista de (ini, fin)
        carga_prof = {}  # prof -> creditos acumulados
        # Para restricción de doble rol (graduados)
        # Asumimos que los graduados están en la lista de profesores con nombre "GRADUADOS" pero también pueden ser estudiantes.
        # Simplificamos: si un profesor es "GRADUADOS", no aplicamos restricciones de disponibilidad ni carga.
        # Para la restricción Rf10, necesitaríamos saber qué cursos toman los graduados. Como no tenemos esa info,
        # omitimos por ahora (se podría añadir una hoja de inscripción). Dejamos la estructura pero sin implementar.
        
        # Para soft constraint R_s2 (distribución equitativa de secciones)
        secciones_por_curso_base = {}  # curso_base -> lista de bloques (día, inicio, fin)
        
        # Para soft constraint R_s4 (compactación), necesitamos agrupar por profesor y día
        horario_prof_dia = {}  # (prof, dia) -> lista de (ini, fin)

        for i, g in enumerate(ind):
            sec = g['sec']
            prof_nombre = g['prof']
            salon = g['salon']
            patron = g['patron']
            ini = g['ini']
            curso_base = sec.cod.split('-')[0]

            # ========== Restricciones Duras ==========
            
            # Rf1: Unicidad (por construcción, cada sección aparece una vez)

            # Rf2: Conflicto de profesor (se evalúa después con occ_prof)
            # Rf3: Conflicto de salón (después con occ_salon)
            
            # Rf4: Suficiencia de capacidad
            salon_info = next((s for s in self.salones if s['CODIGO'] == salon), None) if salon != "TBA" else None
            if salon_info and salon_info['CAPACIDAD'] < sec.cupo:
                penalty += 10000
                conflicts += 1
                conflict_details.append(f"[{sec.cod}] Capacidad insuficiente en {salon}")
                bad_indices.add(i)

            # Rf5: Compatibilidad de tipo de salón
            if salon_info and salon_info['TIPO'] != sec.tipo_salon:
                # Excepción: si es salón mega y la sección es fusionable, se permite
                if not (salon in self.mega_salones and sec.es_fusionable):
                    penalty += 10000
                    conflicts += 1
                    conflict_details.append(f"[{sec.cod}] Tipo de salón incorrecto")
                    bad_indices.add(i)

            # Rf6: Disponibilidad del profesor (bloqueos)
            if prof_nombre not in ["GRADUADOS", "TBA"]:
                prof_obj = self.profesores.get(prof_nombre)
                if prof_obj:
                    for dia, contrib in patron['days'].items():
                        fin = ini + int(contrib * 50)
                        if self._es_bloqueo_activo(prof_obj, dia, ini, fin):
                            penalty += 10000
                            conflicts += 1
                            conflict_details.append(f"[{sec.cod}] {prof_nombre} en hora de bloqueo")
                            bad_indices.add(i)

            # Rf7: Carga máxima del profesor (se acumula después)
            # Rf8: Carga mínima (se evalúa al final)

            # Rf9: Hora universal
            for dia, contrib in patron['days'].items():
                if dia in ["Ma", "Ju"]:
                    fin = ini + int(contrib * 50)
                    if max(ini, self.hora_universal[0]) < min(fin, self.hora_universal[1]):
                        penalty += 10000
                        conflicts += 1
                        conflict_details.append(f"[{sec.cod}] Invade hora universal el {dia}")
                        bad_indices.add(i)

            # Rf10: Conflicto de doble rol (omitido por ahora, se podría implementar con datos de matrícula)

            # Restricción institucional: cursos de 3 horas después de 3:30 PM
            if sec.creditos == 3:
                for dia, contrib in patron['days'].items():
                    if contrib >= 3:  # intensivo
                        if ini < 930:
                            penalty += 10000
                            conflicts += 1
                            conflict_details.append(f"[{sec.cod}] Intensivo antes de 3:30 PM")
                            bad_indices.add(i)

            # ========== Acumulación para restricciones que requieren comparaciones ==========
            if prof_nombre not in ["GRADUADOS", "TBA"]:
                carga_prof[prof_nombre] = carga_prof.get(prof_nombre, 0) + sec.creditos

            for dia, contrib in patron['days'].items():
                fin = ini + int(contrib * 50)
                rango = (ini, fin)

                # Ocupación de profesor (para Rf2)
                if prof_nombre not in ["GRADUADOS", "TBA"]:
                    clave_prof = (prof_nombre, dia)
                    if clave_prof not in occ_prof:
                        occ_prof[clave_prof] = []
                    # Verificar conflictos con asignaciones previas
                    for (ini_ex, fin_ex) in occ_prof[clave_prof]:
                        if max(ini, ini_ex) < min(fin, fin_ex):
                            penalty += 10000
                            conflicts += 1
                            conflict_details.append(f"[{sec.cod}] {prof_nombre} solapado el {dia}")
                            bad_indices.add(i)
                    occ_prof[clave_prof].append((ini, fin))

                # Ocupación de salón (para Rf3)
                if salon != "TBA":
                    clave_salon = (salon, dia)
                    if clave_salon not in occ_salon:
                        occ_salon[clave_salon] = []
                    # Verificar conflictos
                    for (ini_ex, fin_ex, cupo_ex, fusionable_ex) in occ_salon[clave_salon]:
                        if max(ini, ini_ex) < min(fin, fin_ex):
                            # Posible fusión
                            if salon in self.mega_salones and sec.es_fusionable and fusionable_ex:
                                # Verificar que la suma no exceda capacidad
                                if salon_info and (sec.cupo + cupo_ex) <= salon_info['CAPACIDAD']:
                                    continue  # fusión permitida, no hay conflicto
                            penalty += 10000
                            conflicts += 1
                            conflict_details.append(f"[{sec.cod}] Salón {salon} solapado el {dia}")
                            bad_indices.add(i)
                    occ_salon[clave_salon].append((ini, fin, sec.cupo, sec.es_fusionable))

                # Para soft R_s2: agrupar por curso base y bloque (día, inicio)
                # Definimos bloque como (dia, ini) para detectar múltiples secciones en el mismo horario
                clave_curso_bloque = (curso_base, dia, ini)
                secciones_por_curso_base.setdefault(clave_curso_bloque, []).append(sec.cod)

                # Para soft R_s4: horario por profesor y día
                if prof_nombre not in ["GRADUADOS", "TBA"]:
                    horario_prof_dia.setdefault((prof_nombre, dia), []).append((ini, fin))

        # ========== Restricciones que se evalúan después de acumular ==========
        
        # Rf7: Carga máxima
        for prof, carga in carga_prof.items():
            prof_obj = self.profesores.get(prof)
            if prof_obj and carga > prof_obj.carga_max:
                penalty += 10000
                conflicts += 1
                conflict_details.append(f"Profesor {prof} sobrecarga de créditos")
                # Marcar todas las secciones de ese profesor como malas (opcional)
                for idx, g in enumerate(ind):
                    if g['prof'] == prof:
                        bad_indices.add(idx)

        # Rf8: Carga mínima (penalización suave o dura? Según la tabla es dura)
        for prof, carga in carga_prof.items():
            prof_obj = self.profesores.get(prof)
            if prof_obj and carga < prof_obj.carga_min:
                penalty += 10000
                conflicts += 1
                conflict_details.append(f"Profesor {prof} no cumple carga mínima")
                for idx, g in enumerate(ind):
                    if g['prof'] == prof:
                        bad_indices.add(idx)

        # ========== Restricciones Suaves ==========
        
        # R_s1: Preferencias horarias del profesor (AM/PM)
        for i, g in enumerate(ind):
            prof_nombre = g['prof']
            if prof_nombre not in ["GRADUADOS", "TBA"]:
                prof_obj = self.profesores.get(prof_nombre)
                if prof_obj and prof_obj.pref_horas in ['AM', 'PM']:
                    # Determinar si la clase cae en AM o PM (consideramos AM antes de 12:00)
                    # Tomamos la hora de inicio como referencia
                    if prof_obj.pref_horas == 'AM' and g['ini'] >= 720:
                        soft_score -= 10  # penalización
                    elif prof_obj.pref_horas == 'PM' and g['ini'] < 720:
                        soft_score -= 10

        # R_s2: Distribución equitativa de secciones
        for (curso_base, dia, ini), secciones in secciones_por_curso_base.items():
            if len(secciones) > 1:
                # Penalizar por cada sección adicional
                soft_score -= (len(secciones) - 1) * 20

        # R_s3: Uso eficiente de la capacidad
        for g in ind:
            if g['salon'] != "TBA":
                salon_info = next((s for s in self.salones if s['CODIGO'] == g['salon']), None)
                if salon_info:
                    desperdicio = (salon_info['CAPACIDAD'] - g['sec'].cupo) / salon_info['CAPACIDAD']
                    soft_score -= desperdicio * 100  # factor de escala

        # R_s4: Compactación de la jornada docente
        for (prof, dia), horarios in horario_prof_dia.items():
            if len(horarios) <= 1:
                continue
            # Ordenar por inicio
            horarios.sort()
            for k in range(len(horarios)-1):
                fin_actual = horarios[k][1]
                inicio_sig = horarios[k+1][0]
                hueco = inicio_sig - fin_actual
                if hueco > 120:  # umbral de 2 horas
                    soft_score -= (hueco - 120) / 30  # penalización proporcional

        # Bonus por preferencias de cursos
        for g in ind:
            prof_nombre = g['prof']
            if prof_nombre not in ["GRADUADOS", "TBA"]:
                prof_obj = self.profesores.get(prof_nombre)
                if prof_obj:
                    prior = self._suit_prof(prof_obj, g['sec'])
                    soft_score += prior * 50

        # Fitness: cuanto mayor mejor. Queremos minimizar penalizaciones duras y maximizar soft_score.
        # Convertimos penalty en algo que reduzca fitness drásticamente.
        # Usamos 1/(1+penalty) como base y sumamos soft_score normalizado.
        fitness = 1 / (1 + penalty) + soft_score * 1e-4
        return fitness, conflicts, conflict_details, list(bad_indices)

    def _mutate_gene(self, gene, aggressive_search=False):
        s = gene['sec']
        lista_patrones = PATRONES.get(s.creditos, PATRONES[3])
        
        # Intentar buscar un patrón y bloque que no viole restricciones básicas
        patron_elegido = random.choice(lista_patrones)
        h_ini = random.choice(self.bloques)
        # Intentamos unas cuantas veces encontrar una combinación que cumpla las restricciones institucionales
        for _ in range(20):
            patron_test = random.choice(lista_patrones)
            ini_test = random.choice(self.bloques)
            # Verificar hora universal
            invade = False
            for dia, contrib in patron_test['days'].items():
                if dia in ["Ma", "Ju"]:
                    fin_test = ini_test + int(contrib * 50)
                    if max(ini_test, self.hora_universal[0]) < min(fin_test, self.hora_universal[1]):
                        invade = True
                        break
            if invade:
                continue
            # Verificar intensivos de 3 horas
            if s.creditos == 3:
                for dia, contrib in patron_test['days'].items():
                    if contrib >= 3 and ini_test < 930:
                        invade = True
                        break
            if invade:
                continue
            # Verificar límite operativo
            dentro = True
            for dia, contrib in patron_test['days'].items():
                fin_test = ini_test + int(contrib * 50)
                if fin_test > self.limite_operativo[1] or ini_test < self.limite_operativo[0]:
                    dentro = False
                    break
            if not dentro:
                continue
            patron_elegido = patron_test
            h_ini = ini_test
            break
        
        if s.cands:
            # Elegir profesor con probabilidad sesgada hacia los que tienen menor carga (si es posible)
            # Para simplificar, elegimos aleatoriamente entre los candidatos, pero podemos mejorar
            prof = random.choice(s.cands) if random.random() < 0.8 else "TBA"
        else:
            prof = "TBA"
            
        candidatos_salon = []
        if s.tipo_salon >= 3:
            candidatos_salon = [sl['CODIGO'] for sl in self.salones if sl['TIPO'] == s.tipo_salon and sl['CAPACIDAD'] >= s.cupo]
            if not candidatos_salon: candidatos_salon = [sl['CODIGO'] for sl in self.salones if sl['TIPO'] == s.tipo_salon]
        else:
            candidatos_salon = [sl['CODIGO'] for sl in self.salones if sl['TIPO'] == s.tipo_salon and sl['CAPACIDAD'] >= s.cupo]
            if s.es_fusionable:
                candidatos_salon.extend([sl['CODIGO'] for sl in self.salones if sl['CODIGO'] in self.mega_salones and sl['CAPACIDAD'] >= s.cupo])
                
        candidatos_salon = list(set(candidatos_salon))
        salon = "TBA"
        if candidatos_salon:
            salon = random.choice(candidatos_salon)
        elif aggressive_search and s.tipo_salon < 3:
            backup = [sl['CODIGO'] for sl in self.salones if sl['CAPACIDAD'] >= s.cupo]
            if backup: salon = random.choice(backup)

        return {'sec': s, 'prof': prof, 'salon': salon, 'patron': patron_elegido, 'ini': h_ini}

    def solve(self, pop_size, generations):
        # Población inicial usando construcción priorizada
        poblacion = [self._create_smart_individual() for _ in range(pop_size)]
        bar = st.progress(0)
        status_text = st.empty()

        mejor_ind = None
        mejor_score = -float('inf')
        mejor_conflictos = []

        for gen in range(generations):
            scored = []
            for ind in poblacion:
                fit, conflictos, detalles, bad = self._fitness_detailed(ind)
                scored.append((fit, ind, conflictos, detalles, bad))

            scored.sort(key=lambda x: x[0], reverse=True)
            if scored[0][0] > mejor_score:
                mejor_score = scored[0][0]
                mejor_ind = scored[0][1]
                mejor_conflictos = scored[0][3]

            if gen % 5 == 0 or gen == generations - 1:
                status_text.markdown(f"**🔄 Optimizando Gen {gen+1}/{generations}** | 🏆 Fitness: `{mejor_score:.6f}` | 🚨 Conflictos: `{scored[0][2]}`")
                bar.progress((gen+1)/generations)

            elite_count = max(1, int(pop_size * 0.1))
            elite = [x[1] for x in scored[:elite_count]]
            nueva_gen = elite.copy()

            while len(nueva_gen) < pop_size:
                # Torneo k=3
                t1 = random.sample(scored, 3)
                t2 = random.sample(scored, 3)
                padre1 = max(t1, key=lambda x: x[0])[1]
                padre2 = max(t2, key=lambda x: x[0])[1]
                
                hijo = []
                for i in range(len(padre1)):
                    hijo.append(padre1[i] if random.random() < 0.5 else padre2[i])
                    
                # Mutacion
                pm = 0.05
                for i in range(len(hijo)):
                    if random.random() < pm:
                        hijo[i] = self._mutate_gene(hijo[i], aggressive_search=True)
                        
                nueva_gen.append(hijo)

            poblacion = nueva_gen

        # Reparación Final
        if len(mejor_conflictos) > 0:
            status_text.markdown(f"**🛠️ Aplicando Reparación Final a {len(mejor_conflictos)} conflictos...**")
            mejor_ind, _, _, mejor_conflictos = self._repair_individual(mejor_ind)
            
        return mejor_ind, mejor_conflictos

    def _repair_individual(self, ind):
        for _ in range(150):
            fit, conflictos, detalles, bad = self._fitness_detailed(ind)
            if conflictos == 0:
                break
            for i in bad:
                ind[i] = self._mutate_gene(ind[i], aggressive_search=True)
        return ind, fit, conflictos, detalles

# ==============================================================================
# 4. UI PRINCIPAL (IDÉNTICA)
# ==============================================================================
def main():
    with st.sidebar:
        st.markdown("### $\Sigma$ Configuración")
        zona = st.selectbox("Zona Campus", ["CENTRAL", "PERIFERICA"])
        pop = st.slider("Población", 50, 500, 100)
        gens = st.slider("Generaciones", 50, 500, 100)
        file = st.file_uploader("Subir Protocolo Excel", type=['xlsx'])

    st.markdown(f"### $\Omega$ Condiciones de Zona: {zona}")
    c1, c2, c3 = st.columns(3)
    
    if zona == "CENTRAL":
        h_bloqueo = "10:30 AM - 12:30 PM"
        limites = "07:30 AM - 07:30 PM"
    else:
        h_bloqueo = "10:00 AM - 12:00 PM"
        limites = "07:00 AM - 07:00 PM"
    
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
            with st.spinner("Inicializando Motor Evolutivo Platinum... Evaluando combinaciones..."):
                xls = pd.ExcelFile(file)
                df_cursos = pd.read_excel(xls, 'Cursos')
                df_profes = pd.read_excel(xls, 'Profesores')
                df_salones = pd.read_excel(xls, 'Salones')

                engine = PlatinumEliteEngine(df_cursos, df_profes, df_salones, zona)
                
                start_time = time.time()
                mejor, conflict_list = engine.solve(pop, gens)
                elapsed = time.time() - start_time
                
                st.session_state.elapsed_time = elapsed
                st.session_state.conflicts = conflict_list
                st.session_state.master = pd.DataFrame([{
                    'ID': g['sec'].cod, 
                    'Asignatura': g['sec'].cod.split('-')[0],
                    'Creditos': g['sec'].creditos,
                    'Persona': g['prof'], 
                    'Días': g['patron']['name'], 
                    'Horario': format_horario(g['patron'], g['ini']), 
                    'Salón': g['salon'],
                    'Tipo_Salon': g['sec'].tipo_salon
                } for g in mejor])

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
                st.error(f"⚠️ Se detectaron {len(conflictos)} conflictos o irregularidades. Ajuste iteraciones o revise el Excel.")
                conflictos_unicos = list(set(conflictos))
                for txt in conflictos_unicos:
                    st.markdown(f"- `{txt}`")
            else:
                st.success("✅ 100% Asignación Perfecta. Cero Conflictos. Se respetaron todas las métricas de espacio, carga y Hora Universal.")
                
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
