import streamlit as st
import pandas as pd
import numpy as np
import random
import io
import copy
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ==============================================================================
# 1. ESTÉTICA PLATINUM
# ==============================================================================
st.set_page_config(page_title="UPRM Academic Planner AI", page_icon="🏛️", layout="wide")

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
# 2. UTILIDADES DE TIEMPO Y EXCEL
# ==============================================================================
def mins_to_str(minutes):
    h, m = divmod(int(minutes), 60)
    am_pm = "AM" if h < 12 else "PM"
    h_disp = h if h <= 12 else h - 12
    if h_disp == 0: h_disp = 12
    return f"{h_disp:02d}:{m:02d} {am_pm}"

def str_to_mins(time_str):
    try:
        t = pd.to_datetime(time_str.strip(), format='%I:%M %p')
        return t.hour * 60 + t.minute
    except: return None

def crear_excel_guia():
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Pestaña Cursos con nueva lógica de demanda
        pd.DataFrame(columns=[
            'CODIGO', 'NOMBRE', 'CREDITOS', 'DEMANDA_TOTAL', 
            'CANT_SECC_GRANDES', 'CUPO_GRANDE', 'CUPO_NORMAL', 
            'CANDIDATOS', 'TIPO_SALON'
        ]).to_excel(writer, sheet_name='Cursos', index=False)
        
        pd.DataFrame(columns=['Nombre', 'Carga_Min', 'Carga_Max', 'DISPONIBILIDAD']).to_excel(writer, sheet_name='Profesores', index=False)
        pd.DataFrame(columns=['CODIGO', 'CAPACIDAD', 'TIPO']).to_excel(writer, sheet_name='Salones', index=False)
    return output.getvalue()

# ==============================================================================
# 3. CLASES DE DATOS
# ==============================================================================
class Seccion:
    def __init__(self, uid, cod_base, nombre, creditos, cupo, candidatos, tipo_salon):
        self.uid = uid
        self.cod_base = cod_base
        self.nombre = nombre
        self.creditos = creditos
        self.cupo = cupo
        self.tipo_salon = tipo_salon
        self.cands = candidatos

# ==============================================================================
# 4. MOTOR GENÉTICO AVANZADO
# ==============================================================================
class UPRMGeneticEngine:
    def __init__(self, cursos_df, profes_df, salones_df, zona, pop_size, generations):
        self.zona = zona
        self.pop_size = pop_size
        self.generations = generations
        self.salones = salones_df.to_dict('records')
        self.profesores = self._procesar_profesores(profes_df)
        self.secciones = self._generar_secciones_automaticas(cursos_df)
        
        # Configuración de Zona UPRM
        if zona == "CENTRAL":
            self.lim_inf, self.lim_sup = 450, 1110 # 7:30 - 18:30
            self.h_univ = (630, 750)              # 10:30 - 12:30
        else:
            self.lim_inf, self.lim_sup = 420, 1080 # 7:00 - 18:00
            self.h_univ = (600, 720)              # 10:00 - 12:00

    def _procesar_profesores(self, df):
        profes = {}
        for _, r in df.iterrows():
            nombre = str(r['Nombre']).upper()
            prefs = []
            disp = str(r.get('DISPONIBILIDAD', ""))
            if disp and disp.lower() != 'nan':
                for bloque in disp.split(';'):
                    try:
                        dias, horas = bloque.strip().split(' ')
                        h1, h2 = horas.split('-')
                        prefs.append({'dias': dias, 'ini': str_to_mins(h1), 'fin': str_to_mins(h2)})
                    except: continue
            profes[nombre] = {
                'min': r['Carga_Min'], 'max': r['Carga_Max'], 'prefs': prefs
            }
        return profes

    def _generar_secciones_automaticas(self, df):
        oferta = []
        for _, r in df.iterrows():
            demanda = int(r['DEMANDA_TOTAL'])
            secc_grandes = int(r['CANT_SECC_GRANDES'])
            cupo_g = int(r['CUPO_GRANDE'])
            cupo_n = int(r['CUPO_NORMAL'])
            cands = [c.strip().upper() for c in str(r['CANDIDATOS']).split(',') if c.strip()]
            
            # Crear secciones grandes
            for i in range(secc_grandes):
                uid = f"{r['CODIGO']}-{i+1:02d}G"
                oferta.append(Seccion(uid, r['CODIGO'], r['NOMBRE'], r['CREDITOS'], cupo_g, cands, r['TIPO_SALON']))
                demanda -= cupo_g
            
            # Crear secciones normales hasta cubrir demanda
            cont = secc_grandes + 1
            while demanda > 0:
                uid = f"{r['CODIGO']}-{cont:02d}"
                oferta.append(Seccion(uid, r['CODIGO'], r['NOMBRE'], r['CREDITOS'], cupo_n, cands, r['TIPO_SALON']))
                demanda -= cupo_n
                cont += 1
        return oferta

    def es_hora_segura(self, ini, fin, dias):
        if "MaJu" in dias:
            if max(ini, self.h_univ[0]) < min(fin, self.h_univ[1]): return False
        return True

    def generar_individuo(self):
        cromosoma = []
        for sec in self.secciones:
            prof = random.choice(sec.cands) if sec.cands else "TBA"
            salon = random.choice([s for s in self.salones if s['CAPACIDAD'] >= sec.cupo])
            es_mj = (sec.creditos == 4 or random.random() > 0.5)
            dias = "MaJu" if es_mj else "LuMiVi"
            dur = 80 if es_mj else 50
            
            # Bucle hasta encontrar hora que no choque con Hora Univ (Hard Constraint)
            h_ini = 0
            for _ in range(50):
                h_ini = random.randrange(self.lim_inf, self.lim_sup - dur, 30)
                if self.es_hora_segura(h_ini, h_ini + dur, dias): break
            
            cromosoma.append({'sec': sec, 'prof': prof, 'salon': salon['CODIGO'], 'ini': h_ini, 'fin': h_ini+dur, 'dias': dias})
        return cromosoma

    def fitness(self, individuo):
        score = 100000
        oc_p, oc_s = {}, {}
        cargas = {p: 0 for p in self.profesores}
        
        for g in individuo:
            # 1. Hard: Choques
            d_list = ["Lu", "Mi", "Vi"] if g['dias'] == "LuMiVi" else ["Ma", "Ju"]
            for d in d_list:
                for t in range(g['ini'], g['fin'], 10):
                    pk, sk = (g['prof'], d, t), (g['salon'], d, t)
                    if pk in oc_p and g['prof'] != "TBA": score -= 5000
                    if sk in oc_s: score -= 5000
                    oc_p[pk] = oc_s[sk] = True
            
            # 2. Hard: Hora Universal
            if not self.es_hora_segura(g['ini'], g['fin'], g['dias']): score -= 20000
            
            # 3. Soft: Preferencias Profe
            p_info = self.profesores.get(g['prof'])
            if p_info and p_info['prefs']:
                cumple = any(g['dias'] in pr['dias'] and g['ini'] >= pr['ini'] and g['fin'] <= pr['fin'] for pr in p_info['prefs'])
                if not cumple: score -= 200
            
            if g['prof'] in cargas: cargas[g['prof']] += g['sec'].creditos

        # 4. Soft: Cargas
        for p, c in cargas.items():
            if c > self.profesores[p]['max']: score -= 1000
            if 0 < c < self.profesores[p]['min']: score -= 500

        return max(score, 1)

    def evolucionar(self):
        poblacion = [self.generar_individuo() for _ in range(self.pop_size)]
        bar = st.progress(0)
        
        for gen in range(self.generations):
            poblacion.sort(key=self.fitness, reverse=True)
            descendencia = poblacion[:5] # Elitismo
            
            while len(descendencia) < self.pop_size:
                p1, p2 = random.sample(poblacion[:15], 2)
                hijo = p1[:len(p1)//2] + p2[len(p1)//2:]
                if random.random() < 0.2: # Mutación
                    m = random.randint(0, len(hijo)-1)
                    hijo[m] = self.generar_individuo()[m]
                descendencia.append(hijo)
            poblacion = descendencia
            bar.progress((gen+1)/self.generations)
            
        return poblacion[0]

# ==============================================================================
# 5. INTERFAZ STREAMLIT
# ==============================================================================
def main():
    st.title("🏛️ UPRM AI Scheduler: Tesis Edition")
    st.markdown("Generación automática de secciones basada en demanda estudiantil.")

    with st.sidebar:
        st.header("Configuración")
        zona = st.selectbox("Zona", ["CENTRAL", "PERIFERICA"])
        pop = st.slider("Población AI", 20, 100, 40)
        gens = st.slider("Generaciones AI", 50, 500, 100)
        file = st.file_uploader("Subir Plantilla", type=['xlsx'])

    if not file:
        st.info("Descarga la plantilla para empezar. El sistema calculará las secciones por ti.")
        st.download_button("📥 Descargar Nueva Plantilla", crear_excel_guia(), "UPRM_Smart_Template.xlsx")
    else:
        xls = pd.ExcelFile(file)
        if st.button("🚀 OPTIMIZAR OFERTA ACADÉMICA"):
            engine = UPRMGeneticEngine(pd.read_excel(xls, 'Cursos'), pd.read_excel(xls, 'Profesores'), pd.read_excel(xls, 'Salones'), zona, pop, gens)
            mejor = engine.evolucionar()
            
            res_df = pd.DataFrame([{
                'Sección': g['sec'].uid, 'Curso': g['sec'].nombre, 'Profesor': g['prof'],
                'Cupo': g['sec'].cupo, 'Días': g['dias'], 
                'Hora': f"{mins_to_str(g['ini'])} - {mins_to_str(g['fin'])}", 'Salón': g['salon']
            } for g in mejor])
            
            st.session_state.horario = res_df
            st.success(f"Se generaron {len(mejor)} secciones automáticamente para cubrir la demanda.")

        if 'horario' in st.session_state:
            st.dataframe(st.session_state.horario, use_container_width=True)
            # Gráfico de Gantt y Cargas (Igual que el anterior)
            # [Aquí irían los bloques de Plotly del código anterior...]



if __name__ == "__main__":
    main()
