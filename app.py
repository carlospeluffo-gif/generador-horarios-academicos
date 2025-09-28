import streamlit as st
import pandas as pd
import random
import json
import numpy as np
from datetime import datetime, timedelta
import copy
import io

# ========================================================
# CONTROL DE PANTALLAS
# ========================================================
if "step" not in st.session_state:
    st.session_state.step = 1

def siguiente_pantalla():
    st.session_state.step += 1

def volver_inicio():
    st.session_state.step = 1

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
        if self.cursos_df is None:
            return
        
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
                except:
                    creditos = 3
                try:
                    estudiantes = int(float(fila[columnas_finales['estudiantes']]))
                except:
                    estudiantes = 30
                if curso_nombre and curso_nombre != 'nan':
                    cursos_lista.append({"nombre": curso_nombre, "creditos": creditos, "estudiantes": estudiantes})
                    creditos_totales += creditos
            if cursos_lista:
                self.profesores_config[profesor] = {
                    "cursos": cursos_lista,
                    "creditos_totales": creditos_totales,
                    "horario_preferido": {},
                    "horario_no_disponible": {}
                }
                
                # Calcular número mínimo de salones necesarios
                cursos_por_bloque = []
                for prof_config in self.profesores_config.values():
                    for curso in prof_config['cursos']:
                        cursos_por_bloque.append(curso['creditos'])
                total_cursos = len(cursos_por_bloque)
                num_salones_minimos = max(1, total_cursos // 3)
                num_salones_minimos = min(num_salones_minimos, 10)
                self.salones = [f"Salon {i+1}" for i in range(num_salones_minimos)]
        st.success(f"✅ Configuración completada: {len(self.profesores_config)} profesores, {len(self.salones)} salones")

# ========================================================
# Generación de bloques
# ========================================================
def generar_bloques():
    bloques = []
    id_counter = 1
    combinaciones_4dias = [["Lu","Ma","Mi","Ju"],["Lu","Ma","Mi","Vi"],["Lu","Ma","Ju","Vi"],["Lu","Mi","Ju","Vi"],["Ma","Mi","Ju","Vi"]]
    for dias in combinaciones_4dias:
        bloques.append({"id": id_counter, "dias": dias, "horas": [1]*4, "creditos": 4})
        id_counter += 1
    combinaciones_2dias=[["Lu","Mi"],["Lu","Vi"],["Ma","Ju"],["Mi","Vi"]]
    for dias in combinaciones_2dias:
        bloques.append({"id": id_counter, "dias": dias, "horas": [2,2], "creditos": 4})
        id_counter += 1
    bloques.append({"id": id_counter, "dias": ["Lu","Mi","Vi"], "horas": [1,1,1], "creditos": 3}); id_counter+=1
    bloques.append({"id": id_counter, "dias": ["Ma","Ju"], "horas": [1.5,1.5], "creditos": 3}); id_counter+=1
    return bloques

# ========================================================
# Función principal de la app con navegación por pasos
# ========================================================
def main():
    st.set_page_config(page_title="Generador de Horarios", layout="wide")
    
    if st.session_state.step==1:
        # Pantalla de bienvenida y selección
        st.markdown("<h1 style='color:#2E86C1;'>GENERACIÓN DE HORARIOS ACADÉMICOS</h1>", unsafe_allow_html=True)
        if "usuario" not in st.session_state:
            st.session_state.usuario=""
        st.session_state.usuario = st.text_input("Ingrese sigla de su departamento", value=st.session_state.usuario)
        
        programas=["Ingeniería Matemática","Licenciatura en Física","Química Industrial","Biología","Ingeniería Química","Matemática Aplicada"]
        if "programa" not in st.session_state:
            st.session_state.programa=""
        st.session_state.programa = st.selectbox("Seleccione su programa", ["--Seleccione--"]+programas)
        
        if st.button("➡️ Siguiente"):
            if not st.session_state.usuario or st.session_state.programa=="--Seleccione--":
                st.warning("Completa todos los datos antes de continuar.")
            else:
                siguiente_pantalla()
    
    elif st.session_state.step==2:
        # Pantalla de carga de Excel
        st.markdown(f"## Departamento: **{st.session_state.usuario}** | Programa: **{st.session_state.programa}**")
        uploaded_file = st.file_uploader("📁 Cargar archivo Excel", type=['xlsx','xls'])
        if uploaded_file is not None:
            st.session_state.config = ConfiguracionSistema(uploaded_file)
            st.session_state.bloques = generar_bloques()
            st.success("✅ Archivo cargado correctamente")
            if st.button("🎯 Generar horario"):
                siguiente_pantalla()
        if st.button("🔙 Volver"):
            volver_inicio()
    
    elif st.session_state.step==3:
        # Pantalla de generación de horario
        st.markdown("## 🗓️ Horario generado")
        if hasattr(st.session_state, 'config') and st.session_state.config:
            config = st.session_state.config
            df_horario=pd.DataFrame()
            for prof, data in config.profesores_config.items():
                for c in data["cursos"]:
                    df_horario=df_horario.append({
                        "Profesor":prof,
                        "Curso":c["nombre"],
                        "Créditos":c["creditos"],
                        "Estudiantes":c["estudiantes"]
                    }, ignore_index=True)
            
            # Mostrar en pestañas
            tab1, tab2, tab3 = st.tabs(["📊 Horario Completo", "👨‍🏫 Por Profesor", "🏫 Por Salón"])
            with tab1:
                st.dataframe(df_horario)
            with tab2:
                for prof in config.profesores_config.keys():
                    st.subheader(prof)
                    st.dataframe(df_horario[df_horario['Profesor']==prof])
            with tab3:
                for salon in config.salones:
                    st.subheader(salon)
                    st.dataframe(df_horario.sample(frac=1).reset_index(drop=True)) # Aquí puedes adaptar según asignación real a salones
            
            csv=df_horario.to_csv(index=False)
            st.download_button("💾 Descargar CSV", csv, file_name="horario.csv")
        
        if st.button("🔙 Volver al inicio"):
            volver_inicio()

if __name__ == "__main__":
    main()
