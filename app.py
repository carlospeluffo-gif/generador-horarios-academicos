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
st.set_page_config(page_title="UPRM Scheduler Platinum AI v3", page_icon="🏛️", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #000000; color: #ffffff; }
    h1, h2, h3 { color: #FFD700 !important; text-shadow: 0px 0px 10px rgba(255, 215, 0, 0.3); }
    .stButton>button { background: linear-gradient(90deg, #B8860B, #FFD700); color: #000; font-weight: bold; border-radius: 8px; }
    .stTabs [data-baseweb="tab"] { color: #FFD700; font-weight: bold; }
    .error-box { padding: 10px; background-color: rgba(255,0,0,0.2); border-left: 5px solid red; margin-bottom: 10px; }
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

def str_to_mins(time_str):
    try:
        t = pd.to_datetime(time_str.strip(), format='%I:%M %p')
        return t.hour * 60 + t.minute
    except: return None

# ==============================================================================
# 3. MOTOR GENÉTICO AVANZADO
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
        self.best_fitness_history = []
        
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
            
            # Coherencia: Se busca una sola hora y salón para todos los días de la sección
            h_ini = 0
            for _ in range(100):
                h_ini = random.randrange(self.lim_inf, self.lim_sup - dur, 30)
                if self.es_hora_segura(h_ini, h_ini + dur, dias): break
                
            ind.append({'sec': sec, 'prof': prof, 'salon': salon, 'ini': h_ini, 'fin': h_ini + dur, 'dias': dias})
        return ind

    def fitness(self, cromosoma):
        penalizacion = 0
        oc_p, oc_s = {}, {}
        cargas = {p: [] for p in self.profesores}
        
        for g in cromosoma:
            # 1. Bloqueo Hora Universal
            if not self.es_hora_segura(g['ini'], g['fin'], g['dias']): penalizacion += 200000
            
            # 2. Choques y Registro de Carga
            d_list = ["Lu", "Mi", "Vi"] if g['dias'] == "LuMiVi" else ["Ma", "Ju"]
            for d in d_list:
                for t in range(g['ini'], g['fin'], 10):
                    pk, sk = (g['prof'], d, t), (g['salon'], d, t)
                    if pk in oc_p and g['prof'] != "TBA": penalizacion += 50000
                    if sk in oc_s and g['salon'] != "TBA": penalizacion += 50000
                    oc_p[pk] = oc_s[sk] = True
                cargas[g['prof']].append({'ini': g['ini'], 'fin': g['fin'], 'dia': d})

        # 3. Restricción: No más de 3 clases seguidas (180 min aprox)
        for p, periods in cargas.items():
            if p == "TBA": continue
            for d in ["Lu", "Ma", "Mi", "Ju", "Vi"]:
                day_clases = sorted([x for x in periods if x['dia'] == d], key=lambda x: x['ini'])
                seguidas = 0
                for i in range(len(day_clases)-1):
                    if day_clases[i+1]['ini'] - day_clases[i]['fin'] <= 15: # 15 min de margen
                        seguidas += 1
                        if seguidas >= 3: penalizacion += 10000
                    else: seguidas = 0
        
        return 1 / (1 + penalizacion)

    def evolucionar(self):
        pob = [self.generar_individuo() for _ in range(self.pop_size)]
        mutation_rate = 0.2
        last_best = 0
        stagnant_gens = 0
        bar = st.progress(0)
        
        for gen in range(self.generations):
            pob.sort(key=self.fitness, reverse=True)
            current_best = self.fitness(pob[0])
            
            # Mutación Adaptativa
            if current_best == last_best:
                stagnant_gens += 1
            else:
                stagnant_gens = 0
                last_best = current_best
            
            if stagnant_gens > 10:
                mutation_rate = min(0.8, mutation_rate + 0.05)
            else:
                mutation_rate = 0.2

            next_gen = pob[:2] # Elitismo estricto
            
            while len(next_gen) < self.pop_size:
                # Selección por Torneo
                p1 = self.torneo(pob)
                p2 = self.torneo(pob)
                
                # Crossover Inteligente (Bloques)
                punto = random.randint(0, len(p1)-1)
                hijo = p1[:punto] + p2[punto:]
                
                # Mutación
                if random.random() < mutation_rate:
                    idx = random.randint(0, len(hijo)-1)
                    hijo[idx] = self.generar_individuo()[idx]
                
                next_gen.append(hijo)
            
            pob = next_gen
            bar.progress((gen + 1) / self.generations)
            
        return pob[0]

    def torneo(self, pob):
        aspirantes = random.sample(pob, 3)
        aspirantes.sort(key=self.fitness, reverse=True)
        return aspirantes[0]

# ==============================================================================
# 4. FUNCIONES DE EXPORTACIÓN Y ANALIZADOR
# ==============================================================================
def exportar_excel_completo(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Horario_Maestro', index=False)
        # Pestañas por Profesor
        for prof in df['Profesor'].unique():
            if prof != "TBA":
                df[df['Profesor'] == prof].to_excel(writer, sheet_name=f"Prof_{prof[:20]}", index=False)
        # Pestañas por Salón
        for salon in df['Salón'].unique():
            if salon != "TBA":
                df[df['Salón'] == salon].to_excel(writer, sheet_name=f"Salon_{salon}", index=False)
    return output.getvalue()

def analizar_horario(df, engine):
    errores = []
    # Simular la lógica de choques
    oc_p, oc_s = {}, {}
    for _, r in df.iterrows():
        # Validar Hora Universal
        # (Aquí se usaría la misma lógica de fitness para reportar)
        dias = ["Lu", "Mi", "Vi"] if r['Días'] == "LuMiVi" else ["Ma", "Ju"]
        ini = str_to_mins(r['Horario'].split(' - ')[0])
        fin = str_to_mins(r['Horario'].split(' - ')[1])
        
        if not engine.es_hora_segura(ini, fin, r['Días']):
            errores.append(f"❌ {r['ID']} viola la Hora Universal.")
            
        for d in dias:
            for t in range(ini, fin, 10):
                pk, sk = (r['Profesor'], d, t), (r['Salón'], d, t)
                if pk in oc_p and r['Profesor'] != "TBA": errores.append(f"⚠️ Choque: {r['Profesor']} a las {mins_to_str(t)} el {d}")
                if sk in oc_s and r['Salón'] != "TBA": errores.append(f"⚠️ Salón Ocupado: {r['Salón']} a las {mins_to_str(t)} el {d}")
                oc_p[pk] = oc_s[sk] = True
    return list(set(errores))

# ==============================================================================
# 5. UI PRINCIPAL CON EDICIÓN MANUAL
# ==============================================================================
def main():
    st.title("🏛️ UPRM Scheduler Platinum AI v3")
    
    if 'master' not in st.session_state:
        st.session_state.master = None

    with st.sidebar:
        st.header("⚙️ Configuración")
        zona = st.selectbox("Zona", ["CENTRAL", "PERIFERICA"])
        pop, gens = st.slider("Población", 20, 100, 40), st.slider("Generaciones", 50, 300, 100)
        file = st.file_uploader("Excel de Datos", type=['xlsx'])

    if file:
        xls = pd.ExcelFile(file)
        if st.button("🚀 GENERAR HORARIO OPTIMIZADO"):
            engine = PlatinumGeneticEngine(pd.read_excel(xls, 'Cursos'), pd.read_excel(xls, 'Profesores'), pd.read_excel(xls, 'Salones'), pd.read_excel(xls, 'Graduados'), zona, pop, gens)
            mejor = engine.evolucionar()
            st.session_state.engine = engine
            st.session_state.master = pd.DataFrame([{
                'ID': g['sec'].uid, 'Curso': g['sec'].nombre, 'Profesor': g['prof'], 
                'Días': g['dias'], 'Horario': f"{mins_to_str(g['ini'])} - {mins_to_str(g['fin'])}",
                'Salón': g['salon']
            } for g in mejor])

    if st.session_state.master is not None:
        tab1, tab2, tab3 = st.tabs(["✍️ EDICIÓN Y AJUSTES", "📋 VISTAS DETALLADAS", "🚨 ANALIZADOR"])
        
        with tab1:
            st.subheader("Edición Manual Interactiva")
            st.info("Puedes cambiar el profesor o el salón directamente en la tabla. El sistema detectará errores al instante.")
            edited_df = st.data_editor(st.session_state.master, num_rows="fixed", use_container_width=True)
            st.session_state.master = edited_df
            
            st.download_button("📥 Descargar Excel para Impresión (Pestañas por Prof/Salón)", 
                               exportar_excel_completo(edited_df), "Horario_Final_UPRM.xlsx")

        with tab2:
            sub1, sub2 = st.columns(2)
            with sub1:
                p_filter = st.selectbox("Ver por Profesor", edited_df['Profesor'].unique())
                st.dataframe(edited_df[edited_df['Profesor'] == p_filter])
            with sub2:
                s_filter = st.selectbox("Ver por Salón", edited_df['Salón'].unique())
                st.dataframe(edited_df[edited_df['Salón'] == s_filter])

        with tab3:
            st.subheader("Reporte de Errores en Tiempo Real")
            errores = analizar_horario(edited_df, st.session_state.engine)
            if not errores:
                st.success("✅ El horario es 100% coherente y sin choques.")
            else:
                for err in errores:
                    st.markdown(f"<div class='error-box'>{err}</div>", unsafe_allow_html=True)



if __name__ == "__main__":
    main()
