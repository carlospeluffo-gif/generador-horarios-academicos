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
# 1. ESTÉTICA PLATINUM (CONSERVADA ÍNTEGRAMENTE)
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
# 2. FUNCIONES DE APOYO Y TIEMPO
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
        pd.DataFrame(columns=['CODIGO', 'NOMBRE', 'CREDITOS', 'CANTIDAD_SECCIONES', 'CUPO', 'CANDIDATOS', 'TIPO_SALON']).to_excel(writer, sheet_name='Cursos', index=False)
        pd.DataFrame(columns=['Nombre', 'Carga_Min', 'Carga_Max', 'DISPONIBILIDAD']).to_excel(writer, sheet_name='Profesores', index=False)
        pd.DataFrame(columns=['CODIGO', 'CAPACIDAD', 'TIPO']).to_excel(writer, sheet_name='Salones', index=False)
        pd.DataFrame(columns=['NOMBRE', 'CREDITOS', 'CLASES A RECIBIR']).to_excel(writer, sheet_name='Graduados', index=False)
    return output.getvalue()

# ==============================================================================
# 3. MOTOR GENÉTICO CON PROHIBICIÓN ESTRICTA DE HORA UNIVERSAL
# ==============================================================================
class Seccion:
    def __init__(self, uid, cod_base, nombre, creditos, cupo, candidatos, tipo_salon, es_grad=False):
        self.uid = uid
        self.cod_base = str(cod_base).upper()
        self.nombre = nombre
        self.creditos = int(creditos)
        self.cupo = int(cupo)
        self.tipo_salon = str(tipo_salon).upper()
        self.cands = [c.strip().upper() for c in str(candidatos).split(',') if c.strip()] if not pd.isna(candidatos) else []
        self.es_graduado = es_grad

class PlatinumGeneticEngine:
    def __init__(self, secciones, profes_dict, salones, zona, pop_size=40, generations=100):
        self.secciones = secciones
        self.profes_dict = profes_dict
        self.salones = salones
        self.zona = zona
        self.pop_size = pop_size
        self.generations = generations
        
        # Límites estrictos según zona UPRM
        if zona == "CENTRAL":
            self.lim_inf, self.lim_sup = 450, 1110 # 7:30 AM - 6:30 PM
            self.h_univ = (630, 750)              # 10:30 AM - 12:30 PM (PROHIBIDO)
        else:
            self.lim_inf, self.lim_sup = 420, 1080 # 7:00 AM - 6:00 PM
            self.h_univ = (600, 720)              # 10:00 AM - 12:00 PM (PROHIBIDO)

        self.prefs = self._parse_prefs()

    def _parse_prefs(self):
        parsed = {}
        for p, info in self.profes_dict.items():
            disp = str(info.get('DISPONIBILIDAD', ""))
            parsed[p] = []
            if disp.lower() != "nan" and disp:
                for bloque in disp.split(';'):
                    try:
                        dias, horas = bloque.strip().split(' ')
                        h1, h2 = horas.split('-')
                        parsed[p].append({'dias': dias, 'ini': str_to_mins(h1), 'fin': str_to_mins(h2)})
                    except: continue
        return parsed

    def es_hora_valida(self, ini, fin, dias):
        """Verifica si el horario choca con la Hora Universal Prohibida"""
        if "MaJu" in dias:
            # Si el rango de la clase se traslapa con la Hora Universal, es falso
            if max(ini, self.h_univ[0]) < min(fin, self.h_univ[1]):
                return False
        return True

    def generar_hora_segura(self, duracion, dias):
        """Genera una hora aleatoria que CUMPLE con la prohibición de Hora Universal"""
        intentos = 0
        while intentos < 100:
            h_ini = random.randrange(self.lim_inf, self.lim_sup - duracion, 30)
            if self.es_hora_valida(h_ini, h_ini + duracion, dias):
                return h_ini
            intentos += 1
        return self.lim_inf # Fallback

    def crear_individuo(self):
        horario = []
        for sec in self.secciones:
            prof = random.choice(sec.cands) if sec.cands else "TBA"
            salon = random.choice(self.salones)
            es_mj = (sec.creditos == 4 or random.random() > 0.5)
            dias = "MaJu" if es_mj else "LuMiVi"
            dur = 80 if es_mj else 50
            
            h_ini = self.generar_hora_segura(dur, dias)
            
            horario.append({
                'sec': sec, 'prof': prof, 'salon': salon['CODIGO'],
                'ini': h_ini, 'fin': h_ini + dur, 'dias': dias
            })
        return horario

    def fitness(self, individuo):
        penalizacion = 0
        oc_p, oc_s = {}, {}
        cargas = {p: 0 for p in self.profes_dict}
        
        for g in individuo:
            # 1. PROHIBICIÓN CRÍTICA: Hora Universal (Si cae aquí, la solución es casi nula)
            if not self.es_hora_valida(g['ini'], g['fin'], g['dias']):
                penalizacion += 100000 
            
            # 2. Preferencias de Profesor (Restricción Blanda)
            if g['prof'] in self.prefs and self.prefs[g['prof']]:
                cumple = False
                for pr in self.prefs[g['prof']]:
                    if g['dias'] in pr['dias'] and g['ini'] >= pr['ini'] and g['fin'] <= pr['fin']:
                        cumple = True; break
                if not cumple: penalizacion += 150

            # 3. Choques de Horario
            dias = ["Lu", "Mi", "Vi"] if g['dias'] == "LuMiVi" else ["Ma", "Ju"]
            for d in dias:
                for t in range(g['ini'], g['fin'], 10):
                    pk, sk = (g['prof'], d, t), (g['salon'], d, t)
                    if pk in oc_p and g['prof'] != "TBA": penalizacion += 1000
                    if sk in oc_s: penalizacion += 1000
                    oc_p[pk] = oc_s[sk] = True
            
            if g['prof'] in cargas: cargas[g['prof']] += g['sec'].creditos

        return 1 / (1 + penalizacion)

    def optimizar(self):
        poblacion = [self.crear_individuo() for _ in range(self.pop_size)]
        bar = st.progress(0)
        
        for gen in range(self.generations):
            poblacion.sort(key=self.fitness, reverse=True)
            proxima_gen = poblacion[:4] # Elitismo de los mejores 4
            
            while len(proxima_gen) < self.pop_size:
                p1, p2 = random.sample(poblacion[:15], 2)
                punto = random.randint(1, len(p1)-1)
                hijo = p1[:punto] + p2[punto:]
                
                # Mutación Inteligente: Si muta la hora, debe seguir siendo segura
                if random.random() < 0.2:
                    m = random.randint(0, len(hijo)-1)
                    dur = hijo[m]['fin'] - hijo[m]['ini']
                    hijo[m]['ini'] = self.generar_hora_segura(dur, hijo[m]['dias'])
                    hijo[m]['fin'] = hijo[m]['ini'] + dur
                
                proxima_gen.append(hijo)
            
            poblacion = proxima_gen
            bar.progress((gen+1)/self.generations)
            
        return poblacion[0]

# ==============================================================================
# 4. INTERFAZ (RESTO DEL CÓDIGO)
# ==============================================================================
def main():
    st.title("🏛️ UPRM Scheduler Platinum AI")
    st.markdown("### 🚫 Restricción Estricta: Hora Universal Protegida")
    
    col_desc, _ = st.columns([1, 2])
    col_desc.download_button("📥 Descargar Plantilla", crear_excel_guia(), "plantilla_uprm.xlsx")
    
    with st.sidebar:
        st.header("⚙️ Configuración Motor")
        zona = st.selectbox("📍 Zona", ["CENTRAL", "PERIFERICA"])
        if zona == "CENTRAL":
            st.warning("Hora Universal: 10:30 AM - 12:30 PM (BLOQUEADA)")
        else:
            st.warning("Hora Universal: 10:00 AM - 12:00 PM (BLOQUEADA)")
            
        pop = st.slider("Población AI", 20, 100, 50)
        gens = st.slider("Generaciones AI", 10, 200, 80)
        file = st.file_uploader("📂 Subir Excel", type=['xlsx'])

    if file:
        xls = pd.ExcelFile(file)
        df_cur = pd.read_excel(xls, 'Cursos')
        df_pro = pd.read_excel(xls, 'Profesores')
        df_sal = pd.read_excel(xls, 'Salones')

        if st.button("🚀 GENERAR HORARIO MAESTRO"):
            profes_dict = {str(r['Nombre']).upper(): {
                'Carga_Min': r['Carga_Min'], 
                'Carga_Max': r['Carga_Max'], 
                'DISPONIBILIDAD': r.get('DISPONIBILIDAD', ""), 
                'es_grad': False
            } for _, r in df_pro.iterrows()}
            
            secciones = []
            for _, r in df_cur.iterrows():
                for i in range(int(r.get('CANTIDAD_SECCIONES', 1))):
                    secciones.append(Seccion(f"{r['CODIGO']}-{i+1:02d}", r['CODIGO'], r['NOMBRE'], r['CREDITOS'], r['CUPO'], r['CANDIDATOS'], r['TIPO_SALON']))
            
            engine = PlatinumGeneticEngine(secciones, profes_dict, df_sal.to_dict('records'), zona, pop, gens)
            mejor_plan = engine.optimizar()
            
            res_rows = []
            cargas_f = {p: 0 for p in profes_dict}
            for g in mejor_plan:
                res_rows.append({
                    'Curso': g['sec'].uid, 'Nombre': g['sec'].nombre, 'Profesor': g['prof'],
                    'Días': g['dias'], 'Inicio': g['ini'], 'Fin': g['fin'], 'Salón': g['salon']
                })
                if g['prof'] in cargas_f: cargas_f[g['prof']] += g['sec'].creditos

            st.session_state.horario = pd.DataFrame(res_rows)
            st.session_state.cargas = cargas_f
            st.session_state.prof_info = profes_dict

        if 'horario' in st.session_state:
            tab1, tab2 = st.tabs(["📅 HORARIO MAESTRO", "👨‍🏫 ANÁLISIS POR PROFESOR"])
            
            with tab1:
                df_disp = st.session_state.horario.copy()
                df_disp['Hora'] = df_disp['Inicio'].apply(mins_to_str) + " - " + df_disp['Fin'].apply(mins_to_str)
                st.dataframe(df_disp[['Curso', 'Nombre', 'Profesor', 'Días', 'Hora', 'Salón']], use_container_width=True)

            with tab2:
                p_sel = st.selectbox("Profesor:", st.session_state.horario['Profesor'].unique())
                df_p = st.session_state.horario[st.session_state.horario['Profesor'] == p_sel]
                
                # Visualización Gantt
                plot_data = []
                d_map = {'Lu': '2026-02-02', 'Ma': '2026-02-03', 'Mi': '2026-02-04', 'Ju': '2026-02-05', 'Vi': '2026-02-06'}
                for _, row in df_p.iterrows():
                    d_list = ["Lu", "Mi", "Vi"] if row['Días'] == "LuMiVi" else ["Ma", "Ju"]
                    for d in d_list:
                        plot_data.append({
                            'Curso': row['Curso'], 'Día': d,
                            'Start': f"{d_map[d]} {int(row['Inicio']//60):02d}:{int(row['Inicio']%60):02d}:00",
                            'Finish': f"{d_map[d]} {int(row['Fin']//60):02d}:{int(row['Fin']%60):02d}:00"
                        })
                if plot_data:
                    fig = px.timeline(pd.DataFrame(plot_data), x_start="Start", x_end="Finish", y="Día", color="Curso", template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)



if __name__ == "__main__":
    main()
