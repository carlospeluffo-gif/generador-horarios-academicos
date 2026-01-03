import streamlit as st
import pandas as pd
import random
import json
import numpy as np
from datetime import datetime, timedelta
import io
import time
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import os
from pathlib import Path
import re

# ========================================================
# CONFIGURACIÓN DE ZONAS (CENTRAL vs PERIFÉRICA)
# ========================================================

class ZonaConfig:
    """Configuración de zonas Central y Periférica"""
    
    CENTRAL = {
        "nombre": "Zona Central",
        "horarios_inicio": ["07:30", "08:30", "09:30", "10:30", "11:30", "12:30", "13:30", "14:30", "15:30", "16:30", "17:30", "18:30"],
        "restricciones": {
            "Ma": [("10:30", "12:30")],
            "Ju": [("10:30", "12:30")]
        },
        "descripcion": "Horarios cada 60 min desde 7:30. Restricción: No clases Ma-Ju 10:30-12:30"
    }
    
    PERIFERICA = {
        "nombre": "Zona Periférica",
        "horarios_inicio": ["07:00", "08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"],
        "restricciones": {
            "Lu": [("10:00", "12:00")],
            "Ma": [("10:00", "12:00")],
            "Mi": [("10:00", "12:00")],
            "Ju": [("10:00", "12:00")],
            "Vi": [("10:00", "12:00")]
        },
        "descripcion": "Horarios cada 60 min desde 7:00. Restricción: No clases 10:00-12:00"
    }

# ========================================================
# PROCESADOR DE EXCEL DEL FORMULARIO DE GOOGLE
# ========================================================

class ProcesadorExcelFormulario:
    """Procesa el Excel generado por el formulario de Google Forms"""
    
    def __init__(self, archivo_excel):
        self.archivo_excel = archivo_excel
        self.df_original = None
        self.profesores_data = {}
        
    def cargar_excel(self):
        """Carga el archivo Excel"""
        try:
            if hasattr(self.archivo_excel, 'read'):
                self.df_original = pd.read_excel(self.archivo_excel, sheet_name=0)
            else:
                self.df_original = pd.read_excel(self.archivo_excel, sheet_name=0)
            
            st.success(f"Excel cargado: {len(self.df_original)} filas")
            return True
        except Exception as e:
            st.error(f"Error al cargar Excel: {e}")
            return False
    
    def extraer_profesor_y_porcentaje(self, profesor_str):
        """Extrae nombre del profesor y porcentaje de carga"""
        if pd.isna(profesor_str) or str(profesor_str).strip() == '':
            return None, 100
        
        # Formato: "Edwin Florez Gomez (100%)"
        match = re.search(r'(.+?)\s*\((\d+)%\)', str(profesor_str))
        if match:
            nombre = match.group(1).strip()
            porcentaje = int(match.group(2))
            return nombre, porcentaje
        else:
            return str(profesor_str).strip(), 100
    
    def parsear_horario_meetings(self, meetings_str):
        """Parsea el campo MEETINGS para extraer días, horas y salón"""
        if pd.isna(meetings_str) or str(meetings_str).strip() == '':
            return None
        
        # Formato: "2:30 pm - 4:20 pm MJ M 316"
        # Formato: "8:30 am - 9:20 am LWV M 316"
        try:
            meetings_str = str(meetings_str).strip()
            
            # Extraer horas
            time_pattern = r'(\d{1,2}:\d{2}\s*[ap]m)\s*-\s*(\d{1,2}:\d{2}\s*[ap]m)'
            time_match = re.search(time_pattern, meetings_str, re.IGNORECASE)
            
            if not time_match:
                return None
            
            hora_inicio = time_match.group(1).strip()
            hora_fin = time_match.group(2).strip()
            
            # Extraer días (después de las horas)
            resto = meetings_str[time_match.end():].strip()
            
            # Días pueden ser: LWV, MJ, LMWJ, etc.
            dias_pattern = r'([LMWJV]+)'
            dias_match = re.search(dias_pattern, resto)
            
            if not dias_match:
                return None
            
            dias_str = dias_match.group(1)
            
            # Convertir días a formato estándar
            dias_map = {'L': 'Lu', 'M': 'Ma', 'W': 'Mi', 'J': 'Ju', 'V': 'Vi'}
            dias = [dias_map.get(d, d) for d in dias_str if d in dias_map]
            
            # Extraer salón (después de los días)
            resto_salon = resto[dias_match.end():].strip()
            salon_pattern = r'(M\s*\d+)'
            salon_match = re.search(salon_pattern, resto_salon)
            
            salon = salon_match.group(1).strip() if salon_match else "M 316"
            
            return {
                'hora_inicio': hora_inicio,
                'hora_fin': hora_fin,
                'dias': dias,
                'salon': salon
            }
        except Exception as e:
            st.warning(f"Error parseando horario '{meetings_str}': {e}")
            return None
    
    def procesar_datos(self):
        """Procesa los datos del Excel y extrae información de profesores y cursos"""
        if self.df_original is None or self.df_original.empty:
            st.error("No hay datos para procesar")
            return False
        
        # Mapeo de columnas esperadas
        columnas_requeridas = {
            'SERIES': 'codigo_curso',
            'NAME SPA': 'nombre_curso',
            'CREDITS': 'creditos',
            'PROFESSORS': 'profesores',
            'PROFESSORS EMAIL': 'email',
            'MEETINGS': 'horario',
            'CAPACITY': 'capacidad'
        }
        
        # Verificar columnas
        columnas_faltantes = []
        for col_excel in columnas_requeridas.keys():
            if col_excel not in self.df_original.columns:
                columnas_faltantes.append(col_excel)
        
        if columnas_faltantes:
            st.warning(f"Columnas faltantes: {columnas_faltantes}")
            st.info("Usando columnas disponibles...")
        
        # Procesar cada fila
        for idx, fila in self.df_original.iterrows():
            try:
                # Extraer datos básicos
                codigo_curso = fila.get('SERIES', f'CURSO_{idx}')
                nombre_curso = fila.get('NAME SPA', fila.get('NAME ENG', 'Curso sin nombre'))
                creditos = fila.get('CREDITS', 3)
                capacidad = fila.get('CAPACITY', 30)
                profesores_str = fila.get('PROFESSORS', '')
                email = fila.get('PROFESSORS EMAIL', '')
                meetings = fila.get('MEETINGS', '')
                
                # Extraer profesor y porcentaje
                profesor_nombre, porcentaje = self.extraer_profesor_y_porcentaje(profesores_str)
                
                if not profesor_nombre:
                    continue
                
                # Parsear horario si existe
                horario_info = self.parsear_horario_meetings(meetings)
                
                # Inicializar profesor si no existe
                if profesor_nombre not in self.profesores_data:
                    self.profesores_data[profesor_nombre] = {
                        'email': email,
                        'cursos': [],
                        'creditos_totales': 0,
                        'horario_preferido': {},
                        'horario_no_disponible': {},
                        'dias_preferidos': [],
                        'turno_preferido': 'Mañana'
                    }
                
                # Agregar curso al profesor
                curso_info = {
                    'codigo': str(codigo_curso),
                    'nombre': str(nombre_curso),
                    'creditos': int(creditos) if not pd.isna(creditos) else 3,
                    'estudiantes': int(capacidad) if not pd.isna(capacidad) else 30,
                    'porcentaje_carga': porcentaje,
                    'horario_actual': horario_info,
                    'seccion': fila.get('SECTION', '001')
                }
                
                self.profesores_data[profesor_nombre]['cursos'].append(curso_info)
                self.profesores_data[profesor_nombre]['creditos_totales'] += curso_info['creditos']
                
            except Exception as e:
                st.warning(f"Error procesando fila {idx}: {e}")
                continue
        
        st.success(f"Procesados {len(self.profesores_data)} profesores con sus cursos")
        return True
    
    def obtener_profesores_config(self):
        """Retorna la configuración de profesores en el formato esperado por el sistema"""
        config_profesores = {}
        
        for profesor, data in self.profesores_data.items():
            config_profesores[profesor] = {
                'cursos': data['cursos'],
                'creditos_totales': data['creditos_totales'],
                'horario_preferido': data['horario_preferido'],
                'horario_no_disponible': data['horario_no_disponible'],
                'email': data['email'],
                'dias_preferidos': data['dias_preferidos'],
                'turno_preferido': data['turno_preferido']
            }
        
        return config_profesores

# ========================================================
# EDITOR DE PREFERENCIAS DE PROFESORES
# ========================================================

def mostrar_editor_preferencias_profesor(profesor_nombre, profesor_config, zona_seleccionada):
    """Interfaz para editar las preferencias de horario de un profesor"""
    
    st.markdown(f"### Preferencias de {profesor_nombre}")
    
    # Información del profesor
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Cursos asignados", len(profesor_config['cursos']))
    with col2:
        st.metric("Créditos totales", profesor_config['creditos_totales'])
    with col3:
        email = profesor_config.get('email', 'No disponible')
        st.info(f"📧 {email}")
    
    # Lista de cursos
    with st.expander("Ver cursos asignados", expanded=False):
        for curso in profesor_config['cursos']:
            st.write(f"• {curso['codigo']} - {curso['nombre']} ({curso['creditos']} créditos)")
    
    st.markdown("---")
    
    # Preferencias de días
    st.markdown("#### Días Preferidos")
    
    dias_opciones = {
        "Lu-Mi-Vi": ["Lu", "Mi", "Vi"],
        "Ma-Ju": ["Ma", "Ju"],
        "Lu-Ma-Mi-Ju": ["Lu", "Ma", "Mi", "Ju"],
        "Todos los días": ["Lu", "Ma", "Mi", "Ju", "Vi"],
        "Personalizado": []
    }
    
    dias_pref_key = f"dias_pref_{profesor_nombre}"
    dias_seleccion = st.selectbox(
        "Patrón de días preferidos",
        list(dias_opciones.keys()),
        key=dias_pref_key
    )
    
    if dias_seleccion == "Personalizado":
        dias_custom = st.multiselect(
            "Seleccionar días específicos",
            ["Lu", "Ma", "Mi", "Ju", "Vi"],
            default=profesor_config.get('dias_preferidos', []),
            key=f"dias_custom_{profesor_nombre}"
        )
        dias_preferidos = dias_custom
    else:
        dias_preferidos = dias_opciones[dias_seleccion]
    
    # Actualizar en config
    profesor_config['dias_preferidos'] = dias_preferidos
    
    st.markdown("---")
    
    # Preferencias de turno
    st.markdown("#### Turno Preferido")
    
    turno_pref = st.radio(
        "Preferencia de horario",
        ["Mañana (antes de 12:30)", "Tarde (después de 12:30)", "Sin preferencia"],
        index=0 if profesor_config.get('turno_preferido') == 'Mañana' else 1,
        key=f"turno_{profesor_nombre}"
    )
    
    if turno_pref == "Mañana (antes de 12:30)":
        profesor_config['turno_preferido'] = 'Mañana'
    elif turno_pref == "Tarde (después de 12:30)":
        profesor_config['turno_preferido'] = 'Tarde'
    else:
        profesor_config['turno_preferido'] = 'Sin preferencia'
    
    st.markdown("---")
    
    # Horarios específicos preferidos
    st.markdown("#### Horarios Específicos Preferidos")
    
    zona_config = ZonaConfig.CENTRAL if zona_seleccionada == "Central" else ZonaConfig.PERIFERICA
    horarios_disponibles = zona_config['horarios_inicio']
    
    usar_horarios_especificos = st.checkbox(
        "Configurar horarios específicos preferidos",
        value=bool(profesor_config.get('horario_preferido')),
        key=f"usar_horarios_{profesor_nombre}"
    )
    
    if usar_horarios_especificos:
        st.info("Selecciona los rangos de horas preferidas para cada día")
        
        for dia in dias_preferidos:
            col1, col2 = st.columns(2)
            with col1:
                hora_inicio = st.selectbox(
                    f"{dia} - Hora inicio",
                    horarios_disponibles,
                    key=f"pref_inicio_{profesor_nombre}_{dia}"
                )
            with col2:
                hora_fin = st.selectbox(
                    f"{dia} - Hora fin",
                    horarios_disponibles,
                    index=min(len(horarios_disponibles)-1, horarios_disponibles.index(hora_inicio) + 4),
                    key=f"pref_fin_{profesor_nombre}_{dia}"
                )
            
            if dia not in profesor_config['horario_preferido']:
                profesor_config['horario_preferido'][dia] = []
            
            profesor_config['horario_preferido'][dia] = [(hora_inicio, hora_fin)]
    
    st.markdown("---")
    
    # Horarios NO disponibles
    st.markdown("#### Horarios NO Disponibles")
    
    usar_no_disponible = st.checkbox(
        "Marcar horarios NO disponibles",
        value=bool(profesor_config.get('horario_no_disponible')),
        key=f"usar_no_disp_{profesor_nombre}"
    )
    
    if usar_no_disponible:
        st.warning("Marca los horarios en los que el profesor NO puede dar clases")
        
        dias_no_disp = st.multiselect(
            "Días no disponibles",
            ["Lu", "Ma", "Mi", "Ju", "Vi"],
            key=f"dias_no_disp_{profesor_nombre}"
        )
        
        for dia in dias_no_disp:
            col1, col2 = st.columns(2)
            with col1:
                hora_inicio_nd = st.selectbox(
                    f"{dia} - Desde",
                    horarios_disponibles,
                    key=f"no_disp_inicio_{profesor_nombre}_{dia}"
                )
            with col2:
                hora_fin_nd = st.selectbox(
                    f"{dia} - Hasta",
                    horarios_disponibles,
                    index=min(len(horarios_disponibles)-1, horarios_disponibles.index(hora_inicio_nd) + 2),
                    key=f"no_disp_fin_{profesor_nombre}_{dia}"
                )
            
            if dia not in profesor_config['horario_no_disponible']:
                profesor_config['horario_no_disponible'][dia] = []
            
            profesor_config['horario_no_disponible'][dia] = [(hora_inicio_nd, hora_fin_nd)]
    
    return profesor_config

# ========================================================
# SISTEMA DE GENERACIÓN DE HORARIOS (ADAPTADO)
# ========================================================

MATEMATICAS_SALONES_FIJOS = [
    "M 102", "M 104", "M 105", "M 110", "M 112", "M 203", "M 205", "M 210", 
    "M 213", "M 214", "M 215", "M 220", "M 222", "M 236", "M 238", "M 302", 
    "M 303", "M 304", "M 305", "M 306", "M 311", "M 315", "M 316", "M 317", 
    "M 338", "M 340", "M 341", "M 402", "M 403", "M 404"
]

def generar_bloques_horarios():
    """Genera bloques de horarios según créditos"""
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
        (["Ma","Ju","Vi"], [1.5,1.5,2]),
        (["Lu","Ma","Mi","Ju","Vi"], [1,1,1,1,1]),
    ]
    for dias, horas in combinaciones_5creditos:
        bloques.append({"id": id_counter, "dias": dias, "horas": horas, "creditos": 5})
        id_counter += 1

    # Bloques de 3 créditos (un solo día con 3 horas)
    for dia in ["Lu","Ma","Mi","Ju","Vi"]:
        bloques.append({"id": id_counter, "dias": [dia], "horas": [3], "creditos": 3})
        id_counter += 1

    return bloques

def a_minutos(hhmm):
    """Convierte hora en formato HH:MM a minutos"""
    try:
        h, m = map(int, hhmm.split(":"))
        return h * 60 + m
    except:
        return 0

def horario_valido_zona(dia, hora_inicio, duracion, zona_config, profesor_config=None):
    """Verifica si un horario es válido según la zona y preferencias del profesor"""
    ini_min = a_minutos(hora_inicio)
    fin_min = ini_min + int(duracion * 60)
    
    # Verificar restricciones de la zona
    restricciones = zona_config['restricciones']
    if dia in restricciones:
        for r_ini, r_fin in restricciones[dia]:
            r_ini_min = a_minutos(r_ini)
            r_fin_min = a_minutos(r_fin)
            if not (fin_min <= r_ini_min or ini_min >= r_fin_min):
                return False
    
    # Verificar horarios NO disponibles del profesor
    if profesor_config and 'horario_no_disponible' in profesor_config:
        if dia in profesor_config['horario_no_disponible']:
            for nd_ini, nd_fin in profesor_config['horario_no_disponible'][dia]:
                nd_ini_min = a_minutos(nd_ini)
                nd_fin_min = a_minutos(nd_fin)
                if not (fin_min <= nd_ini_min or ini_min >= nd_fin_min):
                    return False
    
    return True

def cumple_preferencias_profesor(dia, hora_inicio, duracion, profesor_config):
    """Verifica si el horario cumple con las preferencias del profesor"""
    score = 0
    
    # Verificar días preferidos
    if 'dias_preferidos' in profesor_config and profesor_config['dias_preferidos']:
        if dia in profesor_config['dias_preferidos']:
            score += 30
        else:
            score -= 20
    
    # Verificar turno preferido
    if 'turno_preferido' in profesor_config:
        hora_min = a_minutos(hora_inicio)
        mediodia = a_minutos("12:30")
        
        if profesor_config['turno_preferido'] == 'Mañana' and hora_min < mediodia:
            score += 20
        elif profesor_config['turno_preferido'] == 'Tarde' and hora_min >= mediodia:
            score += 20
    
    # Verificar horarios específicos preferidos
    if 'horario_preferido' in profesor_config and dia in profesor_config['horario_preferido']:
        ini_min = a_minutos(hora_inicio)
        fin_min = ini_min + int(duracion * 60)
        
        for pref_ini, pref_fin in profesor_config['horario_preferido'][dia]:
            pref_ini_min = a_minutos(pref_ini)
            pref_fin_min = a_minutos(pref_fin)
            if ini_min >= pref_ini_min and fin_min <= pref_fin_min:
                score += 50
    
    return score

class AsignacionClase:
    def __init__(self, curso_info, profesor, bloque, hora_inicio, salon):
        self.curso_codigo = curso_info["codigo"]
        self.curso_nombre = curso_info["nombre"]
        self.profesor = profesor
        self.bloque = bloque
        self.hora_inicio = hora_inicio
        self.estudiantes = curso_info["estudiantes"]
        self.salon = salon
        self.creditos = curso_info["creditos"]
        self.seccion = curso_info.get("seccion", "001")
        
    def get_horario_detallado(self):
        horarios = []
        for dia, duracion in zip(self.bloque["dias"], self.bloque["horas"]):
            hora_fin_min = a_minutos(self.hora_inicio) + int(duracion * 60)
            hora_fin = f"{hora_fin_min//60:02d}:{hora_fin_min%60:02d}"
            
            horarios.append({
                "Código": self.curso_codigo,
                "Curso": self.curso_nombre,
                "Profesor": self.profesor,
                "Sección": self.seccion,
                "Día": dia,
                "Hora Inicio": self.hora_inicio,
                "Hora Fin": hora_fin,
                "Duración": duracion,
                "Créditos": self.creditos,
                "Estudiantes": self.estudiantes,
                "Salón": self.salon
            })
        return horarios

def hay_conflictos(nueva_asignacion, asignaciones_existentes):
    """Verifica si hay conflictos de horario"""
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

def generar_horario_optimizado(profesores_config, zona_config, salones, intentos=250):
    """Genera un horario optimizado según zona y preferencias"""
    mejor_asignaciones = None
    mejor_score = -float('inf')
    
    bloques = generar_bloques_horarios()
    horas_inicio = zona_config['horarios_inicio']
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for intento in range(intentos):
        progress_bar.progress((intento + 1) / intentos)
        status_text.text(f"Generando horarios... {intento+1}/{intentos}")
        
        asignaciones = []
        score_total = 0
        
        for profesor, prof_config in profesores_config.items():
            for curso_info in prof_config['cursos']:
                # Buscar bloques compatibles
                bloques_compatibles = [b for b in bloques if b["creditos"] == curso_info["creditos"]]
                if not bloques_compatibles:
                    bloques_compatibles = bloques[:5]
                
                mejor_asignacion_curso = None
                mejor_score_curso = -float('inf')
                
                # Probar varias combinaciones
                for _ in range(50):
                    bloque = random.choice(bloques_compatibles)
                    hora_inicio = random.choice(horas_inicio)
                    salon = random.choice(salones)
                    
                    # Verificar validez
                    valido = True
                    score_curso = 0
                    
                    for dia, duracion in zip(bloque["dias"], bloque["horas"]):
                        if not horario_valido_zona(dia, hora_inicio, duracion, zona_config, prof_config):
                            valido = False
                            break
                        score_curso += cumple_preferencias_profesor(dia, hora_inicio, duracion, prof_config)
                    
                    if not valido:
                        continue
                    
                    nueva_asignacion = AsignacionClase(curso_info, profesor, bloque, hora_inicio, salon)
                    
                    if not hay_conflictos(nueva_asignacion, asignaciones):
                        if score_curso > mejor_score_curso:
                            mejor_score_curso = score_curso
                            mejor_asignacion_curso = nueva_asignacion
                
                if mejor_asignacion_curso:
                    asignaciones.append(mejor_asignacion_curso)
                    score_total += mejor_score_curso
        
        # Verificar si todas las clases fueron asignadas
        total_cursos = sum(len(prof['cursos']) for prof in profesores_config.values())
        if len(asignaciones) == total_cursos and score_total > mejor_score:
            mejor_score = score_total
            mejor_asignaciones = asignaciones
    
    status_text.text(f"Generación completada. Mejor puntuación: {mejor_score}")
    return mejor_asignaciones, mejor_score

def exportar_horario(asignaciones):
    """Exporta el horario a DataFrame"""
    registros = []
    for asig in asignaciones:
        registros.extend(asig.get_horario_detallado())
    return pd.DataFrame(registros)

# ========================================================
# VISUALIZACIÓN
# ========================================================

def crear_tabla_horario_visual(df_horario):
    """Crea una tabla visual del horario"""
    if df_horario.empty:
        st.warning("No hay datos para mostrar")
        return
    
    # Crear matriz de horarios
    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
    dias_map = {'Lu': 'Lunes', 'Ma': 'Martes', 'Mi': 'Miércoles', 'Ju': 'Jueves', 'Vi': 'Viernes'}
    
    # Obtener rango de horas
    horas_unicas = sorted(df_horario['Hora Inicio'].unique())
    
    # Crear tabla
    st.markdown("### Vista de Horario Semanal")
    
    for hora in horas_unicas:
        st.markdown(f"**{hora}**")
        cols = st.columns(5)
        
        for idx, dia in enumerate(dias):
            dia_corto = [k for k, v in dias_map.items() if v == dia][0]
            clases_hora_dia = df_horario[
                (df_horario['Hora Inicio'] == hora) & 
                (df_horario['Día'] == dia_corto)
            ]
            
            with cols[idx]:
                if not clases_hora_dia.empty:
                    for _, clase in clases_hora_dia.iterrows():
                        st.info(f"""
                        **{clase['Curso']}**  
                        Prof: {clase['Profesor']}  
                        Salón: {clase['Salón']}  
                        {clase['Hora Inicio']} - {clase['Hora Fin']}
                        """)
                else:
                    st.write("")
        
        st.markdown("---")

# ========================================================
# INTERFAZ PRINCIPAL
# ========================================================

def main():
    st.set_page_config(
        page_title="Sistema de Horarios - Departamento de Matemáticas",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Sistema de Generación de Horarios")
    st.markdown("### Departamento de Matemáticas - RUM")
    
    # Sidebar - Configuración
    st.sidebar.header("Configuración")
    
    # Selector de zona
    st.sidebar.subheader("1. Seleccionar Zona")
    zona_seleccionada = st.sidebar.radio(
        "Zona del campus:",
        ["Central", "Periférica"],
        help="Central: 7:30, 8:30... | Periférica: 7:00, 8:00..."
    )
    
    zona_config = ZonaConfig.CENTRAL if zona_seleccionada == "Central" else ZonaConfig.PERIFERICA
    
    st.sidebar.info(f"**{zona_config['nombre']}**\n\n{zona_config['descripcion']}")
    
    # Cargar archivo Excel
    st.sidebar.subheader("2. Cargar Excel del Formulario")
    uploaded_file = st.sidebar.file_uploader(
        "Subir archivo Excel",
        type=['xlsx', 'xls'],
        help="Excel generado por el formulario de Google Forms"
    )
    
    # Inicializar session state
    if 'procesador' not in st.session_state:
        st.session_state.procesador = None
    if 'profesores_config' not in st.session_state:
        st.session_state.profesores_config = {}
    if 'horario_generado' not in st.session_state:
        st.session_state.horario_generado = None
    
    # Procesar archivo
    if uploaded_file is not None:
        if st.sidebar.button("Procesar Excel", type="primary"):
            with st.spinner("Procesando archivo..."):
                procesador = ProcesadorExcelFormulario(uploaded_file)
                if procesador.cargar_excel():
                    if procesador.procesar_datos():
                        st.session_state.procesador = procesador
                        st.session_state.profesores_config = procesador.obtener_profesores_config()
                        st.success("✅ Archivo procesado correctamente")
                        st.rerun()
    
    # Mostrar información si hay datos cargados
    if st.session_state.profesores_config:
        st.markdown("---")
        
        # Métricas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Profesores", len(st.session_state.profesores_config))
        with col2:
            total_cursos = sum(len(p['cursos']) for p in st.session_state.profesores_config.values())
            st.metric("Cursos totales", total_cursos)
        with col3:
            total_creditos = sum(p['creditos_totales'] for p in st.session_state.profesores_config.values())
            st.metric("Créditos totales", total_creditos)
        
        # Tabs principales
        tab1, tab2, tab3 = st.tabs(["📝 Editar Preferencias", "🔄 Generar Horario", "📊 Ver Horario"])
        
        with tab1:
            st.markdown("## Editor de Preferencias de Profesores")
            st.info("Configura las preferencias de horario para cada profesor antes de generar el horario")
            
            profesor_seleccionado = st.selectbox(
                "Seleccionar profesor:",
                list(st.session_state.profesores_config.keys())
            )
            
            if profesor_seleccionado:
                st.markdown("---")
                profesor_config = st.session_state.profesores_config[profesor_seleccionado]
                
                # Editor de preferencias
                profesor_config_actualizado = mostrar_editor_preferencias_profesor(
                    profesor_seleccionado,
                    profesor_config,
                    zona_seleccionada
                )
                
                # Guardar cambios
                if st.button("💾 Guardar Preferencias", type="primary"):
                    st.session_state.profesores_config[profesor_seleccionado] = profesor_config_actualizado
                    st.success(f"✅ Preferencias guardadas para {profesor_seleccionado}")
        
        with tab2:
            st.markdown("## Generador de Horarios")
            
            st.info(f"Zona seleccionada: **{zona_config['nombre']}**")
            
            col1, col2 = st.columns(2)
            with col1:
                intentos = st.slider("Iteraciones de optimización", 50, 500, 250, 50)
            with col2:
                st.metric("Salones disponibles", len(MATEMATICAS_SALONES_FIJOS))
            
            if st.button("🚀 Generar Horario Optimizado", type="primary"):
                with st.spinner("Generando horario optimizado..."):
                    asignaciones, score = generar_horario_optimizado(
                        st.session_state.profesores_config,
                        zona_config,
                        MATEMATICAS_SALONES_FIJOS,
                        intentos
                    )
                    
                    if asignaciones:
                        st.session_state.horario_generado = exportar_horario(asignaciones)
                        st.session_state.asignaciones = asignaciones
                        st.success(f"✅ Horario generado exitosamente. Puntuación: {score}")
                        st.balloons()
                    else:
                        st.error("❌ No se pudo generar un horario válido. Intenta ajustar las preferencias.")
        
        with tab3:
            st.markdown("## Visualización del Horario")
            
            if st.session_state.horario_generado is not None:
                df_horario = st.session_state.horario_generado
                
                # Opciones de visualización
                vista = st.radio(
                    "Tipo de vista:",
                    ["Tabla Visual", "Tabla Completa", "Por Profesor", "Por Salón"],
                    horizontal=True
                )
                
                if vista == "Tabla Visual":
                    crear_tabla_horario_visual(df_horario)
                
                elif vista == "Tabla Completa":
                    st.dataframe(df_horario, use_container_width=True)
                    
                    # Descargar
                    csv = df_horario.to_csv(index=False)
                    st.download_button(
                        "📥 Descargar CSV",
                        csv,
                        "horario_matematicas.csv",
                        "text/csv"
                    )
                
                elif vista == "Por Profesor":
                    profesor_filtro = st.selectbox(
                        "Seleccionar profesor:",
                        sorted(df_horario['Profesor'].unique())
                    )
                    df_filtrado = df_horario[df_horario['Profesor'] == profesor_filtro]
                    st.dataframe(df_filtrado, use_container_width=True)
                
                elif vista == "Por Salón":
                    salon_filtro = st.selectbox(
                        "Seleccionar salón:",
                        sorted(df_horario['Salón'].unique())
                    )
                    df_filtrado = df_horario[df_horario['Salón'] == salon_filtro]
                    st.dataframe(df_filtrado, use_container_width=True)
                
                # Estadísticas
                st.markdown("---")
                st.markdown("### Estadísticas")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Clases programadas", len(df_horario))
                with col2:
                    st.metric("Profesores activos", df_horario['Profesor'].nunique())
                with col3:
                    st.metric("Salones utilizados", df_horario['Salón'].nunique())
                with col4:
                    st.metric("Estudiantes totales", df_horario['Estudiantes'].sum())
            
            else:
                st.info("👆 Genera un horario en la pestaña 'Generar Horario' para visualizarlo aquí")
    
    else:
        st.info("👈 Sube el archivo Excel del formulario en el sidebar para comenzar")
        
        with st.expander("ℹ️ Información del Sistema"):
            st.markdown("""
            ### Cómo usar este sistema:
            
            1. **Seleccionar Zona**: Elige entre Zona Central o Periférica según la ubicación de tus salones
            2. **Cargar Excel**: Sube el archivo Excel generado por el formulario de Google Forms
            3. **Editar Preferencias**: Configura las preferencias de horario para cada profesor
            4. **Generar Horario**: El sistema creará un horario optimizado respetando todas las restricciones
            5. **Visualizar**: Revisa el horario generado en diferentes vistas
            
            ### Diferencias entre zonas:
            
            **Zona Central:**
            - Horarios: 7:30, 8:30, 9:30, 10:30, 11:30, 12:30...
            - Restricción: No hay clases Martes y Jueves de 10:30 a 12:30
            
            **Zona Periférica:**
            - Horarios: 7:00, 8:00, 9:00, 10:00, 11:00, 12:00...
            - Restricción: No hay clases de 10:00 a 12:00 (todos los días)
            """)

if __name__ == "__main__":
    main()
