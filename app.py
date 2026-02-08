import streamlit as st
import pandas as pd
import numpy as np
import random
import io
import copy
from datetime import datetime

# ==============================================================================
# 1. ESTÉTICA PLATINUM ELITE
# ==============================================================================
st.set_page_config(page_title="UPRM Scheduler Platinum AI v3", page_icon="🏛️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Source+Code+Pro:wght@300;500&display=swap');
    .stApp { background: radial-gradient(circle at top, #1a1a1a 0%, #000000 100%); color: #e0e0e0; }
    h1, h2, h3 { font-family: 'Playfair Display', serif !important; color: #D4AF37 !important; text-align: center; text-shadow: 2px 2px 10px rgba(212, 175, 55, 0.3); }
    .glass-card { background: rgba(255, 255, 255, 0.03); border-radius: 15px; padding: 25px; border: 1px solid rgba(212, 175, 55, 0.2); backdrop-filter: blur(10px); margin-bottom: 20px; }
    .stButton>button { background: linear-gradient(135deg, #8E6E13 0%, #D4AF37 50%, #8E6E13 100%) !important; color: white !important; font-weight: bold !important; border-radius: 2px !important; width: 100%; }
    [data-testid="stSidebar"] { background-color: #050505; border-right: 1px solid #D4AF37; }
    .math-text { font-family: 'Source Code Pro', monospace; color: #B8860B; font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. UTILIDADES Y PLANTILLA (LIBRO GRADUADOS ACTUALIZADO)
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
        pd.DataFrame(columns=['CODIGO', 'CREDITOS', 'CANT_SECCIONES', 'CUPO', 'CANDIDATOS', 'TIPO_SALON']).to_excel(writer, sheet_name='Cursos', index=False)
        pd.DataFrame(columns=['Nombre', 'Carga_Min', 'Carga_Max', 'Pref_Dias', 'Pref_Horario']).to_excel(writer, sheet_name='Profesores', index=False)
        pd.DataFrame(columns=['CODIGO', 'CAPACIDAD', 'TIPO']).to_excel(writer, sheet_name='Salones', index=False)
        # NUEVO: Estructura para Graduados de Matemáticas
        pd.DataFrame(columns=['NOMBRE_GRADUADO', 'CREDITOS_A_DICTAR', 'CODIGOS_RECIBE']).to_excel(writer, sheet_name='Graduados', index=False)
    return output.getvalue()

# ==============================================================================
# 3. MOTOR IA (LÓGICA DE BLOQUEO MATEMÁTICO)
# ==============================================================================
class Seccion:
    def __init__(self, uid, creditos, cupo, candidatos, tipo_salon, es_ayudantia=False):
        self.uid, self.creditos = uid, creditos
        self.cupo, self.tipo_salon, self.cands = cupo, tipo_salon, candidatos
        self.es_ayudantia = es_ayudantia

class PlatinumGeneticEngine:
    def __init__(self, df_cursos, df_profes, df_salones, df_grad, zona, pop_size, generations):
        self.zona = zona
        self.pop_size = pop_size
        self.generations = generations
        self.salones = df_salones.to_dict('records')
        
        # Diccionario de Profesores
        self.profesores = {str(r['Nombre']).upper().strip(): {
            'min': r['Carga_Min'], 'max': r['Carga_Max'],
            'pref_dias': str(r['Pref_Dias']).strip(), 'pref_horario': str(r['Pref_Horario']).strip()
        } for _, r in df_profes.iterrows()}
        
        # Diccionario de Graduados (Solo para Matemáticas)
        self.graduados = {}
        for _, r in df_grad.iterrows():
            nombre = str(r['NOMBRE_GRADUADO']).upper().strip()
            clases_recibe = [c.strip().upper() for c in str(r['CODIGOS_RECIBE']).split(',') if c.strip()]
            self.graduados[nombre] = clases_recibe

        self.secciones = self._generar_secciones(df_cursos, df_grad)
        
        if zona == "CENTRAL":
            self.lim_inf, self.lim_sup, self.h_univ = 450, 1110, (630, 750)
        else:
            self.lim_inf, self.lim_sup, self.h_univ = 420, 1080, (600, 720)

    def _generar_secciones(self, df_c, df_g):
        oferta = []
        for _, r in df_c.iterrows():
            cands = [c.strip().upper() for c in str(r['CANDIDATOS']).split(',') if c.strip()]
            for i in range(int(r['CANT_SECCIONES'])):
                oferta.append(Seccion(f"{r['CODIGO']}-{i+1:02d}", r['CREDITOS'], r['CUPO'], cands, r['TIPO_SALON']))
        
        # Añadir Ayudantías de Graduados
        for _, r in df_g.iterrows():
            nombre = str(r['NOMBRE_GRADUADO']).upper().strip()
            oferta.append(Seccion(f"AYUD-{nombre[:3]}", r['CREDITOS_A_DICTAR'], 1, [nombre], "OFICINA", True))
        return oferta

    def fitness(self, cromosoma):
        penalizacion = 0
        oc_p, oc_s = {}, {}
        
        # Mapa rápido de horarios para verificar qué clases "recibe" el graduado
        horario_clases = {g['sec'].uid.split('-')[0]: g for g in cromosoma}
        
        for g in cromosoma:
            # 1. Bloqueo Universitario
            if "MaJu" in g['dias']:
                if max(g['ini'], self.h_univ[0]) < min(g['fin'], self.h_univ[1]): 
                    penalizacion += 100000
            
            # 2. RESTRICCIÓN OBLIGATORIA: Graduado recibiendo clase
            p_nom = g['prof']
            if p_nom in self.graduados:
                clases_que_toma = self.graduados[p_nom]
                for cod_clase in clases_que_toma:
                    if cod_clase in horario_clases:
                        clase_dictada = horario_clases[cod_clase]
                        # Si los días coinciden, verificar solapamiento entre la clase que da y la que recibe
                        dias_dan = set(["Lu", "Mi", "Vi"] if g['dias'] == "LuMiVi" else ["Ma", "Ju"])
                        dias_recibe = set(["Lu", "Mi", "Vi"] if clase_dictada['dias'] == "LuMiVi" else ["Ma", "Ju"])
                        
                        if dias_dan.intersection(dias_recibe):
                            if max(g['ini'], clase_dictada['ini']) < min(g['fin'], clase_dictada['fin']):
                                penalizacion += 500000 # Penalidad máxima: No puede estar en dos sitios

            # 3. Colisiones de Profesores y Salones
            d_list = ["Lu", "Mi", "Vi"] if g['dias'] == "LuMiVi" else ["Ma", "Ju"]
            for d in d_list:
                for t in range(g['ini'], g['fin'], 10):
                    pk, sk = (g['prof'], d, t), (g['salon'], d, t)
                    if pk in oc_p and g['prof'] != "TBA": penalizacion += 10000
                    if sk in oc_s and g['salon'] != "TBA": penalizacion += 10000
                    oc_p[pk] = oc_s[sk] = True
                    
        return 1 / (1 + penalizacion)

    def evolucionar(self):
        pob = [self.generar_individuo() for _ in range(self.pop_size)]
        bar = st.progress(0)
        for gen in range(self.generations):
            pob.sort(key=self.fitness, reverse=True)
            nueva_gen = pob[:2]
            while len(nueva_gen) < self.pop_size:
                p1, p2 = random.sample(pob[:10], 2)
                punto = len(p1)//2
                hijo = p1[:punto] + p2[punto:]
                nueva_gen.append(hijo)
            pob = nueva_gen
            bar.progress((gen + 1) / self.generations)
        return pob[0]

    def generar_individuo(self):
        ind = []
        for sec in self.secciones:
            prof = random.choice(sec.cands) if sec.cands else "TBA"
            sal_filtrados = [s for s in self.salones if s['CAPACIDAD'] >= sec.cupo]
            salon = random.choice(sal_filtrados)['CODIGO'] if sal_filtrados else "TBA"
            es_mj = (sec.creditos == 4 or random.random() > 0.5)
            dias, dur = ("MaJu", 80) if es_mj else ("LuMiVi", 50)
            h_ini = random.randrange(self.lim_inf, self.lim_sup - dur, 30)
            ind.append({'sec': sec, 'prof': prof, 'salon': salon, 'ini': h_ini, 'fin': h_ini + dur, 'dias': dias})
        return ind

# ==============================================================================
# 4. UI
# ==============================================================================
def main():
    st.markdown("<h1>🏛️ PLATINUM SCHEDULER AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#888;'>Specialized for Mathematics Graduate Program</p>", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### $\Sigma$ Configuración")
        zona = st.selectbox("Zona Campus", ["CENTRAL", "PERIFERICA"])
        pop = st.slider("Población", 20, 100, 50)
        gens = st.slider("Generaciones", 50, 500, 100)
        file = st.file_uploader("Subir Protocolo Excel", type=['xlsx'])

    if not file:
        st.markdown("<div class='glass-card' style='text-align: center;'><h3>📥 Plantilla con Bloqueo de Graduados</h3></div>", unsafe_allow_html=True)
        st.download_button("DESCARGAR PLANTILLA V3.2", crear_excel_guia(), "Plantilla_Matematicas_UPRM.xlsx", use_container_width=True)
    else:
        xls = pd.ExcelFile(file)
        if st.button("🚀 INICIAR OPTIMIZACIÓN"):
            engine = PlatinumGeneticEngine(pd.read_excel(xls, 'Cursos'), pd.read_excel(xls, 'Profesores'), pd.read_excel(xls, 'Salones'), pd.read_excel(xls, 'Graduados'), zona, pop, gens)
            mejor = engine.evolucionar()
            st.session_state.master = pd.DataFrame([{
                'ID': g['sec'].uid, 'Persona': g['prof'], 
                'Días': g['dias'], 'Horario': f"{mins_to_str(g['ini'])} - {mins_to_str(g['fin'])}",
                'Salón': g['salon']
            } for g in mejor])

    if 'master' in st.session_state:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.data_editor(st.session_state.master, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
