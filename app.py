import streamlit as st
import pandas as pd
import random
import json
import numpy as np
from datetime import datetime, timedelta
import copy
import io
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import os
from pathlib import Path

# ========================================================
# SISTEMA DE RESERVAS DE SALONES
# ========================================================

class SistemaReservasSalones:
    def __init__(self, archivo_reservas="reservas_salones_ae.json"):
        self.archivo_reservas = archivo_reservas
        self.reservas = self.cargar_reservas()
    
    def cargar_reservas(self):
        """Carga las reservas existentes desde el archivo JSON"""
        if os.path.exists(self.archivo_reservas):
            try:
                with open(self.archivo_reservas, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                st.warning(f"Error al cargar reservas: {e}")
                return {}
        return {}
    
    def guardar_reservas(self):
        """Guarda las reservas en el archivo JSON"""
        try:
            with open(self.archivo_reservas, 'w', encoding='utf-8') as f:
                json.dump(self.reservas, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            st.error(f"Error al guardar reservas: {e}")
            return False
    
    def verificar_disponibilidad(self, salon, dia, hora_inicio, hora_fin, programa_solicitante):
        """Verifica si un salón está disponible en un horario específico"""
        clave_reserva = f"{salon}_{dia}_{hora_inicio}_{hora_fin}"
        
        if clave_reserva in self.reservas:
            programa_actual = self.reservas[clave_reserva].get('programa', '')
            if programa_actual != programa_solicitante:
                return False, programa_actual
        
        # Verificar solapamientos de tiempo
        for reserva_key, reserva_info in self.reservas.items():
            if reserva_key.startswith(f"{salon}_{dia}_"):
                reserva_inicio = reserva_info['hora_inicio']
                reserva_fin = reserva_info['hora_fin']
                programa_reserva = reserva_info.get('programa', '')
                
                if programa_reserva != programa_solicitante:
                    # Convertir a minutos para comparar
                    inicio_min = self.a_minutos(hora_inicio)
                    fin_min = self.a_minutos(hora_fin)
                    res_inicio_min = self.a_minutos(reserva_inicio)
                    res_fin_min = self.a_minutos(reserva_fin)
                    
                    # Verificar solapamiento
                    if not (fin_min <= res_inicio_min or inicio_min >= res_fin_min):
                        return False, programa_reserva
        
        return True, None
    
    def reservar_salon(self, salon, dia, hora_inicio, hora_fin, programa, curso, profesor):
        """Reserva un salón para un programa específico"""
        clave_reserva = f"{salon}_{dia}_{hora_inicio}_{hora_fin}"
        
        self.reservas[clave_reserva] = {
            'salon': salon,
            'dia': dia,
            'hora_inicio': hora_inicio,
            'hora_fin': hora_fin,
            'programa': programa,
            'curso': curso,
            'profesor': profesor,
            'fecha_reserva': datetime.now().isoformat()
        }
        
        return self.guardar_reservas()
    
    def liberar_reservas_programa(self, programa):
        """Libera todas las reservas de un programa específico"""
        claves_a_eliminar = []
        for clave, reserva in self.reservas.items():
            if reserva.get('programa') == programa:
                claves_a_eliminar.append(clave)
        
        for clave in claves_a_eliminar:
            del self.reservas[clave]
        
        return self.guardar_reservas()
    
    def obtener_reservas_programa(self, programa):
        """Obtiene todas las reservas de un programa específico"""
        reservas_programa = {}
        for clave, reserva in self.reservas.items():
            if reserva.get('programa') == programa:
                reservas_programa[clave] = reserva
        return reservas_programa
    
    def obtener_salones_disponibles(self, dia, hora_inicio, hora_fin, programa, lista_salones):
        """Obtiene lista de salones disponibles para un horario específico"""
        salones_disponibles = []
        for salon in lista_salones:
            disponible, _ = self.verificar_disponibilidad(salon, dia, hora_inicio, hora_fin, programa)
            if disponible:
                salones_disponibles.append(salon)
        return salones_disponibles
    
    def a_minutos(self, hhmm):
        """Convierte hora HH:MM a minutos desde medianoche"""
        h, m = map(int, hhmm.split(":"))
        return h * 60 + m
    
    def obtener_estadisticas_uso(self):
        """Obtiene estadísticas de uso de salones"""
        stats = {
            'total_reservas': len(self.reservas),
            'programas_activos': len(set(r.get('programa', '') for r in self.reservas.values())),
            'salones_en_uso': len(set(r.get('salon', '') for r in self.reservas.values())),
            'reservas_por_programa': {},
            'reservas_por_salon': {}
        }
        
        for reserva in self.reservas.values():
            programa = reserva.get('programa', 'Sin programa')
            salon = reserva.get('salon', 'Sin salón')
            
            stats['reservas_por_programa'][programa] = stats['reservas_por_programa'].get(programa, 0) + 1
            stats['reservas_por_salon'][salon] = stats['reservas_por_salon'].get(salon, 0) + 1
        
        return stats

# ========================================================
# CONFIGURACIÓN RUM (Programas por colegio y nivel)
# ========================================================

PROGRAMAS_RUM = {
    "COLEGIO DE ADMINISTRACIÓN DE EMPRESAS": {
        "color": "#FF6B6B",
        "salones_compartidos": 18,
        "prefijo_salon": "AE",
        "sistema_reservas": True,  # NUEVO: Indica que usa sistema de reservas
        "niveles": {
            "Bachilleratos en Administración de Empresas": [
                "Contabilidad",
                "Finanzas",
                "Gerencia de Recursos Humanos",
                "Mercadeo",
                "Gerencia de Operaciones",
                "Sistemas Computadorizados de Información",
                "Administración de Oficinas"
            ],
            "Maestrías en Administración de Empresas": [
                "Administración de Empresas (Programa General)",
                "Finanzas",
                "Gerencia Industrial",
                "Recursos Humanos"
            ]
        }
    },
    "COLEGIO DE ARTES Y CIENCIAS": {
        "color": "#4ECDC4",
        "salones_compartidos": 25,
        "prefijo_salon": "AC",
        "sistema_reservas": False,
        "niveles": {
            "Bachilleratos en Artes": [
                "Literatura Comparada", "Economía", "Inglés", "Historia",
                "Lengua y Literatura Francesa", "Estudios Hispánicos", "Filosofía",
                "Educación Física – Enseñanza", "Educación Física – Adiestramiento y Arbitraje",
                "Artes Plásticas", "Ciencias Políticas", "Psicología",
                "Ciencias Sociales", "Sociología", "Teoría del Arte"
            ],
            "Bachilleratos en Ciencias": [
                "Biología", "Microbiología Industrial", "Pre-Médica", "Biotecnología Industrial",
                "Química", "Geología", "Matemáticas", "Matemáticas – Ciencias de la Computación",
                "Educación Matemática", "Enfermería", "Física", "Ciencias Físicas"
            ],
            "Maestrías en Artes": [
                "Estudios Culturales y Humanísticos", "Estudios Hispánicos",
                "Educación en Inglés", "Kinesiología"
            ],
            "Maestrías en Ciencias": [
                "Biología", "Química", "Geología", "Ciencias Marinas", "Física",
                "Matemáticas Aplicadas", "Matemática Estadística", "Matemática Pura",
                "Enseñanza de las Matemáticas a nivel preuniversitario",
                "Computación Científica", "Psicología Escolar"
            ],
            "Doctorados en Filosofía": [
                "Ciencias Marinas", "Química Aplicada", "Psicología Escolar"
            ]
        }
    },
    "COLEGIO DE CIENCIAS AGRÍCOLAS": {
        "color": "#96CEB4",
        "salones_compartidos": 15,
        "prefijo_salon": "CA",
        "sistema_reservas": False,
        "niveles": {
            "Bachilleratos en Ciencias Agrícolas": [
                "Ciencias Agrícolas", "Agronomía", "Economía Agrícola", "Horticultura",
                "Ciencia Animal", "Protección de Cultivos", "Agronegocios",
                "Educación Agrícola", "Extensión Agrícola", "Suelos",
                "Sistemas Agrícolas y Ambientales", "Pre-Veterinaria (No conducente a grado)"
            ],
            "Maestrías en Ciencias": [
                "Agronomía", "Ciencias y Tecnología de Alimentos", "Economía Agrícola",
                "Educación Agrícola", "Extensión Agrícola", "Horticultura",
                "Ciencia Animal", "Protección de Cultivos", "Suelos"
            ]
        }
    },
    "COLEGIO DE INGENIERÍA": {
        "color": "#FFEAA7",
        "salones_compartidos": 20,
        "prefijo_salon": "ING",
        "sistema_reservas": False,
        "niveles": {
            "Bachilleratos en Ingeniería": [
                "Ingeniería Química", "Ingeniería Civil", "Ingeniería de Computadoras",
                "Ciencias e Ingeniería de la Computación", "Ingeniería Eléctrica",
                "Ingeniería Industrial", "Ingeniería Mecánica", "Ingeniería de Software",
                "Agrimensura y Topografía"
            ],
            "Maestrías en Ciencias": [
                "Bioingeniería", "Ingeniería Química", "Ingeniería Civil",
                "Ingeniería de Computadoras", "Ingeniería Eléctrica", "Ingeniería Industrial",
                "Ciencia e Ingeniería de Materiales", "Ingeniería Mecánica"
            ],
            "Maestrías en Ingeniería": [
                "Bioingeniería", "Ingeniería Química", "Ingeniería Civil",
                "Ingeniería de Computadoras", "Ingeniería Eléctrica", "Ingeniería Industrial",
                "Ciencia e Ingeniería de Materiales", "Ingeniería Mecánica"
            ],
            "Doctorados en Filosofía": [
                "Bioingeniería", "Ingeniería Química", "Ingeniería Civil",
                "Ingeniería Eléctrica", "Ingeniería Mecánica",
                "Ciencias e Ingeniería de la Información y la Computación"
            ]
        }
    }
}

# ========================================================
# CONFIGURACIÓN DEL SISTEMA CON RESERVAS
# ========================================================

class ConfiguracionSistema:
    def __init__(self, archivo_excel=None, programa_actual=None, colegio_actual=None):
        self.archivo_excel = archivo_excel
        self.programa_actual = programa_actual
        self.colegio_actual = colegio_actual
        self.profesores_config = {}
        self.salones = []
        self.cursos_df = None
        
        # NUEVO: Sistema de reservas si el colegio lo requiere
        self.usa_reservas = False
        if colegio_actual and colegio_actual in PROGRAMAS_RUM:
            self.usa_reservas = PROGRAMAS_RUM[colegio_actual].get('sistema_reservas', False)
            if self.usa_reservas:
                self.sistema_reservas = SistemaReservasSalones()
        
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
                
                if any('profesor' in col or 'docente' in col for col in columnas_df) and \
                   any('curso' in col or 'materia' in col or 'asignatura' in col for col in columnas_df):
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
        
        # Configurar salones según el colegio
        if self.colegio_actual and self.colegio_actual in PROGRAMAS_RUM:
            colegio_info = PROGRAMAS_RUM[self.colegio_actual]
            num_salones = colegio_info.get('salones_compartidos', 15)
            prefijo = colegio_info.get('prefijo_salon', 'SALON')
            self.salones = [f"{prefijo}-{i+1:02d}" for i in range(num_salones)]
        else:
            # Salones por defecto
            num_salones = 15
            self.salones = [f"Salon {i+1}" for i in range(num_salones)]
        
        st.success(f"✅ Configuración completada: {len(self.profesores_config)} profesores, {len(self.salones)} salones")

# Resto de las funciones de generación de bloques y horarios (sin cambios)
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

# Tabla de créditos adicionales por tamaño de sección
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

# Horario de 7:00 a 19:20 en intervalos de 30 minutos
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

def horario_valido(dia, hora_inicio, duracion, profesor=None, creditos=None):
    """Verifica si un horario es válido según las restricciones fuertes"""
    ini_min = a_minutos(hora_inicio)
    fin_min = ini_min + int(duracion * 60)
    
    if fin_min > a_minutos(config.restricciones_globales["hora_fin_max"]):
        return False
    
    if ini_min < a_minutos(config.restricciones_globales["hora_inicio_min"]):
        return False
    
    if creditos and not es_bloque_tres_horas_valido(dia, hora_inicio, duracion, creditos):
        return False
    
    restricciones_horario = config.restricciones_globales["horarios_prohibidos"]
    if dia in restricciones_horario:
        for r_ini, r_fin in restricciones_horario[dia]:
            r_ini_min = a_minutos(r_ini)
            r_fin_min = a_minutos(r_fin)
            if not (fin_min <= r_ini_min or ini_min >= r_fin_min):
                return False
    
    if profesor and profesor in config.profesores_config:
        prof_config = config.profesores_config[profesor]
        if dia in prof_config["horario_no_disponible"]:
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
    if dia not in prof_config["horario_preferido"]:
        return False
    
    ini_min = a_minutos(hora_inicio)
    fin_min = ini_min + int(duracion * 60)
    
    for pref_ini, pref_fin in prof_config["horario_preferido"][dia]:
        pref_ini_min = a_minutos(pref_ini)
        pref_fin_min = a_minutos(pref_fin)
        if ini_min >= pref_ini_min and fin_min <= pref_fin_min:
            return True
    
    return False

# Clase para representar una asignación de clase (MODIFICADA CON RESERVAS)
class AsignacionClase:
    def __init__(self, curso_info, profesor, bloque, hora_inicio, salon):
        self.curso_nombre = curso_info["nombre"]
        self.profesor = profesor
        self.bloque = bloque
        self.hora_inicio = hora_inicio
        self.estudiantes = curso_info["estudiantes"]
        self.salon = salon
        self.creditos = curso_info["creditos"]
        self.horas_contacto = int(sum(bloque["horas"]))
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

# NUEVA FUNCIÓN: Generador de horarios con sistema de reservas
def generar_horario_valido_con_reservas():
    """Genera un horario que cumple todas las restricciones fuertes Y verifica reservas de salones"""
    asignaciones = []
    
    for profesor, prof_config in config.profesores_config.items():
        cursos_asignados = 0
        intentos = 0
        max_intentos = 3000
        
        while cursos_asignados < len(prof_config["cursos"]) and intentos < max_intentos:
            intentos += 1
            
            curso_info = prof_config["cursos"][cursos_asignados]
            
            bloques_compatibles = [b for b in bloques if b["creditos"] == curso_info["creditos"]]
            
            if not bloques_compatibles:
                bloques_compatibles = sorted(bloques, key=lambda x: abs(x["creditos"] - curso_info["creditos"]))[:5]
            
            bloque = random.choice(bloques_compatibles)
            hora_inicio = random.choice(horas_inicio)
            
            # NUEVO: Verificar salones disponibles considerando reservas
            if config.usa_reservas:
                salones_disponibles = []
                for dia, duracion in zip(bloque["dias"], bloque["horas"]):
                    hora_fin_min = a_minutos(hora_inicio) + int(duracion * 60)
                    hora_fin = f"{hora_fin_min//60:02d}:{hora_fin_min%60:02d}"
                    
                    salones_dia = config.sistema_reservas.obtener_salones_disponibles(
                        dia, hora_inicio, hora_fin, config.programa_actual, config.salones
                    )
                    
                    if not salones_disponibles:
                        salones_disponibles = salones_dia
                    else:
                        # Intersección de salones disponibles en todos los días
                        salones_disponibles = list(set(salones_disponibles) & set(salones_dia))
                
                if not salones_disponibles:
                    continue  # No hay salones disponibles, intentar otro horario
                
                salon = random.choice(salones_disponibles)
            else:
                salon = random.choice(config.salones)
            
            # Verificar validez del horario
            valido = True
            for dia, duracion in zip(bloque["dias"], bloque["horas"]):
                if not horario_valido(dia, hora_inicio, duracion, profesor, curso_info["creditos"]):
                    valido = False
                    break
            
            if not valido:
                continue
            
            nueva_asignacion = AsignacionClase(curso_info, profesor, bloque, hora_inicio, salon)
            
            if not hay_conflictos(nueva_asignacion, asignaciones):
                asignaciones.append(nueva_asignacion)
                cursos_asignados += 1
        
        if cursos_asignados < len(prof_config["cursos"]):
            return None
    
    return asignaciones

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

def evaluar_horario(asignaciones):
    """Evalúa un horario considerando restricciones fuertes y suaves configurables"""
    if asignaciones is None:
        return -float('inf')
    
    penalizacion = 0
    bonus = 0
    
    # Verificar que cada profesor tenga todos sus cursos asignados
    for profesor, prof_config in config.profesores_config.items():
        cursos_asignados = sum(1 for asig in asignaciones if asig.profesor == profesor)
        cursos_requeridos = len(prof_config["cursos"])
        if cursos_asignados != cursos_requeridos:
            penalizacion += abs(cursos_asignados - cursos_requeridos) * 2000
    
    # Verificar límite de créditos por profesor
    creditos_por_prof = {}
    for asig in asignaciones:
        creditos_por_prof.setdefault(asig.profesor, 0)
        creditos_por_prof[asig.profesor] += asig.creditos
    
    for profesor, prof_config in config.profesores_config.items():
        creditos_actuales = creditos_por_prof.get(profesor, 0)
        creditos_objetivo = prof_config["creditos_totales"]
        
        if creditos_actuales > config.restricciones_globales["creditos_max_profesor"]:
            penalizacion += (creditos_actuales - config.restricciones_globales["creditos_max_profesor"]) * 1000
        
        if creditos_actuales < config.restricciones_globales["creditos_min_profesor"]:
            penalizacion += (config.restricciones_globales["creditos_min_profesor"] - creditos_actuales) * 1000
        
        if creditos_actuales != creditos_objetivo:
            penalizacion += abs(creditos_actuales - creditos_objetivo) * 200
    
    # Verificar conflictos de horario
    for i, asig1 in enumerate(asignaciones):
        for j, asig2 in enumerate(asignaciones):
            if i >= j:
                continue
            if hay_conflictos(asig1, [asig2]):
                penalizacion += 5000
    
    # Verificar cumplimiento de restricción de 3 horas
    for asig in asignaciones:
        for dia, duracion in zip(asig.bloque["dias"], asig.bloque["horas"]):
            if not es_bloque_tres_horas_valido(dia, asig.hora_inicio, duracion, asig.creditos):
                penalizacion += 10000
    
    # Restricciones suaves
    pesos = config.pesos_restricciones
    
    for asig in asignaciones:
        for dia, duracion in zip(asig.bloque["dias"], asig.bloque["horas"]):
            if cumple_horario_preferido(dia, asig.hora_inicio, duracion, asig.profesor):
                bonus += pesos["horario_preferido"]
        
        if asig.estudiantes > config.restricciones_globales["estudiantes_max_salon"]:
            penalizacion += pesos["estudiantes_por_salon"] * (asig.estudiantes - config.restricciones_globales["estudiantes_max_salon"])
    
    return bonus - penalizacion

def buscar_mejor_horario(intentos=200):
    """Genera varios horarios y retorna el mejor según la evaluación"""
    mejor_asignaciones = None
    mejor_score = -float('inf')
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(intentos):
        progress_bar.progress((i + 1) / intentos)
        status_text.text(f"🔄 Generando horarios... {i+1}/{intentos}")
        
        # Usar función con reservas si está habilitado
        if config.usa_reservas:
            asignaciones = generar_horario_valido_con_reservas()
        else:
            asignaciones = generar_horario_valido()
            
        score = evaluar_horario(asignaciones)
        if score > mejor_score:
            mejor_score = score
            mejor_asignaciones = asignaciones
    
    status_text.text(f"✅ Generación completada. Mejor puntuación: {mejor_score}")
    return mejor_asignaciones, mejor_score

def exportar_horario(asignaciones):
    """Convierte las asignaciones a un DataFrame para visualización"""
    registros = []
    for asig in asignaciones:
        registros.extend(asig.get_horario_detallado())
    df = pd.DataFrame(registros)
    return df

# NUEVA FUNCIÓN: Guardar reservas del horario generado
def guardar_reservas_horario(asignaciones, programa):
    """Guarda las reservas de salones del horario generado"""
    if not config.usa_reservas:
        return True
    
    # Primero liberar reservas anteriores del programa
    config.sistema_reservas.liberar_reservas_programa(programa)
    
    # Guardar nuevas reservas
    for asig in asignaciones:
        for dia, duracion in zip(asig.bloque["dias"], asig.bloque["horas"]):
            hora_fin_min = a_minutos(asig.hora_inicio) + int(duracion * 60)
            hora_fin = f"{hora_fin_min//60:02d}:{hora_fin_min%60:02d}"
            
            config.sistema_reservas.reservar_salon(
                salon=asig.salon,
                dia=dia,
                hora_inicio=asig.hora_inicio,
                hora_fin=hora_fin,
                programa=programa,
                curso=asig.curso_nombre,
                profesor=asig.profesor
            )
    
    return True

# ========================================================
# FUNCIONES DE VISUALIZACIÓN (sin cambios significativos)
# ========================================================

def generar_colores_cursos(df_horario):
    """Genera una paleta de colores única para cada curso"""
    cursos_unicos = df_horario['Curso'].unique()
    
    # Paleta de colores moderna y vibrante
    colores_base = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', 
        '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9',
        '#F8C471', '#82E0AA', '#F1948A', '#85C1E9', '#D5A6BD',
        '#AED6F1', '#A9DFBF', '#F9E79F', '#D7BDE2', '#A3E4D7'
    ]
    
    # Asignar colores a cursos
    colores_cursos = {}
    for i, curso in enumerate(cursos_unicos):
        colores_cursos[curso] = colores_base[i % len(colores_base)]
    
    return colores_cursos

def crear_calendario_interactivo(df_horario, profesor_filtro=None):
    """Crea un calendario visual estilo Google Calendar con Plotly"""
    
    # Filtrar por profesor si se especifica
    if profesor_filtro and profesor_filtro != "Todos los profesores":
        df_filtrado = df_horario[df_horario['Profesor'] == profesor_filtro]
        titulo_calendario = f"📅 Calendario de {profesor_filtro}"
    else:
        df_filtrado = df_horario
        titulo_calendario = "📅 Calendario Semanal de Clases - Vista Completa"
    
    # Generar colores para cada curso
    colores_cursos = generar_colores_cursos(df_horario)
    
    # Mapeo de días a números para el eje X
    dias_map = {'Lu': 1, 'Ma': 2, 'Mi': 3, 'Ju': 4, 'Vi': 5}
    dias_nombres = ['', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
    
    # Crear figura
    fig = go.Figure()
    
    # Procesar cada clase para crear los bloques
    for _, fila in df_filtrado.iterrows():
        dia_num = dias_map[fila['Dia']]
        
        # Convertir horas a minutos desde medianoche para el eje Y
        hora_inicio_min = a_minutos(fila['Hora Inicio'])
        hora_fin_min = a_minutos(fila['Hora Fin'])
        
        # Crear el bloque de la clase
        fig.add_shape(
            type="rect",
            x0=dia_num - 0.4,
            y0=hora_inicio_min,
            x1=dia_num + 0.4,
            y1=hora_fin_min,
            fillcolor=colores_cursos[fila['Curso']],
            opacity=0.8,
            line=dict(color="white", width=2),
        )
        
        # Añadir texto de información de la clase
        texto_clase = f"<b>{fila['Curso']}</b><br>"
        texto_clase += f"👨‍🏫 {fila['Profesor']}<br>"
        texto_clase += f"🏫 {fila['Salon']}<br>"
        texto_clase += f"👥 {fila['Estudiantes']} estudiantes<br>"
        texto_clase += f"⏰ {fila['Hora Inicio']} - {fila['Hora Fin']}<br>"
        texto_clase += f"📚 {fila['Créditos']} créditos"
        
        # Añadir texto centrado en el bloque
        fig.add_annotation(
            x=dia_num,
            y=(hora_inicio_min + hora_fin_min) / 2,
            text=f"<b>{fila['Curso']}</b><br>{fila['Hora Inicio']}-{fila['Hora Fin']}<br>{fila['Salon']}",
            showarrow=False,
            font=dict(color="white", size=10, family="Arial Black"),
            bgcolor="rgba(0,0,0,0.7)",
            bordercolor="white",
            borderwidth=1,
            borderpad=4,
            hovertext=texto_clase
        )
    
    # Configurar el layout del calendario
    fig.update_layout(
        title={
            'text': titulo_calendario,
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24, 'color': '#2C3E50'}
        },
        xaxis=dict(
            tickmode='array',
            tickvals=[1, 2, 3, 4, 5],
            ticktext=dias_nombres[1:],
            range=[0.5, 5.5],
            showgrid=True,
            gridcolor='lightgray',
            title="Días de la Semana",
            title_font=dict(size=16, color='#34495E')
        ),
        yaxis=dict(
            tickmode='array',
            tickvals=[i*60 for i in range(7, 21)],
            ticktext=[f"{i:02d}:00" for i in range(7, 21)],
            range=[7*60, 20*60],
            showgrid=True,
            gridcolor='lightgray',
            title="Hora del Día",
            title_font=dict(size=16, color='#34495E'),
            autorange='reversed'
        ),
        plot_bgcolor='white',
        paper_bgcolor='#F8F9FA',
        width=1200,
        height=800,
        showlegend=False,
        margin=dict(l=80, r=80, t=100, b=80)
    )
    
    # Añadir líneas de cuadrícula más prominentes para las horas
    for hora in range(8, 20):
        fig.add_hline(
            y=hora*60, 
            line_dash="dot", 
            line_color="gray", 
            opacity=0.5
        )
    
    return fig, colores_cursos

def mostrar_leyenda_cursos(colores_cursos, df_horario, profesor_filtro=None):
    """Muestra una leyenda de colores para los cursos (filtrada si es necesario)"""
    
    # Filtrar cursos si hay un profesor seleccionado
    if profesor_filtro and profesor_filtro != "Todos los profesores":
        cursos_filtrados = df_horario[df_horario['Profesor'] == profesor_filtro]['Curso'].unique()
        colores_mostrar = {curso: color for curso, color in colores_cursos.items() if curso in cursos_filtrados}
        st.subheader(f"🎨 Cursos de {profesor_filtro}")
    else:
        colores_mostrar = colores_cursos
        st.subheader("🎨 Leyenda de Colores por Curso")
    
    # Crear columnas para mostrar la leyenda
    num_cols = 3
    cols = st.columns(num_cols)
    
    for i, (curso, color) in enumerate(colores_mostrar.items()):
        with cols[i % num_cols]:
            st.markdown(
                f"""
                <div style="
                    display: flex; 
                    align-items: center; 
                    margin: 5px 0;
                    padding: 8px;
                    border-radius: 5px;
                    background-color: {color}20;
                    border-left: 4px solid {color};
                ">
                    <div style="
                        width: 20px; 
                        height: 20px; 
                        background-color: {color}; 
                        margin-right: 10px;
                        border-radius: 3px;
                    "></div>
                    <span style="font-weight: 500; color: #2C3E50;">{curso}</span>
                </div>
                """, 
                unsafe_allow_html=True
            )

# NUEVA FUNCIÓN: Mostrar estado de reservas
def mostrar_estado_reservas():
    """Muestra el estado actual de las reservas de salones"""
    if not config.usa_reservas:
        return
    
    st.subheader("🏫 Estado Actual de Reservas de Salones")
    
    # Obtener estadísticas
    stats = config.sistema_reservas.obtener_estadisticas_uso()
    
    # Mostrar métricas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📋 Total Reservas", stats['total_reservas'])
    with col2:
        st.metric("📚 Programas Activos", stats['programas_activos'])
    with col3:
        st.metric("🏫 Salones en Uso", stats['salones_en_uso'])
    with col4:
        disponibles = len(config.salones) - stats['salones_en_uso']
        st.metric("✅ Salones Disponibles", disponibles)
    
    # Mostrar reservas por programa
    if stats['reservas_por_programa']:
        st.write("**📊 Reservas por Programa:**")
        for programa, cantidad in stats['reservas_por_programa'].items():
            st.write(f"• {programa}: {cantidad} reservas")
    
    # Mostrar reservas detalladas
    with st.expander("🔍 Ver todas las reservas activas"):
        if config.sistema_reservas.reservas:
            reservas_df = []
            for clave, reserva in config.sistema_reservas.reservas.items():
                reservas_df.append({
                    'Salón': reserva['salon'],
                    'Día': reserva['dia'],
                    'Hora Inicio': reserva['hora_inicio'],
                    'Hora Fin': reserva['hora_fin'],
                    'Programa': reserva['programa'],
                    'Curso': reserva['curso'],
                    'Profesor': reserva['profesor']
                })
            
            df_reservas = pd.DataFrame(reservas_df)
            st.dataframe(df_reservas, use_container_width=True)
        else:
            st.info("No hay reservas activas")

# ========================================================
# UI DE SELECCIÓN DE PROGRAMA Y GENERADOR (MODIFICADA)
# ========================================================

# Globals usados por el generador
config = None
bloques = []

def mostrar_seleccion_programa():
    """Muestra la interfaz de selección de programa por colegio y nivel académico"""
    st.markdown("## 🏛️ Selecciona tu Programa Académico")
    st.markdown("Elige tu programa de estudio del Recinto Universitario de Mayagüez para generar horarios optimizados.")
    
    # NUEVO: Información sobre sistema de reservas
    st.info("""
    🔄 **Sistema de Reservas de Salones**: 
    Para el Colegio de Administración de Empresas, este sistema evita conflictos de salones entre departamentos. 
    Cada jefe de departamento puede generar su horario de forma independiente, y el sistema automáticamente 
    bloquea los salones ya reservados por otros programas.
    """)
    
    for colegio, info in PROGRAMAS_RUM.items():
        with st.expander(f"🏛️ {colegio}", expanded=False):
            total_programas = sum(len(programas) for programas in info['niveles'].values())
            
            # Mostrar información sobre sistema de reservas
            if info.get('sistema_reservas', False):
                st.success(f"🔄 **Sistema de Reservas Activo**: {info['salones_compartidos']} salones compartidos entre todos los programas")
                st.info("💡 **Ventaja**: Cada jefe de departamento puede generar horarios independientemente sin conflictos de salones")
            
            st.markdown(f"**{total_programas} programas disponibles en {len(info['niveles'])} niveles académicos**")
            
            for nivel, programas in info['niveles'].items():
                st.markdown(f"### 🎓 {nivel}")
                st.markdown(f"*{len(programas)} programas*")
                
                cols = st.columns(3)
                for idx, programa in enumerate(programas):
                    with cols[idx % 3]:
                        card_html = f"""
                        <div style="
                            border: 1px solid {info['color']};
                            border-radius: 8px;
                            padding: 0.8rem;
                            margin: 0.3rem 0;
                            background: linear-gradient(135deg, {info['color']}15, {info['color']}08);
                            text-align: center;
                            min-height: 80px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                        ">
                            <p style="color: #333; margin: 0; font-size: 0.85rem; font-weight: 500; line-height: 1.2;">{programa}</p>
                        </div>
                        """
                        st.markdown(card_html, unsafe_allow_html=True)
                        if st.button("Seleccionar", key=f"btn_{colegio}_{nivel}_{programa}", use_container_width=True):
                            st.session_state.programa_seleccionado = programa
                            st.session_state.colegio_seleccionado = colegio
                            st.session_state.nivel_seleccionado = nivel
                            st.session_state.pagina_actual = 'generador'
                            st.rerun()
                st.markdown("---")
    
    if st.session_state.programa_seleccionado:
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.success(f"✅ **Programa:** {st.session_state.programa_seleccionado}")
            st.info(f"🎓 **Nivel:** {st.session_state.nivel_seleccionado}")
            st.info(f"🏛️ **Colegio:** {st.session_state.colegio_seleccionado}")
            if st.button("🚀 Continuar al Generador de Horarios", type="primary", use_container_width=True):
                st.session_state.pagina_actual = 'generador'
                st.rerun()

def mostrar_generador_horarios():
    """Muestra la interfaz del generador de horarios con sistema de reservas"""
    # Cabecera contextual del programa
    colegio_info = None
    for colegio, info in PROGRAMAS_RUM.items():
        if colegio == st.session_state.colegio_seleccionado:
            colegio_info = info
            break
    
    if colegio_info:
        # Mostrar información sobre reservas si aplica
        if colegio_info.get('sistema_reservas', False):
            st.markdown(f"""
            <div style="
                background: linear-gradient(90deg, {colegio_info['color']}30, {colegio_info['color']}10);
                padding: 1.5rem;
                border-radius: 10px;
                margin-bottom: 2rem;
                border-left: 5px solid {colegio_info['color']};
            ">
                <h3 style="margin: 0; color: #333;">📚 {st.session_state.programa_seleccionado}</h3>
                <p style="margin: 0.3rem 0; color: #666; font-size: 1rem;">🎓 {st.session_state.nivel_seleccionado}</p>
                <p style="margin: 0.3rem 0; color: #888; font-size: 0.9rem;">🏛️ {st.session_state.colegio_seleccionado}</p>
                <p style="margin: 0.5rem 0 0 0; color: #e74c3c; font-size: 0.9rem;">🔄 <strong>Sistema de Reservas Activo</strong> - Evita conflictos con otros departamentos</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="
                background: linear-gradient(90deg, {colegio_info['color']}30, {colegio_info['color']}10);
                padding: 1.5rem;
                border-radius: 10px;
                margin-bottom: 2rem;
                border-left: 5px solid {colegio_info['color']};
            ">
                <h3 style="margin: 0; color: #333;">📚 {st.session_state.programa_seleccionado}</h3>
                <p style="margin: 0.3rem 0; color: #666; font-size: 1rem;">🎓 {st.session_state.nivel_seleccionado}</p>
                <p style="margin: 0.3rem 0 0 0; color: #888; font-size: 0.9rem;">🏛️ {st.session_state.colegio_seleccionado}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("## 📁 Cargar Datos para Generación de Horarios")
    with st.expander("📋 Instrucciones para tu programa"):
        st.markdown(f"""
        ### Configuración para {st.session_state.programa_seleccionado}
        **Nivel:** {st.session_state.nivel_seleccionado}
        
        **Formato del archivo Excel requerido:**
        - **Hoja:** Debe contener los datos de profesores y cursos
        - **Columnas requeridas:** Profesor, Curso/Materia, Créditos, Estudiantes
        """)
        
        # Información específica sobre reservas
        if colegio_info and colegio_info.get('sistema_reservas', False):
            st.markdown(f"""
            **🔄 Sistema de Reservas de Salones:**
            - **Salones compartidos:** {colegio_info['salones_compartidos']} salones disponibles
            - **Coordinación automática:** El sistema evita conflictos con otros departamentos
            - **Generación independiente:** Cada jefe puede generar su horario cuando guste
            - **Bloqueo automático:** Los salones ocupados se marcan como no disponibles
            """)

    # Sidebar de estado y acciones
    st.sidebar.header("⚙️ Configuración")
    st.sidebar.markdown("### 📋 Estado Actual")
    if st.session_state.programa_seleccionado:
        st.sidebar.success(f"**Programa:** {st.session_state.programa_seleccionado}")
        if st.session_state.nivel_seleccionado:
            st.sidebar.info(f"**Nivel:** {st.session_state.nivel_seleccionado}")
        if st.session_state.colegio_seleccionado:
            st.sidebar.info(f"**Colegio:** {st.session_state.colegio_seleccionado}")
            
            # NUEVO: Mostrar estado de reservas en sidebar
            if colegio_info and colegio_info.get('sistema_reservas', False):
                st.sidebar.markdown("---")
                st.sidebar.markdown("### 🔄 Sistema de Reservas")
                st.sidebar.success("✅ Activo")
    else:
        st.sidebar.warning("No hay programa seleccionado")
    
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Cambiar Programa", use_container_width=True):
        st.session_state.pagina_actual = 'seleccion'
        st.session_state.programa_seleccionado = None
        st.session_state.colegio_seleccionado = None
        st.session_state.nivel_seleccionado = None
        st.rerun()

    # Upload del archivo Excel en sidebar
    uploaded_file = st.sidebar.file_uploader(
        "📁 Cargar archivo Excel con datos de profesores y cursos",
        type=['xlsx', 'xls'],
        help="El archivo debe contener columnas como: Profesor, Curso/Materia, Créditos, Estudiantes"
    )

    if uploaded_file is not None:
        # Guardar archivo temporalmente
        with open("temp_excel.xlsx", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Inicializar configuración
        global config, bloques
        config = ConfiguracionSistema(
            "temp_excel.xlsx", 
            st.session_state.programa_seleccionado,
            st.session_state.colegio_seleccionado
        )
        bloques = generar_bloques()

        # NUEVO: Mostrar estado de reservas si aplica
        if config.usa_reservas:
            mostrar_estado_reservas()
            
            # Opción para liberar reservas anteriores
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Liberar Reservas Anteriores", type="secondary"):
                    if config.sistema_reservas.liberar_reservas_programa(st.session_state.programa_seleccionado):
                        st.success("✅ Reservas anteriores liberadas correctamente")
                        st.rerun()
                    else:
                        st.error("❌ Error al liberar reservas")
            
            with col2:
                st.info("💡 Libera las reservas si necesitas regenerar el horario completamente")

        # Control de cantidad de salones en la barra lateral
        st.sidebar.subheader("🏫 Infraestructura")
        if colegio_info:
            num_salones_default = colegio_info.get('salones_compartidos', 15)
            if config.usa_reservas:
                st.sidebar.info(f"Salones compartidos: {num_salones_default}")
                st.sidebar.warning("⚠️ Los salones ya reservados por otros programas no estarán disponibles")
        else:
            num_salones_default = 15
        
        num_salones = st.sidebar.number_input(
            "Salones totales del edificio",
            min_value=1,
            max_value=100,
            value=num_salones_default,
            step=1,
            help="Cantidad total de salones en el edificio (compartidos entre programas)" if config.usa_reservas else "Cantidad de salones disponibles para el programa"
        )
        
        # Actualizar lista de salones
        if colegio_info:
            prefijo = colegio_info.get('prefijo_salon', 'SALON')
            config.salones = [f"{prefijo}-{i+1:02d}" for i in range(int(num_salones))]
        else:
            config.salones = [f"Salon {i+1}" for i in range(int(num_salones))]
        
        if config.profesores_config:
            st.success("✅ Archivo cargado correctamente")
            
            # Resumen de datos cargados
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("👨‍🏫 Profesores", len(config.profesores_config))
            with col2:
                total_cursos = sum(len(prof['cursos']) for prof in config.profesores_config.values())
                st.metric("📚 Cursos", total_cursos)
            with col3:
                st.metric("🏫 Salones Totales", len(config.salones))
            
            # Datos cargados
            with st.expander("📋 Ver datos cargados"):
                for profesor, data in config.profesores_config.items():
                    st.write(f"**{profesor}** ({data['creditos_totales']} créditos)")
                    for curso in data['cursos']:
                        st.write(f"  - {curso['nombre']} ({curso['creditos']} créditos, {curso['estudiantes']} estudiantes)")
            
            # Parámetros de Optimización
            st.sidebar.subheader("🎯 Parámetros de Optimización")
            intentos = st.sidebar.slider("Número de iteraciones", 50, 500, 200, 50)

            # Determinar presets por nivel
            nivel_text = st.session_state.nivel_seleccionado or ""
            if "Bachillerato" in nivel_text:
                hora_inicio_default = "07:30"
                hora_fin_default = "17:00"
                creditos_max_default = 15
            elif "Maestría" in nivel_text:
                hora_inicio_default = "08:00"
                hora_fin_default = "21:00"
                creditos_max_default = 12
            elif "Doctorado" in nivel_text:
                hora_inicio_default = "09:00"
                hora_fin_default = "19:00"
                creditos_max_default = 8
            else:
                hora_inicio_default = "07:30"
                hora_fin_default = "19:30"
                creditos_max_default = 15

            # Restricciones Globales
            with st.sidebar.expander("🔒 Restricciones Globales"):
                config.restricciones_globales["hora_inicio_min"] = st.time_input(
                    "Hora inicio mínima", 
                    datetime.strptime(hora_inicio_default, "%H:%M").time()
                ).strftime("%H:%M")
                
                config.restricciones_globales["hora_fin_max"] = st.time_input(
                    "Hora fin máxima", 
                    datetime.strptime(hora_fin_default, "%H:%M").time()
                ).strftime("%H:%M")
                
                config.restricciones_globales["creditos_max_profesor"] = st.number_input(
                    "Créditos máximos por profesor", 1, 20, creditos_max_default
                )
                
                config.restricciones_globales["estudiantes_max_salon"] = st.number_input(
                    "Estudiantes máximos por salón", 20, 100, 50
                )
            
            # Preferencias de Profesores
            st.sidebar.subheader("👤 Preferencias de Profesores")
            profesor_seleccionado = st.sidebar.selectbox(
                "Seleccionar profesor para configurar",
                ["Ninguno"] + list(config.profesores_config.keys())
            )
            
            if profesor_seleccionado != "Ninguno":
                with st.sidebar.expander(f"Configurar {profesor_seleccionado}"):
                    st.write("**Horarios preferidos:**")
                    dias = ["Lu", "Ma", "Mi", "Ju", "Vi"]
                    for dia in dias:
                        col1_pref, col2_pref = st.columns(2)
                        with col1_pref:
                            inicio = st.time_input(f"{dia} inicio", key=f"pref_{profesor_seleccionado}_{dia}_inicio")
                        with col2_pref:
                            fin = st.time_input(f"{dia} fin", key=f"pref_{profesor_seleccionado}_{dia}_fin")
                        
                        if inicio != datetime.strptime("00:00", "%H:%M").time():
                            if profesor_seleccionado not in config.profesores_config:
                                config.profesores_config[profesor_seleccionado] = {"horario_preferido": {}}
                            if "horario_preferido" not in config.profesores_config[profesor_seleccionado]:
                                config.profesores_config[profesor_seleccionado]["horario_preferido"] = {}
                            config.profesores_config[profesor_seleccionado]["horario_preferido"][dia] = [
                                (inicio.strftime("%H:%M"), fin.strftime("%H:%M"))
                            ]
            
            # Botón de generación
            if st.button("🚀 Generar Horario Optimizado", type="primary"):
                with st.spinner("Generando horario optimizado..."):
                    mejor, score = buscar_mejor_horario(intentos)
                    
                    if mejor is None:
                        st.error("❌ No se pudo generar un horario válido. Intenta ajustar las restricciones o liberar algunas reservas.")
                        if config.usa_reservas:
                            st.info("💡 **Sugerencia**: Algunos salones pueden estar ocupados por otros programas. Verifica el estado de reservas arriba.")
                    else:
                        st.success(f"✅ Horario generado exitosamente! Puntuación: {score}")
                        
                        # NUEVO: Guardar reservas si el sistema está activo
                        if config.usa_reservas:
                            if guardar_reservas_horario(mejor, st.session_state.programa_seleccionado):
                                st.success("🔄 Reservas de salones guardadas correctamente")
                            else:
                                st.warning("⚠️ Horario generado pero hubo problemas al guardar las reservas")
                        
                        df_horario = exportar_horario(mejor)
                        
                        # PESTAÑAS CON INFORMACIÓN DE RESERVAS
                        tab1, tab2, tab3, tab4, tab5 = st.tabs([
                            "📅 Calendario Visual", 
                            "📊 Horario Completo", 
                            "👨‍🏫 Por Profesor", 
                            "🏫 Por Salón", 
                            "📈 Estadísticas"
                        ])
                        
                        # PESTAÑA 1: CALENDARIO VISUAL INTERACTIVO
                        with tab1:
                            st.subheader("📅 Vista de Calendario Interactivo")
                            
                            # Información sobre reservas
                            if config.usa_reservas:
                                st.info("🔄 **Sistema de Reservas Activo**: Este horario ha sido registrado automáticamente para evitar conflictos con otros departamentos.")
                            
                            # NUEVO: Selector de profesor para filtrar el calendario
                            col1_filtro, col2_filtro = st.columns([2, 1])
                            with col1_filtro:
                                st.markdown("""
                                <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                                            padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                                    <p style="color: white; margin: 0; text-align: center; font-size: 1.1rem;">
                                        🎨 <strong>Calendario estilo Google Calendar</strong> - Cada curso tiene un color único
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col2_filtro:
                                # Selector de profesor
                                profesores_disponibles = ["Todos los profesores"] + sorted(df_horario['Profesor'].unique().tolist())
                                profesor_filtro = st.selectbox(
                                    "👨‍🏫 Filtrar por profesor:",
                                    profesores_disponibles,
                                    key="filtro_profesor_calendario"
                                )
                            
                            # Crear y mostrar el calendario (filtrado o completo)
                            fig_calendario, colores_cursos = crear_calendario_interactivo(df_horario, profesor_filtro)
                            st.plotly_chart(fig_calendario, use_container_width=True)
                            
                            # Mostrar leyenda de colores (filtrada si es necesario)
                            mostrar_leyenda_cursos(colores_cursos, df_horario, profesor_filtro)
                            
                            # Información adicional
                            col1_info, col2_info = st.columns(2)
                            with col1_info:
                                st.info("💡 **Tip:** Pasa el mouse sobre los bloques para ver información detallada")
                            with col2_info:
                                st.info("🔍 **Zoom:** Usa las herramientas de Plotly para hacer zoom y navegar")
                        
                        # PESTAÑA 2: HORARIO COMPLETO (original)
                        with tab2:
                            st.subheader("📊 Horario Completo")
                            
                            # Información sobre reservas
                            if config.usa_reservas:
                                st.success("🔄 **Reservas Confirmadas**: Todos los salones de este horario están reservados para tu programa.")
                            
                            st.dataframe(df_horario, use_container_width=True)
                            csv = df_horario.to_csv(index=False)
                            st.download_button(
                                label="💾 Descargar horario (CSV)",
                                data=csv,
                                file_name=f"horario_{st.session_state.programa_seleccionado.replace(' ', '_')}.csv",
                                mime="text/csv"
                            )
                        
                        # PESTAÑA 3: POR PROFESOR (original)
                        with tab3:
                            st.subheader("👨‍🏫 Horario por Profesor")
                            
                            # Selector de profesor para vista individual
                            profesor_individual = st.selectbox(
                                "Seleccionar profesor:",
                                sorted(config.profesores_config.keys()),
                                key="selector_profesor_individual"
                            )
                            
                            if profesor_individual:
                                df_prof = df_horario[df_horario['Profesor'] == profesor_individual]
                                if not df_prof.empty:
                                    # Mostrar calendario individual del profesor
                                    fig_prof, colores_prof = crear_calendario_interactivo(df_horario, profesor_individual)
                                    st.plotly_chart(fig_prof, use_container_width=True)
                                    
                                    # Mostrar tabla de datos
                                    st.dataframe(df_prof, use_container_width=True)
                                    
                                    # Estadísticas del profesor
                                    col1_prof, col2_prof, col3_prof = st.columns(3)
                                    with col1_prof:
                                        st.metric("📚 Total Cursos", len(df_prof))
                                    with col2_prof:
                                        st.metric("⏰ Horas Semanales", f"{df_prof['Duración'].sum():.1f}")
                                    with col3_prof:
                                        st.metric("🎓 Créditos Totales", df_prof['Créditos'].sum())
                                else:
                                    st.warning(f"No se encontraron clases para {profesor_individual}")
                        
                        # PESTAÑA 4: POR SALÓN (mejorada con información de reservas)
                        with tab4:
                            st.subheader("🏫 Horario por Salón")
                            
                            # Mostrar información sobre disponibilidad
                            if config.usa_reservas:
                                st.info("🔄 **Nota**: Solo se muestran los salones asignados a tu programa. Otros salones pueden estar ocupados por otros departamentos.")
                            
                            salones_usados = df_horario['Salon'].unique()
                            for salon in sorted(salones_usados):
                                with st.expander(f"Horario del {salon}"):
                                    df_salon = df_horario[df_horario['Salon'] == salon]
                                    st.dataframe(df_salon, use_container_width=True)
                                    
                                    # Estadísticas del salón
                                    horas_uso = df_salon['Duración'].sum()
                                    st.metric("⏰ Horas de uso semanal", f"{horas_uso:.1f}h")
                            
                            # Mostrar salones no utilizados
                            salones_no_usados = set(config.salones) - set(salones_usados)
                            if salones_no_usados:
                                st.write(f"**🏫 Salones no utilizados por tu programa:** {len(salones_no_usados)}")
                                if config.usa_reservas:
                                    st.info("💡 Algunos de estos salones pueden estar ocupados por otros programas")
                        
                        # PESTAÑA 5: ESTADÍSTICAS (mejorada con información de reservas)
                        with tab5:
                            st.subheader("📈 Estadísticas del Horario")
                            
                            # Métricas principales
                            col1_met, col2_met, col3_met, col4_met = st.columns(4)
                            with col1_met:
                                st.metric("📚 Total Cursos", len(df_horario))
                            with col2_met:
                                st.metric("👨‍🏫 Profesores", df_horario['Profesor'].nunique())
                            with col3_met:
                                st.metric("🏫 Salones Usados", df_horario['Salon'].nunique())
                            with col4_met:
                                total_estudiantes = df_horario['Estudiantes'].sum()
                                st.metric("👥 Total Estudiantes", total_estudiantes)
                            
                            # NUEVO: Información sobre eficiencia de uso de salones
                            if config.usa_reservas:
                                st.markdown("---")
                                st.subheader("🔄 Eficiencia del Sistema de Reservas")
                                
                                total_salones = len(config.salones)
                                salones_usados_programa = df_horario['Salon'].nunique()
                                eficiencia = (salones_usados_programa / total_salones) * 100
                                
                                col1_ef, col2_ef, col3_ef = st.columns(3)
                                with col1_ef:
                                    st.metric("🏫 Salones Totales", total_salones)
                                with col2_ef:
                                    st.metric("✅ Usados por tu Programa", salones_usados_programa)
                                with col3_ef:
                                    st.metric("📊 Eficiencia de Uso", f"{eficiencia:.1f}%")
                            
                            # Gráficos
                            col1_stats, col2_stats = st.columns(2)
                            with col1_stats:
                                st.write("**📊 Distribución de créditos por profesor:**")
                                creditos_prof = df_horario.groupby('Profesor')['Créditos'].sum()
                                fig_creditos = px.bar(
                                    x=creditos_prof.index, 
                                    y=creditos_prof.values,
                                    title="Créditos por Profesor",
                                    color=creditos_prof.values,
                                    color_continuous_scale="viridis"
                                )
                                fig_creditos.update_layout(showlegend=False)
                                st.plotly_chart(fig_creditos, use_container_width=True)
                            
                            with col2_stats:
                                st.write("**🏫 Utilización de salones:**")
                                uso_salones = df_horario.groupby('Salon').size()
                                fig_salones = px.pie(
                                    values=uso_salones.values, 
                                    names=uso_salones.index,
                                    title="Uso de Salones"
                                )
                                st.plotly_chart(fig_salones, use_container_width=True)
                            
                            # Análisis de restricciones
                            clases_3h = df_horario[df_horario['3h Consecutivas'] == 'SÍ']
                            if len(clases_3h) > 0:
                                st.write("**⏰ Cumplimiento de restricción de 3 horas consecutivas:**")
                                cumple = len(clases_3h[clases_3h['Restricción 15:30'] == 'CUMPLE'])
                                viola = len(clases_3h[clases_3h['Restricción 15:30'] == 'VIOLA'])
                                
                                col1_m, col2_m = st.columns(2)
                                with col1_m:
                                    st.metric("✅ Cumple restricción", cumple)
                                with col2_m:
                                    st.metric("⚠️ Viola restricción", viola)
                                
                                if viola > 0:
                                    st.warning("⚠️ Algunas clases de 3 horas consecutivas violan la restricción de horario (antes de 15:30)")
                                    st.dataframe(clases_3h[clases_3h['Restricción 15:30'] == 'VIOLA'])
        else:
            st.error("❌ No se pudieron cargar los datos del archivo Excel")
    else:
        st.info("📁 Por favor, carga un archivo Excel para comenzar")
        with st.expander("📋 Formato esperado del archivo Excel"):
            st.write("""
            El archivo Excel debe contener al menos las siguientes columnas:
            
            | Profesor | Curso/Materia | Créditos | Estudiantes |
            |----------|---------------|----------|-------------|
            | Juan Pérez | Matemáticas I | 4 | 35 |
            | Juan Pérez | Álgebra | 3 | 28 |
            | María García | Física I | 4 | 30 |
            
            **Notas:**
            - Los nombres de las columnas pueden variar (profesor/docente, curso/materia/asignatura, etc.)
            - Si faltan columnas de créditos o estudiantes, se usarán valores por defecto
            - El sistema detecta automáticamente las columnas relevantes
            """)
            
            # Información adicional sobre reservas
            if colegio_info and colegio_info.get('sistema_reservas', False):
                st.markdown("""
                ---
                **🔄 Sistema de Reservas de Salones:**
                - Cada vez que generes un horario, se reservarán automáticamente los salones
                - Otros jefes de departamento no podrán usar esos salones en los mismos horarios
                - Puedes liberar reservas anteriores si necesitas regenerar el horario
                - El sistema muestra qué salones están disponibles en tiempo real
                """)

def main():
    # Configuración de la página
    st.set_page_config(
        page_title="Sistema de Generación de Horarios Académicos - RUM",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # CSS personalizado para mejorar la apariencia
    st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f0f2f6;
        border-radius: 8px 8px 0px 0px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

    # Inicializar session state
    if 'programa_seleccionado' not in st.session_state:
        st.session_state.programa_seleccionado = None
    if 'colegio_seleccionado' not in st.session_state:
        st.session_state.colegio_seleccionado = None
    if 'nivel_seleccionado' not in st.session_state:
        st.session_state.nivel_seleccionado = None
    if 'pagina_actual' not in st.session_state:
        st.session_state.pagina_actual = 'seleccion'

    # Header principal
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 2rem;">
        <h1 style="color: white; margin: 0; font-size: 2.5rem;">🎓 Sistema de Generación de Horarios RUM</h1>
        <p style="color: white; margin: 0.5rem 0 0 0; font-size: 1.2rem;">Recinto Universitario de Mayagüez - Optimización con Algoritmos Genéticos</p>
        <p style="color: white; margin: 0.3rem 0 0 0; font-size: 1rem;">🔄 Con Sistema de Reservas de Salones para Coordinación entre Departamentos</p>
    </div>
    """, unsafe_allow_html=True)

    # Navegación
    if st.session_state.pagina_actual == 'seleccion':
        mostrar_seleccion_programa()
    elif st.session_state.pagina_actual == 'generador':
        mostrar_generador_horarios()

if __name__ == "__main__":
    main()
