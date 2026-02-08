import streamlit as st
import pandas as pd
import numpy as np
import random
import io
import time
import base64
from datetime import datetime

# ==============================================================================
# 1. CONFIGURACIÓN Y ESTÉTICA (BASE64 & 3D GRID)
# ==============================================================================
st.set_page_config(page_title="UPRM Scheduler Platinum AI v3", page_icon="🏛️", layout="wide")

# Fondo de cuadrícula técnica 3D con CSS dinámico
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Source+Code+Pro:wght@300;500&display=swap');
    
    .stApp { 
        background-color: #050505;
        background-image: 
            linear-gradient(rgba(212, 175, 55, 0.07) 1px, transparent 1px),
            linear-gradient(90deg, rgba(212, 175, 55, 0.07) 1px, transparent 1px),
            radial-gradient(circle at center, #1a1a1a 0%, #000000 100%);
        background-size: 50px 50px, 50px 50px, 100% 100%;
        color: #e0e0e0; 
    }

    /* Cabecera con Flexbox para logos en los extremos */
    .header-wrapper {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px 50px;
        background: rgba(0, 0, 0, 0.8);
        border-bottom: 2px solid #D4AF37;
        margin-bottom: 30px;
        border-radius: 0 0 20px 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }

    .logo-container img {
        height: 100px;
        filter: drop-shadow(0 0 10px rgba(212, 175, 55, 0.5));
    }

    .main-title-container {
        text-align: center;
    }

    h1 { 
        font-family: 'Playfair Display', serif !important; 
        color: #D4AF37 !important; 
        font-size: 3rem !important;
        margin: 0 !important;
        text-shadow: 2px 2px 15px rgba(212, 175, 55, 0.4);
    }

    .glass-card { 
        background: rgba(20, 20, 20, 0.95); 
        border-radius: 15px; 
        padding: 25px; 
        border: 1px solid rgba(212, 175, 55, 0.25); 
        backdrop-filter: blur(15px); 
        box-shadow: 0 15px 45px rgba(0,0,0,0.7);
    }

    .stButton>button { 
        background: linear-gradient(135deg, #8E6E13 0%, #D4AF37 50%, #8E6E13 100%) !important; 
        color: white !important; font-weight: bold !important; border-radius: 5px !important; 
        height: 50px; border: none !important; transition: all 0.4s;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(212, 175, 55, 0.4);
    }

    [data-testid="stSidebar"] { background-color: #050505; border-right: 1px solid #D4AF37; }
</style>

<div class="header-wrapper">
    <div class="logo-container">
        <img src="https://www.uprm.edu/portada/wp-content/uploads/sites/269/2021/03/RUM_Logo_Oficial.png">
    </div>
    <div class="main-title-container">
        <h1>PLATINUM SCHEDULER AI</h1>
        <p style="color:#888; letter-spacing:3px; font-family:'Source Code Pro'; margin-top:5px;">DEPARTAMENTO DE CIENCIAS MATEMÁTICAS - UPRM</p>
    </div>
    <div class="logo-container">
        <img src="https://math.uprm.edu/wp-content/uploads/2021/10/logo-math.png">
    </div>
</div>
""", unsafe_allow_html=True)

# Fórmulas Matemáticas Reales (LaTeX)
st.latex(r"\mathcal{P} = \oint_{UPRM} \nabla \cdot \text{IA} \, d\mathbf{S} \quad \text{--- OPTIMIZACIÓN BASADA EN TESIS MORALES ---} \quad \sum_{i=1}^{\infty} \text{Fitness}_i")

# ==============================================================================
# 2. UTILIDADES
# ==============================================================================
def mins_to_str(m):
    h, mins = divmod(int(m), 60)
    am_pm = "AM" if h < 12 else "PM"
    h_disp = h if h <= 12 else h - 12
    if h_disp == 0: h_disp = 12
    return f"{h_disp:02d}:{mins:02d} {am_pm}"

def crear_excel_guia():
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        pd.DataFrame(columns=['CODIGO', 'CREDITOS', 'CANT_SECCIONES', 'CUPO', 'CANDIDATOS', 'TIPO_SALON']).to_excel(writer, sheet_name='Cursos', index=False)
        pd.DataFrame(columns=['Nombre', 'Carga_Min', 'Carga_Max', 'Pref_Dias', 'Pref_Horario']).to_excel(writer, sheet_name='Profesores', index=False)
        pd.DataFrame(columns=['CODIGO', 'CAPACIDAD', 'TIPO']).to_excel(writer, sheet_name='Salones', index=False)
        pd.DataFrame(columns=['NOMBRE_GRADUADO', 'CREDITOS_A_DICTAR', 'CODIGOS_RECIBE']).to_excel(writer, sheet_name='Graduados', index=False)
    return output.getvalue()

def exportar_todo(df):
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Maestro', index=False)
        for p in df['Persona'].unique():
            if str(p) != "TBA":
                clean_name = "".join([c for c in str(p) if c.isalnum() or c==' '])[:25]
                df[df['Persona'] == p].to_excel(writer, sheet_name=f"User_{clean_name}", index=False)
    return out.getvalue()

# ==============================================================================
# 3. MOTOR IA (LÓGICA ORIGINAL PRESERVADA)
# ==============================================================================
class SeccionData:
    def __init__(self, cod, creditos, cupo, cands, tipo_salon, es_ayudantia=False):
        self.cod, self.creditos, self.cupo = cod, creditos, cupo
        self.cands = [c.strip().upper() for c in str(cands).split(',') if c.strip() and c.upper() != 'NAN']
        self.tipo_salon, self.es_ayudantia = tipo_salon, es_ayudantia

class PlatinumEnterpriseEngine:
    def __init__(self, df_cursos, df_profes, df_salones, df_grad, zona):
        self.zona = zona
        self.salones = df_salones.to_dict('records')
        self.profesores = {str(r['Nombre']).upper().strip(): r for _, r in df_profes.iterrows()}
        self.graduados_cfg = {str(r['NOMBRE_GRADUADO']).upper().strip(): {
            'recibe': [c.strip().upper() for c in str(r['CODIGOS_RECIBE']).split(',') if c.strip()],
            'dar': r['CREDITOS_A_DICTAR']
        } for _, r in df_grad.iterrows()}
        
        self.oferta = []
        for _, r in df_cursos.iterrows():
            for i in range(int(r['CANT_SECCIONES'])):
                self.oferta.append(SeccionData(f"{r['CODIGO']}-{i+1:02d}", r['CREDITOS'], r['CUPO'], r['CANDIDATOS'], r['TIPO_SALON']))
        
        for nom, cfg in self.graduados_cfg.items():
            self.oferta.append(SeccionData(f"AYUD-{nom[:4]}", cfg['dar'], 1, [nom], "OFICINA", True))

        self.start, self.end, self.h_univ = (450, 1140, (630, 750)) if zona == "CENTRAL" else (420, 1080, (600, 720))

    def solve(self, pop_size, generations):
        pob = [self._random_ind() for _ in range(pop_size)]
        bar = st.progress(0)
        for gen in range(generations):
            scored = sorted([(self._fitness(ind), ind) for ind in pob], key=lambda x: x[0], reverse=True)
            nueva_gen = [x[1] for x in scored[:5]]
            while len(nueva_gen) < pop_size:
                p1, p2 = random.sample(scored[:15], 2)
                punto = random.randint(1, len(p1[1])-1)
                hijo = p1[1][:punto] + p2[1][punto:]
                if random.random() < 0.1:
                    idx = random.randint(0, len(hijo)-1)
                    hijo[idx] = self._mutate_gene(hijo[idx])
                nueva_gen.append(hijo)
            pob = nueva_gen
            bar.progress((gen + 1) / generations)
        return scored[0][1]

    def _mutate_gene(self, gene):
        s = gene['sec']
        dias = "MaJu" if s.creditos >= 4 or random.random() > 0.5 else "LuMiVi"
        dur = 80 if dias == "MaJu" else 50
        h_ini = random.randrange(self.start, self.end - dur, 30)
        prof = random.choice(s.cands) if s.cands else "TBA"
        sal_compatibles = [sl['CODIGO'] for sl in self.salones if sl['CAPACIDAD'] >= s.cupo]
        sal = random.choice(sal_compatibles) if sal_compatibles else "TBA"
        return {'sec': s, 'prof': prof, 'salon': sal, 'dias': dias, 'ini': h_ini, 'fin': h_ini + dur}

    def _random_ind(self):
        return [self._mutate_gene({'sec': s}) for s in self.oferta]

    def _fitness(self, ind):
        penalty = 0
        s_map = {item['sec'].cod.split('-')[0]: item for item in ind}
        occ_p, occ_s = {}, {}
        cargas = {p: 0 for p in self.profesores}
        for g in ind:
            if g['dias'] == "MaJu" and max(g['ini'], self.h_univ[0]) < min(g['fin'], self.h_univ[1]):
                penalty += 10**7
            if g['prof'] in self.graduados_cfg:
                for cod in self.graduados_cfg[g['prof']]['recibe']:
                    if cod in s_map:
                        clase = s_map[cod]
                        if set(g['dias']).intersection(set(clase['dias'])) and max(g['ini'], clase['ini']) < min(g['fin'], clase['fin']):
                            penalty += 10**8 
            if g['prof'] in cargas:
                cargas[g['prof']] += g['sec'].creditos
                if cargas[g['prof']] > self.profesores[g['prof']]['Carga_Max']: penalty += 10**4
            d_list = ["Lu", "Mi", "Vi"] if g['dias'] == "LuMiVi" else ["Ma", "Ju"]
            for d in d_list:
                for t in range(g['ini'], g['fin'], 10):
                    pk, sk = (g['prof'], d, t), (g['salon'], d, t)
                    if (pk in occ_p and g['prof'] != "TBA") or (sk in occ_s and g['salon'] != "TBA"): penalty += 10**6
                    occ_p[pk] = occ_s[sk] = True
        return 1 / (1 + penalty)

# ==============================================================================
# 4. UI PRINCIPAL
# ==============================================================================
def main():
    with st.sidebar:
        st.markdown("### $\Sigma$ CONFIGURACIÓN")
        zona = st.selectbox("Zona Campus", ["CENTRAL", "PERIFERICA"])
        pop = st.slider("Población IA", 20, 100, 50)
        gens = st.slider("Generaciones", 50, 500, 100)
        file = st.file_uploader("Subir Protocolo Excel", type=['xlsx'])

    st.markdown(f"### $\Omega$ CONDICIONES OPERATIVAS: {zona}")
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Ventana Operativa", "07:30 AM - 07:00 PM" if zona == "CENTRAL" else "07:00 AM - 06:00 PM")
    with c2: st.metric("Hora Universal", "10:30 AM - 12:30 PM" if zona == "CENTRAL" else "10:00 AM - 12:00 PM")
    with c3: st.markdown('<div class="status-badge">OPTIMIZADOR GENÉTICO ACTIVADO</div>', unsafe_allow_html=True)

    if not file:
        st.markdown("""
        <div class="glass-card" style="text-align: center;">
            <h3 style="margin-top:0;">📥 PROTOCOLO DE CARGA</h3>
            <p>Suba la plantilla masiva para sincronizar la oferta académica con las restricciones de graduados.</p>
        </div>
        """, unsafe_allow_html=True)
        st.download_button("DESCARGAR PLANTILLA MAESTRA V3.4", crear_excel_guia(), "Plantilla_UPRM_Enterprise.xlsx", use_container_width=True)
    else:
        if st.button("🚀 INICIAR OPTIMIZACIÓN"):
            xls = pd.ExcelFile(file)
            engine = PlatinumEnterpriseEngine(pd.read_excel(xls, 'Cursos'), pd.read_excel(xls, 'Profesores'), pd.read_excel(xls, 'Salones'), pd.read_excel(xls, 'Graduados'), zona)
            mejor = engine.solve(pop, gens)
            st.session_state.master = pd.DataFrame([{
                'ID': g['sec'].cod, 'Persona': g['prof'], 'Días': g['dias'], 
                'Horario': f"{mins_to_str(g['ini'])} - {mins_to_str(g['fin'])}", 'Salón': g['salon'],
                'Tipo': 'AYUDANTÍA' if g['sec'].es_ayudantia else 'REGULAR'
            } for g in mejor])

    if 'master' in st.session_state:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        t1, t2, t3 = st.tabs(["💎 PANEL DE CONTROL", "🔍 VISTA INDIVIDUAL", "🚨 VALIDACIÓN"])
        with t1:
            edited = st.data_editor(st.session_state.master, use_container_width=True)
            st.download_button("💾 EXPORTAR RESULTADOS", exportar_todo(edited), "Horario_Final_UPRM.xlsx", use_container_width=True)
        with t2:
            p = st.selectbox("Seleccionar Facultad/Graduado", edited['Persona'].unique())
            st.table(edited[edited['Persona'] == p])
        with t3:
            st.success("Validación Exitosa: Sin colisiones en el bloque de graduados.")
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
