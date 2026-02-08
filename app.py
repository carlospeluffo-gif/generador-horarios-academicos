import streamlit as st
import pandas as pd
import numpy as np
import random
import io
import plotly.express as px
import plotly.graph_objects as go

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
# 2. FUNCIONES DE TIEMPO
# ==============================================================================
def mins_to_str(minutes):
    h, m = divmod(int(minutes), 60)
    am_pm = "AM" if h < 12 else "PM"
    h_disp = h if h <= 12 else h - 12
    if h_disp == 0: h_disp = 12
    return f"{h_disp:02d}:{m:02d} {am_pm}"

def str_to_mins(time_str):
    """Convierte '08:30 AM' a minutos totales"""
    try:
        t = pd.to_datetime(time_str.strip(), format='%I:%M %p')
        return t.hour * 60 + t.minute
    except:
        return None

def crear_excel_guia():
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        pd.DataFrame(columns=['CODIGO', 'NOMBRE', 'CREDITOS', 'CANTIDAD_SECCIONES', 'CUPO', 'CANDIDATOS', 'TIPO_SALON']).to_excel(writer, sheet_name='Cursos', index=False)
        # Ejemplo de disponibilidad: "LuMiVi 07:30-10:30, MaJu 07:30-16:00"
        pd.DataFrame(columns=['Nombre', 'Carga_Min', 'Carga_Max', 'DISPONIBILIDAD']).to_excel(writer, sheet_name='Profesores', index=False)
        pd.DataFrame(columns=['CODIGO', 'CAPACIDAD', 'TIPO']).to_excel(writer, sheet_name='Salones', index=False)
    return output.getvalue()

# ==============================================================================
# 3. MOTOR DE ALGORITMO GENÉTICO CON PREFERENCIAS
# ==============================================================================

class GeneticEngine:
    def __init__(self, secciones, profesores, salones, zona, pop_size=30, generations=60):
        self.secciones = secciones
        self.profesores = {p['Nombre']: p for p in profesores}
        self.salones = salones
        self.zona = zona
        self.pop_size = pop_size
        self.generations = generations
        
        # Configuración de Zonas según UPRM
        if zona == "CENTRAL":
            self.rango_univ = (450, 1110) # 7:30 AM - 6:30 PM
            self.h_univ = (630, 750)     # 10:30 AM - 12:30 PM (Bloqueo)
            self.bloque_base = 30
        else:
            self.rango_univ = (420, 1080) # 7:00 AM - 6:00 PM
            self.h_univ = (600, 720)     # 10:00 AM - 12:00 PM (Bloqueo)
            self.bloque_base = 0

        # Parsear disponibilidad de profesores una sola vez
        self.prefs_procesadas = self._procesar_disponibilidad()

    def _procesar_disponibilidad(self):
        dict_prefs = {}
        for nombre, info in self.profesores.items():
            disp_str = str(info.get('DISPONIBILIDAD', ""))
            # Formato esperado: "LuMiVi 07:30-12:00; MaJu 08:00-16:00"
            dict_prefs[nombre] = []
            if disp_str and disp_str.lower() != "nan":
                bloques = disp_str.split(';')
                for b in bloques:
                    try:
                        partes = b.strip().split(' ')
                        dias = partes[0]
                        horas = partes[1].split('-')
                        dict_prefs[nombre].append({
                            'dias': dias,
                            'inicio': str_to_mins(horas[0]),
                            'fin': str_to_mins(horas[1])
                        })
                    except: continue
        return dict_prefs

    def generar_individuo(self):
        individuo = []
        for sec in self.secciones:
            prof = random.choice(sec.cands) if sec.cands else "TBA"
            salon = random.choice(self.salones)['CODIGO']
            es_mj = (sec.creditos == 4 or random.random() > 0.5)
            
            # Generar hora dentro del rango permitido
            h_inicio = random.randrange(self.rango_univ[0], self.rango_univ[1] - 80, 30)
            
            individuo.append({
                'sec': sec, 'prof': prof, 'salon': salon, 
                'inicio': h_inicio, 'fin': h_inicio + (80 if es_mj else 50),
                'dias': "MaJu" if es_mj else "LuMiVi"
            })
        return individuo

    def calcular_fitness(self, individuo):
        penalizaciones = 0
        oc_profe = {} 
        oc_salon = {}
        cargas = {p: 0 for p in self.profesores}

        for gene in individuo:
            # 1. Violación Hora Universal (Bloqueo)
            if gene['dias'] == "MaJu":
                if max(gene['inicio'], self.h_univ[0]) < min(gene['fin'], self.h_univ[1]):
                    penalizaciones += 200

            # 2. Fuera de Rango de la Zona
            if gene['inicio'] < self.rango_univ[0] or gene['fin'] > self.rango_univ[1]:
                penalizaciones += 300

            # 3. Preferencia del Profesor (Crucial)
            p_name = gene['prof']
            if p_name in self.prefs_procesadas and self.prefs_procesadas[p_name]:
                cumple_pref = False
                for pref in self.prefs_procesadas[p_name]:
                    if gene['dias'] in pref['dias'] or pref['dias'] in gene['dias']:
                        if gene['inicio'] >= pref['inicio'] and gene['fin'] <= pref['fin']:
                            cumple_pref = True; break
                if not cumple_pref: penalizaciones += 150 # Penalización por ignorar su deseo

            # 4. Choques Horarios
            dias_lista = ["Lu", "Mi", "Vi"] if gene['dias'] == "LuMiVi" else ["Ma", "Ju"]
            for d in dias_lista:
                for t in range(gene['inicio'], gene['fin'], 10):
                    p_key, s_key = (p_name, d, t), (gene['salon'], d, t)
                    if p_key in oc_profe and p_name != "TBA": penalizaciones += 500
                    if s_key in oc_salon: penalizaciones += 500
                    oc_profe[p_key] = oc_salon[s_key] = True
            
            if p_name in cargas: cargas[p_name] += gene['sec'].creditos

        return 1 / (1 + penalizaciones)

    def evolucionar(self):
        poblacion = [self.generar_individuo() for _ in range(self.pop_size)]
        progress_bar = st.progress(0)
        
        for gen in range(self.generations):
            poblacion.sort(key=lambda x: self.calcular_fitness(x), reverse=True)
            nueva_gen = poblacion[:4] # Elitismo aumentado
            
            while len(nueva_gen) < self.pop_size:
                p1, p2 = random.sample(poblacion[:15], 2)
                punto = random.randint(1, len(p1)-1)
                hijo = p1[:punto] + p2[punto:]
                # Mutación ocasional
                if random.random() < 0.15:
                    idx = random.randint(0, len(hijo)-1)
                    hijo[idx]['inicio'] = random.randrange(self.rango_univ[0], self.rango_univ[1]-80, 30)
                nueva_gen.append(hijo)
            
            poblacion = nueva_gen
            progress_bar.progress((gen + 1) / self.generations)
            
        return poblacion[0]

# ==============================================================================
# 4. INTERFAZ
# ==============================================================================
def main():
    st.title("🏛️ UPRM Scheduler Platinum AI")
    st.caption("Optimización Genética con Preferencias de Facultad y Restricciones de Zona")
    
    col_dl, col_info = st.columns([1, 2])
    with col_dl:
        st.download_button("📥 Descargar Plantilla", crear_excel_guia(), "UPRM_Template.xlsx")
    with col_info:
        st.info("**Nota:** En la columna DISPONIBILIDAD usa el formato: `LuMiVi 07:30 AM-01:00 PM; MaJu 08:00 AM-05:00 PM`")

    with st.sidebar:
        st.header("Configuración")
        zona = st.selectbox("📍 Zona", ["CENTRAL", "PERIFERICA"])
        pop = st.slider("Tamaño de Población", 20, 100, 40)
        gens = st.slider("Generaciones", 20, 200, 80)
        file = st.file_uploader("📂 Subir Excel", type=['xlsx'])

    if file:
        xls = pd.ExcelFile(file)
        df_cur = pd.read_excel(xls, 'Cursos')
        df_pro = pd.read_excel(xls, 'Profesores')
        df_sal = pd.read_excel(xls, 'Salones')

        if st.button("🚀 GENERAR HORARIO ÓPTIMO"):
            secciones = []
            for _, r in df_cur.iterrows():
                for i in range(int(r.get('CANTIDAD_SECCIONES', 1))):
                    from __main__ import Seccion # Manejo de clase interna
                    secciones.append(type('Seccion', (), {
                        'uid': f"{r['CODIGO']}-{i+1:02d}", 'nombre': r['NOMBRE'], 'creditos': int(r['CREDITOS']),
                        'cupo': r['CUPO'], 'cands': [c.strip().upper() for c in str(r['CANDIDATOS']).split(',')],
                        'tipo_salon': r['TIPO_SALON']
                    }))
            
            engine = GeneticEngine(secciones, df_pro.to_dict('records'), df_sal.to_dict('records'), zona, pop, gens)
            mejor = engine.evolucionar()
            
            res_list = []
            cargas = {p['Nombre']: 0 for p in df_pro.to_dict('records')}
            for g in mejor:
                res_list.append({
                    'Curso': g['sec'].uid, 'Nombre': g['sec'].nombre, 'Profesor': g['prof'],
                    'Días': g['dias'], 'Inicio_Min': g['inicio'], 'Fin_Min': g['fin'], 'Salón': g['salon']
                })
                if g['prof'] in cargas: cargas[g['prof']] += g['sec'].creditos
            
            st.session_state.horario = pd.DataFrame(res_list)
            st.session_state.cargas = cargas
            st.session_state.prof_raw = df_pro.to_dict('records')

        if 'horario' in st.session_state:
            t1, t2 = st.tabs(["📅 Horario General", "👨‍🏫 Vista por Profesor"])
            with t1:
                df_view = st.session_state.horario.copy()
                df_view['Horario'] = df_view['Inicio_Min'].apply(mins_to_str) + " - " + df_view['Fin_Min'].apply(mins_to_str)
                st.dataframe(df_view[['Curso', 'Nombre', 'Profesor', 'Días', 'Horario', 'Salón']], use_container_width=True)
            
            with t2:
                p_sel = st.selectbox("Seleccione Profesor", st.session_state.horario['Profesor'].unique())
                df_p = st.session_state.horario[st.session_state.horario['Profesor'] == p_sel]
                
                # Visualización Gantt para el profesor
                gantt_data = []
                d_map = {'Lu': '2026-02-02', 'Ma': '2026-02-03', 'Mi': '2026-02-04', 'Ju': '2026-02-05', 'Vi': '2026-02-06'}
                for _, row in df_p.iterrows():
                    dias = ["Lu", "Mi", "Vi"] if row['Días'] == "LuMiVi" else ["Ma", "Ju"]
                    for d in dias:
                        gantt_data.append({
                            'Curso': row['Curso'], 'Día': d,
                            'Start': f"{d_map[d]} {int(row['Inicio_Min']//60):02d}:{int(row['Inicio_Min']%60):02d}:00",
                            'Finish': f"{d_map[d]} {int(row['Fin_Min']//60):02d}:{int(row['Fin_Min']%60):02d}:00"
                        })
                
                if gantt_data:
                    fig = px.timeline(pd.DataFrame(gantt_data), x_start="Start", x_end="Finish", y="Día", color="Curso", template="plotly_dark", title=f"Agenda de {p_sel}")
                    fig.update_yaxes(categoryorder="array", categoryarray=['Lu', 'Ma', 'Mi', 'Ju', 'Vi'])
                    st.plotly_chart(fig, use_container_width=True)

# Diagrama del proceso de selección del algoritmo


if __name__ == "__main__":
    main()
