import streamlit as st
import pandas as st_pd
import pandas as pd
import numpy as np
import random
import math
import time

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(page_title="Generador de Horarios UPRM - Algoritmos Genéticos", layout="wide")
st.title("Generador de Horarios de Clases (Timetabling) mediante Algoritmos Genéticos")
st.markdown("""
Basado en las restricciones de tesis de programación de cursos:
- **Restricciones Fuertes (Hard Constraints):** Sin cruces de salón, sin cruces de profesor, respetando capacidades y candidatos válidos.
- **Restricciones Suaves (Soft Constraints):** Preferencias de días y horas (implementación base).
""")

# ==========================================
# DEFINICIÓN DE ESPACIO DE TIEMPO (TIMESLOTS)
# ==========================================
# Simplificación de bloques de tiempo de la UPRM
DIAS = ["LWV", "MJ", "LMWJ"]
HORAS = ["07:30-08:20", "08:30-09:20", "09:30-10:20", "10:30-11:20", "11:30-12:20", 
         "12:30-13:20", "13:30-14:20", "14:30-15:20", "15:30-16:20"]
TIMESLOTS = [(d, h) for d in DIAS for h in HORAS]

# ==========================================
# CLASES DEL MODELO
# ==========================================
class HorarioGA:
    def __init__(self, df_cursos, df_profesores, df_salones, pop_size=50, mutation_rate=0.1):
        self.df_cursos = df_cursos
        self.df_profesores = df_profesores
        self.df_salones = df_salones
        
        self.pop_size = pop_size
        self.mutation_rate = mutation_rate
        
        # Procesar datos
        self.secciones = self._generar_secciones()
        self.salones = self.df_salones.to_dict('records')
        self.profesores = self.df_profesores.set_index('NOMBRE').to_dict('index')
        
    def _generar_secciones(self):
        """Calcula cuántas secciones se necesitan por curso basado en DEMANDA y CUPO"""
        secciones = []
        for _, row in self.df_cursos.iterrows():
            demanda = int(row['DEMANDA'])
            cupo = int(row['CUPO'])
            num_secciones = math.ceil(demanda / cupo) if cupo > 0 else 1
            candidatos = [c.strip() for c in str(row['CANDIDATOS']).split(',')] if pd.notna(row['CANDIDATOS']) else []
            
            for i in range(num_secciones):
                secciones.append({
                    'id_seccion': f"{row['CODIGO']}-{i+1}",
                    'codigo': row['CODIGO'],
                    'creditos': row['CREDITOS'],
                    'cupo': cupo,
                    'tipo_salon': row['TIPO_SALON'],
                    'candidatos': candidatos
                })
        return secciones

    def crear_individuo(self):
        """Crea un horario aleatorio inicial (Cromosoma)"""
        individuo = []
        for sec in self.secciones:
            # Seleccionar un profesor candidato válido al azar
            profs_validos = [p for p in sec['candidatos'] if p in self.profesores]
            profesor = random.choice(profs_validos) if profs_validos else "SIN_ASIGNAR"
            
            # Seleccionar salón que cumpla capacidad y tipo
            salones_validos = [s for s in self.salones if s['CAPACIDAD'] >= sec['cupo'] and str(s['TIPO']) == str(sec['tipo_salon'])]
            salon = random.choice(salones_validos)['CODIGO'] if salones_validos else random.choice(self.salones)['CODIGO']
            
            # Seleccionar timeslot
            timeslot = random.choice(TIMESLOTS)
            
            individuo.append({
                'seccion': sec,
                'profesor': profesor,
                'salon': salon,
                'timeslot': timeslot
            })
        return individuo

    def calcular_fitness(self, individuo):
        """Calcula la aptitud del horario. 0 es perfecto (100% factible). Penaliza violaciones."""
        penalizacion = 0
        
        # Diccionarios para rastrear cruces
        uso_profesores = {} # (profesor, timeslot) -> count
        uso_salones = {}    # (salon, timeslot) -> count
        carga_profesores = {} # profesor -> creditos totales
        
        for gen in individuo:
            prof = gen['profesor']
            salon = gen['salon']
            ts = gen['timeslot']
            creds = gen['seccion']['creditos']
            
            # 1. Restricción Fuerte: Cruce de Profesores
            if prof != "SIN_ASIGNAR":
                if (prof, ts) in uso_profesores:
                    penalizacion += 1000  # Penalización alta por doble reserva
                uso_profesores[(prof, ts)] = uso_profesores.get((prof, ts), 0) + 1
                
                # Sumar carga
                carga_profesores[prof] = carga_profesores.get(prof, 0) + creds
            else:
                penalizacion += 500 # Penalizar clases sin profesor
                
            # 2. Restricción Fuerte: Cruce de Salones
            if (salon, ts) in uso_salones:
                penalizacion += 1000
            uso_salones[(salon, ts)] = uso_salones.get((salon, ts), 0) + 1
            
        # 3. Restricción Fuerte: Cargas de Profesores (Min y Max)
        for prof, creditos in carga_profesores.items():
            if prof in self.profesores:
                carga_max = self.profesores[prof].get('CARGA_MAX', 12)
                if pd.notna(carga_max) and creditos > float(carga_max):
                    penalizacion += 100 * (creditos - float(carga_max)) # Penaliza exceso

        # Fitness es inverso a la penalización (1 / (1 + penalizacion))
        # Si penalización es 0, fitness es 1.0 (Horario 100% factible)
        return 1.0 / (1.0 + penalizacion), penalizacion

    def cruzar(self, padre1, padre2):
        """Cruce de un punto"""
        punto = random.randint(1, len(padre1) - 1)
        hijo1 = padre1[:punto] + padre2[punto:]
        hijo2 = padre2[:punto] + padre1[punto:]
        return hijo1, hijo2

    def mutar(self, individuo):
        """Muta un gen (asignación de clase) al azar"""
        for i in range(len(individuo)):
            if random.random() < self.mutation_rate:
                sec = individuo[i]['seccion']
                # Reasignar profesor
                profs_validos = [p for p in sec['candidatos'] if p in self.profesores]
                if profs_validos:
                    individuo[i]['profesor'] = random.choice(profs_validos)
                # Reasignar salon y timeslot
                salones_validos = [s for s in self.salones if s['CAPACIDAD'] >= sec['cupo'] and str(s['TIPO']) == str(sec['tipo_salon'])]
                if salones_validos:
                    individuo[i]['salon'] = random.choice(salones_validos)['CODIGO']
                individuo[i]['timeslot'] = random.choice(TIMESLOTS)
        return individuo

    def ejecutar(self, generaciones, st_placeholder):
        # Inicializar población
        poblacion = [self.crear_individuo() for _ in range(self.pop_size)]
        
        mejor_individuo = None
        mejor_fitness = -1
        mejor_penalizacion = float('inf')
        
        progress_bar = st.progress(0)
        
        for gen in range(generaciones):
            # Evaluar
            fitness_scores = []
            for ind in poblacion:
                fit, pen = self.calcular_fitness(ind)
                fitness_scores.append((ind, fit, pen))
                
                if fit > mejor_fitness:
                    mejor_fitness = fit
                    mejor_individuo = ind
                    mejor_penalizacion = pen
            
            # Mostrar progreso
            if gen % 10 == 0 or gen == generaciones - 1:
                st_placeholder.text(f"Generación {gen}/{generaciones} | Mejor Fitness: {mejor_fitness:.6f} | Penalizaciones: {mejor_penalizacion}")
            progress_bar.progress((gen + 1) / generaciones)
            
            # Si encontramos solución perfecta
            if mejor_penalizacion == 0:
                st_placeholder.success(f"¡Solución 100% factible encontrada en la generación {gen}!")
                break
                
            # Selección (Torneo) y Reproducción
            fitness_scores.sort(key=lambda x: x, reverse=True)
            nueva_poblacion = [x for x in fitness_scores[:int(self.pop_size * 0.1)]] # Elitismo (10%)
            
            while len(nueva_poblacion) < self.pop_size:
                # Torneo simple
                torneo = random.sample(fitness_scores, 3)
                padre1 = max(torneo, key=lambda x: x)
                torneo = random.sample(fitness_scores, 3)
                padre2 = max(torneo, key=lambda x: x)
                
                hijo1, hijo2 = self.cruzar(padre1, padre2)
                nueva_poblacion.extend([self.mutar(hijo1), self.mutar(hijo2)])
                
            poblacion = nueva_poblacion[:self.pop_size]
            
        return mejor_individuo, mejor_penalizacion

# ==========================================
# INTERFAZ DE STREAMLIT
# ==========================================
st.sidebar.header("Sube tus archivos CSV")
file_cursos = st.sidebar.file_uploader("Archivo de Cursos", type=['csv'])
file_profesores = st.sidebar.file_uploader("Archivo de Profesores", type=['csv'])
file_salones = st.sidebar.file_uploader("Archivo de Salones", type=['csv'])

st.sidebar.header("Parámetros del AG")
pop_size = st.sidebar.slider("Tamaño de Población", 20, 200, 50)
generaciones = st.sidebar.slider("Número de Generaciones", 50, 1000, 200)
mutation_rate = st.sidebar.slider("Tasa de Mutación", 0.01, 0.5, 0.1)

if file_cursos and file_profesores and file_salones:
    try:
        df_cursos = pd.read_csv(file_cursos)
        df_profesores = pd.read_csv(file_profesores)
        df_salones = pd.read_csv(file_salones)
        
        st.subheader("Vista previa de los datos")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("Cursos", df_cursos.head(3))
        with col2:
            st.write("Profesores", df_profesores.head(3))
        with col3:
            st.write("Salones", df_salones.head(3))
            
        if st.button("Generar Horario mediante Algoritmo Genético", type="primary"):
            st.write("Iniciando el proceso evolutivo...")
            status_text = st.empty()
            
            # Inicializar y ejecutar el AG
            ag = HorarioGA(df_cursos, df_profesores, df_salones, pop_size, mutation_rate)
            mejor_horario, penalizaciones = ag.ejecutar(generaciones, status_text)
            
            # Formatear la salida para visualización
            st.subheader("Mejor Horario Encontrado")
            
            if penalizaciones == 0:
                st.success("El horario es 100% Factible (Cero cruces, respeta capacidades y cargas).")
            else:
                st.warning(f"El horario tiene un puntaje de penalización de {penalizaciones}. Puede haber cruces o sobrecargas si no se iteró lo suficiente.")
            
            # Convertir a DataFrame
            resultado_list = []
            for gen in mejor_horario:
                resultado_list.append({
                    "Sección": gen['seccion']['id_seccion'],
                    "Curso": gen['seccion']['codigo'],
                    "Profesor": gen['profesor'],
                    "Días": gen['timeslot'],
                    "Horario": gen['timeslot'],
                    "Salón": gen['salon']
                })
                
            df_resultado = pd.DataFrame(resultado_list)
            st.dataframe(df_resultado, use_container_width=True)
            
            # Opción para descargar
            csv = df_resultado.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Descargar Horario en CSV",
                data=csv,
                file_name='horario_generado.csv',
                mime='text/csv',
            )
            
    except Exception as e:
        st.error(f"Error procesando los archivos: {e}")
else:
    st.info("Por favor, sube los tres archivos (Cursos, Profesores, Salones) en la barra lateral para comenzar.")
