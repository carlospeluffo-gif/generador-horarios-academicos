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
# SISTEMA DE AUTENTICACIÓN Y CREDENCIALES SIMPLIFICADO
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
            # Artes - Humanidades
            "literatura": "Literatura Comparada",
            "frances": "Lengua y Literatura Francesa",
            "filosofia": "Filosofía",
            "artes_plasticas": "Artes Plásticas",
            "teoria_arte": "Teoría del Arte",
            # Artes - Otros
            "economia": "Economía",
            "ingles": "Inglés",
            "historia": "Historia",
            "ciencias_politicas": "Ciencias Políticas",
            "sociologia": "Sociología",
            "hispanicos": "Estudios Hispánicos",
            "educacion_fisica": "Educación Física – Pedagogía en Educación Física",
            "psicologia": "Psicología",
            # Ciencias
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
        
        # Información de ayuda SIMPLIFICADA
        with st.expander("ℹ️ ¿Cómo obtener mis credenciales?", expanded=False):
            st.markdown("""
            **🎯 CREDENCIALES SIMPLIFICADAS (sin tildes ni espacios):**
            
            **Usuarios disponibles:**
            - `admin_empresas` - Administración de Empresas
            - `artes_ciencias` - Artes y Ciencias
            - `ciencias_agricolas` - Ciencias Agrícolas
            - `ingenieria` - Ingeniería
            - `matematicas` - Matemáticas
            
            **Contraseñas (ejemplos):**
            - `contabilidad`, `finanzas`, `mercadeo`
            - `literatura`, `filosofia`, `biologia`, `quimica`
            - `agronomia`, `horticultura`
            - `ing_civil`, `ing_quimica`, `ing_electrica`
            - `mate_aplicada`, `estadistica`
            
            **Ejemplo de acceso:**
            - Usuario: `artes_ciencias`
            - Contraseña: `biologia`
            """)
        
        # Formulario de login
        usuario = st.text_input("👤 Usuario", placeholder="Ej: artes_ciencias", key="login_usuario_simple")
        contraseña = st.text_input("🔑 Contraseña", type="password", placeholder="Ej: biologia", key="login_password_simple")
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("🚀 Iniciar Sesión", type="primary", use_container_width=True, key="btn_login_simple"):
                if usuario and contraseña:
                    info_usuario = verificar_credenciales_simplificadas(usuario, contraseña)
                    if info_usuario:
                        # Guardar información de sesión
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
        
        # Mostrar programas disponibles para referencia
        with st.expander("📚 Ver todos los programas disponibles"):
            credenciales = generar_credenciales_simplificadas()
            programas_por_colegio = {}
            
            for info in credenciales.values():
                colegio = info['usuario']
                if colegio not in programas_por_colegio:
                    programas_por_colegio[colegio] = []
                programas_por_colegio[colegio].append(f"{info['contraseña']} → {info['programa']}")
            
            for colegio, programas in sorted(programas_por_colegio.items()):
                st.markdown(f"**🏛️ {colegio}**")
                for programa in sorted(programas):
                    st.markdown(f"  • {programa}")
                st.markdown("---")
        
        st.markdown("</div>", unsafe_allow_html=True)

def mostrar_header_usuario_corregido():
    """Muestra la información del usuario autenticado en el header - CORREGIDO (Clave única para cerrar sesión)"""
    if st.session_state.get('usuario_autenticado') and st.session_state.get('info_usuario'):
        info = st.session_state.info_usuario
        
        titulo_programa = f"🎓 {info['programa']}"
        subtitulo = f"🏛️ {info['colegio_completo']} • 📚 {info['nivel']}"
        usuario_display = info['usuario']
        
        # Header con información del usuario
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
        
        # Botón de cerrar sesión en sidebar - CLAVE ÚNICA (CORREGIDO)
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 👤 Sesión Actual")
        st.sidebar.info(f"**Usuario:** {usuario_display}")
        st.sidebar.info(f"**Programa:** {info['programa']}")
        
        # CLAVE ÚNICA para evitar duplicados en el botón de cerrar sesión
        logout_key = f"btn_logout_{info['usuario']}_{info['programa']}_{int(time.time()*1000)}"
        if st.sidebar.button("🚪 Cerrar Sesión", type="secondary", use_container_width=True, key=logout_key):
            # Limpiar session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# ========================================================
# VISUALIZACIÓN DE HORARIOS MEJORADA - ESTILO TABLA
# ========================================================

def a_minutos(hhmm):
    """Convierte la hora HH:MM a minutos desde medianoche"""
    if isinstance(hhmm, datetime):
        hhmm = hhmm.strftime("%H:%M")
    h, m = map(int, hhmm.split(":"))
    return h * 60 + m

def crear_tabla_horario_profesional(df_horario, filtro_tipo="completo", filtro_valor=None):
    """Crea una tabla de horarios profesional similar a la imagen"""
    
    # Filtrar datos según el tipo
    if filtro_tipo == "profesor" and filtro_valor and filtro_valor != "Todos los profesores":
        df_filtrado = df_horario[df_horario['Profesor'] == filtro_valor]
        titulo = f"📅 Horario de {filtro_valor}"
    elif filtro_tipo == "salon" and filtro_valor and filtro_valor != "Todos los salones":
        df_filtrado = df_horario[df_horario['Salon'] == filtro_valor]
        titulo = f"🏫 Horario del Salón {filtro_valor}"
    elif filtro_tipo == "programa" and filtro_valor and filtro_valor != "Todos los programas":
        df_filtrado = df_horario[df_horario['Programa'] == filtro_valor]
        titulo = f"📚 Horario del Programa {filtro_valor}"
    else:
        df_filtrado = df_horario
        titulo = "📅 Horario Completo"
    
    if df_filtrado.empty:
        st.warning("No hay datos para mostrar con los filtros seleccionados.")
        return
    
    # Crear estructura de períodos de tiempo
    periodos = []
    hora_inicio = 7 * 60 + 30  # 7:30 AM en minutos
    hora_fin = 19 * 60 + 30    # 7:30 PM en minutos
    
    # Generar períodos cada 30 minutos
    tiempo_actual = hora_inicio
    while tiempo_actual < hora_fin:
        hora = tiempo_actual // 60
        minuto = tiempo_actual % 60
        tiempo_fin = tiempo_actual + 30
        hora_fin_periodo = tiempo_fin // 60
        minuto_fin_periodo = tiempo_fin % 60
        
        periodo_str = f"{hora:02d}:{minuto:02d}-{hora_fin_periodo:02d}:{minuto_fin_periodo:02d}"
        periodos.append({
            'periodo': periodo_str,
            'inicio_min': tiempo_actual,
            'fin_min': tiempo_fin
        })
        tiempo_actual += 30
    
    # Días de la semana
    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
    dias_cortos = ['Lu', 'Ma', 'Mi', 'Ju', 'Vi']
    
    # Crear matriz de horarios
    matriz_horario = {}
    for periodo in periodos:
        matriz_horario[periodo['periodo']] = {dia: '' for dia in dias}
    
    # Llenar la matriz con los cursos
    for _, fila in df_filtrado.iterrows():
        dia_completo = {
            'Lu': 'Lunes', 'Ma': 'Martes', 'Mi': 'Miércoles', 
            'Ju': 'Jueves', 'Vi': 'Viernes'
        }.get(fila['Dia'], fila['Dia'])
        
        if dia_completo not in dias:
            continue
            
        # Convertir horas a minutos
        # Asegúrate de que las columnas existan y el formato sea correcto
        try:
            inicio_clase = a_minutos(fila['Hora Inicio'])
            fin_clase = a_minutos(fila['Hora Fin'])
        except Exception:
            # Si hay un error en el formato de hora, saltar esta fila
            continue

        # Información del curso
        if filtro_tipo == "salon":
            info_curso = f"{fila['Curso']} - {fila.get('Seccion', '001')}\n{fila['Profesor']}"
        elif filtro_tipo == "profesor":
            info_curso = f"{fila['Curso']} - {fila.get('Seccion', '001')}\n{fila['Salon']}"
        else:
            info_curso = f"{fila['Curso']} - {fila.get('Seccion', '001')}\n{fila['Profesor']}\n{fila['Salon']}"
        
        # Buscar períodos que se solapan con la clase
        for periodo in periodos:
            if not (fin_clase <= periodo['inicio_min'] or inicio_clase >= periodo['fin_min']):
                if matriz_horario[periodo['periodo']][dia_completo] == '':
                    matriz_horario[periodo['periodo']][dia_completo] = info_curso
    
    # Mostrar título
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                border-radius: 10px; margin-bottom: 1rem;">
        <h2 style="color: white; margin: 0;">{titulo}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Crear DataFrame para la tabla
    tabla_data = []
    # Usar solo los períodos que tienen clases programadas
    periodos_con_clases = []
    for periodo_info in periodos:
        periodo = periodo_info['periodo']
        tiene_clases = any(matriz_horario[periodo][dia] != '' for dia in dias)
        if tiene_clases:
            periodos_con_clases.append(periodo_info)
    
    # Si no hay clases en el rango 7:30 a 19:30, mostrar un mensaje
    if not periodos_con_clases:
        st.info("No hay clases programadas en el rango de horario seleccionado (7:30 AM a 7:30 PM).")
        return
        
    for periodo_info in periodos_con_clases:
        periodo = periodo_info['periodo']
        fila_data = {'Períodos': periodo}
        for dia in dias:
            fila_data[dia] = matriz_horario[periodo][dia]
        tabla_data.append(fila_data)
    
    df_tabla = pd.DataFrame(tabla_data)
    
    # Aplicar estilos CSS para que se vea como la imagen
    st.markdown("""
    <style>
    .horario-tabla {
        font-family: 'Courier New', monospace;
        font-size: 12px;
        border-collapse: collapse;
        width: 100%;
        margin: 20px 0;
    }
    .horario-tabla th, .horario-tabla td {
        border: 1px solid #333;
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
        /* Colorear celdas con contenido */
        color: #333; /* Color de texto oscuro para contraste */
    }
    .horario-tabla .periodo-col {
        background-color: #e9e9e9;
        font-weight: bold;
        width: 120px;
    }
    /* Estilo para celdas con contenido (opcional, si se quiere un color diferente) */
    .horario-tabla td:not(.periodo-col):not(:empty) {
        background-color: #d1e7dd; /* Un color suave para las clases */
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Convertir DataFrame a HTML con estilos
    html_tabla = df_tabla.to_html(escape=False, index=False, classes='horario-tabla')
    
    # Personalizar el HTML para que se vea mejor (Reemplazar la columna de períodos)
    html_tabla = html_tabla.replace('<td>Períodos</td>', '<td class="periodo-col">Períodos</td>')
    
    # Aplicar clase especial a la columna de períodos
    for periodo_info in periodos_con_clases:
        periodo = periodo_info['periodo']
        html_tabla = html_tabla.replace(f'<td>{periodo}</td>', f'<td class="periodo-col">{periodo}</td>')
    
    st.markdown(html_tabla, unsafe_allow_html=True)
    
    # Estadísticas resumidas
    if not df_filtrado.empty:
        # Calcular duración total en horas (asumiendo que 'Duración' existe en df_horario)
        if 'Duración' not in df_filtrado.columns:
            # Si no existe la columna Duración, hay que recalcularla o estimarla
            df_filtrado['Duración'] = (df_filtrado['Hora Fin'].apply(a_minutos) - df_filtrado['Hora Inicio'].apply(a_minutos)) / 60
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📚 Total Cursos", df_filtrado['Curso'].nunique())
        with col2:
            if filtro_tipo != "profesor":
                st.metric("👨‍🏫 Profesores", df_filtrado['Profesor'].nunique())
            else:
                st.metric("⏰ Horas Semanales", f"{df_filtrado['Duración'].sum():.1f}")
        with col3:
            if filtro_tipo != "salon":
                st.metric("🏫 Salones", df_filtrado['Salon'].nunique())
            else:
                st.metric("📊 Clases Diferentes", len(df_filtrado))
        with col4:
            # La columna 'Estudiantes' debe ser numérica, se usa .sum() con seguridad
            total_estudiantes = df_filtrado['Estudiantes'].sum()
            st.metric("👥 Total Estudiantes", int(total_estudiantes) if pd.notna(total_estudiantes) else 0)

# ========================================================
# RESTO DEL CÓDIGO ORIGINAL (MANTENIDO)
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
            except Exception as e:
                st.warning(f"Error al cargar reservas: {e}")
                return {}
        return {}
    
    def guardar_reservas(self):
        try:
            with open(self.archivo_reservas, 'w', encoding='utf-8') as f:
                json.dump(self.reservas, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            st.error(f"Error al guardar reservas: {e}")
            return False
    
    def a_minutos(self, hhmm):
        h, m = map(int, hhmm.split(":"))
        return h * 60 + m

    def verificar_disponibilidad(self, salon, dia, hora_inicio, hora_fin, departamento_solicitante):
        for reserva_key, reserva_info in self.reservas.items():
            if reserva_info.get('salon') == salon and reserva_info.get('dia') == dia:
                res_inicio = reserva_info['hora_inicio']
                res_fin = reserva_info['hora_fin']
                
                inicio_min = self.a_minutos(hora_inicio)
                fin_min = self.a_minutos(hora_fin)
                res_inicio_min = self.a_minutos(res_inicio)
                res_fin_min = self.a_minutos(res_fin)
                
                if not (fin_min <= res_inicio_min or inicio_min >= res_fin_min):
                    departamento_reserva = reserva_info.get('departamento', '')
                    return False, departamento_reserva
        
        return True, None
    
    def reservar_salon(self, salon, dia, hora_inicio, hora_fin, departamento, programa, curso, profesor):
        clave_reserva = f"{salon}_{dia}_{hora_inicio}_{hora_fin}_{departamento}"
        
        self.reservas[clave_reserva] = {
            'salon': salon,
            'dia': dia,
            'hora_inicio': hora_inicio,
            'hora_fin': hora_fin,
            'departamento': departamento,
            'programa': programa,
            'curso': curso,
            'profesor': profesor,
            'fecha_reserva': datetime.now().isoformat()
        }
        
        return self.guardar_reservas()
    
    def liberar_reservas_departamento(self, departamento):
        claves_a_eliminar = []
        for clave, reserva in self.reservas.items():
            if reserva.get('departamento') == departamento:
                claves_a_eliminar.append(clave)
        
        for clave in claves_a_eliminar:
            del self.reservas[clave]
        
        return self.guardar_reservas()
    
    def obtener_reservas_departamento(self, departamento):
        reservas_departamento = {}
        for clave, reserva in self.reservas.items():
            if reserva.get('departamento') == departamento:
                reservas_departamento[clave] = reserva
        return reservas_departamento
    
    def obtener_salones_disponibles(self, dia, hora_inicio, hora_fin, departamento, lista_salones):
        salones_disponibles = []
        for salon in lista_salones:
            disponible, _ = self.verificar_disponibilidad(salon, dia, hora_inicio, hora_fin, departamento)
            if disponible:
                salones_disponibles.append(salon)
        return salones_disponibles
    
    def obtener_estadisticas_uso(self):
        stats = {
            'total_reservas': len(self.reservas),
            'departamentos_activos': len(set(r.get('departamento', '') for r in self.reservas.values())),
            'salones_en_uso': len(set(r.get('salon', '') for r in self.reservas.values())),
            'reservas_por_departamento': {},
            'reservas_por_salon': {}
        }
        
        for reserva in self.reservas.values():
            departamento = reserva.get('departamento', 'Sin departamento')
            salon = reserva.get('salon', 'Sin salón')
            
            stats['reservas_por_departamento'][departamento] = stats['reservas_por_departamento'].get(departamento, 0) + 1
            stats['reservas_por_salon'][salon] = stats['reservas_por_salon'].get(salon, 0) + 1
        
        return stats

# Configuración RUM (simplificada)
PROGRAMAS_RUM = {
    "COLEGIO DE ADMINISTRACIÓN DE EMPRESAS": {
        "color": "#FF6B6B",
        "salones_compartidos": len(AE_SALONES_FIJOS),
        "prefijo_salon": "AE",
        "sistema_reservas": True,
        "generacion_unificada": True,
        "horarios_exactos": True,
        "niveles": {
            "Bachilleratos en Administración de Empresas": [
                "Contabilidad", "Finanzas", "Gerencia de Recursos Humanos",
                "Mercadeo", "Gerencia de Operaciones", "Sistemas Computadorizados de Información",
                "Administración de Oficinas"
            ]
        }
    },
    "DEPARTAMENTO DE MATEMÁTICAS": {
        "color": "#9B59B6",
        "salones_compartidos": len(MATEMATICAS_SALONES_FIJOS),
        "prefijo_salon": "M",
        "sistema_reservas": True,
        "generacion_unificada": True,
        "horarios_exactos": True,
        "niveles": {
            "Bachilleratos en Matemáticas": [
                "Matemáticas Aplicadas", "Matemáticas Puras", "Matemática Estadística",
                "Educación Matemática", "Ciencias de la Computación"
            ]
        }
    },
    "COLEGIO DE ARTES Y CIENCIAS": {
        "color": "#4ECDC4",
        "salones_compartidos": len(ARTES_CIENCIAS_SALONES_COMPARTIDOS),
        "prefijo_salon": "AC",
        "sistema_reservas": True,
        "generacion_unificada": False,
        "horarios_exactos": False,
        "niveles": {
            "Bachilleratos en Artes y Ciencias": [
                "Literatura Comparada", "Filosofía", "Artes Plásticas", "Economía",
                "Inglés", "Historia", "Ciencias Políticas", "Sociología",
                "Estudios Hispánicos", "Educación Física", "Psicología",
                "Biología", "Microbiología Industrial", "Pre-Médica", "Biotecnología Industrial",
                "Química", "Geología", "Matemáticas – Matemática Pura", "Enfermería",
                "Física", "Ciencias Marinas"
            ]
        }
    },
    "COLEGIO DE CIENCIAS AGRÍCOLAS": {
        "color": "#F39C12",
        "salones_compartidos": 0,
        "prefijo_salon": "CA",
        "sistema_reservas": False,
        "generacion_unificada": False,
        "horarios_exactos": False,
        "niveles": {
            "Bachilleratos en Ciencias Agrícolas": [
                "Agronomía", "Economía Agrícola", "Horticultura", 
                "Ciencia Animal", "Protección de Cultivos", "Agronegocios"
            ]
        }
    },
    "COLEGIO DE INGENIERÍA": {
        "color": "#3498DB",
        "salones_compartidos": 0,
        "prefijo_salon": "ING",
        "sistema_reservas": False,
        "generacion_unificada": False,
        "horarios_exactos": False,
        "niveles": {
            "Bachilleratos en Ingeniería": [
                "Ingeniería Química", "Ingeniería Civil", "Ingeniería de Computadoras",
                "Ciencias e Ingeniería de la Computación", "Ingeniería Eléctrica",
                "Ingeniería Industrial", "Ingeniería Mecánica", "Ingeniería de Software"
            ]
        }
    }
}

# Clases y estructuras de datos (mantenidas igual)
class AsignacionClase:
    def __init__(self, curso_info, profesor, bloque, hora_inicio, salon):
        self.curso = curso_info["curso"]
        self.profesor = profesor
        self.bloque = bloque
        self.hora_inicio = hora_inicio
        self.salon = salon
        self.creditos = curso_info["creditos"]
        self.estudiantes = curso_info["estudiantes"]
        self.programa = curso_info["programa"]
        self.seccion = curso_info["seccion"]

    def to_dict(self):
        # Generar una fila por día/duración del bloque
        filas = []
        for dia, duracion in zip(self.bloque["dias"], self.bloque["horas"]):
            inicio_min = a_minutos(self.hora_inicio)
            fin_min = inicio_min + int(duracion * 60)
            
            # Convertir minutos de vuelta a HH:MM
            def min_a_hhmm(minutos):
                h = minutos // 60
                m = minutos % 60
                return f"{h:02d}:{m:02d}"

            filas.append({
                "Curso": self.curso,
                "Seccion": self.seccion,
                "Programa": self.programa,
                "Profesor": self.profesor,
                "Créditos": self.creditos,
                "Estudiantes": self.estudiantes,
                "Dia": dia,
                "Hora Inicio": self.hora_inicio,  # Hora de inicio del bloque
                "Hora Fin": min_a_hhmm(fin_min), # Hora de fin de la clase
                "Duración": duracion, # Duración en horas
                "Salon": self.salon
            })
        return filas

# Configuración del sistema (simplificada)
class ConfiguracionSistema:
    def __init__(self, archivo_excel=None, programa_actual=None, colegio_actual=None, departamento_actual=None):
        self.archivo_excel = archivo_excel
        self.programa_actual = programa_actual
        self.colegio_actual = colegio_actual
        self.departamento_actual = departamento_actual
        self.profesores_config = {}
        self.salones = []
        self.cursos_df = None
        
        # Configuración específica del colegio
        self.es_generacion_unificada = False
        self.usa_horarios_exactos = False
        self.usa_reservas = False
        self.prefijo_salon = ""
        
        if colegio_actual and colegio_actual in PROGRAMAS_RUM:
            colegio_info = PROGRAMAS_RUM[colegio_actual]
            self.usa_reservas = colegio_info.get('sistema_reservas', False)
            self.es_generacion_unificada = colegio_info.get('generacion_unificada', False)
            self.usa_horarios_exactos = colegio_info.get('horarios_exactos', False)
            self.prefijo_salon = colegio_info.get('prefijo_salon', '')
        
        self.sistema_reservas = SistemaReservasSalones() if self.usa_reservas else None
        
        self.restricciones_globales = {
            "horarios_prohibidos": self._obtener_restricciones_colegio(),
            "hora_inicio_min": "07:30",
            "hora_fin_max": "19:30",
            "estudiantes_max_salon": 40
        }
        
        self.pesos_restricciones = {
            "hard_conflictos": 1000000,
            "hard_disponibilidad": 1000000,
            "hard_salon_disponible": 1000000,
            "hard_tres_horas": 10000, # Ponerlo como hard para los colegios que lo requieran
            "horario_preferido": 50, # Bonus por cumplir
            "estudiantes_por_salon": 10, # Penalización por exceso
            "cambio_salon": 5 # Penalización por cambiar de salón (si aplica)
        }
        
        if self.archivo_excel:
            self._cargar_datos_excel()

    def _obtener_restricciones_colegio(self):
        """Define horarios prohibidos específicos por colegio (Ej. Convocatorias)"""
        restricciones = {}
        if self.colegio_actual in ["COLEGIO DE ADMINISTRACIÓN DE EMPRESAS", "COLEGIO DE ARTES Y CIENCIAS"]:
            # Martes y Jueves de 10:30 a 12:30 para convocatorias
            restricciones['Ma'] = [("10:30", "12:30")]
            restricciones['Ju'] = [("10:30", "12:30")]
        # Se pueden añadir más restricciones específicas aquí
        return restricciones

    def _cargar_datos_excel(self):
        """Carga y procesa el archivo Excel"""
        try:
            df = pd.read_excel(self.archivo_excel)
        except Exception as e:
            st.error(f"❌ Error al leer el archivo Excel: {e}")
            return
        
        # 1. Mapeo de columnas (se mantiene la lógica de mapeo flexible)
        mapeo_columnas = {
            'profesor': ['profesor', 'docente', 'teacher', 'instructor'],
            'curso': ['curso', 'materia', 'asignatura', 'subject', 'course'],
            'creditos': ['creditos', 'créditos', 'credits', 'horas'],
            'estudiantes': ['estudiantes', 'alumnos', 'students', 'enrollment', 'seccion'],
            'programa': ['programa', 'program', 'carrera', 'major'],
            'seccion': ['seccion', 'section', 'sec', 'grupo']
        }
        
        columnas_finales = {}
        for campo, posibles in mapeo_columnas.items():
            for col in df.columns:
                # Normalizar columnas para mejor coincidencia
                col_normalizada = col.lower().replace('.', '').replace('-', '').strip()
                if any(pos in col_normalizada for pos in posibles):
                    columnas_finales[campo] = col
                    break
        
        # st.write(f"🔗 Mapeo de columnas: {columnas_finales}")

        if 'profesor' not in columnas_finales or 'curso' not in columnas_finales:
            st.error("❌ Error: No se encontraron las columnas básicas (profesor, curso) en el archivo.")
            return

        # 2. Valores por defecto para columnas faltantes (mantenido igual)
        if 'creditos' not in columnas_finales:
            df['creditos_default'] = 3
            columnas_finales['creditos'] = 'creditos_default'
            st.warning("⚠️ No se encontró columna de créditos, usando 3 por defecto.")
        
        if 'estudiantes' not in columnas_finales:
            df['estudiantes_default'] = 30
            columnas_finales['estudiantes'] = 'estudiantes_default'
            st.warning("⚠️ No se encontró columna de estudiantes, usando 30 por defecto.")
            
        if 'programa' not in columnas_finales:
            df['programa_default'] = self.programa_actual or 'Programa General'
            columnas_finales['programa'] = 'programa_default'
            # st.warning("⚠️ No se encontró columna de programa, usando el programa actual por defecto.")
            
        if 'seccion' not in columnas_finales:
            df['seccion_default'] = '001'
            columnas_finales['seccion'] = 'seccion_default'
            # st.warning("⚠️ No se encontró columna de sección, usando '001' por defecto.")
            
        # 3. Preparar DataFrame final
        columnas_a_mantener = list(columnas_finales.values())
        df_cursos = df[columnas_a_mantener].rename(columns={v: k for k, v in columnas_finales.items()})
        df_cursos['creditos'] = df_cursos['creditos'].astype(int)
        df_cursos['estudiantes'] = df_cursos['estudiantes'].fillna(30).astype(int)
        df_cursos['seccion'] = df_cursos['seccion'].astype(str)
        
        # Filtrar por el programa actual (si la columna programa está presente y se definió un programa actual)
        if self.programa_actual and 'programa' in df_cursos.columns:
            df_cursos = df_cursos[df_cursos['programa'].astype(str).str.strip() == self.programa_actual].copy()
            if df_cursos.empty:
                 st.error(f"❌ No se encontraron cursos para el programa: **{self.programa_actual}**")
                 return
        
        self.cursos_df = df_cursos
        
        # 4. Configurar profesores y cursos por profesor
        self.profesores_config = {}
        for profesor in df_cursos['profesor'].unique():
            cursos_profesor = df_cursos[df_cursos['profesor'] == profesor].to_dict('records')
            self.profesores_config[profesor] = {
                "cursos": cursos_profesor,
                "horario_no_disponible": {}, # Ejemplo: {'Lu': [('08:30', '09:30')]}
                "horario_preferido": {} # Ejemplo: {'Ma': [('13:30', '15:00')]}
            }
            
        # 5. Definir salones disponibles
        if self.prefijo_salon == "AE":
            self.salones = AE_SALONES_FIJOS
        elif self.prefijo_salon == "M":
            self.salones = MATEMATICAS_SALONES_FIJOS
        elif self.prefijo_salon == "AC":
            self.salones = ARTES_CIENCIAS_SALONES_COMPARTIDOS
        else:
            # Aquí se pueden añadir salones específicos para Ing o CA si se definen
            self.salones = [f"{self.prefijo_salon} {i:03d}" for i in range(1, 11)] # Salones genéricos
        
        st.success(f"✅ Datos cargados: {len(self.profesores_config)} profesores, {len(self.salones)} salones")

# Funciones auxiliares (mantenidas igual)
def generar_bloques():
    """Define los bloques de tiempo válidos para la generación de horarios."""
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
    bloques.append({"id": id_counter, "dias": ["Lu","Mi"], "horas": [1.5,1.5], "creditos": 3})
    id_counter += 1

    # Bloques de 5 créditos
    combinaciones_5creditos = [
        (["Lu","Mi","Vi"], [2,2,1]), (["Lu","Ma","Mi","Vi"], [1,1,1,2]), 
        (["Lu","Ma","Ju","Vi"], [1,1,1,2]), (["Lu","Mi","Ju"], [2,1,2]),
    ]
    for dias, horas in combinaciones_5creditos:
        bloques.append({"id": id_counter, "dias": dias, "horas": horas, "creditos": 5})
        id_counter += 1
        
    # Bloques de 1 y 2 créditos (Laboratorios o Seminarios)
    for dia in ["Lu", "Ma", "Mi", "Ju", "Vi"]:
        bloques.append({"id": id_counter, "dias": [dia], "horas": [1], "creditos": 1})
        id_counter += 1
        bloques.append({"id": id_counter, "dias": [dia], "horas": [2], "creditos": 2})
        id_counter += 1
        bloques.append({"id": id_counter, "dias": [dia], "horas": [3], "creditos": 3}) # Bloque de 3h un solo día
        id_counter += 1
        
    # Bloque 3 créditos: L/M/W 1.5/0/1.5 (solo dos días)
    bloques.append({"id": id_counter, "dias": ["Lu","Mi"], "horas": [1.5,1.5], "creditos": 3}) 
    id_counter += 1
    
    # Bloque 3 créditos: L/M/W 1/1/1
    bloques.append({"id": id_counter, "dias": ["Lu","Mi","Vi"], "horas": [1,1,1], "creditos": 3}) 
    id_counter += 1

    # Filtro para solo bloques de 3 créditos (para simplificar en caso de que sea necesario)
    # bloques = [b for b in bloques if b["creditos"] == 3] 

    return bloques

def generar_horas_inicio():
    """Genera las posibles horas de inicio cada 30 minutos (7:30 - 18:30)"""
    horas = []
    inicio_min = a_minutos("07:30")
    fin_min = a_minutos("18:30") 
    
    tiempo_actual = inicio_min
    while tiempo_actual <= fin_min:
        h = tiempo_actual // 60
        m = tiempo_actual % 60
        horas.append(f"{h:02d}:{m:02d}")
        tiempo_actual += 30
    return horas

def es_bloque_tres_horas_valido(dia, hora_inicio, duracion, creditos):
    """Verifica si una clase de 3 horas consecutivas cumple con la restricción de empezar a tiempo"""
    if creditos == 3 and duracion == 3.0:
        if dia in ['Lu', 'Mi', 'Vi']:
            return a_minutos(hora_inicio) % 60 == 30 # Debe empezar a las XX:30
        elif dia in ['Ma', 'Ju']:
            return a_minutos(hora_inicio) % 60 == 0 # Debe empezar a las XX:00
    return True

def horario_valido(dia, hora_inicio, duracion, profesor, creditos, config: ConfiguracionSistema):
    """Verifica si la clase cumple con las restricciones de tiempo (globales y de profesor)"""
    ini_min = a_minutos(hora_inicio)
    fin_min = ini_min + int(duracion * 60)
    
    # 1. Restricciones de tiempo global
    if fin_min > a_minutos(config.restricciones_globales["hora_fin_max"]) or \
       ini_min < a_minutos(config.restricciones_globales["hora_inicio_min"]): 
        return False
        
    # 2. Restricción específica de 3 horas (si aplica)
    if config.usa_horarios_exactos and creditos and not es_bloque_tres_horas_valido(dia, hora_inicio, duracion, creditos): 
        return False
        
    # 3. Horarios prohibidos globales (Ej. Convocatorias)
    restricciones_horario = config.restricciones_globales["horarios_prohibidos"]
    if dia in restricciones_horario:
        for r_ini, r_fin in restricciones_horario[dia]:
            r_ini_min = a_minutos(r_ini)
            r_fin_min = a_minutos(r_fin)
            if not (fin_min <= r_ini_min or ini_min >= r_fin_min):
                return False

    # 4. Horarios no disponibles del profesor
    if profesor and profesor in config.profesores_config:
        prof_config = config.profesores_config[profesor]
        if dia in prof_config["horario_no_disponible"]:
            for r_ini, r_fin in prof_config["horario_no_disponible"][dia]:
                r_ini_min = a_minutos(r_ini)
                r_fin_min = a_minutos(r_fin)
                if not (fin_min <= r_ini_min or ini_min >= r_fin_min):
                    return False
    
    return True

def cumple_horario_preferido(dia, hora_inicio, duracion, profesor, config: ConfiguracionSistema):
    """Verifica si la clase cae dentro del horario preferido del profesor (para calcular bonus)"""
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
        
        # El curso está contenido completamente dentro del horario preferido
        if ini_min >= pref_ini_min and fin_min <= pref_fin_min:
            return True
            
    return False

def hay_conflictos(nueva_asignacion: AsignacionClase, asignaciones_existentes: list[AsignacionClase]):
    """Verifica conflictos de tiempo con asignaciones existentes (Profesor, Salón, Curso)"""
    
    dias_nueva = nueva_asignacion.bloque["dias"]
    duraciones_nueva = nueva_asignacion.bloque["horas"]
    inicio_min_nueva = a_minutos(nueva_asignacion.hora_inicio)
    
    for asig_existente in asignaciones_existentes:
        # Conflicto de Profesor
        if nueva_asignacion.profesor == asig_existente.profesor:
            # Iterar sobre los días del bloque existente
            dias_existente = asig_existente.bloque["dias"]
            duraciones_existente = asig_existente.bloque["horas"]
            inicio_min_existente = a_minutos(asig_existente.hora_inicio)
            
            for dia_nueva, duracion_nueva in zip(dias_nueva, duraciones_nueva):
                fin_min_nueva = inicio_min_nueva + int(duracion_nueva * 60)
                
                for dia_existente, duracion_existente in zip(dias_existente, duraciones_existente):
                    if dia_nueva == dia_existente:
                        fin_min_existente = inicio_min_existente + int(duracion_existente * 60)
                        
                        # Hay solapamiento de tiempo
                        if not (fin_min_nueva <= inicio_min_existente or inicio_min_nueva >= fin_min_existente):
                            # Evitar el conflicto si se trata de la misma clase (por si se reevalúa)
                            if nueva_asignacion.curso == asig_existente.curso and nueva_asignacion.seccion == asig_existente.seccion:
                                continue 
                                
                            return True # Conflicto de Profesor

        # Conflicto de Salón
        if nueva_asignacion.salon == asig_existente.salon:
            dias_existente = asig_existente.bloque["dias"]
            duraciones_existente = asig_existente.bloque["horas"]
            inicio_min_existente = a_minutos(asig_existente.hora_inicio)
            
            for dia_nueva, duracion_nueva in zip(dias_nueva, duraciones_nueva):
                fin_min_nueva = inicio_min_nueva + int(duracion_nueva * 60)
                
                for dia_existente, duracion_existente in zip(dias_existente, duraciones_existente):
                    if dia_nueva == dia_existente:
                        fin_min_existente = inicio_min_existente + int(duracion_existente * 60)
                        
                        if not (fin_min_nueva <= inicio_min_existente or inicio_min_nueva >= fin_min_existente):
                            return True # Conflicto de Salón
                            
    # Conflicto de Curso (evitar asignar el mismo curso/sección dos veces)
    for asig_existente in asignaciones_existentes:
        if nueva_asignacion.curso == asig_existente.curso and nueva_asignacion.seccion == asig_existente.seccion:
            # Esto solo debería ocurrir si el algoritmo es defectuoso, pero es una buena verificación de seguridad
            return True 
            
    return False

def generar_horario_valido(config: ConfiguracionSistema, bloques, horas_inicio):
    """Genera un horario completo (una solución inicial) con todas las restricciones HARD"""
    asignaciones = []
    
    # Ordenar profesores por la cantidad de cursos que dan (heurística simple)
    profesores_ordenados = sorted(
        config.profesores_config.keys(), 
        key=lambda p: len(config.profesores_config[p]["cursos"]), 
        reverse=True
    )
    
    # Shuffle para asegurar variedad en la búsqueda
    random.shuffle(profesores_ordenados) 
    
    for profesor in profesores_ordenados:
        prof_config = config.profesores_config[profesor]
        
        for curso_info in prof_config["cursos"]:
            encontrado = False
            
            # Bloques compatibles con los créditos del curso
            bloques_compatibles = [b for b in bloques if b["creditos"] == curso_info["creditos"]]
            
            # Si no hay bloque exacto, tomar los 5 más cercanos (para permitir flexibilidad en la optimización)
            if not bloques_compatibles:
                bloques_compatibles = sorted(bloques, key=lambda x: abs(x["creditos"] - curso_info["creditos"]))[:5]
            
            # Intentos para encontrar una asignación válida para un curso
            max_intentos_curso = 100 
            intentos_curso = 0
            
            while not encontrado and intentos_curso < max_intentos_curso:
                intentos_curso += 1
                
                bloque = random.choice(bloques_compatibles)
                hora_inicio = random.choice(horas_inicio)
                
                salones_dia = []
                valido_horario = True
                
                # 1. Verificar el horario (incluye disponibilidad de profesor y restricciones globales)
                for dia, duracion in zip(bloque["dias"], bloque["horas"]):
                    if not horario_valido(dia, hora_inicio, duracion, profesor, curso_info["creditos"], config):
                        valido_horario = False
                        break
                        
                if not valido_horario:
                    continue
                
                # 2. Verificar disponibilidad de salón (incluye reservas si aplica)
                salones_disponibles_bloque = []
                for dia, duracion in zip(bloque["dias"], bloque["horas"]):
                    # Calcular la hora de fin
                    ini_min = a_minutos(hora_inicio)
                    fin_min = ini_min + int(duracion * 60)
                    hora_fin = f"{fin_min // 60:02d}:{fin_min % 60:02d}"
                    
                    if config.usa_reservas:
                        # Usar el sistema de reservas para encontrar salones disponibles
                        salones_dia = config.sistema_reservas.obtener_salones_disponibles(
                            dia, hora_inicio, hora_fin, config.departamento_actual, config.salones
                        )
                    else:
                        # Si no hay reservas, todos los salones base están disponibles (por ahora)
                        salones_dia = config.salones 
                        
                    if not salones_dia:
                        valido_horario = False
                        break
                        
                    if not salones_disponibles_bloque:
                        salones_disponibles_bloque = salones_dia
                    else:
                        # Intersección de salones disponibles para todos los días del bloque
                        salones_disponibles_bloque = list(set(salones_disponibles_bloque) & set(salones_dia))
                        
                if not valido_horario or not salones_disponibles_bloque:
                    continue
                
                # 3. Asignar salón y verificar conflictos con asignaciones previas
                salon_elegido = random.choice(salones_disponibles_bloque)
                nueva_asignacion = AsignacionClase(curso_info, profesor, bloque, hora_inicio, salon_elegido)
                
                if not hay_conflictos(nueva_asignacion, asignaciones):
                    asignaciones.append(nueva_asignacion)
                    encontrado = True
                    break # Salir del bucle de intentos del curso
            
            # Si no se pudo asignar el curso después de los intentos
            if not encontrado:
                # Retornar None para indicar que la generación falló
                # st.warning(f"No se pudo asignar el curso {curso_info['curso']} de {profesor}. Intentando regenerar...")
                return None 

    return asignaciones

# Función de Generación con Reservas (Mantenida igual)
def generar_horario_valido_con_reservas(config: ConfiguracionSistema, bloques, horas_inicio):
    """
    Genera un horario y realiza la reserva de salones. 
    Se intenta generar el horario, si es válido, se procede a reservar.
    """
    
    # 1. Generar el horario sin la restricción de reservas
    asignaciones = generar_horario_valido(config, bloques, horas_inicio)
    
    if asignaciones is None:
        return None
    
    # 2. Verificar la disponibilidad de las reservas para todo el horario (Restricción HARD)
    reservas_pendientes = []
    conflictos_reserva = False
    
    for asig in asignaciones:
        for dia, duracion in zip(asig.bloque["dias"], asig.bloque["horas"]):
            ini_min = a_minutos(asig.hora_inicio)
            fin_min = ini_min + int(duracion * 60)
            hora_fin = f"{fin_min // 60:02d}:{fin_min % 60:02d}"
            
            disponible, depto_conflicto = config.sistema_reservas.verificar_disponibilidad(
                asig.salon, dia, asig.hora_inicio, hora_fin, config.departamento_actual
            )
            
            if not disponible and depto_conflicto != config.departamento_actual:
                # El salón está reservado por otro departamento
                conflictos_reserva = True
                # st.error(f"❌ Conflicto de reserva: Salón {asig.salon}, Día {dia}, con {depto_conflicto}")
                return None # Fallar inmediatamente si hay un conflicto de reserva
            
            # Si está disponible o si es una reserva propia (se ignora por ahora, se hace la lista)
            reservas_pendientes.append({
                'salon': asig.salon,
                'dia': dia,
                'hora_inicio': asig.hora_inicio,
                'hora_fin': hora_fin,
                'departamento': config.departamento_actual,
                'programa': asig.programa,
                'curso': asig.curso,
                'profesor': asig.profesor
            })

    # 3. Si no hay conflictos con otras reservas, se procede a reservar
    if not conflictos_reserva:
        # Liberar reservas propias anteriores para el mismo departamento (limpieza)
        config.sistema_reservas.liberar_reservas_departamento(config.departamento_actual)
        
        # Realizar nuevas reservas
        for reserva in reservas_pendientes:
            config.sistema_reservas.reservar_salon(
                reserva['salon'], reserva['dia'], reserva['hora_inicio'], reserva['hora_fin'], 
                reserva['departamento'], reserva['programa'], reserva['curso'], reserva['profesor']
            )
            
        return asignaciones
    
    return None # Falló por conflicto de reserva


def calcular_score(asignaciones: list[AsignacionClase], config: ConfiguracionSistema):
    """Calcula el score (fitness) de una solución usando penalizaciones y bonus."""
    
    if not asignaciones:
        return -float('inf')
        
    penalizacion = 0
    bonus = 0
    pesos = config.pesos_restricciones

    # --- Soft Constraints y Penalizaciones ---

    # 1. Horario preferido del profesor (BONUS)
    for asig in asignaciones:
        for dia, duracion in zip(asig.bloque["dias"], asig.bloque["horas"]):
            if cumple_horario_preferido(dia, asig.hora_inicio, duracion, asig.profesor, config):
                bonus += pesos["horario_preferido"]

    # 2. Capacidad del salón (PENALIZACIÓN)
    for asig in asignaciones:
        if asig.estudiantes > config.restricciones_globales["estudiantes_max_salon"]:
            penalizacion += pesos["estudiantes_por_salon"] * (asig.estudiantes - config.restricciones_globales["estudiantes_max_salon"])
    
    # 3. Penalización por bloques de 3 horas si no cumplen la restricción (SOFT)
    if not config.usa_horarios_exactos:
        for asig in asignaciones:
            for dia, duracion in zip(asig.bloque["dias"], asig.bloque["horas"]):
                if asig.creditos == 3 and duracion == 3.0:
                    if dia in ['Lu', 'Mi', 'Vi'] and a_minutos(asig.hora_inicio) % 60 != 30:
                        penalizacion += 1000 # Penalización por empezar en hora incorrecta L/M/V
                    elif dia in ['Ma', 'Ju'] and a_minutos(asig.hora_inicio) % 60 != 0:
                        penalizacion += 1000 # Penalización por empezar en hora incorrecta M/J
    
    # --- Hard Constraints (Se asume que la función de generación ya las maneja, 
    # pero se re-verifica aquí para la función de Mutación/Cruzamiento si se usara AG completo)

    # 4. Conflictos de Tiempo (Profesor/Salón)
    for i in range(len(asignaciones)):
        for j in range(i + 1, len(asignaciones)):
            asig1 = asignaciones[i]
            asig2 = asignaciones[j]
            if hay_conflictos(asig1, [asig2]):
                penalizacion += pesos["hard_conflictos"] # Penalización muy alta

    # 5. Restricción de 3 horas (si es HARD)
    if config.usa_horarios_exactos:
        for asig in asignaciones:
            for dia, duracion in zip(asig.bloque["dias"], asig.bloque["horas"]):
                if not es_bloque_tres_horas_valido(dia, asig.hora_inicio, duracion, asig.creditos):
                    penalizacion += pesos["hard_tres_horas"]

    return bonus - penalizacion

def buscar_mejor_horario(config: ConfiguracionSistema, bloques, horas_inicio, intentos=250):
    """Búsqueda iterativa de un buen horario (simulación de AG simple)"""
    mejor_asignaciones = None
    mejor_score = -float('inf')
    
    # Solo mostrar barra de progreso si hay datos cargados
    if not config.profesores_config:
        return None, 0
        
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(intentos):
        progress_bar.progress((i + 1) / intentos)
        status_text.text(f"🔄 Generando horarios... {i+1}/{intentos}")
        
        try:
            if config.usa_reservas:
                # Usar la función con manejo de reservas
                asignaciones = generar_horario_valido_con_reservas(config, bloques, horas_inicio)
            else:
                # Usar la función estándar
                asignaciones = generar_horario_valido(config, bloques, horas_inicio)
            
            if asignaciones is not None:
                score = calcular_score(asignaciones, config)
                
                if score > mejor_score:
                    mejor_score = score
                    mejor_asignaciones = asignaciones
                    
        except Exception as e:
            # Capturar errores durante la generación para no interrumpir el proceso
            # st.error(f"Error en la iteración {i}: {e}")
            pass
            
    progress_bar.empty()
    status_text.empty()
    
    if mejor_asignaciones is not None:
        st.success(f"✅ Horario Optimizado Encontrado (Score: {mejor_score:.2f})")
    else:
        st.error("❌ No se pudo generar un horario válido.")
        
    return mejor_asignaciones, mejor_score

def generar_colores_cursos(df_horario):
    """Genera un color único para cada curso/materia"""
    cursos_unicos = df_horario['Curso'].unique()
    colores_map = {}
    
    # Seed para que los colores sean consistentes entre ejecuciones
    random.seed(42) 
    
    # Generar colores brillantes
    for curso in cursos_unicos:
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        colores_map[curso] = f'rgb({r},{g},{b})'
        
    return colores_map

# Funciones de visualización de interfaz (mantenidas igual, excepto la nueva tabla)
def mostrar_estado_reservas(config: ConfiguracionSistema):
    """Muestra el estado actual de las reservas para el departamento actual"""
    if config.sistema_reservas:
        reservas_propias = config.sistema_reservas.obtener_reservas_departamento(config.departamento_actual)
        st.sidebar.subheader("🔒 Estado de Reservas")
        st.sidebar.info(f"**{config.departamento_actual}** tiene **{len(reservas_propias)}** reservas activas.")
        
        if len(reservas_propias) > 0:
            with st.sidebar.expander("Ver reservas propias"):
                reservas_df = pd.DataFrame(reservas_propias.values())
                reservas_df = reservas_df[['dia', 'hora_inicio', 'hora_fin', 'salon', 'curso']]
                st.dataframe(reservas_df, use_container_width=True)
                
        stats = config.sistema_reservas.obtener_estadisticas_uso()
        with st.sidebar.expander("Estadísticas de Uso Total"):
            st.metric("Total Reservas Sistema", stats['total_reservas'])
            st.metric("Salones en Uso", stats['salones_en_uso'])
            st.metric("Deptos. Activos", stats['departamentos_activos'])

def mostrar_configuracion_profesor(config: ConfiguracionSistema):
    """Interfaz para configurar restricciones de profesores"""
    
    profesores = sorted(list(config.profesores_config.keys()))
    profesor_seleccionado = st.sidebar.selectbox("👨‍🏫 Seleccionar Profesor", profesores)
    
    if profesor_seleccionado:
        st.sidebar.markdown("---")
        st.sidebar.subheader("❌ Restricciones de Disponibilidad")
        
        # Interfaz de Horarios No Disponibles (Restricción HARD)
        st.sidebar.caption("Horas que el profesor NO puede dar clases.")
        prof_config = config.profesores_config[profesor_seleccionado]
        
        dias = ["Lu", "Ma", "Mi", "Ju", "Vi"]
        for dia in dias:
            with st.sidebar.expander(f"Bloque No Disponible {dia}", expanded=False):
                col1_no, col2_no = st.columns(2)
                
                # Usar una clave única para cada elemento
                key_start = f"no_disponible_{profesor_seleccionado}_{dia}_inicio"
                key_end = f"no_disponible_{profesor_seleccionado}_{dia}_fin"
                
                # Se utiliza st.time_input para facilitar la entrada de hora
                inicio_no = st.time_input(f"{dia} inicio", value=datetime.strptime("00:00", "%H:%M").time(), key=key_start)
                fin_no = st.time_input(f"{dia} fin", value=datetime.strptime("00:00", "%H:%M").time(), key=key_end)
                
                # Guardar la restricción si no es 00:00
                if inicio_no != datetime.strptime("00:00", "%H:%M").time():
                    if "horario_no_disponible" not in prof_config:
                        prof_config["horario_no_disponible"] = {}
                    
                    if inicio_no.strftime("%H:%M") != fin_no.strftime("%H:%M"):
                        prof_config["horario_no_disponible"][dia] = [
                            (inicio_no.strftime("%H:%M"), fin_no.strftime("%H:%M"))
                        ]
                        st.success(f"Guardado: {dia} de {inicio_no.strftime('%H:%M')} a {fin_no.strftime('%H:%M')}")
                    else:
                        st.error("La hora de inicio y fin no pueden ser iguales.")
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("⭐ Horario Preferido")
        st.sidebar.caption("Horas que el profesor PREFIERE dar clases. (BONUS)")
        
        # Interfaz de Horarios Preferidos (Restricción SOFT)
        for dia in dias:
            with st.sidebar.expander(f"Bloque Preferido {dia}", expanded=False):
                col1_pref, col2_pref = st.columns(2)
                
                # Usar una clave única para cada elemento
                key_start_pref = f"preferido_{profesor_seleccionado}_{dia}_inicio"
                key_end_pref = f"preferido_{profesor_seleccionado}_{dia}_fin"
                
                inicio_pref = st.time_input(f"{dia} inicio", value=datetime.strptime("00:00", "%H:%M").time(), key=key_start_pref)
                fin_pref = st.time_input(f"{dia} fin", value=datetime.strptime("00:00", "%H:%M").time(), key=key_end_pref)
                
                # Guardar el horario preferido si no es 00:00
                if inicio_pref != datetime.strptime("00:00", "%H:%M").time():
                    if "horario_preferido" not in prof_config:
                        prof_config["horario_preferido"] = {}
                        
                    if inicio_pref.strftime("%H:%M") != fin_pref.strftime("%H:%M"):
                        prof_config["horario_preferido"][dia] = [
                            (inicio_pref.strftime("%H:%M"), fin_pref.strftime("%H:%M"))
                        ]
                        st.success(f"Guardado: {dia} de {inicio_pref.strftime('%H:%M')} a {fin_pref.strftime('%H:%M')}")
                    else:
                        st.error("La hora de inicio y fin no pueden ser iguales.")

def mostrar_calendario_visual(df_horario, colores_cursos, filtro_tipo="completo", filtro_valor=None):
    """Muestra un calendario visual del horario usando Plotly"""
    
    # Filtrar datos según el tipo
    if filtro_tipo == "profesor" and filtro_valor and filtro_valor != "Todos los profesores":
        df_filtrado = df_horario[df_horario['Profesor'] == filtro_valor]
        titulo_calendario = f"👨‍🏫 Horario del Profesor: {filtro_valor}"
    elif filtro_tipo == "programa" and filtro_valor and filtro_valor != "Todos los programas":
        df_filtrado = df_horario[df_horario['Programa'] == filtro_valor]
        titulo_calendario = f"📚 Horario del Programa: {filtro_valor}"
    elif filtro_tipo == "salon" and filtro_valor and filtro_valor != "Todos los salones":
        df_filtrado = df_horario[df_horario['Salon'] == filtro_valor]
        titulo_calendario = f"🏫 Horario del Salón: {filtro_valor}"
    else:
        df_filtrado = df_horario
        titulo_calendario = "📅 Calendario Semanal de Clases - Vista Completa"
    
    if df_filtrado.empty:
        st.warning("No hay datos para mostrar con los filtros seleccionados.")
        return

    # Mapeo de días a números para el eje X
    dias_map = {'Lu': 1, 'Ma': 2, 'Mi': 3, 'Ju': 4, 'Vi': 5}
    dias_nombres = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
    
    # Rango de horas en minutos (7:30 a 19:30)
    hora_min = a_minutos("07:30") 
    hora_max = a_minutos("19:30") 
    
    # Crear figura
    fig = make_subplots(rows=1, cols=1)

    # Preparar columnas por salón para cada día (para que no se solapen visualmente)
    salones_por_dia = {}
    for dia in dias_map.keys():
        salones_unicos = df_filtrado[df_filtrado['Dia'] == dia]['Salon'].unique().tolist()
        salones_por_dia[dia] = sorted(salones_unicos)

    # Procesar cada clase para crear los bloques
    for _, fila in df_filtrado.iterrows():
        dia = fila['Dia']
        if dia not in dias_map: continue
        dia_num = dias_map[dia]
        
        # Convertir horas a minutos para el eje Y
        try:
            inicio_min = a_minutos(fila['Hora Inicio'])
            fin_min = a_minutos(fila['Hora Fin'])
        except Exception:
            continue
            
        duracion_min = fin_min - inicio_min
        
        # Normalizar el eje X (para que no se solapen clases en el mismo día/hora)
        salones_dia = salones_por_dia.get(dia, [])
        total_cols = max(len(salones_dia), 1)
        salon_idx = salones_dia.index(fila['Salon']) if fila['Salon'] in salones_dia else 0
        
        # Ancho por columna para el salón (ajustar para que quepan 5 días)
        width_col = 0.8 / total_cols
        x_start = dia_num - 0.5 + (salon_idx * width_col)
        x_end = x_start + width_col
        x_center = (x_start + x_end) / 2
        
        # Asignar color basado en el curso
        color = colores_cursos.get(fila['Curso'], 'rgb(100,100,100)')

        # Texto del hover
        texto_hover = f"<b>{fila['Curso']} - {fila.get('Seccion', '001')}</b><br>" \
                      f"Programa: {fila['Programa']}<br>" \
                      f"Profesor: {fila['Profesor']}<br>" \
                      f"Salón: {fila['Salon']}<br>" \
                      f"Hora: {fila['Hora Inicio']} - {fila['Hora Fin']}"
                      
        # Crear la forma de la barra (clase)
        fig.add_shape(
            type="rect",
            xref="x", yref="y",
            x0=x_start, x1=x_end,
            y0=inicio_min, y1=fin_min,
            fillcolor=color,
            line=dict(color="black", width=1),
            opacity=0.9
        )
        
        # Agregar texto centrado en la barra
        texto_clase = f"{fila['Curso']}<br>{fila.get('Seccion', '001')}<br>{fila['Salon']}"
        fig.add_annotation(
            x=x_center, y=inicio_min + duracion_min / 2,
            text=texto_clase,
            showarrow=False,
            font=dict(size=10, color="white"),
            hovertext=texto_hover,
            hoverlabel=dict(bgcolor=color, font=dict(color="white"))
        )

    # Configuración del Layout
    fig.update_layout(
        title={
            'text': titulo_calendario,
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=24, color='#34495E')
        },
        xaxis=dict(
            tickmode='array',
            tickvals=[1.5, 2.5, 3.5, 4.5, 5.5],
            ticktext=dias_nombres,
            range=[0.5, 5.5], # Días de Lu a Vi
            showgrid=True,
            gridcolor='lightgray',
            title="Día de la Semana",
            title_font=dict(size=16, color='#34495E')
        ),
        yaxis=dict(
            tickmode='array',
            tickvals=[i*60 for i in range(7, 20)],
            ticktext=[f"{i:02d}:00" for i in range(7, 20)],
            range=[hora_max, hora_min], # Invertir el eje Y para que la mañana esté arriba
            showgrid=True,
            gridcolor='lightgray',
            title="Hora del Día",
            title_font=dict(size=16, color='#34495E')
        ),
        plot_bgcolor='white',
        paper_bgcolor='#F8F9FA',
        width=1600,
        height=1000,
        showlegend=False,
        margin=dict(l=80, r=80, t=100, b=80)
    )

    # Líneas de cuadrícula más prominentes para las horas
    for hora in range(8, 20):
        fig.add_hline(
            y=hora*60,
            line_dash="dot",
            line_color="gray",
            opacity=0.5
        )

    return fig

def mostrar_leyenda_cursos(colores_cursos, df_horario, filtro_tipo=None, filtro_valor=None):
    """Muestra una leyenda de colores para los cursos"""
    
    # Filtrar los cursos que realmente están en el horario actual
    if filtro_tipo and filtro_valor and filtro_valor not in ["Todos los profesores", "Todos los programas", "Todos los salones"]:
        if filtro_tipo == "profesor":
            cursos_filtrados = df_horario[df_horario['Profesor'] == filtro_valor]['Curso'].unique()
            titulo = f"🎨 Cursos de {filtro_valor}"
        elif filtro_tipo == "programa":
            cursos_filtrados = df_horario[df_horario['Programa'] == filtro_valor]['Curso'].unique()
            titulo = f"🎨 Cursos del Programa {filtro_valor}"
        elif filtro_tipo == "salon":
            cursos_filtrados = df_horario[df_horario['Salon'] == filtro_valor]['Curso'].unique()
            titulo = f"🎨 Cursos en Salón {filtro_valor}"
        else:
            cursos_filtrados = df_horario['Curso'].unique()
            titulo = "🎨 Leyenda de Cursos"
    else:
        cursos_filtrados = df_horario['Curso'].unique()
        titulo = "🎨 Leyenda de Cursos"
    
    st.subheader(titulo)
    
    # Crear dos columnas para mostrar la leyenda de manera más compacta
    cols = st.columns(min(3, len(cursos_filtrados)))
    col_idx = 0
    
    # Mostrar la leyenda de colores
    for curso in sorted(cursos_filtrados):
        color = colores_cursos.get(curso, 'rgb(100,100,100)')
        
        # Convertir rgb(r,g,b) a hex para Streamlit markdown
        def rgb_to_hex(rgb_str):
            r, g, b = map(int, rgb_str.replace('rgb(', '').replace(')', '').split(','))
            return f'#{r:02x}{g:02x}{b:02x}'
            
        hex_color = rgb_to_hex(color)
        
        with cols[col_idx]:
            st.markdown(f"""
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <div style="width: 15px; height: 15px; background-color: {hex_color}; border-radius: 3px; margin-right: 10px;"></div>
                <span style="font-size: 14px;">{curso}</span>
            </div>
            """, unsafe_allow_html=True)
            
        col_idx = (col_idx + 1) % len(cols)

def _creditos_unicos_por_profesor(df):
    """Calcula los créditos totales asignados a cada profesor (contando el curso una vez)"""
    if df.empty:
        return 0
    # Agrupar por Profesor y Curso para obtener los créditos únicos
    df_unique = df[['Profesor', 'Curso', 'Créditos']].drop_duplicates()
    return df_unique.groupby('Profesor')['Créditos'].sum()

def mostrar_tabs_horario_mejoradas(df_horario):
    """Renderiza las pestañas de visualización del horario MEJORADAS"""
    
    colores_cursos = generar_colores_cursos(df_horario)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📅 Tabla Profesional", "🎨 Calendario Visual", 
        "📊 Horario Completo", "👨‍🏫 Por Profesor", 
        "🏫 Por Salón", "📈 Estadísticas"
    ])

    # PESTAÑA 1: TABLA PROFESIONAL (NUEVA - ESTILO IMAGEN)
    with tab1:
        st.subheader("📅 Vista de Tabla Profesional")
        crear_tabla_horario_profesional(df_horario)
        st.markdown("---")
        mostrar_leyenda_cursos(colores_cursos, df_horario)


    # PESTAÑA 2: CALENDARIO VISUAL
    with tab2:
        st.subheader("🎨 Calendario Visual Interactivo")
        fig_cal = mostrar_calendario_visual(df_horario, colores_cursos)
        st.plotly_chart(fig_cal, use_container_width=True, key="plotly_calendario_completo")
        st.markdown("---")
        mostrar_leyenda_cursos(colores_cursos, df_horario)


    # PESTAÑA 3: HORARIO COMPLETO (DATAFRAME)
    with tab3:
        st.subheader("📊 Horario Completo (Datos Crudos)")
        st.info(f"Mostrando {len(df_horario)} bloques de clase asignados.")
        st.dataframe(df_horario, use_container_width=True)

    # PESTAÑA 4: POR PROFESOR
    with tab4:
        st.subheader("👨‍🏫 Horario por Profesor")
        profesores_unicos = ["Todos los profesores"] + sorted(df_horario['Profesor'].unique().tolist())
        filtro_profesor = st.selectbox("Seleccionar Profesor", profesores_unicos, key="filtro_profesor_tab")
        
        if filtro_profesor != "Todos los profesores":
            df_profesor = df_horario[df_horario['Profesor'] == filtro_profesor].sort_values(by=['Dia', 'Hora Inicio'])
            # Mostrar como tabla profesional
            crear_tabla_horario_profesional(df_horario, filtro_tipo="profesor", filtro_valor=filtro_profesor)
            st.markdown("---")
            mostrar_leyenda_cursos(colores_cursos, df_horario, filtro_tipo="profesor", filtro_valor=filtro_profesor)
        else:
            crear_tabla_horario_profesional(df_horario)
            st.markdown("---")
            mostrar_leyenda_cursos(colores_cursos, df_horario)

    # PESTAÑA 5: POR SALÓN
    with tab5:
        st.subheader("🏫 Horario por Salón")
        salones_unicos = ["Todos los salones"] + sorted(df_horario['Salon'].unique().tolist())
        filtro_salon = st.selectbox("Seleccionar Salón", salones_unicos, key="filtro_salon_tab")

        if filtro_salon != "Todos los salones":
            df_salon = df_horario[df_horario['Salon'] == filtro_salon].sort_values(by=['Dia', 'Hora Inicio'])
            # Mostrar como tabla profesional
            crear_tabla_horario_profesional(df_horario, filtro_tipo="salon", filtro_valor=filtro_salon)
            st.markdown("---")
            mostrar_leyenda_cursos(colores_cursos, df_horario, filtro_tipo="salon", filtro_valor=filtro_salon)
        else:
            crear_tabla_horario_profesional(df_horario)
            st.markdown("---")
            mostrar_leyenda_cursos(colores_cursos, df_horario)

    # PESTAÑA 6: ESTADÍSTICAS
    with tab6:
        st.subheader("📈 Estadísticas del Horario")

        # Créditos por profesor
        creditos_prof = _creditos_unicos_por_profesor(df_horario)
        fig_creditos = px.bar(
            x=creditos_prof.index, 
            y=creditos_prof.values, 
            title="Créditos Asignados por Profesor (por curso único)",
            color=list(creditos_prof.values),
            color_continuous_scale="viridis"
        )
        fig_creditos.update_layout(showlegend=False)
        st.plotly_chart(fig_creditos, use_container_width=True, key="plotly_creditos_general")

        # Utilización de salones
        uso_salones = df_horario.groupby('Salon').agg({
            'Duración': 'sum',
            'Curso': 'nunique'
        }).round(1)
        uso_salones.columns = ['Horas Totales', 'Cursos Diferentes']

        fig_salones = px.bar(
            uso_salones,
            x=uso_salones.index,
            y='Horas Totales',
            title="Utilización de Salones (Horas Totales por Semana)",
            color='Horas Totales',
            color_continuous_scale="blues"
        )
        st.plotly_chart(fig_salones, use_container_width=True, key="plotly_salones_general")


# Función principal de la aplicación (mantenida igual)
def main():
    st.set_page_config(
        page_title="Generador de Horarios RUM",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Inicializar estado de sesión
    if 'usuario_autenticado' not in st.session_state:
        st.session_state.usuario_autenticado = False

    # ------------------
    # MANEJO DE LOGIN
    # ------------------
    if not st.session_state.usuario_autenticado:
        mostrar_login_simplificado()
        return

    # ------------------
    # APLICACIÓN PRINCIPAL
    # ------------------
    
    # Mostrar header del usuario autenticado (CORREGIDO)
    mostrar_header_usuario_corregido()

    # Obtener información del usuario
    info_usuario = st.session_state.info_usuario
    st.info(f"🎯 **Generando horarios para**: {info_usuario['programa']} en el nivel {info_usuario['nivel']}")

    st.markdown("## 📁 Cargar Datos para Generación de Horarios")

    # Sidebar de configuración
    st.sidebar.header("⚙️ Configuración del Sistema")
    
    # Upload del archivo Excel en sidebar
    uploaded_file = st.sidebar.file_uploader(
        "📁 Cargar archivo Excel con datos de profesores y cursos",
        type=['xlsx', 'xls'],
        help="El archivo debe contener columnas como: Profesor, Curso/Materia, Créditos, Estudiantes, Programa, Sección",
        key="file_uploader_simplificado"
    )
    
    # Inicializar configuración al cargar archivo
    if uploaded_file is not None:
        # Guardar temporalmente el archivo para que ConfiguracionSistema pueda leerlo
        file_path = Path("temp_excel.xlsx")
        file_path.write_bytes(uploaded_file.getbuffer())
        
        # Inicializar las variables globales config, bloques y horas_inicio
        # Las horas_inicio y bloques se generan una sola vez
        global config, bloques, horas_inicio
        config = ConfiguracionSistema(
            "temp_excel.xlsx", 
            st.session_state.programa_seleccionado, 
            st.session_state.colegio_seleccionado,
            info_usuario['usuario']
        )
        bloques = generar_bloques()
        horas_inicio = generar_horas_inicio()

        # Mostrar estado de reservas si aplica
        if config.usa_reservas:
            mostrar_estado_reservas(config)
            
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                # Botón para liberar reservas (CLAVE ÚNICA)
                liberar_key = f"btn_liberar_reservas_{info_usuario['usuario']}_{int(time.time()*1000)}"
                if st.button("🗑️ Liberar Reservas", type="secondary", key=liberar_key):
                    if config.sistema_reservas.liberar_reservas_departamento(info_usuario['usuario']):
                        st.success("✅ Reservas liberadas correctamente")
                        st.rerun()
                    else:
                        st.error("❌ Error al liberar reservas")
            with col2:
                st.info("💡 Libera las reservas si necesitas regenerar el horario")

        # Infraestructura (Salones)
        st.sidebar.subheader("🏫 Infraestructura")
        salones_info = (
            "**Salones disponibles:**\n"
            f"- Prefijo de salón: **{config.prefijo_salon}**\n"
            f"- Total de salones: **{len(config.salones)}**\n"
            f"- Estudiantes máx. por salón: **{config.restricciones_globales['estudiantes_max_salon']}**\n"
            "\n**Restricciones de Horario:**\n"
            f"- Inicio: **{config.restricciones_globales['hora_inicio_min']}**\n"
            f"- Fin: **{config.restricciones_globales['hora_fin_max']}**"
        )
        st.sidebar.markdown(salones_info)
        
        # Mostrar restricciones específicas del colegio (Ejemplo)
        if info_usuario['colegio_completo'] == "COLEGIO DE ADMINISTRACIÓN DE EMPRESAS":
            st.warning("⚠️ Horarios prohibidos globales: Martes y Jueves 10:30-12:30")
        elif info_usuario['colegio_completo'] == "COLEGIO DE ARTES Y CIENCIAS":
            st.warning("⚠️ Horarios prohibidos globales: Martes y Jueves 10:30-12:30")
        elif info_usuario['colegio_completo'] == "DEPARTAMENTO DE MATEMÁTICAS":
            st.success("✅ Sin horarios prohibidos globales específicos.")
        else:
            st.warning("⚠️ Revise si existen horarios prohibidos globales para su colegio.")

        st.markdown("---")

        # CONFIGURACIÓN DE PROFESORES
        if config.profesores_config:
            st.sidebar.markdown("---")
            st.sidebar.subheader("👤 Restricciones por Profesor")
            mostrar_configuracion_profesor(config)
        else:
            st.warning("⚠️ Cargue el archivo Excel para configurar profesores.")
            return

        # Botones de control del horario
        st.markdown("---")
        col_gen, col_info = st.columns(2)
        with col_gen:
            # Botón Generar Horario (CLAVE ÚNICA)
            generar_key = f"btn_generar_horario_{info_usuario['usuario']}_{int(time.time()*1000)}"
            if st.button("🚀 Generar Horario Optimizado", type="primary", key=generar_key):
                with st.spinner("Generando horario optimizado... (Puede tardar varios segundos)"):
                    mejor_asignaciones, score = buscar_mejor_horario(500, config, bloques, horas_inicio)
                    
                    if mejor_asignaciones is not None:
                        # Convertir a DataFrame y guardar en session state
                        df_resultado = pd.DataFrame([fila for asig in mejor_asignaciones for fila in asig.to_dict()])
                        st.session_state.df_horario_generado = df_resultado
                        st.session_state.score_horario = score
                        st.rerun() # Recargar para limpiar el spinner
                    elif config.usa_reservas:
                        st.info("💡 **Sugerencia**: Algunos salones pueden estar ocupados por otros departamentos. Intente liberar las reservas o reajustar los horarios de no disponibilidad.")
                    else:
                        st.error("❌ No se pudo generar un horario válido. Ajuste las restricciones de profesor o verifique si hay suficientes salones.")
        
        with col_info:
            st.markdown("""
            ### ℹ️ Instrucciones de Carga
            - El archivo debe ser **Excel (.xlsx/.xls)**
            - Columnas reconocidas: `Profesor`, `Curso/Materia`, `Créditos`, `Estudiantes`, `Programa`, `Sección`
            - Si faltan columnas de créditos, estudiantes, programa o sección, se usarán valores por defecto.
            - El sistema detecta automáticamente las columnas relevantes.
            - Incluir la columna **Programa** es importante para filtros por carrera.
            """)
        
        st.markdown("---")

        # VISUALIZACIÓN DEL RESULTADO
        if 'df_horario_generado' in st.session_state:
            st.markdown(f"## ✅ Resultado de la Optimización (Score: {st.session_state.score_horario:.2f})")
            mostrar_tabs_horario_mejoradas(st.session_state.df_horario_generado)

    else:
        st.info("Por favor, cargue un archivo Excel para comenzar la generación de horarios.")

if __name__ == "__main__":
    main()
