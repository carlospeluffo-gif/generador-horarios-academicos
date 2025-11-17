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
from typing import List, Dict, Any, Tuple
import os
import hashlib
from pathlib import Path

# ========================================================
# SISTEMA DE AUTENTICACIÓN Y CREDENCIALES SIMPLIFICADO
# ========================================================

def generar_credenciales_simplificadas() -> Dict[str, Dict[str, str]]:
    """Genera el diccionario de credenciales simplificadas sin tildes ni caracteres especiales."""
    credenciales = {}
    
    # Mapear colegios a usuarios simplificados (SIN TILDES NI ESPACIOS)
    mapeo_usuarios = {
        "COLEGIO DE ADMINISTRACIÓN DE EMPRESAS": "admin_empresas",
        "COLEGIO DE ARTES Y CIENCIAS": "artes_ciencias", 
        "COLEGIO DE CIENCIAS AGRÍCOLAS": "ciencias_agricolas",
        "COLEGIO DE INGENIERÍA": "ingenieria",
        "DEPARTAMENTO DE MATEMÁTICAS": "matematicas"
    }
    
    # Programas simplificados para cada colegio (usados como contraseña simple)
    programas_simplificados = {
        "COLEGIO DE ADMINISTRACIÓN DE EMPRESAS": {
            "contabilidad": "Contabilidad", "finanzas": "Finanzas", 
            "recursos_humanos": "Gerencia de Recursos Humanos", "mercadeo": "Mercadeo",
            "operaciones": "Gerencia de Operaciones", "sistemas": "Sistemas Computadorizados de Información",
            "oficinas": "Administración de Oficinas"
        },
        "DEPARTAMENTO DE MATEMÁTICAS": {
            "mate_aplicada": "Matemáticas Aplicadas", "mate_pura": "Matemáticas Puras",
            "estadistica": "Matemática Estadística", "educacion_mate": "Educación Matemática",
            "computacion": "Ciencias de la Computación"
        },
        "COLEGIO DE ARTES Y CIENCIAS": {
            "literatura": "Literatura Comparada", "frances": "Lengua y Literatura Francesa",
            "filosofia": "Filosofía", "artes_plasticas": "Artes Plásticas",
            "teoria_arte": "Teoría del Arte", "economia": "Economía", "ingles": "Inglés",
            "historia": "Historia", "ciencias_politicas": "Ciencias Políticas",
            "sociologia": "Sociología", "hispanicos": "Estudios Hispánicos",
            "educacion_fisica": "Educación Física – Pedagogía en Educación Física",
            "psicologia": "Psicología", "biologia": "Biología",
            "microbiologia": "Microbiología Industrial", "premedica": "Pre-Médica",
            "biotecnologia": "Biotecnología Industrial", "quimica": "Química",
            "geologia": "Geología", "matematicas": "Matemáticas – Matemática Pura",
            "enfermeria": "Enfermería", "fisica": "Física", "ciencias_marinas": "Ciencias Marinas"
        },
        "COLEGIO DE CIENCIAS AGRÍCOLAS": {
            "agronomia": "Agronomía", "economia_agricola": "Economía Agrícola",
            "horticultura": "Horticultura", "ciencia_animal": "Ciencia Animal",
            "proteccion_cultivos": "Protección de Cultivos", "agronegocios": "Agronegocios"
        },
        "COLEGIO DE INGENIERÍA": {
            "ing_quimica": "Ingeniería Química", "ing_civil": "Ingeniería Civil",
            "ing_computadoras": "Ingeniería de Computadoras", "ing_electrica": "Ingeniería Eléctrica",
            "ing_industrial": "Ingeniería Industrial", "ing_mecanica": "Ingeniería Mecánica",
            "ing_software": "Ingeniería de Software"
        }
    }
    
    # Llenar el diccionario de credenciales
    for colegio, usuario in mapeo_usuarios.items():
        # Usar el primer programa como clave de contraseña (simplificado)
        programa_clave = list(programas_simplificados.get(colegio, {}).keys())[0] if programas_simplificados.get(colegio) else "default"
        
        credenciales[usuario] = {
            'password': programa_clave, # Contraseña simplificada
            'colegio': colegio,
            'programas': programas_simplificados.get(colegio, {})
        }
        
    return credenciales

# ========================================================
# CLASES Y CONFIGURACIÓN DEL AG
# ========================================================

# Listas fijas de salones (tal cual se solicitó)
AE_SALONES_FIJOS = [
    "AE 102", "AE 103", "AE 104", "AE 105", "AE 106", "AE 203C",
    "AE 236", "AE 302", "AE 303", "AE 304", "AE 305", "AE 306",
    "AE 338", "AE 340", "AE 341", "AE 402", "AE 403", "AE 404",
]

MATEMATICAS_SALONES_FIJOS = [
    "M 102", "M 104", "M 105", "M 110", "M 112", "M 203", "M 205", "M 210", 
    "M 213", "M 214", "M 215", "M 220", "M 222", "M 236", "M 238", "M 302", 
    "M 303", "M 304", "M 305", "M 306", "M 311", "M 315", "M 316", "M 317", 
    "M 338", "M 340", "M 341", "M 402", "M 403", "M 404"
]

ARTES_CIENCIAS_SALONES_COMPARTIDOS = [
    "AC 101", "AC 102", "AC 103", "AC 104", "AC 105", "AC 106", "AC 107", "AC 108",
    "AC 201", "AC 202", "AC 203", "AC 204", "AC 205", "AC 206", "AC 207", "AC 208",
    "AC 301", "AC 302", "AC 303", "AC 304", "AC 305", "AC 306", "AC 307", "AC 308",
    "AC 401", "AC 402", "AC 403", "AC 404", "AC 405", "AC 406", "AC 407", "AC 408",
    "LAB 101", "LAB 102", "LAB 103", "LAB 104", "LAB 105", "LAB 106", "LAB 107", "LAB 108"
]

# Sistema de reservas de salones (Simulación de archivo JSON con Streamlit state)
class SistemaReservasSalones:
    def __init__(self, departamento_colegio: str):
        self.departamento_colegio = departamento_colegio
        # Usar st.session_state para simular la persistencia de las reservas.
        if 'reservas_salones' not in st.session_state:
            st.session_state.reservas_salones = {}
        self.reservas = st.session_state.reservas_salones
    
    # Métodos de archivo se simplifican a manipulación de st.session_state
    def cargar_reservas(self):
        # Simula cargar desde archivo al inicio de la sesión
        return st.session_state.reservas_salones
    
    def guardar_reservas(self):
        # Simula guardar en archivo
        st.session_state.reservas_salones = self.reservas
        return True
    
    def a_minutos(self, hhmm): 
        try:
            h, m = map(int, str(hhmm).strip().split(":"))
            return h * 60 + m
        except:
            return 0

    def verificar_disponibilidad(self, salon, dia, hora_inicio, hora_fin, departamento_solicitante) -> Tuple[bool, str | None]:
        inicio_min = self.a_minutos(hora_inicio)
        fin_min = self.a_minutos(hora_fin)
        
        for reserva_info in self.reservas.values():
            if reserva_info.get('salon') == salon and reserva_info.get('dia') == dia:
                res_inicio_min = self.a_minutos(reserva_info['hora_inicio'])
                res_fin_min = self.a_minutos(reserva_info['hora_fin'])
                
                # Conflicto: Si la nueva reserva inicia antes de que la vieja termine Y
                # la nueva reserva termina después de que la vieja inicia.
                if not (fin_min <= res_inicio_min or inicio_min >= res_fin_min):
                    return False, reserva_info.get('departamento', 'Desconocido')
        
        return True, None
    
    def reservar_salon(self, salon, dia, hora_inicio, hora_fin, departamento, programa, curso, profesor):
        # Generar una clave única para la reserva
        clave_reserva = hashlib.sha1(f"{salon}_{dia}_{hora_inicio}_{hora_fin}_{departamento}_{curso}".encode('utf-8')).hexdigest()
        
        self.reservas[clave_reserva] = {
            'salon': salon, 'dia': dia, 'hora_inicio': hora_inicio, 'hora_fin': hora_fin,
            'departamento': departamento, 'programa': programa, 'curso': curso, 
            'profesor': profesor, 'fecha_reserva': datetime.now().isoformat()
        }
        return self.guardar_reservas()
    
    def liberar_reservas_departamento(self, departamento):
        claves_a_eliminar = [k for k, r in self.reservas.items() if r.get('departamento') == departamento]
        for clave in claves_a_eliminar:
            del self.reservas[clave]
        return self.guardar_reservas()
    
    def obtener_reservas_departamento(self, departamento):
        return {k: r for k, r in self.reservas.items() if r.get('departamento') == departamento}

# Funciones auxiliares (mantenidas igual)
def generar_bloques():
    """Genera bloques predefinidos de horas por día para distintos créditos."""
    bloques = []
    id_counter = 1

    # Bloques de 4 créditos (4 días, 1 hora cada día)
    combinaciones_4dias = [
        ["Lu","Ma","Mi","Ju"], ["Lu","Ma","Mi","Vi"], ["Lu","Ma","Ju","Vi"],
        ["Lu","Mi","Ju","Vi"], ["Ma","Mi","Ju","Vi"],
    ]
    for dias in combinaciones_4dias:
        bloques.append({"id": id_counter, "dias": dias, "horas": [1]*4, "creditos": 4})
        id_counter += 1

    # Bloques de 4 créditos (2 días, 2 horas cada día)
    combinaciones_2dias = [
        ["Lu","Mi"], ["Lu","Vi"], ["Ma","Ju"], ["Mi","Vi"],
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
        (["Lu","Mi","Vi"], [2,2,1]), (["Lu","Ma","Mi","Vi"], [1,1,1,2]),
        (["Lu","Ma","Ju","Vi"], [1,1,1,2]), (["Lu","Mi","Ju","Vi"], [1,1,1,2]),
        (["Ma","Mi","Ju","Vi"], [1,1,1,2]), (["Ma","Ju","Vi"], [1.5,1.5,2]),
        (["Lu","Ma","Mi","Ju","Vi"], [1,1,1,1,1]), (["Lu","Ma","Mi"], [2,1,2]),
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
    """Calcula créditos adicionales basados en la tabla de horas de contacto y estudiantes."""
    if horas_contacto not in tabla_creditos:
        return 0
    for minimo, maximo, creditos in tabla_creditos[horas_contacto]:
        if minimo <= estudiantes <= maximo:
            return creditos
    return 0

# =========================================================
# FUNCIONES AUXILIARES GLOBALES (Mantenidas y Refinadas)
# =========================================================

def a_minutos(hhmm) -> int:
    """Convierte una hora HH:MM a minutos desde medianoche."""
    if pd.isna(hhmm): return 0
    try:
        hhmm_str = str(hhmm).strip()
        if not hhmm_str: return 0
        if isinstance(hhmm, datetime):
            hhmm_str = hhmm.strftime("%H:%M")
        h, m = map(int, hhmm_str.split(":"))
        return h * 60 + m
    except:
        return 0 

def minutos_a_hhmm(minutos: int) -> str:
    """Convierte minutos desde medianoche a formato HH:MM."""
    h = minutos // 60
    m = minutos % 60
    return f"{h:02d}:{m:02d}"

# =========================================================
# CLASE DE CONFIGURACIÓN DINÁMICA (Central para el control de usuario)
# =========================================================

class ConfiguracionDinamica:
    """Almacena la configuración de datos y restricciones obtenida desde la UI."""
    def __init__(self, cursos_df: pd.DataFrame, salones: Dict, profesores: Dict, alpha: Dict, reservas: Dict):
        self.cursos_df = cursos_df
        self.salones_info = salones
        self.profesores_info = profesores
        self.restricciones_alpha = alpha
        self.reservas_externas = reservas # Reservas de otros departamentos
        
        self.profesores_unicos = list(profesores.keys())
        self.salones_unicos = list(salones.keys())
        self.dias = ['Lu', 'Ma', 'Mi', 'Ju', 'Vi']
        
        # Generar bloques de tiempo (de 60 min) basado en alpha
        min_inicio = a_minutos(alpha.get('Hora Inicio Institucional', '07:30'))
        max_fin = a_minutos(alpha.get('Hora Fin Institucional', '19:30'))
        
        self.bloques_tiempo = []
        # Generar puntos de inicio en intervalos de 30 minutos, pero clases solo de 60 en 60
        # Simplificación: Asumimos inicio en la hora o media hora.
        for inicio in range(min_inicio, max_fin, 30): 
             # Si el curso más corto es de 1 hora, filtramos luego en la asignación.
             self.bloques_tiempo.append((inicio, inicio + 60))
        
        self.cursos_dict = cursos_df.set_index('ID_Sección').to_dict('index')
        self.cursos_df['Duracion_min'] = self.cursos_df['Duración (horas)'] * 60

# ----------------------------------------------------------------
# Carga de Datos y Mocking 
# ----------------------------------------------------------------

def cargar_datos_mock() -> Tuple[pd.DataFrame, Dict, Dict, Dict, Dict]:
    """Genera datos de cursos, salones, profesores, restricciones alpha y reservas mock."""
    
    # 1. Cursos
    cursos_data = {
        'ID_Sección': ['MATH-3171-001', 'INGE-3015-001', 'FISI-3001-002', 'QUIM-4009-001', 'MATE-3031-001'],
        'Curso': ['Cálculo I', 'Ingeniería', 'Física', 'Química Avanzada', 'Álgebra'],
        'Profesor': ['Dr. Pérez', 'Dra. García', 'Prof. López', 'Dr. Pérez', 'Dra. García'],
        'Estudiantes': [30, 65, 95, 20, 45], 
        'Duración (horas)': [1.5, 2.0, 1.0, 3.0, 1.0],
        'Recurso Requerido': ['Aula Estándar', 'Aula Estándar', 'Aula Grande', 'Laboratorio', 'Aula Estándar'] 
    }
    cursos_df = pd.DataFrame(cursos_data)
    cursos_df['Duración (horas)'] = cursos_df['Duración (horas)'].astype(float)

    # 2. Salones (Unificamos los fijos de Matemáticas y agregamos info)
    salones_info = {
        **{s: {'Capacidad': 35, 'Tipo': 'Aula Estándar', 'Zona': 2} for s in MATEMATICAS_SALONES_FIJOS[:3]},
        'M 205': {'Capacidad': 70, 'Tipo': 'Aula Estándar', 'Zona': 2},
        'AC 201': {'Capacidad': 100, 'Tipo': 'Aula Grande', 'Zona': 1},
        'LAB 101': {'Capacidad': 25, 'Tipo': 'Laboratorio', 'Zona': 3},
    }

    # 3. Profesores 
    profesores_info = {
        'Dr. Pérez': {'Carga Min': 6, 'Carga Max': 12, 'No Disponible': [('Ma', '10:30', '12:30')], 'C2 (Días Deseados)': ['Lu', 'Mi', 'Vi']},
        'Dra. García': {'Carga Min': 9, 'Carga Max': 15, 'No Disponible': [('Vi', '15:30', '18:30')], 'C2 (Días Deseados)': ['Lu', 'Ma', 'Mi', 'Ju']},
        'Prof. López': {'Carga Min': 9, 'Carga Max': 12, 'No Disponible': [], 'C2 (Días Deseados)': ['Ma', 'Ju']},
    }

    # 4. Restricciones Institucionales (Alpha)
    restricciones_alpha = {
        'Hora Inicio Institucional': '07:30', 'Hora Fin Institucional': '19:30',
        'Bloqueos por Zona': { 1: [('Ma', '10:30', '12:30')], 2: [('Mi', '10:00', '12:00')] },
        'Hora Limite 3 Horas': '15:30' 
    }
    
    # 5. Reservas Externas Mock (Por ejemplo, del Depto. de Física en un salón compartido)
    reservas_mock = {
        'reserva_1': {'salon': 'AC 201', 'dia': 'Lu', 'hora_inicio': '08:30', 'hora_fin': '10:00', 'departamento': 'Física'}
    }
    
    return cursos_df, salones_info, profesores_info, restricciones_alpha, reservas_mock

# ----------------------------------------------------------------
# Algoritmo Genético: Funciones (Mantenidas y dependientes de Config)
# ----------------------------------------------------------------

def inicializar_cromosoma(config: ConfiguracionDinamica) -> List[Tuple[str, str, str, str, str]]:
    """Genera un cromosoma inicial (un horario) aleatorio basado en la configuración dinámica."""
    cromosoma = []
    max_minutos_fin = a_minutos(config.restricciones_alpha.get('Hora Fin Institucional', '19:30'))
    
    for index, row in config.cursos_df.iterrows():
        profesor = random.choice(config.profesores_unicos)
        
        # Filtro inicial de salones por tipo de recurso (para mejorar el inicio)
        recurso_req = row.get('Recurso Requerido', 'Aula Estándar')
        salones_filtrados = [s for s, info in config.salones_info.items() if info.get('Tipo') == recurso_req]
        salon = random.choice(salones_filtrados) if salones_filtrados else random.choice(config.salones_unicos)
        
        dia = random.choice(config.dias)
        
        duracion_min = int(row['Duración (horas)'] * 60)
        
        # Filtrar bloques de tiempo por duración y fin institucional
        bloques_compatibles = [
            b for b in config.bloques_tiempo 
            if b[0] + duracion_min <= max_minutos_fin
        ]
        
        hora_inicio = '07:30' # Fallback
        if bloques_compatibles:
            inicio_minutos, _ = random.choice(bloques_compatibles)
            hora_inicio = minutos_a_hhmm(inicio_minutos)
        
        cromosoma.append((row['ID_Sección'], profesor, salon, dia, hora_inicio))
    
    return cromosoma

def calcular_penalizacion_fuertes(cromosoma: List[Tuple], config: ConfiguracionDinamica) -> float:
    """Evalúa las Restricciones Fuertes (Rf1-Rf6, Alpha, y Reservas Externas) usando la configuración dinámica."""
    penalizacion = 0.0
    PENALTY_RF = 1000000.0 

    horario_salones: Dict[Tuple[str, int, str], str] = {}
    horario_profesores: Dict[Tuple[str, int, str], str] = {}

    alpha = config.restricciones_alpha
    min_inst = a_minutos(alpha.get('Hora Inicio Institucional', '07:30'))
    max_inst = a_minutos(alpha.get('Hora Fin Institucional', '19:30'))
    hora_limite_3h = a_minutos(alpha.get('Hora Limite 3 Horas', '15:30'))
    bloqueos_institucionales = alpha.get('Bloqueos por Zona', {})
    
    # 1. Integrar Reservas Externas como bloqueos duros en el horario de salones
    for res_id, res_info in config.reservas_externas.items():
        salon = res_info['salon']
        dia = res_info['dia']
        inicio_min = a_minutos(res_info['hora_inicio'])
        fin_min = a_minutos(res_info['hora_fin'])
        
        for t in range(inicio_min, fin_min, 30):
            bloque_tiempo_clave = t // 30 
            clave_salon = (dia, bloque_tiempo_clave, salon)
            horario_salones[clave_salon] = f"RESERVA_EXTERNA_{res_id}"


    for (id_seccion, profesor, salon, dia, hora_inicio_str) in cromosoma:
        
        curso = config.cursos_dict.get(id_seccion)
        if not curso: continue

        duracion_min = int(curso['Duración (horas)'] * 60)
        hora_inicio_min = a_minutos(hora_inicio_str)
        hora_fin_min = hora_inicio_min + duracion_min
        
        salon_info = config.salones_info.get(salon, {})
        profesor_info = config.profesores_info.get(profesor, {})

        # --- RESTRICCIONES DE DISPONIBILIDAD (Alpha) ---
        
        # 1. Rango horario institucional (Alpha 1)
        if hora_inicio_min < min_inst or hora_fin_min > max_inst:
            penalizacion += PENALTY_RF * 1.5 
        
        # 2. Horarios Prohibidos (Alpha 2 - Institucional)
        # Nota: Convertimos la zona a string ya que la carga desde Streamlit puede ser string.
        zona = salon_info.get('Zona', 1)
        bloqueos_zona = bloqueos_institucionales.get(str(zona), []) 
        for (dia_b, inicio_b_str, fin_b_str) in bloqueos_zona:
            if dia_b == dia:
                inicio_b_min = a_minutos(inicio_b_str)
                fin_b_min = a_minutos(fin_b_str)
                if hora_inicio_min < fin_b_min and inicio_b_min < hora_fin_min:
                    penalizacion += PENALTY_RF 

        # 3. Disponibilidad del Profesor (Alpha 4)
        bloqueos_prof = profesor_info.get('No Disponible', [])
        for (dia_b, inicio_b_str, fin_b_str) in bloqueos_prof:
            if dia_b == dia:
                inicio_b_min = a_minutos(inicio_b_str)
                fin_b_min = a_minutos(fin_b_str)
                if hora_inicio_min < fin_b_min and inicio_b_min < hora_fin_min:
                    penalizacion += PENALTY_RF 

        # 4. Restricción especial de 3 horas consecutivas (Alpha 3)
        if duracion_min > 120 and hora_inicio_min < hora_limite_3h:
             penalizacion += PENALTY_RF 

        # --- Rf3: Inexistencia de Conflicto de Espacio (Incluye Reservas Externas) ---
        for t in range(hora_inicio_min, hora_fin_min, 30):
            bloque_tiempo_clave = t // 30 
            clave_salon = (dia, bloque_tiempo_clave, salon)
            
            if clave_salon in horario_salones:
                penalizacion += PENALTY_RF 
                # Salimos para no contar el mismo conflicto muchas veces
                break 
            else:
                horario_salones[clave_salon] = id_seccion

        # --- Rf2: Inexistencia de Conflicto Docente ---
        for t in range(hora_inicio_min, hora_fin_min, 30):
            bloque_tiempo_clave = t // 30 
            clave_profesor = (dia, bloque_tiempo_clave, profesor)
            
            if clave_profesor in horario_profesores:
                penalizacion += PENALTY_RF 
                break 
            else:
                horario_profesores[clave_profesor] = id_seccion
        
        # --- Rf4: Suficiencia de Capacidad ---
        capacidad_salon = salon_info.get('Capacidad', 0)
        estudiantes = curso.get('Estudiantes', 0)
        if capacidad_salon < estudiantes:
            penalizacion += PENALTY_RF * 0.5
            
        # --- Rf5: Compatibilidad de Tipo de Recurso ---
        recurso_req = curso.get('Recurso Requerido', 'Aula Estándar')
        tipo_salon = salon_info.get('Tipo', 'Aula Estándar')
        if recurso_req != tipo_salon:
            penalizacion += PENALTY_RF * 0.75
            
    # --- Rf6: Límites de Carga Docente (chequeo final) ---
    carga_por_profesor: Dict[str, float] = {}
    for (id_seccion, profesor, _, _, _) in cromosoma:
        duracion_horas = config.cursos_dict.get(id_seccion, {}).get('Duración (horas)', 0.0)
        carga_por_profesor[profesor] = carga_por_profesor.get(profesor, 0.0) + duracion_horas
        
    for profesor, carga in carga_por_profesor.items():
        prof_info = config.profesores_info.get(profesor, {})
        carga_min = prof_info.get('Carga Min', 0)
        carga_max = prof_info.get('Carga Max', float('inf'))
        
        if carga < carga_min or carga > carga_max:
            penalizacion += PENALTY_RF * 0.3 

    return penalizacion

# La función calcular_penalizacion_suave (Rs1-Rs4) se mantiene igual
def calcular_penalizacion_suave(cromosoma: List[Tuple], config: ConfiguracionDinamica) -> float:
    """Evalúa las Restricciones Suaves (Rs1-Rs4) usando la configuración dinámica."""
    penalizacion = 0.0
    PENALTY_RS_PREF = 100.0  
    PENALTY_RS_HUECO = 500.0 
    PENALTY_RS_CAPACIDAD = 5.0 
    PENALTY_RS_NO_DESEABLE = 50.0 

    prof_horarios: Dict[str, Dict[str, List[int]]] = {} 

    for (id_seccion, profesor, salon, dia, hora_inicio_str) in cromosoma:
        curso = config.cursos_dict.get(id_seccion)
        if not curso: continue
        
        duracion_min = int(curso['Duración (horas)'] * 60)
        hora_inicio_min = a_minutos(hora_inicio_str)
        hora_fin_min = hora_inicio_min + duracion_min
        
        prof_info = config.profesores_info.get(profesor, {})
        salon_info = config.salones_info.get(salon, {})
        
        # Rs1: Satisfacción de Preferencias Horarias (Días Deseados)
        dias_deseados = prof_info.get('C2 (Días Deseados)', config.dias)
        if dia not in dias_deseados:
            penalizacion += PENALTY_RS_PREF

        # Rs3: Uso Eficiente de la Capacidad (Desperdicio)
        capacidad_salon = salon_info.get('Capacidad', 1)
        estudiantes = curso.get('Estudiantes', 1)
        desperdicio = capacidad_salon - estudiantes
        if desperdicio > 0 and capacidad_salon > 0:
            # Penalización proporcional al desperdicio
            penalizacion += (desperdicio / capacidad_salon) * PENALTY_RS_CAPACIDAD

        # Rs4: Distribución Balanceada de Clases (Bloques No Deseables)
        hora_no_deseable_temp = a_minutos('08:30')
        hora_no_deseable_tarde = a_minutos('18:30')
        
        if hora_inicio_min < hora_no_deseable_temp or hora_fin_min > hora_no_deseable_tarde:
            penalizacion += PENALTY_RS_NO_DESEABLE
            
        # Acumular horario para chequeo de Compactación (Rs2)
        if profesor not in prof_horarios:
            prof_horarios[profesor] = {d: [] for d in config.dias}
        prof_horarios[profesor][dia].append((hora_inicio_min, hora_fin_min))

    # Rs2: Compactación del Horario (Chequear 'huecos')
    for _, horario_dias in prof_horarios.items():
        for _, bloques in horario_dias.items():
            if len(bloques) > 1:
                bloques.sort(key=lambda x: x[0]) 
                for i in range(len(bloques) - 1):
                    fin_clase_anterior = bloques[i][1]
                    inicio_clase_siguiente = bloques[i+1][0]
                    
                    hueco_minutos = inicio_clase_siguiente - fin_clase_anterior
                    
                    if hueco_minutos > 90: # Hueco grande (más de 90 minutos)
                        penalizacion += PENALTY_RS_HUECO * (hueco_minutos / 60)
    
    return penalizacion

def calcular_fitness_simulada(cromosoma: List[Tuple], config: ConfiguracionDinamica) -> float:
    """Calcula el fitness (aptitud) de un cromosoma. Un fitness más BAJO es mejor."""
    
    penalizacion_fuerte = calcular_penalizacion_fuertes(cromosoma, config)
    
    if penalizacion_fuerte > 0:
        return penalizacion_fuerte 
    
    penalizacion_suave = calcular_penalizacion_suave(cromosoma, config)
    
    return penalizacion_fuerte + penalizacion_suave

def mutar_cromosoma(cromosoma: List[Tuple], config: ConfiguracionDinamica, tasa_mutacion: float) -> List[Tuple]:
    """Aplica mutaciones aleatorias a un cromosoma."""
    nuevo_cromosoma = []
    max_minutos_fin = a_minutos(config.restricciones_alpha.get('Hora Fin Institucional', '19:30'))

    for gen in cromosoma:
        (id_seccion, profesor, salon, dia, hora_inicio_str) = gen
        
        if random.random() < tasa_mutacion:
            mutacion_tipo = random.choice(['profesor', 'salon', 'dia', 'hora'])
            
            if mutacion_tipo == 'profesor' and config.profesores_unicos:
                nuevo_profesor = random.choice(config.profesores_unicos)
                nuevo_cromosoma.append((id_seccion, nuevo_profesor, salon, dia, hora_inicio_str))
            
            elif mutacion_tipo == 'salon' and config.salones_unicos:
                nuevo_salon = random.choice(config.salones_unicos)
                nuevo_cromosoma.append((id_seccion, profesor, nuevo_salon, dia, hora_inicio_str))
            
            elif mutacion_tipo == 'dia':
                nuevo_dia = random.choice(config.dias)
                nuevo_cromosoma.append((id_seccion, profesor, salon, nuevo_dia, hora_inicio_str))
            
            elif mutacion_tipo == 'hora':
                curso = config.cursos_dict.get(id_seccion)
                if curso:
                    duracion_min = int(curso['Duración (horas)'] * 60)
                    # Filtramos bloques de inicio que permitan la duración
                    bloques_compatibles = [
                        b[0] for b in config.bloques_tiempo 
                        if b[0] + duracion_min <= max_minutos_fin
                    ]
                    
                    if bloques_compatibles:
                        inicio_minutos = random.choice(bloques_compatibles)
                        nueva_hora_inicio = minutos_a_hhmm(inicio_minutos)
                        nuevo_cromosoma.append((id_seccion, profesor, salon, dia, nueva_hora_inicio))
                    else:
                        nuevo_cromosoma.append(gen)
                else:
                    nuevo_cromosoma.append(gen)
        else:
            nuevo_cromosoma.append(gen)
            
    return nuevo_cromosoma

def cruzar_cromosomas(padre1: List[Tuple], padre2: List[Tuple]) -> Tuple[List[Tuple], List[Tuple]]:
    """Aplica cruce de un punto (one-point crossover) a dos cromosomas."""
    punto_cruce = random.randint(1, len(padre1) - 1)
    
    hijo1 = padre1[:punto_cruce] + padre2[punto_cruce:]
    hijo2 = padre2[:punto_cruce] + padre1[punto_cruce:]
    
    return hijo1, hijo2

def buscar_mejor_horario(config: ConfiguracionDinamica) -> Tuple[List[Tuple], float, pd.DataFrame]:
    """Función principal del Algoritmo Genético."""
    
    # Parámetros del GA 
    TAMANO_POBLACION = 50
    TASA_CRUCE = 0.8
    TASA_MUTACION = 0.2
    MAX_ITERACIONES = 500
    
    poblacion = [inicializar_cromosoma(config) for _ in range(TAMANO_POBLACION)]
    
    mejor_cromosoma = None
    mejor_fitness = float('inf')
    
    for generacion in range(MAX_ITERACIONES):
        
        fitness_poblacion = []
        for cromosoma in poblacion:
            fitness = calcular_fitness_simulada(cromosoma, config)
            fitness_poblacion.append((cromosoma, fitness))
            
            if fitness < mejor_fitness:
                mejor_fitness = fitness
                mejor_cromosoma = cromosoma
                
        if mejor_fitness == 0.0 and generacion > 100:
            break
        
        def seleccionar_por_torneo(pop_fitness: List[Tuple], k=5):
            competidores = random.sample(pop_fitness, min(k, len(pop_fitness)))
            return min(competidores, key=lambda x: x[1])[0] 

        nueva_poblacion = []
        # Elitismo: Mantener el mejor de la generación anterior
        if mejor_cromosoma:
            nueva_poblacion.append(mejor_cromosoma)

        while len(nueva_poblacion) < TAMANO_POBLACION:
            padre1 = seleccionar_por_torneo(fitness_poblacion)
            padre2 = seleccionar_por_torneo(fitness_poblacion)
            
            hijo1, hijo2 = padre1, padre2
            
            if random.random() < TASA_CRUCE:
                hijo1, hijo2 = cruzar_cromosomas(padre1, padre2)
            
            hijo1_mutado = mutar_cromosoma(hijo1, config, TASA_MUTACION)
            hijo2_mutado = mutar_cromosoma(hijo2, config, TASA_MUTACION)

            nueva_poblacion.extend([hijo1_mutado, hijo2_mutado])

        poblacion = nueva_poblacion[:TAMANO_POBLACION]
        
    df_horario = None
    final_score = 0.0
    
    if mejor_cromosoma:
        final_score = calcular_fitness_simulada(mejor_cromosoma, config)
        
        df_horario = pd.DataFrame(mejor_cromosoma, columns=['ID_Sección', 'Profesor', 'Salón', 'Día', 'Hora_Inicio'])
        df_horario = df_horario.merge(config.cursos_df[['ID_Sección', 'Curso', 'Duración (horas)', 'Estudiantes']], on='ID_Sección', how='left')
        
        df_horario['Hora_Inicio_min'] = df_horario['Hora_Inicio'].apply(a_minutos)
        df_horario['Hora_Fin_min'] = df_horario['Hora_Inicio_min'] + (df_horario['Duración (horas)'] * 60).astype(int)
        df_horario['Hora_Fin'] = df_horario['Hora_Fin_min'].apply(minutos_a_hhmm)

        if calcular_penalizacion_fuertes(mejor_cromosoma, config) > 0:
            st.warning(f"⚠️ El mejor horario encontrado NO CUMPLE las Restricciones Fuertes (Penalización: {calcular_penalizacion_fuertes(mejor_cromosoma, config):.0f}).")
            df_horario = None
            
    return mejor_cromosoma, final_score, df_horario


# ----------------------------------------------------------------
# Streamlit UI
# ----------------------------------------------------------------

def ui_configuracion_profesores(profesores_df_base: pd.DataFrame) -> Dict:
    """Configuración dinámica de preferencias de profesores (Rs1, Rf6, Alpha)."""
    st.subheader("👨‍🏫 Preferencias y Carga Docente")
    st.info("Ajuste los límites de carga (Rf6), días deseados (Rs1) y no disponibilidad (Alpha) para cada profesor.")
    
    profesores_dict: Dict[str, Dict] = {}
    
    # Inicializar valores por defecto (ejemplo: 9-12 horas)
    default_cargas = {p: {'Carga Min': 9, 'Carga Max': 12, 'No Disponible': [], 'C2 (Días Deseados)': ['Lu', 'Ma', 'Mi', 'Ju']} 
                      for p in profesores_df_base['Profesor'].unique()}
    
    for profesor in profesores_df_base['Profesor'].unique():
        defaults = default_cargas.get(profesor, {})
        
        with st.expander(f"Profesor: {profesor}"):
            # Rf6: Límites de Carga Docente
            col1, col2 = st.columns(2)
            carga_min = col1.number_input(f"Carga Mínima (Horas/Sem.)", min_value=0, max_value=20, value=defaults.get('Carga Min', 9), key=f'min_{profesor}')
            carga_max = col2.number_input(f"Carga Máxima (Horas/Sem.)", min_value=carga_min, max_value=20, value=defaults.get('Carga Max', 12), key=f'max_{profesor}')
            
            # Rs1: Días Deseados (Preferencia Suave)
            dias_deseados = st.multiselect("Días Deseados (Rs1)", 
                                           ['Lu', 'Ma', 'Mi', 'Ju', 'Vi'], 
                                           default=defaults.get('C2 (Días Deseados)', ['Lu', 'Ma', 'Mi', 'Ju']),
                                           key=f'dias_{profesor}')
            
            # Alpha 4: No Disponibilidad del Profesor (Restricción Fuerte)
            st.markdown("##### Bloques de Tiempo No Disponibles (Alpha)")
            num_bloqueos = st.number_input("Número de Bloqueos No Disponibles", min_value=0, max_value=3, value=len(defaults.get('No Disponible', [])), key=f'num_bl_{profesor}')
            
            bloqueos_list = []
            for i in range(num_bloqueos):
                default_bl = defaults.get('No Disponible', [('', '10:30', '12:30')])[i] if i < len(defaults.get('No Disponible', [])) else ('Lu', '10:30', '12:30')
                col_b1, col_b2, col_b3 = st.columns(3)
                dia_b = col_b1.selectbox(f"Día {i+1}", ['Lu', 'Ma', 'Mi', 'Ju', 'Vi'], index=['Lu', 'Ma', 'Mi', 'Ju', 'Vi'].index(default_bl[0]) if default_bl[0] in ['Lu', 'Ma', 'Mi', 'Ju', 'Vi'] else 0, key=f'b_dia_{profesor}_{i}')
                hora_in = col_b2.text_input(f"Inicio (HH:MM) {i+1}", value=default_bl[1], key=f'b_in_{profesor}_{i}')
                hora_fin = col_b3.text_input(f"Fin (HH:MM) {i+1}", value=default_bl[2], key=f'b_fin_{profesor}_{i}')
                bloqueos_list.append((dia_b, hora_in, hora_fin))
                
            profesores_dict[profesor] = {
                'Carga Min': carga_min,
                'Carga Max': carga_max,
                'C2 (Días Deseados)': dias_deseados,
                'No Disponible': bloqueos_list
            }
            
    return profesores_dict

def ui_configuracion_salones(departamento_colegio: str) -> Dict:
    """Configuración dinámica de salones (Rf3, Rf4, Rf5) según el departamento logueado."""
    st.subheader(f"🏢 Salones Disponibles ({departamento_colegio})")
    
    # 1. Definir la lista base de salones según el departamento logueado
    if "ADMINISTRACIÓN DE EMPRESAS" in departamento_colegio:
        salones_base_list = AE_SALONES_FIJOS
        zona_defecto = 1
    elif "MATEMÁTICAS" in departamento_colegio:
        salones_base_list = MATEMATICAS_SALONES_FIJOS
        zona_defecto = 2
    elif "ARTES Y CIENCIAS" in departamento_colegio:
        # Artes y Ciencias puede acceder a compartidos, pero mostramos un subconjunto para no saturar
        salones_base_list = ARTES_CIENCIAS_SALONES_COMPARTIDOS[:10]
        zona_defecto = 3
    else:
        # Otros colegios/departamentos o mock data
        salones_base_list = ['A-101 (Default)', 'L-210 (Default)']
        zona_defecto = 4

    st.info(f"Salones para configurar: {', '.join(salones_base_list[:3])}... (total {len(salones_base_list)})")
    
    salones_dict: Dict[str, Dict] = {}
    
    for salon in salones_base_list:
        # Mock de valores por defecto para evitar claves repetidas
        cap_def = random.randint(30, 100)
        tipo_def = 'Aula Estándar' if 'LAB' not in salon else 'Laboratorio'
        
        with st.expander(f"Salón: {salon}", expanded=False):
            col1, col2, col3 = st.columns(3)
            cap = col1.number_input("Capacidad (Rf4)", min_value=1, value=cap_def, key=f'cap_{salon}')
            tipo = col2.selectbox("Tipo de Recurso (Rf5)", 
                                  ['Aula Estándar', 'Laboratorio', 'Aula Grande'], 
                                  index=0 if tipo_def == 'Aula Estándar' else 1,
                                  key=f'tipo_{salon}')
            zona = col3.number_input("Zona", min_value=1, max_value=5, value=zona_defecto, key=f'zona_{salon}')
            
            salones_dict[salon] = {
                'Capacidad': cap,
                'Tipo': tipo,
                'Zona': zona
            }
            
    return salones_dict

def ui_restricciones_alpha() -> Dict:
    """Configuración dinámica de restricciones institucionales (Alpha)."""
    st.subheader("⏱️ Restricciones Institucionales (Alpha)")
    st.info("Ajuste los límites horarios generales y los bloqueos fijos.")
    
    alpha_config: Dict[str, Any] = {}
    
    col_a1, col_a2 = st.columns(2)
    alpha_config['Hora Inicio Institucional'] = col_a1.text_input("Rango: Hora de Inicio", value='07:30', key='alpha_h_in')
    alpha_config['Hora Fin Institucional'] = col_a2.text_input("Rango: Hora de Fin", value='19:30', key='alpha_h_fin')
    
    alpha_config['Hora Limite 3 Horas'] = st.text_input("3h Consecutivas solo después de (HH:MM)", value='15:30', key='alpha_h_limit')
    
    st.markdown("##### Bloqueos Horarios Fijos por Zona (Alpha 2)")
    num_zonas = 3
    bloqueos_por_zona: Dict[str, List[Tuple[str, str, str]]] = {}

    for z in range(1, num_zonas + 1):
        st.caption(f"Bloqueos para Zona {z} (Ej. Reuniones Fijas)")
        num_bloqueos_z = st.number_input(f"Número de Bloqueos Fijos en Zona {z}", min_value=0, max_value=2, value=1 if z == 1 else 0, key=f'num_bl_z{z}')
        
        bloqueos_list = []
        for i in range(num_bloqueos_z):
            col_b1, col_b2, col_b3 = st.columns(3)
            dia_b = col_b1.selectbox(f"Día Zona {z}-{i+1}", ['Lu', 'Ma', 'Mi', 'Ju', 'Vi'], key=f'zb_dia_{z}_{i}', index=1)
            hora_in = col_b2.text_input(f"Inicio (HH:MM) Zona {z}-{i+1}", value='10:30', key=f'zb_in_{z}_{i}')
            hora_fin = col_b3.text_input(f"Fin (HH:MM) Zona {z}-{i+1}", value='12:30', key=f'zb_fin_{z}_{i}')
            bloqueos_list.append((dia_b, hora_in, hora_fin))
            
        bloqueos_por_zona[str(z)] = bloqueos_list
    
    alpha_config['Bloqueos por Zona'] = bloqueos_por_zona
    return alpha_config

def mostrar_tabs_horario_mejoradas(df_horario: pd.DataFrame):
    """Muestra el horario en diferentes vistas con visualizaciones de Plotly."""
    
    if df_horario is None or df_horario.empty:
        st.error("No hay horario válido para mostrar.")
        return

    tab_general, tab_profesor, tab_salon = st.tabs(["Vista General", "Horario por Profesor", "Horario por Salón"])

    # 1. Vista General (Tabla y Gráfico)
    with tab_general:
        st.dataframe(df_horario.sort_values(['Día', 'Hora_Inicio_min']), use_container_width=True)
        st.markdown("---")
        df_plot = df_horario.copy()
        
        # Gráfico Timeline
        fig = px.timeline(df_plot, 
                          x_start="Hora_Inicio", 
                          x_end="Hora_Fin", 
                          y="Día", 
                          color="Profesor",
                          text="Curso",
                          hover_data=['Salón', 'Estudiantes'],
                          title="Distribución Horaria General")
        fig.update_yaxes(categoryorder="array", categoryarray=['Lu', 'Ma', 'Mi', 'Ju', 'Vi'])
        fig.update_xaxes(tickformat="%H:%M") 
        st.plotly_chart(fig, use_container_width=True)

    # 2. Horario por Profesor
    with tab_profesor:
        profesor_seleccionado = st.selectbox("Seleccionar Profesor", df_horario['Profesor'].unique(), key="sel_prof_tab")
        df_prof = df_horario[df_horario['Profesor'] == profesor_seleccionado].sort_values(['Día', 'Hora_Inicio_min'])
        st.dataframe(df_prof[['Día', 'Hora_Inicio', 'Hora_Fin', 'Curso', 'Salón', 'Estudiantes', 'Duración (horas)']], use_container_width=True)
        
        carga_total = df_prof['Duración (horas)'].sum()
        st.info(f"Carga Total Asignada: {carga_total:.1f} horas/semana.")
        
        fig_prof = px.timeline(df_prof, 
                               x_start="Hora_Inicio", 
                               x_end="Hora_Fin", 
                               y="Día", 
                               color="Curso",
                               title=f"Horario Compactado de {profesor_seleccionado}")
        fig_prof.update_yaxes(categoryorder="array", categoryarray=['Lu', 'Ma', 'Mi', 'Ju', 'Vi'])
        fig_prof.update_xaxes(tickformat="%H:%M") 
        st.plotly_chart(fig_prof, use_container_width=True)


    # 3. Horario por Salón (Verificación de Rf3)
    with tab_salon:
        salon_seleccionado = st.selectbox("Seleccionar Salón", df_horario['Salón'].unique(), key="sel_salon_tab")
        df_salon = df_horario[df_horario['Salón'] == salon_seleccionado].sort_values(['Día', 'Hora_Inicio_min'])
        st.dataframe(df_salon[['Día', 'Hora_Inicio', 'Hora_Fin', 'Curso', 'Profesor', 'Estudiantes']], use_container_width=True)
        
        fig_salon = px.timeline(df_salon, 
                                x_start="Hora_Inicio", 
                                x_end="Hora_Fin", 
                                y="Día", 
                                color="Curso",
                                title=f"Uso del Salón {salon_seleccionado} (Verificación Rf3)")
        fig_salon.update_yaxes(categoryorder="array", categoryarray=['Lu', 'Ma', 'Mi', 'Ju', 'Vi'])
        fig_salon.update_xaxes(tickformat="%H:%M") 
        st.plotly_chart(fig_salon, use_container_width=True)

def login():
    """Lógica de autenticación simplificada."""
    
    st.sidebar.header("🔑 Acceso al Sistema")
    
    col_u, col_p = st.sidebar.columns(2)
    username = col_u.text_input("Usuario", key="user_input")
    password = col_p.text_input("Contraseña", type="password", key="pass_input")
    
    credenciales = generar_credenciales_simplificadas()
    
    if st.sidebar.button("Iniciar Sesión"):
        if username in credenciales and credenciales[username]['password'] == password:
            st.session_state['logged_in'] = True
            st.session_state['user_info'] = credenciales[username]
            st.session_state['departamento_colegio'] = credenciales[username]['colegio']
            st.session_state['reservas_sistema'] = SistemaReservasSalones(credenciales[username]['colegio'])
            st.sidebar.success(f"¡Bienvenido/a, {credenciales[username]['colegio']}!")
            st.rerun()
        else:
            st.sidebar.error("Usuario o contraseña incorrectos.")
    
    # Mostrar la tabla de ayuda para el mock
    with st.sidebar.expander("Ayuda de Credenciales (Mock)"):
        st.markdown("Use: `admin_empresas` / `contabilidad`")
        st.markdown("O: `matematicas` / `mate_aplicada`")
        st.markdown("O: `artes_ciencias` / `literatura`")


def main():
    st.set_page_config(layout="wide", page_title="Optimizador Dinámico de Horarios Académicos con GA")
    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'cursos_df' not in st.session_state:
        st.session_state.cursos_df = pd.DataFrame()
        
    if not st.session_state.logged_in:
        login()
        st.title("Sistema de Generación de Horarios")
        st.warning("Por favor, inicie sesión en la barra lateral para acceder.")
        return

    # --- Una vez autenticado ---
    departamento = st.session_state['departamento_colegio']
    st.title(f"Sistema de Horarios: {departamento}")
    st.markdown("Utilice la barra lateral para cargar los datos y configurar las restricciones dinámicas.")

    # --------------------------------------------------------
    # Barra Lateral (Configuración Dinámica)
    # --------------------------------------------------------
    with st.sidebar:
        st.header(f"Configuración de {departamento}")
        
        # 1. Carga de Cursos
        uploaded_file = st.file_uploader("Cargar Archivo CSV de Cursos", type="csv")
        
        if st.button("Cargar Mock Data de Matemáticas (Ejemplo)", key="btn_cargar_mock"):
            cursos_df, salones_mock, profesores_mock, alpha_mock, reservas_mock = cargar_datos_mock()
            st.session_state.cursos_df = cursos_df
            st.session_state.salones_base = salones_mock # Solo para inicializar la UI
            st.session_state.profesores_base = profesores_mock
            st.session_state.alpha_base = alpha_mock
            st.session_state.reservas_externas = reservas_mock
            st.success("✅ Datos Mock cargados y listos para configurar.")
            
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.session_state.cursos_df = df
                st.session_state.reservas_externas = {} # Limpiar reservas al cargar nuevos datos
                st.success("✅ Archivo de cursos cargado. ¡Configure las restricciones!")
            except Exception as e:
                st.error(f"Error al leer el archivo: {e}")
                
        # --------------------------------------------------------
        # UI de Configuración de Restricciones (si hay datos)
        # --------------------------------------------------------
        cursos_df = st.session_state.get('cursos_df')
        if not cursos_df.empty:
            st.markdown("---")
            st.markdown("## 🛠️ Restricciones y Preferencias")
            
            # --- Tablas de configuración dinámicas ---
            # Las restricciones de Salones dependen del Departamento (a diferencia de la versión anterior)
            st.session_state.salones_final = ui_configuracion_salones(departamento)
            st.session_state.profesores_final = ui_configuracion_profesores(cursos_df[['Profesor']].drop_duplicates())
            st.session_state.alpha_final = ui_restricciones_alpha()
            
            # Mostrar Reservas Externas (simulando que Artes y Ciencias reservó un salón)
            if st.session_state.get('reservas_externas'):
                 st.markdown("---")
                 st.subheader("⚠️ Bloqueos Externos")
                 st.warning(f"Existen {len(st.session_state.reservas_externas)} reservas externas que el algoritmo debe respetar.")
            
            # 5. Crear la configuración final para el GA
            st.session_state.config = ConfiguracionDinamica(
                st.session_state.cursos_df,
                st.session_state.salones_final,
                st.session_state.profesores_final,
                st.session_state.alpha_final,
                st.session_state.reservas_externas # Pasa las reservas externas como RF dura
            )
            st.success("Todas las restricciones y preferencias dinámicas cargadas.")

    # --------------------------------------------------------
    # Contenido Principal (Ejecución del GA)
    # --------------------------------------------------------
    
    config = st.session_state.get('config')
    
    if config and not config.cursos_df.empty:
        st.markdown("---")
        st.markdown("## Ejecución del Algoritmo Genético")
        st.markdown("El algoritmo utilizará **TODAS** las restricciones y preferencias que usted configuró en la barra lateral.")
        
        if st.button("🚀 Generar Horario Optimizado", type="primary", key="btn_generar_horario_simple"):
            with st.spinner("Generando horario optimizado (Simulación de 500 iteraciones)..."):
                mejor, score, df_horario = buscar_mejor_horario(config) 
                
                if df_horario is None or df_horario.empty:
                    st.error("❌ No se pudo generar un horario válido que cumpla todas las Restricciones Fuertes. Ajuste las restricciones o pruebe con menos cursos.")
                    st.session_state.horario_generado = False
                else:
                    st.session_state.horario_generado = True
                    st.session_state.horario_optimo_df = df_horario
                    
                    st.success(f"✅ Horario generado. Puntuación de Fitness (Soft Constraints): {score:.2f} (Restricciones Fuertes Cumplidas)")
                    st.balloons()
            
    elif st.session_state.get('cursos_df').empty:
        st.warning("⚠️ Por favor, cargue el archivo CSV o la 'Mock Data' en la barra lateral para comenzar.")
    
    # Sección de resultados
    if st.session_state.get('horario_generado'):
        df_horario = st.session_state['horario_optimo_df']
        st.markdown("---")
        st.markdown("## 📊 Resultados del Algoritmo Genético")
        mostrar_tabs_horario_mejoradas(df_horario)


if __name__ == "__main__":
    main()
