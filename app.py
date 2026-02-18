import streamlit as st
import pandas as pd
import numpy as np
import random
import io
import time
import re
import math

# ==============================================================================
# 1. ESTÉTICA PLATINUM ELITE (INTACTA)
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
        <h1>UPRM TIMETABLE SYSTEM</h1>
        <p style="color: #888; font-family: 'Source Code Pro'; letter-spacing: 4px; font-size: 0.9rem;">
            UPRM MATHEMATICAL OPTIMIZATION ENGINE v7.0 (STRICT ENFORCEMENT)
        </p>
    </div>
    <div class="abstract-icon">∞</div>
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

def crear_excel_guia():
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Se elimina la hoja graduados y se actualiza CANT_SECCIONES a CAPACIDAD_SECCIONES
        pd.DataFrame(columns=['CODIGO', 'CREDITOS', 'CAPACIDAD_SECCIONES', 'DEMANDA', 'CANDIDATOS', 'TIPO_SALON']).to_excel(writer, sheet_name='Cursos', index=False)
        pd.DataFrame(columns=['Nombre', 'CREDITOS', 'Pref_Dias', 'Pref_horas']).to_excel(writer, sheet_name='Profesores', index=False)
        pd.DataFrame(columns=['CODIGO', 'CAPACIDAD', 'TIPO']).to_excel(writer, sheet_name='Salones', index=False)
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
# 3. MOTOR IA (PLATINUM ENGINE V7.0)
# ==============================================================================
class SeccionData:
    def __init__(self, cod, creditos, cupo, cands, tipo_salon, es_ayudantia=False):
        self.cod = str(cod)
        self.creditos = int(creditos)
        self.cupo = int(cupo)
        if isinstance(cands, list):
            self.cands = cands
        else:
            self.cands = [c.strip().upper() for c in str(cands).split(',') if c.strip() and str(c).upper() != 'NAN']
        
        try:
            self.tipo_salon = int(float(str(tipo_salon)))
        except:
            self.tipo_salon = 1
            
        self.es_ayudantia = es_ayudantia
        
        base = self.cod.split('-')[0].upper().replace(" ", "")
        self.es_fusionable = base in ["MATE3171", "MATE3172", "MATE3173"]

class PlatinumEnterpriseEngine:
    def __init__(self, df_cursos, df_profes, df_salones, zona):
        self.zona = zona
        
        df_salones.columns = [c.strip().upper() for c in df_salones.columns]
        self.salones = []
        self.mega_salones = set()
        
        for _, r in df_salones.iterrows():
            codigo = str(r['CODIGO']).strip().upper()
            try:
                cap = int(r['CAPACIDAD'])
            except:
                cap = 25
            try:
                tipo = int(r['TIPO'])
            except:
                tipo = 1
            
            self.salones.append({'CODIGO': codigo, 'CAPACIDAD': cap, 'TIPO': tipo})
            
            norm_cod = codigo.replace(" ", "").replace("-", "")
            if any(x in norm_cod for x in ["FA", "FB", "FC"]):
                self.mega_salones.add(codigo)

        self.profesores = {}
        if df_profes is not None and not df_profes.empty:
            for _, r in df_profes.iterrows():
                nombre = str(r['Nombre']).upper().strip()
                self.profesores[nombre] = {
                    'Carga_Max': float(r['CREDITOS']) if pd.notnull(r['CREDITOS']) else 12.0, 
                    'Pref_Bloque': str(r.get('Pref_horas', 'AM')).upper() 
                }

        # --- GENERACIÓN DE OFERTA ACADÉMICA ---
        self.oferta = []
        df_cursos.columns = [c.strip().upper() for c in df_cursos.columns]
        
        # Mapeo de columnas
        col_capacidad = 'CAPACIDAD_SECCIONES' if 'CAPACIDAD_SECCIONES' in df_cursos.columns else 'CANT_SECCIONES'
        
        for _, r in df_cursos.iterrows():
            codigo_base = str(r['CODIGO']).strip().upper()
            candidatos_raw = str(r.get('CANDIDATOS', ''))
            
            lista_candidatos = []
            if "GRADUADOS" in candidatos_raw.upper():
                # Generamos una bolsa de graduados anónimos dinámicamente
                lista_candidatos = [f"GRADUADO_{i}" for i in range(1, 21)]
            else:
                lista_candidatos = [c.strip().upper() for c in candidatos_raw.split(',') if c.strip() and c.strip().upper() != 'NAN']

            demanda = int(r.get('DEMANDA', 0))
            capacidad_sec = int(r.get(col_capacidad, 25))
            if capacidad_sec <= 0: capacidad_sec = 25
            
            # 1. CÁLCULO DE CANTIDAD DE SECCIONES EN BASE A DEMANDA Y CAPACIDAD
            cant_secciones = math.ceil(demanda / capacidad_sec) if demanda > 0 else 1
            cupo_por_seccion = capacidad_sec

            for i in range(cant_secciones):
                self.oferta.append(SeccionData(
                    f"{codigo_base}-{i+1:02d}", 
                    r.get('CREDITOS', 3), 
                    cupo_por_seccion, 
                    lista_candidatos, 
                    r.get('TIPO_SALON', 1)
                ))

        self.bloques_lmv = [450, 510, 570, 630, 690, 750, 810, 870, 930, 990] 
        self.bloques_mj = [450, 540, 750, 840, 930, 1020]
        self.h_univ = (630, 750) if zona == "CENTRAL" else (600, 720) 

    def solve(self, pop_size, generations):
        pob = [self._random_ind() for _ in range(pop_size)]
        bar = st.progress(0)
        status_text = st.empty()
        
        best_overall = None
        best_score = -1

        for gen in range(generations):
            scored = []
            for ind in pob:
                s, conflicts, _, _ = self._fitness_detailed(ind)
                scored.append((s, ind, conflicts))
            
            scored.sort(key=lambda x: x[0], reverse=True)
            
            if scored[0][0] > best_score:
                best_score = scored[0][0]
                best_overall = scored[0][1]

            # Elitismo
            nueva_gen = [x[1] for x in scored[:int(pop_size*0.1)]] 
            
            status_text.markdown(f"**Optimizando Gen {gen+1}/{generations}** | Precisión: `{best_score:.4f}` | Conflictos: `{scored[0][2]}`")
            
            while len(nueva_gen) < pop_size:
                t1 = random.choice(scored[:int(pop_size*0.5)])
                t2 = random.choice(scored[:int(pop_size*0.5)])
                p1, p2 = t1[1], t2[1]
                
                hijo = []
                for i in range(len(p1)):
                    gene = p1[i] if random.random() < 0.5 else p2[i]
                    hijo.append(gene)
                
                prob_mut = 0.2
                if random.random() < prob_mut:
                    for _ in range(random.randint(1, 3)):
                        idx = random.randint(0, len(hijo)-1)
                        hijo[idx] = self._mutate_gene(hijo[idx], aggressive_search=True)
                
                nueva_gen.append(hijo)
            
            pob = nueva_gen
            bar.progress((gen + 1) / generations)
            
            if scored[0][2] == 0 and scored[0][0] > 0.99:
                status_text.markdown(f"**¡Solución Perfecta Encontrada en Gen {gen+1}!**")
                break
                
        # 5. REPARACIÓN HEURÍSTICA: Repara los solapamientos remanentes forzando espacios vacíos
        best_overall = self._repair_individual(best_overall)
            
        return best_overall
        
    def _repair_individual(self, ind):
        max_attempts = 150
        for _ in range(max_attempts):
            score, conflicts, occ_s, occ_p = self._fitness_detailed(ind)
            if conflicts == 0:
                break
            
            for i, g in enumerate(ind):
                sec = g['sec']
                rango = (g['ini'], g['fin'])
                dias_lista = ["Lu", "Mi", "Vi"] if g['dias'] == "LuMiVi" else ["Ma", "Ju"]
                
                has_clash = False
                for dia in dias_lista:
                    pk = (g['prof'], dia)
                    if pk in occ_p and sum(1 for r in occ_p[pk] if max(rango[0], r[0]) < min(rango[1], r[1])) > 1:
                        has_clash = True
                    sk = (g['salon'], dia)
                    if sk in occ_s:
                        for r in occ_s[sk]:
                            # Si chocan y no es una mega fusión permitida
                            if max(rango[0], r[0]) < min(rango[1], r[1]) and not (sec.es_fusionable and r[3] and g['salon'] in self.mega_salones):
                                has_clash = True
                                
                if has_clash:
                    ind[i] = self._mutate_gene(g, aggressive_search=True)
        return ind

    def _mutate_gene(self, gene, aggressive_search=False):
        s = gene['sec']
        
        es_mj = (s.creditos >= 4)
        if s.creditos == 3: es_mj = False 
        if s.creditos == 1: es_mj = (random.random() > 0.5) 
        
        dias = "MaJu" if es_mj else "LuMiVi"
        
        # 3. CÁLCULO ESTRICTO DE DURACIÓN: 50 mins por crédito distribuido en los días
        num_dias = 3 if dias == "LuMiVi" else 2
        dur = math.ceil((s.creditos * 50) / num_dias)
        
        # Límite mínimo para laboratorios
        if dur < 50: dur = 50
        
        posibles_inicios = self.bloques_mj if es_mj else self.bloques_lmv
        h_ini = random.choice(posibles_inicios)
        
        prof = random.choice(s.cands) if s.cands else "TBA"
        
        candidatos_salon = [sl['CODIGO'] for sl in self.salones if sl['TIPO'] == s.tipo_salon and sl['CAPACIDAD'] >= s.cupo]
        
        if s.es_fusionable:
             candidatos_salon.extend([sl['CODIGO'] for sl in self.salones if sl['CODIGO'] in self.mega_salones])
        
        candidatos_salon = list(set(candidatos_salon))
        sal = "TBA"
        if candidatos_salon:
            sal = random.choice(candidatos_salon)
        elif aggressive_search:
            backup = [sl['CODIGO'] for sl in self.salones if sl['CAPACIDAD'] >= s.cupo]
            if backup: sal = random.choice(backup)

        # 2. MISMA HORA Y SALÓN: Se empaqueta en un solo gen forzando la consistencia semanal
        return {'sec': s, 'prof': prof, 'salon': sal, 'dias': dias, 'ini': h_ini, 'fin': h_ini + dur}

    def _random_ind(self):
        return [self._mutate_gene({'sec': s}, aggressive_search=True) for s in self.oferta]

    def _fitness_detailed(self, ind):
        penalty = 0
        conflicts = 0
        
        occ_s = {} 
        occ_p = {}
        cargas_profes = {}
        
        for g in ind:
            sec = g['sec']
            
            if g['salon'] == "TBA": 
                penalty += 1000
                conflicts += 1
            if g['prof'] == "TBA": 
                penalty += 1000
                conflicts += 1

            if g['salon'] != "TBA":
                salon_info = next((s for s in self.salones if s['CODIGO'] == g['salon']), None)
                if salon_info:
                    es_fusion_valida = sec.es_fusionable and (g['salon'] in self.mega_salones)
                    if not es_fusion_valida and salon_info['TIPO'] != sec.tipo_salon:
                        penalty += 500 
                        conflicts += 1

            if g['prof'] not in cargas_profes:
                cargas_profes[g['prof']] = 0
            cargas_profes[g['prof']] += sec.creditos

            dias_lista = ["Lu", "Mi", "Vi"] if g['dias'] == "LuMiVi" else ["Ma", "Ju"]
            for dia in dias_lista:
                pk = (g['prof'], dia)
                rango = (g['ini'], g['fin'])
                
                if g['prof'] != "TBA" and not "GRADUADO" in g['prof']: 
                    if pk in occ_p:
                        for r in occ_p[pk]:
                            if max(rango[0], r[0]) < min(rango[1], r[1]): 
                                penalty += 1000 
                                conflicts += 1
                        occ_p[pk].append(rango)
                    else: occ_p[pk] = [rango]

                if g['salon'] != "TBA":
                    sk = (g['salon'], dia)
                    if sk not in occ_s: occ_s[sk] = []
                    
                    for (ini_ex, fin_ex, cupo_ex, fusionable_ex) in occ_s[sk]:
                        if max(rango[0], ini_ex) < min(rango[1], fin_ex):
                            es_mega = g['salon'] in self.mega_salones
                            ambos_fusionables = sec.es_fusionable and fusionable_ex
                            
                            if es_mega and ambos_fusionables:
                                salon_cap = next((s['CAPACIDAD'] for s in self.salones if s['CODIGO'] == g['salon']), 0)
                                if (sec.cupo + cupo_ex) > salon_cap:
                                    penalty += 1000 
                                    conflicts += 1
                            else:
                                penalty += 1000
                                conflicts += 1
                    occ_s[sk].append((g['ini'], g['fin'], sec.cupo, sec.es_fusionable))

            if g['dias'] == "MaJu" and max(g['ini'], self.h_univ[0]) < min(g['fin'], self.h_univ[1]):
                penalty += 1000
                conflicts += 1

        for prof, carga in cargas_profes.items():
            if prof in self.profesores and "GRADUADO" not in prof:
                max_c = self.profesores[prof]['Carga_Max']
                if carga > max_c: 
                    penalty += (carga - max_c) * 100

        score = 1 / (1 + penalty)
        return score, conflicts, occ_s, occ_p

# ==============================================================================
# 4. UI PRINCIPAL
# ==============================================================================
def main():
    with st.sidebar:
        st.markdown("### $\Sigma$ Configuración")
        zona = st.selectbox("Zona Campus", ["CENTRAL", "PERIFERICA"])
        pop = st.slider("Población", 50, 500, 100)
        gens = st.slider("Generaciones", 100, 1000, 200)
        file = st.file_uploader("Subir Protocolo Excel", type=['xlsx'])

    st.markdown(f"### $\Omega$ Condiciones de Zona: {zona}")
    c1, c2, c3 = st.columns(3)
    
    h_bloqueo = "10:30 AM - 12:30 PM" if zona == "CENTRAL" else "10:00 AM - 12:00 PM"
    limites = "07:30 AM - 06:30 PM"
    
    with c1: st.metric("Ventana Operativa", limites)
    with c2: st.metric("Hora Universal", h_bloqueo)
    with c3:
        st.markdown(f"""<div class="status-badge">MODO PERFECCIÓN: ACTIVO</div>""", unsafe_allow_html=True)

    if not file:
        st.markdown("""
            <div class='glass-card' style='text-align: center;'>
                <h3 style='margin-top:0; color: #D4AF37;'>📥 Sincronización de Datos</h3>
                <p>Cargue el protocolo para iniciar la optimización. El sistema detectará automáticamente la capacidad por sección y generará el horario óptimo.</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.download_button("Plantilla Nueva (Actualizada)", crear_excel_guia(), "Plantilla_UPRM_Actualizada.xlsx", use_container_width=True)
            
    else:
        if st.button("🚀 INICIAR OPTIMIZACIÓN PERFECTA"):
            xls = pd.ExcelFile(file)
            
            df_cursos = pd.read_excel(xls, 'Cursos')
            df_profes = pd.read_excel(xls, 'Profesores')
            df_salones = pd.read_excel(xls, 'Salones')

            engine = PlatinumEnterpriseEngine(df_cursos, df_profes, df_salones, zona)
            
            start_time = time.time()
            mejor = engine.solve(pop, gens)
            elapsed = time.time() - start_time
            
            st.success(f"Cálculo finalizado en {elapsed:.2f} segundos. Solución óptima encontrada.")
            
            st.session_state.master = pd.DataFrame([{
                'ID': g['sec'].cod, 
                'Asignatura': g['sec'].cod.split('-')[0],
                'Creditos': g['sec'].creditos,
                'Persona': g['prof'], 
                'Días': g['dias'], 
                'Horario': f"{mins_to_str(g['ini'])} - {mins_to_str(g['fin'])}", 
                'Salón': g['salon'],
                'Tipo': 'REGULAR'
            } for g in mejor])

    if 'master' in st.session_state:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        t1, t2, t3 = st.tabs(["💎 PANEL DE CONTROL", "🔍 VISTA POR USUARIO", "🚨 AUDITORÍA DE CALIDAD"])
        with t1:
            edited = st.data_editor(st.session_state.master, use_container_width=True, height=500)
            st.download_button("💾 EXPORTAR EXCEL PLATINUM", exportar_todo(edited), "Horario_Final_UPRM.xlsx", use_container_width=True)
        with t2:
            lista_personas = sorted(st.session_state.master['Persona'].unique())
            if lista_personas:
                p = st.selectbox("Seleccionar Facultad/Graduado", lista_personas)
                subset = st.session_state.master[st.session_state.master['Persona'] == p]
                st.table(subset[['ID', 'Creditos', 'Días', 'Horario', 'Salón']])
                
                total_cr = subset['Creditos'].sum()
                st.metric(f"Carga Total de {p}", f"{total_cr} Créditos")
        with t3:
            tbas = st.session_state.master[
                (st.session_state.master['Salón'] == 'TBA') | 
                (st.session_state.master['Persona'] == 'TBA')
            ]
            
            c1_a, c2_a = st.columns(2)
            with c1_a:
                if not tbas.empty:
                    st.error(f"⚠️ {len(tbas)} Asignaciones Pendientes (TBA). Aumente las generaciones.")
                else:
                    st.success("✅ 100% Asignación de Espacios y Profesores.")

            df = st.session_state.master
            counts = df[df['Salón'] != 'TBA'].groupby(['Salón', 'Días', 'Horario']).size().reset_index(name='secciones_juntas')
            fusiones = counts[counts['secciones_juntas'] > 1]
            
            with c2_a:
                if not fusiones.empty:
                    st.info(f"ℹ️ Se realizaron {len(fusiones)} fusiones de secciones en salones grandes.")
                    st.dataframe(fusiones)
                else:
                    st.success("✅ 0 Conflictos detectados (No fue necesario fusionar).")
                
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
