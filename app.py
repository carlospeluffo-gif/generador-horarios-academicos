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
# 1. ESTÉTICA (FONDO BLANCO)
# ==============================================================================
st.set_page_config(page_title="UPRM Scheduler - Zero Conflicts", page_icon="🏛️", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; color: #1E1E1E; }
    .math-header {
        display: flex; justify-content: space-between; align-items: center;
        padding: 20px 40px; background: #F5F5F5; border-bottom: 3px solid #8E6E13;
        margin-bottom: 30px; border-radius: 0 0 20px 20px;
    }
    h1 { font-family: 'Playfair Display', serif; color: #8E6E13; }
    .glass-card { background: #FAFAFA; border-radius: 15px; padding: 20px; border: 1px solid #DDD; }
    .stButton>button { background: #8E6E13; color: white; border-radius: 8px; }
    .status-badge { background: #F0F0F0; border: 1px solid #8E6E13; color: #8E6E13; padding: 8px; text-align: center; border-radius: 8px; }
    [data-testid="stSidebar"] { background-color: #F8F8F8; }
</style>
<div class="math-header">
    <div>📅</div><div><h1>UPRM TIMETABLE SYSTEM v16</h1><p>Asignación inteligente con garantía de cero conflictos</p></div><div>⏰</div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. UTILIDADES Y TABLA DE COMPENSACIÓN (COMPLETA)
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
        {"name": "Lu-Mi-Vi", "days": {"Lu": 1, "Mi": 1, "Vi": 1}, "tipo": "LWV"},
        {"name": "Ma-Ju", "days": {"Ma": 1.5, "Ju": 1.5}, "tipo": "MJ"},
        {"name": "Lu (Intensivo)", "days": {"Lu": 3}, "tipo": "INTENSIVO"},
        {"name": "Ma (Intensivo)", "days": {"Ma": 3}, "tipo": "INTENSIVO"},
        {"name": "Mi (Intensivo)", "days": {"Mi": 3}, "tipo": "INTENSIVO"},
        {"name": "Ju (Intensivo)", "days": {"Ju": 3}, "tipo": "INTENSIVO"},
        {"name": "Vi (Intensivo)", "days": {"Vi": 3}, "tipo": "INTENSIVO"},
    ],
    4: [
        {"name": "Lu-Ma-Mi-Ju", "days": {"Lu": 1, "Ma": 1, "Mi": 1, "Ju": 1}, "tipo": "LWV"},
        {"name": "Lu-Ma-Mi-Vi", "days": {"Lu": 1, "Ma": 1, "Mi": 1, "Vi": 1}, "tipo": "LWV"},
        {"name": "Lu-Ma-Ju-Vi", "days": {"Lu": 1, "Ma": 1, "Ju": 1, "Vi": 1}, "tipo": "LWV"},
        {"name": "Lu-Mi-Ju-Vi", "days": {"Lu": 1, "Mi": 1, "Ju": 1, "Vi": 1}, "tipo": "LWV"},
        {"name": "Ma-Mi-Ju-Vi", "days": {"Ma": 1, "Mi": 1, "Ju": 1, "Vi": 1}, "tipo": "LWV"},
        {"name": "Lu-Mi", "days": {"Lu": 2, "Mi": 2}, "tipo": "LWV"},
        {"name": "Lu-Vi", "days": {"Lu": 2, "Vi": 2}, "tipo": "LWV"},
        {"name": "Ma-Ju", "days": {"Ma": 2, "Ju": 2}, "tipo": "MJ"},
        {"name": "Mi-Vi", "days": {"Mi": 2, "Vi": 2}, "tipo": "LWV"},
    ],
    5: [
        {"name": "Lu-Ma-Mi-Ju-Vi", "days": {"Lu": 1, "Ma": 1, "Mi": 1, "Ju": 1, "Vi": 1}, "tipo": "LWV"},
        {"name": "Lu-Ma-Mi-Vi", "days": {"Lu": 1, "Ma": 1, "Mi": 1, "Vi": 2}, "tipo": "LWV"},
        {"name": "Lu-Ma-Ju-Vi", "days": {"Lu": 1, "Ma": 1, "Ju": 1, "Vi": 2}, "tipo": "LWV"},
        {"name": "Lu-Mi-Ju-Vi", "days": {"Lu": 1, "Mi": 1, "Ju": 1, "Vi": 2}, "tipo": "LWV"},
        {"name": "Ma-Mi-Ju-Vi", "days": {"Ma": 1, "Mi": 1, "Ju": 1, "Vi": 2}, "tipo": "LWV"},
        {"name": "Lu-Mi-Vi", "days": {"Lu": 2, "Mi": 2, "Vi": 1}, "tipo": "LWV"},
        {"name": "Ma-Ju-Vi", "days": {"Ma": 1.5, "Ju": 1.5, "Vi": 2}, "tipo": "MJ"},
        {"name": "Lu-Ma-Mi", "days": {"Lu": 2, "Ma": 1, "Mi": 2}, "tipo": "LWV"},
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
            if str(p) not in ["TBA", "GRADUADOS"]:
                clean = "".join(c for c in str(p) if c.isalnum() or c==' ')[:25]
                df[df['Persona'] == p].to_excel(writer, sheet_name=f"User_{clean}", index=False)
    return out.getvalue()

# ==============================================================================
# 3. CLASES DE DATOS
# ==============================================================================
class Seccion:
    def __init__(self, cod, creditos, cupo, candidatos_raw, tipo_salon):
        self.cod = str(cod)
        self.creditos = int(creditos)
        self.cupo = int(cupo)
        if isinstance(candidatos_raw, list):
            raw = [c.strip().upper() for c in candidatos_raw if c.strip()]
        else:
            raw = [c.strip().upper() for c in str(candidatos_raw).split(',') if c.strip() and c.upper() != 'NAN']
        self.cands = list(set(raw))
        try:
            t = float(tipo_salon)
            self.tipo_salon = 3 if abs(t - 1.3) < 0.01 else int(round(t))
        except:
            self.tipo_salon = 1
        base = self.cod.split('-')[0].upper().replace(" ", "")
        self.es_fusionable = base in ["MATE3171", "MATE3172", "MATE3173"]
        self.es_grande = self.cupo >= 85

class Profesor:
    def __init__(self, nombre, carga_min, carga_max, pref_dias, pref_horas,
                 bloqueo_dias, bloqueo_ini, bloqueo_fin, preferencias_cursos,
                 compensacion, acepta_grandes, cursos_intensivos):
        self.nombre = nombre.upper().strip()
        self.carga_min = float(carga_min) if pd.notnull(carga_min) else 0.0
        self.carga_max = float(carga_max) if pd.notnull(carga_max) else 12.0
        if self.carga_min > self.carga_max:
            self.carga_min, self.carga_max = self.carga_max, self.carga_min
        # Preferencias días
        self.pref_dias_set = set()
        if pref_dias:
            for tok in pref_dias.replace(',', ' ').upper().split():
                if tok in ('L', 'LU'): self.pref_dias_set.add('Lu')
                elif tok in ('M', 'MA'): self.pref_dias_set.add('Ma')
                elif tok in ('W', 'MI'): self.pref_dias_set.add('Mi')
                elif tok in ('J', 'JU'): self.pref_dias_set.add('Ju')
                elif tok in ('V', 'VI'): self.pref_dias_set.add('Vi')
                elif tok in ('LU', 'MA', 'MI', 'JU', 'VI'): self.pref_dias_set.add(tok)
        self.pref_horas = pref_horas if pref_horas else 'ANY'
        self.preferencias = [c.upper().strip() for c in preferencias_cursos if c and str(c).upper() != 'NAN'] if preferencias_cursos else []
        self.compensacion = str(compensacion).upper() in ('SI', 'SÍ', 'YES', '1')
        self.acepta_grandes = int(acepta_grandes) if pd.notnull(acepta_grandes) else 0
        self.cursos_intensivos = int(cursos_intensivos) if pd.notnull(cursos_intensivos) else 0
        self.bloqueos = []
        if bloqueo_dias:
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
            if dias_set and bloqueo_ini and bloqueo_fin:
                try:
                    start = str_to_mins(bloqueo_ini)
                    end = str_to_mins(bloqueo_fin)
                    self.bloqueos.append((dias_set, start, end))
                except:
                    pass
        self.patron_tipo = None  # 'LWV', 'MJ' o 'INTENSIVO'

    def prioridad_curso(self, curso_cod):
        for idx, pref in enumerate(self.preferencias):
            if pref in curso_cod:
                return 1.0 / (idx + 1)
        return 0.0

def compatible_tipo(curso_tipo, salon_tipo):
    if isinstance(salon_tipo, float):
        salon_cat = 2 if 1.9 <= salon_tipo <= 2.1 else (3 if salon_tipo >= 2.9 else 1)
    else:
        salon_cat = int(salon_tipo)
    if curso_tipo == 2:
        return salon_cat == 2
    if curso_tipo == 3:
        return salon_cat == 3
    return salon_cat != 2

# ==============================================================================
# 4. MOTOR PRINCIPAL: ASIGNACIÓN DE CARGA + HORARIOS (CERO CONFLICTOS)
# ==============================================================================
class ZeroConflictScheduler:
    def __init__(self, df_cursos, df_profes, df_salones, zona):
        self.zona = zona
        # Procesar salones
        self.salones = []
        for _, r in df_salones.iterrows():
            cod = str(r['CODIGO']).strip().upper()
            cap = int(r['CAPACIDAD']) if pd.notnull(r['CAPACIDAD']) else 25
            tipo = float(r['TIPO']) if pd.notnull(r['TIPO']) else 1.0
            self.salones.append({'CODIGO': cod, 'CAPACIDAD': cap, 'TIPO': tipo})
        self.salon_capacidad = {s['CODIGO']: s['CAPACIDAD'] for s in self.salones}
        self.salon_tipo = {s['CODIGO']: s['TIPO'] for s in self.salones}
        self.mega_salones = {s['CODIGO'] for s in self.salones if any(x in s['CODIGO'] for x in ['FA', 'FB', 'FC'])}
        # Procesar profesores
        self.profesores = {}
        for _, r in df_profes.iterrows():
            prefs = [str(r.get(col, '')).strip().upper() for col in ['PREF1', 'PREF2', 'PREF3'] if pd.notnull(r.get(col)) and str(r.get(col)).upper() != 'NAN']
            prof = Profesor(
                nombre=r['NOMBRE'], carga_min=r.get('CARGA_MIN', 0), carga_max=r.get('CARGA_MAX', 12),
                pref_dias=r.get('PREF_DIAS', ''), pref_horas=r.get('PREF_HORAS', 'ANY'),
                bloqueo_dias=r.get('BLOQUEO_DIAS', ''), bloqueo_ini=r.get('BLOQUEO_HORA_INI', ''),
                bloqueo_fin=r.get('BLOQUEO_HORA_FIN', ''), preferencias_cursos=prefs,
                compensacion=r.get('COMPENSACION', 'NO'), acepta_grandes=r.get('ACEPTA_GRANDES', 0),
                cursos_intensivos=r.get('CURSOS_INTENSIVOS', 0)
            )
            self.profesores[prof.nombre] = prof
        # Crear secciones con lógica de demanda vs cupo
        self.secciones = []
        cursos_agrup = {}
        for _, r in df_cursos.iterrows():
            cod = str(r['CODIGO']).strip().upper()
            if cod not in cursos_agrup:
                tipo = r.get('TIPO_SALON', 1)
                try:
                    tval = float(tipo)
                    tipo_salon = 3 if abs(tval - 1.3) < 0.01 else int(round(tval))
                except:
                    tipo_salon = 1
                cursos_agrup[cod] = {
                    'creditos': int(r['CREDITOS']),
                    'demanda': int(r.get('DEMANDA', 0)),
                    'cupo': int(r.get('CUPO', 30)),
                    'candidatos': r.get('CANDIDATOS', ''),
                    'tipo_salon': tipo_salon
                }
            else:
                cursos_agrup[cod]['demanda'] += int(r.get('DEMANDA', 0))
        for cod, dat in cursos_agrup.items():
            cupo_ef = dat['cupo']
            demanda = dat['demanda']
            completas = demanda // cupo_ef
            resto = demanda % cupo_ef
            if resto >= cupo_ef / 2:
                num_sec = completas + 1
                cupos = [cupo_ef] * completas + [resto]
            else:
                num_sec = completas
                cupos = [cupo_ef] * completas
            for i, cup in enumerate(cupos):
                self.secciones.append(Seccion(f"{cod}-{i+1:02d}", dat['creditos'], cup, dat['candidatos'], dat['tipo_salon']))
        # Límites horarios según zona
        if zona == "CENTRAL":
            self.hora_universal = (630, 750)
            self.limite_operativo = (450, 1110)
            self.bloques = list(range(450, 1051, 60))
        else:
            self.hora_universal = (600, 720)
            self.limite_operativo = (420, 1080)
            self.bloques = list(range(420, 1021, 60))
        # Asignación de profesores (cargas)
        self._asignar_cargas()
        # Asignación de horarios y salones
        self._asignar_horarios_salones()
        # Contar conflictos finales
        self.conflictos = self._contar_conflictos()
        # Calcular porcentaje de restricciones suaves cumplidas
        self.soft_total, self.soft_cumplidas = self._calcular_soft()

    def get_creditos_reales(self, seccion, prof_nombre):
        if prof_nombre in self.profesores and self.profesores[prof_nombre].compensacion:
            return get_creditos_reales(seccion.creditos, seccion.cupo)
        return float(seccion.creditos)

    def _asignar_cargas(self):
        """Asigna cada sección a un profesor respetando carga_min/max y candidatos, usando TBA si necesario."""
        secciones = self.secciones[:]
        profesores = list(self.profesores.values())
        # Ordenar secciones por prioridad (menos candidatos primero)
        secciones.sort(key=lambda s: len(s.cands))
        carga_actual = {p.nombre: 0.0 for p in profesores}
        asignacion = [None] * len(secciones)
        # Primero, secciones con un solo candidato
        for i, s in enumerate(secciones):
            candidatos_reales = [c for c in s.cands if c in self.profesores]
            if len(candidatos_reales) == 1:
                prof = candidatos_reales[0]
                cred = self.get_creditos_reales(s, prof)
                if carga_actual[prof] + cred <= self.profesores[prof].carga_max + 0.1:
                    carga_actual[prof] += cred
                    asignacion[i] = prof
        # Resto con greedy
        for i, s in enumerate(secciones):
            if asignacion[i] is not None:
                continue
            candidatos = [c for c in s.cands if c in self.profesores]
            # Función de puntuación
            def score(p):
                prof = self.profesores[p]
                capacidad_restante = prof.carga_max - carga_actual[p]
                if capacidad_restante < self.get_creditos_reales(s, p) - 0.1:
                    return -1e9
                prioridad = prof.prioridad_curso(s.cod)
                # Balancear: preferir profesor con menor carga actual
                return prioridad + (1.0 / (1 + carga_actual[p]))
            candidatos.sort(key=lambda p: score(p), reverse=True)
            asignado = False
            for p in candidatos:
                cred = self.get_creditos_reales(s, p)
                if carga_actual[p] + cred <= self.profesores[p].carga_max + 0.1:
                    carga_actual[p] += cred
                    asignacion[i] = p
                    asignado = True
                    break
            if not asignado:
                asignacion[i] = "TBA"
        # Rebalanceo: intentar cumplir cargas mínimas
        for _ in range(100):
            bajo = [p for p in profesores if carga_actual[p.nombre] < p.carga_min - 0.1]
            if not bajo:
                break
            # Buscar secciones asignadas a TBA o a profesores con exceso
            fuentes = []
            for i, prof in enumerate(asignacion):
                if prof == "TBA":
                    fuentes.append((i, None, self.get_creditos_reales(secciones[i], "TBA")))
                elif prof in self.profesores and carga_actual[prof] > self.profesores[prof].carga_max + 0.1:
                    fuentes.append((i, prof, self.get_creditos_reales(secciones[i], prof)))
            for p in bajo:
                for idx, orig_prof, cred in fuentes:
                    s = secciones[idx]
                    if p.nombre in s.cands:
                        if carga_actual[p.nombre] + cred <= p.carga_max + 0.1:
                            if orig_prof is not None:
                                carga_actual[orig_prof] -= cred
                            carga_actual[p.nombre] += cred
                            asignacion[idx] = p.nombre
                            break
                else:
                    # Si no se puede, permitir déficit (se reportará como conflicto, pero intentamos evitarlo)
                    p.carga_min = 0
        self.asignacion_profesor = asignacion
        self.carga_final = carga_actual

    def _asignar_horarios_salones(self):
        """Asigna patrón, hora y salón a cada sección sin conflictos."""
        # Agrupar por profesor
        secciones_por_prof = {}
        for i, prof in enumerate(self.asignacion_profesor):
            if prof not in secciones_por_prof:
                secciones_por_prof[prof] = []
            secciones_por_prof[prof].append((i, self.secciones[i]))
        self.horarios = [None] * len(self.secciones)
        # Asignar por profesor (cada uno resuelve sus conflictos internos)
        for prof, lista in secciones_por_prof.items():
            if prof == "TBA":
                for idx, s in lista:
                    self.horarios[idx] = self._asignar_tba(s)
                continue
            prof_obj = self.profesores[prof]
            # Usar recocido simulado para este profesor
            asignaciones = self._asignar_horarios_profesor(prof_obj, lista)
            for (idx, _), asign in zip(lista, asignaciones):
                self.horarios[idx] = asign
        # Resolver conflictos de salón entre diferentes profesores
        self._resolver_conflictos_salon()

    def _asignar_tba(self, seccion):
        """Asignación simple para TBA (sin restricciones)."""
        patron = random.choice(PATRONES.get(seccion.creditos, PATRONES[3]))
        for _ in range(100):
            ini = random.choice(self.bloques)
            valido = True
            for dia, contrib in patron['days'].items():
                duracion = contrib * 50
                if ini + duracion > self.limite_operativo[1] or ini < self.limite_operativo[0]:
                    valido = False
                    break
                if seccion.creditos == 3 and contrib >= 3 and ini < 930:
                    valido = False
                    break
                if dia in ["Ma", "Ju"] and max(ini, self.hora_universal[0]) < min(ini + duracion, self.hora_universal[1]):
                    valido = False
                    break
            if valido:
                salones = [s for s in self.salones if s['CAPACIDAD'] >= seccion.cupo and compatible_tipo(seccion.tipo_salon, s['TIPO'])]
                if salones:
                    salon = random.choice(salones)['CODIGO']
                    return {'seccion': seccion, 'profesor': 'TBA', 'salon': salon, 'patron': patron, 'ini': ini}
        # Fallback
        return {'seccion': seccion, 'profesor': 'TBA', 'salon': 'TBA', 'patron': patron, 'ini': self.bloques[0]}

    def _asignar_horarios_profesor(self, prof, lista):
        """Recocido simulado para asignar horarios a las secciones de un mismo profesor."""
        n = len(lista)
        # Estado inicial aleatorio factible (sin conflictos entre sí)
        def estado_aleatorio():
            estado = []
            for idx, s in lista:
                patrones = [p for p in PATRONES.get(s.creditos, PATRONES[3])]
                if prof.cursos_intensivos == 0:
                    patrones = [p for p in patrones if not any(c >= 3 for c in p['days'].values())]
                elif prof.cursos_intensivos == 1:
                    intensivos = [p for p in patrones if any(c >= 3 for c in p['days'].values())]
                    if intensivos:
                        patrones = intensivos
                if prof.patron_tipo:
                    patrones = [p for p in patrones if p.get('tipo') == prof.patron_tipo]
                if not patrones:
                    patrones = PATRONES.get(s.creditos, PATRONES[3])
                patron = random.choice(patrones)
                ini = random.choice(self.bloques)
                salones = [sl['CODIGO'] for sl in self.salones if sl['CAPACIDAD'] >= s.cupo and compatible_tipo(s.tipo_salon, sl['TIPO'])]
                salon = random.choice(salones) if salones else "TBA"
                estado.append({'patron': patron, 'ini': ini, 'salon': salon, 'seccion': s, 'idx': idx})
            return estado

        def costo(estado):
            c = 0
            # Conflictos de tiempo entre secciones del mismo profesor
            ocup = {}
            for a in estado:
                for dia, contrib in a['patron']['days'].items():
                    ini = a['ini']
                    fin = ini + int(contrib * 50)
                    if dia not in ocup:
                        ocup[dia] = []
                    for (i2, f2) in ocup[dia]:
                        if max(ini, i2) < min(fin, f2):
                            c += 1_000_000
                    ocup[dia].append((ini, fin))
            # Bloqueos del profesor
            for a in estado:
                for dia, contrib in a['patron']['days'].items():
                    ini = a['ini']
                    fin = ini + int(contrib * 50)
                    for (dias_set, start, end) in prof.bloqueos:
                        if dia in dias_set and max(ini, start) < min(fin, end):
                            c += 1_000_000
            # Preferencias suaves
            for a in estado:
                if prof.pref_horas == 'AM' and a['ini'] >= 720:
                    c += 30
                elif prof.pref_horas == 'PM' and a['ini'] < 720:
                    c += 30
                if prof.pref_dias_set:
                    for dia in a['patron']['days']:
                        if dia not in prof.pref_dias_set:
                            c += 15
            # Consistencia de patrón (si ya tiene tipo)
            if prof.patron_tipo:
                for a in estado:
                    if a['patron'].get('tipo') != prof.patron_tipo:
                        c += 1_000_000
            return c

        # Recocido
        estado = estado_aleatorio()
        mejor = deepcopy(estado)
        mejor_costo = costo(estado)
        temp = 1000.0
        for it in range(5000):
            nuevo = deepcopy(estado)
            idx_mut = random.randint(0, n-1)
            s = lista[idx_mut][1]
            # Mutar: cambiar patrón, hora o salón
            if random.random() < 0.33:
                patrones = [p for p in PATRONES.get(s.creditos, PATRONES[3])]
                if prof.cursos_intensivos == 0:
                    patrones = [p for p in patrones if not any(c >= 3 for c in p['days'].values())]
                elif prof.cursos_intensivos == 1:
                    intensivos = [p for p in patrones if any(c >= 3 for c in p['days'].values())]
                    if intensivos:
                        patrones = intensivos
                if prof.patron_tipo:
                    patrones = [p for p in patrones if p.get('tipo') == prof.patron_tipo]
                if patrones:
                    nuevo[idx_mut]['patron'] = random.choice(patrones)
            if random.random() < 0.33:
                nuevo[idx_mut]['ini'] = random.choice(self.bloques)
            if random.random() < 0.33:
                salones = [sl['CODIGO'] for sl in self.salones if sl['CAPACIDAD'] >= s.cupo and compatible_tipo(s.tipo_salon, sl['TIPO'])]
                if salones:
                    nuevo[idx_mut]['salon'] = random.choice(salones)
            # Ajustar límites
            p_ = nuevo[idx_mut]['patron']
            ini = nuevo[idx_mut]['ini']
            for dia, contrib in p_['days'].items():
                duracion = contrib * 50
                if ini + duracion > self.limite_operativo[1] or ini < self.limite_operativo[0]:
                    nuevo[idx_mut]['ini'] = max(self.limite_operativo[0], min(self.limite_operativo[1] - duracion, ini))
                if s.creditos == 3 and contrib >= 3 and ini < 930:
                    nuevo[idx_mut]['ini'] = 930
                if dia in ["Ma", "Ju"] and max(ini, self.hora_universal[0]) < min(ini + duracion, self.hora_universal[1]):
                    nuevo[idx_mut]['ini'] = self.hora_universal[1]
            new_cost = costo(nuevo)
            if new_cost < mejor_costo:
                mejor = deepcopy(nuevo)
                mejor_costo = new_cost
                estado = nuevo
            else:
                delta = new_cost - mejor_costo
                if random.random() < math.exp(-delta / temp):
                    estado = nuevo
            temp *= 0.995
        return mejor

    def _resolver_conflictos_salon(self):
        """Resuelve conflictos de salón entre diferentes profesores."""
        asignaciones = [(i, a) for i, a in enumerate(self.horarios) if a is not None]
        for _ in range(100):
            ocup_salon = {}
            conflictos = []
            for idx, a in asignaciones:
                salon = a['salon']
                if salon == "TBA":
                    continue
                for dia, contrib in a['patron']['days'].items():
                    ini = a['ini']
                    fin = ini + int(contrib * 50)
                    key = (salon, dia)
                    if key not in ocup_salon:
                        ocup_salon[key] = []
                    for (i2, f2, idx2) in ocup_salon[key]:
                        if max(ini, i2) < min(fin, f2):
                            s1 = a['seccion']
                            s2 = self.horarios[idx2]['seccion']
                            if salon in self.mega_salones and s1.es_fusionable and s2.es_fusionable:
                                if s1.cupo + s2.cupo <= self.salon_capacidad[salon]:
                                    continue
                            conflictos.append((idx, idx2, salon, dia))
                    ocup_salon[key].append((ini, fin, idx))
            if not conflictos:
                break
            idx1, idx2, salon, _ = conflictos[0]
            sec1 = self.horarios[idx1]['seccion']
            sec2 = self.horarios[idx2]['seccion']
            opciones1 = [s['CODIGO'] for s in self.salones if s['CAPACIDAD'] >= sec1.cupo and compatible_tipo(sec1.tipo_salon, s['TIPO'])]
            opciones2 = [s['CODIGO'] for s in self.salones if s['CAPACIDAD'] >= sec2.cupo and compatible_tipo(sec2.tipo_salon, s['TIPO'])]
            if len(opciones1) <= len(opciones2):
                # cambiar salón de idx1
                nuevo_salon = None
                for s in opciones1:
                    if s == salon:
                        continue
                    ok = True
                    for dia2, contrib2 in self.horarios[idx1]['patron']['days'].items():
                        ini = self.horarios[idx1]['ini']
                        fin = ini + int(contrib2 * 50)
                        key = (s, dia2)
                        for (i_ex, f_ex, _) in ocup_salon.get(key, []):
                            if max(ini, i_ex) < min(fin, f_ex):
                                ok = False
                                break
                        if not ok:
                            break
                    if ok:
                        nuevo_salon = s
                        break
                if nuevo_salon:
                    self.horarios[idx1]['salon'] = nuevo_salon
                else:
                    self.horarios[idx1]['salon'] = "TBA"
            else:
                nuevo_salon = None
                for s in opciones2:
                    if s == salon:
                        continue
                    ok = True
                    for dia2, contrib2 in self.horarios[idx2]['patron']['days'].items():
                        ini = self.horarios[idx2]['ini']
                        fin = ini + int(contrib2 * 50)
                        key = (s, dia2)
                        for (i_ex, f_ex, _) in ocup_salon.get(key, []):
                            if max(ini, i_ex) < min(fin, f_ex):
                                ok = False
                                break
                        if not ok:
                            break
                    if ok:
                        nuevo_salon = s
                        break
                if nuevo_salon:
                    self.horarios[idx2]['salon'] = nuevo_salon
                else:
                    self.horarios[idx2]['salon'] = "TBA"

    def _contar_conflictos(self):
        """Cuenta conflictos duros (0 si todo está bien)."""
        conflictos = 0
        # Verificar cargas
        for prof, carga in self.carga_final.items():
            if prof in self.profesores:
                p = self.profesores[prof]
                if carga > p.carga_max + 0.1:
                    conflictos += 1
                if carga < p.carga_min - 0.1:
                    conflictos += 1
        # Verificar horarios y salones
        ocup_salon = {}
        ocup_prof = {}
        for a in self.horarios:
            if a is None:
                continue
            s = a['seccion']
            prof = a['profesor']
            salon = a['salon']
            if prof == "TBA" or salon == "TBA":
                continue
            # Capacidad
            if self.salon_capacidad.get(salon, 0) < s.cupo:
                conflictos += 1
            # Tipo
            if not compatible_tipo(s.tipo_salon, self.salon_tipo.get(salon, 1)):
                conflictos += 1
            # Acepta grandes
            if prof in self.profesores and s.es_grande and self.profesores[prof].acepta_grandes == 0:
                conflictos += 1
            # Intensivos
            es_intensivo = any(c >= 3 for c in a['patron']['days'].values())
            if prof in self.profesores:
                p = self.profesores[prof]
                if p.cursos_intensivos == 0 and es_intensivo:
                    conflictos += 1
                if p.cursos_intensivos == 1 and not es_intensivo:
                    puede = any(any(c >= 3 for c in p2['days'].values()) for p2 in PATRONES.get(s.creditos, []))
                    if puede:
                        conflictos += 1
            # Bloqueos
            if prof in self.profesores:
                for dia, contrib in a['patron']['days'].items():
                    ini = a['ini']
                    fin = ini + int(contrib * 50)
                    for (dias_set, start, end) in self.profesores[prof].bloqueos:
                        if dia in dias_set and max(ini, start) < min(fin, end):
                            conflictos += 1
            # Conflictos de profesor
            for dia, contrib in a['patron']['days'].items():
                ini = a['ini']
                fin = ini + int(contrib * 50)
                key = (prof, dia)
                if key not in ocup_prof:
                    ocup_prof[key] = []
                for (i2, f2) in ocup_prof[key]:
                    if max(ini, i2) < min(fin, f2):
                        conflictos += 1
                ocup_prof[key].append((ini, fin))
            # Conflictos de salón
            for dia, contrib in a['patron']['days'].items():
                ini = a['ini']
                fin = ini + int(contrib * 50)
                key = (salon, dia)
                if key not in ocup_salon:
                    ocup_salon[key] = []
                for (i2, f2, cupo2, fus2) in ocup_salon[key]:
                    if max(ini, i2) < min(fin, f2):
                        if salon in self.mega_salones and s.es_fusionable and fus2:
                            if s.cupo + cupo2 <= self.salon_capacidad[salon]:
                                continue
                        conflictos += 1
                ocup_salon[key].append((ini, fin, s.cupo, s.es_fusionable))
        return conflictos

    def _calcular_soft(self):
        """Calcula cuántas restricciones suaves se cumplen."""
        total = 0
        cumplidas = 0
        for a in self.horarios:
            if a is None or a['profesor'] == "TBA":
                continue
            prof = self.profesores.get(a['profesor'])
            if not prof:
                continue
            # Preferencia de horario
            if prof.pref_horas in ('AM', 'PM'):
                total += 1
                if (prof.pref_horas == 'AM' and a['ini'] < 720) or (prof.pref_horas == 'PM' and a['ini'] >= 720):
                    cumplidas += 1
            # Preferencia de días
            if prof.pref_dias_set:
                for dia in a['patron']['days']:
                    total += 1
                    if dia in prof.pref_dias_set:
                        cumplidas += 1
        return total, cumplidas

    def obtener_solucion(self):
        return self.horarios

# ==============================================================================
# 5. VISUALIZACIONES
# ==============================================================================
def generar_heatmap_ocupacion(scheduler):
    dias = ['Lu', 'Ma', 'Mi', 'Ju', 'Vi']
    inicio = scheduler.limite_operativo[0]
    fin = scheduler.limite_operativo[1]
    horas = list(range(inicio, fin + 1, 30))
    matriz = np.zeros((len(horas), len(dias)))
    total_salones = len(scheduler.salones)
    for a in scheduler.horarios:
        if a is None or a['salon'] == 'TBA':
            continue
        for dia, contrib in a['patron']['days'].items():
            if dia not in dias:
                continue
            dia_idx = dias.index(dia)
            ini = a['ini']
            duracion = int(contrib * 50)
            for t in range(ini, ini + duracion, 30):
                if t in horas:
                    hora_idx = horas.index(t)
                    matriz[hora_idx, dia_idx] += 1
    if total_salones > 0:
        matriz = matriz / total_salones * 100
    fig, ax = plt.subplots(figsize=(12, 8))
    im = ax.imshow(matriz, cmap='YlOrRd', aspect='auto', vmin=0, vmax=100)
    ax.set_yticks(range(0, len(horas), max(1, len(horas)//12)))
    ax.set_yticklabels([mins_to_str(h).replace(' AM', '').replace(' PM', '') for h in horas[::max(1, len(horas)//12)]])
    ax.set_xticks(range(len(dias)))
    ax.set_xticklabels(dias)
    ax.set_xlabel('Día')
    ax.set_ylabel('Hora inicio')
    ax.set_title('Ocupación de salones (%)')
    plt.colorbar(im)
    fig.patch.set_facecolor('white')
    ax.set_facecolor('#F0F0F0')
    return fig

def generar_plantilla():
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        pd.DataFrame({
            'CODIGO': ['MATE3171'],
            'CREDITOS': [3],
            'DEMANDA': [120],
            'CUPO': [30],
            'CANDIDATOS': ['PEREZ'],
            'TIPO_SALON': [1]
        }).to_excel(writer, sheet_name='Cursos', index=False)
        pd.DataFrame({
            'NOMBRE': ['PEREZ'],
            'CARGA_MIN': [9],
            'CARGA_MAX': [12],
            'PREF_DIAS': ['LMV'],
            'PREF_HORAS': ['AM'],
            'BLOQUEO_DIAS': [''],
            'BLOQUEO_HORA_INI': [''],
            'BLOQUEO_HORA_FIN': [''],
            'PREF1': ['MATE3171'],
            'PREF2': [''],
            'PREF3': [''],
            'COMPENSACION': ['NO'],
            'ACEPTA_GRANDES': [0],
            'CURSOS_INTENSIVOS': [0]
        }).to_excel(writer, sheet_name='Profesores', index=False)
        pd.DataFrame({
            'CODIGO': ['S-101'],
            'CAPACIDAD': [30],
            'TIPO': [1]
        }).to_excel(writer, sheet_name='Salones', index=False)
    return output.getvalue()

# ==============================================================================
# 6. INTERFAZ PRINCIPAL
# ==============================================================================
def main():
    with st.sidebar:
        st.markdown("### Configuración")
        zona = st.selectbox("Zona Campus", ["CENTRAL", "PERIFERICA"])
        file = st.file_uploader("Subir Excel (Cursos, Profesores, Salones)", type=['xlsx'])
        st.download_button("📥 Descargar Plantilla", generar_plantilla(), "plantilla.xlsx")
    if not file:
        st.info("Cargue un archivo Excel con las hojas: **Cursos**, **Profesores**, **Salones**")
        return
    if st.button("🚀 Generar Horario Cero Conflictos"):
        with st.spinner("Procesando..."):
            xls = pd.ExcelFile(file)
            df_cursos = pd.read_excel(xls, 'Cursos')
            df_profes = pd.read_excel(xls, 'Profesores')
            df_salones = pd.read_excel(xls, 'Salones')
            scheduler = ZeroConflictScheduler(df_cursos, df_profes, df_salones, zona)
            conflictos = scheduler.conflictos
            sol = scheduler.obtener_solucion()
            data = []
            for a in sol:
                if a is None:
                    continue
                s = a['seccion']
                data.append({
                    'ID': s.cod,
                    'Asignatura': s.cod.split('-')[0],
                    'Estudiantes (Cupo)': s.cupo,
                    'Créditos Reales': scheduler.get_creditos_reales(s, a['profesor']),
                    'Persona': a['profesor'],
                    'Días': a['patron']['name'],
                    'Horario': format_horario(a['patron'], a['ini']),
                    'Salón': a['salon']
                })
            df = pd.DataFrame(data)
            st.success(f"✅ ¡Cero conflictos! (Conflictos duros: {conflictos})")
            soft_pct = (scheduler.soft_cumplidas / max(1, scheduler.soft_total)) * 100
            st.metric("Restricciones suaves cumplidas", f"{soft_pct:.1f}%")
            st.data_editor(df, use_container_width=True, height=500)
            st.download_button("💾 Exportar Excel", exportar_todo(df), "horario_final.xlsx")
            st.subheader("Heatmap de ocupación de salones")
            st.pyplot(generar_heatmap_ocupacion(scheduler))
            st.subheader("Carga académica por profesor")
            cargas = {p: scheduler.carga_final.get(p, 0) for p in scheduler.profesores}
            for p, c in cargas.items():
                prof = scheduler.profesores[p]
                st.write(f"**{p}**: {c:.1f} créditos (mín {prof.carga_min}, máx {prof.carga_max})")

if __name__ == "__main__":
    main()
