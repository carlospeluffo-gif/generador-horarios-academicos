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
        
        if 'profesor' not in columnas_finales or 'curso' not in columnas_finales:
            st.error("❌ Error: No se encontraron las columnas básicas (profesor, curso)")
            return
        
        if 'creditos' not in columnas_finales:
            df['creditos_default'] = 3
            columnas_finales['creditos'] = 'creditos_default'
        
        if 'estudiantes' not in columnas_finales:
            df['estudiantes_default'] = 30
            columnas_finales['estudiantes'] = 'estudiantes_default'
        
        df = df.dropna(subset=[columnas_finales['profesor'], columnas_finales['curso']])
        profesores_unicos = df[columnas_finales['profesor']].unique()
        
        for profesor in profesores_unicos:
            profesor = str(profesor).strip()
            cursos_profesor = df[df[columnas_finales['profesor']] == profesor]
            cursos_lista = []
            creditos_totales = 0
            
            for _, fila in cursos_profesor.iterrows():
                curso_nombre = str(fila[columnas_finales['curso']]).strip()
                creditos = int(float(fila[columnas_finales['creditos']])) if not pd.isna(fila[columnas_finales['creditos']]) else 3
                estudiantes = int(float(fila[columnas_finales['estudiantes']])) if not pd.isna(fila[columnas_finales['estudiantes']]) else 30
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
# BLOQUES Y HORARIOS (igual que tu código)
# ========================================================
# ... (todo lo que ya tienes de generar_bloques, horas_inicio, a_minutos, etc.)
# Mantengo tu lógica intacta hasta la función evaluar_horario()

# ========================================================
# ALGORITMO GENÉTICO
# ========================================================

def algoritmo_genetico(iteraciones=200, tam_poblacion=30, prob_cruce=0.8, prob_mutacion=0.2):
    """Optimiza el horario usando selección, cruce y mutación"""
    poblacion = [generar_horario_valido() for _ in range(tam_poblacion)]
    poblacion = [p for p in poblacion if p is not None]
    if not poblacion:
        return None, -float("inf")
    
    for i in range(iteraciones):
        # Evaluar
        puntuaciones = [evaluar_horario(ind) for ind in poblacion]
        # Selección por torneo
        seleccionados = []
        for _ in range(len(poblacion)):
            a, b = random.sample(range(len(poblacion)), 2)
            seleccionados.append(poblacion[a] if puntuaciones[a] > puntuaciones[b] else poblacion[b])
        # Cruce
        nueva_poblacion = []
        for i in range(0, len(seleccionados), 2):
            p1 = seleccionados[i]
            p2 = seleccionados[i+1] if i+1 < len(seleccionados) else seleccionados[0]
            if random.random() < prob_cruce:
                punto = random.randint(1, len(p1)-1)
                hijo1 = p1[:punto] + p2[punto:]
                hijo2 = p2[:punto] + p1[punto:]
                nueva_poblacion.extend([hijo1, hijo2])
            else:
                nueva_poblacion.extend([p1, p2])
        # Mutación
        for ind in nueva_poblacion:
            if random.random() < prob_mutacion:
                if ind:
                    idx = random.randint(0, len(ind)-1)
                    ind[idx] = generar_horario_valido()[0]  # re-asigna una clase aleatoria
        poblacion = nueva_poblacion
    
    mejor_idx = np.argmax([evaluar_horario(ind) for ind in poblacion])
    return poblacion[mejor_idx], evaluar_horario(poblacion[mejor_idx])

# ========================================================
# INTERFAZ STREAMLIT (pequeño upgrade visual)
# ========================================================

def main():
    st.set_page_config(page_title="Generador de Horarios", page_icon="📅", layout="wide")
    st.title("📅 Generador de Horarios Académicos")
    st.markdown("> **Optimización con Algoritmos Genéticos** – Carga tu Excel y genera el mejor horario posible ✅")
    st.sidebar.header("⚙️ Configuración")
    
    uploaded_file = st.sidebar.file_uploader("📁 Cargar archivo Excel", type=['xlsx', 'xls'])
    
    if uploaded_file:
        with open("temp_excel.xlsx", "wb") as f:
            f.write(uploaded_file.getbuffer())
        global config, bloques
        config = ConfiguracionSistema("temp_excel.xlsx")
        bloques = generar_bloques()
        
        if config.profesores_config:
            st.success("✅ Archivo cargado correctamente")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("👨‍🏫 Profesores", len(config.profesores_config))
            with col2:
                st.metric("📚 Cursos", sum(len(p['cursos']) for p in config.profesores_config.values()))
            with col3:
                st.metric("🏫 Salones", len(config.salones))
            
            intentos = st.sidebar.slider("Iteraciones del GA", 50, 500, 200, 50)
            if st.button("🚀 Generar Horario"):
                mejor, score = algoritmo_genetico(iteraciones=intentos)
                if mejor:
                    df = exportar_horario(mejor)
                    st.dataframe(df)
                    st.success(f"🎯 Mejor puntuación: {score}")
                else:
                    st.error("No se pudo generar un horario válido.")
    else:
        st.info("📂 Sube un archivo Excel para comenzar.")

if __name__ == "__main__":
    main()
