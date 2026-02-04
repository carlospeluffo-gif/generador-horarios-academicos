import streamlit as st
import pandas as pd
import numpy as np
import random
import copy
import time
import io
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ==============================================================================
# 1. ESTÉTICA PLATINUM (INTACTA)
# ==============================================================================
st.set_page_config(page_title="UPRM Scheduler Platinum", page_icon="🏛️", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #000000; background-image: linear-gradient(rgba(15, 15, 15, 0.50), rgba(15, 15, 15, 0.50)), url("https://www.transparenttextures.com/patterns/cubes.png"); color: #ffffff; }
    p, label, .stMarkdown, .stDataFrame, div[data-testid="stMarkdownContainer"] p { color: #e0e0e0 !important; font-family: 'Segoe UI', sans-serif; }
    h1, h2, h3, h4 { color: #FFD700 !important; text-shadow: 0px 0px 15px rgba(255, 215, 0, 0.4); }
    [data-testid="stSidebar"] { background-color: #080808; border-right: 1px solid #333; }
    .stButton>button { background: linear-gradient(90deg, #B8860B, #FFD700); color: #000 !important; font-weight: 800; border: none; padding: 0.6rem 1.2rem; border-radius: 6px; transition: transform 0.2s; }
    .stButton>button:hover { transform: scale(1.05); box-shadow: 0 0 20px rgba(255, 215, 0, 0.5); }
    [data-testid="stDataFrame"] { background-color: #111; border: 1px solid #333; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. LÓGICA DE TIEMPO Y BLOQUES
# ==============================================================================
def generar_bloques_por_zona(zona):
    bloques = {}
    h_inicio = [h*60 + 30 for h in range(7, 20)] if zona == "CENTRAL" else [h*60 for h in range(7, 20)]
    def add_b(id_base, dias, dur, lbl):
        for h in h_inicio:
            if h + dur > 1320: continue 
            bloques[f"{id_base}_{h}"] = {'id_base': id_base, 'dias': dias, 'inicio': h, 'duracion': dur, 'label': lbl}
    add_b(1, ['Lu', 'Mi', 'Vi'], 50, "LMV")
    add_b(2, ['Ma', 'Ju'], 80, "MJ")
    add_b(8, ['Lu','Ma','Mi','Ju'], 50, "LMWJ")
    add_b(13, ['Lu', 'Mi'], 110, "LW (Largo)")
    add_b(15, ['Ma', 'Ju'], 110, "MJ (Largo)")
    add_b(17, ['Lu','Ma','Mi','Ju','Vi'], 50, "Diario")
    return bloques

def mins_to_str(minutes):
    h, m = int(minutes // 60), int(minutes % 60)
    ap = "AM" if h < 12 else "PM"
    hd = h if h <= 12 else h - 12
    if hd == 0: hd = 12
    return f"{hd:02d}:{m:02d} {ap}"

# ==============================================================================
# 3. ESTRUCTURAS DE DATOS
# ==============================================================================
class Seccion:
    def __init__(self, uid, cod_base, creditos, cupo, candidatos, tipo_salon):
        self.uid = uid
        self.cod_base = str(cod_base).strip().upper()
        self.creditos = int(creditos)
        self.cupo = int(cupo)
        self.tipo_salon = str(tipo_salon).strip().upper()
        cands = str(candidatos).strip().upper()
        self.cands_list = [c.strip() for c in cands.split(',') if c.strip()]
        self.solo_graduados = "GRADUADOS" in self.cands_list

class Profesor:
    def __init__(self, nombre, c_min, c_max, es_graduado=False, clases_recibe=None):
        self.nombre = str(nombre).strip().upper()
        self.c_min = float(c_min)
        self.c_max = float(c_max)
        self.es_graduado = es_graduado
        self.clases_recibe = clases_recibe if clases_recibe else []

class HorarioGen:
    def __init__(self, seccion, prof_nom, b_key, salon_obj):
        self.seccion, self.prof_nom, self.b_key, self.salon_obj = seccion, prof_nom, b_key, salon_obj

# ==============================================================================
# 4. MOTOR INTELIGENTE PLATINUM
# ==============================================================================
class PlatinumEngine:
    def __init__(self, secciones, profesores, salones, zona):
        self.secciones = secciones
        self.profes_dict = {p.nombre: p for p in profesores}
        self.salones = salones
        self.bloques = generar_bloques_por_zona(zona)
        self.h_univ = (630, 750) if zona == "CENTRAL" else (600, 720)

    def es_compatible(self, b_key, prof_nom, s_obj, oc_p, oc_s, mapa_clases_grad):
        b = self.bloques[b_key]
        ini, fin = b['inicio'], b['inicio'] + b['duracion']
        
        # 1. Hora Universal
        if any(d in ['Ma', 'Ju'] for d in b['dias']):
            if max(ini, self.h_univ[0]) < min(fin, self.h_univ[1]): return False

        # 2. Bloqueo Graduado (Clases que recibe)
        p_obj = self.profes_dict.get(prof_nom)
        if p_obj and p_obj.clases_recibe:
            for cod_recibe in p_obj.clases_recibe:
                if cod_recibe in mapa_clases_grad:
                    for (t1, t2, dias_rec) in mapa_clases_grad[cod_recibe]:
                        if any(d in b['dias'] for d in dias_rec):
                            if max(ini, t1) < min(fin, t2): return False

        # 3. Choques de salón y profesor
        for d in b['dias']:
            if (s_obj.codigo, d) in oc_s:
                for (t1, t2) in oc_s[(s_obj.codigo, d)]:
                    if max(ini, t1) < min(fin, t2): return False
            if prof_nom != "TBA" and (prof_nom, d) in oc_p:
                for (t1, t2) in oc_p[(prof_nom, d)]:
                    if max(ini, t1) < min(fin, t2): return False
        return True

    def generar_individuo(self):
        genes, oc_p, oc_s, cargas = [], {}, {}, {p: 0 for p in self.profes_dict}
        mapa_grad = {} # Para rastrear donde quedan las clases que graduados reciben
        
        sec_ord = sorted(self.secciones, key=lambda x: (not x.solo_graduados, random.random()))

        for sec in sec_ord:
            # Filtrar Candidatos
            if sec.solo_graduados:
                pool_p = [p.nombre for p in self.profes_dict.values() if p.es_graduado]
            else:
                pool_p = [c for c in sec.cands_list if c in self.profes_dict]
            
            prof = "TBA"
            if pool_p:
                validos = [p for p in pool_p if cargas[p] + sec.creditos <= self.profes_dict[p].c_max]
                if validos:
                    validos.sort(key=lambda p: (cargas[p] >= self.profes_dict[p].c_min, cargas[p]))
                    prof = validos[0]

            pool_b = list(self.bloques.keys())
            pool_s = [s for s in self.salones if s.capacidad >= sec.cupo]
            if sec.tipo_salon != 'GENERAL': pool_s = [s for s in pool_s if s.tipo == sec.tipo_salon]
            if not pool_s: pool_s = self.salones

            random.shuffle(pool_b); random.shuffle(pool_s)
            
            asignado = False
            for s in pool_s:
                for bk in pool_b:
                    if self.es_compatible(bk, prof, s, oc_p, oc_s, mapa_grad):
                        bd = self.bloques[bk]
                        cargas[prof] += sec.creditos
                        for d in bd['dias']:
                            oc_s.setdefault((s.codigo, d), []).append((bd['inicio'], bd['inicio']+bd['duracion']))
                            if prof != "TBA": oc_p.setdefault((prof, d), []).append((bd['inicio'], bd['inicio']+bd['duracion']))
                        
                        genes.append(HorarioGen(sec, prof, bk, s))
                        mapa_grad.setdefault(sec.cod_base, []).append((bd['inicio'], bd['inicio']+bd['duracion'], bd['dias']))
                        asignado = True; break
                if asignado: break
            if not asignado: genes.append(HorarioGen(sec, prof, random.choice(pool_b), random.choice(pool_s)))
        return genes

    def evolucionar(self, pop_size, gens, callback):
        poblacion = [self.generar_individuo() for _ in range(pop_size)]
        best_ind, best_fit = None, -9999
        for g in range(gens):
            scores = []
            for ind in poblacion:
                # Detección básica de conflictos para el fitness
                oc_p, oc_s, err = {}, {}, 0
                for gen in ind:
                    b = self.bloques[gen.b_key]
                    for d in b['dias']:
                        ks, kp = (gen.salon_obj.codigo, d), (gen.prof_nom, d)
                        if ks in oc_s: err += 1
                        oc_s[ks] = True
                        if gen.prof_nom != "TBA":
                            if kp in oc_p: err += 1
                            oc_p[kp] = True
                fit = -err
                scores.append((fit, ind))
                if fit > best_fit: best_fit, best_ind = fit, ind
            if best_fit == 0: break
            callback(g, gens, abs(best_fit))
            scores.sort(key=lambda x: x[0], reverse=True)
            poblacion = [s[1] for s in scores[:pop_size//2]] * 2
        return best_ind, abs(best_fit)

# ==============================================================================
# 5. INTERFAZ DE USUARIO
# ==============================================================================
def main():
    st.title("🏛️ UPRM Scheduler Platinum")
    with st.sidebar:
        st.header("⚙️ Configuración")
        zona = st.selectbox("📍 Zona de Horarios", ["CENTRAL", "PERIFERICA"])
        excel = st.file_uploader("📂 Subir Excel Maestro", type=['xlsx'])
        pop = st.slider("Población", 20, 100, 50)
        gens = st.slider("Generaciones", 10, 200, 50)

    if excel:
        try:
            xls = pd.ExcelFile(excel)
            df_cur = pd.read_excel(xls, 'Cursos')
            df_pro = pd.read_excel(xls, 'Profesores')
            df_sal = pd.read_excel(xls, 'Salones')
            df_gra = pd.read_excel(xls, 'Graduados') if 'Graduados' in xls.sheet_names else pd.DataFrame()

            # 1. Cargar Profesores y Graduados
            profesores = []
            for _, r in df_pro.iterrows():
                profesores.append(Profesor(r['Nombre'], r['Carga_Min'], r['Carga_Max']))
            for _, r in df_gra.iterrows():
                clases = [c.strip().upper() for c in str(r.get('CLASES A RECIBIR','')).split(',') if c.strip()]
                profesores.append(Profesor(r['NOMBRE'], 0, r['CREDITOS'], es_graduado=True, clases_recibe=clases))

            # 2. Generar Secciones (Punto 2)
            secciones = []
            for _, r in df_cur.iterrows():
                cod, cupo_total = str(r['CODIGO']), int(r['CUPO'])
                conf = str(r.get('CANTIDAD_SECCIONES', ''))
                idx, cupo_actual = 1, 0
                
                if 'x' in conf.lower():
                    for p in conf.split(','):
                        cant, tam = p.lower().split('x')
                        for _ in range(int(cant)):
                            secciones.append(Seccion(f"{cod}-{idx:03d}", cod, r['CREDITOS'], int(tam), r['CANDIDATOS'], r.get('TIPO_SALON','GENERAL')))
                            cupo_actual += int(tam); idx += 1
                
                while cupo_actual < cupo_total:
                    secciones.append(Seccion(f"{cod}-{idx:03d}", cod, r['CREDITOS'], 30, r['CANDIDATOS'], r.get('TIPO_SALON','GENERAL')))
                    cupo_actual += 30; idx += 1

            salones = [type('S',(),{'codigo':str(r['CODIGO']), 'capacidad':int(r['CAPACIDAD']), 'tipo':str(r['TIPO']).upper()}) for _,r in df_sal.iterrows()]

            if st.button("🚀 GENERAR HORARIO MAESTRO", use_container_width=True):
                engine = PlatinumEngine(secciones, profesores, salones, zona)
                bar = st.progress(0)
                best, conflicts = engine.evolucionar(pop, gens, lambda g,t,f: bar.progress((g+1)/t))
                
                res = []
                for g in best:
                    b = engine.bloques[g.b_key]
                    res.append({'Sección': g.seccion.uid, 'Profesor': g.prof_nom, 'Días': "".join(b['dias']), 'Inicio': mins_to_str(b['inicio']), 'Salón': g.salon_obj.codigo})
                
                st.session_state.final_df = pd.DataFrame(res).sort_values('Sección')
                st.success(f"Horario Generado con {conflicts} conflictos.")

            if 'final_df' in st.session_state:
                st.dataframe(st.session_state.final_df, use_container_width=True, hide_index=True)
                
        except Exception as e:
            st.error(f"Error procesando el Excel: {e}")

if __name__ == "__main__": main()
