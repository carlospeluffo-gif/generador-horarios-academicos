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
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; }
    .stTabs [data-baseweb="tab"] { color: #FFD700; border-bottom-color: #FFD700; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. UTILIDADES DE TIEMPO
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
        pd.DataFrame(columns=['CODIGO', 'NOMBRE', 'CREDITOS', 'DEMANDA_TOTAL', 'CANT_SECC_GRANDES', 'CUPO_GRANDE', 'CUPO_NORMAL', 'CANDIDATOS', 'TIPO_SALON']).to_excel(writer, sheet_name='Cursos', index=False)
        pd.DataFrame(columns=['Nombre', 'Carga_Min', 'Carga_Max', 'DISPONIBILIDAD']).to_excel(writer, sheet_name='Profesores', index=False)
        pd.DataFrame(columns=['CODIGO', 'CAPACIDAD', 'TIPO']).to_excel(writer, sheet_name='Salones', index=False)
        pd.DataFrame(columns=['NOMBRE', 'CREDITOS', 'CLASES_NECESARIAS']).to_excel(writer, sheet_name='Graduados', index=False)
    return output.getvalue()

# ==============================================================================
# 3. MOTOR DE ALGORITMO GENÉTICO
# ==============================================================================
class Seccion:
    def __init__(self, uid, cod_base, nombre, creditos, cupo, candidatos, tipo_salon, es_grad=False):
        self.uid, self.cod_base, self.nombre, self.creditos = uid, cod_base, nombre, creditos
        self.cupo, self.tipo_salon, self.cands, self.es_graduado = cupo, tipo_salon, candidatos, es_grad

class PlatinumGeneticEngine:
    def __init__(self, df_cursos, df_profes, df_salones, df_grad, zona, pop_size, generations):
        self.zona, self.pop_size, self.generations = zona, pop_size, generations
        self.salones = df_salones.to_dict('records')
        self.profesores = self._procesar_profesores(df_profes)
        self.secciones = self._automatizar_oferta(df_cursos, df_grad)
        
        if zona == "CENTRAL":
            self.lim_inf, self.lim_sup, self.h_univ = 450, 1110, (630, 750)
        else:
            self.lim_inf, self.lim_sup, self.h_univ = 420, 1080, (600, 720)

    def _procesar_profesores(self, df):
        p_dict = {}
        for _, r in df.iterrows():
            nombre = str(r['Nombre']).upper()
            prefs = []
            disp = str(r.get('DISPONIBILIDAD', ""))
            if disp and disp.lower() != 'nan':
                for bloque in disp.split(';'):
                    try:
                        partes = bloque.strip().split(' ')
                        dias, horas = partes[0], partes[1].split('-')
                        prefs.append({'dias': dias, 'ini': str_to_mins(horas[0]), 'fin': str_to_mins(horas[1])})
                    except: continue
            p_dict[nombre] = {'min': r['Carga_Min'], 'max': r['Carga_Max'], 'prefs': prefs}
        return p_dict

    def _automatizar_oferta(self, df_c, df_g):
        oferta = []
        for _, r in df_c.iterrows():
            demanda, secc_g, cupo_g, cupo_n = int(r['DEMANDA_TOTAL']), int(r['CANT_SECC_GRANDES']), int(r['CUPO_GRANDE']), int(r['CUPO_NORMAL'])
            cands = [c.strip().upper() for c in str(r['CANDIDATOS']).split(',') if c.strip()]
            for i in range(secc_g):
                if demanda <= 0: break
                oferta.append(Seccion(f"{r['CODIGO']}-{i+1:02d}G", r['CODIGO'], r['NOMBRE'], r['CREDITOS'], cupo_g, cands, r['TIPO_SALON']))
                demanda -= cupo_g
            cont = secc_g + 1
            while demanda > 0:
                oferta.append(Seccion(f"{r['CODIGO']}-{cont:02d}", r['CODIGO'], r['NOMBRE'], r['CREDITOS'], cupo_n, cands, r['TIPO_SALON']))
                demanda -= cupo_n
                cont += 1
        for _, r in df_g.iterrows():
            for i in range(int(r['CLASES_NECESARIAS'])):
                oferta.append(Seccion(f"GRAD-{r['NOMBRE'][:3]}-{i+1}", "GRAD", r['NOMBRE'], r['CREDITOS'], 1, ["TBA"], "OFICINA", True))
        return oferta

    def es_hora_segura(self, ini, fin, dias):
        if "MaJu" in dias:
            if max(ini, self.h_univ[0]) < min(fin, self.h_univ[1]): return False
        return True

    def generar_hora_valida(self, dur, dias):
        for _ in range(100):
            h_ini = random.randrange(self.lim_inf, self.lim_sup - dur, 30)
            if self.es_hora_segura(h_ini, h_ini + dur, dias): return h_ini
        return self.lim_inf

    def crear_individuo(self):
        ind = []
        for sec in self.secciones:
            prof = random.choice(sec.cands) if sec.cands else "TBA"
            sal_filtrados = [s for s in self.salones if s['CAPACIDAD'] >= sec.cupo]
            salon = random.choice(sal_filtrados)['CODIGO'] if sal_filtrados else "TBA"
            es_mj = (sec.creditos == 4 or random.random() > 0.5)
            dias, dur = ("MaJu", 80) if es_mj else ("LuMiVi", 50)
            h_ini = self.generar_hora_valida(dur, dias)
            ind.append({'sec': sec, 'prof': prof, 'salon': salon, 'ini': h_ini, 'fin': h_ini + dur, 'dias': dias})
        return ind

    def fitness(self, cromosoma):
        penalizacion = 0
        oc_p, oc_s = {}, {}
        cargas = {p: 0 for p in self.profesores}
        for g in cromosoma:
            if not self.es_hora_segura(g['ini'], g['fin'], g['dias']): penalizacion += 100000
            d_list = ["Lu", "Mi", "Vi"] if g['dias'] == "LuMiVi" else ["Ma", "Ju"]
            for d in d_list:
                for t in range(g['ini'], g['fin'], 10):
                    pk, sk = (g['prof'], d, t), (g['salon'], d, t)
                    if pk in oc_p and g['prof'] != "TBA": penalizacion += 10000
                    if sk in oc_s and g['salon'] != "TBA": penalizacion += 10000
                    oc_p[pk] = oc_s[sk] = True
            p_inf = self.profesores.get(g['prof'])
            if p_inf and p_inf['prefs']:
                if not any(g['dias'] in pr['dias'] and g['ini'] >= pr['ini'] and g['fin'] <= pr['fin'] for pr in p_inf['prefs']): penalizacion += 100
            if g['prof'] in cargas: cargas[g['prof']] += g['sec'].creditos
        for p, c in cargas.items():
            if c > self.profesores[p]['max']: penalizacion += 500
            if 0 < c < self.profesores[p]['min']: penalizacion += 200
        return 1 / (1 + penalizacion)

    def evolucionar(self):
        pob = [self.crear_individuo() for _ in range(self.pop_size)]
        bar = st.progress(0)
        for gen in range(self.generations):
            pob.sort(key=self.fitness, reverse=True)
            next_gen = pob[:4]
            while len(next_gen) < self.pop_size:
                p1, p2 = random.sample(pob[:15], 2)
                hijo = p1[:len(p1)//2] + p2[len(p1)//2:]
                if random.random() < 0.2:
                    idx = random.randint(0, len(hijo)-1)
                    dur = hijo[idx]['fin'] - hijo[idx]['ini']
                    hijo[idx]['ini'] = self.generar_hora_valida(dur, hijo[idx]['dias'])
                    hijo[idx]['fin'] = hijo[idx]['ini'] + dur
                next_gen.append(hijo)
            pob = next_gen
            bar.progress((gen + 1) / self.generations)
        return pob[0]

# ==============================================================================
# 4. ANALIZADOR DE ERRORES (DEBUGGER)
# ==============================================================================
def analizar_errores(horario, engine):
    errores = []
    oc_p, oc_s = {}, {}
    cargas = {p: 0 for p in engine.profesores}
    
    for g in horario:
        # Check Hora Universal
        if not engine.es_hora_segura(g['ini'], g['fin'], g['dias']):
            errores.append(f"❌ CRÍTICO: {g['sec'].uid} viola Hora Universal ({g['dias']} en {mins_to_str(g['ini'])})")
        
        # Check Choques
        d_list = ["Lu", "Mi", "Vi"] if g['dias'] == "LuMiVi" else ["Ma", "Ju"]
        for d in d_list:
            for t in range(g['ini'], g['fin'], 10):
                pk, sk = (g['prof'], d, t), (g['salon'], d, t)
                if pk in oc_p and g['prof'] != "TBA":
                    errores.append(f"⚠️ CHOQUE PROFESOR: {g['prof']} tiene dos clases el {d} a las {mins_to_str(t)}")
                if sk in oc_s and g['salon'] != "TBA":
                    errores.append(f"⚠️ CHOQUE SALÓN: El salón {g['salon']} está doblemente ocupado el {d} a las {mins_to_str(t)}")
                oc_p[pk] = oc_s[sk] = True
        if g['prof'] in cargas: cargas[g['prof']] += g['sec'].creditos

    for p, c in cargas.items():
        if c > engine.profesores[p]['max']: errores.append(f"⚖️ SOBRECARGA: {p} tiene {c} créditos (Máx: {engine.profesores[p]['max']})")
        if 0 < c < engine.profesores[p]['min']: errores.append(f"⚖️ CARGA BAJA: {p} tiene {c} créditos (Mín: {engine.profesores[p]['min']})")
    
    return list(set(errores)) # Eliminar duplicados de tiempo

# ==============================================================================
# 5. UI PRINCIPAL
# ==============================================================================
def main():
    st.title("🏛️ UPRM Scheduler Platinum AI")
    st.markdown("### Sistema de Optimización Genética de Oferta Académica")

    with st.sidebar:
        st.header("🧬 Panel de Control")
        zona = st.selectbox("Zona Campus", ["CENTRAL", "PERIFERICA"])
        pop, gens = st.slider("Población", 20, 100, 50), st.slider("Generaciones", 50, 500, 100)
        file = st.file_uploader("Subir Datos (Excel)", type=['xlsx'])
        if not file: st.download_button("📥 Plantilla", crear_excel_guia(), "UPRM_Template.xlsx")

    if file:
        xls = pd.ExcelFile(file)
        if st.button("🚀 INICIAR OPTIMIZACIÓN"):
            engine = PlatinumGeneticEngine(pd.read_excel(xls, 'Cursos'), pd.read_excel(xls, 'Profesores'), pd.read_excel(xls, 'Salones'), pd.read_excel(xls, 'Graduados'), zona, pop, gens)
            mejor_raw = engine.evolucionar()
            
            st.session_state.master = pd.DataFrame([{
                'ID': g['sec'].uid, 'Curso': g['sec'].nombre, 'Profesor': g['prof'], 'Días': g['dias'],
                'Horario': f"{mins_to_str(g['ini'])} - {mins_to_str(g['fin'])}", 'Salón': g['salon'],
                'Es_Grad': g['sec'].es_graduado, 'ini': g['ini'], 'fin': g['fin']
            } for g in mejor_raw])
            st.session_state.errores = analizar_errores(mejor_raw, engine)
            st.session_state.engine_data = engine

        if 'master' in st.session_state:
            tab_c, tab_p, tab_s, tab_e = st.tabs(["📚 POR CURSO", "👨‍🏫 POR PROFESOR", "🏠 POR SALÓN", "🚨 REPORTE DE ERRORES"])
            
            with tab_c:
                c_sel = st.selectbox("Filtrar Curso:", sorted(st.session_state.master['Curso'].unique()))
                st.table(st.session_state.master[st.session_state.master['Curso'] == c_sel][['ID', 'Profesor', 'Días', 'Horario', 'Salón']])

            with tab_p:
                p_sel = st.selectbox("Filtrar Profesor:", sorted(st.session_state.master['Profesor'].unique()))
                df_p = st.session_state.master[st.session_state.master['Profesor'] == p_sel]
                st.table(df_p[['ID', 'Curso', 'Días', 'Horario', 'Salón']])
                # Gantt Visual
                g_list = []
                d_map = {'Lu': '2026-02-02', 'Ma': '2026-02-03', 'Mi': '2026-02-04', 'Ju': '2026-02-05', 'Vi': '2026-02-06'}
                for _, r in df_p.iterrows():
                    for d in (["Lu", "Mi", "Vi"] if r['Días'] == "LuMiVi" else ["Ma", "Ju"]):
                        g_list.append({'Curso': r['ID'], 'Día': d, 'Start': f"{d_map[d]} {int(r['ini']//60):02d}:{int(r['ini']%60):02d}", 'End': f"{d_map[d]} {int(r['fin']//60):02d}:{int(r['fin']%60)}"})
                if g_list: st.plotly_chart(px.timeline(pd.DataFrame(g_list), x_start="Start", x_end="End", y="Día", color="Curso", template="plotly_dark", title=f"Agenda de {p_sel}"))

            with tab_s:
                s_sel = st.selectbox("Filtrar Salón:", sorted(st.session_state.master['Salón'].unique()))
                st.table(st.session_state.master[st.session_state.master['Salón'] == s_sel][['ID', 'Curso', 'Profesor', 'Días', 'Horario']])

            with tab_e:
                st.subheader("Informe de Consistencia")
                if not st.session_state.errores:
                    st.success("✨ ¡Horario Perfecto! No se encontraron conflictos ni choques.")
                else:
                    for err in st.session_state.errores:
                        if "❌" in err: st.error(err)
                        elif "⚠️" in err: st.warning(err)
                        else: st.info(err)



if __name__ == "__main__":
    main()
