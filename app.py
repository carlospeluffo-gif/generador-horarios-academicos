import streamlit as st
import pandas as pd
import random
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
        """Procesa los datos del Excel y crea la configuración de profesores"""
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
                    cursos_lista.append({"nombre": curso_nombre,"creditos": creditos,"estudiantes": estudiantes})
                    creditos_totales += creditos
            if cursos_lista:
                self.profesores_config[profesor] = {
                    "cursos": cursos_lista,
                    "creditos_totales": creditos_totales,
                    "horario_preferido": {},
                    "horario_no_disponible": {}
                }
        
        # Calcular número mínimo de salones
        cursos_por_bloque = []
        for prof_config in self.profesores_config.values():
            for curso in prof_config['cursos']:
                cursos_por_bloque.append(curso['creditos'])
        total_cursos = len(cursos_por_bloque)
        num_salones_minimos = max(1, total_cursos // 3)
        num_salones_minimos = min(num_salones_minimos, 10)
        self.salones = [f"Salon {i+1}" for i in range(num_salones_minimos)]
        st.write(f"🏫 Número mínimo de salones calculado: {num_salones_minimos}")

# ========================================================
# FUNCIONES AUXILIARES
# ========================================================

def generar_bloques():
    bloques = []
    id_counter = 1
    # Bloques ejemplo
    combinaciones_4dias = [["Lu","Ma","Mi","Ju"], ["Lu","Ma","Mi","Vi"], ["Lu","Ma","Ju","Vi"], ["Lu","Mi","Ju","Vi"], ["Ma","Mi","Ju","Vi"]]
    for dias in combinaciones_4dias:
        bloques.append({"id": id_counter, "dias": dias, "horas": [1]*len(dias), "creditos": 4})
        id_counter +=1
    combinaciones_2dias = [["Lu","Mi"], ["Lu","Vi"], ["Ma","Ju"], ["Mi","Vi"]]
    for dias in combinaciones_2dias:
        bloques.append({"id": id_counter, "dias": dias, "horas": [2]*len(dias), "creditos": 4})
        id_counter +=1
    return bloques

# Horario de ejemplo
horas_inicio = []
for h in range(7,20):
    for m in [0,30]:
        horas_inicio.append(f"{h:02d}:{m:02d}")

def a_minutos(hhmm):
    h, m = map(int, hhmm.split(":"))
    return h*60 + m

# Clase de asignación de clase
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
    
    def get_horario_detallado(self):
        horarios = []
        for dia, duracion in zip(self.bloque["dias"], self.bloque["horas"]):
            hora_fin_min = a_minutos(self.hora_inicio) + int(duracion*60)
            hora_fin = f"{hora_fin_min//60:02d}:{hora_fin_min%60:02d}"
            horarios.append({
                "Curso": self.curso_nombre,
                "Profesor": self.profesor,
                "Bloque": self.bloque["id"],
                "Dia": dia,
                "Hora Inicio": self.hora_inicio,
                "Hora Fin": hora_fin,
                "Duración": duracion,
                "Créditos": self.creditos,
                "Estudiantes": self.estudiantes,
                "Salon": self.salon
            })
        return horarios

def generar_horario_valido():
    asignaciones = []
    for profesor, prof_config in config.profesores_config.items():
        for curso_info in prof_config["cursos"]:
            bloque = random.choice(bloques)
            hora_inicio = random.choice(horas_inicio)
            salon = random.choice(config.salones)
            asignaciones.append(AsignacionClase(curso_info, profesor, bloque, hora_inicio, salon))
    return asignaciones

def exportar_horario(asignaciones):
    registros = []
    for asig in asignaciones:
        registros.extend(asig.get_horario_detallado())
    df = pd.DataFrame(registros)
    return df

# ========================================================
# INTERFAZ STREAMLIT
# ========================================================

def main():
    st.set_page_config(page_title="Generador de Horarios", page_icon="📅", layout="wide")
    
    # ======== PANTALLA DE BIENVENIDA ========
    st.markdown(
        "<div style='text-align: center; margin-top:50px;'>"
        "<h1 style='color: #2E86C1; font-size: 60px; font-weight:bold;'>GENERACIÓN DE HORARIOS ACADÉMICOS</h1>"
        "<h3 style='color: #5D6D7E; font-size:28px;'>CON ALGORITMOS GENÉTICOS</h3>"
        "</div>",
        unsafe_allow_html=True
    )
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    usuario = st.text_input("Ingrese la sigla de su departamento (ej: MATE, QUIM, FIS)", max_chars=10)
    
    programas = ["Ingeniería Matemática", "Licenciatura en Física", "Química Industrial", "Biología", "Ingeniería Química", "Matemática Aplicada"]
    st.markdown("### Seleccione su programa académico:")
    programa_seleccionado = st.selectbox("Programa", ["--Seleccione--"] + programas)
    
    if st.button("➡️ Siguiente"):
        if not usuario:
            st.warning("⚠️ Ingresa la sigla de tu departamento antes de continuar.")
        elif programa_seleccionado == "--Seleccione--":
            st.warning("⚠️ Selecciona un programa antes de continuar.")
        else:
            st.success(f"✅ Departamento: **{usuario}** | Programa: **{programa_seleccionado}**")
            
            # ======== SECCIÓN DE CARGA DE EXCEL ========
            uploaded_file = st.file_uploader(
                "📁 Cargar archivo Excel con datos de profesores y cursos",
                type=['xlsx','xls'],
                help="El archivo debe contener columnas como: Profesor, Curso/Materia, Créditos, Estudiantes"
            )
            
            if uploaded_file is not None:
                global config, bloques
                config = ConfiguracionSistema(uploaded_file)
                bloques = generar_bloques()
                st.success("✅ Archivo cargado y procesado correctamente.")
                
                if st.button("🎯 Generar horario"):
                    asignaciones = generar_horario_valido()
                    df_horario = exportar_horario(asignaciones)
                    st.dataframe(df_horario)
                    
                    # Botón para exportar
                    excel_buffer = io.BytesIO()
                    df_horario.to_excel(excel_buffer, index=False)
                    st.download_button(
                        label="💾 Descargar Horario en Excel",
                        data=excel_buffer,
                        file_name=f"horario_{programa_seleccionado}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            else:
                st.error("❌ No se pudieron cargar los datos del archivo Excel")

if __name__ == "__main__":
    main()


