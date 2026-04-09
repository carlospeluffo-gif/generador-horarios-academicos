import streamlit as st
import pandas as pd
import numpy as np
import random
import io
import time
import math
from datetime import time as dtime
import matplotlib.pyplot as plt
from copy import deepcopy

# ==============================================================================
# 1. ESTÉTICA (fondo blanco)
# ==============================================================================
st.set_page_config(page_title="UPRM Scheduler Platinum v14", page_icon="🏛️", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #ffffff; color: #1e1e1e; }
    .math-header {
        display: flex; justify-content: space-between; align-items: center;
        padding: 20px 40px; background: #f5f5f5; border-bottom: 3px solid #D4AF37;
        margin-bottom: 30px; border-radius: 0 0 20px 20px;
    }
    .title-box { text-align: center; }
    .abstract-icon { font-size: 2rem; color: #D4AF37; border: 1px solid #D4AF37; padding: 5px 15px; border-radius: 20px; }
    h1 { font-family: 'Playfair Display', serif; color: #8E6E13; font-size: 2.5rem; }
    .glass-card { background: #fefefe; border-radius: 15px; padding: 20px; border: 1px solid #e0e0e0; box-shadow: 0 2px 8px rgba(0,0,0,0.05); margin-bottom: 20px; }
    .stButton>button { background: linear-gradient(135deg, #8E6E13, #D4AF37); color: white; border-radius: 8px; height: 45px; }
    [data-testid="stSidebar"] { background-color: #fafafa; border-right: 1px solid #ddd; }
    .status-badge { background: #f0f0f0; border: 1px solid #D4AF37; color: #8E6E13; padding: 8px; border-radius: 8px; text-align: center; }
</style>
<div class="math-header">
    <div class="abstract-icon">Δx</div>
    <div class="title-box"><h1>UPRM TIMETABLE SYSTEM</h1><p style="color:#666;">Optimización con compacidad horaria</p></div>
    <div class="abstract-icon">∞</div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. UTILIDADES (sin cambios)
# ==============================================================================
COMPENSACION_TABLE = [
    (1,1,44,0.0),(1,45,74,0.5),(1,75,104,1.0),(1,105,134,1.5),(1,135,164,2.0),
    (2,1,37,0.0),(2,38,52,0.5),(2,53,67,1.0),(2,68,82,1.5),(2,83,97,2.0),
    (2,98,112,2.5),(2,113,127,3.0),(2,128,142,3.5),(2,143,147,4.0),
    (3,1,34,0.0),(3,35,44,0.5),(3,45,54,1.0),(3,55,64,1.5),(3,65,74,2.0),
    (3,75,84,2.5),(3,85,94,3.0),(3,95,104,3.5),(3,105,114,4.0),(3,115,124,4.5),
    (3,125,134,5.0),(3,135,144,5.5),(3,145,154,6.0),
    (4,1,33,0.0),(4,34,41,0.5),(4,42,48,1.0),(4,49,56,1.5),(4,57,63,2.0),
    (4,64,71,2.5),(4,72,78,3.0),(4,79,86,3.5),(4,87,93,4.0),(4,94,101,4.5),
    (4,102,108,5.0),(4,109,116,5.5),(4,117,123,6.0),(4,124,131,6.5),(4,132,138,7.0),
    (4,139,146,7.5),(4,147,153,8.0),
    (5,1,32,0.0),(5,33,38,0.5),(5,39,44,1.0),(5,45,50,1.5),(5,51,56,2.0),
    (5,57,62,2.5),(5,63,68,3.0),(5,69,74,3.5),(5,75,80,4.0),(5,81,86,4.5),
    (5,87,92,5.0),(5,93,98,5.5),(5,99,104,6.0),(5,105,110,6.5),(5,111,116,7.0),
    (5,117,122,7.5),(5,123,128,8.0)
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
        {"name": "Lu-Mi-Vi", "days": {"Lu":1, "Mi":1, "Vi":1}},
        {"name": "Ma-Ju", "days": {"Ma":1.5, "Ju":1.5}},
        {"name": "Lu (Intensivo)", "days": {"Lu":3}},
        {"name": "Ma (Intensivo)", "days": {"Ma":3}},
        {"name": "Mi (Intensivo)", "days": {"Mi":3}},
        {"name": "Ju (Intensivo)", "days": {"Ju":3}},
        {"name": "Vi (Intensivo)", "days": {"Vi":3}},
    ],
    4: [
        {"name": "Lu-Ma-Mi-Ju", "days": {"Lu":1,"Ma":1,"Mi":1,"Ju":1}},
        {"name": "Lu-Ma-Mi-Vi", "days": {"Lu":1,"Ma":1,"Mi":1,"Vi":1}},
        {"name": "Lu-Ma-Ju-Vi", "days": {"Lu":1,"Ma":1,"Ju":1,"Vi":1}},
        {"name": "Lu-Mi-Ju-Vi", "days": {"Lu":1,"Mi":1,"Ju":1,"Vi":1}},
        {"name": "Ma-Mi-Ju-Vi", "days": {"Ma":1,"Mi":1,"Ju":1,"Vi":1}},
        {"name": "Lu-Mi", "days": {"Lu":2,"Mi":2}},
        {"name": "Lu-Vi", "days": {"Lu":2,"Vi":2}},
        {"name": "Ma-Ju", "days": {"Ma":2,"Ju":2}},
        {"name": "Mi-Vi", "days": {"Mi":2,"Vi":2}},
    ],
    5: [
        {"name": "Lu-Ma-Mi-Ju-Vi", "days": {"Lu":1,"Ma":1,"Mi":1,"Ju":1,"Vi":1}},
        {"name": "Lu-Ma-Mi-Vi", "days": {"Lu":1,"Ma":1,"Mi":1,"Vi":2}},
        {"name": "Lu-Ma-Ju-Vi", "days": {"Lu":1,"Ma":1,"Ju":1,"Vi":2}},
        {"name": "Lu-Mi-Ju-Vi", "days": {"Lu":1,"Mi":1,"Ju":1,"Vi":2}},
        {"name": "Ma-Mi-Ju-Vi", "days": {"Ma":1,"Mi":1,"Ju":1,"Vi":2}},
        {"name": "Lu-Mi-Vi", "days": {"Lu":2,"Mi":2,"Vi":1}},
        {"name": "Ma-Ju-Vi", "days": {"Ma":1.5,"Ju":1.5,"Vi":2}},
        {"name": "Lu-Ma-Mi", "days": {"Lu":2,"Ma":1,"Mi":2}},
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
            if str(p) not in ["TBA","GRADUADOS"]:
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
            t = float(tipo_salon)
            self.tipo_salon = 3 if abs(t-1.3)<0.01 else int(round(t))
        except:
            self.tipo_salon = 1
        self.es_ayudantia = es_ayudantia
        base = self.cod.split('-')[0].upper().replace(" ", "")
        self.es_fusionable = base in ["MATE3171","MATE3172","MATE3173"]
        self.prof_preasignado = None
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
            for token in pref_dias.replace(',',' ').upper().split():
                if token in ('L','LU'): self.pref_dias_set.add('Lu')
                elif token in ('M','MA'): self.pref_dias_set.add('Ma')
                elif token in ('W','MI'): self.pref_dias_set.add('Mi')
                elif token in ('J','JU'): self.pref_dias_set.add('Ju')
                elif token in ('V','VI'): self.pref_dias_set.add('Vi')
                elif token in ('LU','MA','MI','JU','VI'): self.pref_dias_set.add(token)
        self.pref_horas = pref_horas if isinstance(pref_horas, str) else 'ANY'
        self.preferencias = []
        if isinstance(preferencias_cursos, list):
            self.preferencias = [c.upper().strip() for c in preferencias_cursos if c and str(c).upper() != 'NAN']
        self.compensacion = str(compensacion).upper().strip() in ('SI','SÍ','YES','1')
        self.acepta_grandes = int(acepta_grandes) if pd.notnull(acepta_grandes) and acepta_grandes != '' else 0
        try:
            self.cursos_intensivos = int(cursos_intensivos)
        except:
            self.cursos_intensivos = 0
        self.bloqueos = []
        if bloqueo_dias and isinstance(bloqueo_dias, str) and bloqueo_dias.strip():
            dias_map = {'L':'Lu','M':'Ma','MI':'Mi','J':'Ju','V':'Vi'}
            dias_limpios = bloqueo_dias.upper().replace(' ','')
            if ',' in dias_limpios: dias_limpios = dias_limpios.replace(',','')
            dias_set = set()
            i = 0
            while i < len(dias_limpios):
                if dias_limpios[i:i+2] == 'MI':
                    dias_set.add('Mi'); i+=2
                else:
                    letra = dias_limpios[i]
                    if letra in dias_map: dias_set.add(dias_map[letra])
                    i+=1
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

def compatible_tipo(curso_tipo, salon_tipo):
    if isinstance(salon_tipo, float):
        if 1.9 <= salon_tipo <= 2.1: salon_cat = 2
        elif salon_tipo >= 2.9: salon_cat = 3
        else: salon_cat = 1
    else: salon_cat = int(salon_tipo)
    if curso_tipo == 2: return salon_cat == 2
    if curso_tipo == 3: return salon_cat == 3
    return salon_cat != 2

# ==============================================================================
# 4. MOTOR DE OPTIMIZACIÓN (VERSIÓN ORIGINAL + COMPACIDAD)
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
            cap = int(r['CAPACIDAD']) if 'CAPACIDAD' in r else 25
            tipo = float(r['TIPO']) if 'TIPO' in r else 1.0
            self.salones.append({'CODIGO':codigo, 'CAPACIDAD':cap, 'TIPO':tipo})
            if any(x in codigo.replace(" ","").replace("-","") for x in ["FA","FB","FC"]):
                self.mega_salones.add(codigo)
        self.salon_tipo = {s['CODIGO']: s['TIPO'] for s in self.salones}
        self.salon_capacidad = {s['CODIGO']: s['CAPACIDAD'] for s in self.salones}
        # Profesores
        self.profesores = {}
        if df_profes is not None and not df_profes.empty:
            df_profes.columns = [c.strip().upper() for c in df_profes.columns]
            for _, r in df_profes.iterrows():
                prefs = [str(r.get(col,'')).strip().upper() for col in ['PREF1','PREF2','PREF3'] if pd.notnull(r.get(col)) and str(r.get(col)).strip().upper()!='NAN']
                prof = Profesor(
                    nombre=str(r['NOMBRE']).strip().upper(),
                    carga_min=r.get('CARGA_MIN',0),
                    carga_max=r.get('CARGA_MAX',15),
                    pref_dias=r.get('PREF_DIAS',''),
                    pref_horas=r.get('PREF_HORAS','ANY'),
                    bloqueo_dias=r.get('BLOQUEO_DIAS',''),
                    bloqueo_ini=r.get('BLOQUEO_HORA_INI',''),
                    bloqueo_fin=r.get('BLOQUEO_HORA_FIN',''),
                    preferencias_cursos=prefs,
                    compensacion=r.get('COMPENSACION','NO'),
                    acepta_grandes=r.get('ACEPTA_GRANDES',0),
                    cursos_intensivos=r.get('CURSOS_INTENSIVOS',0)
                )
                self.profesores[prof.nombre] = prof
        # Cursos y Secciones (MÉTODO ORIGINAL: siempre cubrir toda la demanda)
        self.secciones = []
        df_cursos.columns = [c.strip().upper() for c in df_cursos.columns]
        cursos_agrupados = {}
        for _, r in df_cursos.iterrows():
            cod_base = str(r['CODIGO']).strip().upper()
            if cod_base not in cursos_agrupados:
                t = r.get('TIPO_SALON',1)
                try:
                    t_val = float(t)
                    tipo_salon = 3 if abs(t_val-1.3)<0.01 else int(round(t_val))
                except:
                    tipo_salon = 1
                cursos_agrupados[cod_base] = {
                    'creditos': int(r['CREDITOS']),
                    'demanda': int(r.get('DEMANDA',0)),
                    'cupo_tipico': int(r.get('CUPO','30')),
                    'candidatos': r.get('CANDIDATOS',''),
                    'tipo_salon': tipo_salon
                }
            else:
                cursos_agrupados[cod_base]['demanda'] += int(r.get('DEMANDA',0))

        for cod_base, datos in cursos_agrupados.items():
            demanda_total = datos['demanda']
            cupo_tipico = datos['cupo_tipico']
            candidatos_list = [c.strip().upper() for c in str(datos['candidatos']).split(',') if c.strip() and str(c).upper() != 'NAN']
            acepta_comp = any(c in self.profesores and self.profesores[c].compensacion for c in candidatos_list)
            if acepta_comp and demanda_total > cupo_tipico:
                cupo_efectivo = min(demanda_total, 85)
            else:
                cupo_efectivo = cupo_tipico
            num_secciones = math.ceil(demanda_total / cupo_efectivo) if demanda_total>0 else 1
            est_sec = [cupo_efectivo] * (num_secciones-1)
            resto = demanda_total - sum(est_sec)
            est_sec.append(resto if resto>0 else cupo_efectivo)
            for i, cupo in enumerate(est_sec):
                self.secciones.append(Seccion(f"{cod_base}-{i+1:02d}", datos['creditos'], cupo, datos['candidatos'], datos['tipo_salon']))

        self._preasignar_profesores_robusto()

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
        # (mismo código original, sin cambios)
        carga_actual = {p:0.0 for p in self.profesores}
        carga_actual["GRADUADOS"] = 0.0
        carga_actual["TBA"] = 0.0
        capacidad_restante = {p.nombre: p.carga_max for p in self.profesores.values()}
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
            if len(cands_validos)==1:
                secciones_unicas.append(s)
            else:
                secciones_multiple.append(s)
        for s in secciones_unicas:
            prof = s.cands[0]
            creditos = self.get_sec_creditos(s, prof)
            s.prof_preasignado = prof
            carga_actual[prof] += creditos
            capacidad_restante[prof] -= creditos
        preferencias = {}
        for s in secciones_multiple:
            preferencias[s] = {}
            for prof in s.cands:
                if prof in self.profesores:
                    prioridad = self.profesores[prof].prioridad_curso(s.cod)
                    if s.es_grande and self.profesores[prof].acepta_grandes==1:
                        prioridad += 0.5
                    preferencias[s][prof] = prioridad
                else:
                    preferencias[s][prof] = 0.0
        secciones_multiple.sort(key=lambda s: (len(s.cands), -max(preferencias[s].values())))
        for s in secciones_multiple:
            candidatos_ordenados = sorted(s.cands, key=lambda p: preferencias[s].get(p,0), reverse=True)
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
            for p,c in carga_actual.items():
                if p in self.profesores:
                    if c < self.profesores[p].carga_min - 1.5:
                        pen += (self.profesores[p].carga_min - c)*10
                    elif c > self.profesores[p].carga_max + 1.5:
                        pen += (c - self.profesores[p].carga_max)*10
            return pen
        penalidad_actual = calc_penalidad()
        T = 100.0
        for _ in range(30000):
            if penalidad_actual == 0: break
            s = random.choice(self.secciones)
            prof_viejo = s.prof_preasignado
            if prof_viejo not in self.profesores: continue
            cands = [p for p in s.cands if p in self.profesores and p != prof_viejo]
            if not cands: continue
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
                if T>0.01 and random.random() < math.exp(-delta/T):
                    penalidad_actual = nueva_pen
                    s.prof_preasignado = nuevo_prof
                else:
                    carga_actual[prof_viejo] += creditos_viejos
                    carga_actual[nuevo_prof] -= creditos_nuevos
            T *= 0.995

    # ---------- NUEVA RESTRICCIÓN DE COMPACIDAD (solo penaliza mezcla MWF/TTH) ----------
    def _penalizar_mezcla_dias(self, sol):
        """Penaliza si un profesor mezcla días L,Mi,Vi con Ma,Ju, a menos que tenga cursos de 4/5 créditos o pref_dias >=4"""
        prof_dias = {}
        for asign in sol:
            prof = asign['profesor']
            if prof in ["GRADUADOS","TBA"] or prof not in self.profesores:
                continue
            days = set(asign['patron']['days'].keys())
            creditos = asign['seccion'].creditos
            if prof not in prof_dias:
                prof_dias[prof] = {'days': set(), 'max_creditos': 0}
            prof_dias[prof]['days'].update(days)
            prof_dias[prof]['max_creditos'] = max(prof_dias[prof]['max_creditos'], creditos)
        penalty = 0
        mwf = {'Lu','Mi','Vi'}
        tth = {'Ma','Ju'}
        for prof, info in prof_dias.items():
            days = info['days']
            tiene_mwf = any(d in mwf for d in days)
            tiene_tth = any(d in tth for d in days)
            if tiene_mwf and tiene_tth:
                # Excepciones: cursos de 4 o 5 créditos, o profesor con preferencia de 4+ días
                if info['max_creditos'] >= 4:
                    continue
                prof_obj = self.profesores[prof]
                if len(prof_obj.pref_dias_set) >= 4:
                    continue
                penalty += 10000   # fuerte
        return penalty

    def _costo_total(self, sol):
        conflicts = 0
        soft_penalty = 0
        occ_prof = {}
        occ_salon = {}
        carga_prof = {p:0.0 for p in self.profesores}
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

            salon_info = next((sl for sl in self.salones if sl['CODIGO']==salon), None)
            if salon_info and salon_info['CAPACIDAD'] < s.cupo:
                conflicts += 10000
            if salon_info and not compatible_tipo(s.tipo_salon, salon_info['TIPO']):
                conflicts += 10000

            if prof in self.profesores:
                prof_obj = self.profesores[prof]
                if prof_obj.acepta_grandes == 0 and s.es_grande:
                    conflicts += 10000

            if prof in carga_prof:
                carga_prof[prof] += self.get_sec_creditos(s, prof)

            es_intensivo = any(c>=3 for c in patron['days'].values())
            puede_ser_intensivo = any(any(c>=3 for c in p['days'].values()) for p in PATRONES.get(s.creditos, PATRONES[3]))

            if prof != "GRADUADOS" and prof in self.profesores:
                prof_obj = self.profesores[prof]
                if prof_obj.cursos_intensivos == 0 and es_intensivo:
                    conflicts += 10000
                elif prof_obj.cursos_intensivos == 1 and puede_ser_intensivo and not es_intensivo:
                    conflicts += 10000

                # Preferencias suaves
                if prof_obj.pref_horas == 'AM' and ini >= 720:
                    soft_penalty += 30
                elif prof_obj.pref_horas == 'PM' and ini < 720:
                    soft_penalty += 30
                if prof_obj.pref_dias_set:
                    for dia in patron['days'].keys():
                        if dia not in prof_obj.pref_dias_set:
                            soft_penalty += 15

                # Bloqueos
                for (dias_set, start, end) in prof_obj.bloqueos:
                    for dia in patron['days'].keys():
                        if dia in dias_set:
                            fin = ini + int(patron['days'][dia]*50)
                            if max(ini, start) < min(fin, end):
                                conflicts += 10000

            for dia, contrib in patron['days'].items():
                fin = ini + int(contrib*50)
                if dia in ["Ma","Ju"] and max(ini, self.hora_universal[0]) < min(fin, self.hora_universal[1]):
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
                            if s.cupo + cupo_ex <= self.salon_capacidad.get(salon,0):
                                continue
                        conflicts += 10000
                occ_salon[clave_s].append((ini, fin, s.cupo, s.es_fusionable))

        for prof, carga in carga_prof.items():
            prof_obj = self.profesores.get(prof)
            if prof_obj:
                if carga > prof_obj.carga_max + 1.5:
                    conflicts += 10000
                if carga < prof_obj.carga_min - 1.5:
                    conflicts += 10000

        # Penalización suave por consistencia de salón (original, leve)
        salones_por_prof_tipo = {}
        for asign in sol:
            prof = asign['profesor']
            if prof not in ["GRADUADOS","TBA"] and prof in self.profesores:
                salon = asign['salon']
                tipo = self.salon_tipo.get(salon,1)
                key = (prof, tipo)
                if key not in salones_por_prof_tipo:
                    salones_por_prof_tipo[key] = set()
                salones_por_prof_tipo[key].add(salon)
        for (prof, tipo), salones in salones_por_prof_tipo.items():
            if len(salones) > 1:
                soft_penalty += (len(salones)-1)*2

        # Añadir penalización por mezcla de días (nueva restricción fuerte)
        conflicts += self._penalizar_mezcla_dias(sol)

        return conflicts + soft_penalty

    def _obtener_conflictos(self, sol):
        # Similar al original, pero incluye la nueva restricción en la lista
        conflictos_list = []
        occ_prof = {}
        occ_salon = {}
        carga_prof = {p:0.0 for p in self.profesores}
        carga_prof["GRADUADOS"] = 0.0
        carga_prof["TBA"] = 0.0

        for asign in sol:
            s = asign['seccion']
            prof = asign['profesor']
            salon = asign['salon']
            patron = asign['patron']
            ini = asign['ini']

            if prof == "TBA": conflictos_list.append(f"Sección {s.cod}: profesor TBA")
            if salon == "TBA": conflictos_list.append(f"Sección {s.cod}: salón TBA")

            salon_info = next((sl for sl in self.salones if sl['CODIGO']==salon), None)
            if salon_info and salon_info['CAPACIDAD'] < s.cupo:
                conflictos_list.append(f"Sección {s.cod}: capacidad insuficiente en {salon}")
            if salon_info and not compatible_tipo(s.tipo_salon, salon_info['TIPO']):
                conflictos_list.append(f"Sección {s.cod}: tipo incompatible (requiere {s.tipo_salon}, tiene {salon_info['TIPO']})")

            if prof in carga_prof:
                carga_prof[prof] += self.get_sec_creditos(s, prof)

            es_intensivo = any(c>=3 for c in patron['days'].values())
            puede_ser_intensivo = any(any(c>=3 for c in p['days'].values()) for p in PATRONES.get(s.creditos, PATRONES[3]))

            if prof != "GRADUADOS" and prof in self.profesores:
                prof_obj = self.profesores[prof]
                if prof_obj.cursos_intensivos == 0 and es_intensivo:
                    conflictos_list.append(f"Sección {s.cod}: Prof {prof} tiene intensivo pero no permite")
                elif prof_obj.cursos_intensivos == 1 and puede_ser_intensivo and not es_intensivo:
                    conflictos_list.append(f"Sección {s.cod}: Prof {prof} no tiene intensivo pero requiere")
                if prof_obj.acepta_grandes == 0 and s.es_grande:
                    conflictos_list.append(f"Sección {s.cod}: Prof {prof} no acepta grandes")
                for (dias_set, start, end) in prof_obj.bloqueos:
                    for dia in patron['days'].keys():
                        if dia in dias_set:
                            fin = ini + int(patron['days'][dia]*50)
                            if max(ini, start) < min(fin, end):
                                conflictos_list.append(f"Bloqueo de {prof} el {dia} {mins_to_str(start)}-{mins_to_str(end)}")

            for dia, contrib in patron['days'].items():
                fin = ini + int(contrib*50)
                if dia in ["Ma","Ju"] and max(ini, self.hora_universal[0]) < min(fin, self.hora_universal[1]):
                    conflictos_list.append(f"Hora universal violada {dia}")
                if s.creditos == 3 and contrib >= 3 and ini < 930:
                    conflictos_list.append(f"Intensivo de 3 créditos antes de 9:30")
                if fin > self.limite_operativo[1] or ini < self.limite_operativo[0]:
                    conflictos_list.append(f"Fuera de ventana operativa")
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
                        if not (salon in self.mega_salones and s.es_fusionable and fus_ex and s.cupo+cupo_ex <= self.salon_capacidad.get(salon,0)):
                            conflictos_list.append(f"Cruce de salón {salon} el {dia}")
                occ_salon[clave_s].append((ini, fin, s.cupo, s.es_fusionable))

        for prof, carga in carga_prof.items():
            prof_obj = self.profesores.get(prof)
            if prof_obj:
                if carga > prof_obj.carga_max + 1.5:
                    conflictos_list.append(f"{prof} excede carga máxima ({carga:.1f} > {prof_obj.carga_max})")
                if carga < prof_obj.carga_min - 1.5:
                    conflictos_list.append(f"{prof} no alcanza carga mínima ({carga:.1f} < {prof_obj.carga_min})")

        # Nueva restricción de mezcla de días
        prof_dias = {}
        for asign in sol:
            prof = asign['profesor']
            if prof in ["GRADUADOS","TBA"] or prof not in self.profesores: continue
            days = set(asign['patron']['days'].keys())
            creditos = asign['seccion'].creditos
            if prof not in prof_dias:
                prof_dias[prof] = {'days':set(), 'max_creditos':0}
            prof_dias[prof]['days'].update(days)
            prof_dias[prof]['max_creditos'] = max(prof_dias[prof]['max_creditos'], creditos)
        mwf = {'Lu','Mi','Vi'}
        tth = {'Ma','Ju'}
        for prof, info in prof_dias.items():
            if any(d in mwf for d in info['days']) and any(d in tth for d in info['days']):
                if info['max_creditos'] < 4 and len(self.profesores[prof].pref_dias_set) < 4:
                    conflictos_list.append(f"Profesor {prof} mezcla horarios MWF y TTh sin justificación (cursos de {info['max_creditos']} créditos)")

        return conflictos_list

    def _construir_solucion_greedy(self):
        sol = [None]*len(self.secciones)
        asignado = [False]*len(self.secciones)
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
            salones_posibles = [sl['CODIGO'] for sl in self.salones if sl['CAPACIDAD'] >= seccion.cupo]
            salon = random.choice(salones_posibles) if salones_posibles else "TBA"
        return {'seccion':seccion, 'profesor':prof, 'salon':salon, 'patron':patron, 'ini':ini}

    def _asignar_seccion(self, idx, prof, sol, asignado):
        s = sol[idx]['seccion'] if sol[idx] else self.secciones[idx]
        patrones = PATRONES.get(s.creditos, PATRONES[3])
        puede_ser_intensivo = any(any(c>=3 for c in p['days'].values()) for p in patrones)
        if prof in self.profesores:
            prof_obj = self.profesores[prof]
            if prof_obj.cursos_intensivos == 0:
                patrones = [p for p in patrones if not any(c>=3 for c in p['days'].values())]
            elif prof_obj.cursos_intensivos == 1 and puede_ser_intensivo:
                intensivos = [p for p in patrones if any(c>=3 for c in p['days'].values())]
                if intensivos: patrones = intensivos
        if not patrones: patrones = PATRONES.get(s.creditos, PATRONES[3])

        random.shuffle(patrones)
        for patron in patrones:
            for dia, contrib in patron['days'].items():
                duracion = contrib*50
                inicios_posibles = [ini for ini in self.bloques if ini>=self.limite_operativo[0] and ini+duracion<=self.limite_operativo[1]]
                if dia in ["Ma","Ju"]:
                    inicios_posibles = [ini for ini in inicios_posibles if not (max(ini, self.hora_universal[0]) < min(ini+duracion, self.hora_universal[1]))]
                if s.creditos == 3 and contrib >= 3:
                    inicios_posibles = [ini for ini in inicios_posibles if ini >= 930]
                salones_posibles = [sl['CODIGO'] for sl in self.salones if sl['CAPACIDAD'] >= s.cupo and compatible_tipo(s.tipo_salon, sl['TIPO'])]
                for ini in inicios_posibles:
                    for salon in salones_posibles:
                        if prof in self.profesores:
                            bloqueado = False
                            for (dias_set, start, end) in self.profesores[prof].bloqueos:
                                if dia in dias_set and max(ini, start) < min(ini+duracion, end):
                                    bloqueado = True; break
                            if bloqueado: continue
                        conflicto = False
                        for j, asign in enumerate(sol):
                            if asign and asignado[j] and j != idx:
                                if asign['profesor'] == prof:
                                    for dia2, contrib2 in asign['patron']['days'].items():
                                        if dia == dia2 and max(ini, asign['ini']) < min(ini+duracion, asign['ini']+int(contrib2*50)):
                                            conflicto = True; break
                                if asign['salon'] == salon:
                                    for dia2, contrib2 in asign['patron']['days'].items():
                                        if dia == dia2 and max(ini, asign['ini']) < min(ini+duracion, asign['ini']+int(contrib2*50)):
                                            if salon in self.mega_salones and s.es_fusionable and asign['seccion'].es_fusionable:
                                                if s.cupo + asign['seccion'].cupo <= self.salon_capacidad.get(salon,0):
                                                    continue
                                            conflicto = True; break
                            if conflicto: break
                        if not conflicto:
                            sol[idx] = {'seccion':s, 'profesor':prof, 'salon':salon, 'patron':patron, 'ini':ini}
                            asignado[idx] = True
                            return True
        return False

    def _mutar_solucion(self, sol):
        nuevo = deepcopy(sol)
        idx = random.randint(0, len(nuevo)-1)
        s = nuevo[idx]['seccion']
        cand_profs = [p for p in s.cands if p in self.profesores]
        if not cand_profs:
            cand_profs = ["GRADUADOS"] if "GRADUADOS" in s.cands else ["TBA"]
        cand_profs.sort(key=lambda p: (
            0 if (p in self.profesores and s.es_grande and self.profesores[p].acepta_grandes==1) else 1,
            -(self.profesores[p].prioridad_curso(s.cod) if p in self.profesores else 0)
        ))
        mejores_opciones = []
        for _ in range(30):
            prof = random.choice(cand_profs)
            patrones = PATRONES.get(s.creditos, PATRONES[3])
            if prof in self.profesores:
                prof_obj = self.profesores[prof]
                patrones = [p for p in patrones if not (prof_obj.cursos_intensivos==0 and any(c>=3 for c in p['days'].values()))]
                if prof_obj.cursos_intensivos == 1:
                    intensivos = [p for p in PATRONES.get(s.creditos, PATRONES[3]) if any(c>=3 for c in p['days'].values())]
                    if intensivos: patrones = intensivos + [p for p in patrones if not any(c>=3 for c in p['days'].values())]
            if not patrones: patrones = PATRONES.get(s.creditos, PATRONES[3])
            patron = random.choice(patrones)
            horas_posibles = set(self.bloques)
            for dia, contrib in patron['days'].items():
                duracion = contrib*50
                horas_dia = [h for h in self.bloques if h>=self.limite_operativo[0] and h+duracion<=self.limite_operativo[1]]
                if dia in ["Ma","Ju"]:
                    horas_dia = [h for h in horas_dia if not (max(h, self.hora_universal[0]) < min(h+duracion, self.hora_universal[1]))]
                if s.creditos == 3 and contrib >= 3:
                    horas_dia = [h for h in horas_dia if h >= 930]
                horas_posibles = horas_posibles.intersection(set(horas_dia))
                if not horas_posibles: break
            if not horas_posibles: continue
            hora = random.choice(list(horas_posibles))
            salones_cand = [sl['CODIGO'] for sl in self.salones if compatible_tipo(s.tipo_salon, sl['TIPO']) and sl['CAPACIDAD'] >= s.cupo]
            if not salones_cand: continue
            salon = random.choice(salones_cand)
            conflicto = False
            for j, asign2 in enumerate(sol):
                if j != idx and asign2:
                    if asign2['profesor'] == prof:
                        for dia2, contrib2 in asign2['patron']['days'].items():
                            if dia2 in patron['days']:
                                fin_actual = hora + int(patron['days'][dia2]*50)
                                fin_exist = asign2['ini'] + int(contrib2*50)
                                if max(hora, asign2['ini']) < min(fin_actual, fin_exist):
                                    conflicto = True; break
                    if conflicto: break
                    if asign2['salon'] == salon:
                        for dia2, contrib2 in asign2['patron']['days'].items():
                            if dia2 in patron['days']:
                                fin_actual = hora + int(patron['days'][dia2]*50)
                                fin_exist = asign2['ini'] + int(contrib2*50)
                                if max(hora, asign2['ini']) < min(fin_actual, fin_exist):
                                    if salon in self.mega_salones and s.es_fusionable and asign2['seccion'].es_fusionable:
                                        if s.cupo + asign2['seccion'].cupo <= self.salon_capacidad.get(salon,0):
                                            continue
                                    conflicto = True; break
                    if conflicto: break
            if not conflicto:
                costo = 0
                if prof in self.profesores:
                    prof_obj = self.profesores[prof]
                    if prof_obj.pref_horas == 'AM' and hora >= 720: costo += 30
                    elif prof_obj.pref_horas == 'PM' and hora < 720: costo += 30
                    if prof_obj.pref_dias_set:
                        for dia in patron['days'].keys():
                            if dia not in prof_obj.pref_dias_set: costo += 15
                mejores_opciones.append((costo, prof, patron, hora, salon))
        if not mejores_opciones:
            return nuevo, self._costo_total(nuevo)
        mejores_opciones.sort(key=lambda x: x[0])
        mejor = mejores_opciones[0]
        nuevo[idx] = {'seccion':s, 'profesor':mejor[1], 'salon':mejor[4], 'patron':mejor[2], 'ini':mejor[3]}
        return nuevo, self._costo_total(nuevo)

    def optimizar(self, iteraciones=3000, bar=None, status_text=None):
        temp_inicial = 5000.0
        self.historial_costos = [self.mejor_costo]
        for it in range(iteraciones):
            vecino, costo_vecino = self._mutar_solucion(self.solucion)
            if costo_vecino <= self.mejor_costo:
                self.solucion = vecino
                self.mejor_costo = costo_vecino
                self.mejor_solucion = deepcopy(self.solucion)
            else:
                temp = temp_inicial / (it+1)
                try:
                    prob = math.exp((self.mejor_costo - costo_vecino)/temp)
                except:
                    prob = 0
                if random.random() < prob:
                    self.solucion = vecino
            self.historial_costos.append(self.mejor_costo)
            if it % 10 == 0 or it == iteraciones-1:
                if status_text:
                    fitness_actual = 10000/(10000+self.mejor_costo)
                    duros = int(self.mejor_costo // 10000)
                    # Calcular % de restricciones suaves cumplidas
                    total_soft, viol_soft = self._calcular_soft_metric(self.mejor_solucion)
                    soft_pct = 100.0 * (1 - viol_soft/max(total_soft,1))
                    status_text.markdown(f"**🔄 Generación {it+1}/{iteraciones}** | Conflictos Duros: {duros} | Costo Total: {self.mejor_costo:.2f} | Fitness: {fitness_actual:.5f} | Soft: {soft_pct:.1f}%")
                if bar:
                    bar.progress((it+1)/iteraciones)
        return self.mejor_solucion, int(self.mejor_costo//10000), self.historial_costos

    def _calcular_soft_metric(self, sol):
        total = 0
        violaciones = 0
        for asign in sol:
            prof = asign['profesor']
            if prof in ["GRADUADOS","TBA"] or prof not in self.profesores:
                continue
            prof_obj = self.profesores[prof]
            total += 1
            if prof_obj.pref_horas == 'AM' and asign['ini'] >= 720:
                violaciones += 1
            elif prof_obj.pref_horas == 'PM' and asign['ini'] < 720:
                violaciones += 1
            for dia in asign['patron']['days'].keys():
                total += 1
                if prof_obj.pref_dias_set and dia not in prof_obj.pref_dias_set:
                    violaciones += 1
        # Penalización por múltiples salones (suave)
        prof_rooms = {}
        for asign in sol:
            prof = asign['profesor']
            if prof in ["GRADUADOS","TBA"] or prof not in self.profesores:
                continue
            salon = asign['salon']
            prof_rooms.setdefault(prof, set()).add(salon)
        for prof, rooms in prof_rooms.items():
            if len(rooms) > 1:
                total += 1
                violaciones += 1
        return total, violaciones

# ==============================================================================
# 5. HEATMAP (ejes intercambiados, fondo blanco)
# ==============================================================================
def generar_heatmap_ocupacion(scheduler, solucion):
    dias = ['Lu','Ma','Mi','Ju','Vi']
    inicio = scheduler.limite_operativo[0]
    fin = scheduler.limite_operativo[1]
    horas = list(range(inicio, fin+1, 30))
    matriz = np.zeros((len(horas), len(dias)))
    total_salones = len(scheduler.salones)
    for asign in solucion:
        salon = asign['salon']
        if salon == "TBA": continue
        patron = asign['patron']
        ini = asign['ini']
        for dia, contrib in patron['days'].items():
            if dia not in dias: continue
            dia_idx = dias.index(dia)
            duracion = int(contrib*50)
            for t in range(ini, ini+duracion, 30):
                if t in horas:
                    hora_idx = horas.index(t)
                    matriz[hora_idx, dia_idx] += 1
    if total_salones > 0:
        matriz = (matriz / total_salones) * 100
    fig, ax = plt.subplots(figsize=(12,6))
    im = ax.imshow(matriz, cmap='YlOrRd', aspect='auto', vmin=0, vmax=100)
    ax.set_yticks(range(len(horas)))
    etiquetas = [mins_to_str(h).replace(' AM','').replace(' PM','') for h in horas]
    step = max(1, len(etiquetas)//12)
    ax.set_yticks(range(0, len(horas), step))
    ax.set_yticklabels(etiquetas[::step], color='black')
    ax.set_xticks(range(len(dias)))
    ax.set_xticklabels(dias, color='black')
    cbar = plt.colorbar(im, ax=ax, label='% Ocupación')
    cbar.ax.yaxis.label.set_color('black')
    cbar.ax.tick_params(colors='black')
    ax.set_title('Ocupación de Salones por Franja Horaria', color='black')
    ax.set_xlabel('Día', color='black')
    ax.set_ylabel('Hora de Inicio', color='black')
    fig.patch.set_facecolor('white')
    ax.set_facecolor('#f5f5f5')
    ax.tick_params(colors='black')
    for spine in ax.spines.values():
        spine.set_edgecolor('#D4AF37')
    plt.tight_layout()
    return fig

# ==============================================================================
# 6. PLANTILLA Y UI
# ==============================================================================
def generar_plantilla():
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_cursos = pd.DataFrame({'CODIGO':['MATE3171','MATE3172'],'CREDITOS':[3,3],'DEMANDA':[120,150],'CUPO':[30,30],'CANDIDATOS':['PEREZ, GONZALEZ','RODRIGUEZ'],'TIPO_SALON':[1,1]})
        df_cursos.to_excel(writer, sheet_name='Cursos', index=False)
        df_profes = pd.DataFrame({'NOMBRE':['PEREZ','GONZALEZ'],'CARGA_MIN':[9,6],'CARGA_MAX':[15,12],'PREF_DIAS':['LMV','MJ'],'PREF_HORAS':['AM','PM'],'BLOQUEO_DIAS':['',''],'BLOQUEO_HORA_INI':['',''],'BLOQUEO_HORA_FIN':['',''],'PREF1':['MATE3171','MATE3172'],'PREF2':['',''],'PREF3':['',''],'COMPENSACION':['NO','SI'],'ACEPTA_GRANDES':[0,1],'CURSOS_INTENSIVOS':[0,1]})
        df_profes.to_excel(writer, sheet_name='Profesores', index=False)
        df_salones = pd.DataFrame({'CODIGO':['S-101','S-102'],'CAPACIDAD':[30,40],'TIPO':[1,2]})
        df_salones.to_excel(writer, sheet_name='Salones', index=False)
    output.seek(0)
    return output.getvalue()

def main():
    with st.sidebar:
        st.markdown("### Configuración")
        zona = st.selectbox("Zona Campus", ["CENTRAL","PERIFERICA"])
        iteraciones = st.slider("Iteraciones", 100, 5000, 3000)
        file = st.file_uploader("Subir Excel", type=['xlsx'])
        st.download_button("📥 Plantilla", data=generar_plantilla(), file_name="PLANTILLA.xlsx")
    st.markdown(f"### Zona: {zona}")
    c1,c2,c3 = st.columns(3)
    with c1: st.metric("Ventana", "07:30-18:30" if zona=="CENTRAL" else "07:00-18:00")
    with c2: st.metric("Hora Universal", "10:30-12:30" if zona=="CENTRAL" else "10:00-12:00")
    with c3: st.markdown('<div class="status-badge">RESTRICCIÓN: COMPACIDAD HORARIA (MWF / TTH)</div>', unsafe_allow_html=True)

    if not file:
        st.markdown('<div class="glass-card"><h3>📥 Cargar archivo</h3><p>Hojas: Cursos, Profesores, Salones</p></div>', unsafe_allow_html=True)
    else:
        if st.button("🚀 OPTIMIZAR"):
            try:
                with st.spinner("Optimizando..."):
                    xls = pd.ExcelFile(file)
                    df_cursos = pd.read_excel(xls, 'Cursos')
                    df_profes = pd.read_excel(xls, 'Profesores')
                    df_salones = pd.read_excel(xls, 'Salones')
                    scheduler = TabuScheduler(df_cursos, df_profes, df_salones, zona)
                    start = time.time()
                    bar = st.progress(0)
                    status = st.empty()
                    mejor_sol, conflictos, historial = scheduler.optimizar(iteraciones, bar, status)
                    elapsed = time.time() - start
                    st.session_state.elapsed = elapsed
                    st.session_state.conflicts = conflictos
                    st.session_state.historial = historial
                    st.session_state.scheduler = scheduler
                    st.session_state.mejor_sol = mejor_sol
                    cargas = {}
                    for a in mejor_sol:
                        p = a['profesor']
                        if p not in ["GRADUADOS","TBA"]:
                            cargas[p] = cargas.get(p,0) + scheduler.get_sec_creditos(a['seccion'], p)
                    for p in scheduler.profesores:
                        if p not in cargas: cargas[p]=0.0
                    st.session_state.cargas = cargas
                    st.session_state.master = pd.DataFrame([{
                        'ID':a['seccion'].cod, 'Asignatura':a['seccion'].cod.split('-')[0],
                        'Cupo':a['seccion'].cupo, 'Créditos':scheduler.get_sec_creditos(a['seccion'], a['profesor']),
                        'Profesor':a['profesor'], 'Patrón':a['patron']['name'],
                        'Horario':format_horario(a['patron'], a['ini']), 'Salón':a['salon']
                    } for a in mejor_sol])
                    st.session_state.detailed = scheduler._obtener_conflictos(mejor_sol)
            except Exception as e:
                st.error(f"Error: {e}")
                return

    if 'master' in st.session_state:
        st.success(f"✅ Optimizado en {st.session_state.elapsed:.2f}s")
        t1,t2,t3,t4 = st.tabs(["📋 Principal","🔍 Detalle","🚨 Auditoría","📊 Analíticas"])
        with t1:
            edited = st.data_editor(st.session_state.master, use_container_width=True, height=400)
            st.download_button("💾 Exportar Excel", exportar_todo(edited), "Horario_UPRM.xlsx")
        with t2:
            f1,f2,f3 = st.tabs(["Profesor","Curso","Salón"])
            df = st.session_state.master
            with f1:
                profs = sorted([p for p in df['Profesor'].unique() if p not in ["GRADUADOS","TBA"]])
                if profs:
                    p = st.selectbox("Profesor", profs)
                    st.table(df[df['Profesor']==p][['ID','Cupo','Créditos','Patrón','Horario','Salón']])
            with f2:
                cursos = sorted(df['Asignatura'].unique())
                if cursos:
                    c = st.selectbox("Curso", cursos)
                    st.table(df[df['Asignatura']==c][['ID','Cupo','Profesor','Patrón','Horario','Salón']])
            with f3:
                salones = sorted(df['Salón'].unique())
                if salones:
                    s = st.selectbox("Salón", salones)
                    st.table(df[df['Salón']==s][['ID','Asignatura','Profesor','Patrón','Horario']])
        with t3:
            if st.session_state.conflicts == 0:
                st.success("✅ CERO CONFLICTOS - Horario perfecto")
            else:
                st.error(f"⚠️ {st.session_state.conflicts} conflictos detectados")
                for c in st.session_state.detailed:
                    st.write(f"- {c}")
        with t4:
            # Evolución
            fitness = [10000/(10000+c) for c in st.session_state.historial]
            fig, ax = plt.subplots(figsize=(10,4))
            ax.plot(fitness, color='#D4AF37', lw=2)
            ax.set_title("Evolución del Fitness", color='black')
            ax.set_xlabel("Iteración", color='black')
            ax.set_ylabel("Fitness (1 = ideal)", color='black')
            fig.patch.set_facecolor('white')
            ax.set_facecolor('#f5f5f5')
            ax.tick_params(colors='black')
            for spine in ax.spines.values(): spine.set_edgecolor('#D4AF37')
            st.pyplot(fig)
            # Carga
            cargas_df = pd.DataFrame(list(st.session_state.cargas.items()), columns=['Profesor','Créditos']).sort_values('Créditos', ascending=False)
            fig2, ax2 = plt.subplots(figsize=(12,5))
            ax2.bar(cargas_df['Profesor'], cargas_df['Créditos'], color='#8E6E13')
            ax2.axhline(y=12, color='red', linestyle='--', label='Carga típica 12')
            ax2.set_xticklabels(cargas_df['Profesor'], rotation=45, ha='right', color='black')
            ax2.tick_params(colors='black')
            fig2.patch.set_facecolor('white')
            ax2.set_facecolor('#f5f5f5')
            ax2.legend()
            st.pyplot(fig2)
            # Heatmap
            st.markdown("### Ocupación de Salones")
            fig3 = generar_heatmap_ocupacion(st.session_state.scheduler, st.session_state.mejor_sol)
            st.pyplot(fig3)

if __name__ == "__main__":
    main()
