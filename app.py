import streamlit as st
import pandas as pd
import numpy as np
import random
import io
import time
import math
import unicodedata
from copy import deepcopy

# ==============================================================================
# 1. ESTÉTICA (TEMA CLARO - FONDO BLANCO)
# ==============================================================================
st.set_page_config(page_title="UPRM Scheduler Platinum AI v13 (Genético)", page_icon="🏛️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Source+Code+Pro:wght@300;500&display=swap');
    
    .stApp { 
        background-color: #F8F9FA;
        background-image: 
            linear-gradient(rgba(212, 175, 55, 0.08) 2px, transparent 2px),
            linear-gradient(90deg, rgba(212, 175, 55, 0.08) 2px, transparent 2px);
        background-size: 80px 80px, 80px 80px;
        color: #1E1E1E; 
    }

    .math-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 30px 60px;
        background: rgba(255, 255, 255, 0.95);
        border-bottom: 3px solid #D4AF37;
        margin-bottom: 40px;
        border-radius: 0 0 30px 30px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
        position: relative;
        overflow: hidden;
    }

    .math-header::before { content: '∑'; position: absolute; left: 5%; font-size: 8rem; color: rgba(212, 175, 55, 0.1); font-family: serif; }
    .math-header::after { content: '∫'; position: absolute; right: 5%; font-size: 8rem; color: rgba(212, 175, 55, 0.1); font-family: serif; }

    .title-box { text-align: center; z-index: 2; }

    .abstract-icon {
        font-size: 3rem;
        color: #D4AF37;
        border: 2px solid #D4AF37;
        padding: 10px 20px;
        border-radius: 50% 0% 50% 0%;
        background: rgba(212, 175, 55, 0.05);
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.2);
    }

    h1 { 
        font-family: 'Playfair Display', serif !important; 
        color: #8E6E13 !important; 
        font-size: 3.2rem !important;
        margin: 10px 0 !important;
        text-shadow: 0 0 5px rgba(212, 175, 55, 0.3);
        letter-spacing: 2px;
    }

    .glass-card { 
        background: rgba(255, 255, 255, 0.95); 
        border-radius: 15px; 
        padding: 25px; 
        border: 1px solid rgba(212, 175, 55, 0.4); 
        backdrop-filter: blur(5px); 
        margin-bottom: 20px; 
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
    }

    .stButton>button { 
        background: linear-gradient(135deg, #8E6E13 0%, #D4AF37 50%, #8E6E13 100%) !important; 
        color: white !important; font-weight: bold !important; border-radius: 4px !important; 
        width: 100%; border: none !important; height: 55px; font-size: 1.1rem;
        transition: 0.4s;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 0 25px rgba(212, 175, 55, 0.5); }

    .stDownloadButton>button {
        background: linear-gradient(135deg, #B8860B 0%, #FFD700 50%, #B8860B 100%) !important;
        color: #000 !important;
        font-weight: 800 !important;
        border: 1px solid #D4AF37 !important;
    }

    [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #D4AF37; }
    
    [data-testid="stSidebar"] h3 {
        color: #8E6E13 !important;
        text-shadow: 0 0 5px rgba(212, 175, 55, 0.3);
        font-family: 'Playfair Display', serif;
    }
</style>

<div class="math-header">
    <div class="abstract-icon">Δx</div>
    <div class="title-box">
        <h1>UPRM TIMETABLE SYSTEM</h1>
        <p style="color: #5C5C5C; font-family: 'Source Code Pro'; letter-spacing: 4px; font-size: 0.9rem;">
            UPRM EVOLUTIONARY GA ENGINE v13 (GENÉTICOS + INTENSIVOS + GRANDES + BLOQUEOS + DOBLE ROL)
        </p>
    </div>
    <div class="abstract-icon">∞</div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. UTILIDADES Y TABLAS DE REFERENCIA
# ==============================================================================
def normalize_name(s: str) -> str:
    s = str(s).strip()
    return unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode().upper()

COMPENSACION_TABLE = [
    (1, 1, 44, 0.0), (1, 45, 74, 0.5), (1, 75, 104, 1.0), (1, 105, 134, 1.5), (1, 135, 164, 2.0),
    (2, 1, 37, 0.0), (2, 38, 52, 0.5), (2, 53, 67, 1.0), (2, 68, 82, 1.5), (2, 83, 97, 2.0), (2, 98, 112, 2.5), 
    (3, 1, 34, 0.0), (3, 35, 44, 0.5), (3, 45, 54, 1.0), (3, 55, 64, 1.5), (3, 65, 74, 2.0), (3, 75, 84, 2.5),
    (4, 1, 33, 0.0), (4, 34, 41, 0.5), (4, 42, 48, 1.0), (4, 49, 56, 1.5), (4, 57, 63, 2.0), (4, 64, 71, 2.5),
    (5, 1, 32, 0.0), (5, 33, 38, 0.5), (5, 39, 44, 1.0), (5, 45, 50, 1.5), (5, 51, 56, 2.0), (5, 57, 62, 2.5)
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
    t_str = str(t_str).strip().upper()
    parts = t_str.split()
    time_part = parts
    ampm = parts if len(parts) > 1 else "AM"
    try:
        h, m = map(int, time_part.split(':'))
        if ampm == "PM" and h != 12: h += 12
        if ampm == "AM" and h == 12: h = 0
        return h * 60 + m
    except:
        return 0

PATRONES = {
    3: [
        {"name": "Lu-Mi-Vi", "days": {"Lu": 1, "Mi": 1, "Vi": 1}},
        {"name": "Ma-Ju", "days": {"Ma": 1.5, "Ju": 1.5}},
        {"name": "Lu (Intensivo)", "days": {"Lu": 3}},
        {"name": "Ma (Intensivo)", "days": {"Ma": 3}},
    ],
    4: [
        {"name": "Lu-Ma-Mi-Ju", "days": {"Lu": 1, "Ma": 1, "Mi": 1, "Ju": 1}},
        {"name": "Lu-Mi", "days": {"Lu": 2, "Mi": 2}},
        {"name": "Ma-Ju", "days": {"Ma": 2, "Ju": 2}},
    ],
    5: [
        {"name": "Lu-Ma-Mi-Ju-Vi", "days": {"Lu": 1, "Ma": 1, "Mi": 1, "Ju": 1, "Vi": 1}},
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
        for p in df['Profesor Asignado'].unique():
            if str(p) != "TBA" and str(p) != "GRADUADOS":
                clean_name = "".join([c for c in str(p) if c.isalnum() or c==' '])[:25]
                df[df['Profesor Asignado'] == p].to_excel(writer, sheet_name=f"User_{clean_name}", index=False)
    return out.getvalue()

# ==============================================================================
# 3. MODELOS DE DATOS 
# ==============================================================================
class Seccion:
    def __init__(self, cod, creditos, cupo, candidatos_raw, tipo_salon):
        self.cod = str(cod)
        self.creditos = int(creditos)
        self.cupo = int(cupo)
        if isinstance(candidatos_raw, list):
            self.cands = list(set([normalize_name(c) for c in candidatos_raw if c.strip()]))
        else:
            self.cands = list(set([normalize_name(c.strip()) for c in str(candidatos_raw).split(',') if c.strip() and str(c).upper() != 'NAN']))
        try:
            self.tipo_salon = int(round(float(tipo_salon)))
        except:
            self.tipo_salon = 1
        
        base = self.cod.split('-').upper().replace(" ", "")
        self.es_fusionable = base in ["MATE3171", "MATE3172", "MATE3173"]
        self.es_grande = self.cupo >= 85

class Profesor:
    def __init__(self, nombre, carga_min, carga_max, pref_dias, pref_horas,
                 bloqueo_dias, bloqueo_ini, bloqueo_fin,
                 preferencias_cursos, compensacion, acepta_grandes, cursos_intensivos=0):
        self.nombre = normalize_name(nombre)
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
                
        self.pref_horas = pref_horas if isinstance(pref_horas, str) else 'ANY'
        self.preferencias = [normalize_name(c) for c in preferencias_cursos if c and str(c).upper() != 'NAN'] if isinstance(preferencias_cursos, list) else []
        self.compensacion = str(compensacion).upper().strip() in ('SI', 'SÍ', 'YES', '1')
        self.acepta_grandes = int(acepta_grandes) if pd.notnull(acepta_grandes) and acepta_grandes != '' else 0
        try: self.cursos_intensivos = int(cursos_intensivos)
        except: self.cursos_intensivos = 0
        
        self.bloqueos = []
        if bloqueo_dias and isinstance(bloqueo_dias, str) and bloqueo_dias.strip():
            dias_map = {'L': 'Lu', 'M': 'Ma', 'MI': 'Mi', 'J': 'Ju', 'V': 'Vi'}
            dias_limpios = bloqueo_dias.upper().replace(' ', '').replace(',', '')
            dias_set = set()
            i = 0
            while i < len(dias_limpios):
                if dias_limpios[i:i+2] == 'MI':
                    dias_set.add('Mi')
                    i += 2
                else:
                    letra = dias_limpios[i]
                    if letra in dias_map: dias_set.add(dias_map[letra])
                    i += 1
            if dias_set:
                try:
                    start_min = str_to_mins(bloqueo_ini) if bloqueo_ini and pd.notnull(bloqueo_ini) else None
                    end_min = str_to_mins(bloqueo_fin) if bloqueo_fin and pd.notnull(bloqueo_fin) else None
                    if start_min is not None and end_min is not None:
                        self.bloqueos.append((dias_set, start_min, end_min))
                except: pass

def compatible_tipo(curso_tipo, salon_tipo):
    salon_cat = int(salon_tipo) if not isinstance(salon_tipo, float) else int(round(salon_tipo))
    if curso_tipo == 2: return salon_cat == 2
    if curso_tipo == 3: return salon_cat == 3
    return salon_cat != 2

# ==============================================================================
# 4. MOTOR ALGORITMO GENÉTICO (REEMPLAZA TABÚ)
# ==============================================================================
class GeneticScheduler:
    def __init__(self, df_cursos, df_profes, df_salones, df_graduados, zona, pop_size=50, mut_rate=0.1):
        self.zona = zona
        self.pop_size = pop_size
        self.mut_rate = mut_rate
        
        # Procesar Salones
        df_salones.columns = [c.strip().upper() for c in df_salones.columns]
        self.salones = []
        self.mega_salones = set()
        for _, r in df_salones.iterrows():
            codigo = str(r['CODIGO']).strip().upper()
            cap = int(r.get('CAPACIDAD', 25))
            tipo = float(r.get('TIPO', 1.0))
            self.salones.append({'CODIGO': codigo, 'CAPACIDAD': cap, 'TIPO': tipo})
            if any(x in codigo.replace(" ", "").replace("-", "") for x in ["FA", "FB", "FC"]):
                self.mega_salones.add(codigo)
                
        # Procesar Profesores
        self.profesores = {}
        if df_profes is not None and not df_profes.empty:
            df_profes.columns = [c.strip().upper() for c in df_profes.columns]
            for _, r in df_profes.iterrows():
                prefs = [normalize_name(str(r.get(col, ''))) for col in ['PREF1', 'PREF2', 'PREF3'] if pd.notnull(r.get(col))]
                prof = Profesor(
                    nombre=str(r['NOMBRE']).strip(), carga_min=r.get('CARGA_MIN', 0), carga_max=r.get('CARGA_MAX', 15),
                    pref_dias=r.get('PREF_DIAS', ''), pref_horas=r.get('PREF_HORAS', 'ANY'),
                    bloqueo_dias=r.get('BLOQUEO_DIAS', ''), bloqueo_ini=r.get('BLOQUEO_HORA_INI', ''), bloqueo_fin=r.get('BLOQUEO_HORA_FIN', ''),
                    preferencias_cursos=prefs, compensacion=r.get('COMPENSACION', 'NO'), acepta_grandes=r.get('ACEPTA_GRANDES', 0),
                    cursos_intensivos=r.get('CURSOS_INTENSIVOS', 0)
                )
                self.profesores[prof.nombre] = prof

        # Procesar Graduados (Doble Rol)
        self.graduados = {}
        if df_graduados is not None and not df_graduados.empty:
            df_graduados.columns = [c.strip().upper() for c in df_graduados.columns]
            for _, r in df_graduados.iterrows():
                nombre = normalize_name(str(r['NOMBRE']).strip())
                cursos = [normalize_name(c) for c in str(r.get('CURSOS_RECIBE', '')).split(',') if c.strip()]
                if nombre in self.profesores:
                    self.graduados[nombre] = set(cursos)

        # Procesar Cursos y Secciones (Redistribución inteligente)
        self.secciones = []
        df_cursos.columns = [c.strip().upper() for c in df_cursos.columns]
        for _, r in df_cursos.iterrows():
            cod_base = normalize_name(str(r['CODIGO']).strip())
            creditos = int(r['CREDITOS'])
            demanda = int(r.get('DEMANDA', 0))
            cupo_tipico = str(r.get('CUPO', '30'))
            cands = r.get('CANDIDATOS', '')
            tipo_salon = r.get('TIPO_SALON', 1)
            
            if ',' in cupo_tipico:
                capacidades = [int(c.strip()) for c in cupo_tipico.split(',') if c.strip().isdigit()]
                for cap in capacidades:
                    self.secciones.append(Seccion(f"{cod_base}-{len(self.secciones)+1:02d}", creditos, cap, cands, tipo_salon))
            else:
                cupo = int(cupo_tipico)
                if demanda <= 0:
                    self.secciones.append(Seccion(f"{cod_base}-01", creditos, cupo, cands, tipo_salon))
                else:
                    secciones_completas = demanda // cupo
                    resto = demanda % cupo
                    umbral = max(1, int(cupo * 0.3))
                    
                    if resto == 0 or secciones_completas == 0:
                        num = max(1, secciones_completas)
                        dem_real = demanda if secciones_completas == 0 else cupo
                        for i in range(num):
                            self.secciones.append(Seccion(f"{cod_base}-{i+1:02d}", creditos, dem_real, cands, tipo_salon))
                    elif resto <= umbral:
                        extra_por_seccion = resto // secciones_completas
                        extra_resto = resto % secciones_completas
                        for i in range(secciones_completas):
                            cap_final = cupo + extra_por_seccion + (1 if i < extra_resto else 0)
                            self.secciones.append(Seccion(f"{cod_base}-{i+1:02d}", creditos, cap_final, cands, tipo_salon))
                    else:
                        for i in range(secciones_completas + 1):
                            cap_final = resto if i == secciones_completas else cupo
                            self.secciones.append(Seccion(f"{cod_base}-{i+1:02d}", creditos, cap_final, cands, tipo_salon))

        # Zonas y Tiempos
        if zona == "CENTRAL":
            self.hora_universal = (630, 750)   # 10:30 - 12:30
            self.limite_operativo = (450, 1110) # 7:30 - 18:30
        else:
            self.hora_universal = (600, 720)   # 10:00 - 12:00
            self.limite_operativo = (420, 1080) # 7:00 - 18:00
            
        self.tiempos_validos = list(range(self.limite_operativo, self.limite_operativo - 50, 30))

    def get_sec_creditos(self, s, prof_name):
        if prof_name in self.profesores and self.profesores[prof_name].compensacion:
            return get_creditos_reales(s.creditos, s.cupo)
        return float(s.creditos)

    def _generar_gen(self, sec):
        # Escoger Profesor
        cands_validos = [p for p in sec.cands if p in self.profesores]
        if not cands_validos:
            prof = "GRADUADOS" if "GRADUADOS" in sec.cands else "TBA"
        else:
            prof = random.choice(cands_validos)
            
        # Escoger Salón
        salones_validos = [sl for sl in self.salones if sl['CAPACIDAD'] >= sec.cupo and compatible_tipo(sec.tipo_salon, sl['TIPO'])]
        salon = random.choice(salones_validos)['CODIGO'] if salones_validos else random.choice(self.salones)['CODIGO']
        
        # Escoger Tiempo
        patrones = PATRONES.get(sec.creditos, PATRONES)
        patron = random.choice(patrones)
        ini = random.choice(self.tiempos_validos)
        
        return {'seccion': sec, 'profesor': prof, 'salon': salon, 'patron': patron, 'ini': ini}

    def crear_individuo(self):
        return [self._generar_gen(sec) for sec in self.secciones]

    def calcular_fitness(self, individuo):
        conflicts = 0
        soft_penalty = 0
        occ_prof = {}
        occ_salon = {}
        carga_prof = {p: 0.0 for p in self.profesores}
        carga_prof["GRADUADOS"] = 0.0
        carga_prof["TBA"] = 0.0
        horarios_prof = {p: {} for p in self.profesores}

        for i, asign in enumerate(individuo):
            s = asign['seccion']
            prof = asign['profesor']
            salon = asign['salon']
            patron = asign['patron']
            ini = asign['ini']

            if prof == "TBA" or salon == "TBA": conflicts += 10000; continue

            # Restricciones de Salón
            salon_info = next((sl for sl in self.salones if sl['CODIGO'] == salon), None)
            if salon_info and salon_info['CAPACIDAD'] < s.cupo: conflicts += 10000
            if salon_info and not compatible_tipo(s.tipo_salon, salon_info['TIPO']): conflicts += 10000

            # Restricciones de Profesor
            if prof in self.profesores:
                prof_obj = self.profesores[prof]
                if prof_obj.acepta_grandes == 0 and s.es_grande: conflicts += 10000
                
                es_intensivo = any(c >= 3 for c in patron['days'].values())
                puede_ser_intensivo = any(any(c >= 3 for c in p['days'].values()) for p in PATRONES.get(s.creditos, PATRONES))
                
                if prof_obj.cursos_intensivos == 0 and es_intensivo: conflicts += 10000
                elif prof_obj.cursos_intensivos == 1 and puede_ser_intensivo and not es_intensivo: conflicts += 10000

                if prof_obj.pref_horas == 'AM' and ini >= 720: soft_penalty += 30
                elif prof_obj.pref_horas == 'PM' and ini < 720: soft_penalty += 30
                
                if prof_obj.pref_dias_set:
                    for dia in patron['days'].keys():
                        if dia not in prof_obj.pref_dias_set: soft_penalty += 15

                for (dias_set, start, end) in prof_obj.bloqueos:
                    for dia in patron['days'].keys():
                        if dia in dias_set:
                            fin = ini + int(patron['days'][dia] * 50)
                            if max(ini, start) < min(fin, end): conflicts += 10000

            # Tiempos, Hora Universal y Cruces
            for dia, contrib in patron['days'].items():
                fin = ini + int(contrib * 50)
                if dia in ["Ma", "Ju"] and max(ini, self.hora_universal) < min(fin, self.hora_universal): conflicts += 10000
                if contrib >= 3 and ini < 930: conflicts += 10000
                if fin > self.limite_operativo or ini < self.limite_operativo: conflicts += 10000

                # Cruce Profesores
                if prof != "GRADUADOS":
                    clave_p = (prof, dia)
                    if clave_p not in occ_prof: occ_prof[clave_p] = []
                    for (ini_ex, fin_ex) in occ_prof[clave_p]:
                        if max(ini, ini_ex) < min(fin, fin_ex): conflicts += 10000
                    occ_prof[clave_p].append((ini, fin))

                # Cruce Salones
                clave_s = (salon, dia)
                if clave_s not in occ_salon: occ_salon[clave_s] = []
                for (ini_ex, fin_ex, cupo_ex, fus_ex) in occ_salon[clave_s]:
                    if max(ini, ini_ex) < min(fin, fin_ex):
                        if salon in self.mega_salones and s.es_fusionable and fus_ex and s.cupo + cupo_ex <= salon_info['CAPACIDAD']: continue
                        conflicts += 10000
                occ_salon[clave_s].append((ini, fin, s.cupo, s.es_fusionable))
                
                if prof in horarios_prof: horarios_prof[prof].setdefault(dia, []).append((ini, fin))

            # Cargas
            if prof in carga_prof:
                carga_prof[prof] += self.get_sec_creditos(s, prof)

            # Doble Rol (Rf10)
            if prof in self.graduados:
                cursos_recibidos = self.graduados[prof]
                for j, otro in enumerate(individuo):
                    if j != i and otro['seccion'].cod.split('-') in cursos_recibidos:
                        for dia, contrib in patron['days'].items():
                            for dia2, contrib2 in otro['patron']['days'].items():
                                if dia == dia2:
                                    fin_actual = ini + int(contrib * 50)
                                    fin_otro = otro['ini'] + int(contrib2 * 50)
                                    if max(ini, otro['ini']) < min(fin_actual, fin_otro):
                                        conflicts += 10000

        # Cargas finales y Compactación
        for p, carga in carga_prof.items():
            if p in self.profesores:
                prof_obj = self.profesores[p]
                if carga > prof_obj.carga_max: conflicts += int((carga - prof_obj.carga_max) * 5000)
                elif carga < prof_obj.carga_min: soft_penalty += int((prof_obj.carga_min - carga) * 100)

        for p, dias_horarios in horarios_prof.items():
            for dia, intervalos in dias_horarios.items():
                if len(intervalos) > 1:
                    intervalos.sort()
                    for k in range(len(intervalos) - 1):
                        hueco = intervalos[k+1] - intervalos[k]
                        if hueco > 0: soft_penalty += (hueco // 30) * 10 

        costo_total = (conflicts * 10000) + soft_penalty
        return 1.0 / (1.0 + costo_total), conflicts, soft_penalty

    def cruzar(self, p1, p2):
        # Uniform Crossover
        h1, h2 = [], []
        for i in range(len(p1)):
            if random.random() > 0.5:
                h1.append(deepcopy(p1[i]))
                h2.append(deepcopy(p2[i]))
            else:
                h1.append(deepcopy(p2[i]))
                h2.append(deepcopy(p1[i]))
        return h1, h2

    def mutar(self, individuo):
        for i in range(len(individuo)):
            if random.random() < self.mut_rate:
                individuo[i] = self._generar_gen(individuo[i]['seccion'])
        return individuo

    def ejecutar(self, generaciones, status_placeholder):
        poblacion = [self.crear_individuo() for _ in range(self.pop_size)]
        mejor_ind, mejor_fit = None, -1
        mejor_conf, mejor_soft = float('inf'), float('inf')
        
        bar = st.progress(0)
        
        for gen in range(generaciones):
            scores = []
            for ind in poblacion:
                fit, conf, soft = self.calcular_fitness(ind)
                scores.append((ind, fit, conf, soft))
                if fit > mejor_fit:
                    mejor_fit, mejor_ind, mejor_conf, mejor_soft = fit, ind, conf, soft
            
            if gen % 5 == 0 or gen == generaciones - 1:
                status_placeholder.markdown(f"**Generación {gen}/{generaciones}** | Colisiones Duras: `{mejor_conf}` | Penalidades Suaves: `{mejor_soft}`")
            bar.progress((gen + 1) / generaciones)
            
            if mejor_conf == 0 and mejor_soft == 0:
                status_placeholder.success("¡Solución PERFECTA encontrada!")
                break
                
            scores.sort(key=lambda x: x, reverse=True)
            nueva_pob = [s for s in scores[:int(self.pop_size * 0.1)]] # 10% Elitismo
            
            while len(nueva_pob) < self.pop_size:
                padre1 = max(random.sample(scores, 3), key=lambda x: x)
                padre2 = max(random.sample(scores, 3), key=lambda x: x)
                h1, h2 = self.cruzar(padre1, padre2)
                nueva_pob.extend([self.mutar(h1), self.mutar(h2)])
                
            poblacion = nueva_pob[:self.pop_size]
            
        return mejor_ind, mejor_conf, mejor_soft

# ==============================================================================
# 5. UI STREAMLIT APP
# ==============================================================================
st.sidebar.markdown("### 1. Datos de Entrada")
uploaded_file = st.sidebar.file_uploader("Sube el archivo Excel Maestro", type=['xlsx'])
zona = st.sidebar.selectbox("Zona de Horario", ["CENTRAL", "OTRA"])

st.sidebar.markdown("### 2. Parámetros del Algoritmo Genético")
pop_size = st.sidebar.slider("Tamaño de Población", 20, 200, 50)
generaciones = st.sidebar.slider("Generaciones Máximas", 50, 2000, 300)
mut_rate = st.sidebar.slider("Tasa de Mutación", 0.01, 0.5, 0.1)

if uploaded_file:
    try:
        xls = pd.ExcelFile(uploaded_file)
        hojas = xls.sheet_names
        
        if not all(h in hojas for h in ['Cursos', 'Profesores', 'Salones']):
            st.error("El archivo debe tener las hojas: 'Cursos', 'Profesores' y 'Salones'.")
        else:
            df_cursos = pd.read_excel(xls, 'Cursos')
            df_profesores = pd.read_excel(xls, 'Profesores')
            df_salones = pd.read_excel(xls, 'Salones')
            df_graduados = pd.read_excel(xls, 'Graduados') if 'Graduados' in hojas else None
            
            st.success("✅ Datos cargados correctamente. Listo para evolucionar.")
            
            if st.button("🚀 INICIAR OPTIMIZACIÓN GENÉTICA"):
                status_ph = st.empty()
                ga = GeneticScheduler(df_cursos, df_profesores, df_salones, df_graduados, zona, pop_size, mut_rate)
                
                mejor_horario, conf, soft = ga.ejecutar(generaciones, status_ph)
                
                if conf == 0:
                    st.success("🎉 Horario 100% Factible (Cero Choques).")
                else:
                    st.warning(f"⚠️ El algoritmo terminó con {conf} choques (Restricciones Duras). Considera aumentar las generaciones o la población.")
                
                # Transformar a DataFrame
                output_data = []
                for gen in mejor_horario:
                    output_data.append({
                        "ID Sección": gen['seccion'].cod,
                        "Cupo": gen['seccion'].cupo,
                        "Créditos": gen['seccion'].creditos,
                        "Profesor Asignado": gen['profesor'],
                        "Salón": gen['salon'],
                        "Días y Horas": format_horario(gen['patron'], gen['ini'])
                    })
                
                df_out = pd.DataFrame(output_data)
                st.dataframe(df_out, use_container_width=True)
                
                # Descarga dividida por profesor (usando tu método exportar_todo)
                excel_data = exportar_todo(df_out)
                st.download_button("📥 Descargar Horario Final (.xlsx)", excel_data, "Horario_UPRM_Evolucionado.xlsx", "application/vnd.ms-excel")

    except Exception as e:
        st.error(f"Error leyendo el archivo: {str(e)}")
else:
    st.info("👈 Por favor, sube tu archivo `.xlsx` en el panel lateral.")
