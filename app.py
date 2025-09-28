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
        try:
            excel_data = pd.read_excel(self.archivo_excel, sheet_name=None)
            st.write(f"📊 Hojas disponibles en el Excel: {list(excel_data.keys())}")
            hoja_cursos = None
            for nombre_hoja, df in excel_data.items():
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
        if self.cursos_df is None: return
        df = self.cursos_df.copy()
        df.columns = [col.lower().strip().replace(' ', '_') for col in df.columns]
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
        if 'profesor' not in columnas_finales or 'curso' not in columnas_finales:
            st.error("❌ Error: No se encontraron las columnas básicas (profesor, curso)")
            return
        if 'creditos' not in columnas_finales:
            df['creditos_default'] = 3
            columnas_finales['creditos'] = 'creditos_default'
            st.warning("⚠️ No se encontró columna de créditos, usando 3 por defecto")
        if 'estudiantes' not in columnas_finales:
            df['estudiantes_default'] = 30
            columnas_finales['estudiantes'] = 'estudiantes_default'
            st.warning("⚠️ No se encontró columna de estudiantes, usando 30 por defecto")
        df = df.dropna(subset=[columnas_finales['profesor'], columnas_finales['curso']])
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
                try:
                    creditos = int(float(fila[columnas_finales['creditos']]))
                except (ValueError, TypeError):
                    creditos = 3
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
        total_cursos = sum(len(config['cursos']) for config in self.profesores_config.values())
        num_salones = max(3, min(10, total_cursos // 3))
        self.salones = [f"Salon {i+1}" for i in range(num_salones)]
        st.success(f"✅ Configuración completada: {len(self.profesores_config)} profesores, {num_salones} salones")

# ========================================================
# BLOQUES, TABLAS Y FUNCIONES DE HORARIO
# ========================================================

# (Aquí van todas las funciones que ya tenías: generar_bloques, calcular_creditos_adicionales,
# a_minutos, es_bloque_tres_horas_valido, horario_valido, cumple_horario_preferido, 
# AsignacionClase, generar_horario_valido, hay_conflictos, evaluar_horario, buscar_mejor_horario, exportar_horario)

# ========================================================
# EXPORTAR HORARIO EN FORMATO TABLA SEMANAL
# ========================================================

def exportar_horario_tabla(asignaciones):
    dias_semana = ["Lu", "Ma", "Mi", "Ju", "Vi"]
    tabla = {}
    horas_unicas = sorted({a.hora_inicio for a in asignaciones}, key=lambda x: a_minutos(x))
    for hora in horas_unicas:
        tabla[hora] = {dia: "" for dia in dias_semana}
    for asig in asignaciones:
        for dia in asig.bloque["dias"]:
            contenido = f"{asig.curso_nombre} ({asig.profesor}) [{asig.salon}]"
            if tabla[asig.hora_inicio][dia]:
                tabla[asig.hora_inicio][dia] += "\n" + contenido
            else:
                tabla[asig.hora_inicio][dia] = contenido
    df_tabla = pd.DataFrame.from_dict(tabla, orient='index')
    df_tabla.index.name = "Hora"
    df_tabla = df_tabla.rename(columns={"Lu":"Lunes","Ma":"Martes","Mi":"Miércoles","Ju":"Jueves","Vi":"Viernes"})
    df_tabla = df_tabla.sort_index(key=lambda x: [a_minutos(h) for h in x])
    return df_tabla

# ========================================================
# INTERFAZ STREAMLIT
# ========================================================

def main():
    st.set_page_config(
        page_title="Generador de Horarios con Algoritmos Genéticos",
        page_icon="📅",
        layout="wide"
    )
    
    st.title("📅 Generador de Horarios Académicos")
    st.markdown("### Sistema de optimización con Algoritmos Genéticos")
    
    uploaded_file = st.file_uploader("📁 Cargar archivo Excel con datos de profesores y cursos", type=['xlsx','xls'])
    
    if uploaded_file:
        with open("temp.xlsx","wb") as f: f.write(uploaded_file.getbuffer())
        global config, bloques
        config = ConfiguracionSistema("temp.xlsx")
        bloques = generar_bloques()
        
        if config.profesores_config:
            mejor, score = buscar_mejor_horario(100)
            df_completo = exportar_horario(mejor)
            df_tabla = exportar_horario_tabla(mejor)
            
            # Pestañas
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📊 Horario Completo", 
                "👨‍🏫 Por Profesor", 
                "🏫 Por Salón", 
                "📈 Estadísticas",
                "📅 Tabla Semanal"
            ])
            
            with tab1:
                st.subheader("📊 Horario Completo")
                st.dataframe(df_completo, use_container_width=True)
            
            with tab2:
                st.subheader("👨‍🏫 Horario por Profesor")
                for profesor in config.profesores_config.keys():
                    with st.expander(f"Horario de {profesor}"):
                        df_prof = df_completo[df_completo['Profesor'] == profesor]
                        st.dataframe(df_prof, use_container_width=True)
            
            with tab3:
                st.subheader("🏫 Horario por Salón")
                for salon in config.salones:
                    with st.expander(f"Horario del {salon}"):
                        df_salon = df_completo[df_completo['Salon'] == salon]
                        st.dataframe(df_salon, use_container_width=True)
            
            with tab4:
                st.subheader("📈 Estadísticas")
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Distribución de créditos por profesor:**")
                    creditos_prof = df_completo.groupby('Profesor')['Créditos'].sum()
                    st.bar_chart(creditos_prof)
                with col2:
                    st.write("**Utilización de salones:**")
                    uso_salones = df_completo.groupby('Salon').size()
                    st.bar_chart(uso_salones)
            
            with tab5:
                st.subheader("📅 Horario Semanal")
                st.dataframe(df_tabla, use_container_width=True)
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                    df_tabla.to_excel(writer, index=True, sheet_name="Horario Semanal")
                    writer.save()
                    st.download_button(
                        "💾 Descargar horario (Excel)", 
                        data=output.getvalue(), 
                        file_name="horario_semanal.xlsx", 
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        else:
            st.error("❌ No se pudieron cargar los datos del Excel")
    else:
        st.info("📁 Por favor carga un archivo Excel para comenzar")

if __name__ == "__main__":
    main()
