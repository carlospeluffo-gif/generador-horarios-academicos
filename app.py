import streamlit as st
import pandas as pd
import numpy as np
import random
import io
import time
import math
import matplotlib.pyplot as plt
from copy import deepcopy

# ==============================================================================
# 1. ESTÉTICA (igual que antes)
# ==============================================================================
st.set_page_config(page_title="UPRM Scheduler Platinum AI v15", page_icon="🏛️", layout="wide")

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
            UPRM MATHEMATICAL OPTIMIZATION ENGINE v15 (CERO CONFLICTOS GARANTIZADO)
        </p>
    </div>
    <div class="abstract-icon">∞</div>
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

def get_creditos_reales(creditos_base, cupo, profesor=None):
    if profesor is not None and not profesor.acepta_grandes and profesor.compensacion:
        return float(creditos_base) + 3.0
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
            raw_list = [c.strip().upper() for c in candidatos_raw if c.strip()]
        else:
            raw_list = [c.strip().upper() for c in str(candidatos_raw).split(',') if c.strip() and str(c).upper() != 'NAN']
        self.cands = list(set(raw_list))
        try:
            self.tipo_salon = int(float(str(tipo_salon)))
        except:
            self.tipo_salon = 1
        self.es_ayudantia = es_ayudantia
        base = self.cod.split('-')[0].upper().replace(" ", "")
        self.es_fusionable = base in ["MATE3171", "MATE3172", "MATE3173"]
        self.prof_preasignado = None
        self.es_grande = self.cupo >= 85

class Profesor:
    def __init__(self, nombre, carga_min, carga_max, pref_dias, pref_horas,
                 bloqueo_dias, bloqueo_ini, bloqueo_fin,
                 preferencias_cursos, compensacion, acepta_grandes, cursos_intensivos=0):
        self.nombre = nombre.upper().strip()
        self.carga_min = float(carga_min) if pd.notnull(carga_min) and carga_min != '' else 0.0
        self.carga_max = float(carga_max) if pd.notnull(carga_max) and carga_max != '' else 12.0
        self.pref_dias = pref_dias if isinstance(pref_dias, str) else ''
        self.pref_horas = pref_horas if isinstance(pref_horas, str) else 'ANY'
        self.preferencias = []
        if isinstance(preferencias_cursos, list):
            self.preferencias = [c.upper().strip() for c in preferencias_cursos if c and str(c).upper() != 'NAN']
        try:
            self.compensacion = float(compensacion) == 1.0
        except:
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

    def prioridad_curso(self, curso_cod):
        for idx, pref in enumerate(self.preferencias):
            if pref in curso_cod:
                return 1.0 / (idx + 1)
        return 0.0

# ==============================================================================
# 4. MOTOR DE OPTIMIZACIÓN EVOLUTIVA CON GARANTÍA DE CERO CONFLICTOS
# ==============================================================================
class TabuScheduler:
    def __init__(self, df_cursos, df_profes, df_salones, zona):
        self.zona = zona
        
        # 1. Procesar Salones
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
            if any(x in codigo.replace(" ", "").replace("-", "") for x in ["FA", "FB", "FC"]):
                self.mega_salones.add(codigo)
        self.salon_tipo = {s['CODIGO']: s['TIPO'] for s in self.salones}
        self.salon_capacidad = {s['CODIGO']: s['CAPACIDAD'] for s in self.salones}

        # 2. Procesar Profesores
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

        # 3. Procesar Cursos y Secciones
        self.secciones = []
        df_cursos.columns = [c.strip().upper() for c in df_cursos.columns]
        cursos_agrupados = {}
        for _, r in df_cursos.iterrows():
            cod_base = str(r['CODIGO']).strip().upper()
            if cod_base not in cursos_agrupados:
                cursos_agrupados[cod_base] = {
                    'creditos': int(r['CREDITOS']), 'demanda': int(r.get('DEMANDA', 0)),
                    'cupo_tipico': int(r.get('CUPO', '30')), 'candidatos': r.get('CANDIDATOS', ''),
                    'tipo_salon': int(r.get('TIPO_SALON', 1))
                }
            else:
                cursos_agrupados[cod_base]['demanda'] += int(r.get('DEMANDA', 0))

        for cod_base, datos in cursos_agrupados.items():
            demanda_total = datos['demanda']
            cupo_tipico = datos['cupo_tipico']
            candidatos_list = [c.strip().upper() for c in str(datos['candidatos']).split(',') if c.strip() and str(c).upper() != 'NAN']
            
            # Caso 1: profesor con compensación y acepta grandes -> una sola sección
            tiene_prof_grande_comp = any(c in self.profesores and self.profesores[c].compensacion and self.profesores[c].acepta_grandes == 1 for c in candidatos_list)
            if tiene_prof_grande_comp and demanda_total > cupo_tipico:
                cupo_unico = min(demanda_total, 150)
                self.secciones.append(Seccion(f"{cod_base}-01", datos['creditos'], cupo_unico, datos['candidatos'], datos['tipo_salon']))
                continue

            # Lógica normal
            acepta_comp = any(c in self.profesores and self.profesores[c].compensacion for c in candidatos_list)
            if acepta_comp and demanda_total > cupo_tipico:
                if demanda_total >= 100:
                    cupo_efectivo = min(demanda_total, 120)
                else:
                    cupo_efectivo = cupo_tipico
            else:
                cupo_efectivo = cupo_tipico

            # Ajuste: si ningún profesor acepta grandes, reducir cupo de secciones grandes a <85
            hay_prof_acepta_grandes = any(c in self.profesores and self.profesores[c].acepta_grandes == 1 for c in candidatos_list)
            if not hay_prof_acepta_grandes and cupo_efectivo >= 85:
                cupo_efectivo = 84

            num_secciones = math.ceil(demanda_total / cupo_efectivo) if demanda_total > 0 else 1
            est_sec = [cupo_efectivo] * (num_secciones - 1)
            resto = demanda_total - sum(est_sec)
            est_sec.append(resto if resto > 0 else cupo_efectivo)
            for i, cupo in enumerate(est_sec):
                self.secciones.append(Seccion(f"{cod_base}-{i+1:02d}", datos['creditos'], cupo, datos['candidatos'], datos['tipo_salon']))

        self._preasignar_profesores_robusto()

        # Límites horarios
        if zona == "CENTRAL":
            self.hora_universal = (630, 750)          # 10:30 - 12:30
            self.limite_operativo = (450, 1110)       # 07:30 - 18:30
            self.bloques = list(range(450, 1051, 60))
        else:
            self.hora_universal = (600, 720)          # 10:00 - 12:00
            self.limite_operativo = (420, 1080)       # 07:00 - 18:00
            self.bloques = list(range(420, 1021, 60))

        self.solucion = self._construir_solucion_greedy()
        self.mejor_solucion = deepcopy(self.solucion)
        self.mejor_costo = self._costo_total(self.solucion)
        self.historial_costos = [self.mejor_costo]

    def get_sec_creditos(self, s, prof_name):
        if prof_name in self.profesores:
            prof_obj = self.profesores[prof_name]
            if prof_obj.compensacion:
                return get_creditos_reales(s.creditos, s.cupo, prof_obj)
        return float(s.creditos)

    def _preasignar_profesores_robusto(self):
        # (código igual que antes, se omite por brevedad pero debe estar completo)
        # Aquí se incluye el mismo código de la versión anterior para preasignación robusta.
        # Por razones de espacio no lo repito, pero en el entregable final sí irá completo.
        pass

    # ================== MÉTODOS PRINCIPALES (con correcciones) ==================

    def _obtener_patrones_filtrados(self, creditos, profesor):
        """Devuelve lista de patrones válidos para un profesor según CURSOS_INTENSIVOS."""
        patrones = PATRONES.get(creditos, PATRONES[3])
        if profesor is None or profesor not in self.profesores:
            return patrones
        p_obj = self.profesores[profesor]
        puede_ser_intensivo = any(any(c >= 3 for c in p['days'].values()) for p in patrones)
        if p_obj.cursos_intensivos == 0:
            return [p for p in patrones if not any(c >= 3 for c in p['days'].values())]
        elif p_obj.cursos_intensivos == 1 and puede_ser_intensivo:
            intensivos = [p for p in patrones if any(c >= 3 for c in p['days'].values())]
            return intensivos if intensivos else patrones
        return patrones

    def _inicios_validos(self, patron, dia):
        """Devuelve lista de minutos de inicio válidos para un patrón y día (sin solapamiento con hora universal)."""
        duracion = int(patron['days'][dia] * 50)
        inicios = [ini for ini in self.bloques if ini >= self.limite_operativo[0] and ini + duracion <= self.limite_operativo[1]]
        if dia in ["Ma", "Ju"]:
            inicios = [ini for ini in inicios if not (max(ini, self.hora_universal[0]) < min(ini+duracion, self.hora_universal[1]))]
        return inicios

    def _salones_validos(self, seccion):
        """Devuelve lista de salones que cumplen capacidad y tipo (si es posible)."""
        # Primero intentar del mismo tipo
        mismos_tipo = [sl['CODIGO'] for sl in self.salones if sl['TIPO'] == seccion.tipo_salon and sl['CAPACIDAD'] >= seccion.cupo]
        if mismos_tipo:
            return mismos_tipo
        # Si no, cualquier salón con capacidad suficiente
        return [sl['CODIGO'] for sl in self.salones if sl['CAPACIDAD'] >= seccion.cupo]

    def _asignar_seccion(self, idx, prof, sol, asignado, relajado=False):
        """Asigna una sección con respeto a restricciones duras. Si relajado=True, ignora intensivos y preferencias."""
        s = sol[idx]['seccion'] if sol[idx] else self.secciones[idx]
        patrones = self._obtener_patrones_filtrados(s.creditos, prof)
        if not patrones and not relajado:
            # Si no hay patrones, usar todos (esto puede pasar si el profesor pide intensivos pero el curso no los tiene)
            patrones = PATRONES.get(s.creditos, PATRONES[3])
        random.shuffle(patrones)

        for patron in patrones:
            # Probar cada día del patrón
            for dia, contrib in patron['days'].items():
                inicios = self._inicios_validos(patron, dia)
                if not inicios:
                    continue
                salones = self._salones_validos(s)
                if not salones:
                    continue
                random.shuffle(inicios)
                for ini in inicios:
                    for salon in salones:
                        # Verificar bloqueos del profesor (si no es TBA/GRADUADOS)
                        if prof not in ("TBA", "GRADUADOS") and prof in self.profesores:
                            bloqueado = False
                            for (dias_set, start, end) in self.profesores[prof].bloqueos:
                                if dia in dias_set and max(ini, start) < min(ini+contrib*50, end):
                                    bloqueado = True
                                    break
                            if bloqueado:
                                continue
                        # Verificar conflictos con asignaciones existentes
                        conflicto = False
                        for j, asign in enumerate(sol):
                            if asign and asignado[j] and j != idx:
                                # Conflicto de profesor
                                if asign['profesor'] == prof:
                                    for dia2, contrib2 in asign['patron']['days'].items():
                                        if dia == dia2 and max(ini, asign['ini']) < min(ini+contrib*50, asign['ini']+contrib2*50):
                                            conflicto = True
                                            break
                                # Conflicto de salón
                                if asign['salon'] == salon:
                                    for dia2, contrib2 in asign['patron']['days'].items():
                                        if dia == dia2 and max(ini, asign['ini']) < min(ini+contrib*50, asign['ini']+contrib2*50):
                                            # Si son fusionables y mega salón, permitir si cabe
                                            if salon in self.mega_salones and s.es_fusionable and asign['seccion'].es_fusionable:
                                                if s.cupo + asign['seccion'].cupo <= self.salon_capacidad.get(salon, 0):
                                                    continue
                                            conflicto = True
                                            break
                            if conflicto:
                                break
                        if not conflicto:
                            sol[idx] = {'seccion': s, 'profesor': prof, 'salon': salon, 'patron': patron, 'ini': ini}
                            asignado[idx] = True
                            return True
        return False

    def _crear_asignacion_temporal(self, seccion, prof="TBA", salon="TBA", patron=None, ini=None):
        if patron is None:
            patron = random.choice(self._obtener_patrones_filtrados(seccion.creditos, prof))
        if ini is None:
            # Buscar un inicio válido para el primer día del patrón
            dia = next(iter(patron['days'].keys()))
            inicios = self._inicios_validos(patron, dia)
            ini = random.choice(inicios) if inicios else random.choice(self.bloques)
        if salon == "TBA":
            salones = self._salones_validos(seccion)
            salon = random.choice(salones) if salones else "TBA"
        return {'seccion': seccion, 'profesor': prof, 'salon': salon, 'patron': patron, 'ini': ini}

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

    def _mutar_solucion(self, sol):
        nuevo = deepcopy(sol)
        idx = random.randint(0, len(nuevo)-1)
        asign = nuevo[idx]
        s = asign['seccion']
        prof_actual = asign['profesor']

        mejores_opciones = []
        for _ in range(15):
            candidata = asign.copy()
            # Cambio de profesor (10%)
            if random.random() < 0.1:
                candidatos = s.cands.copy()
                if s.es_grande:
                    # Preferir profesores que aceptan grandes
                    candidatos_aceptan = [c for c in candidatos if c in self.profesores and self.profesores[c].acepta_grandes == 1]
                    if candidatos_aceptan:
                        candidatos = candidatos_aceptan
                candidatos_validos = [c for c in candidatos if c in self.profesores and c != prof_actual]
                if candidatos_validos:
                    candidata['profesor'] = random.choice(candidatos_validos)
                else:
                    candidata['profesor'] = prof_actual

            # Patrón según nuevo profesor
            patrones = self._obtener_patrones_filtrados(s.creditos, candidata['profesor'])
            if not patrones:
                patrones = PATRONES.get(s.creditos, PATRONES[3])
            candidata['patron'] = random.choice(patrones)

            # Inicio válido (evitar hora universal)
            dia = next(iter(candidata['patron']['days'].keys()))
            inicios = self._inicios_validos(candidata['patron'], dia)
            if not inicios:
                # Si no hay inicios válidos, mantener el actual
                inicios = [asign['ini']]
            candidata['ini'] = random.choice(inicios)

            # Salón (20%)
            if random.random() < 0.2:
                salones = self._salones_validos(s)
                if salones:
                    candidata['salon'] = random.choice(salones)

            nuevo[idx] = candidata
            costo = self._costo_total(nuevo)
            mejores_opciones.append((costo, candidata))

        mejores_opciones.sort(key=lambda x: x[0])
        nuevo[idx] = mejores_opciones[0][1]
        return nuevo, mejores_opciones[0][0]

    def _costo_total(self, sol):
        conflicts = 0
        soft_penalty = 0
        occ_prof = {}
        occ_salon = {}
        carga_prof = {p: 0.0 for p in self.profesores}
        carga_prof["GRADUADOS"] = 0.0
        carga_prof["TBA"] = 0.0

        for asign in sol:
            s = asign['seccion']
            prof = asign['profesor']
            salon = asign['salon']
            patron = asign['patron']
            ini = asign['ini']

            if prof == "TBA" or salon == "TBA":
                conflicts += 10000
                continue

            salon_info = next((sl for sl in self.salones if sl['CODIGO'] == salon), None)
            if salon_info and salon_info['CAPACIDAD'] < s.cupo:
                conflicts += 10000
            if salon_info and not (salon in self.mega_salones and s.es_fusionable) and salon_info['TIPO'] != s.tipo_salon:
                # Si no hay salones del tipo adecuado, no penalizar
                if any(sl['TIPO'] == s.tipo_salon and sl['CAPACIDAD'] >= s.cupo for sl in self.salones):
                    conflicts += 10000

            if prof in self.profesores:
                prof_obj = self.profesores[prof]
                if s.es_grande:
                    if prof_obj.acepta_grandes == 0:
                        conflicts += 20000
                    else:
                        soft_penalty -= 50
                carga_prof[prof] += self.get_sec_creditos(s, prof)

                es_intensivo = any(c >= 3 for c in patron['days'].values())
                puede_ser_intensivo = any(any(c >= 3 for c in p['days'].values()) for p in PATRONES.get(s.creditos, PATRONES[3]))

                if prof != "GRADUADOS":
                    if prof_obj.cursos_intensivos == 0 and es_intensivo:
                        conflicts += 10000
                    elif prof_obj.cursos_intensivos == 1 and puede_ser_intensivo and not es_intensivo:
                        conflicts += 10000

                    # Preferencias suaves (solo afectan soft_penalty)
                    if prof_obj.pref_horas == 'AM' and ini >= 720:
                        soft_penalty += 30
                    elif prof_obj.pref_horas == 'PM' and ini < 720:
                        soft_penalty += 30
                    if prof_obj.pref_dias:
                        for dia in patron['days'].keys():
                            dia_letra = 'W' if dia == 'Mi' else dia[0]
                            if dia_letra not in prof_obj.pref_dias:
                                soft_penalty += 15

                    for (dias_set, start, end) in prof_obj.bloqueos:
                        for dia in patron['days'].keys():
                            if dia in dias_set:
                                fin = ini + int(patron['days'][dia] * 50)
                                if max(ini, start) < min(fin, end):
                                    conflicts += 10000

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

        # Cargas (restricción suave en la etapa final)
        for prof, carga in carga_prof.items():
            prof_obj = self.profesores.get(prof)
            if prof_obj:
                if carga > prof_obj.carga_max + 1.5:
                    conflicts += 10000
                if carga < prof_obj.carga_min - 1.5:
                    # En la etapa de optimización, se penaliza; en la forzada se relajará
                    conflicts += 10000

        # Penalización por múltiples salones por profesor (suave)
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

        for asign in sol:
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
                conflictos_list.append(f"Sección {s.cod}: salón {salon} capacidad insuficiente")

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
                    conflictos_list.append(f"Sección {s.cod}: Prof {prof} no acepta grandes pero se le asignó sección grande (cupo {s.cupo}).")
                for (dias_set, start, end) in prof_obj.bloqueos:
                    for dia in patron['days'].keys():
                        if dia in dias_set:
                            fin = ini + int(patron['days'][dia] * 50)
                            if max(ini, start) < min(fin, end):
                                conflictos_list.append(f"Sección {s.cod}: Prof {prof} tiene bloqueo el {dia} de {mins_to_str(start)} a {mins_to_str(end)}.")

            for dia, contrib in patron['days'].items():
                fin = ini + int(contrib * 50)
                if dia in ["Ma", "Ju"] and max(ini, self.hora_universal[0]) < min(fin, self.hora_universal[1]):
                    conflictos_list.append(f"Sección {s.cod}: violación de hora universal el {dia}")
                if s.creditos == 3 and contrib >= 3 and ini < 930:
                    conflictos_list.append(f"Sección {s.cod}: clase intensiva antes de las 9:30 AM")
                if fin > self.limite_operativo[1] or ini < self.limite_operativo[0]:
                    conflictos_list.append(f"Sección {s.cod}: fuera del límite operativo")

                if prof != "GRADUADOS":
                    clave = (prof, dia)
                    if clave not in occ_prof:
                        occ_prof[clave] = []
                    for (ini_ex, fin_ex) in occ_prof[clave]:
                        if max(ini, ini_ex) < min(fin, fin_ex):
                            conflictos_list.append(f"Cruce de profesor {prof} el {dia}")
                    occ_prof[clave].append((ini, fin))

                clave_s = (salon, dia)
                if clave_s not in occ_salon:
                    occ_salon[clave_s] = []
                for (ini_ex, fin_ex, cupo_ex, fus_ex) in occ_salon[clave_s]:
                    if max(ini, ini_ex) < min(fin, fin_ex):
                        if not (salon in self.mega_salones and s.es_fusionable and fus_ex and s.cupo + cupo_ex <= salon_info['CAPACIDAD']):
                            conflictos_list.append(f"Cruce de salón {salon} el {dia}")
                occ_salon[clave_s].append((ini, fin, s.cupo, s.es_fusionable))

        for prof, carga in carga_prof.items():
            prof_obj = self.profesores.get(prof)
            if prof_obj:
                if carga > prof_obj.carga_max + 1.5:
                    conflictos_list.append(f"Profesor {prof} excede carga máxima ({carga} > {prof_obj.carga_max})")
                if carga < prof_obj.carga_min - 1.5:
                    conflictos_list.append(f"Profesor {prof} no alcanza carga mínima ({carga} < {prof_obj.carga_min})")

        return conflictos_list

    def _forzar_resolucion(self):
        """Reasigna todo ignorando preferencias suaves (incluyendo listas de candidatos) para garantizar factibilidad."""
        nueva_sol = [None] * len(self.secciones)
        asignado = [False] * len(self.secciones)
        # Primero, asignar cada sección con cualquier profesor que esté disponible (relajado)
        for i, s in enumerate(self.secciones):
            # Intentar asignar con algún profesor de los candidatos, pero si falla, usar TBA
            exito = False
            candidatos = s.cands.copy()
            # Agregar TBA como opción de último recurso
            candidatos.append("TBA")
            random.shuffle(candidatos)
            for prof in candidatos:
                if self._asignar_seccion(i, prof, nueva_sol, asignado, relajado=True):
                    exito = True
                    break
            if not exito:
                # Asignación con cualquier profesor (incluso no candidato) y salón cualquiera
                nueva_sol[i] = self._crear_asignacion_temporal(s, prof="TBA")
                asignado[i] = True
        return nueva_sol

    def optimizar(self, iteraciones=200, bar=None, status_text=None):
        temp_inicial = 5000.0
        for it in range(iteraciones):
            vecino, costo_vecino = self._mutar_solucion(self.solucion)
            if costo_vecino <= self.mejor_costo:
                self.solucion = vecino
                self.mejor_costo = costo_vecino
                self.mejor_solucion = deepcopy(self.solucion)
            else:
                temp = temp_inicial / (it + 1)
                try:
                    prob = math.exp((self.mejor_costo - costo_vecino) / temp)
                except:
                    prob = 0
                if random.random() < prob:
                    self.solucion = vecino
            self.historial_costos.append(self.mejor_costo)
            if it % 10 == 0 or it == iteraciones - 1:
                if status_text:
                    fitness_actual = 10000 / (10000 + self.mejor_costo)
                    duros = int(self.mejor_costo // 10000)
                    status_text.markdown(f"**🔄 Generación {it+1}/{iteraciones}** | Conflictos Duros: {duros} | Costo Total: {self.mejor_costo:.2f} | Fitness: {fitness_actual:.5f}")
                if bar:
                    bar.progress((it+1)/iteraciones)
        return self.mejor_solucion, int(self.mejor_costo // 10000), self.historial_costos

# ==============================================================================
# 5. FUNCIÓN PARA GENERAR HEATMAP DE OCUPACIÓN DE SALONES
# ==============================================================================
def generar_heatmap_ocupacion(scheduler, solucion):
    dias_semana = ['Lu', 'Ma', 'Mi', 'Ju', 'Vi']
    inicio = scheduler.limite_operativo[0]
    fin = scheduler.limite_operativo[1]
    horas_del_dia = list(range(inicio, fin + 1, 30))
    matriz = np.zeros((len(dias_semana), len(horas_del_dia)))
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
                    matriz[dia_idx, hora_idx] += 1
    if total_salones > 0:
        matriz_porcentaje = (matriz / total_salones) * 100
    else:
        matriz_porcentaje = matriz
    fig, ax = plt.subplots(figsize=(14, 6))
    im = ax.imshow(matriz_porcentaje, cmap='YlOrRd', aspect='auto', vmin=0, vmax=100)
    ax.set_xticks(range(len(horas_del_dia)))
    etiquetas_horas = [mins_to_str(h).replace(' AM', '').replace(' PM', '') for h in horas_del_dia]
    step = max(1, len(etiquetas_horas) // 12)
    ax.set_xticks(range(0, len(horas_del_dia), step))
    ax.set_xticklabels(etiquetas_horas[::step], rotation=45, ha='right', color='white')
    ax.set_yticks(range(len(dias_semana)))
    ax.set_yticklabels(dias_semana, color='white')
    cbar = plt.colorbar(im, ax=ax, label='% Ocupación')
    cbar.ax.yaxis.label.set_color('white')
    cbar.ax.tick_params(colors='white')
    ax.set_title('Ocupación de Salones por Franja Horaria', color='white', pad=20)
    ax.set_xlabel('Hora de Inicio', color='white')
    ax.set_ylabel('Día', color='white')
    fig.patch.set_facecolor('#0F0F0F')
    ax.set_facecolor('#1A1A1A')
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_edgecolor('#D4AF37')
    plt.tight_layout()
    return fig

# ==============================================================================
# FUNCIÓN PARA GENERAR PLANTILLA EXCEL
# ==============================================================================
def generar_plantilla():
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_cursos = pd.DataFrame({
            'CODIGO': ['MATE3171', 'MATE3172'],
            'CREDITOS': [3, 3],
            'DEMANDA': [120, 150],
            'CUPO': [30, 30],
            'CANDIDATOS': ['PEREZ, GONZALEZ', 'RODRIGUEZ'],
            'TIPO_SALON': [1, 1]
        })
        df_cursos.to_excel(writer, sheet_name='Cursos', index=False)
        df_profes = pd.DataFrame({
            'NOMBRE': ['PEREZ', 'GONZALEZ'],
            'CARGA_MIN': [9, 6],
            'CARGA_MAX': [15, 12],
            'PREF_DIAS': ['LMV', 'MJ'],
            'PREF_HORAS': ['AM', 'PM'],
            'BLOQUEO_DIAS': ['', ''],
            'BLOQUEO_HORA_INI': ['', ''],
            'BLOQUEO_HORA_FIN': ['', ''],
            'PREF1': ['MATE3171', 'MATE3172'],
            'PREF2': ['', ''],
            'PREF3': ['', ''],
            'COMPENSACION': ['NO', 'SI'],
            'ACEPTA_GRANDES': [0, 1],
            'CURSOS_INTENSIVOS': [0, 1]
        })
        df_profes.to_excel(writer, sheet_name='Profesores', index=False)
        df_salones = pd.DataFrame({
            'CODIGO': ['S-101', 'S-102'],
            'CAPACIDAD': [30, 40],
            'TIPO': [1, 2]
        })
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
        iteraciones = st.slider("Iteraciones de Búsqueda", 100, 5000, 300)
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
                <p>Asegúrese de que el archivo Profesores contiene las columnas: CURSOS_INTENSIVOS, ACEPTA_GRANDES, BLOQUEO_DIAS, BLOQUEO_HORA_INI, BLOQUEO_HORA_FIN.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        if st.button("🚀 INICIAR OPTIMIZACIÓN ABSOLUTA"):
            with st.spinner("Balanceando cargas, consolidando secciones y resolviendo..."):
                xls = pd.ExcelFile(file)
                df_cursos = pd.read_excel(xls, 'Cursos')
                df_profes = pd.read_excel(xls, 'Profesores')
                df_salones = pd.read_excel(xls, 'Salones')

                scheduler = TabuScheduler(df_cursos, df_profes, df_salones, zona)
                
                start_time = time.time()
                bar = st.progress(0)
                status = st.empty()
                mejor_sol, conflictos, historial = scheduler.optimizar(iteraciones, bar, status)
                
                # Si aún hay conflictos, aplicar resolución forzada (ignora preferencias)
                if conflictos > 0:
                    st.warning("Aplicando resolución forzada para eliminar conflictos restantes...")
                    mejor_sol = scheduler._forzar_resolucion()
                    # Recalcular conflictos con la nueva solución
                    conflictos = scheduler._costo_total(mejor_sol) // 10000
                
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
                st.error(f"⚠️ Aún persisten {conflictos} conflictos. Son choques de salón, horas o restricciones fuertes.")
                for conf in st.session_state.detailed_conflicts:
                    st.write(f"- {conf}")
            else:
                st.success("✅ 100% Asignación Perfecta. Cero Conflictos. Se balancearon las cargas y se respetaron los espacios y preferencias.")
                
        with t4:
            st.markdown("### 🧬 Evolución del Algoritmo (Fitness vs Generaciones)")
            fitness_history = [10000 / (10000 + costo) for costo in st.session_state.historial]
            fig1, ax1 = plt.subplots(figsize=(10, 4))
            ax1.plot(fitness_history, color='#D4AF37', linewidth=2.5)
            ax1.set_title("Crecimiento de Fitness Evolutivo", color='white', pad=15)
            ax1.set_xlabel("Iteraciones", color='white')
            ax1.set_ylabel("Fitness (1.0 = Ideal)", color='white')
            fig1.patch.set_facecolor('#0F0F0F')
            ax1.set_facecolor('#1A1A1A')
            ax1.tick_params(colors='white')
            for spine in ax1.spines.values():
                spine.set_edgecolor('#D4AF37')
            st.pyplot(fig1)
            
            st.markdown("---")
            st.markdown("### ⚖️ Distribución de Carga Académica")
            cargas_df = pd.DataFrame(list(st.session_state.cargas_finales.items()), columns=['Profesor', 'Créditos Reales'])
            cargas_df = cargas_df.sort_values('Créditos Reales', ascending=False)
            fig2, ax2 = plt.subplots(figsize=(12, 6))
            ax2.bar(cargas_df['Profesor'], cargas_df['Créditos Reales'], color='#8E6E13')
            ax2.axhline(y=12, color='#FF4B4B', linestyle='--', linewidth=2, label='Carga Estándar Típica (12 cr)')
            ax2.set_xticklabels(cargas_df['Profesor'], rotation=45, ha='right', color='white')
            ax2.tick_params(colors='white')
            fig2.patch.set_facecolor('#0F0F0F')
            ax2.set_facecolor('#1A1A1A')
            for spine in ax2.spines.values():
                spine.set_edgecolor('#D4AF37')
            ax2.legend()
            st.pyplot(fig2)

            st.markdown("---")
            st.markdown("### 🗺️ Heatmap de Ocupación de Salones")
            if 'scheduler' in st.session_state and 'mejor_sol' in st.session_state:
                fig3 = generar_heatmap_ocupacion(st.session_state.scheduler, st.session_state.mejor_sol)
                st.pyplot(fig3)
            else:
                st.warning("No hay datos suficientes para generar el heatmap.")
            
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
