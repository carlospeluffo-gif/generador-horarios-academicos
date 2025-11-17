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
import hashlib

# ========================================================
# FUNCIONES AUXILIARES GLOBALES
# ========================================================

def a_minutos(hhmm):
    """Convierte una hora HH:MM a minutos desde medianoche."""
    if pd.isna(hhmm): return 0
    try:
        # Asegurarse de que el input es una cadena antes de split
        hhmm_str = str(hhmm).strip()
        if not hhmm_str: return 0
        
        # Manejar el caso de 'datetime.time' si entra
        if isinstance(hhmm, datetime):
            hhmm_str = hhmm.strftime("%H:%M")
        elif isinstance(hhmm, time.struct_time):
             hhmm_str = f"{hhmm.tm_hour:02d}:{hhmm.tm_min:02d}"
        
        h, m = map(int, hhmm_str.split(":"))
        return h * 60 + m
    except:
        return 0 
        
# ========================================================
# SISTEMA DE AUTENTICACIÓN Y CREDENCIALES SIMPLIFICADO
# (Tomado de app (9).py)
# ========================================================

def generar_credenciales_simplificadas():
    """Genera el diccionario de credenciales simplificadas sin tildes ni caracteres especiales"""
    credenciales = {}
    
    # Mapear colegios a usuarios simplificados (SIN TILDES NI ESPACIOS)
    mapeo_usuarios = {
        "COLEGIO DE ADMINISTRACIÓN DE EMPRESAS": "admin_empresas",
        "COLEGIO DE ARTES Y CIENCIAS": "artes_ciencias", 
        "COLEGIO DE CIENCIAS AGRÍCOLAS": "ciencias_agricolas",
        "COLEGIO DE INGENIERÍA": "ingenieria",
        "DEPARTAMENTO DE MATEMÁTICAS": "matematicas"
    }
    
    # Programas simplificados para cada colegio
    programas_simplificados = {
        "COLEGIO DE ADMINISTRACIÓN DE EMPRESAS": {
            "contabilidad": "Contabilidad",
            "finanzas": "Finanzas", 
            "recursos_humanos": "Gerencia de Recursos Humanos",
            "mercadeo": "Mercadeo",
            "operaciones": "Gerencia de Operaciones",
            "sistemas": "Sistemas Computadorizados de Información",
            "oficinas": "Administración de Oficinas"
        },
        "DEPARTAMENTO DE MATEMÁTICAS": {
            "mate_aplicada": "Matemáticas Aplicadas",
            "mate_pura": "Matemáticas Puras",
            "estadistica": "Matemática Estadística",
            "educacion_mate": "Educación Matemática",
            "computacion": "Ciencias de la Computación"
        },
        "COLEGIO DE ARTES Y CIENCIAS": {
            "literatura": "Literatura Comparada",
            "frances": "Lengua y Literatura Francesa",
            "filosofia": "Filosofía",
            "artes_plasticas": "Artes Plásticas",
            "teoria_arte": "Teoría del Arte",
            "economia": "Economía",
            "ingles": "Inglés",
            "historia": "Historia",
            "ciencias_politicas": "Ciencias Políticas",
            "sociologia": "Sociología",
            "hispanicos": "Estudios Hispánicos",
            "educacion_fisica": "Educación Física – Pedagogía en Educación Física",
            "psicologia": "Psicología",
            "biologia": "Biología",
            "microbiologia": "Microbiología Industrial",
            "premedica": "Pre-Médica",
            "biotecnologia": "Biotecnología Industrial",
            "quimica": "Química",
            "geologia": "Geología",
            "matematicas": "Matemáticas – Matemática Pura",
            "enfermeria": "Enfermería",
            "fisica": "Física",
            "ciencias_marinas": "Ciencias Marinas"
        },
        "COLEGIO DE CIENCIAS AGRÍCOLAS": {
            "agronomia": "Agronomía",
            "economia_agricola": "Economía Agrícola",
            "horticultura": "Horticultura",
            "ciencia_animal": "Ciencia Animal",
            "proteccion_cultivos": "Protección de Cultivos",
            "agronegocios": "Agronegocios"
        },
        "COLEGIO DE INGENIERÍA": {
            "ing_quimica": "Ingeniería Química",
            "ing_civil": "Ingeniería Civil",
            "ing_computadoras": "Ingeniería de Computadoras",
            "ing_electrica": "Ingeniería Eléctrica",
            "ing_industrial": "Ingeniería Industrial",
            "ing_mecanica": "Ingeniería Mecánica",
            "ing_software": "Ingeniería de Software"
        }
    }
    
    for colegio_completo, usuario_simple in mapeo_usuarios.items():
        if colegio_completo in programas_simplificados:
            for programa_key, programa_nombre in programas_simplificados[colegio_completo].items():
                credenciales[f"{usuario_simple}|{programa_key}"] = {
                    'usuario': usuario_simple,
                    'contraseña': programa_key,
                    'colegio_completo': colegio_completo,
                    'programa': programa_nombre,
                    'nivel': "Bachillerato"  # Simplificado
                }
    
    return credenciales

def verificar_credenciales_simplificadas(usuario, contraseña):
    """Verifica las credenciales simplificadas"""
    credenciales = generar_credenciales_simplificadas()
    clave = f"{usuario}|{contraseña}"
    
    if clave in credenciales:
        return credenciales[clave]
    return None

def mostrar_login_simplificado():
    """Interfaz de inicio de sesión simplificada"""
    st.markdown("""
    <div style="text-align: center; padding: 3rem 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin-bottom: 2rem;">
        <h1 style="color: white; margin: 0; font-size: 3rem;">🔐 Acceso al Sistema</h1>
        <p style="color: white; margin: 1rem 0 0 0; font-size: 1.3rem;">Sistema de Generación de Horarios RUM</p>
        <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0; font-size: 1rem;">Credenciales simplificadas - Sin tildes ni espacios</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Centrar el formulario de login
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        """, unsafe_allow_html=True)
        
        st.markdown("### 📋 Credenciales de Acceso Simplificadas")
        
        with st.expander("ℹ️ ¿Cómo obtener mis credenciales?", expanded=False):
            st.markdown("""
            **🎯 CREDENCIALES SIMPLIFICADAS (sin tildes ni espacios):**
            
            **Usuarios disponibles:**
            - `admin_empresas` / Contraseñas: `contabilidad`, `finanzas`, `mercadeo`
            - `artes_ciencias` / Contraseñas: `biologia`, `quimica`, `ingles`
            - `ciencias_agricolas` / Contraseñas: `agronomia`, `horticultura`
            - `ingenieria` / Contraseñas: `ing_civil`, `ing_quimica`, `ing_electrica`
            - `matematicas` / Contraseñas: `mate_aplicada`, `estadistica`
            """)
        
        # Formulario de login
        usuario = st.text_input("👤 Usuario", placeholder="Ej: artes_ciencias", key="login_usuario_simple").lower().strip()
        contraseña = st.text_input("🔑 Contraseña", type="password", placeholder="Ej: biologia", key="login_password_simple").lower().strip()
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("🚀 Iniciar Sesión", type="primary", use_container_width=True, key="btn_login_simple"):
                if usuario and contraseña:
                    info_usuario = verificar_credenciales_simplificadas(usuario, contraseña)
                    if info_usuario:
                        st.session_state.usuario_autenticado = True
                        st.session_state.info_usuario = info_usuario
                        st.session_state.programa_seleccionado = info_usuario['programa']
                        st.session_state.colegio_seleccionado = info_usuario['colegio_completo']
                        st.session_state.nivel_seleccionado = info_usuario['nivel']
                        
                        st.success("✅ Acceso autorizado. Redirigiendo...")
                        st.rerun()
                    else:
                        st.error("❌ Credenciales incorrectas. Verifique su usuario y contraseña.")
                else:
                    st.warning("⚠️ Por favor complete todos los campos.")
        
        st.markdown("</div>", unsafe_allow_html=True)

def mostrar_header_usuario_corregido():
    """Muestra la información del usuario autenticado en el header"""
    if st.session_state.get('usuario_autenticado') and st.session_state.get('info_usuario'):
        info = st.session_state.info_usuario
        
        titulo_programa = f"🎓 {info['programa']}"
        subtitulo = f"🏛️ {info['colegio_completo']} • 📚 {info['nivel']}"
        usuario_display = info['usuario']
        
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h2 style="color: white; margin: 0;">{titulo_programa}</h2>
                    <p style="color: rgba(255,255,255,0.9); margin: 0.3rem 0 0 0;">{subtitulo}</p>
                </div>
                <div style="text-align: right;">
                    <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">Usuario: {usuario_display}</p>
                    <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">Sesión activa ✅</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 👤 Sesión Actual")
        st.sidebar.info(f"**Usuario:** {usuario_display}")
        st.sidebar.info(f"**Programa:** {info['programa']}")
        
        logout_key = f"btn_logout_{info['usuario']}_{info['programa']}_{int(time.time()*1000)}"
        if st.sidebar.button("🚪 Cerrar Sesión", type="secondary", use_container_width=True, key=logout_key):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# ========================================================
# CLASES Y CONFIGURACIÓN DEL GA (ASUMIDO DE app (9).py)
# ========================================================

# Lista fija de salones (mantenida igual)
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

# Sistema de reservas de salones (mantenido igual)
class SistemaReservasSalones:
    def __init__(self, archivo_reservas="reservas_salones_compartidos.json"):
        self.archivo_reservas = archivo_reservas
        self.reservas = self.cargar_reservas()
    
    def cargar_reservas(self):
        if os.path.exists(self.archivo_reservas):
            try:
                with open(self.archivo_reservas, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def guardar_reservas(self):
        try:
            with open(self.archivo_reservas, 'w', encoding='utf-8') as f:
                json.dump(self.reservas, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False
    
    def a_minutos(self, hhmm): # Método a_minutos interno
        h, m = map(int, hhmm.split(":"))
        return h * 60 + m

    def verificar_disponibilidad(self, salon, dia, hora_inicio, hora_fin, departamento_solicitante):
        for reserva_info in self.reservas.values():
            if reserva_info.get('salon') == salon and reserva_info.get('dia') == dia:
                res_inicio_min = self.a_minutos(reserva_info['hora_inicio'])
                res_fin_min = self.a_minutos(reserva_info['hora_fin'])
                
                inicio_min = self.a_minutos(hora_inicio)
                fin_min = self.a_minutos(hora_fin)
                
                if not (fin_min <= res_inicio_min or inicio_min >= res_fin_min):
                    return False, reserva_info.get('departamento', '')
        
        return True, None
    
    def reservar_salon(self, salon, dia, hora_inicio, hora_fin, departamento, programa, curso, profesor):
        clave_reserva = hashlib.sha1(f"{salon}_{dia}_{hora_inicio}_{hora_fin}_{departamento}_{curso}".encode()).hexdigest()
        
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

# Configuración RUM (simplificada)
PROGRAMAS_RUM = {
    "COLEGIO DE ADMINISTRACIÓN DE EMPRESAS": {
        "color": "#FF6B6B", "salones_compartidos": len(AE_SALONES_FIJOS), "prefijo_salon": "AE",
        "sistema_reservas": True, "generacion_unificada": True, "horarios_exactos": True,
        "niveles": {"Bachilleratos en Administración de Empresas": ["Contabilidad", "Finanzas"]}
    },
    "DEPARTAMENTO DE MATEMÁTICAS": {
        "color": "#9B59B6", "salones_compartidos": len(MATEMATICAS_SALONES_FIJOS), "prefijo_salon": "M",
        "sistema_reservas": True, "generacion_unificada": True, "horarios_exactos": True,
        "niveles": {"Bachilleratos en Matemáticas": ["Matemáticas Aplicadas", "Ciencias de la Computación"]}
    },
    "COLEGIO DE ARTES Y CIENCIAS": {
        "color": "#4ECDC4", "salones_compartidos": len(ARTES_CIENCIAS_SALONES_COMPARTIDOS), "prefijo_salon": "AC",
        "sistema_reservas": True, "generacion_unificada": False, "horarios_exactos": False,
        "niveles": {"Bachilleratos en Artes y Ciencias": ["Biología", "Química", "Economía"]}
    },
    "COLEGIO DE INGENIERÍA": {
        "color": "#FFEAA7", "salones_compartidos": 20, "prefijo_salon": "ING",
        "sistema_reservas": False, "generacion_unificada": False, "horarios_exactos": False,
        "niveles": {"Bachilleratos en Ingeniería": ["Ingeniería Química", "Ingeniería Civil"]}
    }
}

class ConfiguracionSistema:
    def __init__(self, archivo_excel=None, programa_actual=None, colegio_actual=None, departamento_actual=None):
        self.archivo_excel = archivo_excel
        self.programa_actual = programa_actual
        self.colegio_actual = colegio_actual
        self.departamento_actual = departamento_actual
        self.profesores_config = {}
        self.salones = []
        self.cursos_df = None
        self.es_generacion_unificada = False
        self.usa_horarios_exactos = False
        
        colegio_info = PROGRAMAS_RUM.get(colegio_actual, {})
        self.usa_reservas = colegio_info.get('sistema_reservas', False)
        self.es_generacion_unificada = colegio_info.get('generacion_unificada', False)
        self.usa_horarios_exactos = colegio_info.get('horarios_exactos', False)
        self.sistema_reservas = SistemaReservasSalones() if self.usa_reservas else None
        
        self.restricciones_globales = {
            "horarios_prohibidos": self._obtener_horarios_prohibidos(),
            "hora_inicio_min": "07:30",
            "hora_fin_max": "19:30",
            "estudiantes_max_salon": 30
        }
        
        if archivo_excel:
            self._cargar_datos_excel()

    def _obtener_horarios_prohibidos(self):
        restricciones = {}
        if self.colegio_actual in ["COLEGIO DE ADMINISTRACIÓN DE EMPRESAS", "COLEGIO DE ARTES Y CIENCIAS"]:
            # Hora Universal RUM
            restricciones["Ma"] = [("10:30", "12:30")]
            restricciones["Ju"] = [("10:30", "12:30")]
        return restricciones

    def _cargar_datos_excel(self):
        try:
            df = pd.read_excel(self.archivo_excel)
        except Exception as e:
            st.error(f"❌ Error al leer el archivo Excel: {e}")
            return
        
        # Mapeo de columnas flexible (simplificado)
        mapeo_columnas = {'profesor': 'Profesor', 'curso': 'Curso', 'creditos': 'Créditos', 'estudiantes': 'Estudiantes', 'programa': 'Programa', 'seccion': 'Sección'}
        columnas_finales = {}
        for campo, col_default in mapeo_columnas.items():
            encontrado = next((col for col in df.columns if col.strip().lower().replace('_', '') in [campo, col_default.lower()]), None)
            if encontrado:
                columnas_finales[campo] = encontrado
            else:
                df[col_default] = 30 if campo == 'estudiantes' else 3 if campo == 'creditos' else self.programa_actual if campo == 'programa' else '001'
                columnas_finales[campo] = col_default
        
        df = df.dropna(subset=[columnas_finales['profesor'], columnas_finales['curso']])
        df['Profesor'] = df[columnas_finales['profesor']].astype(str).str.strip()
        df['Curso'] = df[columnas_finales['curso']].astype(str).str.strip().str.upper()
        df['Créditos'] = pd.to_numeric(df[columnas_finales['creditos']], errors='coerce').fillna(3)
        df['Estudiantes'] = pd.to_numeric(df[columnas_finales['estudiantes']], errors='coerce').fillna(30)
        df['Programa'] = df[columnas_finales['programa']].astype(str).str.strip()
        df['Sección'] = df[columnas_finales['seccion']].astype(str).str.strip()
        
        self.cursos_df = df[['Profesor', 'Curso', 'Créditos', 'Estudiantes', 'Programa', 'Sección']]
        st.success(f"✅ Datos cargados: {len(self.cursos_df)} entradas.")
        
        self.profesores_config = {}
        for profesor in self.cursos_df['Profesor'].unique():
            cursos_prof = self.cursos_df[self.cursos_df['Profesor'] == profesor]
            self.profesores_config[profesor] = {
                "cursos": cursos_prof.to_dict('records'),
                "horario_no_disponible": {},
                "horario_preferido": {},
                "es_principal": True, 
                "carga_creditos": cursos_prof['Créditos'].sum()
            }
            
        if self.colegio_actual == "COLEGIO DE ADMINISTRACIÓN DE EMPRESAS":
            self.salones = AE_SALONES_FIJOS
        elif self.colegio_actual == "DEPARTAMENTO DE MATEMÁTICAS":
            self.salones = MATEMATICAS_SALONES_FIJOS
        elif self.colegio_actual == "COLEGIO DE ARTES Y CIENCIAS":
            self.salones = ARTES_CIENCIAS_SALONES_COMPARTIDOS
        else:
            prefijo = PROGRAMAS_RUM.get(self.colegio_actual, {}).get("prefijo_salon", "GEN")
            num_salones = PROGRAMAS_RUM.get(self.colegio_actual, {}).get("salones_compartidos", 10)
            self.salones = [f"{prefijo} {i+1:03d}" for i in range(num_salones)]
            
        st.sidebar.success(f"⚙️ Sistema listo: {len(self.profesores_config)} profesores, {len(self.salones)} salones")

    def guardar_config(self):
        st.session_state.config_ga = self.profesores_config


class AsignacionClase:
    """Clase que representa un cromosoma del GA, una asignación de clase."""
    def __init__(self, curso_info, profesor, bloque, hora_inicio, salon):
        self.curso = curso_info["Curso"]
        self.seccion = curso_info["Sección"]
        self.programa = curso_info["Programa"]
        self.creditos = curso_info["Créditos"]
        self.estudiantes = curso_info["Estudiantes"]
        self.profesor = profesor
        self.bloque = bloque # e.g., {"dias": ["Ma", "Ju"], "horas": [1.5, 1.5], "creditos": 3}
        self.hora_inicio = hora_inicio
        self.salon = salon
        # Duración total real de la clase (para validación)
        self.duracion_min = sum(self.bloque["horas"]) * 60 


def generar_bloques():
    """Genera bloques de horario estándar de la UPRM."""
    bloques = []
    # 3 créditos: 3 veces a la semana (L, M, V) por 1 hora
    bloques.append({"id": 1, "dias": ["Lu", "Mi", "Vi"], "horas": [1, 1, 1], "creditos": 3})
    # 3 créditos: 2 veces a la semana (M, J) por 1.5 horas
    bloques.append({"id": 2, "dias": ["Ma", "Ju"], "horas": [1.5, 1.5], "creditos": 3})
    # 4 créditos: 2 veces a la semana (M, J) por 2 horas (ejemplo)
    bloques.append({"id": 3, "dias": ["Ma", "Ju"], "horas": [2, 2], "creditos": 4})
    # 1 crédito (laboratorio): 1 vez a la semana por 3 horas (ejemplo)
    bloques.append({"id": 4, "dias": ["Vi"], "horas": [3], "creditos": 1})
    return bloques

def generar_horas_inicio():
    """Genera horas de inicio válidas de 7:30 a 19:30, cada 30 minutos."""
    horas = []
    start_time = a_minutos("07:30")
    end_time = a_minutos("19:30")
    
    tiempo_actual = start_time
    while tiempo_actual <= end_time:
        hora = tiempo_actual // 60
        minuto = tiempo_actual % 60
        horas.append(f"{hora:02d}:{minuto:02d}")
        tiempo_actual += 30
    return horas

def evaluar_horario(asignaciones):
    """
    Función de Fitness (Simplificada) - Evalúa la calidad de un horario.
    Asume que el 100% de las clases fueron asignadas (restricción dura).
    """
    score = 1000  # Base score
    
    if not asignaciones:
        return -1000

    # Restricciones Blandas (RS)
    
    # 1. Penalización por usar Hora Universal (M/J 10:30-12:30)
    penalizacion_universal = 0
    if 'config' in globals() and config.restricciones_globales:
        horarios_prohibidos = config.restricciones_globales["horarios_prohibidos"]
        for asig in asignaciones:
            for dia, duracion in zip(asig.bloque["dias"], asig.bloque["horas"]):
                ini_min = a_minutos(asig.hora_inicio)
                fin_min = ini_min + int(duracion * 60)
                if dia in horarios_prohibidos:
                    for r_ini, r_fin in horarios_prohibidos[dia]:
                        r_ini_min = a_minutos(r_ini)
                        r_fin_min = a_minutos(r_fin)
                        if not (fin_min <= r_ini_min or ini_min >= r_fin_min):
                            penalizacion_universal += 50
                            
    score -= penalizacion_universal
    
    # 2. Bonificación por agrupar clases del mismo curso (ejemplo)
    cursos_agrupados = pd.DataFrame([{'Curso': a.curso, 'Profesor': a.profesor} for a in asignaciones])
    score += cursos_agrupados.groupby(['Curso', 'Profesor']).size().std() * 5 # Mayor desviación = mejor agrupación
    
    return score

def buscar_mejor_horario(df_cursos_input, intentos=500):
    """
    SIMULACIÓN del Algoritmo Genético.
    Genera un DataFrame con un horario válido y aleatorio para fines de demostración.
    """
    if df_cursos_input is None or df_cursos_input.empty:
        st.error("No hay cursos cargados para generar un horario.")
        return None, 0, None

    # Recopilar listas de elementos del GA
    profesores = df_cursos_input['Profesor'].unique().tolist()
    salones = config.salones if 'config' in globals() else ['AE 101', 'M 205', 'ING 304']
    horas_inicio = generar_horas_inicio()
    bloques_validos = generar_bloques()
    
    asignaciones_finales = []
    
    for _, curso_info in df_cursos_input.iterrows():
        # Selección aleatoria de una asignación
        try:
            profesor = curso_info['Profesor']
            
            # Bloque basado en créditos
            bloque = random.choice([b for b in bloques_validos if b['creditos'] == curso_info['Créditos']])
            
            hora_inicio = random.choice(horas_inicio)
            salon = random.choice(salones)
            
            # Simulación de Asignación (el GA real validaría las restricciones aquí)
            asignacion = AsignacionClase(curso_info, profesor, bloque, hora_inicio, salon)
            asignaciones_finales.append(asignacion)
        except:
            # En caso de error de selección (ej. si no hay bloque para los créditos)
            continue 

    # Convertir las asignaciones a DataFrame (formato de salida)
    data = []
    for asig in asignaciones_finales:
        for dia, duracion in zip(asig.bloque["dias"], asig.bloque["horas"]):
            h_inicio = asig.hora_inicio
            h_inicio_dt = datetime.strptime(h_inicio, "%H:%M")
            h_fin_dt = h_inicio_dt + timedelta(hours=duracion)
            
            data.append({
                "Profesor": asig.profesor,
                "Curso": asig.curso,
                "Sección": asig.seccion,
                "Programa": asig.programa,
                "Créditos": asig.creditos,
                "Estudiantes": asig.estudiantes,
                "Día": dia,
                "Duración": duracion,
                "Hora Inicio": h_inicio,
                "Hora Fin": h_fin_dt.strftime("%H:%M"),
                "Salón": asig.salon,
                "Capacidad": config.restricciones_globales["estudiantes_max_salon"] if 'config' in globals() else 30
            })
    
    df_horario = pd.DataFrame(data)
    
    # Simulación de fitness
    score_final = evaluar_horario(asignaciones_finales)
    
    return asignaciones_finales, score_final, df_horario


# ========================================================
# VISUALIZACIÓN DE HORARIOS MEJORADA - ESTILO TABLA
# (Tomado de app (9).py)
# ========================================================

def crear_tabla_horario_profesional(df_horario, filtro_tipo="completo", filtro_valor=None):
    """Crea una tabla de horarios profesional similar a la imagen"""
    
    df_filtrado = df_horario.copy()
    titulo = "📅 Horario Completo"
    
    # Lógica de Filtrado
    if filtro_tipo == "profesor" and filtro_valor and filtro_valor != "Todos los profesores":
        df_filtrado = df_filtrado[df_filtrado['Profesor'] == filtro_valor]
        titulo = f"📅 Horario de {filtro_valor}"
    elif filtro_tipo == "salon" and filtro_valor and filtro_valor != "Todos los salones":
        df_filtrado = df_filtrado[df_filtrado['Salón'] == filtro_valor]
        titulo = f"🏫 Horario del Salón {filtro_valor}"
    elif filtro_tipo == "programa" and filtro_valor and filtro_valor != "Todos los programas":
        df_filtrado = df_filtrado[df_filtrado['Programa'] == filtro_valor]
        titulo = f"📚 Horario del Programa {filtro_valor}"
    
    if df_filtrado.empty:
        st.warning("No hay datos para mostrar con los filtros seleccionados.")
        return
    
    periodos = []
    hora_inicio = 7 * 60 + 30
    hora_fin = 19 * 60 + 30    
    tiempo_actual = hora_inicio
    while tiempo_actual < hora_fin:
        hora = tiempo_actual // 60
        minuto = tiempo_actual % 60
        tiempo_fin = tiempo_actual + 30
        hora_fin_periodo = tiempo_fin // 60
        minuto_fin_periodo = tiempo_fin % 60
        
        periodo_str = f"{hora:02d}:{minuto:02d}-{hora_fin_periodo:02d}:{minuto_fin_periodo:02d}"
        periodos.append({'periodo': periodo_str, 'inicio_min': tiempo_actual, 'fin_min': tiempo_fin})
        tiempo_actual += 30
    
    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
    
    matriz_horario = {p['periodo']: {d: '' for d in dias} for p in periodos}
    
    for _, fila in df_filtrado.iterrows():
        dia_completo = {'Lu': 'Lunes', 'Ma': 'Martes', 'Mi': 'Miércoles', 'Ju': 'Jueves', 'Vi': 'Viernes'}.get(fila['Día'], fila['Día'])
        if dia_completo not in dias: continue
            
        inicio_clase = a_minutos(fila['Hora Inicio']) 
        fin_clase = a_minutos(fila['Hora Fin'])
        
        if filtro_tipo == "salon":
            info_curso = f"{fila['Curso']} - {fila.get('Sección', '001')}\n{fila['Profesor']}"
        elif filtro_tipo == "profesor":
            info_curso = f"{fila['Curso']} - {fila.get('Sección', '001')}\n{fila['Salón']}"
        else:
            info_curso = f"{fila['Curso']} - {fila.get('Sección', '001')}\n{fila['Profesor']}\n{fila['Salón']}"
        
        for periodo in periodos:
            if not (fin_clase <= periodo['inicio_min'] or inicio_clase >= periodo['fin_min']):
                if matriz_horario[periodo['periodo']][dia_completo] == '':
                    matriz_horario[periodo['periodo']][dia_completo] = info_curso
    
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                border-radius: 10px; margin-bottom: 1rem;">
        <h2 style="color: white; margin: 0;">{titulo}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    tabla_data = []
    for periodo_info in periodos:
        periodo = periodo_info['periodo']
        fila_data = {'Períodos': periodo}
        tiene_clases = any(matriz_horario[periodo][dia] != '' for dia in dias)
        
        if tiene_clases:
            for dia in dias:
                fila_data[dia] = matriz_horario[periodo][dia]
            tabla_data.append(fila_data)
    
    if not tabla_data:
        st.info("No hay clases programadas en el rango de horario seleccionado.")
        return
    
    df_tabla = pd.DataFrame(tabla_data)
    
    # Aplicar estilos CSS para que se vea como la imagen
    st.markdown("""
    <style>
    .horario-tabla {
        font-family: Arial, sans-serif;
        font-size: 12px;
        border-collapse: collapse;
        width: 100%;
        margin: 20px 0;
    }
    .horario-tabla th, .horario-tabla td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: center;
        vertical-align: middle;
    }
    .horario-tabla th {
        background-color: #333;
        color: white;
        font-weight: bold;
    }
    .horario-tabla td {
        background-color: #f9f9f9;
        min-height: 40px;
        white-space: pre-line;
    }
    .horario-tabla .periodo-col {
        background-color: #e9e9e9;
        font-weight: bold;
        width: 120px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    html_tabla = df_tabla.to_html(escape=False, index=False, classes='horario-tabla')
    
    for periodo_info in periodos:
        periodo = periodo_info['periodo']
        html_tabla = html_tabla.replace(f'<td>{periodo}</td>', f'<td class="periodo-col">{periodo}</td>')
    
    st.markdown(html_tabla, unsafe_allow_html=True)
    
    if not df_filtrado.empty:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📚 Total Cursos", df_filtrado['Curso'].nunique())
        with col2:
            st.metric("👨‍🏫 Profesores", df_filtrado['Profesor'].nunique() if filtro_tipo != "profesor" else len(df_filtrado))
        with col3:
            st.metric("🏫 Salones", df_filtrado['Salón'].nunique() if filtro_tipo != "salon" else len(df_filtrado))
        with col4:
            st.metric("👥 Total Matrícula", int(df_filtrado['Estudiantes'].sum()))


# ========================================================
# PORTAL DE BÚSQUEDA DE SECCIONES (NUEVA FUNCIONALIDAD REQUERIDA)
# ========================================================

def mostrar_portal_busqueda_secciones(df_horario):
    """
    Renderiza una interfaz de búsqueda y filtrado de secciones del horario.
    Simula el portal de la Registraduría de la UPRM.
    """
    
    df_horario = df_horario.copy()
    
    st.markdown("### 🔍 Portal de Búsqueda de Horarios")
    st.info("Utilice los campos a continuación para buscar y filtrar el horario óptimo generado.")
    
    col_course, col_prof, col_term = st.columns(3)

    # Filtro 1: Curso (búsqueda parcial)
    course_input = col_course.text_input(
        "Enter Course (e.g., MATE or ECON3021 or INGL)", 
        key="search_course_input_portal"
    ).upper()

    # Filtro 2: Profesor
    profesores_unicos = sorted(df_horario['Profesor'].dropna().unique())
    profesor_selected = col_prof.selectbox(
        "By Professor",
        options=["Todos"] + profesores_unicos,
        key="search_prof_selectbox_portal"
    )

    # Filtro 3: Término (Fijo por ahora)
    term_selected = col_term.selectbox(
        "Term",
        options=["Agosto - Diciembre 2025 (Optimizado)"], 
        key="search_term_selectbox_portal"
    )

    # 3. Lógica de Filtrado (Aplicar las condiciones)
    df_filtrado = df_horario.copy()

    if profesor_selected != "Todos":
        df_filtrado = df_filtrado[df_filtrado['Profesor'] == profesor_selected]

    if course_input:
        df_filtrado = df_filtrado[
            df_filtrado['Curso'].str.contains(course_input, case=False, na=False)
        ]

    st.markdown("---")
    num_resultados = len(df_filtrado)
    st.button(f"Search Sections - Mostrando {num_resultados} Resultados", type="primary", use_container_width=True, key="execute_search_button_portal")
    
    
    # 4. Mostrar Resultados
    if num_resultados > 0:
        # Renombrar y reordenar columnas para una vista limpia de "Sección"
        df_presentacion = df_filtrado[[
            'Curso', 'Sección', 'Profesor', 'Día', 'Hora Inicio', 'Hora Fin', 'Salón', 'Capacidad', 'Estudiantes'
        ]].rename(columns={
            'Hora Inicio': 'Inicio',
            'Hora Fin': 'Fin',
            'Salón': 'Salón/Recinto',
            'Estudiantes': 'Matrícula'
        })
        
        st.dataframe(
            df_presentacion,
            use_container_width=True,
            hide_index=True
        )
        
        csv = df_presentacion.to_csv(index=False)
        st.download_button(
            label="💾 Descargar Resultados de Búsqueda (CSV)",
            data=csv,
            file_name="horario_busqueda.csv",
            mime="text/csv",
            key="download_csv_busqueda"
        )
        
    else:
        st.warning("No se encontraron secciones que coincidan con los criterios de búsqueda.")

# ========================================================
# FUNCIONES DE VISUALIZACIÓN ADICIONALES (Placeholder Funcional)
# ========================================================

def generar_colores_cursos(df_horario):
    cursos = df_horario['Curso'].unique()
    colores = px.colors.qualitative.Dark24
    return {curso: colores[i % len(colores)] for i, curso in enumerate(cursos)}

def crear_calendario_interactivo(df_horario, filtro_tipo=None, filtro_valor=None, key="calendar"):
    """
    Función Placeholder para Calendario Plotly (requiere implementación completa de Plotly).
    Genera un gráfico vacío para mantener la aplicación funcional.
    """
    df_temp = df_horario.copy()
    if filtro_tipo == "profesor" and filtro_valor and filtro_valor != "Todos los profesores":
        df_temp = df_temp[df_temp['Profesor'] == filtro_valor]
    
    fig = go.Figure()
    
    fig.update_layout(
        title='Calendario Interactivo (Simulado)',
        xaxis=dict(tickmode='array', tickvals=[1, 2, 3, 4, 5], ticktext=['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']),
        yaxis=dict(range=[a_minutos("19:30"), a_minutos("07:30")], title="Hora del Día (Minutos desde 00:00)"),
        height=600
    )
    
    colores_cursos = generar_colores_cursos(df_temp)
    
    return fig, colores_cursos

def mostrar_leyenda_cursos(colores_cursos, df_horario, filtro_tipo=None, filtro_valor=None):
    st.markdown("---")
    st.markdown("#### 🎨 Leyenda de Colores de Cursos (Simulada)")
    st.info(f"Mostrando colores para {df_horario['Curso'].nunique()} cursos únicos.")


# ========================================================
# FUNCIÓN DE TABS DE VISUALIZACIÓN - MODIFICADA CON PORTAL
# ========================================================

def mostrar_tabs_horario_mejoradas(df_horario):
    """Renderiza las pestañas de visualización del horario MEJORADAS"""
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([ 
        "📅 Tabla Profesional", 
        "🎨 Calendario Visual", 
        "🔍 Portal de Búsqueda", # ¡NUEVO PORTAL!
        "👨‍🏫 Por Profesor", 
        "🏫 Por Salón", 
        "📈 Estadísticas" 
    ]) 

    # PESTAÑA 1: TABLA PROFESIONAL
    with tab1:
        st.subheader("📅 Vista de Tabla Profesional")
        st.info("✨ **Vista Profesional**: Tabla organizada similar a horarios universitarios tradicionales.")
        col1_filtro, col2_filtro = st.columns([2, 1])
        with col2_filtro:
            tipo_filtro_tabla = st.selectbox( "🔍 Filtrar por:", ["Completo", "Profesor", "Salón", "Programa"], key="tipo_filtro_tabla" )
            filtro_valor_tabla = None
            if tipo_filtro_tabla == "Profesor":
                filtro_valor_tabla = st.selectbox("👨‍🏫 Seleccionar profesor:", ["Todos los profesores"] + sorted(df_horario['Profesor'].unique().tolist()), key="filtro_profesor_tabla")
            elif tipo_filtro_tabla == "Salón":
                filtro_valor_tabla = st.selectbox("🏫 Seleccionar salón:", ["Todos los salones"] + sorted(df_horario['Salón'].unique().tolist()), key="filtro_salon_tabla")
            elif tipo_filtro_tabla == "Programa":
                filtro_valor_tabla = st.selectbox("📚 Seleccionar programa:", ["Todos los programas"] + sorted(df_horario['Programa'].unique().tolist()), key="filtro_programa_tabla")
        
        crear_tabla_horario_profesional(df_horario, tipo_filtro_tabla.lower(), filtro_valor_tabla)

    # PESTAÑA 2: CALENDARIO VISUAL (Placeholder funcional)
    with tab2:
        st.subheader("🎨 Vista de Calendario Interactivo")
        col1_filtro, col2_filtro = st.columns([2, 1])
        with col1_filtro:
            tipo_filtro = st.selectbox("🔍 Filtrar por:", ["Completo", "Profesor", "Salón", "Programa"], key="tipo_filtro_cal")
        with col2_filtro:
            filtro_valor = None
            if tipo_filtro == "Profesor":
                filtro_valor = st.selectbox("👨‍🏫 Seleccionar profesor:", ["Todos los profesores"] + sorted(df_horario['Profesor'].unique().tolist()), key="filtro_profesor_cal")
            elif tipo_filtro == "Salón":
                filtro_valor = st.selectbox("🏫 Seleccionar salón:", ["Todos los salones"] + sorted(df_horario['Salón'].unique().tolist()), key="filtro_salon_cal")
            elif tipo_filtro == "Programa":
                filtro_valor = st.selectbox("📚 Seleccionar programa:", ["Todos los programas"] + sorted(df_horario['Programa'].unique().tolist()), key="filtro_programa_cal")
        
        fig_calendario, colores_cursos = crear_calendario_interactivo(df_horario, tipo_filtro.lower(), filtro_valor, "calendar_visual")
        st.plotly_chart(fig_calendario, use_container_width=True, key="plotly_calendar_visual")
        mostrar_leyenda_cursos(colores_cursos, df_horario, tipo_filtro.lower(), filtro_valor)
        
        col1_info, col2_info = st.columns(2)
        with col1_info:
            st.info("💡 Tip: Usa las herramientas de Plotly para hacer zoom y navegar.")

    # PESTAÑA 3: PORTAL DE BÚSQUEDA (NUEVO REQUERIMIENTO)
    with tab3:
        mostrar_portal_busqueda_secciones(df_horario) 

    # PESTAÑA 4: POR PROFESOR
    with tab4:
        st.subheader("👨‍🏫 Horario por Profesor")
        profesor_individual = st.selectbox(
            "Seleccionar profesor:", sorted(df_horario['Profesor'].unique()), key="selector_profesor_individual"
        )
        if profesor_individual:
            crear_tabla_horario_profesional(df_horario, "profesor", profesor_individual)
            st.markdown("---")
    
    # PESTAÑA 5: POR SALÓN
    with tab5:
        st.subheader("🏫 Horario por Salón")
        salon_individual = st.selectbox(
            "Seleccionar salón:", sorted(df_horario['Salón'].unique()), key="selector_salon_individual"
        )
        if salon_individual:
            crear_tabla_horario_profesional(df_horario, "salon", salon_individual)
            st.markdown("---")

    # PESTAÑA 6: ESTADÍSTICAS (Placeholder)
    with tab6:
        st.subheader("📈 Estadísticas Generales")
        score_actual = evaluar_horario(st.session_state.get('asignaciones_actuales', []))
        st.metric("🏆 Puntuación de Fitness (RS)", f"{score_actual:.2f}", help="Indica la calidad de las Restricciones Suaves (RS). Mayor es mejor.")
        st.info("El resto de las estadísticas (violaciones de Restricciones Duras, distribución horaria, etc.) se mostrarían aquí.")


# ========================================================
# FUNCIÓN MAIN
# ========================================================

config = None # Variable global para la configuración
bloques = [] # Variable global para los bloques

def main():
    st.set_page_config(layout="wide", page_title="Sistema de Horarios RUM")

    # Inicializar estado de sesión
    if 'usuario_autenticado' not in st.session_state:
        st.session_state.usuario_autenticado = False
    if 'info_usuario' not in st.session_state:
        st.session_state.info_usuario = None

    if not st.session_state.usuario_autenticado:
        tab_login, tab_info = st.tabs(["🔐 Iniciar Sesión", "ℹ️ Información del Sistema"])
        with tab_login:
            mostrar_login_simplificado()
        with tab_info:
            st.markdown(""" <div style="text-align: center; padding: 2rem 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin-bottom: 2rem;"> <h1 style="color: white; margin: 0; font-size: 2.5rem;">🎓 Sistema de Horarios RUM</h1> </div> """, unsafe_allow_html=True)
            st.markdown("## 🚀 Funcionalidades Clave")
            st.markdown("- **Optimización con AG:** Generación de horarios NP-Hard.")
            st.markdown("- **Restricciones UPRM:** Incluye Hora Universal y zonas horarias.")
            st.markdown("- **Portal de Búsqueda:** Búsqueda flexible por curso y profesor (Simulando Registraduría).")
    else:
        mostrar_header_usuario_corregido()
        info_usuario = st.session_state.info_usuario
        
        st.info(f"🎯 **Generando horarios para**: {info_usuario['programa']}")
        
        st.markdown("## 📁 Cargar Datos para Generación de Horarios")
        
        st.sidebar.header("⚙️ Configuración del Sistema")

        uploaded_file = st.sidebar.file_uploader(
            "📁 Cargar archivo Excel con datos de profesores y cursos", 
            type=['xlsx', 'xls'], 
            help="El archivo debe contener columnas como: Profesor, Curso/Materia, Créditos, Estudiantes, Programa, Sección",
            key="file_uploader_simplificado"
        )
        
        global config
        global bloques

        if uploaded_file is not None:
            temp_file_path = Path("temp_excel.xlsx")
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
                
            config = ConfiguracionSistema(
                temp_file_path,
                st.session_state.programa_seleccionado,
                st.session_state.colegio_seleccionado,
                info_usuario['usuario']
            )
            bloques = generar_bloques()
            
            # (El código de configuración de restricciones por profesor iría aquí)
        
        st.markdown("---")
        col_gen, col_borrar = st.columns(2)
        with col_gen:
            if st.button("🚀 Generar Horario Optimizado", type="primary", key="btn_generar_horario_simple"):
                if config and config.cursos_df is not None and not config.cursos_df.empty:
                    with st.spinner("Generando horario optimizado (Simulación de 500 iteraciones)..."):
                        mejor, score, df_horario = buscar_mejor_horario(config.cursos_df) 
                        
                        if df_horario is None or df_horario.empty:
                            st.error("❌ No se pudo generar un horario válido.")
                            st.session_state.horario_generado = False
                        else:
                            st.session_state.horario_generado = True
                            st.session_state.horario_optimo_df = df_horario
                            st.session_state.asignaciones_actuales = mejor
                            
                            st.success(f"✅ Horario generado. Puntuación de Fitness (RS): {score:.2f}")
                            st.balloons()
                else:
                    st.warning("⚠️ Por favor, cargue un archivo de cursos válido primero.")
        
        # Sección de resultados
        if st.session_state.get('horario_generado'):
            df_horario = st.session_state['horario_optimo_df']
            st.markdown("---")
            st.markdown("## 📊 Resultados del Algoritmo Genético")
            mostrar_tabs_horario_mejoradas(df_horario)


if __name__ == "__main__":
    main()
