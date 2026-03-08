import streamlit as st
import pandas as pd
import numpy as np
import random
import io
import time
import re
import math
from datetime import time as dtime

# ==============================================================================
# 1. ESTÉTICA PLATINUM ELITE (INTACTA)
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
            UPRM MATHEMATICAL OPTIMIZATION ENGINE v8.0 (STRICT ENFORCEMENT)
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
    """Convierte hora en formato 'HH:MM AM/PM' a minutos desde medianoche."""
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
# 3. MOTOR IA (PLATINUM ENGINE V8.0)
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

        # ===== Cursos y generación de secciones =====
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

        self.bloques = list(range(420, 1141, 30))  # 7:00 AM a 7:00 PM
        self.h_univ = (630, 750) if zona == "CENTRAL" else (600, 720) 

    def _es_bloqueo_activo(self, prof, dia, ini, fin):
        if not prof.bloqueo_dias or dia not in prof.bloqueo_dias: return False
        if prof.bloqueo_ini is None or prof.bloqueo_fin is None: return False
        return max(ini, prof.bloqueo_ini) < min(fin, prof.bloqueo_fin)

    def _suit_prof(self, prof, seccion):
        prioridad = prof.prioridad_curso(seccion.cod.split('-')[0])
        if seccion.cupo >= 85:
            return 2.0 * prioridad if prof.acepta_grandes == 1 else 0.0
        return prioridad

    def _create_smart_individual(self):
        """ Inicialización Heurística para arrancar con casi 0 conflictos """
        ind = []
        occ_prof = {}
        occ_salon = {}
        carga_prof = {}
        
        # Ordenamos las secciones por tamaño (las más difíciles primero)
        oferta_ordenada = sorted(self.oferta, key=lambda x: x.cupo, reverse=True)
        
        for s in oferta_ordenada:
            # 1. Asignar Profesor inteligentemente
            candidatos = s.cands if s.cands else []
            valid_profs = []
            for p in candidatos:
                if p == "GRADUADOS":
                    valid_profs.append(p)
                    continue
                prof_obj = self.profesores.get(p)
                if prof_obj:
                    # Filtro inteligente para no sobrecargar desde el inicio
                    if carga_prof.get(p, 0) + s.creditos <= prof_obj.carga_max:
                        valid_profs.append(p)
            
            prof = "TBA"
            if valid_profs: prof = random.choice(valid_profs)
            elif candidatos: prof = random.choice(candidatos)
            
            if prof != "TBA" and prof != "GRADUADOS":
                carga_prof[prof] = carga_prof.get(prof, 0) + s.creditos

            # 2. Asignar Patrón, Bloque y Salón sin que choquen
            lista_patrones = PATRONES.get(s.creditos, PATRONES[3])
            
            candidatos_salon = [sl['CODIGO'] for sl in self.salones if sl['TIPO'] == s.tipo_salon and sl['CAPACIDAD'] >= s.cupo]
            if not candidatos_salon: candidatos_salon = [sl['CODIGO'] for sl in self.salones]
            
            best_patron = random.choice(lista_patrones)
            best_ini = random.choice(self.bloques)
            best_salon = random.choice(candidatos_salon) if candidatos_salon else "TBA"
            
            found_perfect = False
            
            # Intentar 25 veces encontrar un hueco perfecto
            for _ in range(25):
                pat_test = random.choice(lista_patrones)
                ini_test = random.choice(self.bloques)
                
                # Check choque profesor
                prof_overlap = False
                if prof != "TBA" and prof != "GRADUADOS":
                    for dia, contrib in pat_test['days'].items():
                        fin_test = ini_test + int(contrib * 50)
                        for (ex_ini, ex_fin) in occ_prof.get((prof, dia), []):
                            if max(ini_test, ex_ini) < min(fin_test, ex_fin):
                                prof_overlap = True; break
                        if prof_overlap: break
                if prof_overlap: continue
                
                # Check choque salón
                random.shuffle(candidatos_salon)
                for sal_test in candidatos_salon:
                    room_overlap = False
                    for dia, contrib in pat_test['days'].items():
                        fin_test = ini_test + int(contrib * 50)
                        for (ex_ini, ex_fin, _, _) in occ_salon.get((sal_test, dia), []):
                            if max(ini_test, ex_ini) < min(fin_test, ex_fin):
                                room_overlap = True; break
                        if room_overlap: break
                        
                    if not room_overlap:
                        best_patron = pat_test
                        best_ini = ini_test
                        best_salon = sal_test
                        found_perfect = True
                        break
                if found_perfect: break
            
            ind.append({'sec': s, 'prof': prof, 'salon': best_salon, 'patron': best_patron, 'ini': best_ini})
            
            # Registrar ocupación para los siguientes ciclos
            if prof != "TBA" and prof != "GRADUADOS":
                for dia, contrib in best_patron['days'].items():
                    occ_prof.setdefault((prof, dia), []).append((best_ini, best_ini + int(contrib * 50)))
            if best_salon != "TBA":
                for dia, contrib in best_patron['days'].items():
                    occ_salon.setdefault((best_salon, dia), []).append((best_ini, best_ini + int(contrib * 50), s.cupo, s.es_fusionable))
                    
        return ind

    def _fitness_detailed(self, ind):
        penalty = 0
        conflicts = 0
        conflict_details = []
        bad_indices = set()
        soft_score = 0.0

        occ_salon = {}   
        occ_prof = {}    
        carga_prof = {}  

        for i, g in enumerate(ind):
            sec = g['sec']
            prof_nombre = g['prof']
            salon = g['salon']
            patron = g['patron']
            ini = g['ini']

            # Violaciones Duras
            if prof_nombre == "TBA":
                penalty += 10000; conflicts += 1; conflict_details.append(f"[{sec.cod}] Profesor TBA"); bad_indices.add(i); continue
            if salon == "TBA":
                penalty += 10000; conflicts += 1; conflict_details.append(f"[{sec.cod}] Salón TBA"); bad_indices.add(i); continue
            if prof_nombre != "GRADUADOS" and prof_nombre not in sec.cands:
                penalty += 10000; conflicts += 1; conflict_details.append(f"[{sec.cod}] Profesor {prof_nombre} no elegible"); bad_indices.add(i); continue

            prof_obj = self.profesores.get(prof_nombre)
            if prof_obj and prof_nombre != "GRADUADOS":
                for dia, contrib in patron['days'].items():
                    fin = ini + int(contrib * 50)
                    if self._es_bloqueo_activo(prof_obj, dia, ini, fin):
                        penalty += 10000; conflicts += 1; conflict_details.append(f"[{sec.cod}] {prof_nombre} en hora de bloqueo"); bad_indices.add(i); break

            if sum(patron['days'].values()) >= 3 and max(patron['days'].values()) >= 3:
                if ini < 930:
                    penalty += 10000; conflicts += 1; conflict_details.append(f"[{sec.cod}] Intensivo antes de 3:30 PM"); bad_indices.add(i)

            salon_info = next((s for s in self.salones if s['CODIGO'] == salon), None)
            if salon_info:
                if salon_info['CAPACIDAD'] < sec.cupo:
                    penalty += 10000; conflicts += 1; conflict_details.append(f"[{sec.cod}] Sobrecupo en {salon}"); bad_indices.add(i); continue
                es_fusion_valida = sec.es_fusionable and (salon in self.mega_salones)
                if not es_fusion_valida and salon_info['TIPO'] != sec.tipo_salon:
                    penalty += 10000; conflicts += 1; conflict_details.append(f"[{sec.cod}] Tipo de salón {salon} erróneo"); bad_indices.add(i); continue

            if prof_nombre != "GRADUADOS":
                carga_prof[prof_nombre] = carga_prof.get(prof_nombre, 0) + sec.creditos

            for dia, contrib in patron['days'].items():
                fin = ini + int(contrib * 50)
                rango = (ini, fin)

                if prof_nombre != "GRADUADOS":
                    pk = (prof_nombre, dia)
                    if pk not in occ_prof: occ_prof[pk] = []
                    for (ini_ex, fin_ex) in occ_prof[pk]:
                        if max(rango[0], ini_ex) < min(rango[1], fin_ex):
                            penalty += 10000; conflicts += 1; conflict_details.append(f"[{sec.cod}] {prof_nombre} solapado"); bad_indices.add(i); break
                    occ_prof[pk].append(rango)

                sk = (salon, dia)
                if sk not in occ_salon: occ_salon[sk] = []
                for (ini_ex, fin_ex, cupo_ex, fusionable_ex) in occ_salon[sk]:
                    if max(rango[0], ini_ex) < min(rango[1], fin_ex):
                        if salon in self.mega_salones and sec.es_fusionable and fusionable_ex:
                            if (sec.cupo + cupo_ex) > salon_info['CAPACIDAD']:
                                penalty += 5000; conflicts += 1; conflict_details.append(f"[{sec.cod}] Exceso en fusión {salon}"); bad_indices.add(i)
                        else:
                            penalty += 10000; conflicts += 1; conflict_details.append(f"[{sec.cod}] Salón {salon} solapado"); bad_indices.add(i); break
                occ_salon[sk].append((ini, fin, sec.cupo, sec.es_fusionable))

            if "Ma" in patron['days'] or "Ju" in patron['days']:
                if max(ini, self.h_univ[0]) < min(ini + 50, self.h_univ[1]):
                    penalty += 2000; conflicts += 1; conflict_details.append(f"[{sec.cod}] Invade hora universal"); bad_indices.add(i)

            # Soft Score
            if prof_nombre != "GRADUADOS":
                prior = self._suit_prof(prof_obj, sec)
                soft_score += prior * 10 
                if prof_obj.pref_dias:
                    dias_patron = set(patron['days'].keys())
                    dias_pref = set(prof_obj.pref_dias.replace(' ', '').split(','))
                    if dias_patron & dias_pref: soft_score += 5
                if prof_obj.pref_horas in ('AM', 'PM'):
                    hora_media = ini + 25 
                    if prof_obj.pref_horas == 'AM' and hora_media < 720: soft_score += 5
                    elif prof_obj.pref_horas == 'PM' and hora_media >= 720: soft_score += 5
                if prof_obj.compensacion:
                    comp = calcular_compensacion(sec.creditos, sec.cupo)
                    soft_score += comp * 2 

        for prof_nombre, carga in carga_prof.items():
            prof_obj = self.profesores.get(prof_nombre)
            if prof_obj:
                if carga > prof_obj.carga_max:
                    penalty += 10000; conflicts += 1; conflict_details.append(f"Profesor {prof_nombre} sobrecarga de créditos")
                    for idx_g, g_val in enumerate(ind):
                        if g_val['prof'] == prof_nombre: bad_indices.add(idx_g)
                elif carga < prof_obj.carga_min:
                    penalty += 1000 # Solo penalizacion suave

        fitness = 1 / (1 + max(0, penalty)) + soft_score * 1e-6
        return fitness, conflicts, conflict_details, list(bad_indices)

    def _mutate_gene(self, gene, aggressive_search=False):
        s = gene['sec']
        lista_patrones = PATRONES.get(s.creditos, PATRONES[3])
        patron_elegido = random.choice(lista_patrones)
        h_ini = random.choice(self.bloques)
        
        if s.cands:
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
                    
                # Mutacion asistida gen por gen
                pm = 0.05
                for i in range(len(hijo)):
                    if random.random() < pm:
                        hijo[i] = self._mutate_gene(hijo[i], aggressive_search=True)
                        
                nueva_gen.append(hijo)

            poblacion = nueva_gen

        # Reparación Final intensa si quedan conflictos
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
# 4. UI PRINCIPAL Y PERSISTENCIA DE SESIÓN
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
    limites = "07:30 AM - 07:00 PM"
    
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
        # BOTON TRIGGER (Solo procesa datos, no renderiza UI abajo)
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
                
                # GUARDAR RESULTADOS EN LA MEMORIA DE STREAMLIT
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

    # RENDERIZADO FUERA DEL BOTÓN (Para que no desaparezca al hacer clic en pestañas)
    if 'master' in st.session_state:
        # Mostrar barra de tiempo de ejecución
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
                st.error(f"⚠️ Se detectaron {len(conflictos)} conflictos. Se recomienda subir las generaciones o flexibilizar los datos en el Excel.")
                # Remover duplicados para que la lista no sea kilométrica
                conflictos_unicos = list(set(conflictos))
                for txt in conflictos_unicos:
                    st.markdown(f"- `{txt}`")
            else:
                st.success("✅ 100% Asignación Perfecta. Cero Conflictos. Se respetaron todas las métricas de espacio y carga.")
                
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
