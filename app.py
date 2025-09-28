import streamlit as st
import pandas as pd
import random
import json
import numpy as np
from datetime import datetime, timedelta
import copy
import io

# ========================================================
# CONFIGURACIÓN DEL SISTEMA - CARGA DESDE EXCEL
# ========================================================

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

# (Aquí van todas tus funciones y clases: generar_bloques, tabla_creditos, calcular_creditos_adicionales, a_minutos,
# es_bloque_tres_horas_valido, horario_valido, cumple_horario_preferido, AsignacionClase, generar_horario_valido,
# hay_conflictos, evaluar_horario, buscar_mejor_horario, exportar_horario)

# ========================================================
# NUEVA FUNCIÓN: CONSTRUIR CALENDARIO
# ========================================================
def construir_calendario(df, dias=None, horas=horas_inicio):
    """
    Construye una tabla tipo calendario (rows = Hora Inicio, cols = días).
    df debe contener al menos las columnas: 'Dia', 'Hora Inicio', 'Hora Fin', 'Curso', 'Profesor', 'Salon'.
    """
    if dias is None:
        dias = ["Lu", "Ma", "Mi", "Ju", "Vi"]

    # Filtrar horas visibles según restricciones globales (si existe config)
    try:
        inicio_min = a_minutos(config.restricciones_globales["hora_inicio_min"])
        fin_max = a_minutos(config.restricciones_globales["hora_fin_max"])
    except Exception:
        inicio_min = min(a_minutos(h) for h in horas)
        fin_max = max(a_minutos(h) for h in horas)

    # Crear lista de horas que mostraremos (filtrando por el rango global)
    horas_visibles = [h for h in horas if inicio_min <= a_minutos(h) <= fin_max]

    # Inicializar DataFrame vacío con índice = Horas y columnas = Días
    filas = []
    for h in horas_visibles:
        fila = {"Hora": h}
        for d in dias:
            fila[d] = ""
        filas.append(fila)
    cal_df = pd.DataFrame(filas).set_index("Hora")

    # Asegurar que las columnas son los días en el orden correcto
    cal_df = cal_df[[d for d in dias]]

    # Rellenar celdas con las clases que empiezan en esa hora y día
    for _, r in df.iterrows():
        dia = r.get("Dia")
        hora_ini = r.get("Hora Inicio")
        hora_fin = r.get("Hora Fin")
        curso = r.get("Curso")
        salon = r.get("Salon")
        profesor = r.get("Profesor")

        if pd.isna(dia) or pd.isna(hora_ini):
            continue

        # Si la hora de inicio no está en las filas (por alguna razón), la añadimos
        if hora_ini not in cal_df.index:
            cal_df.loc[hora_ini] = [""] * len(cal_df.columns)
            # reordenar índice por tiempo
            cal_df = cal_df.reindex(sorted(cal_df.index, key=lambda x: a_minutos(str(x))))

        if dia not in cal_df.columns:
            continue

        contenido = f"{curso} ({salon})\n{hora_ini}-{hora_fin}"
        actual = cal_df.at[hora_ini, dia]
        if actual and str(actual).strip() != "":
            cal_df.at[hora_ini, dia] = f"{actual}  |  {contenido}"
        else:
            cal_df.at[hora_ini, dia] = contenido

    # Ordenar índice por hora (por si se agregaron filas fuera del orden)
    cal_df = cal_df.loc[sorted(cal_df.index, key=lambda x: a_minutos(str(x)))]
    return cal_df

# ========================================================
# STREAMLIT INTERFAZ
# ========================================================

st.title("🗓️ Generador de Horarios Académicos")

# Cargar Excel de configuración
archivo = st.file_uploader("Sube tu archivo Excel de cursos", type=["xlsx"])
if archivo:
    config = ConfiguracionSistema(archivo_excel=archivo)
else:
    st.warning("⚠️ Por favor sube un archivo Excel válido para configurar los cursos")
    config = ConfiguracionSistema()  # Por defecto

# Suponiendo que df_horario ya fue generado previamente
# df_horario = exportar_horario(mejor_horario)

# ============================================
# PESTAÑAS STREAMLIT
# ============================================

tab1, tab2, tab3, tab4 = st.tabs(["📊 Horario Completo", "👨‍🏫 Por Profesor (Calendario)", "🏫 Por Salón (Calendario)", "📈 Estadísticas"])

with tab1:
    st.subheader("📊 Horario Completo (lista)")
    st.dataframe(df_horario, use_container_width=True)

    # Descargas
    csv = df_horario.to_csv(index=False)
    st.download_button("💾 Descargar horario CSV", csv, "horario_generado.csv", "text/csv")
    
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
        df_horario.to_excel(writer, index=False, sheet_name="Horario")
    st.download_button("💾 Descargar horario Excel", excel_buffer.getvalue(), "horario_generado.xlsx", "application/vnd.ms-excel")

with tab2:
    st.subheader("👨‍🏫 Horario por Profesor (Calendario)")
    for profesor in config.profesores_config.keys():
        with st.expander(f"Horario de {profesor}"):
            df_prof = df_horario[df_horario['Profesor'] == profesor]
            if not df_prof.empty:
                cal_prof = construir_calendario(df_prof)
                st.dataframe(cal_prof, use_container_width=True)
            else:
                st.warning(f"No se encontraron clases para {profesor}")

with tab3:
    st.subheader("🏫 Horario por Salón (Calendario)")
    for salon in config.salones:
        with st.expander(f"Horario del {salon}"):
            df_salon = df_horario[df_horario['Salon'] == salon]
            if not df_salon.empty:
                cal_salon = construir_calendario(df_salon)
                st.dataframe(cal_salon, use_container_width=True)
            else:
                st.info(f"No hay clases asignadas al {salon}")

with tab4:
    st.subheader("📈 Estadísticas del Horario")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Distribución de créditos por profesor:**")
        creditos_prof = df_horario.groupby('Profesor')['Créditos'].sum()
        st.bar_chart(creditos_prof)
    
    with col2:
        st.write("**Utilización de salones:**")
        uso_salones = df_horario.groupby('Salon').size()
        st.bar_chart(uso_salones)
