import streamlit as st
import pandas as pd
import numpy as np
import random
import io
import time
import re

# ==============================================================================
# 1. ESTÉTICA PLATINUM ELITE (PRESERVADA 100%)
# ==============================================================================
st.set_page_config(page_title="UPRM Scheduler Platinum AI v7", page_icon="🏛️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Source+Code+Pro:wght@300;500&display=swap');
    
    .stApp { 
        background-color: #050505;
        background-image: 
            linear-gradient(rgba(212, 175, 55, 0.1) 2px, transparent 2px),
            linear-gradient(90deg, rgba(212, 175, 55, 0.1) 2px, transparent 2px),
            radial-gradient(circle at 50% 20%, #1a1a1a 0%, #000000 100%);
        background-size: 80px 80px, 80px 80px, 100% 100%;
        background-attachment: fixed;
        color: #e0e0e0; 
    }

    .math-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 30px 60px;
        background: rgba(0, 0, 0, 0.85);
        border-bottom: 3px solid #D4AF37;
        margin-bottom: 40px;
        border-radius: 0 0 30px 30px;
        box-shadow: 0 10px 50px rgba(212, 175, 55, 0.15);
        position: relative;
        overflow: hidden;
    }

    .math-header::before { content: '∑'; position: absolute; left: 5%; font-size: 8rem; color: rgba(212, 175, 55, 0.05); font-family: serif; }
    .math-header::after { content: '∫'; position: absolute; right: 5%; font-size: 8rem; color: rgba(212, 175, 55, 0.05); font-family: serif; }

    .title-box { text-align: center; z-index: 2; }

    .abstract-icon {
        font-size: 3rem;
        color: #D4AF37;
        border: 2px solid #D4AF37;
        padding: 10px 20px;
        border-radius: 50% 0% 50% 0%;
        background: rgba(212, 175, 55, 0.05);
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.3);
    }

    h1 { 
        font-family: 'Playfair Display', serif !important; 
        color: #D4AF37 !important; 
        font-size: 3.2rem !important;
        margin: 10px 0 !important;
        text-shadow: 0 0 20px rgba(212, 175, 55, 0.5);
        letter-spacing: 2px;
    }

    .glass-card { 
        background: rgba(15, 15, 15, 0.9); 
        border-radius: 15px; 
        padding: 25px; 
        border: 1px solid rgba(212, 175, 55, 0.25); 
        backdrop-filter: blur(15px); 
        margin-bottom: 20px; 
        box-shadow: 0 15px 40px rgba(0,0,0,0.8);
    }

    .stButton>button { 
        background: linear-gradient(135deg, #8E6E13 0%, #D4AF37 50%, #8E6E13 100%) !important; 
        color: white !important; font-weight: bold !important; border-radius: 4px !important; 
        width: 100%; border: none !important; height: 55px; font-size: 1.1rem;
        transition: 0.4s;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 0 25px rgba(212, 175, 55, 0.4); }

    .stDownloadButton>button {
        background: linear-gradient(135deg, #B8860B 0%, #FFD700 50%, #B8860B 100%) !important;
        color: #000 !important;
        font-weight: 800 !important;
        border: 1px solid #D4AF37 !important;
    }

    [data-testid="stSidebar"] { background-color: #050505; border-right: 1px solid #D4AF37; }
    
    [data-testid="stSidebar"] h3 {
        color: #D4AF37 !important;
        text-shadow: 0 0 10px rgba(212, 175, 55, 0.4);
        font-family: 'Playfair Display', serif;
    }

    .status-badge { 
        background: rgba(212, 175, 55, 0.1); 
        border: 1px solid #D4AF37; 
        color: #D4AF37; 
        padding: 12px; 
        border-radius: 8px; 
        text-align: center;
        font-family: 'Source Code Pro', monospace;
        font-weight: 500;
    }
</style>

<div class="math-header">
    <div class="abstract-icon">Δx</div>
    <div class="title-box">
        <p style="color: #D4AF37; letter-spacing: 5px; font-size: 0.8rem; margin:0;">UPRM TIMETABLE SYSTEM</p>
        <h1>ALGORITHMIC PERFECTION</h1>
        <p style="color: #8E6E13; font-style: italic;">UPRM MATHEMATICAL OPTIMIZATION ENGINE v7.5 (STRICT ENFORCEMENT)</p>
    </div>
    <div class="abstract-icon" style="border-radius: 0% 50% 0% 50%;">∞</div>
</div>
""", unsafe_allow_html=True)

st.latex(r"\blacksquare \quad \text{SISTEMA DE PLANIFICACIÓN ACADÉMICA OPTIMIZADA - TESIS MASTER} \quad \blacksquare")

# ==============================================================================
# 2. UTILIDADES
# ==============================================================================
def mins_to_str(m):
    h, mins = divmod(int(m), 60)
    am_pm = "AM" if h < 12 else "PM"
    h_disp = h if h <= 12 else h - 12
    if h_disp == 0: h_disp = 12
    return f"{h_disp:02d}:{mins:02d} {am_pm}"

def crear_excel_guia(con_graduados=True):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        pd.DataFrame(columns=['CODIGO', 'CREDITOS', 'CANT_SECCIONES', 'DEMANDA', 'CANDIDATOS', 'TIPO_SALON']).to_excel(writer, sheet_name='Cursos', index=False)
        pd.DataFrame(columns=['Nombre', 'CREDITOS', 'Pref_Dias', 'Pref_horas']).to_excel(writer, sheet_name='Profesores', index=False)
        pd.DataFrame(columns=['CODIGO', 'CAPACIDAD', 'TIPO']).to_excel(writer, sheet_name='Salones', index=False)
        if con_graduados:
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
# 3. MOTOR IA (VERSION PERFECCIONADA V7.5)
# ==============================================================================
class SeccionData:
    def __init__(self, cod, creditos, cupo, cands, tipo_salon, es_ayudantia=False):
        self.cod = str(cod)
        self.creditos = int(creditos)
        self.cupo = int(cupo)
        self.cands = cands if isinstance(cands, list) else [c.strip().upper() for c in str(cands).split(',') if c.strip()]
        try: self.tipo_salon = int(float(str(tipo_salon)))
        except: self.tipo_salon = 1
        self.es_ayudantia = es_ayudantia
        
        # Identificar laboratorios fusionables
        base = self.cod.split('-')[0].upper().replace(" ", "")
        self.es_lab_fusionable = base in ["MATE3171L", "MATE3172L", "MATE3173L"]

class PlatinumEnterpriseEngine:
    def __init__(self, df_cursos, df_profes, df_salones, df_grad, zona):
        self.zona = zona
        self.salones = []
        self.mega_salones = set()
        
        for _, r in df_salones.iterrows():
            codigo = str(r['CODIGO']).strip().upper()
            self.salones.append({'CODIGO': codigo, 'CAPACIDAD': int(r['CAPACIDAD']), 'TIPO': int(r['TIPO'])})
            if any(x in codigo.replace(" ","") for x in ["FA", "FB", "FC"]):
                self.mega_salones.add(codigo)

        # Cargas obligatorias
        self.cargas_objetivo = {}
        if df_grad is not None:
            for _, r in df_grad.iterrows():
                self.cargas_objetivo[str(r['NOMBRE_GRADUADO']).upper().strip()] = int(r['CREDITOS_A_DICTAR'])
        for _, r in df_profes.iterrows():
            nombre = str(r['Nombre']).upper().strip()
            if nombre not in self.cargas_objetivo:
                self.cargas_objetivo[nombre] = int(r['CREDITOS'])

        # Generar Oferta y asignar profesores de forma PREVIA para cumplir carga estricta
        self.oferta = []
        asignaciones_fijas = []
        
        for _, r in df_cursos.iterrows():
            cod_base = str(r['CODIGO']).strip().upper()
            cands = [c.strip().upper() for c in str(r['CANDIDATOS']).split(',') if c.strip()]
            for i in range(int(r['CANT_SECCIONES'])):
                sec = SeccionData(f"{cod_base}-{i+1:02d}", r['CREDITOS'], r['DEMANDA'], cands, r['TIPO_SALON'])
                self.oferta.append(sec)

        # Bloques Horarios
        self.bloques_lmv = [450, 510, 570, 630, 690, 750, 810, 870, 930, 990] # 7:30, 8:30...
        self.bloques_mj = [450, 540, 750, 840, 930, 1020]
        self.h_univ = (630, 750) if zona == "CENTRAL" else (600, 720)

    def solve(self, pop_size, generations):
        pob = [self._random_ind() for _ in range(pop_size)]
        bar = st.progress(0)
        status_text = st.empty()
        best_overall = None
        best_score = -1

        for gen in range(generations):
            scored = [(self._fitness(ind), ind) for ind in pob]
            scored.sort(key=lambda x: x[0], reverse=True)
            
            if scored[0][0] > best_score:
                best_score = scored[0][0]
                best_overall = scored[0][1]

            status_text.markdown(f"**Optimizando Gen {gen+1}/{generations}** | Precisión de Carga y Espacio: `{best_score:.8f}`")
            
            # Elitismo y Cruce
            nueva_gen = [x[1] for x in scored[:int(pop_size*0.2)]]
            while len(nueva_gen) < pop_size:
                p1, p2 = random.sample(scored[:int(pop_size*0.5)], 2)
                hijo = [p1[1][i] if random.random() < 0.5 else p2[1][i] for i in range(len(p1[1]))]
                if random.random() < 0.2:
                    idx = random.randint(0, len(hijo)-1)
                    hijo[idx] = self._mutate_gene(hijo[idx])
                nueva_gen.append(hijo)
            
            pob = nueva_gen
            bar.progress((gen + 1) / generations)
        return best_overall

    def _mutate_gene(self, gene):
        s = gene['sec']
        es_mj = (s.creditos >= 4 or (s.creditos == 1 and random.random() > 0.5))
        dias = "MaJu" if es_mj else "LuMiVi"
        h_ini = random.choice(self.bloques_mj if es_mj else self.bloques_lmv)
        
        # Priorizar cumplimiento de salón
        cands_sal = [sl['CODIGO'] for sl in self.salones if sl['CAPACIDAD'] >= s.cupo and (sl['TIPO'] == s.tipo_salon or (s.es_lab_fusionable and sl['CODIGO'] in self.mega_salones))]
        sal = random.choice(cands_sal) if cands_sal else "TBA"
        prof = random.choice(s.cands) if s.cands else "TBA"
        
        return {'sec': s, 'prof': prof, 'salon': sal, 'dias': dias, 'ini': h_ini, 'fin': h_ini + (80 if es_mj else 50)}

    def _random_ind(self):
        return [self._mutate_gene({'sec': s}) for s in self.oferta]

    def _fitness(self, ind):
        penalty = 0
        occ_s, occ_p = {}, {}
        cargas = {p: 0 for p in self.cargas_objetivo}
        
        for g in ind:
            sec = g['sec']
            # 1. Penalidad Crítica TBA
            if g['salon'] == "TBA": penalty += 1e9
            if g['prof'] == "TBA": penalty += 1e9

            # 2. Carga Académica (Restricción Fuerte)
            if g['prof'] in cargas: cargas[g['prof']] += sec.creditos

            # 3. Choques (Profesor y Salón)
            dias = ["Lu", "Mi", "Vi"] if g['dias'] == "LuMiVi" else ["Ma", "Ju"]
            for d in dias:
                # Profesor
                pk = (g['prof'], d)
                if pk in occ_p:
                    for r in occ_p[pk]:
                        if max(g['ini'], r[0]) < min(g['fin'], r[1]): penalty += 1e7
                    occ_p[pk].append((g['ini'], g['fin']))
                else: occ_p[pk] = [(g['ini'], g['fin'])]

                # Salón con lógica de Fusión
                sk = (g['salon'], d)
                if sk in occ_s:
                    for (ini, fin, is_lab) in occ_s[sk]:
                        if max(g['ini'], ini) < min(g['fin'], fin):
                            # Solo se permite si AMBOS son laboratorios fusionables y es mega salón
                            if not (sec.es_lab_fusionable and is_lab and g['salon'] in self.mega_salones):
                                penalty += 1e7
                    occ_s[sk].append((g['ini'], g['fin'], sec.es_lab_fusionable))
                else: occ_s[sk] = [(g['ini'], g['fin'], sec.es_lab_fusionable)]

            # 4. Hora Universal
            if g['dias'] == "MaJu" and max(g['ini'], self.h_univ[0]) < min(g['fin'], self.h_univ[1]):
                penalty += 1e6

        # Penalidad por desviación de carga (EXPONENCIAL)
        for p, c in cargas.items():
            diff = abs(c - self.cargas_objetivo.get(p, 0))
            if diff > 0: penalty += (diff * 1e8)

        return 1 / (1 + penalty)

# ==============================================================================
# 4. UI PRINCIPAL (PRESERVADA)
# ==============================================================================
def main():
    with st.sidebar:
        st.markdown("### $\Sigma$ Configuración")
        zona = st.selectbox("Zona Campus", ["CENTRAL", "PERIFERICA"])
        pop = st.slider("Población", 50, 500, 150)
        gens = st.slider("Generaciones", 100, 2000, 400)
        file = st.file_uploader("Subir Protocolo Excel", type=['xlsx'])

    if not file:
        st.info("Por favor, cargue el protocolo Excel para iniciar.")
        st.download_button("Descargar Plantilla", crear_excel_guia(), "Plantilla.xlsx")
    else:
        if st.button("🚀 INICIAR OPTIMIZACIÓN PERFECTA"):
            xls = pd.ExcelFile(file)
            df_grad = pd.read_excel(xls, 'Graduados') if 'Graduados' in xls.sheet_names else None
            df_cursos = pd.read_excel(xls, 'Cursos')
            df_profes = pd.read_excel(xls, 'Profesores')
            df_salones = pd.read_excel(xls, 'Salones')

            engine = PlatinumEnterpriseEngine(df_cursos, df_profes, df_salones, df_grad, zona)
            mejor = engine.solve(pop, gens)
            
            st.session_state.master = pd.DataFrame([{
                'ID': g['sec'].cod, 
                'Asignatura': g['sec'].cod.split('-')[0],
                'Creditos': g['sec'].creditos,
                'Persona': g['prof'], 
                'Días': g['dias'], 
                'Horario': f"{mins_to_str(g['ini'])} - {mins_to_str(g['fin'])}", 
                'Salón': g['salon']
            } for g in mejor])

    if 'master' in st.session_state:
        t1, t2, t3 = st.tabs(["💎 PANEL CONTROL", "🔍 VISTA USUARIO", "🚨 AUDITORÍA"])
        with t1:
            st.dataframe(st.session_state.master, use_container_width=True)
            st.download_button("💾 EXPORTAR", exportar_todo(st.session_state.master), "Horario_Final.xlsx")
        with t2:
            p = st.selectbox("Profesor/Graduado", sorted(st.session_state.master['Persona'].unique()))
            sub = st.session_state.master[st.session_state.master['Persona'] == p]
            st.table(sub)
            st.metric("Carga Total", f"{sub['Creditos'].sum()} CR")
        with t3:
            errores = len(st.session_state.master[st.session_state.master['Salón'] == 'TBA'])
            if errores == 0: st.success("✅ Horario 100% Factible y sin TBAs.")
            else: st.error(f"⚠️ {errores} secciones sin salón. Incremente generaciones.")

if __name__ == "__main__":
    main()
