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
import csv

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
# PROCESADOR DE EXCEL/CSV DEL FORMULARIO DE GOOGLE (MEJORADO)
# ========================================================

class ProcesadorExcelFormulario:
    """Procesa el Excel/CSV generado por el formulario de Google Forms"""
    
    def __init__(self, archivo):
        self.archivo = archivo
        self.df_original = None
        self.profesores_data = {}
        
    def detectar_y_cargar_archivo(self):
        """Detecta el formato del archivo y lo carga apropiadamente"""
        try:
            # Leer el contenido del archivo
            if hasattr(self.archivo, 'read'):
                contenido = self.archivo.read()
                self.archivo.seek(0)  # Resetear el puntero
            else:
                with open(self.archivo, 'rb') as f:
                    contenido = f.read()
            
            # Detectar si es CSV (contiene muchas comas)
            contenido_str = contenido.decode('utf-8', errors='ignore')[:1000]
            num_comas = contenido_str.count(',')
            num_tabs = contenido_str.count('\t')
            
            st.info(f"Detectando formato... Comas: {num_comas}, Tabs: {num_tabs}")
            
            # Intentar cargar como CSV primero
            if num_comas > num_tabs * 2:
                st.info("📄 Detectado formato CSV (separado por comas)")
                try:
                    # Intentar diferentes encodings
                    for encoding in ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']:
                        try:
                            self.archivo.seek(0)
                            self.df_original = pd.read_csv(self.archivo, encoding=encoding)
                            st.success(f"✅ CSV cargado con encoding: {encoding}")
                            break
                        except:
                            continue
                    
                    if self.df_original is None:
                        # Último intento: leer como texto y parsear manualmente
                        self.archivo.seek(0)
                        contenido_texto = self.archivo.read().decode('utf-8', errors='ignore')
                        lineas = contenido_texto.strip().split('\n')
                        
                        # Parsear CSV manualmente
                        reader = csv.reader(lineas)
                        datos = list(reader)
                        
                        if len(datos) > 1:
                            self.df_original = pd.DataFrame(datos[1:], columns=datos[0])
                            st.success("✅ CSV parseado manualmente")
                        else:
                            raise ValueError("No se pudo parsear el CSV")
                
                except Exception as e:
                    st.error(f"Error al cargar CSV: {e}")
                    return False
            
            else:
                # Intentar cargar como Excel
                st.info("📊 Detectado formato Excel")
                try:
                    self.archivo.seek(0)
                    self.df_original = pd.read_excel(self.archivo, sheet_name=0)
                    st.success("✅ Excel cargado correctamente")
                except Exception as e:
                    st.error(f"Error al cargar Excel: {e}")
                    return False
            
            # Mostrar información del DataFrame cargado
            if self.df_original is not None:
                st.success(f"✅ Archivo cargado: {len(self.df_original)} filas, {len(self.df_original.columns)} columnas")
                
                # Mostrar columnas detectadas
                with st.expander("🔍 Ver columnas detectadas"):
                    st.write("**Columnas encontradas:**")
                    for i, col in enumerate(self.df_original.columns):
                        st.write(f"{i+1}. `{col}`")
                
                # Mostrar primeras filas
                with st.expander("👀 Ver primeras filas del archivo"):
                    st.dataframe(self.df_original.head(3))
                
                return True
            else:
                st.error("No se pudo cargar el archivo")
                return False
                
        except Exception as e:
            st.error(f"Error general al cargar archivo: {e}")
            import traceback
            st.code(traceback.format_exc())
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
        
        try:
            meetings_str = str(meetings_str).strip()
            
            # Extraer horas
            time_pattern = r'(\d{1,2}:\d{2}\s*[ap]m)\s*-\s*(\d{1,2}:\d{2}\s*[ap]m)'
            time_match = re.search(time_pattern, meetings_str, re.IGNORECASE)
            
            if not time_match:
                return None
            
            hora_inicio = time_match.group(1).strip()
            hora_fin = time_match.group(2).strip()
            
            # Extraer días
            resto = meetings_str[time_match.end():].strip()
            dias_pattern = r'([LMWJV]+)'
            dias_match = re.search(dias_pattern, resto)
            
            if not dias_match:
                return None
            
            dias_str = dias_match.group(1)
            dias_map = {'L': 'Lu', 'M': 'Ma', 'W': 'Mi', 'J': 'Ju', 'V': 'Vi'}
            dias = [dias_map.get(d, d) for d in dias_str if d in dias_map]
            
            # Extraer salón
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
            return None
    
    def normalizar_nombre_columna(self, col_name):
        """Normaliza nombres de columnas para búsqueda flexible"""
        if pd.isna(col_name):
            return ""
        return str(col_name).strip().upper().replace(" ", "_")
    
    def buscar_columna(self, posibles_nombres):
        """Busca una columna por varios nombres posibles"""
        columnas_normalizadas = {self.normalizar_nombre_columna(col): col for col in self.df_original.columns}
        
        for nombre in posibles_nombres:
            nombre_norm = self.normalizar_nombre_columna(nombre)
            if nombre_norm in columnas_normalizadas:
                return columnas_normalizadas[nombre_norm]
        
        return None
    
    def procesar_datos(self):
        """Procesa los datos del Excel/CSV y extrae información de profesores y cursos"""
        if self.df_original is None or self.df_original.empty:
            st.error("No hay datos para procesar")
            return False
        
        # Buscar columnas de forma flexible
        col_series = self.buscar_columna(['SERIES', 'CODIGO', 'CODE', 'COURSE_CODE'])
        col_nombre = self.buscar_columna(['NAME SPA', 'NAME_SPA', 'NOMBRE', 'NAME', 'COURSE_NAME'])
        col_creditos = self.buscar_columna(['CREDITS', 'CREDITOS', 'CREDIT'])
        col_profesores = self.buscar_columna(['PROFESSORS', 'PROFESOR', 'TEACHER', 'INSTRUCTOR'])
        col_email = self.buscar_columna(['PROFESSORS EMAIL', 'PROFESSORS_EMAIL', 'EMAIL', 'CORREO'])
        col_meetings = self.buscar_columna(['MEETINGS', 'HORARIO', 'SCHEDULE'])
        col_capacidad = self.buscar_columna(['CAPACITY', 'CAPACIDAD', 'CAP', 'ESTUDIANTES'])
        col_seccion = self.buscar_columna(['SECTION', 'SECCION', 'SEC'])
        
        st.info("🔍 Columnas mapeadas:")
        mapeo = {
            'Código': col_series,
            'Nombre': col_nombre,
            'Créditos': col_creditos,
            'Profesores': col_profesores,
            'Email': col_email,
            'Horario': col_meetings,
            'Capacidad': col_capacidad,
            'Sección': col_seccion
        }
        
        for campo, columna in mapeo.items():
            if columna:
                st.success(f"✅ {campo}: `{columna}`")
            else:
                st.warning(f"⚠️ {campo}: No encontrada (usando valores por defecto)")
        
        # Procesar cada fila
        filas_procesadas = 0
        filas_con_error = 0
        
        for idx, fila in self.df_original.iterrows():
            try:
                # Extraer datos básicos
                codigo_curso = fila.get(col_series, f'CURSO_{idx}') if col_series else f'CURSO_{idx}'
                nombre_curso = fila.get(col_nombre, 'Curso sin nombre') if col_nombre else 'Curso sin nombre'
                creditos = fila.get(col_creditos, 3) if col_creditos else 3
                capacidad = fila.get(col_capacidad, 30) if col_capacidad else 30
                profesores_str = fila.get(col_profesores, '') if col_profesores else ''
                email = fila.get(col_email, '') if col_email else ''
                meetings = fila.get(col_meetings, '') if col_meetings else ''
                seccion = fila.get(col_seccion, '001') if col_seccion else '001'
                
                # Saltar filas vacías
                if pd.isna(codigo_curso) or str(codigo_curso).strip() == '':
                    continue
                
                # Extraer profesor
                profesor_nombre, porcentaje = self.extraer_profesor_y_porcentaje(profesores_str)
                
                if not profesor_nombre:
                    profesor_nombre = f"Profesor_{idx}"
                
                # Parsear horario
                horario_info = self.parsear_horario_meetings(meetings)
                
                # Inicializar profesor
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
                
                # Convertir créditos y capacidad a números
                try:
                    creditos_num = int(float(creditos)) if not pd.isna(creditos) else 3
                except:
                    creditos_num = 3
                
                try:
                    capacidad_num = int(float(capacidad)) if not pd.isna(capacidad) else 30
                except:
                    capacidad_num = 30
                
                # Agregar curso
                curso_info = {
                    'codigo': str(codigo_curso),
                    'nombre': str(nombre_curso),
                    'creditos': creditos_num,
                    'estudiantes': capacidad_num,
                    'porcentaje_carga': porcentaje,
                    'horario_actual': horario_info,
                    'seccion': str(seccion)
                }
                
                self.profesores_data[profesor_nombre]['cursos'].append(curso_info)
                self.profesores_data[profesor_nombre]['creditos_totales'] += curso_info['creditos']
                
                filas_procesadas += 1
                
            except Exception as e:
                filas_con_error += 1
                st.warning(f"⚠️ Error en fila {idx}: {e}")
                continue
        
        st.success(f"✅ Procesamiento completado:")
        st.info(f"• {filas_procesadas} cursos procesados correctamente")
        st.info(f"• {len(self.profesores_data)} profesores identificados")
        if filas_con_error > 0:
            st.warning(f"• {filas_con_error} filas con errores (ignoradas)")
        
        # Mostrar resumen de profesores
        with st.expander("👥 Ver resumen de profesores"):
            for profesor, data in self.profesores_data.items():
                st.write(f"**{profesor}** - {len(data['cursos'])} cursos, {data['creditos_totales']} créditos")
        
        return len(self.profesores_data) > 0
    
    def obtener_profesores_config(self):
        """Retorna la configuración de profesores"""
        return self.profesores_data

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
    
    dias_pref_key = f"dias_pref_{profesor_nombre}_{hash(profesor_nombre)}"
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
            key=f"dias_custom_{profesor_nombre}_{hash(profesor_nombre)}"
        )
        dias_preferidos = dias_custom
    else:
        dias_preferidos = dias_opciones[dias_seleccion]
    
    profesor_config['dias_preferidos'] = dias_preferidos
    
    st.markdown("---")
    
    # Preferencias de turno
    st.markdown("#### Turno Preferido")
    
    turno_pref = st.radio(
        "Preferencia de horario",
        ["Mañana (antes de 12:30)", "Tarde (después de 12:30)", "Sin preferencia"],
        index=0 if profesor_config.get('turno_preferido') == 'Mañana' else 1,
        key=f"turno_{profesor_nombre}_{hash(profesor_nombre)}"
    )
    
    if turno_pref == "Mañana (antes de 12:30)":
        profesor_config['turno_preferido'] = 'Mañana'
    elif turno_pref == "Tarde (después de 12:30)":
        profesor_config['turno_preferido'] = 'Tarde'
    else:
        profesor_config['turno_preferido'] = 'Sin preferencia'
    
    return profesor_config

# ========================================================
# SISTEMA DE GENERACIÓN DE HORARIOS
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

    # Bloques de 4 créditos
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

    for dia in ["Lu","Ma","Mi","Ju","Vi"]:
        bloques.append({"id": id_counter, "dias": [dia], "horas": [3], "creditos": 3})
        id_counter += 1

    return bloques

def a_minutos(hhmm):
    """Convierte hora a minutos"""
    try:
        h, m = map(int, hhmm.split(":"))
        return h * 60 + m
    except:
        return 0

def horario_valido_zona(dia, hora_inicio, duracion, zona_config, profesor_config=None):
    """Verifica validez del horario"""
    ini_min = a_minutos(hora_inicio)
    fin_min = ini_min + int(duracion * 60)
    
    restricciones = zona_config['restricciones']
    if dia in restricciones:
        for r_ini, r_fin in restricciones[dia]:
            r_ini_min = a_minutos(r_ini)
            r_fin_min = a_minutos(r_fin)
            if not (fin_min <= r_ini_min or ini_min >= r_fin_min):
                return False
    
    if profesor_config and 'horario_no_disponible' in profesor_config:
        if dia in profesor_config['horario_no_disponible']:
            for nd_ini, nd_fin in profesor_config['horario_no_disponible'][dia]:
                nd_ini_min = a_minutos(nd_ini)
                nd_fin_min = a_minutos(nd_fin)
                if not (fin_min <= nd_ini_min or ini_min >= nd_fin_min):
                    return False
    
    return True

def cumple_preferencias_profesor(dia, hora_inicio, duracion, profesor_config):
    """Calcula score de preferencias"""
    score = 0
    
    if 'dias_preferidos' in profesor_config and profesor_config['dias_preferidos']:
        if dia in profesor_config['dias_preferidos']:
            score += 30
        else:
            score -= 20
    
    if 'turno_preferido' in profesor_config:
        hora_min = a_minutos(hora_inicio)
        mediodia = a_minutos("12:30")
        
        if profesor_config['turno_preferido'] == 'Mañana' and hora_min < mediodia:
            score += 20
        elif profesor_config['turno_preferido'] == 'Tarde' and hora_min >= mediodia:
            score += 20
    
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
    """Verifica conflictos"""
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
    """Genera horario optimizado"""
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
                bloques_compatibles = [b for b in bloques if b["creditos"] == curso_info["creditos"]]
                if not bloques_compatibles:
                    bloques_compatibles = bloques[:5]
                
                mejor_asignacion_curso = None
                mejor_score_curso = -float('inf')
                
                for _ in range(50):
                    bloque = random.choice(bloques_compatibles)
                    hora_inicio = random.choice(horas_inicio)
                    salon = random.choice(salones)
                    
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
        
        total_cursos = sum(len(prof['cursos']) for prof in profesores_config.values())
        if len(asignaciones) == total_cursos and score_total > mejor_score:
            mejor_score = score_total
            mejor_asignaciones = asignaciones
    
    status_text.text(f"Generación completada. Mejor puntuación: {mejor_score}")
    return mejor_asignaciones, mejor_score

def exportar_horario(asignaciones):
    """Exporta horario"""
    registros = []
    for asig in asignaciones:
        registros.extend(asig.get_horario_detallado())
    return pd.DataFrame(registros)

# ========================================================
# VISUALIZACIÓN
# ========================================================

def crear_tabla_horario_visual(df_horario):
    """Crea tabla visual"""
    if df_horario.empty:
        st.warning("No hay datos para mostrar")
        return
    
    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
    dias_map = {'Lu': 'Lunes', 'Ma': 'Martes', 'Mi': 'Miércoles', 'Ju': 'Jueves', 'Vi': 'Viernes'}
    
    horas_unicas = sorted(df_horario['Hora Inicio'].unique())
    
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
    st.markdown("**Versión 2.0** - Soporte mejorado para CSV y Excel")
    
    # Sidebar
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
    
    # Cargar archivo
    st.sidebar.subheader("2. Cargar Archivo")
    uploaded_file = st.sidebar.file_uploader(
        "Subir Excel o CSV",
        type=['xlsx', 'xls', 'csv'],
        help="Archivo del formulario de Google Forms"
    )
    
    # Session state
    if 'procesador' not in st.session_state:
        st.session_state.procesador = None
    if 'profesores_config' not in st.session_state:
        st.session_state.profesores_config = {}
    if 'horario_generado' not in st.session_state:
        st.session_state.horario_generado = None
    
    # Procesar archivo
    if uploaded_file is not None:
        if st.sidebar.button("🔄 Procesar Archivo", type="primary"):
            with st.spinner("Procesando archivo..."):
                procesador = ProcesadorExcelFormulario(uploaded_file)
                if procesador.detectar_y_cargar_archivo():
                    if procesador.procesar_datos():
                        st.session_state.procesador = procesador
                        st.session_state.profesores_config = procesador.obtener_profesores_config()
                        st.success("✅ Archivo procesado correctamente")
                        st.rerun()
    
    # Mostrar interfaz principal
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
        
        # Tabs
        tab1, tab2, tab3 = st.tabs(["📝 Editar Preferencias", "🔄 Generar Horario", "📊 Ver Horario"])
        
        with tab1:
            st.markdown("## Editor de Preferencias de Profesores")
            
            profesor_seleccionado = st.selectbox(
                "Seleccionar profesor:",
                list(st.session_state.profesores_config.keys()),
                key="selector_profesor_main"
            )
            
            if profesor_seleccionado:
                st.markdown("---")
                profesor_config = st.session_state.profesores_config[profesor_seleccionado]
                
                profesor_config_actualizado = mostrar_editor_preferencias_profesor(
                    profesor_seleccionado,
                    profesor_config,
                    zona_seleccionada
                )
                
                if st.button("💾 Guardar Preferencias", type="primary", key="btn_guardar_pref"):
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
            
            if st.button("🚀 Generar Horario Optimizado", type="primary", key="btn_generar_horario"):
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
                        st.error("❌ No se pudo generar un horario válido")
        
        with tab3:
            st.markdown("## Visualización del Horario")
            
            if st.session_state.horario_generado is not None:
                df_horario = st.session_state.horario_generado
                
                vista = st.radio(
                    "Tipo de vista:",
                    ["Tabla Visual", "Tabla Completa", "Por Profesor", "Por Salón"],
                    horizontal=True
                )
                
                if vista == "Tabla Visual":
                    crear_tabla_horario_visual(df_horario)
                
                elif vista == "Tabla Completa":
                    st.dataframe(df_horario, use_container_width=True)
                    
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
                        sorted(df_horario['Profesor'].unique()),
                        key="filtro_profesor"
                    )
                    df_filtrado = df_horario[df_horario['Profesor'] == profesor_filtro]
                    st.dataframe(df_filtrado, use_container_width=True)
                
                elif vista == "Por Salón":
                    salon_filtro = st.selectbox(
                        "Seleccionar salón:",
                        sorted(df_horario['Salón'].unique()),
                        key="filtro_salon"
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
                st.info("👆 Genera un horario en la pestaña 'Generar Horario'")
    
    else:
        st.info("👈 Sube el archivo en el sidebar para comenzar")
        
        with st.expander("ℹ️ Información del Sistema"):
            st.markdown("""
            ### Cómo usar:
            
            1. **Seleccionar Zona**: Central o Periférica
            2. **Cargar Archivo**: Excel (.xlsx) o CSV (.csv)
            3. **Editar Preferencias**: Configura cada profesor
            4. **Generar Horario**: Optimización automática
            5. **Visualizar**: Múltiples vistas
            
            ### Formatos soportados:
            
            - ✅ Excel (.xlsx, .xls)
            - ✅ CSV separado por comas
            - ✅ CSV con diferentes encodings (UTF-8, Latin-1, etc.)
            
            ### Zonas:
            
            **Central:** 7:30, 8:30, 9:30... | No clases Ma-Ju 10:30-12:30
            
            **Periférica:** 7:00, 8:00, 9:00... | No clases 10:00-12:00
            """)

if __name__ == "__main__":
    main()
