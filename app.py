import streamlit as st
import pandas as pd
import random
import numpy as np
from datetime import datetime, timedelta
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
        
        self.restricciones_globales = {
            "horarios_prohibidos": {"Ma": [("10:30", "12:30")], "Ju": [("10:30", "12:30")]},
            "hora_inicio_min": "07:30",
            "hora_fin_max": "19:30",
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
    
    def cargar_desde_excel(self):
        try:
            excel_data = pd.read_excel(self.archivo_excel, sheet_name=None)
            hoja_cursos = None
            for nombre_hoja, df in excel_data.items():
                columnas_df = [col.lower().strip() for col in df.columns]
                if any('profesor' in col or 'docente' in col for col in columnas_df) and any('curso' in col or 'materia' in col or 'asignatura' in col for col in columnas_df):
                    hoja_cursos = df
                    break
            if hoja_cursos is None:
                st.error("❌ No se encontró hoja con datos válidos")
                return
            self.cursos_df = hoja_cursos
            self.procesar_datos_excel()
        except Exception as e:
            st.error(f"❌ Error al cargar Excel: {e}")

    def procesar_datos_excel(self):
        if self.cursos_df is None:
            return
        df = self.cursos_df.copy()
        df.columns = [col.lower().strip().replace(' ', '_') for col in df.columns]
        mapeo_columnas = {
            'profesor': ['profesor', 'docente'],
            'curso': ['curso', 'materia', 'asignatura'],
            'creditos': ['creditos', 'créditos', 'horas'],
            'estudiantes': ['estudiantes', 'alumnos', 'students', 'seccion']
        }
        columnas_finales = {}
        for campo, posibles in mapeo_columnas.items():
            for col in df.columns:
                if any(pos in col for pos in posibles):
                    columnas_finales[campo] = col
                    break
        if 'creditos' not in columnas_finales:
            df['creditos_default'] = 3
            columnas_finales['creditos'] = 'creditos_default'
        if 'estudiantes' not in columnas_finales:
            df['estudiantes_default'] = 30
            columnas_finales['estudiantes'] = 'estudiantes_default'
        df = df.dropna(subset=[columnas_finales['profesor'], columnas_finales['curso']])
        profesores_unicos = df[columnas_finales['profesor']].unique()
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
        total_cursos = sum(len(config['cursos']) for config in self.profesores_config.values())
        num_salones = max(3, min(10, total_cursos // 3))
        self.salones = [f"Salon {i+1}" for i in range(num_salones)]

# ========================================================
# GENERACIÓN DE BLOQUES Y HORARIOS
# ========================================================

def generar_bloques():
    bloques = []
    id_counter = 1
    combinaciones_4dias = [["Lu","Ma","Mi","Ju"],["Lu","Ma","Mi","Vi"],["Lu","Ma","Ju","Vi"],["Lu","Mi","Ju","Vi"],["Ma","Mi","Ju","Vi"]]
    for dias in combinaciones_4dias:
        bloques.append({"id": id_counter, "dias": dias, "horas": [1]*len(dias), "creditos": 4})
        id_counter += 1
    combinaciones_2dias = [["Lu","Mi"],["Lu","Vi"],["Ma","Ju"],["Mi","Vi"]]
    for dias in combinaciones_2dias:
        bloques.append({"id": id_counter, "dias": dias, "horas": [2]*len(dias), "creditos": 4})
        id_counter += 1
    bloques.append({"id": id_counter, "dias": ["Lu","Mi","Vi"], "horas": [1,1,1], "creditos": 3}); id_counter+=1
    bloques.append({"id": id_counter, "dias": ["Ma","Ju"], "horas": [1.5,1.5], "creditos": 3}); id_counter+=1
    return bloques

horas_inicio = []
for h in range(7, 20):
    for m in [0, 30]:
        horas_inicio.append(f"{h:02d}:{m:02d}")

def a_minutos(hhmm):
    h, m = map(int, hhmm.split(":"))
    return h*60+m

class AsignacionClase:
    def __init__(self, curso_info, profesor, bloque, hora_inicio, salon):
        self.curso_nombre = curso_info["nombre"]
        self.profesor = profesor
        self.bloque = bloque
        self.hora_inicio = hora_inicio
        self.estudiantes = curso_info["estudiantes"]
        self.salon = salon
        self.creditos = curso_info["creditos"]

def generar_horario_valido():
    asignaciones = []
    for profesor, prof_config in config.profesores_config.items():
        for curso_info in prof_config['cursos']:
            bloque = random.choice(bloques)
            hora_inicio = random.choice(horas_inicio)
            salon = random.choice(config.salones)
            asignaciones.append(AsignacionClase(curso_info, profesor, bloque, hora_inicio, salon))
    return asignaciones

# ========================================================
# EXPORTAR HORARIO A DATAFRAME DETALLADO
# ========================================================

def exportar_horario_dataframe(asignaciones):
    datos = []
    for a in asignaciones:
        for dia in a.bloque["dias"]:
            datos.append({
                "Profesor": a.profesor,
                "Curso": a.curso_nombre,
                "Salon": a.salon,
                "Día": dia,
                "Hora Inicio": a.hora_inicio,
                "Créditos": a.creditos,
                "Estudiantes": a.estudiantes
            })
    df = pd.DataFrame(datos)
    return df

# ========================================================
# STREAMLIT
# ========================================================

def main():
    st.set_page_config(page_title="Generador de Horarios", page_icon="📅", layout="wide")
    st.title("📅 Generador de Horarios Académicos")
    
    uploaded_file = st.file_uploader("📁 Cargar archivo Excel", type=['xlsx','xls'])
    if uploaded_file:
        with open("temp.xlsx","wb") as f: f.write(uploaded_file.getbuffer())
        global config, bloques
        config = ConfiguracionSistema("temp.xlsx")
        bloques = generar_bloques()
        
        if config.profesores_config:
            mejor = generar_horario_valido()
            df_horario = exportar_horario_dataframe(mejor)
            
            # ===========================
            # Mostrar horario en pestañas
            # ===========================
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Horario Completo", "👨‍🏫 Por Profesor", "🏫 Por Salón", "📈 Estadísticas"])
            
            with tab1:
                st.subheader("📊 Horario Completo")
                st.dataframe(df_horario, use_container_width=True)
                
                csv = df_horario.to_csv(index=False)
                st.download_button(
                    label="💾 Descargar horario (CSV)",
                    data=csv,
                    file_name="horario_generado.csv",
                    mime="text/csv"
                )
                
                # Exportar Excel
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                    df_horario.to_excel(writer, index=False, sheet_name="Horario Completo")
                    writer.save()
                    st.download_button("💾 Descargar horario (Excel)", data=output.getvalue(), file_name="horario_completo.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            
            with tab2:
                st.subheader("👨‍🏫 Horario por Profesor")
                for profesor in config.profesores_config.keys():
                    with st.expander(f"Horario de {profesor}"):
                        df_prof = df_horario[df_horario['Profesor'] == profesor]
                        if not df_prof.empty:
                            st.dataframe(df_prof, use_container_width=True)
                        else:
                            st.warning(f"No se encontraron clases para {profesor}")
            
            with tab3:
                st.subheader("🏫 Horario por Salón")
                for salon in config.salones:
                    with st.expander(f"Horario del {salon}"):
                        df_salon = df_horario[df_horario['Salon'] == salon]
                        if not df_salon.empty:
                            st.dataframe(df_salon, use_container_width=True)
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
        else:
            st.error("❌ No se pudieron cargar los datos del Excel")
    else:
        st.info("📁 Por favor carga un archivo Excel para comenzar")

if __name__ == "__main__":
    main()
