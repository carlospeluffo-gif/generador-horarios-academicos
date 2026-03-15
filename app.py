import streamlit as st
import pandas as pd
import numpy as np
import random
import io
import time
import math
from datetime import time as dtime
import matplotlib.subplots as plt
import matplotlib.pyplot as plt
from copy import deepcopy

# ==============================================================================
# 1. ESTÉTICA
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
            UPRM MATHEMATICAL OPTIMIZATION ENGINE v9.5 (PRE-ASIGNACIÓN + TABÚ)
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
# 3. MODELO DE DATOS
# ==============================================================================
class Seccion:
    def __init__(self, cod, creditos, cupo, candidatos_raw, tipo_salon, es_ayudantia=False):
        self.cod = str(cod)
        self.creditos = int(creditos)
        self.cupo = int(cupo)
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
        self.prof_preasignado = None  # ¡AQUÍ ESTÁ LA TRAMPA! Se guarda fijo.

class Profesor:
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

# ==============================================================================
# 4. MOTOR DE OPTIMIZACIÓN
# ==============================================================================
class TabuScheduler:
    def __init__(self, df_cursos, df_profes, df_salones, zona):
        self.zona = zona
        
        # Salones
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

        # Profesores
        self.profesores = {}
        if df_profes is not None and not df_profes.empty:
            for _, r in df_profes.iterrows():
                prefs = []
                for col in ['PREF1', 'PREF2', 'PREF3']:
                    val = r.get(col, '')
                    if pd.notnull(val) and str(val).strip().upper() != 'NAN':
                        prefs.append(str(val).strip().upper())
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
                    acepta_grandes=r.get('ACEPTA_GRANDES', 0)
                )
                self.profesores[prof.nombre] = prof

        # Cursos y generación de secciones
        self.secciones = []
        df_cursos.columns = [c.strip().upper() for c in df_cursos.columns]
        cursos_agrupados = {}
        for _, r in df_cursos.iterrows():
            cod_base = str(r['CODIGO']).strip().upper()
            creditos = int(r['CREDITOS'])
            demanda = int(r.get('DEMANDA', 0))
            cupo_tipico = int(r.get('CUPO', '30'))
            candidatos_raw = r.get('CANDIDATOS', '')
            tipo_salon = int(r.get('TIPO_SALON', 1))
            if cod_base not in cursos_agrupados:
                cursos_agrupados[cod_base] = {
                    'creditos': creditos,
                    'demanda': demanda,
                    'cupo_tipico': cupo_tipico,
                    'candidatos': candidatos_raw,
                    'tipo_salon': tipo_salon
                }
            else:
                cursos_agrupados[cod_base]['demanda'] += demanda

        for cod_base, datos in cursos_agrupados.items():
            demanda_total = datos['demanda']
            cupo_tipico = datos['cupo_tipico']
            creditos = datos['creditos']
            candidatos = datos['candidatos']
            tipo_salon = datos['tipo_salon']
            num_secciones = math.ceil(demanda_total / cupo_tipico) if demanda_total > 0 else 1
            estudiantes_por_seccion = [cupo_tipico] * (num_secciones - 1)
            resto = demanda_total - sum(estudiantes_por_seccion)
            estudiantes_por_seccion.append(resto if resto > 0 else cupo_tipico)
            
            for i, cupo in enumerate(estudiantes_por_seccion):
                cod_seccion = f"{cod_base}-{i+1:02d}"
                s = Seccion(cod_seccion, creditos, cupo, candidatos, tipo_salon)
                self.secciones.append(s)

        # ¡NUEVO! Ejecutamos la trampa matemática antes de hacer nada más.
        self._preasignar_profesores_perfectamente()

        # Bloques de 30 minutos
        self.bloques = list(range(420, 1171, 30))  # 7:00 a 19:30
        
        # Restricciones
        if zona == "CENTRAL":
            self.hora_universal = (630, 750)    # 10:30-12:30
            self.limite_operativo = (450, 1170) # 7:30-19:30
        else:
            self.hora_universal = (600, 720)    # 10:00-12:00
            self.limite_operativo = (420, 1140) # 7:00-19:00

        # Construir solución inicial greedy
        self.solucion = self._construir_solucion_greedy()
        self.mejor_solucion = deepcopy(self.solucion)
        self.mejor_costo = self._costo_total(self.solucion)
        self.tabu_list = []
        self.tabu_tenure = 20
        self.historial_costos = [self.mejor_costo]

    # ================== LA TRAMPA MATEMÁTICA ==================
    def _preasignar_profesores_perfectamente(self):
        """Distribuye la carga matemáticamente y prohíbe cambios posteriores."""
        carga_actual = {p: 0.0 for p in self.profesores}
        carga_actual["GRADUADOS"] = 0.0
        
        # Ordenamos secciones de las más difíciles (menos candidatos) a las más fáciles
        secciones_ordenadas = sorted(self.secciones, key=lambda x: len([c for c in x.cands if c in self.profesores]))

        # FASE 1: Asegurar que todos lleguen a su MÍNIMO de carga
        for s in secciones_ordenadas:
            if s.prof_preasignado: continue
            
            cands_validos = [p for p in s.cands if p in self.profesores]
            cands_necesitados = [p for p in cands_validos if carga_actual[p] + s.creditos <= self.profesores[p].carga_min]
            
            if cands_necesitados:
                # Priorizamos al que le falte más para llegar a su mínimo
                cands_necesitados.sort(key=lambda p: carga_actual[p] - self.profesores[p].carga_min)
                elegido = cands_necesitados[0]
                s.prof_preasignado = elegido
                carga_actual[elegido] += s.creditos

        # FASE 2: Llenar hasta llegar al MÁXIMO de carga
        for s in secciones_ordenadas:
            if s.prof_preasignado: continue
            
            cands_validos = [p for p in s.cands if p in self.profesores]
            cands_disponibles = [p for p in cands_validos if carga_actual[p] + s.creditos <= self.profesores[p].carga_max]
            
            if cands_disponibles:
                # Priorizamos al que tenga menos carga actualmente
                cands_disponibles.sort(key=lambda p: carga_actual[p])
                elegido = cands_disponibles[0]
                s.prof_preasignado = elegido
                carga_actual[elegido] += s.creditos

        # FASE 3: Fallbacks (Graduados o forzar al menos cargado)
        for s in secciones_ordenadas:
            if s.prof_preasignado: continue
            
            if "GRADUADOS" in s.cands:
                s.prof_preasignado = "GRADUADOS"
                carga_actual["GRADUADOS"] += s.creditos
            else:
                cands_validos = [p for p in s.cands if p in self.profesores]
                if cands_validos:
                    cands_validos.sort(key=lambda p: carga_actual[p])
                    elegido = cands_validos[0]
                    s.prof_preasignado = elegido
                    carga_actual[elegido] += s.creditos
                else:
                    s.prof_preasignado = "TBA"

    # ================== FUNCIÓN DE COSTO ==================
    def _costo_total(self, sol):
        conflicts = 0
        soft_penalty = 0
        occ_prof = {}
        occ_salon = {}
        carga_prof = {}
        
        for i, asign in enumerate(sol):
            s = asign['seccion']
            prof = asign['profesor']
            salon = asign['salon']
            patron = asign['patron']
            ini = asign['ini']
            
            if prof == "TBA":
                conflicts += 10000
                continue
            if salon == "TBA":
                conflicts += 10000
                continue
            
            salon_info = next((sl for sl in self.salones if sl['CODIGO'] == salon), None)
            if salon_info and salon_info['CAPACIDAD'] < s.cupo:
                conflicts += 10000
                continue
            if salon_info and not (salon in self.mega_salones and s.es_fusionable) and salon_info['TIPO'] != s.tipo_salon:
                conflicts += 10000
                continue
            
            if prof != "GRADUADOS":
                carga_prof[prof] = carga_prof.get(prof, 0) + s.creditos
            
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
                    if clave not in occ_prof:
                        occ_prof[clave] = []
                    for (ini_ex, fin_ex) in occ_prof[clave]:
                        if max(ini, ini_ex) < min(fin, fin_ex):
                            conflicts += 10000
                    occ_prof[clave].append((ini, fin))
                
                clave_s = (salon, dia)
                if clave_s not in occ_salon:
                    occ_salon[clave_s] = []
                for (ini_ex, fin_ex, cupo_ex, fus_ex) in occ_salon[clave_s]:
                    if max(ini, ini_ex) < min(fin, fin_ex):
                        if salon in self.mega_salones and s.es_fusionable and fus_ex:
                            if s.cupo + cupo_ex <= salon_info['CAPACIDAD']:
                                continue
                        conflicts += 10000
                occ_salon[clave_s].append((ini, fin, s.cupo, s.es_fusionable))
            
            if prof != "GRADUADOS" and prof in self.profesores:
                prof_obj = self.profesores[prof]
                prior = prof_obj.prioridad_curso(s.cod.split('-')[0])
                soft_penalty += (1 - prior) * 10
                if prof_obj.compensacion:
                    if s.cupo >= 85 and not prof_obj.acepta_grandes:
                        soft_penalty += 20
                if prof_obj.pref_horas == 'AM' and ini >= 720:
                    soft_penalty += 5
                elif prof_obj.pref_horas == 'PM' and ini < 720:
                    soft_penalty += 5
        
        for prof, carga in carga_prof.items():
            prof_obj = self.profesores.get(prof)
            if prof_obj:
                if carga > prof_obj.carga_max:
                    conflicts += 10000
                if carga < prof_obj.carga_min:
                    conflicts += 10000
        
        return conflicts + soft_penalty

    def _obtener_conflictos(self, sol):
        conflictos_list = []
        occ_prof = {}
        occ_salon = {}
        carga_prof = {}
        
        for i, asign in enumerate(sol):
            s = asign['seccion']
            prof = asign['profesor']
            salon = asign['salon']
            patron = asign['patron']
            ini = asign['ini']
            
            if prof == "TBA":
                conflictos_list.append(f"Sección {s.cod}: profesor TBA")
            if salon == "TBA":
                conflictos_list.append(f"Sección {s.cod}: salón TBA")
            
            salon_info = next((sl for sl in self.salones if sl['CODIGO'] == salon), None)
            if salon_info and salon_info['CAPACIDAD'] < s.cupo:
                conflictos_list.append(f"Sección {s.cod}: salón {salon} capacidad insuficiente ({salon_info['CAPACIDAD']} < {s.cupo})")
            if salon_info and not (salon in self.mega_salones and s.es_fusionable) and salon_info['TIPO'] != s.tipo_salon:
                conflictos_list.append(f"Sección {s.cod}: tipo de salón incorrecto (requiere {s.tipo_salon}, tiene {salon_info['TIPO']})")
            
            if prof != "GRADUADOS":
                carga_prof[prof] = carga_prof.get(prof, 0) + s.creditos
            
            for dia, contrib in patron['days'].items():
                fin = ini + int(contrib * 50)
                if dia in ["Ma", "Ju"] and max(ini, self.hora_universal[0]) < min(fin, self.hora_universal[1]):
                    conflictos_list.append(f"Sección {s.cod}: violación de hora universal el {dia}")
                if s.creditos == 3 and contrib >= 3 and ini < 930:
                    conflictos_list.append(f"Sección {s.cod}: intensivo antes de 3:30 PM")
                if fin > self.limite_operativo[1] or ini < self.limite_operativo[0]:
                    conflictos_list.append(f"Sección {s.cod}: fuera del límite operativo")
                
                if prof != "GRADUADOS":
                    clave = (prof, dia)
                    if clave not in occ_prof:
                        occ_prof[clave] = []
                    for (ini_ex, fin_ex) in occ_prof[clave]:
                        if max(ini, ini_ex) < min(fin, fin_ex):
                            conflictos_list.append(f"Conflicto de profesor {prof} el {dia} entre {mins_to_str(ini)}-{mins_to_str(fin)} y otra clase")
                    occ_prof[clave].append((ini, fin))
                
                clave_s = (salon, dia)
                if clave_s not in occ_salon:
                    occ_salon[clave_s] = []
                for (ini_ex, fin_ex, cupo_ex, fus_ex) in occ_salon[clave_s]:
                    if max(ini, ini_ex) < min(fin, fin_ex):
                        if salon in self.mega_salones and s.es_fusionable and fus_ex:
                            if s.cupo + cupo_ex <= salon_info['CAPACIDAD']:
                                continue
                        conflictos_list.append(f"Conflicto de salón {salon} el {dia} entre {mins_to_str(ini)}-{mins_to_str(fin)} y otra clase")
                occ_salon[clave_s].append((ini, fin, s.cupo, s.es_fusionable))
        
        for prof, carga in carga_prof.items():
            prof_obj = self.profesores.get(prof)
            if prof_obj:
                if carga > prof_obj.carga_max:
                    conflictos_list.append(f"Profesor {prof} excede carga máxima ({carga} > {prof_obj.carga_max})")
                if carga < prof_obj.carga_min:
                    conflictos_list.append(f"Profesor {prof} no alcanza carga mínima ({carga} < {prof_obj.carga_min})")
        
        return conflictos_list

    # ================== CONSTRUCCIÓN GREEDY (MODIFICADA) ==================
    def _construir_solucion_greedy(self):
        sol = [None] * len(self.secciones)
        asignado = [False] * len(self.secciones)
        
        for i, s in enumerate(self.secciones):
            # Usamos SÍ O SÍ al profesor que ya fue pre-asignado matemáticamente.
            prof = getattr(s, 'prof_preasignado', 'TBA')
            exito = self._asignar_seccion(i, prof, sol, asignado)
            if not exito:
                sol[i] = self._crear_asignacion_temporal(s, prof=prof)
                asignado[i] = True
                
        return sol

    def _crear_asignacion_temporal(self, seccion, prof="TBA", salon="TBA", patron=None, ini=None):
        if patron is None:
            patron = random.choice(PATRONES.get(seccion.creditos, PATRONES[3]))
        if ini is None:
            ini = random.choice(self.bloques)
        if salon == "TBA":
            salones_posibles = [sl['CODIGO'] for sl in self.salones if sl['CAPACIDAD'] >= seccion.cupo]
            salon = random.choice(salones_posibles) if salones_posibles else "TBA"
        return {
            'seccion': seccion,
            'profesor': prof,
            'salon': salon,
            'patron': patron,
            'ini': ini
        }

    def _asignar_seccion(self, idx, prof, sol, asignado):
        s = sol[idx]['seccion'] if sol[idx] else self.secciones[idx]
        patrones = PATRONES.get(s.creditos, PATRONES[3])
        random.shuffle(patrones)
        for patron in patrones:
            for dia, contrib in patron['days'].items():
                duracion = contrib * 50
                inicios_posibles = [ini for ini in self.bloques 
                                    if ini >= self.limite_operativo[0] 
                                    and ini + duracion <= self.limite_operativo[1]]
                if not inicios_posibles:
                    continue
                if dia in ["Ma", "Ju"]:
                    inicios_posibles = [ini for ini in inicios_posibles
                                        if not (max(ini, self.hora_universal[0]) < min(ini+duracion, self.hora_universal[1]))]
                if not inicios_posibles:
                    continue
                if s.creditos == 3 and contrib >= 3:
                    inicios_posibles = [ini for ini in inicios_posibles if ini >= 930]
                if not inicios_posibles:
                    continue
                
                salones_posibles = [sl['CODIGO'] for sl in self.salones 
                                    if sl['TIPO'] == s.tipo_salon and sl['CAPACIDAD'] >= s.cupo]
                if not salones_posibles:
                    salones_posibles = [sl['CODIGO'] for sl in self.salones if sl['CAPACIDAD'] >= s.cupo]
                if not salones_posibles:
                    continue
                
                for ini in inicios_posibles:
                    for salon in salones_posibles:
                        conflicto = False
                        for j, asign in enumerate(sol):
                            if asign and asignado[j] and j != idx:
                                if asign['profesor'] == prof:
                                    for dia2, contrib2 in asign['patron']['days'].items():
                                        if dia == dia2:
                                            fin = ini + duracion
                                            fin2 = asign['ini'] + int(contrib2 * 50)
                                            if max(ini, asign['ini']) < min(fin, fin2):
                                                conflicto = True
                                                break
                                if asign['salon'] == salon:
                                    for dia2, contrib2 in asign['patron']['days'].items():
                                        if dia == dia2:
                                            fin = ini + duracion
                                            fin2 = asign['ini'] + int(contrib2 * 50)
                                            if max(ini, asign['ini']) < min(fin, fin2):
                                                if salon in self.mega_salones and s.es_fusionable and asign['seccion'].es_fusionable:
                                                    if s.cupo + asign['seccion'].cupo <= next(sl['CAPACIDAD'] for sl in self.salones if sl['CODIGO']==salon):
                                                        continue
                                                conflicto = True
                                                break
                                if conflicto:
                                    break
                            if conflicto:
                                break
                        if not conflicto:
                            sol[idx] = {
                                'seccion': s,
                                'profesor': prof,
                                'salon': salon,
                                'patron': patron,
                                'ini': ini
                            }
                            asignado[idx] = True
                            return True
        return False

    # ================== OPERADORES TABÚ (MODIFICADOS) ==================
    def _generar_vecinos(self, sol, num_vecinos=3):
        vecinos = []
        indices = list(range(len(sol)))
        random.shuffle(indices)
        for idx in indices[:num_vecinos]:
            for _ in range(2):
                nuevo = deepcopy(sol)
                asign = nuevo[idx]
                s = asign['seccion']
                
                # ¡YA NO SE MUTA EL PROFESOR! Solo Salón y Horario.
                op = random.choice(['salon', 'horario']) 
                
                if op == 'salon':
                    salones_posibles = [sl['CODIGO'] for sl in self.salones if sl['TIPO'] == s.tipo_salon and sl['CAPACIDAD'] >= s.cupo]
                    if not salones_posibles:
                        salones_posibles = [sl['CODIGO'] for sl in self.salones if sl['CAPACIDAD'] >= s.cupo]
                    if salones_posibles:
                        nuevo[idx]['salon'] = random.choice(salones_posibles)
                elif op == 'horario':
                    nuevo[idx]['patron'] = random.choice(PATRONES.get(s.creditos, PATRONES[3]))
                    nuevo[idx]['ini'] = random.choice(self.bloques)
                vecinos.append(nuevo)
        return vecinos

    def _hash_sol(self, sol):
        return hash(tuple((a['seccion'].cod, a['profesor'], a['salon'], a['patron']['name'], a['ini']) for a in sol))

    def optimizar(self, iteraciones=200, bar=None, status_text=None):
        self.iteraciones = iteraciones
        for it in range(iteraciones):
            vecinos = self._generar_vecinos(self.solucion, num_vecinos=3)
            mejor_vecino = None
            mejor_costo_vecino = float('inf')
            
            for vecino in vecinos:
                h = self._hash_sol(vecino)
                if h in self.tabu_list:
                    continue
                costo = self._costo_total(vecino)
                if costo < mejor_costo_vecino:
                    mejor_costo_vecino = costo
                    mejor_vecino = vecino
            
            if mejor_vecino is not None:
                self.solucion = mejor_vecino
                self.tabu_list.append(self._hash_sol(self.solucion))
                if len(self.tabu_list) > self.tabu_tenure:
                    self.tabu_list.pop(0)
                
                if mejor_costo_vecino < self.mejor_costo:
                    self.mejor_costo = mejor_costo_vecino
                    self.mejor_solucion = deepcopy(self.solucion)
            
            self.historial_costos.append(self.mejor_costo)
            
            if it % 10 == 0 or it == iteraciones - 1:
                fitness_val = 1 / (1 + self.mejor_costo) if self.mejor_costo >= 0 else 1.0
                conflictos_aprox = self.mejor_costo // 10000
                if status_text:
                    status_text.markdown(f"**🔄 Iteración {it+1}/{iteraciones}** | Mejor costo: {self.mejor_costo} | Fitness: {fitness_val:.6f} | Conflictos duros aprox: {conflictos_aprox}")
                if bar:
                    bar.progress((it+1)/iteraciones)
        
        return self.mejor_solucion, self.mejor_costo // 10000

# ==============================================================================
# 5. UI PRINCIPAL
# ==============================================================================
def main():
    with st.sidebar:
        st.markdown("### $\Sigma$ Configuración")
        zona = st.selectbox("Zona Campus", ["CENTRAL", "PERIFERICA"])
        iteraciones = st.slider("Iteraciones de Búsqueda", 100, 5000, 200)
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
            with st.spinner("Inicializando Motor (Pre-asignando Cargas y Resolviendo)..."):
                xls = pd.ExcelFile(file)
                df_cursos = pd.read_excel(xls, 'Cursos')
                df_profes = pd.read_excel(xls, 'Profesores')
                df_salones = pd.read_excel(xls, 'Salones')

                scheduler = TabuScheduler(df_cursos, df_profes, df_salones, zona)
                
                start_time = time.time()
                bar = st.progress(0)
                status = st.empty()
                mejor_sol, conflictos = scheduler.optimizar(iteraciones, bar, status)
                elapsed = time.time() - start_time
                
                st.session_state.elapsed_time = elapsed
                st.session_state.conflicts = conflictos
                st.session_state.master = pd.DataFrame([{
                    'ID': a['seccion'].cod, 
                    'Asignatura': a['seccion'].cod.split('-')[0],
                    'Creditos': a['seccion'].creditos,
                    'Persona': a['profesor'], 
                    'Días': a['patron']['name'], 
                    'Horario': format_horario(a['patron'], a['ini']), 
                    'Salón': a['salon'],
                    'Tipo_Salon': a['seccion'].tipo_salon,
                    'Demanda': a['seccion'].cupo
                } for a in mejor_sol])
                
                st.session_state.historial = scheduler.historial_costos
                st.session_state.detailed_conflicts = scheduler._obtener_conflictos(mejor_sol)

    if 'master' in st.session_state:
        st.success(f"✅ Optimización completada en {st.session_state.elapsed_time:.2f} segundos.")
        
        if 'historial' in st.session_state and len(st.session_state.historial) > 0:
            with st.expander("📈 Ver evolución de la optimización"):
                fitness_hist = [1/(1+c) for c in st.session_state.historial]
                fig, ax = plt.subplots(figsize=(10, 4))
                ax.plot(fitness_hist, color='#D4AF37', linewidth=2)
                ax.set_xlabel("Iteración")
                ax.set_ylabel("Fitness (1/(1+costo))")
                ax.set_title("Convergencia del algoritmo Tabú (Fitness)")
                ax.grid(True, alpha=0.3)
                ax.set_facecolor('#111111')
                fig.patch.set_facecolor('#111111')
                ax.tick_params(colors='white')
                ax.xaxis.label.set_color('white')
                ax.yaxis.label.set_color('white')
                ax.title.set_color('white')
                st.pyplot(fig)
        
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
                    
                    dias_semana = ['Lu', 'Ma', 'Mi', 'Ju', 'Vi']
                    carga_dia = {dia: 0 for dia in dias_semana}
                    for _, row in subset.iterrows():
                        patron_nombre = row['Días']
                        for dia in dias_semana:
                            if dia in patron_nombre:
                                carga_dia[dia] += row['Creditos']
                    fig, ax = plt.subplots()
                    ax.bar(carga_dia.keys(), carga_dia.values(), color='#D4AF37')
                    ax.set_xlabel("Día")
                    ax.set_ylabel("Créditos")
                    ax.set_title(f"Carga semanal de {p}")
                    ax.set_facecolor('#111111')
                    fig.patch.set_facecolor('#111111')
                    ax.tick_params(colors='white')
                    ax.xaxis.label.set_color('white')
                    ax.yaxis.label.set_color('white')
                    ax.title.set_color('white')
                    st.pyplot(fig)
            
            with f2:
                lista_cursos = sorted(df_master['Asignatura'].unique())
                if lista_cursos:
                    c = st.selectbox("Seleccionar Curso", lista_cursos)
                    subset = df_master[df_master['Asignatura'] == c]
                    st.table(subset[['ID', 'Persona', 'Días', 'Horario', 'Salón']])
                    
                    dias_semana = ['Lu', 'Ma', 'Mi', 'Ju', 'Vi']
                    secciones_dia = {dia: 0 for dia in dias_semana}
                    for _, row in subset.iterrows():
                        patron_nombre = row['Días']
                        for dia in dias_semana:
                            if dia in patron_nombre:
                                secciones_dia[dia] += 1
                    fig, ax = plt.subplots()
                    ax.bar(secciones_dia.keys(), secciones_dia.values(), color='#D4AF37')
                    ax.set_xlabel("Día")
                    ax.set_ylabel("Número de secciones")
                    ax.set_title(f"Secciones del curso {c} por día")
                    ax.set_facecolor('#111111')
                    fig.patch.set_facecolor('#111111')
                    ax.tick_params(colors='white')
                    ax.xaxis.label.set_color('white')
                    ax.yaxis.label.set_color('white')
                    ax.title.set_color('white')
                    st.pyplot(fig)
            
            with f3:
                lista_salones = sorted(df_master['Salón'].unique())
                if lista_salones:
                    sl = st.selectbox("Seleccionar Salón", lista_salones)
                    subset = df_master[df_master['Salón'] == sl]
                    st.table(subset[['ID', 'Asignatura', 'Persona', 'Días', 'Horario']])
                    
                    dias_semana = ['Lu', 'Ma', 'Mi', 'Ju', 'Vi']
                    ocupacion = {dia: 0 for dia in dias_semana}
                    for _, row in subset.iterrows():
                        patron_nombre = row['Días']
                        for dia in dias_semana:
                            if dia in patron_nombre:
                                ocupacion[dia] += 1
                    fig, ax = plt.subplots()
                    ax.bar(ocupacion.keys(), ocupacion.values(), color='#D4AF37')
                    ax.set_xlabel("Día")
                    ax.set_ylabel("Número de clases")
                    ax.set_title(f"Ocupación del salón {sl}")
                    ax.set_facecolor('#111111')
                    fig.patch.set_facecolor('#111111')
                    ax.tick_params(colors='white')
                    ax.xaxis.label.set_color('white')
                    ax.yaxis.label.set_color('white')
                    ax.title.set_color('white')
                    st.pyplot(fig)
            
            with f4:
                st.markdown("#### Clases asignadas a Estudiantes Graduados")
                subset = df_master[df_master['Persona'] == "GRADUADOS"]
                st.table(subset[['ID', 'Asignatura', 'Días', 'Horario', 'Salón']])
                st.metric("Total Secciones de Graduados", len(subset))
                
        with t3:
            conflictos = st.session_state.conflicts
            if conflictos > 0:
                st.error(f"⚠️ Se detectaron aproximadamente {conflictos} conflictos duros. Aumente iteraciones o revise los datos.")
                if 'detailed_conflicts' in st.session_state and st.session_state.detailed_conflicts:
                    st.markdown("**Detalle de conflictos:**")
                    for conf in st.session_state.detailed_conflicts:
                        st.write(f"- {conf}")
                else:
                    st.write("No se pudo generar el detalle.")
            else:
                st.success("✅ 100% Asignación Perfecta. Cero Conflictos. Se respetaron todas las métricas de espacio, carga y Hora Universal.")
                
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
