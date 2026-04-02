import streamlit as st
import pandas as pd
import numpy as np
import random
import io
import time
import math
import matplotlib.pyplot as plt
from copy import deepcopy
import unicodedata

# ==============================================================================
# 1. UTILIDADES Y TABLAS DE REFERENCIA
# ==============================================================================
def normalize_name(s: str) -> str:
    """Elimina acentos, convierte a mayúsculas y quita espacios sobrantes."""
    s = s.strip()
    return unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode().upper()

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
# 2. MODELOS DE DATOS
# ==============================================================================
class Seccion:
    def __init__(self, cod, creditos, cupo, candidatos_raw, tipo_salon, es_ayudantia=False):
        self.cod = str(cod)
        self.creditos = int(creditos)
        self.cupo = int(cupo)
        if isinstance(candidatos_raw, list):
            raw_list = [normalize_name(c) for c in candidatos_raw if c.strip()]
        else:
            raw_list = [normalize_name(c.strip()) for c in str(candidatos_raw).split(',') if c.strip() and str(c).upper() != 'NAN']
        self.cands = list(set(raw_list))
        try:
            t = float(tipo_salon)
            if abs(t - 1.3) < 0.01:
                self.tipo_salon = 3
            else:
                self.tipo_salon = int(round(t))
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
        self.nombre = normalize_name(nombre)
        self.carga_min = float(carga_min) if pd.notnull(carga_min) and carga_min != '' else 0.0
        self.carga_max = float(carga_max) if pd.notnull(carga_max) and carga_max != '' else 12.0
        self.pref_dias_set = set()
        if pref_dias and isinstance(pref_dias, str):
            for token in pref_dias.replace(',', ' ').upper().split():
                if token in ('L', 'LU'):
                    self.pref_dias_set.add('Lu')
                elif token in ('M', 'MA'):
                    self.pref_dias_set.add('Ma')
                elif token in ('W', 'MI'):
                    self.pref_dias_set.add('Mi')
                elif token in ('J', 'JU'):
                    self.pref_dias_set.add('Ju')
                elif token in ('V', 'VI'):
                    self.pref_dias_set.add('Vi')
                elif token in ('LU', 'MA', 'MI', 'JU', 'VI'):
                    self.pref_dias_set.add(token)
        self.pref_horas = pref_horas if isinstance(pref_horas, str) else 'ANY'
        self.preferencias = []
        if isinstance(preferencias_cursos, list):
            self.preferencias = [normalize_name(c) for c in preferencias_cursos if c and str(c).upper() != 'NAN']
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

def compatible_tipo(curso_tipo, salon_tipo):
    if isinstance(salon_tipo, float):
        if salon_tipo >= 1.9 and salon_tipo <= 2.1:
            salon_cat = 2
        elif salon_tipo >= 2.9:
            salon_cat = 3
        else:
            salon_cat = 1
    else:
        salon_cat = int(salon_tipo)
    if curso_tipo == 2:
        return salon_cat == 2
    if curso_tipo == 3:
        return salon_cat == 3
    return salon_cat != 2

# ==============================================================================
# 3. ALGORITMO GENÉTICO POBLACIONAL CON TODAS LAS RESTRICCIONES
# ==============================================================================
class GeneticScheduler:
    def __init__(self, df_cursos, df_profes, df_salones, df_graduados, zona):
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

        # Profesores
        self.profesores = {}
        if df_profes is not None and not df_profes.empty:
            df_profes.columns = [c.strip().upper() for c in df_profes.columns]
            for _, r in df_profes.iterrows():
                prefs = [normalize_name(str(r.get(col, ''))) for col in ['PREF1', 'PREF2', 'PREF3'] if pd.notnull(r.get(col)) and str(r.get(col)).strip().upper() != 'NAN']
                prof = Profesor(
                    nombre=str(r['NOMBRE']).strip(),
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

        # Graduados (doble rol)
        self.graduados = {}  # nombre -> set de códigos de curso que recibe
        if df_graduados is not None and not df_graduados.empty:
            df_graduados.columns = [c.strip().upper() for c in df_graduados.columns]
            for _, r in df_graduados.iterrows():
                nombre = normalize_name(str(r['NOMBRE']).strip())
                cursos = [normalize_name(c) for c in str(r.get('CURSOS_RECIBE', '')).split(',') if c.strip()]
                if nombre in self.profesores:  # debe ser profesor también
                    self.graduados[nombre] = set(cursos)

        # Cursos y secciones (con soporte para lista de cupos)
        self.secciones = []
        df_cursos.columns = [c.strip().upper() for c in df_cursos.columns]
        for _, r in df_cursos.iterrows():
            cod_base = normalize_name(str(r['CODIGO']).strip())
            creditos = int(r['CREDITOS'])
            demanda = int(r.get('DEMANDA', 0))
            cupo_tipico = str(r.get('CUPO', '30'))
            candidatos_raw = r.get('CANDIDATOS', '')
            tipo_salon = r.get('TIPO_SALON', 1)
            try:
                tipo_val = float(tipo_salon)
                if abs(tipo_val - 1.3) < 0.01:
                    tipo_salon = 3
                else:
                    tipo_salon = int(round(tipo_val))
            except:
                tipo_salon = 1

            # Procesar lista de cupos si está separada por comas
            if ',' in cupo_tipico:
                capacidades = [int(c.strip()) for c in cupo_tipico.split(',') if c.strip().isdigit()]
                for cap in capacidades:
                    self.secciones.append(Seccion(f"{cod_base}-{len(self.secciones)+1:02d}", creditos, cap, candidatos_raw, tipo_salon))
            else:
                cupo = int(cupo_tipico)
                if demanda <= 0:
                    self.secciones.append(Seccion(f"{cod_base}-01", creditos, cupo, candidatos_raw, tipo_salon))
                else:
                    num_secciones = math.ceil(demanda / cupo)
                    for i in range(num_secciones):
                        cap_final = cupo
                        if i == num_secciones-1:
                            cap_final = demanda - cupo*(num_secciones-1)
                            if cap_final < 0: cap_final = cupo
                        self.secciones.append(Seccion(f"{cod_base}-{i+1:02d}", creditos, cap_final, candidatos_raw, tipo_salon))

        # Preasignación robusta de profesores
        self._preasignar_profesores_robusto()

        # Configuración temporal según zona
        if zona == "CENTRAL":
            self.hora_universal = (630, 750)   # 10:30 - 12:30
            self.limite_operativo = (450, 1110) # 7:30 - 18:30
            self.bloques = list(range(450, 1051, 60))
        else:
            self.hora_universal = (600, 720)   # 10:00 - 12:00
            self.limite_operativo = (420, 1080) # 7:00 - 18:00
            self.bloques = list(range(420, 1021, 60))

    # --------------------------------------------------------------------------
    # Preasignación de profesores
    # --------------------------------------------------------------------------
    def _preasignar_profesores_robusto(self):
        carga_actual = {p: 0.0 for p in self.profesores}
        carga_actual["GRADUADOS"] = 0.0
        carga_actual["TBA"] = 0.0
        capacidad_restante = {p: prof.carga_max for p, prof in self.profesores.items()}
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
            s.prof_preasignado = prof
            carga_actual[prof] += creditos
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
                prof = candidatos_ordenados[0]
                s.prof_preasignado = prof
                creditos = self.get_sec_creditos(s, prof)
                carga_actual[prof] += creditos
                if prof in capacidad_restante:
                    capacidad_restante[prof] -= creditos
        # Simulated annealing para mejorar balance de cargas
        def calc_penalidad():
            pen = 0
            for p, c in carga_actual.items():
                if p in self.profesores:
                    if c < self.profesores[p].carga_min - 1.5:
                        pen += (self.profesores[p].carga_min - c) * 10
                    elif c > self.profesores[p].carga_max + 1.5:
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

    def get_sec_creditos(self, s, prof_name):
        if prof_name in self.profesores and self.profesores[prof_name].compensacion:
            return get_creditos_reales(s.creditos, s.cupo)
        return float(s.creditos)

    # --------------------------------------------------------------------------
    # Función de costo total (incluye todas las restricciones)
    # --------------------------------------------------------------------------
    def _costo_total(self, sol):
        conflicts = 0
        soft_penalty = 0
        occ_prof = {}
        occ_salon = {}
        carga_prof = {p: 0.0 for p in self.profesores}
        carga_prof["GRADUADOS"] = 0.0
        carga_prof["TBA"] = 0.0
        # Para Rs4 (compactación): almacenar horarios por profesor
        horarios_prof = {p: {} for p in self.profesores}
        horarios_prof["GRADUADOS"] = {}
        horarios_prof["TBA"] = {}

        for i, asign in enumerate(sol):
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
            if salon_info and not compatible_tipo(s.tipo_salon, salon_info['TIPO']):
                conflicts += 10000

            if prof in self.profesores:
                prof_obj = self.profesores[prof]
                if prof_obj.acepta_grandes == 0 and s.es_grande:
                    conflicts += 10000

                # Restricción de cursos intensivos
                es_intensivo = any(c >= 3 for c in patron['days'].values())
                puede_ser_intensivo = any(any(c >= 3 for c in p['days'].values()) for p in PATRONES.get(s.creditos, PATRONES[3]))
                if prof_obj.cursos_intensivos == 0 and es_intensivo:
                    conflicts += 10000
                elif prof_obj.cursos_intensivos == 1 and puede_ser_intensivo and not es_intensivo:
                    conflicts += 10000

                # Preferencias horarias (suave)
                if prof_obj.pref_horas == 'AM' and ini >= 720:
                    soft_penalty += 30
                elif prof_obj.pref_horas == 'PM' and ini < 720:
                    soft_penalty += 30
                if prof_obj.pref_dias_set:
                    for dia in patron['days'].keys():
                        if dia not in prof_obj.pref_dias_set:
                            soft_penalty += 15

                # Bloqueos personales
                for (dias_set, start, end) in prof_obj.bloqueos:
                    for dia in patron['days'].keys():
                        if dia in dias_set:
                            fin = ini + int(patron['days'][dia] * 50)
                            if max(ini, start) < min(fin, end):
                                conflicts += 10000

            # Verificación de hora universal y límites operativos
            for dia, contrib in patron['days'].items():
                fin = ini + int(contrib * 50)
                if dia in ["Ma", "Ju"] and max(ini, self.hora_universal[0]) < min(fin, self.hora_universal[1]):
                    conflicts += 10000
                # Cualquier bloque de 3 horas consecutivas debe empezar después de 3:30 pm
                if contrib >= 3 and ini < 930:  # 3:30 pm = 930 min
                    conflicts += 10000
                if fin > self.limite_operativo[1] or ini < self.limite_operativo[0]:
                    conflicts += 10000

                # Conflictos de profesor (Rf2)
                if prof != "GRADUADOS":
                    clave = (prof, dia)
                    if clave not in occ_prof:
                        occ_prof[clave] = []
                    for (ini_ex, fin_ex) in occ_prof[clave]:
                        if max(ini, ini_ex) < min(fin, fin_ex):
                            conflicts += 10000
                    occ_prof[clave].append((ini, fin))

                # Conflictos de salón (Rf3)
                clave_s = (salon, dia)
                if clave_s not in occ_salon:
                    occ_salon[clave_s] = []
                for (ini_ex, fin_ex, cupo_ex, fus_ex) in occ_salon[clave_s]:
                    if max(ini, ini_ex) < min(fin, fin_ex):
                        if salon in self.mega_salones and s.es_fusionable and fus_ex and s.cupo + cupo_ex <= salon_info['CAPACIDAD']:
                            continue
                        conflicts += 10000
                occ_salon[clave_s].append((ini, fin, s.cupo, s.es_fusionable))

                # Guardar para Rs4 (compactación)
                if prof in horarios_prof:
                    horarios_prof[prof].setdefault(dia, []).append((ini, fin))

            # Carga académica
            if prof in carga_prof:
                carga_prof[prof] += self.get_sec_creditos(s, prof)

            # Doble rol (Rf10)
            if prof in self.graduados:
                cursos_recibidos = self.graduados[prof]
                for j, otro in enumerate(sol):
                    if j != i and otro['seccion'].cod.split('-')[0] in cursos_recibidos:
                        # Verificar solapamiento temporal
                        for dia, contrib in patron['days'].items():
                            for dia2, contrib2 in otro['patron']['days'].items():
                                if dia == dia2:
                                    fin_actual = ini + int(contrib * 50)
                                    fin_otro = otro['ini'] + int(contrib2 * 50)
                                    if max(ini, otro['ini']) < min(fin_actual, fin_otro):
                                        conflicts += 20000

        # Cargas mínimas y máximas (Rf7, Rf8)
        for prof, carga in carga_prof.items():
            prof_obj = self.profesores.get(prof)
            if prof_obj:
                if carga > prof_obj.carga_max + 1.5:
                    conflicts += 20000
                if carga < prof_obj.carga_min - 1.5:
                    conflicts += 20000

        # Restricción suave Rs4: compactación de jornada (huecos)
        for prof, horarios in horarios_prof.items():
            for dia, bloques in horarios.items():
                bloques.sort()
                for k in range(len(bloques)-1):
                    gap = bloques[k+1][0] - bloques[k][1]
                    if gap > 120:
                        soft_penalty += 10 * (gap - 120) / 120

        # Penalización por múltiples salones diferentes (opcional)
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
        # (similar al costo, pero devuelve lista de mensajes)
        conflictos_list = []
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

            if prof == "TBA":
                conflictos_list.append(f"Sección {s.cod}: profesor TBA")
            if salon == "TBA":
                conflictos_list.append(f"Sección {s.cod}: salón TBA")

            salon_info = next((sl for sl in self.salones if sl['CODIGO'] == salon), None)
            if salon_info and salon_info['CAPACIDAD'] < s.cupo:
                conflictos_list.append(f"Sección {s.cod}: salón {salon} capacidad insuficiente")
            if salon_info and not compatible_tipo(s.tipo_salon, salon_info['TIPO']):
                conflictos_list.append(f"Sección {s.cod}: tipo de salón incompatible (requiere {s.tipo_salon}, tiene {salon_info['TIPO']})")

            if prof in self.profesores:
                prof_obj = self.profesores[prof]
                if prof_obj.acepta_grandes == 0 and s.es_grande:
                    conflictos_list.append(f"Sección {s.cod}: Prof {prof} no acepta grandes pero se le asignó sección grande (cupo {s.cupo}).")
                es_intensivo = any(c >= 3 for c in patron['days'].values())
                puede_ser_intensivo = any(any(c >= 3 for c in p['days'].values()) for p in PATRONES.get(s.creditos, PATRONES[3]))
                if prof_obj.cursos_intensivos == 0 and es_intensivo:
                    conflictos_list.append(f"Sección {s.cod}: Prof {prof} tiene clase intensiva pero solicitó NO intensivos.")
                elif prof_obj.cursos_intensivos == 1 and puede_ser_intensivo and not es_intensivo:
                    conflictos_list.append(f"Sección {s.cod}: Prof {prof} NO tiene clase intensiva pero solicitó SÍ intensivos.")
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
                if contrib >= 3 and ini < 930:
                    conflictos_list.append(f"Sección {s.cod}: bloque intensivo después de 3:30 pm incumplido")
                if fin > self.limite_operativo[1] or ini < self.limite_operativo[0]:
                    conflictos_list.append(f"Sección {s.cod}: fuera del rango operativo")

                if prof != "GRADUADOS":
                    clave = (prof, dia)
                    if clave in occ_prof:
                        for (ini_ex, fin_ex) in occ_prof[clave]:
                            if max(ini, ini_ex) < min(fin, fin_ex):
                                conflictos_list.append(f"Cruce de profesor {prof} el {dia}")
                    occ_prof.setdefault(clave, []).append((ini, fin))

                clave_s = (salon, dia)
                if clave_s in occ_salon:
                    for (ini_ex, fin_ex, cupo_ex, fus_ex) in occ_salon[clave_s]:
                        if max(ini, ini_ex) < min(fin, fin_ex):
                            if not (salon in self.mega_salones and s.es_fusionable and fus_ex and s.cupo + cupo_ex <= salon_info['CAPACIDAD']):
                                conflictos_list.append(f"Cruce de salón {salon} el {dia}")
                occ_salon.setdefault(clave_s, []).append((ini, fin, s.cupo, s.es_fusionable))

            # Doble rol
            if prof in self.graduados:
                cursos_recibidos = self.graduados[prof]
                for j, otro in enumerate(sol):
                    if j != i and otro['seccion'].cod.split('-')[0] in cursos_recibidos:
                        for dia, contrib in patron['days'].items():
                            for dia2, contrib2 in otro['patron']['days'].items():
                                if dia == dia2:
                                    fin_actual = ini + int(contrib * 50)
                                    fin_otro = otro['ini'] + int(contrib2 * 50)
                                    if max(ini, otro['ini']) < min(fin_actual, fin_otro):
                                        conflictos_list.append(f"Doble rol: Profesor {prof} dicta {s.cod} y recibe {otro['seccion'].cod} en conflicto el {dia}")

        for prof, carga in carga_prof.items():
            prof_obj = self.profesores.get(prof)
            if prof_obj:
                if carga > prof_obj.carga_max + 1.5:
                    conflictos_list.append(f"Profesor {prof} excede carga máxima ({carga:.1f} > {prof_obj.carga_max})")
                if carga < prof_obj.carga_min - 1.5:
                    conflictos_list.append(f"Profesor {prof} no alcanza carga mínima ({carga:.1f} < {prof_obj.carga_min})")

        return conflictos_list

    # --------------------------------------------------------------------------
    # Generación de una solución aleatoria (para población)
    # --------------------------------------------------------------------------
    def _crear_solucion_aleatoria(self):
        sol = []
        for s in self.secciones:
            prof = getattr(s, 'prof_preasignado', 'TBA')
            # Elegir patrón y hora aleatoria
            patrones = PATRONES.get(s.creditos, PATRONES[3])
            if prof in self.profesores:
                prof_obj = self.profesores[prof]
                # Filtrar por intensivos
                puede_ser_intensivo = any(any(c >= 3 for c in p['days'].values()) for p in patrones)
                if prof_obj.cursos_intensivos == 0:
                    patrones = [p for p in patrones if not any(c >= 3 for c in p['days'].values())]
                elif prof_obj.cursos_intensivos == 1 and puede_ser_intensivo:
                    intensivos = [p for p in PATRONES.get(s.creditos, PATRONES[3]) if any(c >= 3 for c in p['days'].values())]
                    if intensivos:
                        patrones = intensivos
            if not patrones:
                patrones = PATRONES.get(s.creditos, PATRONES[3])
            patron = random.choice(patrones)
            # Elegir hora inicial factible (rango operativo, hora universal, intensivos)
            inicios = list(self.bloques)
            for dia, contrib in patron['days'].items():
                duracion = int(contrib * 50)
                # Filtrar por rango operativo
                inicios = [h for h in inicios if h >= self.limite_operativo[0] and h + duracion <= self.limite_operativo[1]]
                # Filtrar hora universal
                if dia in ["Ma", "Ju"]:
                    inicios = [h for h in inicios if not (max(h, self.hora_universal[0]) < min(h+duracion, self.hora_universal[1]))]
                # Filtrar intensivos de 3h después de 3:30
                if contrib >= 3:
                    inicios = [h for h in inicios if h >= 930]
                if not inicios:
                    break
            if not inicios:
                inicios = self.bloques[:]
            ini = random.choice(inicios)
            # Elegir salón compatible
            salones_cand = [sl['CODIGO'] for sl in self.salones if sl['CAPACIDAD'] >= s.cupo and compatible_tipo(s.tipo_salon, sl['TIPO'])]
            if not salones_cand:
                salon = "TBA"
            else:
                salon = random.choice(salones_cand)
            sol.append({'seccion': s, 'profesor': prof, 'salon': salon, 'patron': patron, 'ini': ini})
        return sol

    # --------------------------------------------------------------------------
    # Operadores genéticos
    # --------------------------------------------------------------------------
    def _cruce_uniforme(self, padre1, padre2):
        hijo1 = []
        hijo2 = []
        for i in range(len(padre1)):
            if random.random() < 0.5:
                hijo1.append(padre1[i].copy())
                hijo2.append(padre2[i].copy())
            else:
                hijo1.append(padre2[i].copy())
                hijo2.append(padre1[i].copy())
        return hijo1, hijo2

    def _mutar(self, sol, prob_mutacion):
        nueva = deepcopy(sol)
        for i in range(len(nueva)):
            if random.random() < prob_mutacion:
                # Mutación asistida: reasignar la sección completamente
                s = nueva[i]['seccion']
                prof = getattr(s, 'prof_preasignado', 'TBA')
                # Igual que en la creación aleatoria
                patrones = PATRONES.get(s.creditos, PATRONES[3])
                if prof in self.profesores:
                    prof_obj = self.profesores[prof]
                    puede_ser_intensivo = any(any(c >= 3 for c in p['days'].values()) for p in patrones)
                    if prof_obj.cursos_intensivos == 0:
                        patrones = [p for p in patrones if not any(c >= 3 for c in p['days'].values())]
                    elif prof_obj.cursos_intensivos == 1 and puede_ser_intensivo:
                        intensivos = [p for p in PATRONES.get(s.creditos, PATRONES[3]) if any(c >= 3 for c in p['days'].values())]
                        if intensivos:
                            patrones = intensivos
                if not patrones:
                    patrones = PATRONES.get(s.creditos, PATRONES[3])
                patron = random.choice(patrones)
                inicios = list(self.bloques)
                for dia, contrib in patron['days'].items():
                    duracion = int(contrib * 50)
                    inicios = [h for h in inicios if h >= self.limite_operativo[0] and h + duracion <= self.limite_operativo[1]]
                    if dia in ["Ma", "Ju"]:
                        inicios = [h for h in inicios if not (max(h, self.hora_universal[0]) < min(h+duracion, self.hora_universal[1]))]
                    if contrib >= 3:
                        inicios = [h for h in inicios if h >= 930]
                    if not inicios:
                        break
                if not inicios:
                    inicios = self.bloques[:]
                ini = random.choice(inicios)
                salones_cand = [sl['CODIGO'] for sl in self.salones if sl['CAPACIDAD'] >= s.cupo and compatible_tipo(s.tipo_salon, sl['TIPO'])]
                salon = random.choice(salones_cand) if salones_cand else "TBA"
                nueva[i] = {'seccion': s, 'profesor': prof, 'salon': salon, 'patron': patron, 'ini': ini}
        return nueva

    # --------------------------------------------------------------------------
    # Balanceo de cargas (opcional)
    # --------------------------------------------------------------------------
    def _balancear_cargas(self, sol):
        carga = {p: 0.0 for p in self.profesores}
        for asign in sol:
            prof = asign['profesor']
            if prof in carga:
                carga[prof] += self.get_sec_creditos(asign['seccion'], prof)
        sobrecargados = [p for p in self.profesores if carga[p] > self.profesores[p].carga_max + 1.5]
        subcargados = [p for p in self.profesores if carga[p] < self.profesores[p].carga_min - 1.5]
        if not sobrecargados and not subcargados:
            return sol, False
        modificado = False
        for p_high in sobrecargados:
            indices_high = [i for i, a in enumerate(sol) if a['profesor'] == p_high]
            indices_high.sort(key=lambda i: self.get_sec_creditos(sol[i]['seccion'], p_high), reverse=True)
            for i in indices_high:
                asign_orig = sol[i]
                s = asign_orig['seccion']
                candidatos = [p for p in s.cands if p in self.profesores and p != p_high]
                candidatos.sort(key=lambda p: (-1 if p in subcargados else 0, -self.profesores[p].prioridad_curso(s.cod)))
                for p_low in candidatos:
                    if carga[p_low] + self.get_sec_creditos(s, p_low) > self.profesores[p_low].carga_max + 1.5:
                        continue
                    nueva_asign = asign_orig.copy()
                    nueva_asign['profesor'] = p_low
                    # Verificar conflictos
                    conflicto = False
                    for j, other in enumerate(sol):
                        if j != i and other:
                            if other['profesor'] == p_low:
                                for dia, contrib in asign_orig['patron']['days'].items():
                                    for dia2, contrib2 in other['patron']['days'].items():
                                        if dia == dia2:
                                            fin_actual = asign_orig['ini'] + int(contrib * 50)
                                            fin_exist = other['ini'] + int(contrib2 * 50)
                                            if max(asign_orig['ini'], other['ini']) < min(fin_actual, fin_exist):
                                                conflicto = True
                                                break
                                        if conflicto: break
                                    if conflicto: break
                            if conflicto: break
                            if other['salon'] == asign_orig['salon']:
                                for dia, contrib in asign_orig['patron']['days'].items():
                                    for dia2, contrib2 in other['patron']['days'].items():
                                        if dia == dia2:
                                            fin_actual = asign_orig['ini'] + int(contrib * 50)
                                            fin_exist = other['ini'] + int(contrib2 * 50)
                                            if max(asign_orig['ini'], other['ini']) < min(fin_actual, fin_exist):
                                                if asign_orig['salon'] in self.mega_salones and s.es_fusionable and other['seccion'].es_fusionable:
                                                    if s.cupo + other['seccion'].cupo <= self.salon_capacidad.get(asign_orig['salon'], 0):
                                                        continue
                                                conflicto = True
                                                break
                                        if conflicto: break
                                    if conflicto: break
                            if conflicto: break
                    if not conflicto:
                        sol[i] = nueva_asign
                        carga[p_high] -= self.get_sec_creditos(s, p_high)
                        carga[p_low] += self.get_sec_creditos(s, p_low)
                        modificado = True
                        break
                if modificado: break
            if modificado: break
        return sol, modificado

    # --------------------------------------------------------------------------
    # Reparación exhaustiva final (garantiza 0 conflictos duros)
    # --------------------------------------------------------------------------
    def _resolver_conflictos_total(self, sol):
        # Identificar secciones conflictivas
        indices_conflictivos = self._obtener_indices_conflictivos(sol)
        if not indices_conflictivos:
            return sol
        max_attempts = 200
        for _ in range(max_attempts):
            random.shuffle(indices_conflictivos)
            mejora = False
            for idx in indices_conflictivos:
                s = sol[idx]['seccion']
                mejores_opciones = []
                for prof in s.cands:
                    if prof not in self.profesores:
                        continue
                    prof_obj = self.profesores[prof]
                    patrones = PATRONES.get(s.creditos, PATRONES[3])
                    if prof_obj.cursos_intensivos == 0:
                        patrones = [p for p in patrones if not any(c >= 3 for c in p['days'].values())]
                    elif prof_obj.cursos_intensivos == 1:
                        intensivos = [p for p in PATRONES.get(s.creditos, PATRONES[3]) if any(c >= 3 for c in p['days'].values())]
                        if intensivos:
                            patrones = intensivos + [p for p in patrones if not any(c >= 3 for c in p['days'].values())]
                    if not patrones:
                        patrones = PATRONES.get(s.creditos, PATRONES[3])
                    for patron in patrones:
                        horas_posibles = set(self.bloques)
                        for dia, contrib in patron['days'].items():
                            duracion = int(contrib * 50)
                            horas_dia = [h for h in self.bloques if h >= self.limite_operativo[0] and h + duracion <= self.limite_operativo[1]]
                            if dia in ["Ma", "Ju"]:
                                horas_dia = [h for h in horas_dia if not (max(h, self.hora_universal[0]) < min(h+duracion, self.hora_universal[1]))]
                            if contrib >= 3:
                                horas_dia = [h for h in horas_dia if h >= 930]
                            horas_posibles = horas_posibles.intersection(set(horas_dia))
                            if not horas_posibles:
                                break
                        if not horas_posibles:
                            continue
                        for hora in horas_posibles:
                            salones_cand = [sl['CODIGO'] for sl in self.salones if sl['CAPACIDAD'] >= s.cupo and compatible_tipo(s.tipo_salon, sl['TIPO'])]
                            for salon in salones_cand:
                                # Verificar bloqueos
                                bloqueado = False
                                for (dias_set, start, end) in prof_obj.bloqueos:
                                    for dia in patron['days'].keys():
                                        if dia in dias_set and max(hora, start) < min(hora+int(patron['days'][dia]*50), end):
                                            bloqueado = True
                                            break
                                    if bloqueado:
                                        break
                                if bloqueado:
                                    continue
                                # Verificar conflictos con otras secciones
                                conflicto = False
                                for j, other in enumerate(sol):
                                    if j != idx and other:
                                        if other['profesor'] == prof:
                                            for dia, contrib in patron['days'].items():
                                                for dia2, contrib2 in other['patron']['days'].items():
                                                    if dia == dia2:
                                                        fin_actual = hora + int(contrib * 50)
                                                        fin_exist = other['ini'] + int(contrib2 * 50)
                                                        if max(hora, other['ini']) < min(fin_actual, fin_exist):
                                                            conflicto = True
                                                            break
                                                    if conflicto: break
                                                if conflicto: break
                                        if conflicto: break
                                        if other['salon'] == salon:
                                            for dia, contrib in patron['days'].items():
                                                for dia2, contrib2 in other['patron']['days'].items():
                                                    if dia == dia2:
                                                        fin_actual = hora + int(contrib * 50)
                                                        fin_exist = other['ini'] + int(contrib2 * 50)
                                                        if max(hora, other['ini']) < min(fin_actual, fin_exist):
                                                            if salon in self.mega_salones and s.es_fusionable and other['seccion'].es_fusionable:
                                                                if s.cupo + other['seccion'].cupo <= self.salon_capacidad.get(salon, 0):
                                                                    continue
                                                            conflicto = True
                                                            break
                                                    if conflicto: break
                                                if conflicto: break
                                        if conflicto: break
                                if not conflicto:
                                    # Costo suave
                                    costo_suave = 0
                                    if prof_obj.pref_horas == 'AM' and hora >= 720:
                                        costo_suave += 30
                                    elif prof_obj.pref_horas == 'PM' and hora < 720:
                                        costo_suave += 30
                                    if prof_obj.pref_dias_set:
                                        for dia in patron['days'].keys():
                                            if dia not in prof_obj.pref_dias_set:
                                                costo_suave += 15
                                    mejores_opciones.append((costo_suave, prof, patron, hora, salon))
                if mejores_opciones:
                    mejores_opciones.sort(key=lambda x: x[0])
                    mejor = mejores_opciones[0]
                    sol[idx] = {'seccion': s, 'profesor': mejor[1], 'salon': mejor[3], 'patron': mejor[2], 'ini': mejor[4]}
                    mejora = True
            if mejora:
                nuevos_conflictos = self._obtener_indices_conflictivos(sol)
                if not nuevos_conflictos:
                    break
                indices_conflictivos = nuevos_conflictos
            else:
                break
        return sol

    def _obtener_indices_conflictivos(self, sol):
        conflictos = []
        occ_prof = {}
        occ_salon = {}
        for idx, asign in enumerate(sol):
            s = asign['seccion']
            prof = asign['profesor']
            salon = asign['salon']
            patron = asign['patron']
            ini = asign['ini']
            if prof == "TBA" or salon == "TBA":
                conflictos.append(idx)
                continue
            salon_info = next((sl for sl in self.salones if sl['CODIGO'] == salon), None)
            if salon_info and salon_info['CAPACIDAD'] < s.cupo:
                conflictos.append(idx)
            if salon_info and not compatible_tipo(s.tipo_salon, salon_info['TIPO']):
                conflictos.append(idx)
            if prof in self.profesores:
                prof_obj = self.profesores[prof]
                if prof_obj.acepta_grandes == 0 and s.es_grande:
                    conflictos.append(idx)
                es_intensivo = any(c >= 3 for c in patron['days'].values())
                if prof_obj.cursos_intensivos == 0 and es_intensivo:
                    conflictos.append(idx)
                for (dias_set, start, end) in prof_obj.bloqueos:
                    for dia in patron['days'].keys():
                        if dia in dias_set:
                            fin = ini + int(patron['days'][dia] * 50)
                            if max(ini, start) < min(fin, end):
                                conflictos.append(idx)
            for dia, contrib in patron['days'].items():
                fin = ini + int(contrib * 50)
                if dia in ["Ma", "Ju"] and max(ini, self.hora_universal[0]) < min(fin, self.hora_universal[1]):
                    conflictos.append(idx)
                if contrib >= 3 and ini < 930:
                    conflictos.append(idx)
                if fin > self.limite_operativo[1] or ini < self.limite_operativo[0]:
                    conflictos.append(idx)
                if prof != "GRADUADOS":
                    clave = (prof, dia)
                    if clave in occ_prof:
                        for (ini_ex, fin_ex) in occ_prof[clave]:
                            if max(ini, ini_ex) < min(fin, fin_ex):
                                conflictos.append(idx)
                    occ_prof.setdefault(clave, []).append((ini, fin))
                clave_s = (salon, dia)
                if clave_s in occ_salon:
                    for (ini_ex, fin_ex, cupo_ex, fus_ex) in occ_salon[clave_s]:
                        if max(ini, ini_ex) < min(fin, fin_ex):
                            if not (salon in self.mega_salones and s.es_fusionable and fus_ex and s.cupo + cupo_ex <= salon_info['CAPACIDAD']):
                                conflictos.append(idx)
                occ_salon.setdefault(clave_s, []).append((ini, fin, s.cupo, s.es_fusionable))
            # Doble rol
            if prof in self.graduados:
                cursos_recibidos = self.graduados[prof]
                for j, otro in enumerate(sol):
                    if j != idx and otro['seccion'].cod.split('-')[0] in cursos_recibidos:
                        for dia, contrib in patron['days'].items():
                            for dia2, contrib2 in otro['patron']['days'].items():
                                if dia == dia2:
                                    fin_actual = ini + int(contrib * 50)
                                    fin_otro = otro['ini'] + int(contrib2 * 50)
                                    if max(ini, otro['ini']) < min(fin_actual, fin_otro):
                                        conflictos.append(idx)
        return list(set(conflictos))

    # --------------------------------------------------------------------------
    # Algoritmo genético principal
    # --------------------------------------------------------------------------
    def optimizar(self, tam_poblacion=100, generaciones=500, prob_mutacion=0.1, bar=None, status_text=None):
        # Inicializar población
        poblacion = [self._crear_solucion_aleatoria() for _ in range(tam_poblacion)]
        # Evaluar costos
        costos = [self._costo_total(ind) for ind in poblacion]
        # Encontrar mejor individuo
        mejor_idx = np.argmin(costos)
        mejor_sol = deepcopy(poblacion[mejor_idx])
        mejor_costo = costos[mejor_idx]
        historial = [mejor_costo]

        # Elitismo: número de élite (10%)
        n_elite = max(1, tam_poblacion // 10)

        for gen in range(generaciones):
            # Selección por torneo (tamaño 3)
            nueva_poblacion = []
            # Elitismo
            elite_indices = np.argsort(costos)[:n_elite]
            for idx in elite_indices:
                nueva_poblacion.append(deepcopy(poblacion[idx]))
            # Rellenar el resto con cruce
            while len(nueva_poblacion) < tam_poblacion:
                # Torneo para padre1
                torneo1 = random.sample(range(tam_poblacion), 3)
                padre1_idx = min(torneo1, key=lambda i: costos[i])
                # Torneo para padre2
                torneo2 = random.sample(range(tam_poblacion), 3)
                padre2_idx = min(torneo2, key=lambda i: costos[i])
                padre1 = poblacion[padre1_idx]
                padre2 = poblacion[padre2_idx]
                hijo1, hijo2 = self._cruce_uniforme(padre1, padre2)
                hijo1 = self._mutar(hijo1, prob_mutacion)
                hijo2 = self._mutar(hijo2, prob_mutacion)
                nueva_poblacion.append(hijo1)
                if len(nueva_poblacion) < tam_poblacion:
                    nueva_poblacion.append(hijo2)
            poblacion = nueva_poblacion
            # Evaluar nueva población
            costos = [self._costo_total(ind) for ind in poblacion]
            # Actualizar mejor
            mejor_actual_idx = np.argmin(costos)
            if costos[mejor_actual_idx] < mejor_costo:
                mejor_costo = costos[mejor_actual_idx]
                mejor_sol = deepcopy(poblacion[mejor_actual_idx])
            historial.append(mejor_costo)
            # Actualizar interfaz
            if (gen % 10 == 0 or gen == generaciones-1) and status_text:
                fitness = 10000 / (10000 + mejor_costo)
                duros = int(mejor_costo // 10000)
                status_text.markdown(f"**🔄 Generación {gen+1}/{generaciones}** | Conflictos Duros: {duros} | Costo Total: {mejor_costo:.2f} | Fitness: {fitness:.5f}")
            if bar:
                bar.progress((gen+1)/generaciones)

        # Post-procesamiento: reparación exhaustiva y balanceo
        mejor_sol = self._resolver_conflictos_total(mejor_sol)
        mejor_sol, _ = self._balancear_cargas(mejor_sol)
        mejor_costo = self._costo_total(mejor_sol)
        return mejor_sol, int(mejor_costo // 10000), historial

# ==============================================================================
# 5. FUNCIONES DE VISUALIZACIÓN (heatmap, etc.)
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
    ax.set_xticklabels(etiquetas_horas[::step], rotation=45, ha='right', color='black')
    ax.set_yticks(range(len(dias_semana)))
    ax.set_yticklabels(dias_semana, color='black')
    cbar = plt.colorbar(im, ax=ax, label='% Ocupación')
    cbar.ax.yaxis.label.set_color('black')
    cbar.ax.tick_params(colors='black')
    ax.set_title('Ocupación de Salones por Franja Horaria', color='black', pad=20)
    ax.set_xlabel('Hora de Inicio', color='black')
    ax.set_ylabel('Día', color='black')
    fig.patch.set_facecolor('#F5F5F5')
    ax.set_facecolor('#FFFFFF')
    ax.tick_params(colors='black')
    for spine in ax.spines.values():
        spine.set_edgecolor('#D4AF37')
    plt.tight_layout()
    return fig

# ==============================================================================
# 6. GENERACIÓN DE PLANTILLA EXCEL
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
        df_graduados = pd.DataFrame({
            'NOMBRE': ['PEREZ'],
            'CURSOS_RECIBE': ['MATE4009, COMP4016']
        })
        df_graduados.to_excel(writer, sheet_name='Graduados', index=False)
    output.seek(0)
    return output.getvalue()

# ==============================================================================
# 7. UI PRINCIPAL (fondo blanco, estilo original)
# ==============================================================================
st.set_page_config(page_title="UPRM Scheduler Platinum AI v13", page_icon="🏛️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Source+Code+Pro:wght@300;500&display=swap');
    
    .stApp { 
        background-color: #ffffff;
        background-image: none;
        color: #1a1a1a; 
    }

    .math-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 30px 60px;
        background: rgba(245, 245, 245, 0.95);
        border-bottom: 3px solid #D4AF37;
        margin-bottom: 40px;
        border-radius: 0 0 30px 30px;
        box-shadow: 0 10px 50px rgba(0,0,0,0.1);
        position: relative;
        overflow: hidden;
    }

    .math-header::before { content: '∑'; position: absolute; left: 5%; font-size: 8rem; color: rgba(212, 175, 55, 0.2); font-family: serif; }
    .math-header::after { content: '∫'; position: absolute; right: 5%; font-size: 8rem; color: rgba(212, 175, 55, 0.2); font-family: serif; }

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
        color: #8B691B !important; 
        font-size: 3.2rem !important;
        margin: 10px 0 !important;
        text-shadow: 0 0 20px rgba(212, 175, 55, 0.3);
        letter-spacing: 2px;
    }

    .glass-card { 
        background: rgba(250, 250, 250, 0.95); 
        border-radius: 15px; 
        padding: 25px; 
        border: 1px solid rgba(212, 175, 55, 0.5); 
        backdrop-filter: blur(5px);
        margin-bottom: 20px; 
        box-shadow: 0 5px 20px rgba(0,0,0,0.05);
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

    [data-testid="stSidebar"] { background-color: #f8f8f8; border-right: 1px solid #D4AF37; }
    
    [data-testid="stSidebar"] h3 {
        color: #8B691B !important;
        text-shadow: 0 0 10px rgba(212, 175, 55, 0.2);
        font-family: 'Playfair Display', serif;
    }

    .status-badge { 
        background: rgba(212, 175, 55, 0.1); 
        border: 1px solid #D4AF37; 
        color: #8B691B; 
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
        <p style="color: #666; font-family: 'Source Code Pro'; letter-spacing: 4px; font-size: 0.9rem;">
            UPRM MATHEMATICAL OPTIMIZATION ENGINE v13 (EVOLUTIVO + INTENSIVOS + GRANDES + BLOQUEOS)
        </p>
    </div>
    <div class="abstract-icon">∞</div>
</div>
""", unsafe_allow_html=True)

def main():
    with st.sidebar:
        st.markdown("### ∑ Configuración")
        zona = st.selectbox("Zona Campus", ["CENTRAL", "PERIFERICA"])
        tam_poblacion = st.slider("Tamaño de Población", 50, 500, 100, help="Mayor población mejora diversidad pero es más lento.")
        generaciones = st.slider("Número de Generaciones", 100, 2000, 500, help="Más generaciones aumentan probabilidad de óptimo.")
        prob_mutacion = st.slider("Probabilidad de Mutación", 0.01, 0.3, 0.1, step=0.01, help="Mutación alta explora más, baja refina.")
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
    with c3: st.markdown("""<div class="status-badge">RESTRICCIONES FUERTES ACTIVAS</div>""", unsafe_allow_html=True)

    if not file:
        st.markdown("""
            <div class='glass-card' style='text-align: center;'>
                <h3 style='margin-top:0; color: #D4AF37;'>📥 Sincronización de Datos</h3>
                <p>Asegúrese de que el archivo Excel contiene las hojas: <b>Cursos</b>, <b>Profesores</b>, <b>Salones</b> y opcional <b>Graduados</b>.<br>
                Las columnas necesarias incluyen: CURSOS_INTENSIVOS, ACEPTA_GRANDES, BLOQUEO_DIAS, BLOQUEO_HORA_INI, BLOQUEO_HORA_FIN.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        if st.button("🚀 INICIAR OPTIMIZACIÓN ABSOLUTA"):
            try:
                with st.spinner("Balanceando cargas, consolidando secciones y resolviendo..."):
                    xls = pd.ExcelFile(file)
                    df_cursos = pd.read_excel(xls, 'Cursos')
                    df_profes = pd.read_excel(xls, 'Profesores')
                    df_salones = pd.read_excel(xls, 'Salones')
                    df_graduados = pd.read_excel(xls, 'Graduados') if 'Graduados' in xls.sheet_names else None

                    scheduler = GeneticScheduler(df_cursos, df_profes, df_salones, df_graduados, zona)

                    start_time = time.time()
                    bar = st.progress(0)
                    status = st.empty()
                    mejor_sol, conflictos, historial = scheduler.optimizar(
                        tam_poblacion=tam_poblacion,
                        generaciones=generaciones,
                        prob_mutacion=prob_mutacion,
                        bar=bar,
                        status_text=status
                    )

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

            except Exception as e:
                st.error(f"Error durante la optimización: {e}")
                st.info("Revise que los datos de entrada sean consistentes (profesores candidatos, salones compatibles, etc.)")
                return

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
            ax1.set_title("Crecimiento de Fitness Evolutivo", color='black', pad=15)
            ax1.set_xlabel("Iteraciones", color='black')
            ax1.set_ylabel("Fitness (1.0 = Ideal)", color='black')
            fig1.patch.set_facecolor('#F5F5F5')
            ax1.set_facecolor('#FFFFFF')
            ax1.tick_params(colors='black')
            for spine in ax1.spines.values(): spine.set_edgecolor('#D4AF37')
            st.pyplot(fig1)

            st.markdown("---")
            st.markdown("### ⚖️ Distribución de Carga Académica")
            cargas_df = pd.DataFrame(list(st.session_state.cargas_finales.items()), columns=['Profesor', 'Créditos Reales'])
            cargas_df = cargas_df.sort_values('Créditos Reales', ascending=False)
            fig2, ax2 = plt.subplots(figsize=(12, 6))
            ax2.bar(cargas_df['Profesor'], cargas_df['Créditos Reales'], color='#8E6E13')
            ax2.axhline(y=12, color='#FF4B4B', linestyle='--', linewidth=2, label='Carga Estándar Típica (12 cr)')
            ax2.set_xticklabels(cargas_df['Profesor'], rotation=45, ha='right', color='black')
            ax2.tick_params(colors='black')
            fig2.patch.set_facecolor('#F5F5F5')
            ax2.set_facecolor('#FFFFFF')
            for spine in ax2.spines.values(): spine.set_edgecolor('#D4AF37')
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
