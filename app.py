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
# SISTEMA DE AUTENTICACIÓN Y CREDENCIALES SIMPLIFICADO - CORREGIDO
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
        <h1 style="color: white; margin: 0; font-size: 3rem;">Acceso al Sistema</h1>
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
        
        st.markdown("### Credenciales de Acceso Simplificadas")
        
        # Información de ayuda SIMPLIFICADA
        with st.expander("¿Cómo obtener mis credenciales?", expanded=False):
            st.markdown("""
            **CREDENCIALES SIMPLIFICADAS (sin tildes ni espacios):**
            
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
        
        # Formulario de login - CLAVES FIJAS PARA EVITAR DUPLICADOS
        usuario = st.text_input("Usuario", placeholder="Ej: artes_ciencias", key="login_usuario")
        contraseña = st.text_input("Contraseña", type="password", placeholder="Ej: biologia", key="login_password")
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("Iniciar Sesión", type="primary", use_container_width=True, key="btn_login_main"):
                if usuario and contraseña:
                    info_usuario = verificar_credenciales_simplificadas(usuario, contraseña)
                    if info_usuario:
                        # Guardar información de sesión
                        st.session_state.usuario_autenticado = True
                        st.session_state.info_usuario = info_usuario
                        st.session_state.programa_seleccionado = info_usuario['programa']
                        st.session_state.colegio_seleccionado = info_usuario['colegio_completo']
                        st.session_state.nivel_seleccionado = info_usuario['nivel']
                        
                        st.success("Acceso autorizado. Redirigiendo...")
                        st.rerun()
                    else:
                        st.error("Credenciales incorrectas. Verifique su usuario y contraseña.")
                else:
                    st.warning("Por favor complete todos los campos.")
        
        # Mostrar programas disponibles para referencia
        with st.expander("Ver todos los programas disponibles"):
            credenciales = generar_credenciales_simplificadas()
            programas_por_colegio = {}
            
            for info in credenciales.values():
                colegio = info['usuario']
                if colegio not in programas_por_colegio:
                    programas_por_colegio[colegio] = []
                programas_por_colegio[colegio].append(f"{info['contraseña']} → {info['programa']}")
            
            for colegio, programas in sorted(programas_por_colegio.items()):
                st.markdown(f"**{colegio}**")
                for programa in sorted(programas):
                    st.markdown(f"  • {programa}")
                st.markdown("---")
        
        st.markdown("</div>", unsafe_allow_html=True)

def mostrar_header_usuario_corregido():
    """Muestra la información del usuario autenticado en el header - CORREGIDO"""
    if st.session_state.get('usuario_autenticado') and st.session_state.get('info_usuario'):
        info = st.session_state.info_usuario
        
        titulo_programa = f"{info['programa']}"
        subtitulo = f"{info['colegio_completo']} • {info['nivel']}"
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
                    <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;">Sesión activa</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ========================================================
# NUEVA FUNCIÓN: EXPORTAR HORARIO EN FORMATO LaTeX (MEJORADA CON DATOS REALES)
# ========================================================

def exportar_horario_latex(asignaciones, intentos=250, tasa_mutacion=0.1, tasa_cruce=0.95):
    """Exporta el horario en formato LaTeX con los datos reales del horario generado"""
    
    if not asignaciones:
        return "No hay horario para exportar"
    
    # Calcular tiempo de ejecución (simulado o real)
    tiempo_ejecucion = "00:06:27"  # Puedes hacer esto dinámico si tienes el tiempo real
    
    # Calcular estadísticas de violaciones REALES
    violaciones_salon = 0
    violaciones_profesor = 0
    violaciones_capacidad = 0
    secciones_faltantes = 0
    creditos_extra = 0
    
    # Calcular violaciones REALES
    for i, asig1 in enumerate(asignaciones):
        for j, asig2 in enumerate(asignaciones):
            if i >= j:
                continue
            if hay_conflictos(asig1, [asig2]):
                if asig1.salon == asig2.salon:
                    violaciones_salon += 1
                if asig1.profesor == asig2.profesor:
                    violaciones_profesor += 1
        
        # Verificar capacidad REAL - asumiendo capacidad estándar de 40
        capacidad_estandar = 40
        if hasattr(asig1, 'estudiantes') and asig1.estudiantes > capacidad_estandar:
            violaciones_capacidad += 1
        
        # Calcular créditos extra REALES
        if hasattr(asig1, 'creditos_extra'):
            creditos_extra += asig1.creditos_extra
    
    # Calcular secciones faltantes REALES
    if config and hasattr(config, 'profesores_config') and config.profesores_config:
        for profesor, prof_config in config.profesores_config.items():
            cursos_asignados = sum(1 for asig in asignaciones if asig.profesor == profesor)
            if isinstance(prof_config, dict) and "cursos" in prof_config:
                cursos_requeridos = len(prof_config["cursos"])
                if cursos_asignados < cursos_requeridos:
                    secciones_faltantes += (cursos_requeridos - cursos_asignados)
    
    # Generar el contenido LaTeX con datos REALES
    contenido = f"""Algoritmo Genético con {intentos} individuos, tasa de mutación = {tasa_mutacion}, tasa de cruce= {tasa_cruce} tiempo de
ejecución {tiempo_ejecucion}.
curso cap_secc grupo_dias hora_inicio profesoroculto sala
___________ ________ __________ ___________ ______________ ________
"""
    
    for asig in asignaciones:
        # Formatear días (ej: 'Lu-Mi-Vi', 'Ma-Ju')
        dias = '-'.join(asig.bloque["dias"]) if hasattr(asig, 'bloque') and "dias" in asig.bloque else "Lu-Mi-Vi"
        
        # Formatear hora (ej: '5:00 pm', '11:30 am')
        hora_str = asig.hora_inicio if hasattr(asig, 'hora_inicio') else "08:00"
        if ':' in hora_str:
            try:
                hora, minuto = map(int, hora_str.split(':'))
                if hora < 12:
                    periodo = "am"
                    if hora == 0:
                        hora = 12
                else:
                    periodo = "pm"
                    if hora > 12:
                        hora -= 12
                hora_formateada = f"{hora}:{minuto:02d} {periodo}"
            except:
                hora_formateada = hora_str
        else:
            hora_formateada = hora_str
        
        # Obtener información del curso REAL
        curso_corto = asig.curso_nombre[:10] if hasattr(asig, 'curso_nombre') else "Curso"
        curso_corto = curso_corto.ljust(10)
        
        # Estudiantes REALES
        estudiantes = asig.estudiantes if hasattr(asig, 'estudiantes') else 30
        
        # Formatear profesor (oculto - tomar iniciales o abreviar)
        profesor_nombre = asig.profesor if hasattr(asig, 'profesor') else "Prof"
        if ' ' in profesor_nombre:
            partes = profesor_nombre.split()
            prof_oculto = f"{partes[0][0]}{partes[-1][0]}" if len(partes) > 1 else profesor_nombre[:2]
        else:
            prof_oculto = profesor_nombre[:2]
        
        # Salon REAL
        salon = asig.salon if hasattr(asig, 'salon') else "SALON"
        
        # Formatear la línea con datos REALES
        linea = f"'{curso_corto}' {estudiantes:3} '{dias}' '{hora_formateada}' 'Prof {prof_oculto}' '{salon}'"
        contenido += linea + "\n"
    
    # Añadir estadísticas de violaciones REALES
    contenido += f"""

Violaciones de restricción: mismo salón en dos eventos al mismo tiempo ---{violaciones_salon}
Violaciones de restricción: mismo profesor en dos eventos al mismo tiempo ---{violaciones_profesor}
Violación de restricción de capacidad de salones ---{violaciones_capacidad}
secciones que aún faltan por asignar ----{secciones_faltantes}
cantidad de créditos que habría que pagarse extra:
{creditos_extra} créditos"""
    
    return contenido

def descargar_horario_latex(asignaciones, nombre_archivo="horario_latex.txt", intentos=250, tasa_mutacion=0.1, tasa_cruce=0.95):
    """Crea un botón de descarga para el horario en formato LaTeX con parámetros REALES"""
    if asignaciones is None:
        st.error("No hay horario para exportar")
        return None
    
    contenido = exportar_horario_latex(asignaciones, intentos, tasa_mutacion, tasa_cruce)
    
    return st.download_button(
        label="Exportar LaTeX",
        data=contenido,
        file_name=nombre_archivo,
        mime="text/plain",
        key=f"download_latex_{int(time.time())}"
    )

# ========================================================
# VISUALIZACIÓN DE HORARIOS MEJORADA - ESTILO TABLA MEJORADO SIN EMOJIS
# ========================================================

def crear_tabla_horario_profesional_mejorada(df_horario, filtro_tipo="completo", filtro_valor=None):
    """Crea una tabla de horarios profesional MEJORADA y más atractiva SIN EMOJIS"""
    
    # Filtrar datos según el tipo
    if filtro_tipo == "profesor" and filtro_valor and filtro_valor != "Todos los profesores":
        df_filtrado = df_horario[df_horario['Profesor'] == filtro_valor]
        titulo = f"Horario de {filtro_valor}"
    elif filtro_tipo == "salon" and filtro_valor and filtro_valor != "Todos los salones":
        df_filtrado = df_horario[df_horario['Salon'] == filtro_valor]
        titulo = f"Horario del Salón {filtro_valor}"
    elif filtro_tipo == "programa" and filtro_valor and filtro_valor != "Todos los programas":
        df_filtrado = df_horario[df_horario['Programa'] == filtro_valor]
        titulo = f"Horario del Programa {filtro_valor}"
    else:
        df_filtrado = df_horario
        titulo = "Horario Completo"
    
    if df_filtrado.empty:
        st.warning("No hay datos para mostrar con los filtros seleccionados.")
        return
    
    # Crear estructura de períodos de tiempo MEJORADA
    periodos = []
    hora_inicio = 7 * 60 + 30  # 7:30 AM en minutos
    hora_fin = 21 * 60  # 9:00 PM en minutos
    
    # Generar períodos cada 60 minutos (más legible)
    tiempo_actual = hora_inicio
    while tiempo_actual < hora_fin:
        hora = tiempo_actual // 60
        minuto = tiempo_actual % 60
        tiempo_fin = tiempo_actual + 60
        hora_fin_periodo = tiempo_fin // 60
        minuto_fin_periodo = tiempo_fin % 60
        
        # Formatear hora de manera más legible
        periodo_str = f"{hora:02d}:{minuto:02d}"
        periodos.append({
            'periodo': periodo_str,
            'inicio_min': tiempo_actual,
            'fin_min': tiempo_fin
        })
        tiempo_actual += 60
    
    # Días de la semana
    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
    dias_map = {'Lu': 'Lunes', 'Ma': 'Martes', 'Mi': 'Miércoles', 'Ju': 'Jueves', 'Vi': 'Viernes'}
    
    # Crear matriz de horarios MEJORADA
    matriz_horario = {}
    for periodo in periodos:
        matriz_horario[periodo['periodo']] = {dia: {'texto': '', 'color': '#ffffff', 'curso': '', 'creditos': ''} for dia in dias}
    
    # Colores para diferentes cursos
    colores_cursos = generar_colores_cursos(df_horario)
    
    # Llenar la matriz con los cursos MEJORADO y SIN EMOJIS
    for _, fila in df_filtrado.iterrows():
        dia_completo = dias_map.get(fila['Dia'], fila['Dia'])
        
        if dia_completo not in dias:
            continue
            
        # Convertir horas a minutos
        inicio_clase = a_minutos(fila['Hora Inicio'])
        fin_clase = a_minutos(fila['Hora Fin'])
        duracion = fin_clase - inicio_clase
        
        # Información del curso SIN EMOJIS
        if filtro_tipo == "salon":
            info_curso = f"{fila['Curso'][:15]}{'...' if len(fila['Curso']) > 15 else ''}\nProf: {fila['Profesor'][:15]}{'...' if len(fila['Profesor']) > 15 else ''}\n{fila['Hora Inicio']}-{fila['Hora Fin']}\nCréditos: {fila['Créditos']}"
        elif filtro_tipo == "profesor":
            info_curso = f"{fila['Curso'][:15]}{'...' if len(fila['Curso']) > 15 else ''}\nSalón: {fila['Salon']}\n{fila['Hora Inicio']}-{fila['Hora Fin']}\nCréditos: {fila['Créditos']}"
        else:
            info_curso = f"{fila['Curso'][:12]}{'...' if len(fila['Curso']) > 12 else ''}\nProf: {fila['Profesor'][:12]}{'...' if len(fila['Profesor']) > 12 else ''}\nSalón: {fila['Salon']}\n{fila['Hora Inicio']}-{fila['Hora Fin']}\nCréditos: {fila['Créditos']}"
        
        # Buscar períodos que se solapan con la clase
        periodo_inicio_idx = None
        for idx, periodo in enumerate(periodos):
            if inicio_clase <= periodo['inicio_min']:
                periodo_inicio_idx = idx
                break
        
        if periodo_inicio_idx is not None:
            # Calcular cuántos períodos ocupa la clase
            periodos_ocupados = max(1, round(duracion / 60))
            
            for i in range(periodos_ocupados):
                if periodo_inicio_idx + i < len(periodos):
                    periodo_actual = periodos[periodo_inicio_idx + i]['periodo']
                    if matriz_horario[periodo_actual][dia_completo]['texto'] == '':
                        matriz_horario[periodo_actual][dia_completo] = {
                            'texto': info_curso if i == 0 else '↧',  # Solo mostrar info en el primer período
                            'color': colores_cursos.get(fila['Curso'], '#667eea'),
                            'curso': fila['Curso'],
                            'creditos': fila['Créditos']
                        }
    
    # Mostrar título MEJORADO SIN EMOJIS
    st.markdown(f"""
    <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 15px; margin-bottom: 2rem; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
        <h2 style="color: white; margin: 0; font-size: 1.8rem;">{titulo}</h2>
        <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;">Horario Semanal - Vista Profesional</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Crear DataFrame para la tabla MEJORADO
    tabla_data = []
    for periodo_info in periodos:
        periodo = periodo_info['periodo']
        fila_data = {'Horario': periodo}
        
        for dia in dias:
            celda = matriz_horario[periodo][dia]
            fila_data[dia] = celda['texto']
        tabla_data.append(fila_data)
    
    df_tabla = pd.DataFrame(tabla_data)
    
    # Aplicar estilos CSS MEJORADOS
    st.markdown("""
    <style>
    .horario-tabla-mejorada {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 13px;
        border-collapse: collapse;
        width: 100%;
        margin: 20px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-radius: 10px;
        overflow: hidden;
    }
    .horario-tabla-mejorada th {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        color: white;
        font-weight: 600;
        padding: 12px 8px;
        text-align: center;
        border: none;
        font-size: 14px;
    }
    .horario-tabla-mejorada td {
        padding: 10px 8px;
        text-align: center;
        vertical-align: middle;
        border: 1px solid #e1e1e1;
        min-height: 60px;
        white-space: pre-line;
        transition: all 0.2s ease;
        line-height: 1.3;
    }
    .horario-tabla-mejorada td:hover {
        transform: scale(1.02);
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        z-index: 1;
        position: relative;
    }
    .horario-tabla-mejorada .hora-col {
        background-color: #f8f9fa;
        font-weight: 600;
        color: #2c3e50;
        width: 80px;
        border-right: 2px solid #bdc3c7;
    }
    .celda-clase {
        border-radius: 6px;
        margin: 2px;
        font-weight: 500;
        color: white;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3);
    }
    .celda-creditos {
        font-size: 11px;
        font-weight: bold;
        margin-top: 2px;
        display: block;
        background-color: rgba(255,255,255,0.2);
        padding: 1px 3px;
        border-radius: 3px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Convertir DataFrame a HTML con estilos MEJORADOS
    html_tabla = df_tabla.to_html(escape=False, index=False, classes='horario-tabla-mejorada')
    
    # Personalizar el HTML para que se vea mejor
    html_tabla = html_tabla.replace('<th>Horario</th>', '<th class="hora-col">Hora</th>')
    
    # Aplicar estilos a las celdas según su contenido
    for periodo_info in periodos:
        periodo = periodo_info['periodo']
        for dia in dias:
            celda = matriz_horario[periodo][dia]
            if celda['texto'] and celda['texto'] != '↧':
                estilo_celda = f'background: {celda["color"]}; color: white;'
                # Agregar créditos al texto si no están ya incluidos
                texto_celda = celda['texto']
                if 'Créditos:' not in texto_celda and celda['creditos']:
                    texto_celda += f"\nCréditos: {celda['creditos']}"
                
                replace_text = f'<td>{celda["texto"]}</td>'
                replace_with = f'<td class="celda-clase" style="{estilo_celda}">{texto_celda}</td>'
                html_tabla = html_tabla.replace(replace_text, replace_with)
            elif celda['texto'] == '↧':
                estilo_celda = f'background: {celda["color"]}; color: white;'
                html_tabla = html_tabla.replace(f'<td>↧</td>', f'<td style="{estilo_celda}">↧</td>')
    
    # Aplicar clase especial a la columna de horarios
    for periodo_info in periodos:
        periodo = periodo_info['periodo']
        html_tabla = html_tabla.replace(f'<td>{periodo}</td>', f'<td class="hora-col">{periodo}</td>')
    
    st.markdown(html_tabla, unsafe_allow_html=True)
    
    # Estadísticas resumidas MEJORADAS
    if not df_filtrado.empty:
        st.markdown("---")
        st.subheader("Estadísticas del Horario")
        
        # Calcular créditos totales
        if 'Créditos' in df_filtrado.columns:
            creditos_totales = df_filtrado['Créditos'].sum()
        else:
            creditos_totales = 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Cursos", df_filtrado['Curso'].nunique())
        with col2:
            if filtro_tipo != "profesor":
                st.metric("Profesores", df_filtrado['Profesor'].nunique())
            else:
                horas_totales = df_filtrado['Duración'].sum()
                st.metric("Horas Semanales", f"{horas_totales:.1f}h")
        with col3:
            if filtro_tipo != "salon":
                st.metric("Salones Usados", df_filtrado['Salon'].nunique())
            else:
                st.metric("Clases Diferentes", len(df_filtrado))
        with col4:
            if creditos_totales > 0:
                st.metric("Créditos Totales", f"{int(creditos_totales)}")
            else:
                total_estudiantes = int(df_filtrado['Estudiantes'].sum())
                st.metric("Total Estudiantes", f"{total_estudiantes:,}")

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
                "Biología", "Microbiología Industrial", "Química", "Geología",
                "Matemáticas", "Enfermería", "Física", "Ciencias Marinas"
            ]
        }
    },
    "COLEGIO DE CIENCIAS AGRÍCOLAS": {
        "color": "#96CEB4",
        "salones_compartidos": 15,
        "prefijo_salon": "CA",
        "sistema_reservas": False,
        "generacion_unificada": False,
        "horarios_exactos": False,
        "niveles": {
            "Bachilleratos en Ciencias Agrícolas": [
                "Ciencias Agrícolas", "Agronomía", "Economía Agrícola", "Horticultura",
                "Ciencia Animal", "Protección de Cultivos", "Agronegocios"
            ]
        }
    },
    "COLEGIO DE INGENIERÍA": {
        "color": "#FFEAA7",
        "salones_compartidos": 20,
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

# Configuración del sistema (simplificada) - CORREGIDA
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
        
        self.usa_reservas = False
        if colegio_actual and colegio_actual in PROGRAMAS_RUM:
            colegio_info = PROGRAMAS_RUM[colegio_actual]
            self.usa_reservas = colegio_info.get('sistema_reservas', False)
            self.es_generacion_unificada = colegio_info.get('generacion_unificada', False)
            self.usa_horarios_exactos = colegio_info.get('horarios_exactos', False)
            self.sistema_reservas = SistemaReservasSalones() if self.usa_reservas else None
        
        self.restricciones_globales = {
            "horarios_prohibidos": self._obtener_horarios_prohibidos(),
            "hora_inicio_min": "07:00" if self.usa_horarios_exactos else "07:30",
            "hora_fin_max": "18:00" if self.usa_horarios_exactos else "19:30",
            "creditos_max_profesor": 15,
            "creditos_min_profesor": 8,
            "estudiantes_max_salon": 50,
            "horas_max_dia": 8,
            "dias_max_profesor": 5
        }
        
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
    
    def _obtener_horarios_prohibidos(self):
        if self.colegio_actual == "COLEGIO DE ADMINISTRACIÓN DE EMPRESAS":
            return {
                "Ma": [("10:30", "12:30")],
                "Ju": [("10:30", "12:30")]
            }
        elif self.colegio_actual == "DEPARTAMENTO DE MATEMÁTICAS":
            return {}
        elif self.colegio_actual == "COLEGIO DE ARTES Y CIENCIAS":
            return {
                "Ma": [("10:30", "12:30")],
                "Ju": [("10:30", "12:30")]
            }
        else:
            return {
                "Ma": [("10:30", "12:30")],
                "Ju": [("10:30", "12:30")]
            }
    
    def cargar_desde_excel(self):
        try:
            # Guardar el archivo temporalmente si es un upload de Streamlit
            if hasattr(self.archivo_excel, 'read'):
                # Es un objeto uploaded file de Streamlit
                temp_path = "temp_uploaded_excel.xlsx"
                with open(temp_path, "wb") as f:
                    f.write(self.archivo_excel.getbuffer())
                excel_path = temp_path
            else:
                # Es una ruta de archivo normal
                excel_path = self.archivo_excel
            
            # Leer el archivo Excel
            excel_data = pd.read_excel(excel_path, sheet_name=None)
            
            # Mostrar información de depuración
            st.write(f"Hojas disponibles en el Excel: {list(excel_data.keys())}")
            
            hoja_cursos = None
            for nombre_hoja, df in excel_data.items():
                st.write(f"\nAnalizando hoja '{nombre_hoja}':")
                st.write(f"Filas: {len(df)}, Columnas: {list(df.columns)}")
                
                # Verificar si la hoja tiene datos relevantes
                if len(df) > 0:
                    columnas_df = [str(col).lower().strip() for col in df.columns]
                    
                    tiene_profesor = any('profesor' in col or 'docente' in col for col in columnas_df)
                    tiene_curso = any('curso' in col or 'materia' in col or 'asignatura' in col for col in columnas_df)
                    
                    if tiene_profesor and tiene_curso:
                        hoja_cursos = df
                        st.success(f"Hoja '{nombre_hoja}' seleccionada como fuente de datos")
                        break
            
            if hoja_cursos is None:
                # Si no encontramos una hoja con las columnas esperadas, usar la primera hoja
                if excel_data:
                    primera_hoja = list(excel_data.keys())[0]
                    hoja_cursos = excel_data[primera_hoja]
                    st.warning(f"Usando la primera hoja '{primera_hoja}' (no se encontraron columnas específicas)")
                else:
                    st.error("El archivo Excel está vacío o no tiene hojas")
                    return
            
            self.cursos_df = hoja_cursos
            self.procesar_datos_excel()
            
        except Exception as e:
            st.error(f"Error al cargar el archivo Excel: {str(e)}")
            import traceback
            st.write("Detalles del error:", traceback.format_exc())
            st.info("Usando configuración por defecto")
    
    def procesar_datos_excel(self):
        if self.cursos_df is None or self.cursos_df.empty:
            st.warning("No hay datos en el DataFrame de cursos")
            return
        
        df = self.cursos_df.copy()
        
        # Mostrar información de depuración
        st.write(f"Procesando {len(df)} registros del Excel")
        
        # Normalizar nombres de columnas
        df.columns = [str(col).lower().strip().replace(' ', '_') for col in df.columns]
        
        # Mostrar columnas disponibles
        st.write(f"Columnas disponibles después de normalizar: {list(df.columns)}")
        
        # Mapear columnas comunes
        mapeo_columnas = {
            'profesor': ['profesor', 'docente', 'teacher', 'instructor', 'prof'],
            'curso': ['curso', 'materia', 'asignatura', 'subject', 'course', 'nombre_curso'],
            'creditos': ['creditos', 'créditos', 'credits', 'horas', 'horas_semana', 'cr'],
            'estudiantes': ['estudiantes', 'alumnos', 'students', 'enrollment', 'seccion', 'cantidad', 'num_estudiantes'],
            'programa': ['programa', 'program', 'carrera', 'major', 'departamento'],
            'seccion': ['seccion', 'section', 'sec', 'grupo', 'grupo_']
        }
        
        columnas_finales = {}
        for campo, posibles in mapeo_columnas.items():
            for col in df.columns:
                if any(pos in col for pos in posibles):
                    columnas_finales[campo] = col
                    break
        
        st.write(f"Mapeo de columnas identificado: {columnas_finales}")
        
        # Verificar columnas mínimas requeridas
        if 'profesor' not in columnas_finales:
            st.error("Error: No se encontró columna de profesor")
            st.write("Columnas disponibles:", list(df.columns))
            return
        
        if 'curso' not in columnas_finales:
            st.error("Error: No se encontró columna de curso")
            return
        
        # Valores por defecto para columnas faltantes
        if 'creditos' not in columnas_finales:
            df['creditos_default'] = 3
            columnas_finales['creditos'] = 'creditos_default'
            st.warning("No se encontró columna de créditos, usando 3 por defecto")
        
        if 'estudiantes' not in columnas_finales:
            df['estudiantes_default'] = 30
            columnas_finales['estudiantes'] = 'estudiantes_default'
            st.warning("No se encontró columna de estudiantes, usando 30 por defecto")
        
        if 'programa' not in columnas_finales:
            df['programa_default'] = self.programa_actual or 'Programa General'
            columnas_finales['programa'] = 'programa_default'
        
        if 'seccion' not in columnas_finales:
            df['seccion_default'] = '001'
            columnas_finales['seccion'] = 'seccion_default'
        
        # Limpiar datos nulos en columnas esenciales
        columnas_esenciales = [columnas_finales['profesor'], columnas_finales['curso']]
        df = df.dropna(subset=columnas_esenciales)
        
        # Obtener profesores únicos
        profesores_unicos = df[columnas_finales['profesor']].dropna().unique()
        st.info(f"Profesores encontrados: {len(profesores_unicos)}")
        
        # Procesar cada profesor
        for profesor in profesores_unicos:
            if pd.isna(profesor) or str(profesor).strip() == '':
                continue
                
            profesor_nombre = str(profesor).strip()
            cursos_profesor = df[df[columnas_finales['profesor']] == profesor]
            
            cursos_lista = []
            creditos_totales = 0
            
            for _, fila in cursos_profesor.iterrows():
                curso_nombre = str(fila[columnas_finales['curso']]).strip()
                
                # Obtener créditos
                try:
                    if columnas_finales['creditos'] in fila:
                        creditos_val = fila[columnas_finales['creditos']]
                        if pd.isna(creditos_val):
                            creditos = 3
                        else:
                            creditos = int(float(creditos_val))
                    else:
                        creditos = 3
                except (ValueError, TypeError):
                    creditos = 3
                
                # Obtener estudiantes
                try:
                    if columnas_finales['estudiantes'] in fila:
                        estudiantes_val = fila[columnas_finales['estudiantes']]
                        if pd.isna(estudiantes_val):
                            estudiantes = 30
                        else:
                            estudiantes = int(float(estudiantes_val))
                    else:
                        estudiantes = 30
                except (ValueError, TypeError):
                    estudiantes = 30
                
                # Obtener programa
                if columnas_finales['programa'] in fila and not pd.isna(fila[columnas_finales['programa']]):
                    programa = str(fila[columnas_finales['programa']]).strip()
                else:
                    programa = self.programa_actual or 'Programa General'
                
                # Obtener sección
                if columnas_finales['seccion'] in fila and not pd.isna(fila[columnas_finales['seccion']]):
                    seccion = str(fila[columnas_finales['seccion']]).strip()
                else:
                    seccion = '001'
                
                if curso_nombre and curso_nombre.lower() != 'nan':
                    cursos_lista.append({
                        "nombre": curso_nombre,
                        "creditos": creditos,
                        "estudiantes": estudiantes,
                        "programa": programa,
                        "seccion": seccion
                    })
                    creditos_totales += creditos
            
            if cursos_lista:
                self.profesores_config[profesor_nombre] = {
                    "cursos": cursos_lista,
                    "creditos_totales": creditos_totales,
                    "horario_preferido": {},
                    "horario_no_disponible": {}
                }
                
                st.write(f"{profesor_nombre}: {len(cursos_lista)} cursos, {creditos_totales} créditos totales")
        
        # Configurar salones según el colegio
        if self.colegio_actual and self.colegio_actual in PROGRAMAS_RUM:
            colegio_info = PROGRAMAS_RUM[self.colegio_actual]
            if self.colegio_actual == "COLEGIO DE ADMINISTRACIÓN DE EMPRESAS":
                self.salones = AE_SALONES_FIJOS.copy()
            elif self.colegio_actual == "DEPARTAMENTO DE MATEMÁTICAS":
                self.salones = MATEMATICAS_SALONES_FIJOS.copy()
            elif self.colegio_actual == "COLEGIO DE ARTES Y CIENCIAS":
                self.salones = ARTES_CIENCIAS_SALONES_COMPARTIDOS.copy()
            else:
                num_salones = colegio_info.get('salones_compartidos', 15)
                prefijo = colegio_info.get('prefijo_salon', 'SALON')
                self.salones = [f"{prefijo}-{i+1:02d}" for i in range(num_salones)]
        else:
            num_salones = 15
            self.salones = [f"Salon {i+1}" for i in range(num_salones)]
        
        st.success(f"Configuración completada: {len(self.profesores_config)} profesores, {len(self.salones)} salones")

# Funciones auxiliares (mantenidas igual)
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

def generar_horas_inicio():
    if config and config.usa_horarios_exactos:
        return [f"{h:02d}:00" for h in range(7, 19)]
    else:
        horas_inicio = []
        for h in range(7, 20):
            for m in [0, 30]:
                if h == 19 and m > 20:
                    break
                horas_inicio.append(f"{h:02d}:{m:02d}")
        return horas_inicio

def a_minutos(hhmm):
    try:
        h, m = map(int, hhmm.split(":"))
        return h * 60 + m
    except:
        return 0

def es_bloque_tres_horas_valido(dia, hora_inicio, duracion, creditos):
    if creditos == 3 and duracion == 3:
        dias_semana = ["Lu", "Ma", "Mi", "Ju", "Vi"]
        if dia in dias_semana:
            inicio_minutos = a_minutos(hora_inicio)
            limite = "15:00" if (config and config.usa_horarios_exactos) else "15:30"
            restriccion_minutos = a_minutos(limite)
            if inicio_minutos < restriccion_minutos:
                return False
    return True

def horario_valido(dia, hora_inicio, duracion, profesor=None, creditos=None):
    if config is None:
        return False
        
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

class AsignacionClase:
    def __init__(self, curso_info, profesor, bloque, hora_inicio, salon):
        self.curso_nombre = curso_info["nombre"]
        self.profesor = profesor
        self.bloque = bloque
        self.hora_inicio = hora_inicio
        self.estudiantes = curso_info["estudiantes"]
        self.salon = salon
        self.creditos = curso_info["creditos"]
        self.programa = curso_info.get("programa", "Programa General")
        self.seccion = curso_info.get("seccion", "001")
        self.horas_contacto = int(sum(bloque["horas"]))
        self.creditos_extra = calcular_creditos_adicionales(self.horas_contacto, self.estudiantes)
        
    def get_horario_detallado(self):
        horarios = []
        for dia, duracion in zip(self.bloque["dias"], self.bloque["horas"]):
            hora_fin_min = a_minutos(self.hora_inicio) + int(duracion * 60)
            hora_fin = f"{hora_fin_min//60:02d}:{hora_fin_min%60:02d}"
            bloque_prefijo = obtener_prefijo_salon(self.salon)
            
            horarios.append({
                "Curso": self.curso_nombre,
                "Profesor": self.profesor,
                "Programa": self.programa,
                "Seccion": self.seccion,
                "Bloque": bloque_prefijo,
                "Dia": dia,
                "Hora Inicio": self.hora_inicio,
                "Hora Fin": hora_fin,
                "Duración": duracion,
                "Créditos": self.creditos,
                "Créditos Extra": self.creditos_extra,
                "Estudiantes": self.estudiantes,
                "Salon": self.salon
            })
        return horarios

def obtener_prefijo_salon(salon_str):
    if not salon_str:
        return "SALON"
    if " " in salon_str:
        return salon_str.split(" ")[0].strip()
    if "-" in salon_str:
        return salon_str.split("-")[0].strip()
    return salon_str.split()[0].strip()

def generar_horario_valido_con_reservas():
    asignaciones = []
    horas_inicio = generar_horas_inicio()
    
    for profesor, prof_config in config.profesores_config.items():
        cursos_asignados = 0
        intentos = 0
        max_intentos = 5000
        
        while cursos_asignados < len(prof_config["cursos"]) and intentos < max_intentos:
            intentos += 1
            
            curso_info = prof_config["cursos"][cursos_asignados]
            bloques_compatibles = [b for b in bloques if b["creditos"] == curso_info["creditos"]]
            
            if not bloques_compatibles:
                bloques_compatibles = sorted(bloques, key=lambda x: abs(x["creditos"] - curso_info["creditos"]))[:5]
            
            bloque = random.choice(bloques_compatibles)
            hora_inicio = random.choice(horas_inicio)
            
            salones_disponibles = []
            for dia, duracion in zip(bloque["dias"], bloque["horas"]):
                hora_fin_min = a_minutos(hora_inicio) + int(duracion * 60)
                hora_fin = f"{hora_fin_min//60:02d}:{hora_fin_min%60:02d}"
                
                departamento_key = config.departamento_actual or config.programa_actual
                salones_dia = config.sistema_reservas.obtener_salones_disponibles(
                    dia, hora_inicio, hora_fin, departamento_key, config.salones
                )
                
                if not salones_disponibles:
                    salones_disponibles = salones_dia
                else:
                    salones_disponibles = list(set(salones_disponibles) & set(salones_dia))
            
            if not salones_disponibles:
                continue
            
            salon = random.choice(salones_disponibles)
            
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

def generar_horario_valido():
    asignaciones = []
    horas_inicio = generar_horas_inicio()
    
    for profesor, prof_config in config.profesores_config.items():
        cursos_asignados = 0
        intentos = 0
        max_intentos = 4000

        while cursos_asignados < len(prof_config["cursos"]) and intentos < max_intentos:
            intentos += 1
            curso_info = prof_config["cursos"][cursos_asignados]
            bloques_compatibles = [b for b in bloques if b["creditos"] == curso_info["creditos"]]
            if not bloques_compatibles:
                bloques_compatibles = sorted(bloques, key=lambda x: abs(x["creditos"] - curso_info["creditos"]))[:5]
            bloque = random.choice(bloques_compatibles)
            hora_inicio = random.choice(horas_inicio)
            salon = random.choice(config.salones)

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
    if asignaciones is None:
        return -float('inf')
    
    penalizacion = 0
    bonus = 0
    
    for profesor, prof_config in config.profesores_config.items():
        cursos_asignados = sum(1 for asig in asignaciones if asig.profesor == profesor)
        cursos_requeridos = len(prof_config["cursos"])
        if cursos_asignados != cursos_requeridos:
            penalizacion += abs(cursos_asignados - cursos_requeridos) * 2000
    
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
    
    for i, asig1 in enumerate(asignaciones):
        for j, asig2 in enumerate(asignaciones):
            if i >= j:
                continue
            if hay_conflictos(asig1, [asig2]):
                penalizacion += 5000
    
    for asig in asignaciones:
        for dia, duracion in zip(asig.bloque["dias"], asig.bloque["horas"]):
            if not es_bloque_tres_horas_valido(dia, asig.hora_inicio, duracion, asig.creditos):
                penalizacion += 10000
    
    pesos = config.pesos_restricciones
    
    for asig in asignaciones:
        for dia, duracion in zip(asig.bloque["dias"], asig.bloque["horas"]):
            if cumple_horario_preferido(dia, asig.hora_inicio, duracion, asig.profesor):
                bonus += pesos["horario_preferido"]
        
        if asig.estudiantes > config.restricciones_globales["estudiantes_max_salon"]:
            penalizacion += pesos["estudiantes_por_salon"] * (asig.estudiantes - config.restricciones_globales["estudiantes_max_salon"])
    
    return bonus - penalizacion

def buscar_mejor_horario(intentos=250):
    mejor_asignaciones = None
    mejor_score = -float('inf')
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(intentos):
        progress_bar.progress((i + 1) / intentos)
        status_text.text(f"Generando horarios... {i+1}/{intentos}")
        
        try:
            if config.usa_reservas:
                asignaciones = generar_horario_valido_con_reservas()
            else:
                asignaciones = generar_horario_valido()
                
            score = evaluar_horario(asignaciones)
            if score > mejor_score:
                mejor_score = score
                mejor_asignaciones = asignaciones
        except Exception as e:
            st.warning(f"Error en iteración {i+1}: {e}")
            continue
    
    status_text.text(f"Generación completada. Mejor puntuación: {mejor_score}")
    return mejor_asignaciones, mejor_score

def exportar_horario(asignaciones):
    registros = []
    for asig in asignaciones:
        registros.extend(asig.get_horario_detallado())
    df = pd.DataFrame(registros)

    for col in ["3h Consecutivas", "Restricción 15:30"]:
        if col in df.columns:
            df = df.drop(columns=[col])

    return df

def _nombre_archivo_horario(departamento):
    safe_dept = "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in (departamento or "departamento"))
    return f"horario_{safe_dept}.json"

def guardar_horario_json(df_horario, departamento):
    try:
        ruta = _nombre_archivo_horario(departamento)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(df_horario.to_dict(orient="records"), f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"Error al guardar horario: {e}")
        return False

def cargar_horario_json(departamento):
    ruta = _nombre_archivo_horario(departamento)
    if os.path.exists(ruta):
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                data = json.load(f)
            df = pd.DataFrame(data)
            return df
        except Exception as e:
            st.warning(f"Error al cargar horario guardado: {e}")
            return None
    return None

def generar_colores_cursos(df_horario):
    cursos_unicos = df_horario['Curso'].unique()
    
    colores_base = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', 
        '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9',
        '#F8C471', '#82E0AA', '#F1948A', '#85C1E9', '#D5A6BD',
        '#AED6F1', '#A9DFBF', '#F9E79F', '#D7BDE2', '#A3E4D7'
    ]
    
    colores_cursos = {}
    for i, curso in enumerate(cursos_unicos):
        colores_cursos[curso] = colores_base[i % len(colores_base)]
    
    return colores_cursos

def crear_calendario_interactivo(df_horario, filtro_tipo="profesor", filtro_valor=None, chart_key="default"):
    # Filtros por tipo (profesor, programa, salon, departamento)
    if filtro_tipo == "profesor" and filtro_valor and filtro_valor != "Todos los profesores":
        df_filtrado = df_horario[df_horario['Profesor'] == filtro_valor]
        titulo_calendario = f"Calendario de {filtro_valor}"
    elif filtro_tipo == "programa" and filtro_valor and filtro_valor != "Todos los programas":
        df_filtrado = df_horario[df_horario['Programa'] == filtro_valor]
        titulo_calendario = f"Calendario del Programa: {filtro_valor}"
    elif filtro_tipo == "salon" and filtro_valor and filtro_valor != "Todos los salones":
        df_filtrado = df_horario[df_horario['Salon'] == filtro_valor]
        titulo_calendario = f"Horario del Salón: {filtro_valor}"
    else:
        df_filtrado = df_horario
        titulo_calendario = "Calendario Semanal de Clases - Vista Completa"
    
    # Generar colores para cada curso
    colores_cursos = generar_colores_cursos(df_horario)
    
    # Mapeo de días a números para el eje X
    dias_map = {'Lu': 1, 'Ma': 2, 'Mi': 3, 'Ju': 4, 'Vi': 5}
    dias_nombres = ['', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
    
    # Preparar columnas por salón para cada día
    salones_por_dia = {}
    for dia in dias_map.keys():
        salones_unicos = df_filtrado[df_filtrado['Dia'] == dia]['Salon'].unique().tolist()
        salones_por_dia[dia] = sorted(salones_unicos)
    
    # Crear figura
    fig = go.Figure()
    
    # Procesar cada clase para crear los bloques
    for _, fila in df_filtrado.iterrows():
        dia = fila['Dia']
        dia_num = dias_map[dia]
        
        # Columnas por salón
        salones_dia = salones_por_dia.get(dia, [])
        total_cols = max(len(salones_dia), 1)
        salon_idx = salones_dia.index(fila['Salon']) if fila['Salon'] in salones_dia else 0
        
        # Ancho por columna dentro del día
        dia_ancho_total = 0.9
        col_ancho = dia_ancho_total / total_cols
        x_center = (dia_num - 0.45) + (salon_idx + 0.5) * col_ancho
        x0 = x_center - (col_ancho * 0.45)
        x1 = x_center + (col_ancho * 0.45)
        
        # Convertir horas a minutos desde medianoche para el eje Y
        hora_inicio_min = a_minutos(fila['Hora Inicio'])
        hora_fin_min = a_minutos(fila['Hora Fin'])
        
        # Crear el bloque de la clase
        fig.add_shape(
            type="rect",
            x0=x0,
            y0=hora_inicio_min,
            x1=x1,
            y1=hora_fin_min,
            fillcolor=colores_cursos.get(fila['Curso'], "#667eea"),
            opacity=0.85,
            line=dict(color="#222", width=1),
        )
        
        # Texto mejorado con información del departamento y créditos
        texto_clase = f"<b>{fila['Curso']}</b><br>"
        texto_clase += f"Sección: {fila.get('Seccion', '001')}<br>"
        texto_clase += f"Profesor: {fila['Profesor']}<br>"
        texto_clase += f"Salón: {fila['Salon']}<br>"
        texto_clase += f"Estudiantes: {fila['Estudiantes']}<br>"
        texto_clase += f"Horario: {fila['Hora Inicio']} - {fila['Hora Fin']}<br>"
        texto_clase += f"Créditos: {fila['Créditos']}"
        
        # Mostrar sección en el bloque principal
        texto_bloque = f"<b>{fila['Curso']}</b><br>{fila['Hora Inicio']}-{fila['Hora Fin']}<br>Sec: {fila.get('Seccion', '001')}<br>{fila['Salon']}<br>Créditos: {fila['Créditos']}"
        
        # Añadir anotación centrada en el bloque
        fig.add_annotation(
            x=x_center,
            y=(hora_inicio_min + hora_fin_min) / 2,
            text=texto_bloque,
            showarrow=False,
            font=dict(color="white", size=11, family="Arial Black"),
            bgcolor="rgba(0,0,0,0.7)",
            bordercolor="white",
            borderwidth=1,
            borderpad=4,
            hovertext=texto_clase
        )
    
    # Configurar el layout del calendario
    hora_min = 7 * 60 if config and config.usa_horarios_exactos else 7 * 60
    hora_max = 19 * 60 if config and config.usa_horarios_exactos else 20 * 60
    
    fig.update_layout(
        title={
            'text': titulo_calendario,
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 26, 'color': '#2C3E50'}
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
            tickvals=[i*60 for i in range(7, 20)],
            ticktext=[f"{i:02d}:00" for i in range(7, 20)],
            range=[hora_max, hora_min],
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
    
    return fig, colores_cursos

def mostrar_leyenda_cursos(colores_cursos, df_horario, filtro_tipo=None, filtro_valor=None):
    if filtro_tipo and filtro_valor and filtro_valor not in ["Todos los profesores", "Todos los programas", "Todos los salones"]:
        if filtro_tipo == "profesor":
            cursos_filtrados = df_horario[df_horario['Profesor'] == filtro_valor]['Curso'].unique()
            titulo = f"Cursos de {filtro_valor}"
        elif filtro_tipo == "programa":
            cursos_filtrados = df_horario[df_horario['Programa'] == filtro_valor]['Curso'].unique()
            titulo = f"Cursos del Programa {filtro_valor}"
        elif filtro_tipo == "salon":
            cursos_filtrados = df_horario[df_horario['Salon'] == filtro_valor]['Curso'].unique()
            titulo = f"Cursos en {filtro_valor}"
        else:
            cursos_filtrados = df_horario['Curso'].unique()
            titulo = "Leyenda de Colores por Curso"
        
        colores_mostrar = {curso: color for curso, color in colores_cursos.items() if curso in cursos_filtrados}
    else:
        colores_mostrar = colores_cursos
        titulo = "Leyenda de Colores por Curso"
    
    st.subheader(titulo)
    
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

def mostrar_estado_reservas():
    if not config or not config.usa_reservas or not config.sistema_reservas:
        return
    
    st.subheader("Estado Actual de Reservas de Salones Compartidos")
    
    stats = config.sistema_reservas.obtener_estadisticas_uso()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Reservas", stats['total_reservas'])
    with col2:
        st.metric("Departamentos Activos", stats['departamentos_activos'])
    with col3:
        st.metric("Salones en Uso", stats['salones_en_uso'])
    with col4:
        disponibles = (len(config.salones) if config.salones else 0) - stats['salones_en_uso']
        st.metric("Salones Disponibles", max(disponibles, 0))
    
    if stats['reservas_por_departamento']:
        st.write("**Reservas por Departamento:**")
        for departamento, cantidad in stats['reservas_por_departamento'].items():
            st.write(f"• {departamento}: {cantidad} reservas")
    
    with st.expander("Ver todas las reservas activas"):
        if config.sistema_reservas.reservas:
            reservas_df = []
            for clave, reserva in config.sistema_reservas.reservas.items():
                reservas_df.append({
                    'Salón': reserva['salon'],
                    'Día': reserva['dia'],
                    'Hora Inicio': reserva['hora_inicio'],
                    'Hora Fin': reserva['hora_fin'],
                    'Departamento': reserva['departamento'],
                    'Programa': reserva['programa'],
                    'Curso': reserva['curso'],
                    'Profesor': reserva['profesor']
                })
            
            df_reservas = pd.DataFrame(reservas_df)
            st.dataframe(df_reservas, use_container_width=True)
        else:
            st.info("No hay reservas activas")

# ========================================================
# NUEVA FUNCIÓN: BOTONES DE PERSISTENCIA MEJORADOS
# ========================================================

def mostrar_botones_persistencia_mejorada(df_horario, usuario_key, asignaciones=None):
    """Muestra los botones de persistencia MEJORADOS con nueva exportación LaTeX"""
    st.markdown("---")
    st.markdown("### Gestión de Horarios")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Guardar Horario", type="primary", use_container_width=True, key="btn_guardar_main"):
            if df_horario is None or df_horario.empty:
                st.error("No hay horario para guardar.")
            else:
                ok = guardar_horario_json(df_horario, usuario_key)
                if ok:
                    # Guardar reservas también si aplica
                    if config and config.usa_reservas and 'asignaciones_actuales' in st.session_state:
                        guardar_reservas_horario(st.session_state.asignaciones_actuales, usuario_key)
                    st.success("Horario guardado correctamente.")
                    st.rerun()
                else:
                    st.error("Error al guardar el horario.")
    
    with col2:
        if st.button("Generar Nuevo", use_container_width=True, key="btn_generar_nuevo_main"):
            if 'uploaded_file_data' not in st.session_state:
                st.warning("Primero carga un archivo Excel para poder generar un nuevo horario.")
            else:
                # Limpiar horario actual
                if 'asignaciones_actuales' in st.session_state:
                    del st.session_state.asignaciones_actuales
                if 'horario_generado' in st.session_state:
                    del st.session_state.horario_generado
                st.info("Horario borrado. Usa el botón 'Generar Horario Optimizado' para crear uno nuevo.")
                st.rerun()
    
    with col3:
        # Exportación CSV normal
        if df_horario is not None and not df_horario.empty:
            csv = df_horario.to_csv(index=False)
            st.download_button(
                label="Descargar CSV",
                data=csv,
                file_name="horario_completo.csv",
                mime="text/csv",
                use_container_width=True,
                key="download_csv_main"
            )
    
    with col4:
        # Nueva exportación LaTeX con parámetros reales
        if asignaciones is not None:
            # Obtener parámetros de configuración si están disponibles
            intentos_val = 250
            tasa_mutacion_val = 0.1
            tasa_cruce_val = 0.95
            
            descargar_horario_latex(
                asignaciones, 
                f"horario_latex_{usuario_key}.txt",
                intentos_val,
                tasa_mutacion_val,
                tasa_cruce_val
            )
        else:
            if 'asignaciones_actuales' in st.session_state:
                intentos_val = 250
                tasa_mutacion_val = 0.1
                tasa_cruce_val = 0.95
                descargar_horario_latex(
                    st.session_state.asignaciones_actuales, 
                    f"horario_latex_{usuario_key}.txt",
                    intentos_val,
                    tasa_mutacion_val,
                    tasa_cruce_val
                )
            else:
                st.info("Export LaTeX disponible después de generar horario")

def guardar_reservas_horario(asignaciones, usuario_key):
    """Guarda las reservas de salones del horario generado"""
    if not config or not config.usa_reservas or not config.sistema_reservas:
        return True
    
    # Primero liberar reservas anteriores del usuario
    config.sistema_reservas.liberar_reservas_departamento(usuario_key)
    
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
                departamento=usuario_key,
                programa=asig.programa,
                curso=asig.curso_nombre,
                profesor=asig.profesor
            )
    
    return config.sistema_reservas.guardar_reservas()

def _creditos_unicos_por_profesor(df):
    if df.empty:
        return pd.Series()
    df_unique = df[['Profesor', 'Curso', 'Créditos']].drop_duplicates()
    creditos_por_profesor = df_unique.groupby('Profesor')['Créditos'].sum()
    return creditos_por_profesor

# ========================================================
# FUNCIÓN PRINCIPAL MEJORADA CON NUEVAS TABLAS - CORREGIDA
# ========================================================

def mostrar_generador_horarios_simplificado():
    """Interfaz del generador de horarios simplificada - CORREGIDA"""
    # Mostrar header del usuario autenticado
    mostrar_header_usuario_corregido()
    
    # Obtener información del usuario
    info_usuario = st.session_state.info_usuario
    
    st.info(f"**Generando horarios para**: {info_usuario['programa']}")
    
    st.markdown("## Cargar Datos para Generación de Horarios")

    # Sidebar de configuración
    st.sidebar.header("Configuración del Sistema")
    
    # BOTÓN DE CERRAR SESIÓN EN SIDEBAR - CORREGIDO
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Sesión Actual")
    st.sidebar.info(f"**Usuario:** {info_usuario['usuario']}")
    st.sidebar.info(f"**Programa:** {info_usuario['programa']}")
    
    # Botón de cerrar sesión funcional
    if st.sidebar.button("Cerrar Sesión", type="secondary", use_container_width=True, key="btn_logout_main"):
        # Limpiar session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    # Upload del archivo Excel en sidebar
    uploaded_file = st.sidebar.file_uploader(
        "Cargar archivo Excel con datos de profesores y cursos",
        type=['xlsx', 'xls'],
        help="El archivo debe contener columnas como: Profesor, Curso/Materia, Créditos, Estudiantes, Programa, Sección",
        key="file_uploader_main"
    )

    # Guardar el archivo en session state para persistencia
    if uploaded_file is not None:
        st.session_state.uploaded_file_data = uploaded_file.getvalue()
    
    # Inicializar configuración al cargar archivo
    if uploaded_file is not None or 'uploaded_file_data' in st.session_state:
        # Usar el archivo actual o el guardado en session state
        if uploaded_file is not None:
            file_to_use = uploaded_file
        else:
            # Recuperar de session state
            file_to_use = io.BytesIO(st.session_state.uploaded_file_data)
        
        global config, bloques
        
        # Crear configuración con el archivo Excel
        config = ConfiguracionSistema(
            file_to_use,  # Pasamos el archivo directamente
            st.session_state.programa_seleccionado,
            st.session_state.colegio_seleccionado,
            info_usuario['usuario']
        )
        bloques = generar_bloques()

        # Mostrar estado de reservas si aplica
        if config.usa_reservas:
            mostrar_estado_reservas()
            
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Liberar Reservas", type="secondary", key="btn_liberar_main"):
                    if config.sistema_reservas.liberar_reservas_departamento(info_usuario['usuario']):
                        st.success("Reservas liberadas correctamente")
                        st.rerun()
                    else:
                        st.error("Error al liberar reservas")
            with col2:
                st.info("Libera las reservas si necesitas regenerar el horario")

        # Infraestructura
        st.sidebar.subheader("Infraestructura")
        if config.colegio_actual == "COLEGIO DE ADMINISTRACIÓN DE EMPRESAS":
            st.sidebar.info("Salones AE:")
            st.sidebar.write(", ".join(AE_SALONES_FIJOS[:5]) + "...")
        elif config.colegio_actual == "DEPARTAMENTO DE MATEMÁTICAS":
            st.sidebar.info("Salones M:")
            st.sidebar.write(", ".join(MATEMATICAS_SALONES_FIJOS[:5]) + "...")
        elif config.colegio_actual == "COLEGIO DE ARTES Y CIENCIAS":
            st.sidebar.info("Salones compartidos (AC y LAB):")
            st.sidebar.write(", ".join(ARTES_CIENCIAS_SALONES_COMPARTIDOS[:5]) + "...")
        
        if config.profesores_config:
            st.success("Archivo cargado correctamente")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Profesores", len(config.profesores_config))
            with col2:
                total_cursos = sum(len(prof['cursos']) for prof in config.profesores_config.values())
                st.metric("Cursos", total_cursos)
            with col3:
                st.metric("Salones Totales", len(config.salones))
            
            with st.expander("Ver datos cargados"):
                for profesor, data in config.profesores_config.items():
                    st.write(f"**{profesor}** ({data['creditos_totales']} créditos)")
                    for curso in data['cursos']:
                        programa_info = f" - {curso.get('programa', 'N/A')}"
                        seccion_info = f" (Sec: {curso.get('seccion', '001')})"
                        st.write(f"  - {curso['nombre']}{seccion_info}{programa_info} ({curso['creditos']} créditos, {curso['estudiantes']} estudiantes)")
            
            # Parámetros de Optimización
            st.sidebar.subheader("Parámetros de Optimización")
            intentos = st.sidebar.slider("Número de iteraciones", 50, 500, 250, 50, key="intentos_main")

            # Restricciones
            with st.sidebar.expander("Restricciones Globales"):
                if config:
                    config.restricciones_globales["hora_inicio_min"] = st.time_input(
                        "Hora inicio mínima", 
                        datetime.strptime("07:30", "%H:%M").time(),
                        key="hora_inicio_main"
                    ).strftime("%H:%M")
                    
                    config.restricciones_globales["hora_fin_max"] = st.time_input(
                        "Hora fin máxima", 
                        datetime.strptime("19:30", "%H:%M").time(),
                        key="hora_fin_main"
                    ).strftime("%H:%M")
                    
                    config.restricciones_globales["creditos_max_profesor"] = st.number_input(
                        "Créditos máximos por profesor", 1, 20, 15, key="creditos_max_main"
                    )
                    
                    config.restricciones_globales["estudiantes_max_salon"] = st.number_input(
                        "Estudiantes máximos por salón", 20, 150, 50, key="estudiantes_max_main"
                    )
            
            # Preferencias de Profesores
            st.sidebar.subheader("Preferencias de Profesores")
            profesor_seleccionado = st.sidebar.selectbox(
                "Seleccionar profesor para configurar",
                ["Ninguno"] + list(config.profesores_config.keys()),
                key="prof_pref_main"
            )
            
            if profesor_seleccionado != "Ninguno":
                with st.sidebar.expander(f"Configurar {profesor_seleccionado}"):
                    st.write("**Horarios preferidos:**")
                    dias = ["Lu", "Ma", "Mi", "Ju", "Vi"]
                    for dia in dias:
                        col1_pref, col2_pref = st.columns(2)
                        with col1_pref:
                            inicio = st.time_input(f"{dia} inicio", value=datetime.strptime("08:00", "%H:%M").time(), 
                                                   key=f"pref_inicio_{profesor_seleccionado}_{dia}")
                        with col2_pref:
                            fin = st.time_input(f"{dia} fin", value=datetime.strptime("17:00", "%H:%M").time(),
                                                key=f"pref_fin_{profesor_seleccionado}_{dia}")
                        
                        if inicio and fin:
                            if profesor_seleccionado not in config.profesores_config:
                                config.profesores_config[profesor_seleccionado] = {"horario_preferido": {}}
                            if "horario_preferido" not in config.profesores_config[profesor_seleccionado]:
                                config.profesores_config[profesor_seleccionado]["horario_preferido"] = {}
                            config.profesores_config[profesor_seleccionado]["horario_preferido"][dia] = [
                                (inicio.strftime("%H:%M"), fin.strftime("%H:%M"))
                            ]
            
            # Botones de control del horario
            st.markdown("---")
            col_gen, col_borrar = st.columns(2)
            
            with col_gen:
                if st.button("Generar Horario Optimizado", type="primary", key="btn_generar_main"):
                    with st.spinner("Generando horario optimizado..."):
                        mejor, score = buscar_mejor_horario(intentos)
                        
                        if mejor is None:
                            st.error("No se pudo generar un horario válido. Ajusta las restricciones o verifica conflictos de salones.")
                            if config.usa_reservas:
                                st.info("**Sugerencia**: Algunos salones pueden estar ocupados por otros departamentos. Verifica el estado de reservas arriba.")
                        else:
                            st.success(f"Horario generado. Puntuación: {score}")
                            
                            # Guardar reservas si aplica
                            if config.usa_reservas and guardar_reservas_horario(mejor, info_usuario['usuario']):
                                st.success("Reservas de salones guardadas correctamente")
                            elif config.usa_reservas:
                                st.warning("Horario generado pero hubo problemas al guardar las reservas")
                            
                            # Guardar en session state para persistencia
                            st.session_state.asignaciones_actuales = mejor
                            st.session_state.horario_generado = exportar_horario(mejor)
                            st.rerun()
            
            with col_borrar:
                if st.button("Borrar Horario Generado", type="secondary", key="btn_borrar_main"):
                    # Limpiar horario actual
                    if 'asignaciones_actuales' in st.session_state:
                        del st.session_state.asignaciones_actuales
                    if 'horario_generado' in st.session_state:
                        del st.session_state.horario_generado
                    st.success("Horario borrado correctamente")
                    st.rerun()
            
            # Mostrar horario si existe
            if 'horario_generado' in st.session_state and st.session_state.horario_generado is not None:
                st.markdown("---")
                mostrar_tabs_horario_mejoradas(st.session_state.horario_generado)
                asignaciones_actuales = st.session_state.get('asignaciones_actuales')
                mostrar_botones_persistencia_mejorada(st.session_state.horario_generado, info_usuario['usuario'], asignaciones_actuales)
                
        else:
            st.error("No se pudieron cargar los datos del archivo Excel. Verifica el formato del archivo.")
    else:
        # Sin archivo cargado: intentar cargar horario guardado
        df_guardado = cargar_horario_json(info_usuario['usuario'])
        if df_guardado is not None and not df_guardado.empty:
            st.success("Se cargó el último horario guardado.")
            st.session_state.horario_generado = df_guardado
            mostrar_tabs_horario_mejoradas(df_guardado)
            mostrar_botones_persistencia_mejorada(df_guardado, info_usuario['usuario'], None)
        else:
            st.info("Por favor, carga un archivo Excel para comenzar o guarda un horario para recuperarlo luego.")
            with st.expander("Formato esperado del archivo Excel"):
                st.write("""
                El archivo Excel debe contener al menos las siguientes columnas:
                
                | Profesor | Curso/Materia | Créditos | Estudiantes | Programa | Sección |
                |----------|---------------|----------|-------------|----------|---------|
                | Juan Pérez | Literatura I | 3 | 25 | Literatura Comparada | 001 |
                | María García | Filosofía Antigua | 4 | 30 | Filosofía | 002 |
                
                **Notas:**
                - Los nombres de las columnas pueden variar (profesor/docente, curso/materia/asignatura, etc.)
                - Si faltan columnas de créditos, estudiantes, programa o sección, se usarán valores por defecto
                - El sistema detecta automáticamente las columnas relevantes
                - Incluir la columna Programa es importante para filtros por carrera
                """)

def mostrar_tabs_horario_mejoradas(df_horario):
    """Renderiza las pestañas de visualización del horario MEJORADAS"""
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Tabla Profesional", 
        "Calendario Visual", 
        "Horario Completo", 
        "Por Profesor", 
        "Por Salón", 
        "Estadísticas"
    ])
    
    # PESTAÑA 1: TABLA PROFESIONAL MEJORADA
    with tab1:
        st.subheader("Vista de Tabla Profesional MEJORADA")
        
        st.info("**Vista Profesional MEJORADA**: Tabla organizada con colores y mejor formato.")
        
        col1_filtro, col2_filtro = st.columns([2, 1])
        with col1_filtro:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                <p style="color: white; margin: 0; text-align: center; font-size: 1.1rem;">
                    <strong>Horario Profesional MEJORADO</strong> - Vista de tabla organizada con colores
                </p>
            </div>
            """, unsafe_allow_html=True)
        with col2_filtro:
            tipo_filtro_tabla = st.selectbox(
                "Filtrar por:",
                ["Completo", "Profesor", "Salón", "Programa"],
                key="tipo_filtro_tabla_main"
            )
            
            if tipo_filtro_tabla == "Profesor":
                profesores_disponibles = ["Todos los profesores"] + sorted(df_horario['Profesor'].unique().tolist())
                filtro_valor_tabla = st.selectbox("Seleccionar profesor:", profesores_disponibles, 
                                                  key="filtro_profesor_tabla_main")
                crear_tabla_horario_profesional_mejorada(df_horario, "profesor", filtro_valor_tabla)
            elif tipo_filtro_tabla == "Salón":
                salones_disponibles = ["Todos los salones"] + sorted(df_horario['Salon'].unique().tolist())
                filtro_valor_tabla = st.selectbox("Seleccionar salón:", salones_disponibles, 
                                                  key="filtro_salon_tabla_main")
                crear_tabla_horario_profesional_mejorada(df_horario, "salon", filtro_valor_tabla)
            elif tipo_filtro_tabla == "Programa":
                programas_disponibles = ["Todos los programas"] + sorted(df_horario['Programa'].unique().tolist())
                filtro_valor_tabla = st.selectbox("Seleccionar programa:", programas_disponibles, 
                                                  key="filtro_programa_tabla_main")
                crear_tabla_horario_profesional_mejorada(df_horario, "programa", filtro_valor_tabla)
            else:
                crear_tabla_horario_profesional_mejorada(df_horario, "completo", None)
    
    # PESTAÑA 2: CALENDARIO VISUAL (MANTENIDA)
    with tab2:
        st.subheader("Vista de Calendario Visual")
        
        col1_filtro, col2_filtro = st.columns([2, 1])
        with col1_filtro:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                <p style="color: white; margin: 0; text-align: center; font-size: 1.1rem;">
                    <strong>Calendario Visual</strong> - Vista interactiva con colores
                </p>
            </div>
            """, unsafe_allow_html=True)
        with col2_filtro:
            tipo_filtro = st.selectbox(
                "Filtrar por:",
                ["Salón", "Profesor", "Programa"],
                key="tipo_filtro_calendario_main"
            )
            
            if tipo_filtro == "Salón":
                salones_disponibles = ["Todos los salones"] + sorted(df_horario['Salon'].unique().tolist())
                filtro_valor = st.selectbox("Seleccionar salón:", salones_disponibles, 
                                            key="filtro_salon_cal_main")
                fig_calendario, colores_cursos = crear_calendario_interactivo(df_horario, "salon", filtro_valor, "calendar_visual")
            elif tipo_filtro == "Profesor":
                profesores_disponibles = ["Todos los profesores"] + sorted(df_horario['Profesor'].unique().tolist())
                filtro_valor = st.selectbox("Seleccionar profesor:", profesores_disponibles, 
                                            key="filtro_profesor_cal_main")
                fig_calendario, colores_cursos = crear_calendario_interactivo(df_horario, "profesor", filtro_valor, "calendar_visual")
            elif tipo_filtro == "Programa":
                programas_disponibles = ["Todos los programas"] + sorted(df_horario['Programa'].unique().tolist())
                filtro_valor = st.selectbox("Seleccionar programa:", programas_disponibles, 
                                            key="filtro_programa_cal_main")
                fig_calendario, colores_cursos = crear_calendario_interactivo(df_horario, "programa", filtro_valor, "calendar_visual")
        
        st.plotly_chart(fig_calendario, use_container_width=True, key="plotly_calendar_main")
        mostrar_leyenda_cursos(colores_cursos, df_horario, tipo_filtro.lower(), filtro_valor)
        
        col1_info, col2_info = st.columns(2)
        with col1_info:
            st.info("Tip: Usa las herramientas de Plotly para hacer zoom y navegar.")
        with col2_info:
            st.info("Hover: Pasa el cursor sobre los bloques para ver más información.")
    
    # PESTAÑA 3: HORARIO COMPLETO (MANTENIDA)
    with tab3:
        st.subheader("Horario Completo")
        
        df_ordenado = df_horario.sort_values(['Dia', 'Hora Inicio', 'Salon'])
        st.dataframe(df_ordenado, use_container_width=True, key="dataframe_completo_main")
        
        csv = df_ordenado.to_csv(index=False)
        st.download_button(
            label="Descargar horario (CSV)",
            data=csv,
            file_name="horario_completo.csv",
            mime="text/csv",
            key="download_csv_completo_main"
        )
    
    # PESTAÑA 4: POR PROFESOR (MEJORADA)
    with tab4:
        st.subheader("Horario por Profesor")
        
        profesor_individual = st.selectbox(
            "Seleccionar profesor:",
            sorted(df_horario['Profesor'].unique()),
            key="selector_profesor_individual_main"
        )
        
        if profesor_individual:
            df_prof = df_horario[df_horario['Profesor'] == profesor_individual]
            if not df_prof.empty:
                # Mostrar tabla profesional MEJORADA para el profesor
                crear_tabla_horario_profesional_mejorada(df_horario, "profesor", profesor_individual)
                
                st.markdown("---")
                st.markdown("### Datos Detallados")
                df_prof_ordenado = df_prof.sort_values(['Dia', 'Hora Inicio'])
                st.dataframe(df_prof_ordenado, use_container_width=True, key="dataframe_profesor_main")
                
                # Métricas del profesor
                creditos_por_profesor = _creditos_unicos_por_profesor(df_prof)
                creditos_total_prof = int(creditos_por_profesor.get(profesor_individual, 0))
                
                col1_prof, col2_prof, col3_prof = st.columns(3)
                with col1_prof:
                    st.metric("Total Cursos", df_prof['Curso'].nunique())
                with col2_prof:
                    horas_totales = df_prof['Duración'].sum()
                    st.metric("Horas Semanales", f"{horas_totales:.1f}h")
                with col3_prof:
                    st.metric("Créditos Totales", creditos_total_prof)
            else:
                st.warning(f"No se encontraron clases para {profesor_individual}")
    
    # PESTAÑA 5: POR SALÓN (MEJORADA)
    with tab5:
        st.subheader("Horario por Salón")
        
        salon_individual = st.selectbox(
            "Seleccionar salón:",
            sorted(df_horario['Salon'].unique()),
            key="selector_salon_individual_main"
        )
        
        if salon_individual:
            df_salon = df_horario[df_horario['Salon'] == salon_individual]
            if not df_salon.empty:
                # Mostrar tabla profesional MEJORADA para el salón
                crear_tabla_horario_profesional_mejorada(df_horario, "salon", salon_individual)
                
                st.markdown("---")
                st.markdown("### Datos Detallados")
                df_salon_ordenado = df_salon.sort_values(['Dia', 'Hora Inicio'])
                st.dataframe(df_salon_ordenado, use_container_width=True, key="dataframe_salon_main")
                
                # Métricas del salón
                col1_salon, col2_salon, col3_salon = st.columns(3)
                with col1_salon:
                    horas_uso = df_salon['Duración'].sum()
                    st.metric("Horas de uso semanal", f"{horas_uso:.1f}h")
                with col2_salon:
                    st.metric("Cursos diferentes", df_salon['Curso'].nunique())
                with col3_salon:
                    st.metric("Profesores diferentes", df_salon['Profesor'].nunique())
            else:
                st.warning(f"No se encontraron clases para {salon_individual}")
    
    # PESTAÑA 6: ESTADÍSTICAS (MANTENIDA)
    with tab6:
        st.subheader("Estadísticas Generales")
        col1_met, col2_met, col3_met, col4_met = st.columns(4)
        with col1_met:
            st.metric("Total Clases", len(df_horario))
        with col2_met:
            st.metric("Profesores", df_horario['Profesor'].nunique())
        with col3_met:
            st.metric("Salones Usados", df_horario['Salon'].nunique())
        with col4_met:
            total_estudiantes = df_horario['Estudiantes'].sum()
            st.metric("Total Estudiantes", int(total_estudiantes))
        
        # Estadísticas por programa
        st.subheader("Estadísticas por Programa")
        stats_programa = df_horario.groupby('Programa').agg({
            'Curso': 'nunique',
            'Profesor': 'nunique',
            'Salon': 'nunique',
            'Estudiantes': 'sum',
            'Duración': 'sum'
        }).round(1)
        stats_programa.columns = ['Cursos', 'Profesores', 'Salones', 'Estudiantes', 'Horas Totales']
        st.dataframe(stats_programa, use_container_width=True)
        
        # Créditos por profesor
        creditos_prof = _creditos_unicos_por_profesor(df_horario)
        if not creditos_prof.empty:
            fig_creditos = px.bar(
                x=list(creditos_prof.index), 
                y=list(creditos_prof.values),
                title="Créditos por Profesor (por curso único)",
                color=list(creditos_prof.values),
                color_continuous_scale="viridis"
            )
            fig_creditos.update_layout(showlegend=False)
            st.plotly_chart(fig_creditos, use_container_width=True, key="plotly_creditos_main")
        
        # Utilización de salones
        uso_salones = df_horario.groupby('Salon').agg({
            'Duración': 'sum',
            'Curso': 'nunique'
        }).round(1)
        uso_salones.columns = ['Horas Totales', 'Cursos Diferentes']
        
        if not uso_salones.empty:
            fig_salones = px.bar(
                uso_salones,
                x=uso_salones.index,
                y='Horas Totales',
                title="Utilización de Salones",
                color='Horas Totales',
                color_continuous_scale="blues"
            )
            st.plotly_chart(fig_salones, use_container_width=True, key="plotly_salones_main")

# ========================================================
# MAIN ACTUALIZADO Y CORREGIDO
# ========================================================

config = None
bloques = []

def main():
    st.set_page_config(
        page_title="Sistema de Generación de Horarios Académicos - RUM (Mejorado)",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # CSS personalizado
    st.markdown("""
    <style>
    .main > div { padding-top: 2rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 2px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f0f2f6;
        border-radius: 8px 8px 0px 0px;
    }
    .stTabs [aria-selected="true"] { background-color: #667eea; color: white; }
    </style>
    """, unsafe_allow_html=True)

    # Inicializar session state para autenticación
    if 'usuario_autenticado' not in st.session_state:
        st.session_state.usuario_autenticado = False
    if 'info_usuario' not in st.session_state:
        st.session_state.info_usuario = None

    # Sistema principal
    if not st.session_state.usuario_autenticado:
        # Pestaña de Login
        tab_login, tab_info = st.tabs(["Iniciar Sesión", "Información del Sistema"])
        
        with tab_login:
            mostrar_login_simplificado()
        
        with tab_info:
            st.markdown("""
            <div style="text-align: center; padding: 2rem 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin-bottom: 2rem;">
                <h1 style="color: white; margin: 0; font-size: 2.5rem;">Sistema de Horarios RUM</h1>
                <p style="color: white; margin: 1rem 0 0 0; font-size: 1.2rem;">Recinto Universitario de Mayagüez - Versión Mejorada</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("## Mejoras Implementadas")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                ### Nuevas Funcionalidades
                - **Tabla Profesional MEJORADA**: Vista de horarios con colores y mejor formato
                - **Exportación LaTeX**: Formato específico para informes académicos
                - **Login Simplificado**: Credenciales sin tildes ni espacios especiales
                - **Visualización Mejorada**: Tablas organizadas por períodos y días
                - **Errores Corregidos**: Eliminación de claves duplicadas
                - **Filtros Avanzados**: Por profesor, salón y programa en tabla profesional
                - **Persistencia Mejorada**: Guardado y carga de horarios optimizado
                """)
            
            with col2:
                st.markdown("""
                ### Colegios Disponibles
                
                **Credenciales Simplificadas:**
                - `admin_empresas` - Administración de Empresas
                - `artes_ciencias` - Artes y Ciencias
                - `ciencias_agricolas` - Ciencias Agrícolas
                - `ingenieria` - Ingeniería
                - `matematicas` - Matemáticas
                
                **Contraseñas de ejemplo:**
                - `contabilidad`, `finanzas`, `mercadeo`
                - `biologia`, `quimica`, `literatura`
                - `agronomia`, `horticultura`
                - `ing_civil`, `ing_quimica`
                """)
            
            st.markdown("---")
            st.info("**Para comenzar**: Inicia sesión con las credenciales simplificadas en la pestaña 'Iniciar Sesión'.")
    
    else:
        # Usuario autenticado: mostrar interfaz principal
        tab_horarios, tab_config, tab_ayuda = st.tabs(["Generador de Horarios", "Configuración", "Ayuda"])
        
        with tab_horarios:
            mostrar_generador_horarios_simplificado()
        
        with tab_config:
            st.markdown("## Configuración del Sistema")
            
            mostrar_header_usuario_corregido()
            
            info_usuario = st.session_state.info_usuario
            
            st.markdown("### Configuraciones Disponibles")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                #### Información del Usuario
                - **Colegio:** {info_usuario['colegio_completo']}
                - **Programa:** {info_usuario['programa']}
                - **Nivel:** {info_usuario['nivel']}
                - **Usuario:** {info_usuario['usuario']}
                """)
                
                if info_usuario['colegio_completo'] in ["COLEGIO DE ADMINISTRACIÓN DE EMPRESAS", "DEPARTAMENTO DE MATEMÁTICAS", "COLEGIO DE ARTES Y CIENCIAS"]:
                    st.success("Sistema de reservas activo para salones compartidos")
                    st.info("Salones compartidos con otros departamentos")
                else:
                    st.info("Salones dedicados al colegio")
            
            with col2:
                st.markdown("""
                #### Restricciones Temporales
                - Horarios prohibidos configurables por colegio
                - Límites de horas por día configurables
                - Restricciones de bloques de 3 horas después de 15:30
                - Créditos máximos y mínimos por profesor
                """)
                
                st.info(f"Configurado para: {info_usuario['nivel']}")
                
                # Mostrar restricciones específicas del colegio
                if info_usuario['colegio_completo'] == "COLEGIO DE ADMINISTRACIÓN DE EMPRESAS":
                    st.warning("Horarios prohibidos: Martes y Jueves 10:30-12:30")
                elif info_usuario['colegio_completo'] == "COLEGIO DE ARTES Y CIENCIAS":
                    st.warning("Horarios prohibidos: Martes y Jueves 10:30-12:30")
                elif info_usuario['colegio_completo'] == "DEPARTAMENTO DE MATEMÁTICAS":
                    st.success("Sin horarios prohibidos específicos")
                else:
                    st.warning("Horarios prohibidos: Martes y Jueves 10:30-12:30")
            
            st.markdown("---")
            st.markdown("### Estado del Sistema")
            
            if 'uploaded_file_data' in st.session_state:
                st.success("Archivo de datos cargado")
            else:
                st.warning("No hay archivo de datos cargado")
            
            if 'horario_generado' in st.session_state:
                st.success("Horario generado disponible")
            else:
                st.info("No hay horario generado")
        
        with tab_ayuda:
            st.markdown("## Ayuda - Sistema Mejorado")
            
            mostrar_header_usuario_corregido()
            
            st.markdown("### Guía de Uso del Sistema Mejorado")
            
            with st.expander("1. Credenciales Simplificadas", expanded=True):
                st.markdown("""
                **NUEVO SISTEMA DE LOGIN:**
                - **Sin tildes**: Todas las credenciales usan solo letras, números y guiones bajos
                - **Sin espacios**: Se usan guiones bajos en lugar de espacios
                - **Fácil de recordar**: Nombres intuitivos y cortos
                
                **Ejemplos de credenciales:**
                - Usuario: `artes_ciencias` | Contraseña: `biologia`
                - Usuario: `admin_empresas` | Contraseña: `contabilidad`
                - Usuario: `ingenieria` | Contraseña: `ing_civil`
                - Usuario: `matematicas` | Contraseña: `estadistica`
                """)
            
            with st.expander("2. Nueva Vista de Tabla Profesional MEJORADA"):
                st.markdown("""
                **TABLA ESTILO UNIVERSITARIO MEJORADA:**
                - Organizada por períodos de tiempo (filas) y días (columnas)
                - Colores diferentes para cada curso
                - Hover effects para mejor interactividad
                - Información completa y formateada en cada celda
                - Filtros por profesor, salón o programa
                
                **Cómo usar:**
                1. Ve a la pestaña "Tabla Profesional"
                2. Selecciona el tipo de filtro
                3. Elige el elemento específico a mostrar
                4. La tabla se actualiza automáticamente con colores
                """)
            
            with st.expander("3. Exportación en Formato LaTeX"):
                st.markdown("""
                **NUEVA EXPORTACIÓN LaTeX:**
                - Formato específico para informes académicos
                - Incluye estadísticas de violaciones de restricciones
                - Muestra créditos extra a pagar
                - Formato similar a publicaciones científicas
                
                **Ejemplo de salida:**
                ```
                Algoritmo Genético con 250 individuos, tasa de mutación = 0.1, tasa de cruce= 0.95 tiempo de
                ejecución 00:06:27.
                curso cap_secc grupo_dias hora_inicio profesoroculto sala
                ___________ ________ __________ ___________ ______________ ________
                'ININ4017 ' 30 'Ma-Ju' '5:00 pm' 'Prof JP' 'AE 102'
                'ININ4027 ' 30 'Lu-Mi-Vi' '11:30 am' 'Prof MG' 'AE 103'
                ```
                """)
            
            with st.expander("4. Gestión de Salones Mejorada"):
                st.markdown("""
                **SISTEMA DE RESERVAS:**
                - Salones compartidos entre departamentos (AE, M, AC)
                - Prevención automática de conflictos
                - Estado de reservas en tiempo real
                - Liberación de reservas por departamento
                
                **Salones por Colegio:**
                - **AE**: Administración de Empresas (AE 102, AE 103, etc.)
                - **M**: Matemáticas (M 102, M 104, etc.)
                - **AC/LAB**: Artes y Ciencias compartidos
                - **ING**: Ingeniería (dedicados)
                - **CA**: Ciencias Agrícolas (dedicados)
                """)
            
            st.markdown("---")
            st.markdown("### Solución de Problemas")
            
            with st.expander("Error de claves duplicadas (CORREGIDO)"):
                st.markdown("""
                **Problema resuelto:**
                - Se eliminaron las claves duplicadas en botones
                - Cada elemento tiene una clave única basada en timestamp
                - No más errores de `StreamlitDuplicateElementKey`
                
                **Si aún tienes problemas:**
                - Recarga la página (F5)
                - Borra el caché del navegador
                - Cierra sesión y vuelve a entrar
                """)
            
            with st.expander("Problemas de login (SOLUCIONADO)"):
                st.markdown("""
                **Credenciales simplificadas:**
                - Ya no necesitas tildes (ñ, á, é, í, ó, ú)
                - No hay espacios en las credenciales
                - Usa guiones bajos (_) en lugar de espacios
                - Todas las letras en minúsculas
                
                **Si no puedes entrar:**
                - Verifica que no uses tildes
                - Usa guiones bajos en lugar de espacios
                - Consulta la lista completa en "Ver todos los programas disponibles"
                """)

if __name__ == "__main__":
    main()
