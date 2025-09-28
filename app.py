# app_horarios_ga_streamlit.py
import streamlit as st
import pandas as pd
import random
import json
import numpy as np
from datetime import datetime, timedelta
import copy
import io
import math
from typing import List, Tuple

# ---------------------------
# UTIL / FUNCIONES BASE (tu código con ligeras adaptaciones)
# ---------------------------
# (Mantengo prácticamente todas tus estructuras y funciones, con algunas mejoras
#  para que el GA pueda llamar a evaluaciones y construir cromosomas)

# -------------------------------------------------
# CLASES Y CONFIG
# -------------------------------------------------
class ConfiguracionSistema:
    def __init__(self, archivo_excel=None):
        self.archivo_excel = archivo_excel
        self.profesores_config = {}
        self.salones = []
        self.cursos_df = None
        
        # Configuración por defecto de restricciones globales
        self.restricciones_globales = {
            "horarios_prohibidos": {
                "Ma": [("10:30", "12:30")],
                "Ju": [("10:30", "12:30")]
            },
            "hora_inicio_min": "07:30",
            "hora_fin_max": "19:30",
            "creditos_max_profesor": 15,
            "creditos_min_profesor": 8,
            "estudiantes_max_salon": 50,
            "horas_max_dia": 8,
            "dias_max_profesor": 5
        }
        
        # Pesos para restricciones suaves
        self.pesos_restricciones = {
            "horario_preferido": 30,
            "compactacion_horario": 20,
            "equilibrio_creditos": 25,
            "utilizacion_salones": 15,
            "estudiantes_por_salon": 10,
            "horas_consecutivas": 18,
            "distribucion_semanal": 12,
            "evitar_horas_pico": 8
        }
        
        if archivo_excel:
            self.cargar_desde_excel()
    
    def cargar_desde_excel(self):
        """Carga la configuración desde el archivo Excel"""
        try:
            # Leer todas las hojas del Excel
            excel_data = pd.read_excel(self.archivo_excel, sheet_name=None)
            
            st.write(f"📊 Hojas disponibles en el Excel: {list(excel_data.keys())}")
            
            # Buscar la hoja que contiene los datos de cursos
            hoja_cursos = None
            for nombre_hoja, df in excel_data.items():
                st.write(f"\n🔍 Analizando hoja '{nombre_hoja}':")
                st.write(f"Columnas: {list(df.columns)}")
                
                # Verificar si esta hoja contiene información de cursos
                columnas_df = [col.lower().strip() for col in df.columns]
                
                if any('profesor' in col or 'docente' in col for col in columnas_df) and any('curso' in col or 'materia' in col or 'asignatura' in col for col in columnas_df):
                    hoja_cursos = df
                    st.success(f"✅ Hoja '{nombre_hoja}' seleccionada como fuente de datos")
                    break
            
            if hoja_cursos is None:
                st.error("❌ No se encontró una hoja con datos de cursos válidos")
                return
            
            self.cursos_df = hoja_cursos
            self.procesar_datos_excel()
            
        except Exception as e:
            st.error(f"❌ Error al cargar el archivo Excel: {e}")
            st.info("ℹ️ Usando configuración por defecto")
    
    def procesar_datos_excel(self):
        """Procesa los datos del Excel y crea la configuración de profesores"""
        if self.cursos_df is None:
            return
        
        df = self.cursos_df.copy()
        
        # Normalizar nombres de columnas
        df.columns = [col.lower().strip().replace(' ', '_') for col in df.columns]
        
        # Mapear columnas comunes
        mapeo_columnas = {
            'profesor': ['profesor', 'docente', 'teacher', 'instructor'],
            'curso': ['curso', 'materia', 'asignatura', 'subject', 'course'],
            'creditos': ['creditos', 'créditos', 'credits', 'horas'],
            'estudiantes': ['estudiantes', 'alumnos', 'students', 'enrollment', 'seccion']
        }
        
        columnas_finales = {}
        for campo, posibles in mapeo_columnas.items():
            for col in df.columns:
                if any(pos in col for pos in posibles):
                    columnas_finales[campo] = col
                    break
        
        st.write(f"🔗 Mapeo de columnas: {columnas_finales}")
        
        # Verificar que tenemos las columnas mínimas necesarias
        if 'profesor' not in columnas_finales or 'curso' not in columnas_finales:
            st.error("❌ Error: No se encontraron las columnas básicas (profesor, curso)")
            return
        
        # Asignar valores por defecto si faltan columnas
        if 'creditos' not in columnas_finales:
            df['creditos_default'] = 3
            columnas_finales['creditos'] = 'creditos_default'
            st.warning("⚠️ No se encontró columna de créditos, usando 3 por defecto")
        
        if 'estudiantes' not in columnas_finales:
            df['estudiantes_default'] = 30
            columnas_finales['estudiantes'] = 'estudiantes_default'
            st.warning("⚠️ No se encontró columna de estudiantes, usando 30 por defecto")
        
        # Limpiar datos
        df = df.dropna(subset=[columnas_finales['profesor'], columnas_finales['curso']])
        
        # Procesar cada profesor
        profesores_unicos = df[columnas_finales['profesor']].unique()
        st.info(f"👨‍🏫 Profesores encontrados: {len(profesores_unicos)}")
        
        for profesor in profesores_unicos:
            if pd.isna(profesor) or str(profesor).strip() == '':
                continue
                
            profesor = str(profesor).strip()
            cursos_profesor = df[df[columnas_finales['profesor']] == profesor]
            
            cursos_lista = []
            creditos_totales = 0
            
            for _, fila in cursos_profesor.iterrows():
                curso_nombre = str(fila[columnas_finales['curso']]).strip()
                
                # Manejar créditos
                try:
                    creditos = int(float(fila[columnas_finales['creditos']]))
                except (ValueError, TypeError):
                    creditos = 3
                
                # Manejar estudiantes
                try:
                    estudiantes = int(float(fila[columnas_finales['estudiantes']]))
                except (ValueError, TypeError):
                    estudiantes = 30
                
                if curso_nombre and curso_nombre != 'nan':
                    cursos_lista.append({
                        "nombre": curso_nombre,
                        "creditos": creditos,
                        "estudiantes": estudiantes
                    })
                    creditos_totales += creditos
            
            if cursos_lista:
                self.profesores_config[profesor] = {
                    "cursos": cursos_lista,
                    "creditos_totales": creditos_totales,
                    "horario_preferido": {},
                    "horario_no_disponible": {}
                }
                
                st.write(f"📚 {profesor}: {len(cursos_lista)} cursos, {creditos_totales} créditos totales")
        
        # Generar salones automáticamente basado en el número de cursos
        total_cursos = sum(len(config['cursos']) for config in self.profesores_config.values())
        num_salones = max(3, min(10, total_cursos // 3))
        self.salones = [f"Salon {i+1}" for i in range(num_salones)]
        
        st.success(f"✅ Configuración completada: {len(self.profesores_config)} profesores, {num_salones} salones")

# -------------------------------------------------
# BLOQUES, TABLA CREDITOS Y UTILS DE HORAS
# -------------------------------------------------
def generar_bloques():
    bloques = []
    id_counter = 1

    # Bloques de 4 créditos (4 días, 1 hora cada día)
    combinaciones_4dias = [
        ["Lu","Ma","Mi","Ju"],
        ["Lu","Ma","Mi","Vi"],
        ["Lu","Ma","Ju","Vi"],
        ["Lu","Mi","Ju","Vi"],
        ["Ma","Mi","Ju","Vi"],
    ]
    for dias in combinaciones_4dias:
        bloques.append({"id": id_counter, "dias": dias, "horas": [1]*4, "creditos": 4})
        id_counter += 1

    # Bloques de 4 créditos (2 días, 2 horas cada día)
    combinaciones_2dias = [
        ["Lu","Mi"],
        ["Lu","Vi"],
        ["Ma","Ju"],
        ["Mi","Vi"],
    ]
    for dias in combinaciones_2dias:
        bloques.append({"id": id_counter, "dias": dias, "horas": [2,2], "creditos": 4})
        id_counter += 1

    # Bloques de 3 créditos
    bloques.append({"id": id_counter, "dias": ["Lu","Mi","Vi"], "horas": [1,1,1], "creditos": 3})
    id_counter += 1
    bloques.append({"id": id_counter, "dias": ["Ma","Ju"], "horas": [1.5,1.5], "creditos": 3})
    id_counter += 1

    # Bloques de 5 créditos
    combinaciones_5creditos = [
        (["Lu","Mi","Vi"], [2,2,1]),
        (["Lu","Ma","Mi","Vi"], [1,1,1,2]),
        (["Lu","Ma","Ju","Vi"], [1,1,1,2]),
        (["Lu","Mi","Ju","Vi"], [1,1,1,2]),
        (["Ma","Mi","Ju","Vi"], [1,1,1,2]),
        (["Ma","Ju","Vi"], [1.5,1.5,2]),
        (["Lu","Ma","Mi","Ju","Vi"], [1,1,1,1,1]),
        (["Lu","Ma","Mi"], [2,1,2]),
    ]
    for dias, horas in combinaciones_5creditos:
        bloques.append({"id": id_counter, "dias": dias, "horas": horas, "creditos": 5})
        id_counter += 1

    # Bloques de 3 créditos (un solo día con 3 horas)
    for dia in ["Lu","Ma","Mi","Ju","Vi"]:
        bloques.append({"id": id_counter, "dias": [dia], "horas": [3], "creditos": 3})
        id_counter += 1

    return bloques

tabla_creditos = {
    1: [(1,44,0),(45,74,0.5),(75,104,1),(105,134,1.5),(135,164,2),(165,194,2.5),
        (195,224,3),(225,254,3.5),(255,284,4),(285,314,4.5),(315,344,5),(345,374,5.5),
        (375,404,6),(405,434,6.5),(435,464,7),(465,494,7.5),(495,524,8)],
    2: [(1,37,0),(38,52,0.5),(53,67,1),(68,82,1.5),(83,97,2),(98,112,2.5),
        (113,127,3),(128,142,3.5),(143,157,4),(158,172,4.5),(173,187,5),(188,202,5.5),
        (203,217,6),(218,232,6.5),(233,247,7),(248,262,7.5),(263,277,8)],
    3: [(1,34,0),(35,44,0.5),(45,54,1),(55,64,1.5),(65,74,2),(75,84,2.5),
        (85,94,3),(95,104,3.5),(105,114,4),(115,124,4.5),(125,134,5),(135,144,5.5),
        (145,154,6),(155,164,6.5),(165,174,7),(175,184,7.5),(185,194,8)],
    4: [(1,33,0),(34,41,0.5),(42,48,1),(49,56,1.5),(57,63,2),(64,71,2.5),
        (72,78,3),(79,86,3.5),(87,93,4),(94,101,4.5),(102,108,5),(109,116,5.5),
        (117,123,6),(124,131,6.5),(132,138,7),(139,146,7.5),(147,153,8)],
    5: [(1,32,0),(33,38,0.5),(39,44,1),(45,50,1.5),(51,56,2),(57,63,2.5),
        (64,69,3),(70,75,3.5),(76,81,4),(82,88,4.5),(89,93,5),(94,99,5.5),
        (100,104,6),(105,110,6.5),(111,116,7),(117,122,7.5),(123,128,8)],
    6: [(1,32,0),(33,37,0.5),(38,42,1),(43,47,1.5),(48,52,2),(53,57,2.5),
        (58,62,3),(63,67,3.5),(68,72,4),(73,77,4.5),(78,82,5),(83,87,5.5),
        (88,92,6),(93,97,6.5),(98,102,7),(103,107,7.5),(108,112,8)]
}

def calcular_creditos_adicionales(horas_contacto, estudiantes):
    if horas_contacto not in tabla_creditos:
        return 0
    for minimo, maximo, creditos in tabla_creditos[horas_contacto]:
        if minimo <= estudiantes <= maximo:
            return creditos
    return 0

# Horario de 7:00 a 19:20 en intervalos de 30 minutos (matching tu original)
horas_inicio = []
for h in range(7, 20):
    for m in [0, 30]:
        if h == 19 and m > 20:
            break
        horas_inicio.append(f"{h:02d}:{m:02d}")

def a_minutos(hhmm):
    h, m = map(int, hhmm.split(":"))
    return h * 60 + m

def es_bloque_tres_horas_valido(dia, hora_inicio, duracion, creditos):
    """Restricción: Las clases de 3 créditos con 3 horas consecutivas 
    SOLO pueden programarse después de las 15:30 (3:30 PM) de lunes a viernes."""
    if creditos == 3 and duracion == 3:
        dias_semana = ["Lu", "Ma", "Mi", "Ju", "Vi"]
        if dia in dias_semana:
            inicio_minutos = a_minutos(hora_inicio)
            restriccion_minutos = a_minutos("15:30")
            if inicio_minutos < restriccion_minutos:
                return False
    return True

def horario_valido(dia, hora_inicio, duracion, profesor=None, creditos=None, config_local=None):
    """Verifica si un horario es válido según las restricciones fuertes"""
    if config_local is None:
        return False
    ini_min = a_minutos(hora_inicio)
    fin_min = ini_min + int(duracion * 60)
    
    if fin_min > a_minutos(config_local.restricciones_globales["hora_fin_max"]):
        return False
    
    if ini_min < a_minutos(config_local.restricciones_globales["hora_inicio_min"]):
        return False
    
    if creditos and not es_bloque_tres_horas_valido(dia, hora_inicio, duracion, creditos):
        return False
    
    restricciones_horario = config_local.restricciones_globales["horarios_prohibidos"]
    if dia in restricciones_horario:
        for r_ini, r_fin in restricciones_horario[dia]:
            r_ini_min = a_minutos(r_ini)
            r_fin_min = a_minutos(r_fin)
            if not (fin_min <= r_ini_min or ini_min >= r_fin_min):
                return False
    
    if profesor and profesor in config_local.profesores_config:
        prof_config = config_local.profesores_config[profesor]
        if dia in prof_config.get("horario_no_disponible", {}):
            for r_ini, r_fin in prof_config["horario_no_disponible"][dia]:
                r_ini_min = a_minutos(r_ini)
                r_fin_min = a_minutos(r_fin)
                if not (fin_min <= r_ini_min or ini_min >= r_fin_min):
                    return False
    
    return True

def cumple_horario_preferido(dia, hora_inicio, duracion, profesor):
    """Verifica si un horario cumple las preferencias del profesor"""
    if profesor not in config.profesores_config:
        return False
    
    prof_config = config.profesores_config[profesor]
    if dia not in prof_config.get("horario_preferido", {}):
        return False
    
    ini_min = a_minutos(hora_inicio)
    fin_min = ini_min + int(duracion * 60)
    
    for pref_ini, pref_fin in prof_config["horario_preferido"][dia]:
        pref_ini_min = a_minutos(pref_ini)
        pref_fin_min = a_minutos(pref_fin)
        if ini_min >= pref_ini_min and fin_min <= pref_fin_min:
            return True
    
    return False

# -------------------------------------------------
# CLASE AsignacionClase y funciones de conflicto
# -------------------------------------------------
class AsignacionClase:
    def __init__(self, curso_info, profesor, bloque, hora_inicio, salon):
        self.curso_nombre = curso_info["nombre"]
        self.profesor = profesor
        self.bloque = bloque
        self.hora_inicio = hora_inicio
        self.estudiantes = curso_info["estudiantes"]
        self.salon = salon
        self.creditos = curso_info["creditos"]
        # horas_contacto: suma de bloque["horas"] como int para tabla_creditos
        self.horas_contacto = int(round(sum(bloque["horas"])))
        self.creditos_extra = calcular_creditos_adicionales(self.horas_contacto, self.estudiantes)
        
    def get_horario_detallado(self):
        """Retorna lista de horarios detallados para cada día del bloque"""
        horarios = []
        for dia, duracion in zip(self.bloque["dias"], self.bloque["horas"]):
            hora_fin_min = a_minutos(self.hora_inicio) + int(duracion * 60)
            hora_fin = f"{hora_fin_min//60:02d}:{hora_fin_min%60:02d}"
            
            es_tres_horas_consecutivas = (self.creditos == 3 and duracion == 3)
            
            horarios.append({
                "Curso": self.curso_nombre,
                "Profesor": self.profesor,
                "Bloque": self.bloque["id"],
                "Dia": dia,
                "Hora Inicio": self.hora_inicio,
                "Hora Fin": hora_fin,
                "Duración": duracion,
                "Créditos": self.creditos,
                "Créditos Extra": self.creditos_extra,
                "Estudiantes": self.estudiantes,
                "Salon": self.salon,
                "3h Consecutivas": "SÍ" if es_tres_horas_consecutivas else "NO",
                "Restricción 15:30": "CUMPLE" if (not es_tres_horas_consecutivas or a_minutos(self.hora_inicio) >= a_minutos("15:30")) else "VIOLA"
            })
        return horarios

def hay_conflictos(nueva_asignacion, asignaciones_existentes):
    """Verifica si hay conflictos de profesor o salón"""
    for asignacion in asignaciones_existentes:
        for dia_nuevo, dur_nuevo in zip(nueva_asignacion.bloque["dias"], nueva_asignacion.bloque["horas"]):
            ini_nuevo = a_minutos(nueva_asignacion.hora_inicio)
            fin_nuevo = ini_nuevo + int(dur_nuevo * 60)
            
            for dia_exist, dur_exist in zip(asignacion.bloque["dias"], asignacion.bloque["horas"]):
                if dia_nuevo == dia_exist:
                    ini_exist = a_minutos(asignacion.hora_inicio)
                    fin_exist = ini_exist + int(dur_exist * 60)
                    
                    if not (fin_nuevo <= ini_exist or ini_nuevo >= fin_exist):
                        if nueva_asignacion.profesor == asignacion.profesor:
                            return True
                        if nueva_asignacion.salon == asignacion.salon:
                            return True
    
    return False

# -------------------------------------------------
# EVALUACIÓN - función adaptada para recibir lista AsignacionClase
# -------------------------------------------------
def evaluar_horario(asignaciones, config_local):
    """Evalúa un horario considerando restricciones fuertes y suaves configurables"""
    if asignaciones is None:
        return -float('inf')
    
    penalizacion = 0
    bonus = 0
    
    # Verificar que cada profesor tenga todos sus cursos asignados
    for profesor, prof_config in config_local.profesores_config.items():
        cursos_asignados = sum(1 for asig in asignaciones if asig.profesor == profesor)
        cursos_requeridos = len(prof_config["cursos"])
        if cursos_asignados != cursos_requeridos:
            penalizacion += abs(cursos_asignados - cursos_requeridos) * 2000
    
    # Verificar límite de créditos por profesor
    creditos_por_prof = {}
    for asig in asignaciones:
        creditos_por_prof.setdefault(asig.profesor, 0)
        creditos_por_prof[asig.profesor] += asig.creditos
    
    for profesor, prof_config in config_local.profesores_config.items():
        creditos_actuales = creditos_por_prof.get(profesor, 0)
        creditos_objetivo = prof_config["creditos_totales"]
        
        if creditos_actuales > config_local.restricciones_globales["creditos_max_profesor"]:
            penalizacion += (creditos_actuales - config_local.restricciones_globales["creditos_max_profesor"]) * 1000
        
        if creditos_actuales < config_local.restricciones_globales["creditos_min_profesor"]:
            penalizacion += (config_local.restricciones_globales["creditos_min_profesor"] - creditos_actuales) * 1000
        
        if creditos_actuales != creditos_objetivo:
            penalizacion += abs(creditos_actuales - creditos_objetivo) * 200
    
    # Verificar conflictos de horario
    for i, asig1 in enumerate(asignaciones):
        for j, asig2 in enumerate(asignaciones):
            if i >= j:
                continue
            # uso de hay_conflictos usando listas de uno
            if hay_conflictos(asig1, [asig2]):
                penalizacion += 5000
    
    # Verificar cumplimiento de restricción de 3 horas
    for asig in asignaciones:
        for dia, duracion in zip(asig.bloque["dias"], asig.bloque["horas"]):
            if not es_bloque_tres_horas_valido(dia, asig.hora_inicio, duracion, asig.creditos):
                penalizacion += 10000
    
    # Restricciones suaves
    pesos = config_local.pesos_restricciones
    
    for asig in asignaciones:
        for dia, duracion in zip(asig.bloque["dias"], asig.bloque["horas"]):
            if cumple_horario_preferido(dia, asig.hora_inicio, duracion, asig.profesor):
                bonus += pesos["horario_preferido"]
        
        if asig.estudiantes > config_local.restricciones_globales["estudiantes_max_salon"]:
            penalizacion += pesos["estudiantes_por_salon"] * (asig.estudiantes - config_local.restricciones_globales["estudiantes_max_salon"])
    
    return bonus - penalizacion


# -------------------------------------------------
# REPRESENTACIÓN DEL GENOMA Y CONVERSIONES
# -------------------------------------------------
# Vamos a construir una lista global de "cursos" en orden fijo:
# cursos_lista = [(profesor, curso_info), ...] y cada gen es (bloque_id, hora_inicio_idx, salon_idx)

def construir_lista_cursos(config_local):
    """Devuelve lista de (profesor, curso_info) en orden fijo"""
    lista = []
    for profesor, info in config_local.profesores_config.items():
        for curso in info["cursos"]:
            lista.append((profesor, curso))
    return lista

def genoma_a_asignaciones(genoma, cursos_lista, bloques, config_local):
    """
    Convierte un genoma en lista de AsignacionClase.
    genoma: list of (bloque_id, hora_idx, salon_idx)
    """
    asignaciones = []
    for gene, (profesor, curso_info) in zip(genoma, cursos_lista):
        bloque_id, hora_idx, salon_idx = gene
        # buscar bloque por id
        bloque = next((b for b in bloques if b["id"] == bloque_id), None)
        hora_inicio = horas_inicio[hora_idx]
        salon = config_local.salones[salon_idx]
        asignacion = AsignacionClase(curso_info, profesor, bloque, hora_inicio, salon)
        asignaciones.append(asignacion)
    return asignaciones

def generar_gen_aleatorio_para_curso(curso_info, bloques, config_local):
    """Crea un gen aleatorio compatible (intento de buena elección): elegir bloques con creditos iguales/parecidos"""
    # Preferir bloques con mismos créditos
    bloques_compatibles = [b for b in bloques if b["creditos"] == curso_info["creditos"]]
    if not bloques_compatibles:
        # fallback: los 6 bloques más cercanos en créditos
        bloques_compatibles = sorted(bloques, key=lambda x: abs(x["creditos"] - curso_info["creditos"]))[:6]
    bloque = random.choice(bloques_compatibles)
    # elegir hora aleatoria entre horas_inicio que cumplan por cada dia la restricción de hora inicio/fin
    # Para simplificar elegimos cualquier hora y dejamos que la evaluación penalice violaciones.
    hora_idx = random.randrange(len(horas_inicio))
    salon_idx = random.randrange(len(config_local.salones))
    return (bloque["id"], hora_idx, salon_idx)

# -------------------------------------------------
# ALGORITMO GENÉTICO
# -------------------------------------------------
def inicializar_poblacion(tamano, cursos_lista, bloques, config_local):
    poblacion = []
    for _ in range(tamano):
        genoma = [generar_gen_aleatorio_para_curso(curso_info, bloques, config_local) for (_, curso_info) in cursos_lista]
        poblacion.append(genoma)
    return poblacion

def fitness_de_genoma(genoma, cursos_lista, bloques, config_local):
    # Convierte genoma a asignaciones y evalúa
    asignaciones = genoma_a_asignaciones(genoma, cursos_lista, bloques, config_local)
    score = evaluar_horario(asignaciones, config_local)
    # Además penalizamos fuertemente horarios que no cumplan horarios válidos por bloque/día
    penal_extra = 0
    for asig in asignaciones:
        for dia, dur in zip(asig.bloque["dias"], asig.bloque["horas"]):
            if not horario_valido(dia, asig.hora_inicio, dur, asig.profesor, asig.creditos, config_local):
                penal_extra += 5000
    return score - penal_extra

def seleccion_torneo(poblacion, scores, k=3):
    # torneo simple: escoger k aleatorios, devolver el mejor
    seleccionados = random.sample(list(range(len(poblacion))), k)
    mejor = max(seleccionados, key=lambda i: scores[i])
    return copy.deepcopy(poblacion[mejor])

def cruce_uniforme(padre1, padre2, prob_swap=0.5):
    hijo = []
    for g1, g2 in zip(padre1, padre2):
        if random.random() < prob_swap:
            hijo.append(copy.deepcopy(g2))
        else:
            hijo.append(copy.deepcopy(g1))
    return hijo

def mutacion(genoma, bloques, config_local, prob_mut=0.05):
    for i in range(len(genoma)):
        if random.random() < prob_mut:
            # mutar bloque/hora/salon parcialmente
            bloque_id, hora_idx, salon_idx = genoma[i]
            # elegir que parte mutar
            r = random.random()
            if r < 0.4:
                # cambiar bloque por otro compatible
                curso_info = None  # tenemos que recuperar curso_info? No aquí; llamador puede mutar libremente
                bloque_id = random.choice(bloques)["id"]
            elif r < 0.8:
                hora_idx = random.randrange(len(horas_inicio))
            else:
                salon_idx = random.randrange(len(config_local.salones))
            genoma[i] = (bloque_id, hora_idx, salon_idx)
    return genoma

def reconstruir_mejor_asignaciones_desde_poblacion(poblacion, scores, cursos_lista, bloques, config_local):
    idx = int(np.argmax(scores))
    return genoma_a_asignaciones(poblacion[idx], cursos_lista, bloques, config_local), scores[idx]


def ga_buscar_mejor_horario(config_local, bloques, poblacion_tamano=80, generaciones=200, prob_mut=0.08, elitismo=0.05, torneo_k=3, progreso_callback=None):
    """
    Algoritmo genético principal.
    progreso_callback: función opcional que recibe (generacion, mejor_score, promedio_score) para actualizar UI.
    """
    cursos_lista = construir_lista_cursos(config_local)
    if not cursos_lista:
        return None, -float('inf')
    
    poblacion = inicializar_poblacion(poblacion_tamano, cursos_lista, bloques, config_local)
    scores = [fitness_de_genoma(ind, cursos_lista, bloques, config_local) for ind in poblacion]
    mejor_global = None
    mejor_score = -float('inf')
    n_elite = max(1, int(elitismo * poblacion_tamano))
    
    for gen in range(generaciones):
        nueva_poblacion = []
        # Elitismo: conservar los mejores
        idx_orden = sorted(range(len(poblacion)), key=lambda i: scores[i], reverse=True)
        for i in idx_orden[:n_elite]:
            nueva_poblacion.append(copy.deepcopy(poblacion[i]))
        
        # Rellenar el resto con cruces
        while len(nueva_poblacion) < poblacion_tamano:
            padre1 = seleccion_torneo(poblacion, scores, k=torneo_k)
            padre2 = seleccion_torneo(poblacion, scores, k=torneo_k)
            hijo = cruce_uniforme(padre1, padre2, prob_swap=0.5)
            hijo = mutacion(hijo, bloques, config_local, prob_mut=prob_mut)
            nueva_poblacion.append(hijo)
        
        poblacion = nueva_poblacion
        scores = [fitness_de_genoma(ind, cursos_lista, bloques, config_local) for ind in poblacion]
        
        gen_mejor_score = max(scores)
        gen_promedio = sum(scores) / len(scores)
        if gen_mejor_score > mejor_score:
            mejor_score = gen_mejor_score
            mejor_global = copy.deepcopy(poblacion[int(np.argmax(scores))])
        
        if progreso_callback:
            progreso_callback(gen+1, mejor_score, gen_promedio)
    
    # reconstruir asignaciones
    mejor_asignaciones = genoma_a_asignaciones(mejor_global, cursos_lista, bloques, config_local)
    return mejor_asignaciones, mejor_score

# -------------------------------------------------
# EXPORTACIÓN A DATAFRAME (igual que tu original)
# -------------------------------------------------
def exportar_horario(asignaciones):
    """Convierte las asignaciones a un DataFrame para visualización"""
    registros = []
    for asig in asignaciones:
        registros.extend(asig.get_horario_detallado())
    df = pd.DataFrame(registros)
    return df

# -------------------------------------------------
# INTERFAZ STREAMLIT - DISEÑO MEJORADO
# -------------------------------------------------

# CSS para estilo más elegante
PAGE_CSS = """
<style>
/* Fondo suave y contenedores */
[data-testid="stAppViewContainer"] {
  background: linear-gradient(180deg, #f7f9fb 0%, #ffffff 100%);
}
header {display:none;}
h1, h2, h3 { font-family: 'Segoe UI', Roboto, Arial; }
.card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 4px 18px rgba(20,30,60,0.08);
  margin-bottom: 12px;
}
.topline {
  display:flex;
  gap:12px;
  align-items:center;
  padding:12px;
}
.logo {
  width:64px;
  height:64px;
  border-radius:12px;
  background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%);
  display:flex;
  align-items:center;
  justify-content:center;
  color:white;
  font-weight:700;
  font-size:20px;
}
.small-muted { color:#6b7280; font-size:13px; }
.metric-card { padding:12px; border-radius:10px; background:linear-gradient(90deg,#ffffff,#fbfdff); }
.footer-small { color:#9ca3af; font-size:12px; margin-top:10px; }
</style>
"""

def main():
    st.set_page_config(
        page_title="Generador de Horarios (GA) — Elegante",
        page_icon="📅",
        layout="wide",
    )
    st.markdown(PAGE_CSS, unsafe_allow_html=True)
    
    # HEADER
    col1, col2 = st.columns([0.12, 0.88])
    with col1:
        st.markdown('<div class="logo">GA</div>', unsafe_allow_html=True)
    with col2:
        st.markdown("<h1>Generador de Horarios Académicos</h1>", unsafe_allow_html=True)
        st.markdown("<div class='small-muted'>Optimización por Algoritmos Genéticos · Interfaz limpia y profesional</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # SIDEBAR: carga y parámetros
    st.sidebar.header("⚙️ Configuración & Parámetros")
    uploaded_file = st.sidebar.file_uploader(
        "📁 Cargar archivo Excel con datos de profesores y cursos",
        type=['xlsx', 'xls'],
        help="Columnas: Profesor, Curso/Materia, Créditos, Estudiantes (flexible)"
    )
    
    # Parámetros GA
    st.sidebar.subheader("🧬 Parámetros del Algoritmo Genético")
    pop_size = st.sidebar.slider("Población", 20, 300, 80, 10)
    generaciones = st.sidebar.slider("Generaciones", 10, 800, 200, 10)
    prob_mut = st.sidebar.slider("Probabilidad de mutación", 0.0, 0.5, 0.08, 0.01)
    elitismo = st.sidebar.slider("Elitismo (fracción)", 0.0, 0.3, 0.06, 0.01)
    torneo_k = st.sidebar.slider("Tamaño torneo", 2, 8, 3, 1)
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📥 Exportar")
    st.sidebar.write("El horario final se puede descargar como CSV tras la generación.")
    
    # Cargar archivo y crear config
    global config, bloques
    if uploaded_file is not None:
        with open("temp_excel.xlsx", "wb") as f:
            f.write(uploaded_file.getbuffer())
        config = ConfiguracionSistema("temp_excel.xlsx")
        bloques = generar_bloques()
    else:
        config = None
        bloques = generar_bloques()
    
    # MAIN: si no hay config, mostrar ejemplo y ayuda
    if config is None or not config.profesores_config:
        with st.container():
            st.info("📁 Por favor, carga un archivo Excel para comenzar. Aquí tienes un ejemplo del formato esperado.")
            with st.expander("📋 Formato esperado del archivo Excel"):
                st.write("""
                El archivo Excel debe contener al menos las siguientes columnas (nombres flexibles):
                
                | Profesor | Curso/Materia | Créditos | Estudiantes |
                |----------|---------------|----------|-------------|
                | Juan Pérez | Matemáticas I | 4 | 35 |
                | Juan Pérez | Álgebra | 3 | 28 |
                | María García | Física I | 4 | 30 |
                """)
            st.write("Consejos rápidos:")
            st.markdown("- Asegúrate que los nombres de profesores estén consistentes (mismo exacto).")
            st.markdown("- Si no incluyes créditos o estudiantes, se usarán valores por defecto (3 y 30).")
        return
    
    # Si llegó aquí: config cargada
    # Tarjetas métricas superiores
    total_cursos = sum(len(p['cursos']) for p in config.profesores_config.values())
    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(f"<div class='card metric-card'><h3>👨‍🏫 Profesores</h3><h2>{len(config.profesores_config)}</h2></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='card metric-card'><h3>📚 Cursos</h3><h2>{total_cursos}</h2></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='card metric-card'><h3>🏫 Salones</h3><h2>{len(config.salones)}</h2></div>", unsafe_allow_html=True)
    col4.markdown(f"<div class='card metric-card'><h3>🕒 Ventana Horaria</h3><h4>{config.restricciones_globales['hora_inicio_min']} - {config.restricciones_globales['hora_fin_max']}</h4></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Mostrar datos cargados en una tabla compacta
    with st.expander("📋 Ver datos cargados (profesores y cursos)"):
        for profesor, data in config.profesores_config.items():
            st.write(f"**{profesor}** — {len(data['cursos'])} cursos — {data['creditos_totales']} créditos")
    
    # Panel de configuración de preferencias por profesor
    st.subheader("👤 Preferencias de Profesores (opcional)")
    profesor_seleccionado = st.selectbox("Seleccionar profesor para agregar preferencia", ["Ninguno"] + list(config.profesores_config.keys()))
    if profesor_seleccionado != "Ninguno":
        with st.expander(f"Configurar preferencia para {profesor_seleccionado}"):
            dias = ["Lu", "Ma", "Mi", "Ju", "Vi"]
            for dia in dias:
                colA, colB = st.columns(2)
                with colA:
                    inicio = st.time_input(f"{dia} inicio", key=f"pref_{profesor_seleccionado}_{dia}_inicio", value=datetime.strptime("07:30","%H:%M").time())
                with colB:
                    fin = st.time_input(f"{dia} fin", key=f"pref_{profesor_seleccionado}_{dia}_fin", value=datetime.strptime("19:30","%H:%M").time())
                
                if inicio != datetime.strptime("07:30","%H:%M").time() or fin != datetime.strptime("19:30","%H:%M").time():
                    config.profesores_config[profesor_seleccionado].setdefault("horario_preferido", {})
                    config.profesores_config[profesor_seleccionado]["horario_preferido"][dia] = [(inicio.strftime("%H:%M"), fin.strftime("%H:%M"))]
    
    st.markdown("---")
    
    # Botón para ejecutar el GA
    run_col1, run_col2 = st.columns([0.2,0.8])
    with run_col1:
        if st.button("🚀 Ejecutar Algoritmo Genético", type="primary"):
            # Preparar UI para progreso
            progress_bar = st.progress(0)
            status = st.empty()
            status.info("Inicializando algoritmo genético...")
            
            # callback para progreso
            def progreso_cb(generacion, mejor_score, promedio):
                frac = generacion / max(1, generaciones)
                progress_bar.progress(min(1.0, frac))
                status.markdown(f"Generación **{generacion} / {generaciones}** — Mejor score: **{mejor_score:.1f}** — Promedio: {promedio:.1f}")
            
            # Ejecutar GA
            with st.spinner("Ejecutando GA, esto puede tardar unos instantes..."):
                mejor_asig, mejor_score = ga_buscar_mejor_horario(
                    config_local=config,
                    bloques=bloques,
                    poblacion_tamano=pop_size,
                    generaciones=generaciones,
                    prob_mut=prob_mut,
                    elitismo=elitismo,
                    torneo_k=torneo_k,
                    progreso_callback=progreso_cb
                )
            
            if mejor_asig is None:
                st.error("❌ No se pudo generar un horario válido. Revisa restricciones y archivos.")
            else:
                st.success(f"✅ Horario generado! Mejor puntuación: {mejor_score:.1f}")
                df_horario = exportar_horario(mejor_asig)
                
                # Mostrar pestañas con la info
                tab1, tab2, tab3, tab4 = st.tabs(["📊 Horario Completo", "👨‍🏫 Por Profesor", "🏫 Por Salón", "📈 Estadísticas"])
                
                with tab1:
                    st.subheader("📊 Horario Completo")
                    st.dataframe(df_horario, use_container_width=True)
                    csv = df_horario.to_csv(index=False)
                    st.download_button("💾 Descargar horario (CSV)", data=csv, file_name="horario_ga.csv", mime="text/csv")
                
                with tab2:
                    st.subheader("👨‍🏫 Horario por Profesor")
                    for profesor in config.profesores_config.keys():
                        with st.expander(f"{profesor}"):
                            df_prof = df_horario[df_horario['Profesor'] == profesor]
                            if not df_prof.empty:
                                st.dataframe(df_prof, use_container_width=True)
                            else:
                                st.write("Sin clases asignadas.")
                
                with tab3:
                    st.subheader("🏫 Horario por Salón")
                    for salon in config.salones:
                        with st.expander(f"{salon}"):
                            df_salon = df_horario[df_horario['Salon'] == salon]
                            if not df_salon.empty:
                                st.dataframe(df_salon, use_container_width=True)
                            else:
                                st.write("Sin clases en este salón.")
                
                with tab4:
                    st.subheader("📈 Estadísticas del Horario")
                    colA, colB = st.columns(2)
                    with colA:
                        st.write("**Créditos por profesor**")
                        creditos_prof = df_horario.groupby('Profesor')['Créditos'].sum()
                        st.bar_chart(creditos_prof)
                    with colB:
                        st.write("**Uso de salones**")
                        uso_salones = df_horario.groupby('Salon').size()
                        st.bar_chart(uso_salones)
                    
                    clases_3h = df_horario[df_horario['3h Consecutivas'] == 'SÍ']
                    if len(clases_3h) > 0:
                        cumple = len(clases_3h[clases_3h['Restricción 15:30'] == 'CUMPLE'])
                        viola = len(clases_3h[clases_3h['Restricción 15:30'] == 'VIOLA'])
                        st.write(f"Clases 3h: {len(clases_3h)}  — Cumplen: {cumple} — Violan: {viola}")
                        if viola > 0:
                            st.warning("⚠️ Algunas clases de 3h violan la restricción (antes de 15:30). Revisa horarios preferidos o aumenta penalizaciones.")
    
    # Pie de página
    st.markdown("<div class='footer-small'>Generador de Horarios • Algoritmo Genético • Diseñado para ser fácil de usar y extensible</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
