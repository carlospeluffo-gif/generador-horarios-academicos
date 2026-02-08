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
# 1. ESTÉTICA PLATINUM (RESTAURADA Y MEJORADA)
# ==============================================================================
st.set_page_config(page_title="UPRM Scheduler Platinum AI v3", page_icon="🏛️", layout="wide")

st.markdown("""
<style>
    .stApp { 
        background-color: #000000; 
        background-image: linear-gradient(rgba(15, 15, 15, 0.6), rgba(15, 15, 15, 0.6)), url("https://www.transparenttextures.com/patterns/cubes.png"); 
        color: #ffffff; 
    }
    p, label, .stMarkdown, .stDataFrame, div[data-testid="stMarkdownContainer"] p { 
        color: #e0e0e0 !important; 
        font-family: 'Segoe UI', sans-serif; 
    }
    h1, h2, h3, h4 { 
        color: #FFD700 !important; 
        text-shadow: 0px 0px 15px rgba(255, 215, 0, 0.4); 
    }
    [data-testid="stSidebar"] { 
        background-color: #080808; 
        border-right: 1px solid #333; 
    }
    .stButton>button { 
        background: linear-gradient(90deg, #B8860B, #FFD700); 
        color: #000 !important; 
        font-weight: 800; 
        border: none; 
        padding: 0.6rem 1.2rem; 
        border-radius: 6px; 
        transition: transform 0.2s; 
    }
    .stButton>button:hover { 
        transform: scale(1.05); 
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.5); 
    }
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; }
    .stTabs [data-baseweb="tab"] { color: #FFD700; border-bottom-color: #FFD700; font-weight: bold; }
    .error-box { 
        padding: 15px; 
        background-color: rgba(255, 0, 0, 0.1); 
        border-left: 5px solid #ff4b4b; 
        border-radius: 4px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. UTILIDADES Y EXCEL DE GUÍA (REINTEGRADO)
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
# 3. MOTOR IA: SELECCIÓN POR TORNEO + BLOQUES + MUTACIÓN ADAPTATIVA
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
            p_dict[nombre] = {'min': r['Carga_Min'], 'max': r['Carga_Max'], 'prefs': []}
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

    def generar_individuo(self):
        ind = []
        for sec in self.secciones:
            prof = random.choice(sec.cands) if sec.cands else "TBA"
            sal_filtrados = [s for s in self.salones if s['CAPACIDAD'] >= sec.cupo]
            salon = random.choice(sal_filtrados)['CODIGO'] if sal_filtrados else "TBA"
            es_mj = (sec.creditos == 4 or random.random() > 0.5)
            dias, dur = ("MaJu", 80) if es_mj else ("LuMiVi", 50)
            h_ini = 0
            for _ in range(50):
                h_ini = random.randrange(self.lim_inf, self.lim_sup - dur, 30)
                if self.es_hora_segura(h_ini, h_ini + dur, dias): break
            ind.append({'sec': sec, 'prof': prof, 'salon': salon, 'ini': h_ini, 'fin': h_ini + dur, 'dias': dias})
        return ind

    def fitness(self, cromosoma):
        penalizacion = 0
        oc_p, oc_s = {}, {}
        cargas_prof = {p: [] for p in self.profesores}
        
        for g in cromosoma:
            if not self.es_hora_segura(g['ini'], g['fin'], g['dias']): penalizacion += 100000
            d_list = ["Lu", "Mi", "Vi"] if g['dias'] == "LuMiVi" else ["Ma", "Ju"]
            for d in d_list:
                for t in range(g['ini'], g['fin'], 10):
                    pk, sk = (g['prof'], d, t), (g['salon'], d, t)
                    if pk in oc_p and g['prof'] != "TBA": penalizacion += 10000
                    if sk in oc_s and g['salon'] != "TBA": penalizacion += 10000
                    oc_p[pk] = oc_s[sk] = True
                if g['prof'] != "TBA":
                    cargas_prof[g['prof']].append({'ini': g['ini'], 'fin': g['fin'], 'dia': d})

        # Regla: No más de 3 clases seguidas
        for p, slots in cargas_prof.items():
            for d in ["Lu", "Ma", "Mi", "Ju", "Vi"]:
                dia_clases = sorted([s for s in slots if s['dia'] == d], key=lambda x: x['ini'])
                seguidas = 0
                for i in range(len(dia_clases)-1):
                    if dia_clases[i+1]['ini'] - dia_clases[i]['fin'] <= 15:
                        seguidas += 1
                        if seguidas >= 3: penalizacion += 5000
                    else: seguidas = 0
        return 1 / (1 + penalizacion)

    def evolucionar(self):
        pob = [self.generar_individuo() for _ in range(self.pop_size)]
        mut_rate = 0.2
        last_best = 0
        stagnant = 0
        progress_bar = st.progress(0)
        
        for gen in range(self.generations):
            pob.sort(key=self.fitness, reverse=True)
            current_best = self.fitness(pob[0])
            
            if current_best == last_best: stagnant += 1
            else: stagnant = 0; last_best = current_best
            
            # Mutación Adaptativa
            mut_rate = 0.5 if stagnant > 10 else 0.2
            
            nueva_gen = pob[:2] # Elitismo
            while len(nueva_gen) < self.pop_size:
                p1 = self.torneo(pob); p2 = self.torneo(pob)
                punto = random.randint(0, len(p1)-1)
                hijo = p1[:punto] + p2[punto:]
                if random.random() < mut_rate:
                    idx = random.randint(0, len(hijo)-1)
                    hijo[idx] = self.generar_individuo()[idx]
                nueva_gen.append(hijo)
            pob = nueva_gen
            progress_bar.progress((gen + 1) / self.generations)
        return pob[0]

    def torneo(self, pob):
        aspirantes = random.sample(pob, 3)
        return max(aspirantes, key=self.fitness)

# ==============================================================================
# 4. EXPORTACIÓN Y ANÁLISIS
# ==============================================================================
def exportar_todo(df):
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Maestro', index=False)
        for p in df['Profesor'].unique():
            if p != "TBA": df[df['Profesor'] == p].to_excel(writer, sheet_name=f"Prof_{p[:20]}", index=False)
        for s in df['Salón'].unique():
            if s != "TBA": df[df['Salón'] == s].to_excel(writer, sheet_name=f"Salon_{s}", index=False)
    return out.getvalue()

def analizar_horario(df, engine):
    errs = []
    oc_p, oc_s = {}, {}
    for _, r in df.iterrows():
        try:
            h_split = r['Horario'].split(' - ')
            ini, fin = str_to_mins(h_split[0]), str_to_mins(h_split[1])
            if not engine.es_hora_segura(ini, fin, r['Días']):
                errs.append(f"❌ {r['ID']} viola Hora Universal en {r['Días']}")
            d_list = ["Lu", "Mi", "Vi"] if r['Días'] == "LuMiVi" else ["Ma", "Ju"]
            for d in d_list:
                for t in range(ini, fin, 10):
                    pk, sk = (r['Profesor'], d, t), (r['Salón'], d, t)
                    if pk in oc_p and r['Profesor'] != "TBA": errs.append(f"⚠️ Choque Prof: {r['Profesor']} ({d} {mins_to_str(t)})")
                    if sk in oc_s and r['Salón'] != "TBA": errs.append(f"⚠️ Choque Salón: {r['Salón']} ({d} {mins_to_str(t)})")
                    oc_p[pk] = oc_s[sk] = True
        except: continue
    return list(set(errs))

# ==============================================================================
# 5. UI PRINCIPAL (RESTAURADA)
# ==============================================================================
def main():
    st.title("🏛️ UPRM Scheduler Platinum AI v3")
    st.markdown("---")

    with st.sidebar:
        st.header("🧬 Configuración de IA")
        zona = st.selectbox("Zona Campus", ["CENTRAL", "PERIFERICA"])
        if zona == "CENTRAL":
            st.info("📍 Zona Central: Bloqueo Hora Universal 10:30 AM - 12:30 PM (MaJu)")
        else:
            st.info("📍 Zona Periférica: Bloqueo Hora Universal 10:00 AM - 12:00 PM (MaJu)")
            
        pop = st.slider("Tamaño de Población", 20, 100, 50)
        gens = st.slider("Generaciones", 50, 500, 100)
        
        st.markdown("---")
        file = st.file_uploader("Subir Archivo Excel", type=['xlsx'])
        if not file:
            st.download_button("📥 Descargar Plantilla Guía", crear_excel_guia(), "Plantilla_UPRM.xlsx")

    if file:
        xls = pd.ExcelFile(file)
        if st.button("🚀 INICIAR OPTIMIZACIÓN GENÉTICA"):
            with st.spinner("La IA está calculando el mejor horario posible..."):
                engine = PlatinumGeneticEngine(pd.read_excel(xls, 'Cursos'), pd.read_excel(xls, 'Profesores'), pd.read_excel(xls, 'Salones'), pd.read_excel(xls, 'Graduados'), zona, pop, gens)
                mejor = engine.evolucionar()
                st.session_state.engine = engine
                st.session_state.master = pd.DataFrame([{
                    'ID': g['sec'].uid, 'Curso': g['sec'].nombre, 'Profesor': g['prof'], 
                    'Días': g['dias'], 'Horario': f"{mins_to_str(g['ini'])} - {mins_to_str(g['fin'])}",
                    'Salón': g['salon']
                } for g in mejor])

    if 'master' in st.session_state:
        tab_edit, tab_view, tab_err = st.tabs(["✍️ EDICIÓN MANUAL", "📋 VISTAS POR CATEGORÍA", "🚨 REPORTE DE CONFLICTOS"])
        
        with tab_edit:
            st.subheader("Ajustes del Horario")
            st.warning("Los cambios realizados aquí se reflejarán automáticamente en el Reporte de Conflictos.")
            edited_df = st.data_editor(st.session_state.master, use_container_width=True, num_rows="fixed")
            st.session_state.master = edited_df
            st.download_button("💾 Exportar Excel Final (Multi-Pestaña)", exportar_todo(edited_df), "Horario_UPRM_Final.xlsx")

        with tab_view:
            c1, c2 = st.columns(2)
            with c1:
                p_sel = st.selectbox("Horario por Profesor", sorted(edited_df['Profesor'].unique()))
                st.table(edited_df[edited_df['Profesor'] == p_sel][['ID', 'Días', 'Horario', 'Salón']])
            with c2:
                s_sel = st.selectbox("Ocupación por Salón", sorted(edited_df['Salón'].unique()))
                st.table(edited_df[edited_df['Salón'] == s_sel][['ID', 'Profesor', 'Días', 'Horario']])

        with tab_err:
            st.subheader("Análisis de Integridad")
            errores = analizar_horario(edited_df, st.session_state.engine)
            if not errores:
                st.success("✨ ¡Perfecto! No se encontraron conflictos en el horario actual.")
            else:
                for err in errores:
                    st.markdown(f"<div class='error-box'>{err}</div>", unsafe_allow_html=True)



if __name__ == "__main__":
    main()
