import streamlit as st
import pandas as pd
import numpy as np
import random
import copy
import io
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ==============================================================================
# 1. ESTÉTICA PLATINUM
# ==============================================================================
st.set_page_config(page_title="UPRM Scheduler Platinum AI", page_icon="🏛️", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #000000; background-image: linear-gradient(rgba(15, 15, 15, 0.50), rgba(15, 15, 15, 0.50)), url("https://www.transparenttextures.com/patterns/cubes.png"); color: #ffffff; }
    p, label, .stMarkdown, .stDataFrame, div[data-testid="stMarkdownContainer"] p { color: #e0e0e0 !important; font-family: 'Segoe UI', sans-serif; }
    h1, h2, h3, h4 { color: #FFD700 !important; text-shadow: 0px 0px 15px rgba(255, 215, 0, 0.4); }
    [data-testid="stSidebar"] { background-color: #080808; border-right: 1px solid #333; }
    .stButton>button { background: linear-gradient(90deg, #B8860B, #FFD700); color: #000 !important; font-weight: 800; border: none; padding: 0.6rem 1.2rem; border-radius: 6px; transition: transform 0.2s; }
    .stButton>button:hover { transform: scale(1.05); box-shadow: 0 0 20px rgba(255, 215, 0, 0.5); }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. FUNCIONES DE APOYO
# ==============================================================================
def mins_to_str(minutes):
    h, m = divmod(int(minutes), 60)
    am_pm = "AM" if h < 12 else "PM"
    h_disp = h if h <= 12 else h - 12
    if h_disp == 0: h_disp = 12
    return f"{h_disp:02d}:{m:02d} {am_pm}"

def crear_excel_guia():
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        pd.DataFrame(columns=['CODIGO', 'NOMBRE', 'CREDITOS', 'CANTIDAD_SECCIONES', 'CUPO', 'CANDIDATOS', 'TIPO_SALON']).to_excel(writer, sheet_name='Cursos', index=False)
        pd.DataFrame(columns=['Nombre', 'Carga_Min', 'Carga_Max']).to_excel(writer, sheet_name='Profesores', index=False)
        pd.DataFrame(columns=['CODIGO', 'CAPACIDAD', 'TIPO']).to_excel(writer, sheet_name='Salones', index=False)
    return output.getvalue()

# ==============================================================================
# 3. MOTOR DE ALGORITMO GENÉTICO
# ==============================================================================

class Seccion:
    def __init__(self, uid, cod_base, nombre, creditos, cupo, candidatos, tipo_salon):
        self.uid = uid
        self.cod_base = str(cod_base).upper()
        self.nombre = nombre
        self.creditos = int(creditos)
        self.cupo = int(cupo)
        self.tipo_salon = str(tipo_salon).upper()
        self.cands = [c.strip().upper() for c in str(candidatos).split(',') if c.strip()] if not pd.isna(candidatos) else []

class GeneticEngine:
    def __init__(self, secciones, profesores, salones, zona, pop_size=20, generations=50):
        self.secciones = secciones
        self.profesores = profesores
        self.salones = salones
        self.zona = zona
        self.pop_size = pop_size
        self.generations = generations
        self.h_univ = (630, 750) if zona == "CENTRAL" else (600, 720)
        
        # Bloques de tiempo posibles
        base = 30 if zona == "CENTRAL" else 0
        self.bloques_lmv = [h*60 + base for h in range(7, 20)]
        self.bloques_mj = [h*60 + base for h in range(7, 20)]

    def generar_individuo_aleatorio(self):
        individuo = []
        for sec in self.secciones:
            prof = random.choice(sec.cands) if sec.cands else "TBA"
            salon = random.choice(self.salones)['CODIGO']
            es_mj = (sec.creditos == 4 or random.random() > 0.6)
            inicio = random.choice(self.bloques_mj if es_mj else self.bloques_lmv)
            duracion = 80 if es_mj else 50
            dias = "MaJu" if es_mj else "LuMiVi"
            
            individuo.append({
                'sec': sec, 'prof': prof, 'salon': salon, 
                'inicio': inicio, 'fin': inicio + duracion, 'dias': dias
            })
        return individuo

    def calcular_fitness(self, individuo):
        penalizaciones = 0
        oc_profe = {} # (profe, dia, bloque)
        oc_salon = {} # (salon, dia, bloque)
        cargas = {p['Nombre']: 0 for p in self.profesores}

        for gene in individuo:
            # 1. Penalizar Hora Universal
            if gene['dias'] == "MaJu":
                if max(gene['inicio'], self.h_univ[0]) < min(gene['fin'], self.h_univ[1]):
                    penalizaciones += 100

            # 2. Choques de Profesor y Salón
            dias_lista = ["Lu", "Mi", "Vi"] if gene['dias'] == "LuMiVi" else ["Ma", "Ju"]
            for d in dias_lista:
                # Slot de tiempo (simplificado a bloques de 10 min para precisión)
                for t in range(gene['inicio'], gene['fin'], 10):
                    # Check Profe
                    p_key = (gene['prof'], d, t)
                    if p_key in oc_profe and gene['prof'] != "TBA": penalizaciones += 150
                    oc_profe[p_key] = True
                    
                    # Check Salon
                    s_key = (gene['salon'], d, t)
                    if s_key in oc_salon: penalizaciones += 150
                    oc_salon[s_key] = True
            
            if gene['prof'] in cargas:
                cargas[gene['prof']] += gene['sec'].creditos

        # 3. Penalizar carga excesiva o insuficiente
        for p in self.profesores:
            c = cargas[p['Nombre']]
            if c > p['Carga_Max']: penalizaciones += 200
            if 0 < c < p['Carga_Min']: penalizaciones += 50

        return 1 / (1 + penalizaciones)

    def crossover(self, padre1, padre2):
        punto = random.randint(0, len(padre1)-1)
        hijo = padre1[:punto] + padre2[punto:]
        return hijo

    def mutar(self, individuo):
        if random.random() < 0.2:
            idx = random.randint(0, len(individuo)-1)
            # Mutar solo tiempo y salón
            es_mj = individuo[idx]['dias'] == "MaJu"
            individuo[idx]['inicio'] = random.choice(self.bloques_mj if es_mj else self.bloques_lmv)
            individuo[idx]['fin'] = individuo[idx]['inicio'] + (80 if es_mj else 50)
            individuo[idx]['salon'] = random.choice(self.salones)['CODIGO']

    def evolucionar(self):
        poblacion = [self.generar_individuo_aleatorio() for _ in range(self.pop_size)]
        
        progress_bar = st.progress(0)
        for gen in range(self.generations):
            poblacion.sort(key=lambda x: self.calcular_fitness(x), reverse=True)
            
            nueva_gen = poblacion[:2] # Elitismo: pasan los 2 mejores
            
            while len(nueva_gen) < self.pop_size:
                p1, p2 = random.sample(poblacion[:10], 2) # Selección de padres
                hijo = self.crossover(p1, p2)
                self.mutar(hijo)
                nueva_gen.append(hijo)
            
            poblacion = nueva_gen
            progress_bar.progress((gen + 1) / self.generations)
            
        mejor = poblacion[0]
        return mejor

# ==============================================================================
# 4. INTERFAZ PRINCIPAL
# ==============================================================================
def main():
    st.title("🏛️ UPRM Scheduler Platinum AI")
    
    excel_guia = crear_excel_guia()
    st.download_button("📥 Plantilla de Excel", excel_guia, "plantilla_uprm.xlsx")
    
    with st.sidebar:
        st.header("🧬 Parámetros Genéticos")
        zona = st.selectbox("📍 Zona", ["CENTRAL", "PERIFERICA"])
        pop = st.slider("Población", 10, 100, 30)
        gens = st.slider("Generaciones", 10, 200, 50)
        file = st.file_uploader("📂 Subir Datos", type=['xlsx'])

    if file:
        xls = pd.ExcelFile(file)
        df_cur = pd.read_excel(xls, 'Cursos')
        df_pro = pd.read_excel(xls, 'Profesores')
        df_sal = pd.read_excel(xls, 'Salones')

        if st.button("🚀 INICIAR EVOLUCIÓN DE HORARIO"):
            secciones = []
            for _, r in df_cur.iterrows():
                for i in range(int(r.get('CANTIDAD_SECCIONES', 1))):
                    secciones.append(Seccion(f"{r['CODIGO']}-{i+1:02d}", r['CODIGO'], r['NOMBRE'], r['CREDITOS'], r['CUPO'], r['CANDIDATOS'], r['TIPO_SALON']))
            
            profesores = df_pro.to_dict('records')
            salones = df_sal.to_dict('records')
            
            engine = GeneticEngine(secciones, profesores, salones, zona, pop, gens)
            mejor_horario = engine.evolucionar()
            
            # Convertir a DataFrame para visualización
            res_data = []
            cargas_finales = {p['Nombre']: 0 for p in profesores}
            for g in mejor_horario:
                res_data.append({
                    'Curso': g['sec'].uid, 'Nombre': g['sec'].nombre,
                    'Profesor': g['prof'], 'Días': g['dias'],
                    'Inicio': g['inicio'], 'Fin': g['fin'], 'Salón': g['salon']
                })
                if g['prof'] in cargas_finales:
                    cargas_finales[g['prof']] += g['sec'].creditos
            
            st.session_state.horario = pd.DataFrame(res_data)
            st.session_state.cargas = cargas_finales
            st.session_state.profes_raw = profesores

        if 'horario' in st.session_state:
            tab1, tab2 = st.tabs(["📅 VISTA MAESTRA", "👨‍🏫 ANÁLISIS POR PROFESOR"])
            
            with tab1:
                df_disp = st.session_state.horario.copy()
                df_disp['Hora'] = df_disp['Inicio'].apply(mins_to_str) + " - " + df_disp['Fin'].apply(mins_to_str)
                st.dataframe(df_disp[['Curso', 'Nombre', 'Profesor', 'Días', 'Hora', 'Salón']], use_container_width=True)

            with tab2:
                p_sel = st.selectbox("Profesor:", st.session_state.horario['Profesor'].unique())
                df_p = st.session_state.horario[st.session_state.horario['Profesor'] == p_sel]
                
                # Gráfico Gantt
                plot_data = []
                dia_map = {'Lu': '2024-01-01', 'Mi': '2024-01-03', 'Vi': '2024-01-05', 'Ma': '2024-01-02', 'Ju': '2024-01-04'}
                for _, row in df_p.iterrows():
                    dias_split = ["Lu", "Mi", "Vi"] if row['Días'] == "LuMiVi" else ["Ma", "Ju"]
                    for d in dias_split:
                        plot_data.append({
                            'Curso': row['Curso'], 'Día': d,
                            'Start': f"{dia_map[d]} {int(row['Inicio']//60):02d}:{int(row['Inicio']%60):02d}:00",
                            'Finish': f"{dia_map[d]} {int(row['Fin']//60):02d}:{int(row['Fin']%60):02d}:00"
                        })
                
                if plot_data:
                    fig = px.timeline(pd.DataFrame(plot_data), x_start="Start", x_end="Finish", y="Día", color="Curso", template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)

                # Gauge de Carga
                target_p = next(p for p in st.session_state.profes_raw if p['Nombre'] == p_sel)
                fig_g = go.Figure(go.Indicator(
                    mode = "gauge+number", value = st.session_state.cargas[p_sel],
                    gauge = {'axis': {'range': [0, 21]}, 'bar': {'color': "#FFD700"},
                             'steps': [{'range': [0, target_p['Carga_Min']], 'color': "#550000"},
                                       {'range': [target_p['Carga_Min'], target_p['Carga_Max']], 'color': "#005500"}]}))
                fig_g.update_layout(height=250, paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
                st.plotly_chart(fig_g, use_container_width=True)

if __name__ == "__main__":
    main()
