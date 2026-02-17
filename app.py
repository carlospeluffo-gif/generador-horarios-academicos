import streamlit as st
import pandas as pd
import numpy as np
import random
import io
import time
import re

# ==============================================================================
# 1. ESTÉTICA PLATINUM ELITE (DISEÑO MATEMÁTICO AVANZADO - INTACTO)
# ==============================================================================
st.set_page_config(page_title="UPRM Scheduler Platinum AI v6", page_icon="🏛️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Source+Code+Pro:wght@300;500&display=swap');
    
    /* Fondo con Cuadrícula 3D Hiper-Realista */
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

    /* Encabezado Abstracto Matemático */
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

    .math-header::before {
        content: '∑';
        position: absolute;
        left: 5%;
        font-size: 8rem;
        color: rgba(212, 175, 55, 0.05);
        font-family: serif;
    }
    .math-header::after {
        content: '∫';
        position: absolute;
        right: 5%;
        font-size: 8rem;
        color: rgba(212, 175, 55, 0.05);
        font-family: serif;
    }

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

    /* Botones Generales */
    .stButton>button { 
        background: linear-gradient(135deg, #8E6E13 0%, #D4AF37 50%, #8E6E13 100%) !important; 
        color: white !important; font-weight: bold !important; border-radius: 4px !important; 
        width: 100%; border: none !important; height: 55px; font-size: 1.1rem;
        transition: 0.4s;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 0 25px rgba(212, 175, 55, 0.4); }

    /* Estilo Dorado para "Descargar Plantilla" */
    .stDownloadButton>button {
        background: linear-gradient(135deg, #B8860B 0%, #FFD700 50%, #B8860B 100%) !important;
        color: #000 !important;
        font-weight: 800 !important;
        border: 1px solid #D4AF37 !important;
    }

    /* Sidebar y Título Σ Configuración */
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
            UPRM MATHEMATICAL OPTIMIZATION ENGINE v6.0 (PLATINUM PERFECT)
        </p>
    </div>
    <div class="abstract-icon">∞</div>
</div>
""", unsafe_allow_html=True)

st.latex(r"\blacksquare \quad \text{SISTEMA DE PLANIFICACIÓN ACADÉMICA OPTIMIZADA - TESIS MASTER} \quad \blacksquare")

# ==============================================================================
# 2. UTILIDADES DE EXPORTACIÓN Y FORMATO
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
# 3. MOTOR IA (PLATINUM ENGINE V6.0 - PERFECT LOGIC)
# ==============================================================================
class SeccionData:
    def __init__(self, cod, creditos, cupo, cands, tipo_salon, es_ayudantia=False):
        self.cod = cod
        self.creditos = creditos
        self.cupo = cupo
        if isinstance(cands, list):
            self.cands = cands
        else:
            self.cands = [c.strip().upper() for c in str(cands).split(',') if c.strip() and str(c).upper() != 'NAN']
        
        self.tipo_salon = int(tipo_salon) if str(tipo_salon).isdigit() else 1 # Asegurar entero
        self.es_ayudantia = es_ayudantia
        
        # Identificar cursos fusionables (Mate 3171, 72, 73)
        base = cod.split('-')[0].upper().replace(" ", "")
        self.es_fusionable = base in ["MATE3171", "MATE3172", "MATE3173"]

class PlatinumEnterpriseEngine:
    def __init__(self, df_cursos, df_profes, df_salones, df_grad, zona):
        self.zona = zona
        df_salones.columns = [c.strip().upper() for c in df_salones.columns]
        
        # Procesar Salones y Detectar "Grandes" (FA, FB, FC)
        self.salones = []
        self.mega_salones = set() # Set de códigos de salones grandes
        
        for _, r in df_salones.iterrows():
            codigo = str(r['CODIGO']).strip().upper()
            cap = int(r['CAPACIDAD'])
            tipo = int(r['TIPO'])
            
            self.salones.append({'CODIGO': codigo, 'CAPACIDAD': cap, 'TIPO': tipo})
            
            # Criterio para FA, FB, FC (Por nombre o alta capacidad)
            # Normalizamos quitando espacios para detectar F A, F-B, etc.
            norm_cod = codigo.replace(" ", "").replace("-", "")
            if norm_cod.startswith("FA") or norm_cod.startswith("FB") or norm_cod.startswith("FC"):
                self.mega_salones.add(codigo)
        
        # Mapa de Profesores y Preferencias
        self.profesores = {}
        for _, r in df_profes.iterrows():
            nombre = str(r['Nombre']).upper().strip()
            self.profesores[nombre] = {
                'Carga_Max': r['CREDITOS'], # Para profesores regulares es un máximo
                'Pref_Bloque': str(r.get('Pref_horas', 'AM')).upper() 
            }
            
        # Mapa de Graduados (Restricción Estricta)
        self.graduados_cfg = {}
        self.graduados_por_curso = {} 
        self.es_graduado = set()
        
        if df_grad is not None and not df_grad.empty:
            for _, r in df_grad.iterrows():
                nom_grad = str(r['NOMBRE_GRADUADO']).upper().strip()
                creditos_exactos = r['CREDITOS_A_DICTAR'] # ESTO ES OBLIGATORIO
                cursos_recibe = [c.strip().upper() for c in str(r['CODIGOS_RECIBE']).split(',') if c.strip()]
                
                self.graduados_cfg[nom_grad] = {
                    'recibe': cursos_recibe,
                    'dar': creditos_exactos
                }
                self.es_graduado.add(nom_grad)
                
                for curso in cursos_recibe:
                    if curso not in self.graduados_por_curso:
                        self.graduados_por_curso[curso] = []
                    self.graduados_por_curso[curso].append(nom_grad)
        
        # Generación de Oferta
        self.oferta = []
        for _, r in df_cursos.iterrows():
            codigo_base = str(r['CODIGO']).strip().upper()
            candidatos_raw = str(r['CANDIDATOS'])
            lista_candidatos = []
            
            if "GRADUADOS" in candidatos_raw.upper():
                if codigo_base in self.graduados_por_curso:
                    lista_candidatos = self.graduados_por_curso[codigo_base]
                else:
                    lista_candidatos = ["TBA"]
            else:
                lista_candidatos = [c.strip().upper() for c in candidatos_raw.split(',') if c.strip()]

            cant_secciones = int(r['CANT_SECCIONES'])
            for i in range(cant_secciones):
                self.oferta.append(SeccionData(
                    f"{codigo_base}-{i+1:02d}", 
                    r['CREDITOS'], 
                    r['DEMANDA'], 
                    lista_candidatos, 
                    r['TIPO_SALON']
                ))
        
        # Ayudantías (Solo para ocupar tiempo del graduado, no salon)
        for nom, cfg in self.graduados_cfg.items():
            # Nota: Esto es simbólico para el horario personal, no ocupa salón físico de clases
            self.oferta.append(SeccionData(f"AYUD-{nom[:4]}", 0, 1, [nom], 0, True)) 

        # Bloques
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
                score = self._fitness(ind)
                scored.append((score, ind))
            
            scored.sort(key=lambda x: x[0], reverse=True)
            
            if scored[0][0] > best_score:
                best_score = scored[0][0]
                best_overall = scored[0][1]

            # Elitismo agresivo para mantener la perfección
            nueva_gen = [x[1] for x in scored[:int(pop_size*0.15)]] 
            
            status_text.markdown(f"**Optimizando Gen {gen+1}/{generations}** | Precisión: `{best_score:.8f}`")
            
            while len(nueva_gen) < pop_size:
                padres = random.sample(scored[:int(pop_size*0.5)], 2) 
                p1, p2 = padres[0][1], padres[1][1]
                
                # Cruce Uniforme (Mejor mezcla)
                hijo = []
                for i in range(len(p1)):
                    hijo.append(p1[i] if random.random() < 0.5 else p2[i])
                
                # Mutación Adaptativa
                if random.random() < 0.25:
                    idx = random.randint(0, len(hijo)-1)
                    hijo[idx] = self._mutate_gene(hijo[idx], aggressive_search=True)
                
                nueva_gen.append(hijo)
            
            pob = nueva_gen
            bar.progress((gen + 1) / generations)
            
        return best_overall

    def _mutate_gene(self, gene, aggressive_search=False):
        s = gene['sec']
        es_mj = (s.creditos >= 4) or (random.random() > 0.6)
        dias = "MaJu" if es_mj else "LuMiVi"
        dur = 80 if es_mj else 50 
        
        posibles_inicios = self.bloques_mj if es_mj else self.bloques_lmv
        h_ini = random.choice(posibles_inicios)
        
        # Selección de Profesor
        prof = random.choice(s.cands) if s.cands else "TBA"
        
        # Selección de Salón con Lógica Estricta + Fusión
        # 1. Filtrar por TIPO exacto (1 o 2)
        candidatos_salon = [sl['CODIGO'] for sl in self.salones if sl['TIPO'] == s.tipo_salon and sl['CAPACIDAD'] >= s.cupo]
        
        # 2. Si el curso es fusionable (Mate317x), AÑADIR los Mega Salones (FA, FB, FC) aunque sean otro tipo
        #    asumiendo que FA/FB/FC pueden alojar estos cursos.
        if s.es_fusionable:
             candidatos_salon.extend([sl['CODIGO'] for sl in self.salones if sl['CODIGO'] in self.mega_salones])
        
        # Eliminar duplicados
        candidatos_salon = list(set(candidatos_salon))

        sal = "TBA"
        if candidatos_salon:
            sal = random.choice(candidatos_salon)
        else:
            # RETRY AGRESIVO: Si no hay salón, intentar relajar restricciones de tipo solo si es desesperado,
            # o buscar en todos los salones que quepan.
            if aggressive_search:
                backup = [sl['CODIGO'] for sl in self.salones if sl['CAPACIDAD'] >= s.cupo]
                if backup: sal = random.choice(backup)

        return {'sec': s, 'prof': prof, 'salon': sal, 'dias': dias, 'ini': h_ini, 'fin': h_ini + dur}

    def _random_ind(self):
        return [self._mutate_gene({'sec': s}, aggressive_search=True) for s in self.oferta]

    def _fitness(self, ind):
        penalty = 0
        soft_penalty = 0 
        
        s_map = {item['sec'].cod.split('-')[0]: item for item in ind}
        
        # Estructuras para colisiones
        # occ_s: (salon, dia) -> lista de (inicio, fin, ocupacion_actual, curso_es_fusionable)
        occ_s = {} 
        occ_p = {}
        cargas_graduados = {g: 0 for g in self.graduados_cfg}
        cargas_profes = {p: 0 for p in self.profesores if p not in self.graduados_cfg}
        
        for g in ind:
            sec = g['sec']
            
            # --- 1. PENALIZACIÓN TBA (Muerte Súbita) ---
            if g['salon'] == "TBA": penalty += 1000000
            if g['prof'] == "TBA": penalty += 1000000

            # --- 2. TIPO DE SALÓN INCORRECTO ---
            # Si el salón no es TBA, verificar que el tipo coincida
            if g['salon'] != "TBA":
                # Buscar info del salón
                salon_info = next((s for s in self.salones if s['CODIGO'] == g['salon']), None)
                if salon_info:
                    # Excepción: Si es fusionable y está en Mega Salón, se permite
                    es_fusion_valida = sec.es_fusionable and (g['salon'] in self.mega_salones)
                    if not es_fusion_valida:
                        if salon_info['TIPO'] != sec.tipo_salon:
                            penalty += 50000 # Muy grave usar lab para teoria

            # --- 3. CRÉDITOS GRADUADOS (SUMA) ---
            if g['prof'] in cargas_graduados:
                cargas_graduados[g['prof']] += sec.creditos
            elif g['prof'] in cargas_profes:
                cargas_profes[g['prof']] += sec.creditos

            # --- 4. CHOQUE DE HORARIO Y FUSIÓN ---
            dias_lista = ["Lu", "Mi", "Vi"] if g['dias'] == "LuMiVi" else ["Ma", "Ju"]
            
            for dia in dias_lista:
                # A. Choque Profesor
                pk = (g['prof'], dia)
                rango = (g['ini'], g['fin'])
                if g['prof'] != "TBA":
                    if pk in occ_p:
                        for r in occ_p[pk]:
                            if max(rango[0], r[0]) < min(rango[1], r[1]): 
                                penalty += 50000 # Profesor no puede estar en dos sitios
                        occ_p[pk].append(rango)
                    else:
                        occ_p[pk] = [rango]

                # B. Choque Salón (Con Lógica de Fusión)
                if g['salon'] != "TBA":
                    sk = (g['salon'], dia)
                    
                    if sk not in occ_s:
                        occ_s[sk] = []
                    
                    # Verificar colisiones con ocupantes existentes
                    for (ini_ex, fin_ex, cupo_ex, fusionable_ex) in occ_s[sk]:
                        # Si hay solapamiento de tiempo
                        if max(rango[0], ini_ex) < min(rango[1], fin_ex):
                            
                            # LOGICA DE FUSION
                            # Se permite SOLO SI:
                            # 1. El salón es Mega Salón (FA, FB, FC)
                            # 2. El curso nuevo es fusionable (Mate317x)
                            # 3. El curso existente TAMBIEN es fusionable
                            # 4. La suma de cupos cabe en el salón
                            
                            es_mega = g['salon'] in self.mega_salones
                            ambos_fusionables = sec.es_fusionable and fusionable_ex
                            
                            if es_mega and ambos_fusionables:
                                # Chequear capacidad total
                                salon_cap = next((s['CAPACIDAD'] for s in self.salones if s['CODIGO'] == g['salon']), 0)
                                if (sec.cupo + cupo_ex) > salon_cap:
                                    penalty += 20000 # Se pasa de capacidad
                                # Si cabe, NO HAY PENALIZACIÓN (Fusión Exitosa)
                            else:
                                # Choque normal (No se pueden fusionar o no es el salón correcto)
                                penalty += 50000
                    
                    # Registrar ocupación
                    occ_s[sk].append((g['ini'], g['fin'], sec.cupo, sec.es_fusionable))

            # --- 5. HORA UNIVERSAL ---
            if g['dias'] == "MaJu":
                if max(g['ini'], self.h_univ[0]) < min(g['fin'], self.h_univ[1]):
                    penalty += 50000

        # --- VALIDACIÓN GLOBAL DE CRÉDITOS GRADUADOS (HARD CONSTRAINT) ---
        for grad, carga_actual in cargas_graduados.items():
            objetivo = self.graduados_cfg[grad]['dar']
            if carga_actual != objetivo:
                # Penalización brutal por cada crédito de diferencia
                diff = abs(carga_actual - objetivo)
                penalty += (diff * 100000) 

        # Validación Profesores (Carga Máxima)
        for prof, carga in cargas_profes.items():
            max_c = self.profesores[prof]['Carga_Max']
            if carga > max_c:
                penalty += 10000

        # Fitness inverso
        return 1 / (1 + penalty + soft_penalty)

# ==============================================================================
# 4. UI PRINCIPAL
# ==============================================================================
def main():
    with st.sidebar:
        st.markdown("### $\Sigma$ Configuración")
        zona = st.selectbox("Zona Campus", ["CENTRAL", "PERIFERICA"])
        # Aumentamos valores por defecto para buscar la perfección
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
                <p>Cargue el protocolo para iniciar la optimización. El sistema detectará automáticamente FA, FB, FC para fusiones.</p>
            </div>
        """, unsafe_allow_html=True)
        
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.download_button("Plantilla Completa (Con Graduados)", crear_excel_guia(con_graduados=True), "Plantilla_UPRM_Full.xlsx", use_container_width=True)
        with col_d2:
            st.download_button("Plantilla Simple (Sin Graduados)", crear_excel_guia(con_graduados=False), "Plantilla_UPRM_Simple.xlsx", use_container_width=True)
            
    else:
        if st.button("🚀 INICIAR OPTIMIZACIÓN PERFECTA"):
            xls = pd.ExcelFile(file)
            
            df_grad = None
            if 'Graduados' in xls.sheet_names:
                df_grad = pd.read_excel(xls, 'Graduados')
            
            engine = PlatinumEnterpriseEngine(
                pd.read_excel(xls, 'Cursos'), 
                pd.read_excel(xls, 'Profesores'), 
                pd.read_excel(xls, 'Salones'), 
                df_grad, 
                zona
            )
            
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
                'Tipo': 'AYUDANTÍA' if g['sec'].es_ayudantia else 'REGULAR'
            } for g in mejor])

    if 'master' in st.session_state:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        t1, t2, t3 = st.tabs(["💎 PANEL DE CONTROL", "🔍 VISTA POR USUARIO", "🚨 AUDITORÍA DE CALIDAD"])
        with t1:
            edited = st.data_editor(st.session_state.master, use_container_width=True, height=500)
            st.download_button("💾 EXPORTAR EXCEL PLATINUM", exportar_todo(edited), "Horario_Final_UPRM.xlsx", use_container_width=True)
        with t2:
            lista_personas = sorted(st.session_state.master['Persona'].unique())
            p = st.selectbox("Seleccionar Facultad/Graduado", lista_personas)
            subset = st.session_state.master[st.session_state.master['Persona'] == p]
            st.table(subset[['ID', 'Días', 'Horario', 'Salón']])
        with t3:
            # Auditoría de TBAs
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

            # Auditoría de Fusiones
            df = st.session_state.master
            counts = df[df['Salón'] != 'TBA'].groupby(['Salón', 'Días', 'Horario']).size().reset_index(name='secciones_juntas')
            fusiones = counts[counts['secciones_juntas'] > 1]
            
            with c2_a:
                if not fusiones.empty:
                    st.info(f"ℹ️ Se realizaron {len(fusiones)} fusiones de secciones en salones grandes.")
                    st.dataframe(fusiones)
                else:
                    st.write("No fue necesario fusionar secciones.")
                
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
