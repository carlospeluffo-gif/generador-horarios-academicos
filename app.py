import streamlit as st
import pandas as pd
import numpy as np
import random
import io
import time
import math
from datetime import time as dtime

# ==============================================================================
# 1. ESTÉTICA PLATINUM ELITE (IDENTICA A LA ORIGINAL)
# ==============================================================================
st.set_page_config(page_title="UPRM Scheduler Platinum AI v8", page_icon="🏛️", layout="wide")

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
            UPRM MATHEMATICAL OPTIMIZATION ENGINE v8.0 (STRICT ENFORCEMENT + TRAMPA)
        </p>
    </div>
    <div class="abstract-icon">∞</div>
</div>
""", unsafe_allow_html=True)

st.latex(r"\blacksquare \quad \text{SISTEMA DE PLANIFICACIÓN ACADÉMICA OPTIMIZADA - TESIS MASTER} \quad \blacksquare")

# ==============================================================================
# 2. UTILIDADES Y TABLA DE PATRONES (IGUAL)
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

# TABLA DE COMPENSACIÓN (exactamente de tu tesis)
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
# 3. MODELO DE DATOS (CORREGIDO)
# ==============================================================================
class SeccionData:
    def __init__(self, cod, creditos, cupo, candidatos_raw, tipo_salon, es_ayudantia=False):
        self.cod = str(cod)
        self.creditos = int(creditos)
        self.cupo = int(cupo)  # capacidad física del salón (máximo de estudiantes)
        self.demanda_asignada = cupo  # por defecto, la demanda es igual a la capacidad (se puede ajustar después)
        if isinstance(candidatos_raw, list):
            self.cands = [c.strip().upper() for c in candidatos_raw if c.strip()]
        else:
            self.cands = [c.strip().upper() for c in str(candidatos_raw).split(',') if c.strip() and str(c).upper() != 'NAN']
        try:
            self.tipo_salon = int(float(str(tipo_salon)))
        except:
            self.tipo_salon = 1
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
        # Manejo correcto de bloqueo_dias
        self.bloqueo_dias = set()
        if isinstance(bloqueo_dias, str) and bloqueo_dias.strip():
            # Eliminar espacios y dividir por comas
            for d in bloqueo_dias.split(','):
                d_clean = d.strip().title()
                if d_clean:
                    self.bloqueo_dias.add(d_clean)
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

# ==============================================================================
# 4. MOTOR GENÉTICO CON TRAMPA DE REPARACIÓN FORZADA
# ==============================================================================
class PlatinumEliteEngine:
    def __init__(self, df_cursos, df_profes, df_salones, zona):
        self.zona = zona
        
        # ===== Salones =====
        df_salones.columns = [c.strip().upper() for c in df_salones.columns]
        self.salones = []
        self.mega_salones = set()
        for _, r in df_salones.iterrows():
            codigo = str(r['CODIGO']).strip().upper()
            try:
                cap = int(r['CAPACIDAD'])
            except:
                cap = 25
            try:
                tipo = int(r['TIPO'])
            except:
                tipo = 1
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

        # ===== Cursos y generación de secciones según demanda =====
        self.oferta = []
        df_cursos.columns = [c.strip().upper() for c in df_cursos.columns]
        
        # Agrupar por curso base para calcular secciones necesarias
        cursos_agrupados = {}
        for _, r in df_cursos.iterrows():
            codigo_base = str(r['CODIGO']).strip().upper()
            creditos = int(r['CREDITOS'])
            demanda = int(r.get('DEMANDA', 0))
            cupo_tipico = int(r.get('CUPO', '30'))  # capacidad típica de una sección
            candidatos_raw = r.get('CANDIDATOS', '')
            tipo_salon = int(r.get('TIPO_SALON', 1))
            
            if codigo_base not in cursos_agrupados:
                cursos_agrupados[codigo_base] = {
                    'creditos': creditos,
                    'demanda': demanda,
                    'cupo_tipico': cupo_tipico,
                    'candidatos': candidatos_raw,
                    'tipo_salon': tipo_salon
                }
            else:
                # Si hay múltiples filas para el mismo curso, sumamos demandas
                cursos_agrupados[codigo_base]['demanda'] += demanda

        # Para cada curso base, generar las secciones necesarias
        for cod_base, datos in cursos_agrupados.items():
            demanda_total = datos['demanda']
            cupo_tipico = datos['cupo_tipico']
            creditos = datos['creditos']
            candidatos = datos['candidatos']
            tipo_salon = datos['tipo_salon']
            
            # Calcular número de secciones: ceil(demanda / cupo_tipico)
            num_secciones = math.ceil(demanda_total / cupo_tipico) if demanda_total > 0 else 1
            # Distribuir estudiantes entre secciones (última puede tener menos)
            estudiantes_por_seccion = [cupo_tipico] * (num_secciones - 1)
            resto = demanda_total - sum(estudiantes_por_seccion)
            estudiantes_por_seccion.append(resto if resto > 0 else cupo_tipico)
            
            for i, cupo in enumerate(estudiantes_por_seccion):
                cod_seccion = f"{cod_base}-{i+1:02d}"
                seccion = SeccionData(cod_seccion, creditos, cupo, candidatos, tipo_salon)
                seccion.demanda_asignada = cupo
                self.oferta.append(seccion)

        # Bloques de 30 minutos
        self.bloques = list(range(420, 1171, 30))  # 7:00 AM a 7:30 PM
        
        # Restricciones institucionales
        if zona == "CENTRAL":
            self.hora_universal = (630, 750)    # 10:30-12:30
            self.limite_operativo = (450, 1170) # 7:30-19:30
        else:
            self.hora_universal = (600, 720)    # 10:00-12:00
            self.limite_operativo = (420, 1140) # 7:00-19:00

    def _es_bloqueo_activo(self, prof, dia, ini, fin):
        if not prof.bloqueo_dias or dia not in prof.bloqueo_dias:
            return False
        if prof.bloqueo_ini is None or prof.bloqueo_fin is None:
            return False
        return max(ini, prof.bloqueo_ini) < min(fin, prof.bloqueo_fin)

    def _suit_prof(self, prof, seccion):
        prioridad = prof.prioridad_curso(seccion.cod.split('-')[0])
        if seccion.demanda_asignada >= 85:
            return 2.0 * prioridad if prof.acepta_grandes == 1 else 0.0
        return prioridad

    def _create_smart_individual(self):
        """Inicialización heurística mejorada (rápida)"""
        ind = []
        occ_prof = {}
        occ_salon = {}
        carga_prof = {}
        
        # Ordenar secciones por demanda descendente y luego por candidatos únicos
        oferta_ordenada = sorted(self.oferta, key=lambda x: (-x.demanda_asignada, -len(x.cands)))
        
        for s in oferta_ordenada:
            candidatos = s.cands if s.cands else []
            valid_profs = []
            for p in candidatos:
                if p == "GRADUADOS":
                    valid_profs.append(p)
                    continue
                prof_obj = self.profesores.get(p)
                if prof_obj:
                    if carga_prof.get(p, 0) + s.creditos <= prof_obj.carga_max:
                        valid_profs.append(p)
            
            prof = "TBA"
            if valid_profs:
                # Elegir el que tenga menor carga actual
                valid_profs.sort(key=lambda x: carga_prof.get(x, 0) if x != "GRADUADOS" else 0)
                prof = valid_profs[0]
            elif candidatos:
                prof = random.choice(candidatos)
            
            if prof != "TBA" and prof != "GRADUADOS":
                carga_prof[prof] = carga_prof.get(prof, 0) + s.creditos

            lista_patrones = PATRONES.get(s.creditos, PATRONES[3])
            
            # Posibles salones: que cumplan tipo y capacidad
            candidatos_salon = [sl['CODIGO'] for sl in self.salones if sl['TIPO'] == s.tipo_salon and sl['CAPACIDAD'] >= s.demanda_asignada]
            if not candidatos_salon:
                candidatos_salon = [sl['CODIGO'] for sl in self.salones if sl['CAPACIDAD'] >= s.demanda_asignada]
            if not candidatos_salon:
                candidatos_salon = [sl['CODIGO'] for sl in self.salones]
            
            best_patron = random.choice(lista_patrones)
            best_ini = random.choice(self.bloques)
            best_salon = random.choice(candidatos_salon) if candidatos_salon else "TBA"
            
            # Buscar una asignación sin conflictos
            for _ in range(30):
                pat_test = random.choice(lista_patrones)
                ini_test = random.choice(self.bloques)
                
                # Verificar hora universal
                invade_univ = False
                for dia, contrib in pat_test['days'].items():
                    if dia in ["Ma", "Ju"]:
                        fin_test = ini_test + int(contrib * 50)
                        if max(ini_test, self.hora_universal[0]) < min(fin_test, self.hora_universal[1]):
                            invade_univ = True
                            break
                if invade_univ:
                    continue
                
                # Verificar intensivos
                if s.creditos == 3:
                    for dia, contrib in pat_test['days'].items():
                        if contrib >= 3 and ini_test < 930:
                            invade_univ = True
                            break
                    if invade_univ:
                        continue
                
                # Verificar conflicto profesor
                prof_overlap = False
                if prof != "TBA" and prof != "GRADUADOS":
                    for dia, contrib in pat_test['days'].items():
                        fin_test = ini_test + int(contrib * 50)
                        for (ex_ini, ex_fin) in occ_prof.get((prof, dia), []):
                            if max(ini_test, ex_ini) < min(fin_test, ex_fin):
                                prof_overlap = True
                                break
                        if prof_overlap:
                            break
                if prof_overlap:
                    continue
                
                # Verificar conflicto salón
                random.shuffle(candidatos_salon)
                for sal_test in candidatos_salon:
                    room_overlap = False
                    for dia, contrib in pat_test['days'].items():
                        fin_test = ini_test + int(contrib * 50)
                        for (ex_ini, ex_fin, _, _) in occ_salon.get((sal_test, dia), []):
                            if max(ini_test, ex_ini) < min(fin_test, ex_fin):
                                room_overlap = True
                                break
                        if room_overlap:
                            break
                    if not room_overlap:
                        best_patron = pat_test
                        best_ini = ini_test
                        best_salon = sal_test
                        break
                if not room_overlap:
                    break
            
            ind.append({'sec': s, 'prof': prof, 'salon': best_salon, 'patron': best_patron, 'ini': best_ini})
            
            if prof != "TBA" and prof != "GRADUADOS":
                for dia, contrib in best_patron['days'].items():
                    occ_prof.setdefault((prof, dia), []).append((best_ini, best_ini + int(contrib * 50)))
            if best_salon != "TBA":
                for dia, contrib in best_patron['days'].items():
                    occ_salon.setdefault((best_salon, dia), []).append((best_ini, best_ini + int(contrib * 50), s.demanda_asignada, s.es_fusionable))
                    
        return ind

    def _fitness_detailed(self, ind):
        """Calcula fitness y detalles de conflictos (igual que el original)"""
        penalty = 0
        conflicts = 0
        conflict_details = []
        bad_indices = set()
        soft_score = 0.0

        occ_salon = {}
        occ_prof = {}
        carga_prof = {}
        compensaciones = {}

        for i, g in enumerate(ind):
            sec = g['sec']
            prof_nombre = g['prof']
            salon = g['salon']
            patron = g['patron']
            ini = g['ini']

            # ===== Duras =====
            if prof_nombre == "TBA":
                penalty += 10000
                conflicts += 1
                conflict_details.append(f"[{sec.cod}] Profesor TBA")
                bad_indices.add(i)
                continue
            if salon == "TBA":
                penalty += 10000
                conflicts += 1
                conflict_details.append(f"[{sec.cod}] Salón TBA")
                bad_indices.add(i)
                continue
            if prof_nombre != "GRADUADOS" and prof_nombre not in sec.cands:
                penalty += 10000
                conflicts += 1
                conflict_details.append(f"[{sec.cod}] Profesor {prof_nombre} no elegible")
                bad_indices.add(i)
                continue

            # Capacidad
            salon_info = next((s for s in self.salones if s['CODIGO'] == salon), None)
            if salon_info:
                if salon_info['CAPACIDAD'] < sec.demanda_asignada:
                    penalty += 10000
                    conflicts += 1
                    conflict_details.append(f"[{sec.cod}] Sobrecupo en {salon} (cap {salon_info['CAPACIDAD']} < demanda {sec.demanda_asignada})")
                    bad_indices.add(i)
                    continue
                if not (salon in self.mega_salones and sec.es_fusionable) and salon_info['TIPO'] != sec.tipo_salon:
                    penalty += 10000
                    conflicts += 1
                    conflict_details.append(f"[{sec.cod}] Tipo de salón erróneo (requerido {sec.tipo_salon}, actual {salon_info['TIPO']})")
                    bad_indices.add(i)
                    continue

            # Acumular carga
            if prof_nombre != "GRADUADOS":
                carga_prof[prof_nombre] = carga_prof.get(prof_nombre, 0) + sec.creditos

            prof_obj = self.profesores.get(prof_nombre)

            # Por cada día
            for dia, contrib in patron['days'].items():
                fin = ini + int(contrib * 50)
                rango = (ini, fin)

                # Hora universal
                if dia in ["Ma", "Ju"]:
                    if max(ini, self.hora_universal[0]) < min(fin, self.hora_universal[1]):
                        penalty += 10000
                        conflicts += 1
                        conflict_details.append(f"[{sec.cod}] Invade hora universal el {dia}")
                        bad_indices.add(i)

                # Bloqueo profesor
                if prof_obj and prof_nombre != "GRADUADOS":
                    if self._es_bloqueo_activo(prof_obj, dia, ini, fin):
                        penalty += 10000
                        conflicts += 1
                        conflict_details.append(f"[{sec.cod}] {prof_nombre} en hora de bloqueo")
                        bad_indices.add(i)

                # Solapamiento profesor
                if prof_nombre != "GRADUADOS":
                    pk = (prof_nombre, dia)
                    if pk not in occ_prof:
                        occ_prof[pk] = []
                    for (ini_ex, fin_ex) in occ_prof[pk]:
                        if max(rango[0], ini_ex) < min(rango[1], fin_ex):
                            penalty += 10000
                            conflicts += 1
                            conflict_details.append(f"[{sec.cod}] {prof_nombre} solapado el {dia}")
                            bad_indices.add(i)
                            break
                    occ_prof[pk].append(rango)

                # Solapamiento salón
                sk = (salon, dia)
                if sk not in occ_salon:
                    occ_salon[sk] = []
                for (ini_ex, fin_ex, cupo_ex, fusionable_ex) in occ_salon[sk]:
                    if max(rango[0], ini_ex) < min(rango[1], fin_ex):
                        if salon in self.mega_salones and sec.es_fusionable and fusionable_ex:
                            if (sec.demanda_asignada + cupo_ex) <= salon_info['CAPACIDAD']:
                                continue
                        penalty += 10000
                        conflicts += 1
                        conflict_details.append(f"[{sec.cod}] Salón {salon} solapado el {dia}")
                        bad_indices.add(i)
                        break
                occ_salon[sk].append((ini, fin, sec.demanda_asignada, sec.es_fusionable))

            # Soft score
            if prof_nombre != "GRADUADOS" and prof_obj:
                prior = self._suit_prof(prof_obj, sec)
                soft_score += prior * 10
                if prof_obj.pref_dias:
                    dias_patron = set(patron['days'].keys())
                    dias_pref = set(prof_obj.pref_dias.replace(' ', '').split(','))
                    if dias_patron & dias_pref:
                        soft_score += 5
                if prof_obj.pref_horas in ('AM', 'PM'):
                    hora_media = ini + 25
                    if prof_obj.pref_horas == 'AM' and hora_media < 720:
                        soft_score += 5
                    elif prof_obj.pref_horas == 'PM' and hora_media >= 720:
                        soft_score += 5
                if prof_obj.compensacion:
                    comp = calcular_compensacion(sec.creditos, sec.demanda_asignada)
                    soft_score += comp * 2

        # Carga máxima y mínima
        for prof_nombre, carga in carga_prof.items():
            prof_obj = self.profesores.get(prof_nombre)
            if prof_obj:
                if carga > prof_obj.carga_max:
                    penalty += 10000
                    conflicts += 1
                    conflict_details.append(f"Profesor {prof_nombre} sobrecarga de créditos ({carga} > {prof_obj.carga_max})")
                    for idx_g, g_val in enumerate(ind):
                        if g_val['prof'] == prof_nombre:
                            bad_indices.add(idx_g)
                elif carga < prof_obj.carga_min and prof_obj.carga_min > 0:
                    penalty += 1000  # penalización menor por no cumplir mínimo
                    conflict_details.append(f"Profesor {prof_nombre} no cumple carga mínima ({carga} < {prof_obj.carga_min})")

        fitness = 1 / (1 + max(0, penalty)) + soft_score * 1e-6
        return fitness, conflicts, conflict_details, list(bad_indices)

    def _mutate_gene(self, gene, aggressive_search=False):
        s = gene['sec']
        lista_patrones = PATRONES.get(s.creditos, PATRONES[3])
        
        # Buscar patrón que no viole hora universal
        patron_elegido = random.choice(lista_patrones)
        h_ini = random.choice(self.bloques)
        for _ in range(10):
            patron_test = random.choice(lista_patrones)
            ini_test = random.choice(self.bloques)
            invade = False
            for dia, contrib in patron_test['days'].items():
                if dia in ["Ma", "Ju"]:
                    fin_test = ini_test + int(contrib * 50)
                    if max(ini_test, self.hora_universal[0]) < min(fin_test, self.hora_universal[1]):
                        invade = True
                        break
            if s.creditos == 3:
                for dia, contrib in patron_test['days'].items():
                    if contrib >= 3 and ini_test < 930:
                        invade = True
                        break
            if not invade:
                patron_elegido = patron_test
                h_ini = ini_test
                break
        
        if s.cands:
            prof = random.choice(s.cands) if random.random() < 0.8 else "TBA"
        else:
            prof = "TBA"
            
        candidatos_salon = []
        # Salones que cumplan tipo y capacidad
        for sl in self.salones:
            if sl['TIPO'] == s.tipo_salon and sl['CAPACIDAD'] >= s.demanda_asignada:
                candidatos_salon.append(sl['CODIGO'])
        if not candidatos_salon:
            for sl in self.salones:
                if sl['CAPACIDAD'] >= s.demanda_asignada:
                    candidatos_salon.append(sl['CODIGO'])
        if not candidatos_salon:
            candidatos_salon = [sl['CODIGO'] for sl in self.salones]
        candidatos_salon = list(set(candidatos_salon))
        salon = "TBA"
        if candidatos_salon:
            salon = random.choice(candidatos_salon)
        elif aggressive_search:
            backup = [sl['CODIGO'] for sl in self.salones if sl['CAPACIDAD'] >= s.demanda_asignada]
            if backup:
                salon = random.choice(backup)

        return {'sec': s, 'prof': prof, 'salon': salon, 'patron': patron_elegido, 'ini': h_ini}

    # ==========================================================================
    # TRAMPA: REPARACIÓN FORZADA (BUSCA FACTIBILIDAD A TODA COSTA)
    # ==========================================================================
    def _force_feasible(self, ind):
        """
        Intenta reparar un individuo conflictivo reasignando las secciones problemáticas
        una por una con un algoritmo voraz que prioriza la factibilidad.
        Si es necesario, permite sobrecarga de profesores (con penalización) o asigna TBA.
        """
        # Identificar las secciones conflictivas
        _, _, conflict_details, bad_indices = self._fitness_detailed(ind)
        if not bad_indices:
            return ind  # ya es factible
        
        # Crear una copia del individuo
        nuevo = [copy.deepcopy(g) for g in ind]
        
        # Reconstruir ocupaciones sin las secciones conflictivas
        occ_prof = {}
        occ_salon = {}
        carga_prof = {}
        
        # Primero, añadir todas las secciones no conflictivas
        for i, g in enumerate(nuevo):
            if i in bad_indices:
                continue
            sec = g['sec']
            prof = g['prof']
            salon = g['salon']
            patron = g['patron']
            ini = g['ini']
            if prof not in ["GRADUADOS", "TBA"]:
                carga_prof[prof] = carga_prof.get(prof, 0) + sec.creditos
                for dia, contrib in patron['days'].items():
                    fin = ini + int(contrib * 50)
                    occ_prof.setdefault((prof, dia), []).append((ini, fin))
            if salon != "TBA":
                for dia, contrib in patron['days'].items():
                    fin = ini + int(contrib * 50)
                    occ_salon.setdefault((salon, dia), []).append((ini, fin, sec.demanda_asignada, sec.es_fusionable))
        
        # Ahora reasignar las conflictivas una por una
        for i in bad_indices:
            g = nuevo[i]
            sec = g['sec']
            
            # Buscar una asignación factible
            asignado = False
            
            # Posibles profesores (todos los candidatos, y TBA como último recurso)
            candidatos_prof = sec.cands.copy() if sec.cands else []
            candidatos_prof.append("TBA")
            # Ordenar: primero los que no excedan carga, luego GRADUADOS, luego TBA
            def prioridad_prof(p):
                if p == "TBA":
                    return 2
                if p == "GRADUADOS":
                    return 1
                prof_obj = self.profesores.get(p)
                if prof_obj:
                    # Permitir sobrecarga temporalmente (pero preferimos los que no sobrecargan)
                    if carga_prof.get(p, 0) + sec.creditos <= prof_obj.carga_max:
                        return 0
                    else:
                        return 0.5  # permitido pero menos prioritario
                return 3
            candidatos_prof.sort(key=prioridad_prof)
            
            # Patrones posibles
            patrones = PATRONES.get(sec.creditos, PATRONES[3])
            random.shuffle(patrones)
            
            # Salones posibles (todos los que cumplan capacidad)
            salones_posibles = [s['CODIGO'] for s in self.salones if s['CAPACIDAD'] >= sec.demanda_asignada]
            if not salones_posibles:
                salones_posibles = [s['CODIGO'] for s in self.salones]
            random.shuffle(salones_posibles)
            
            # Búsqueda exhaustiva
            for prof in candidatos_prof:
                for patron in patrones:
                    for ini in self.bloques:
                        # Verificar restricciones institucionales
                        invade = False
                        for dia, contrib in patron['days'].items():
                            fin = ini + int(contrib * 50)
                            if dia in ["Ma", "Ju"]:
                                if max(ini, self.hora_universal[0]) < min(fin, self.hora_universal[1]):
                                    invade = True
                                    break
                            if sec.creditos == 3 and contrib >= 3 and ini < 930:
                                invade = True
                                break
                            if fin > self.limite_operativo[1] or ini < self.limite_operativo[0]:
                                invade = True
                                break
                        if invade:
                            continue
                        
                        for salon in salones_posibles:
                            # Verificar conflictos
                            conflicto = False
                            for dia, contrib in patron['days'].items():
                                fin = ini + int(contrib * 50)
                                # Profesor
                                if prof not in ["GRADUADOS", "TBA"]:
                                    for (ini_ex, fin_ex) in occ_prof.get((prof, dia), []):
                                        if max(ini, ini_ex) < min(fin, fin_ex):
                                            conflicto = True
                                            break
                                    if conflicto:
                                        break
                                # Salón
                                for (ini_ex, fin_ex, cupo_ex, fus_ex) in occ_salon.get((salon, dia), []):
                                    if max(ini, ini_ex) < min(fin, fin_ex):
                                        # Verificar fusión
                                        salon_info = next(s for s in self.salones if s['CODIGO'] == salon)
                                        if salon in self.mega_salones and sec.es_fusionable and fus_ex:
                                            if sec.demanda_asignada + cupo_ex <= salon_info['CAPACIDAD']:
                                                continue
                                        conflicto = True
                                        break
                                if conflicto:
                                    break
                            
                            if not conflicto:
                                # Asignación encontrada
                                nuevo[i]['prof'] = prof
                                nuevo[i]['salon'] = salon
                                nuevo[i]['patron'] = patron
                                nuevo[i]['ini'] = ini
                                # Actualizar ocupaciones
                                if prof not in ["GRADUADOS", "TBA"]:
                                    carga_prof[prof] = carga_prof.get(prof, 0) + sec.creditos
                                    for dia, contrib in patron['days'].items():
                                        fin = ini + int(contrib * 50)
                                        occ_prof.setdefault((prof, dia), []).append((ini, fin))
                                if salon != "TBA":
                                    for dia, contrib in patron['days'].items():
                                        fin = ini + int(contrib * 50)
                                        occ_salon.setdefault((salon, dia), []).append((ini, fin, sec.demanda_asignada, sec.es_fusionable))
                                asignado = True
                                break
                        if asignado:
                            break
                    if asignado:
                        break
            if not asignado:
                # No se pudo asignar, dejar como estaba (seguirá en conflicto)
                pass
        
        return nuevo

    def solve(self, pop_size, generations):
        poblacion = [self._create_smart_individual() for _ in range(pop_size)]
        bar = st.progress(0)
        status_text = st.empty()

        mejor_ind = None
        mejor_score = -float('inf')
        mejor_conflictos = []
        mejor_detalles = []

        for gen in range(generations):
            scored = []
            for ind in poblacion:
                fit, conflictos, detalles, bad = self._fitness_detailed(ind)
                scored.append((fit, ind, conflictos, detalles, bad))

            scored.sort(key=lambda x: x[0], reverse=True)
            if scored[0][0] > mejor_score:
                mejor_score = scored[0][0]
                mejor_ind = scored[0][1]
                mejor_conflictos = scored[0][2]
                mejor_detalles = scored[0][3]

            if gen % 5 == 0 or gen == generations - 1:
                status_text.markdown(f"**🔄 Optimizando Gen {gen+1}/{generations}** | 🏆 Fitness: `{mejor_score:.6f}` | 🚨 Conflictos: `{scored[0][2]}`")
                bar.progress((gen+1)/generations)

            elite_count = max(1, int(pop_size * 0.1))
            elite = [x[1] for x in scored[:elite_count]]
            nueva_gen = elite.copy()

            while len(nueva_gen) < pop_size:
                t1 = random.sample(scored, 3)
                t2 = random.sample(scored, 3)
                padre1 = max(t1, key=lambda x: x[0])[1]
                padre2 = max(t2, key=lambda x: x[0])[1]
                
                hijo = []
                for i in range(len(padre1)):
                    hijo.append(padre1[i] if random.random() < 0.5 else padre2[i])
                    
                pm = 0.05
                for i in range(len(hijo)):
                    if random.random() < pm:
                        hijo[i] = self._mutate_gene(hijo[i], aggressive_search=True)
                        
                nueva_gen.append(hijo)

            poblacion = nueva_gen

        # Reparación final
        if mejor_conflictos > 0:
            status_text.markdown(f"**🛠️ Aplicando Reparación Final a {mejor_conflictos} conflictos...**")
            mejor_ind = self._force_feasible(mejor_ind)
            # Volver a evaluar
            fit, conflictos, detalles, bad = self._fitness_detailed(mejor_ind)
            mejor_conflictos = conflictos
            mejor_detalles = detalles
            
        return mejor_ind, mejor_detalles

# ==============================================================================
# 5. UI PRINCIPAL (EXACTAMENTE IGUAL A LA ORIGINAL)
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
    
    h_bloqueo = "10:30 AM - 12:30 PM" if zona == "CENTRAL" else "10:00 AM - 12:00 PM"
    limites = "07:30 AM - 07:00 PM" if zona == "CENTRAL" else "07:00 AM - 07:00 PM"
    
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
                    'Tipo_Salon': g['sec'].tipo_salon,
                    'Demanda': g['sec'].demanda_asignada
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
                # Mostrar detalles en un expander
                with st.expander("Ver detalles de conflictos"):
                    for txt in conflictos:
                        st.markdown(f"- `{txt}`")
            else:
                st.success("✅ 100% Asignación Perfecta. Cero Conflictos. Se respetaron todas las métricas de espacio, carga y Hora Universal.")
                
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
