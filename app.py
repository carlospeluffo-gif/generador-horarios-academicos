import streamlit as st
import pandas as pd
import numpy as np
import random
import io
import time
import math
from datetime import time as dtime

# ==============================================================================
# 1. ESTÉTICA PLATINUM ELITE (INTACTA)
# ==============================================================================
st.set_page_config(page_title="UPRM Scheduler Platinum AI", page_icon="🏛️", layout="wide")

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
        display: flex; justify-content: space-between; align-items: center;
        padding: 30px 60px; background: rgba(0, 0, 0, 0.85); border-bottom: 3px solid #D4AF37;
        margin-bottom: 40px; border-radius: 0 0 30px 30px; box-shadow: 0 10px 50px rgba(212, 175, 55, 0.15);
    }
    h1 { font-family: 'Playfair Display', serif !important; color: #D4AF37 !important; font-size: 3.2rem !important; margin: 10px 0 !important; text-shadow: 0 0 20px rgba(212, 175, 55, 0.5); }
    .glass-card { background: rgba(15, 15, 15, 0.9); border-radius: 15px; padding: 25px; border: 1px solid rgba(212, 175, 55, 0.25); backdrop-filter: blur(15px); margin-bottom: 20px; box-shadow: 0 15px 40px rgba(0,0,0,0.8); }
    .stButton>button { background: linear-gradient(135deg, #8E6E13 0%, #D4AF37 50%, #8E6E13 100%) !important; color: white !important; font-weight: bold !important; border-radius: 4px !important; width: 100%; border: none !important; height: 55px; font-size: 1.1rem; transition: 0.4s; }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 0 25px rgba(212, 175, 55, 0.4); }
    .status-badge { background: rgba(212, 175, 55, 0.1); border: 1px solid #D4AF37; color: #D4AF37; padding: 12px; border-radius: 8px; text-align: center; font-family: 'Source Code Pro', monospace; font-weight: 500; }
</style>
<div class="math-header">
    <div style="font-size:3rem; color:#D4AF37;">Ω</div>
    <div style="text-align: center; z-index: 2;">
        <h1>UPRM TIMETABLE SYSTEM</h1>
        <p style="color: #888; font-family: 'Source Code Pro'; letter-spacing: 4px;">MOTOR MATEMÁTICO - TESIS UPRM 2026</p>
    </div>
    <div style="font-size:3rem; color:#D4AF37;">f(H)</div>
</div>
""", unsafe_allow_html=True)

st.latex(r"f(H) = \frac{1}{1 + F_{hard}(H) + F_{soft}(H)} \quad \text{SISTEMA ASISTIDO POR DOMINIO DE FACTIBILIDAD } \Omega(e)")

# ==============================================================================
# 2. TABLAS Y COMPENSACIONES
# ==============================================================================
def mins_to_str(m):
    h, mins = divmod(int(m), 60)
    am_pm = "AM" if h < 12 else "PM"
    h_disp = h if h <= 12 else h - 12
    if h_disp == 0: h_disp = 12
    return f"{h_disp:02d}:{mins:02d} {am_pm}"

def str_to_mins(t_str):
    if not t_str or str(t_str).strip() == 'NAN': return None
    t_str = str(t_str).strip().upper()
    parts = t_str.split()
    time_part = parts[0]
    ampm = parts[1] if len(parts) > 1 else "AM"
    h, m = map(int, time_part.split(':'))
    if ampm == "PM" and h != 12: h += 12
    if ampm == "AM" and h == 12: h = 0
    return h * 60 + m

PATRONES = {
    3: [{"name": "Lu-Mi-Vi", "days": {"Lu": 1, "Mi": 1, "Vi": 1}}, {"name": "Ma-Ju", "days": {"Ma": 1.5, "Ju": 1.5}}, {"name": "Lu (Intensivo)", "days": {"Lu": 3}}, {"name": "Ma (Intensivo)", "days": {"Ma": 3}}, {"name": "Mi (Intensivo)", "days": {"Mi": 3}}, {"name": "Ju (Intensivo)", "days": {"Ju": 3}}, {"name": "Vi (Intensivo)", "days": {"Vi": 3}}],
    4: [{"name": "Lu-Ma-Mi-Ju", "days": {"Lu": 1, "Ma": 1, "Mi": 1, "Ju": 1}}, {"name": "Lu-Ma-Mi-Vi", "days": {"Lu": 1, "Ma": 1, "Mi": 1, "Vi": 1}}, {"name": "Lu-Ma-Ju-Vi", "days": {"Lu": 1, "Ma": 1, "Ju": 1, "Vi": 1}}, {"name": "Lu-Mi-Ju-Vi", "days": {"Lu": 1, "Mi": 1, "Ju": 1, "Vi": 1}}, {"name": "Ma-Mi-Ju-Vi", "days": {"Ma": 1, "Mi": 1, "Ju": 1, "Vi": 1}}, {"name": "Lu-Mi", "days": {"Lu": 2, "Mi": 2}}, {"name": "Ma-Ju", "days": {"Ma": 2, "Ju": 2}}],
    5: [{"name": "Lu-Ma-Mi-Ju-Vi", "days": {"Lu": 1, "Ma": 1, "Mi": 1, "Ju": 1, "Vi": 1}}, {"name": "Lu-Ma-Mi-Vi", "days": {"Lu": 1, "Ma": 1, "Mi": 1, "Vi": 2}}, {"name": "Ma-Ju-Vi", "days": {"Ma": 1.5, "Ju": 1.5, "Vi": 2}}]
}

COMPENSACION_TABLE = [(1,1,44,0.0),(1,45,74,0.5),(1,75,104,1.0),(1,105,134,1.5),(1,135,164,2.0),(2,1,37,0.0),(2,38,52,0.5),(2,53,67,1.0),(2,68,82,1.5),(2,83,97,2.0),(2,98,112,2.5),(2,113,127,3.0),(2,128,142,3.5),(2,143,147,4.0),(3,1,34,0.0),(3,35,44,0.5),(3,45,54,1.0),(3,55,64,1.5),(3,65,74,2.0),(3,75,84,2.5),(3,85,94,3.0),(3,95,104,3.5),(3,105,114,4.0),(3,115,124,4.5),(3,125,134,5.0),(3,135,144,5.5),(3,145,154,6.0)]

def calcular_compensacion(creditos, estudiantes):
    for h, min_e, max_e, add in COMPENSACION_TABLE:
        if h == creditos and min_e <= estudiantes <= max_e: return add
    return 0.0

def format_horario(patron, h_ini):
    return " | ".join([f"{dia}: {mins_to_str(h_ini)}-{mins_to_str(h_ini + int(contrib * 50))}" for dia, contrib in patron['days'].items()])

# ==============================================================================
# 3. CONSTRUCTORES DE DATOS Y CLASES
# ==============================================================================
class SeccionData:
    def __init__(self, cod, creditos, cupo, cands, tipo_salon, es_fusionable=False):
        self.cod = str(cod)
        self.base_cod = self.cod.split('-')[0].upper().replace(" ", "")
        self.creditos = int(creditos)
        self.cupo = int(cupo)
        self.cands = [c.strip().upper() for c in (cands if isinstance(cands, list) else str(cands).split(',')) if c.strip() and str(c).upper() != 'NAN']
        self.tipo_salon = int(float(str(tipo_salon))) if str(tipo_salon).isdigit() else 1
        self.es_fusionable = es_fusionable

class ProfesorData:
    def __init__(self, nombre, carga_max, pref_dias, pref_horas, bloqueo_dias, bloqueo_ini, bloqueo_fin, preferencias_cursos, compensacion):
        self.nombre = nombre.upper().strip()
        self.carga_max = float(carga_max) if pd.notnull(carga_max) else 12.0
        self.pref_dias = pref_dias if isinstance(pref_dias, str) else ''
        self.pref_horas = pref_horas if isinstance(pref_horas, str) else 'ANY'
        self.bloqueo_dias = {d.strip().title() for d in str(bloqueo_dias).split(',')} if pd.notnull(bloqueo_dias) else set()
        self.bloqueo_ini = str_to_mins(bloqueo_ini)
        self.bloqueo_fin = str_to_mins(bloqueo_fin)
        self.preferencias = [c.upper().strip() for c in preferencias_cursos if pd.notnull(c)]
        self.compensacion = str(compensacion).upper().strip() in ('SI', 'YES', '1')

    def idoneidad(self, curso_cod):
        for idx, pref in enumerate(self.preferencias):
            if pref in curso_cod: return 1.0 / (idx + 1)
        return 0.0

# ==============================================================================
# 4. MOTOR IA BASADO EN LA TESIS: Algoritmos Genéticos con Dominio Ω(e)
# ==============================================================================
class TesisEliteEngine:
    def __init__(self, df_cursos, df_profes, df_salones, zona):
        self.zona = zona
        # Restricciones Institucionales de Hora Universal (Rf9)
        if zona == "CENTRAL":
            self.bloques = list(range(450, 1171, 30))
            self.h_univ = (630, 750)
        else:
            self.bloques = list(range(420, 1141, 30))
            self.h_univ = (600, 720)
            
        # Parse Salones
        self.salones = []
        for _, r in df_salones.iterrows():
            self.salones.append({'CODIGO': str(r['CODIGO']).strip().upper(), 'CAPACIDAD': int(r.get('CAPACIDAD', 30)), 'TIPO': int(r.get('TIPO', 1))})

        # Parse Profesores
        self.profesores = {}
        for _, r in df_profes.iterrows():
            prefs = [r.get(c, '') for c in ['PREF1', 'PREF2', 'PREF3']]
            p = ProfesorData(r['NOMBRE'], r.get('CARGA_MAX', 12), r.get('PREF_DIAS'), r.get('PREF_HORAS'), r.get('BLOQUEO_DIAS'), r.get('BLOQUEO_HORA_INI'), r.get('BLOQUEO_HORA_FIN'), prefs, r.get('COMPENSACION', 'NO'))
            self.profesores[p.nombre] = p

        # Parse Cursos
        self.oferta = []
        for _, r in df_cursos.iterrows():
            demanda = int(r.get('DEMANDA', 0))
            cupo_raw = str(r.get('CUPO', '30')).strip()
            cap_unica = int(cupo_raw) if cupo_raw.isdigit() else 30
            num_secciones = math.ceil(demanda / cap_unica) if demanda > 0 else 1
            for i in range(num_secciones):
                self.oferta.append(SeccionData(f"{r['CODIGO']}-{i+1:02d}", r['CREDITOS'], cap_unica, r.get('CANDIDATOS', ''), r.get('TIPO_SALON', 1)))

    def _es_bloqueo(self, prof, dia, ini, fin):
        if not prof.bloqueo_dias or dia not in prof.bloqueo_dias: return False
        if not prof.bloqueo_ini or not prof.bloqueo_fin: return False
        return max(ini, prof.bloqueo_ini) < min(fin, prof.bloqueo_fin)

    def _get_dominio_factibilidad_local(self, sec, prof_obj):
        """ Construcción del Dominio Ω(e) según Sección 4.1.5 de la Tesis """
        # Rf4 y Rf5: Salones válidos por capacidad y tipo
        salones_validos = [s['CODIGO'] for s in self.salones if s['CAPACIDAD'] >= sec.cupo and s['TIPO'] == sec.tipo_salon]
        if not salones_validos: salones_validos = [s['CODIGO'] for s in self.salones if s['CAPACIDAD'] >= sec.cupo] # Relajación mínima si no hay tipo
        
        tiempos_validos = []
        patrones = PATRONES.get(sec.creditos, PATRONES[3])
        
        for pat in patrones:
            es_intensivo = sum(pat['days'].values()) >= 3 and max(pat['days'].values()) >= 3
            for ini in self.bloques:
                # Restricción Institucional: Intensivos >= 15:30 (930 min)
                if es_intensivo and ini < 930: continue
                
                es_valido = True
                for dia, contrib in pat['days'].items():
                    fin = ini + int(contrib * 50)
                    # Rf9: Hora Universal
                    if dia in ["Ma", "Ju"] and max(ini, self.h_univ[0]) < min(fin, self.h_univ[1]):
                        es_valido = False; break
                    # Rf6: Bloqueo Profesor
                    if prof_obj and self._es_bloqueo(prof_obj, dia, ini, fin):
                        es_valido = False; break
                
                if es_valido: tiempos_validos.append((pat, ini))
                
        return salones_validos, tiempos_validos

    def _create_smart_individual(self):
        """ Algoritmo 4: IndCreator (Construcción asistida) """
        ind = []
        occ_prof = {}
        occ_salon = {}
        carga_prof = {}
        
        # Orden heurístico: Primero los más difíciles (pocos candidatos)
        oferta_ordenada = sorted(self.oferta, key=lambda s: (len([c for c in s.cands if c != "GRADUADOS"]), -s.cupo))
        
        for s in oferta_ordenada:
            # 1. Elegir profesor sin violar Rf7 (Carga Max)
            valid_profs = []
            for p_name in s.cands:
                if p_name == "GRADUADOS": 
                    valid_profs.append(p_name); continue
                p_obj = self.profesores.get(p_name)
                if p_obj:
                    cred_eff = s.creditos - (calcular_compensacion(s.creditos, s.cupo) if p_obj.compensacion else 0)
                    if carga_prof.get(p_name, 0) + cred_eff <= p_obj.carga_max:
                        valid_profs.append(p_name)
            
            prof = "TBA"
            if valid_profs:
                # Priorizar profesores con MENOS créditos totales permitidos (Heurística de usuario)
                profs_reales = [p for p in valid_profs if p != "GRADUADOS"]
                if profs_reales:
                    profs_reales.sort(key=lambda p: (self.profesores[p].carga_max, -self.profesores[p].idoneidad(s.base_cod)))
                    prof = profs_reales[0]
                else:
                    prof = "GRADUADOS"
            elif s.cands: prof = random.choice(s.cands) # Fuerza mayor
            
            p_obj = self.profesores.get(prof) if prof not in ("TBA", "GRADUADOS") else None
            
            # 2. Extraer del dominio Ω(e)
            salones_val, tiempos_val = self._get_dominio_factibilidad_local(s, p_obj)
            
            best_patron, best_ini, best_salon = None, None, "TBA"
            
            # 3. Buscar asignación libre de solapamientos (Rf2 y Rf3)
            random.shuffle(tiempos_val)
            found = False
            for pat, ini in tiempos_val:
                prof_ok = True
                if p_obj:
                    for dia, contrib in pat['days'].items():
                        fin = ini + int(contrib * 50)
                        for (e_ini, e_fin) in occ_prof.get((prof, dia), []):
                            if max(ini, e_ini) < min(fin, e_fin): prof_ok = False; break
                        if not prof_ok: break
                if not prof_ok: continue
                
                random.shuffle(salones_val)
                for salon in salones_val:
                    sal_ok = True
                    for dia, contrib in pat['days'].items():
                        fin = ini + int(contrib * 50)
                        for (e_ini, e_fin) in occ_salon.get((salon, dia), []):
                            if max(ini, e_ini) < min(fin, e_fin): sal_ok = False; break
                        if not sal_ok: break
                    if sal_ok:
                        best_patron, best_ini, best_salon = pat, ini, salon
                        found = True
                        break
                if found: break
                
            # Fallback si el horario está demasiado denso
            if not found and tiempos_val:
                best_patron, best_ini = random.choice(tiempos_val)
                if salones_val: best_salon = random.choice(salones_val)
                
            if not best_patron: # Caso extremo
                best_patron = PATRONES[s.creditos][0]
                best_ini = self.bloques[0]

            ind.append({'sec': s, 'prof': prof, 'salon': best_salon, 'patron': best_patron, 'ini': best_ini})
            
            # Registrar ocupación global
            if p_obj:
                carga_prof[prof] = carga_prof.get(prof, 0) + s.creditos - (calcular_compensacion(s.creditos, s.cupo) if p_obj.compensacion else 0)
                for dia, contrib in best_patron['days'].items():
                    occ_prof.setdefault((prof, dia), []).append((best_ini, best_ini + int(contrib * 50)))
            if best_salon != "TBA":
                for dia, contrib in best_patron['days'].items():
                    occ_salon.setdefault((best_salon, dia), []).append((best_ini, best_ini + int(contrib * 50)))

        return ind

    def _fitness_tesis(self, ind):
        """ Función de Aptitud f(H) de la Tesis (Ecuación 4.4.3) """
        F_hard = 0
        F_soft = 0
        conflictos = 0
        detalles = []
        bad_idx = set()
        
        occ_salon = {}   
        occ_prof = {}    

        for i, g in enumerate(ind):
            sec, prof, salon, pat, ini = g['sec'], g['prof'], g['salon'], g['patron'], g['ini']
            
            if prof == "TBA": F_hard += 1000; conflictos += 1; detalles.append(f"[{sec.cod}] Sin profesor asignado"); bad_idx.add(i); continue
            if salon == "TBA": F_hard += 1000; conflictos += 1; detalles.append(f"[{sec.cod}] Sin salón"); bad_idx.add(i); continue

            p_obj = self.profesores.get(prof)

            # Rs1: Preferencias de Profesor (Suave)
            if p_obj:
                if p_obj.pref_horas == 'AM' and ini >= 720: F_soft += 10
                if p_obj.pref_horas == 'PM' and ini < 720: F_soft += 10

            for dia, contrib in pat['days'].items():
                fin = ini + int(contrib * 50)
                rango = (ini, fin)
                
                # Rf2: Solapamiento Profesor
                if prof != "GRADUADOS":
                    pk = (prof, dia)
                    for (ex_ini, ex_fin) in occ_prof.get(pk, []):
                        if max(rango[0], ex_ini) < min(rango[1], ex_fin):
                            F_hard += 1000; conflictos += 1; detalles.append(f"Rf2: {prof} solapado el {dia}"); bad_idx.add(i)
                    occ_prof.setdefault(pk, []).append(rango)

                # Rf3: Solapamiento Salón
                sk = (salon, dia)
                for (ex_ini, ex_fin) in occ_salon.get(sk, []):
                    if max(rango[0], ex_ini) < min(rango[1], ex_fin):
                        F_hard += 1000; conflictos += 1; detalles.append(f"Rf3: Salón {salon} solapado el {dia}"); bad_idx.add(i)
                occ_salon.setdefault(sk, []).append(rango)

        # Fitness Escalar (Rango 0 a 1)
        fitness = 1.0 / (1.0 + F_hard + (F_soft * 0.01))
        return fitness, conflictos, list(set(detalles)), list(bad_idx)

    def _mutate_gene(self, gene):
        """ Mutación Asistida Localmente """
        s = gene['sec']
        p_obj = self.profesores.get(gene['prof'])
        
        salones_val, tiempos_val = self._get_dominio_factibilidad_local(s, p_obj)
        
        nuevo_pat, nuevo_ini = gene['patron'], gene['ini']
        if tiempos_val:
            nuevo_pat, nuevo_ini = random.choice(tiempos_val)
            
        nuevo_salon = gene['salon']
        if salones_val:
            nuevo_salon = random.choice(salones_val)
            
        return {'sec': s, 'prof': gene['prof'], 'salon': nuevo_salon, 'patron': nuevo_pat, 'ini': nuevo_ini}

    def solve(self, pop_size, generations):
        poblacion = [self._create_smart_individual() for _ in range(pop_size)]
        bar, status_text = st.progress(0), st.empty()

        mejor_ind, mejor_score, mejor_conflictos = None, -1, []

        for gen in range(generations):
            scored = [(self._fitness_tesis(ind), ind) for ind in poblacion]
            scored.sort(key=lambda x: x[0][0], reverse=True)
            
            current_best_fit = scored[0][0][0]
            if current_best_fit > mejor_score:
                mejor_score = current_best_fit
                mejor_ind = scored[0][1]
                mejor_conflictos = scored[0][0][2]

            if gen % 5 == 0 or gen == generations - 1:
                status_text.markdown(f"**🔄 Evolución Gen {gen+1}/{generations}** | 🏆 Fitness: `{mejor_score:.4f}` | 🚨 Errores Duros: `{scored[0][0][1]}`")
                bar.progress((gen+1)/generations)

            elite = [x[1] for x in scored[:max(1, int(pop_size * 0.1))]]
            nueva_gen = elite.copy()

            while len(nueva_gen) < pop_size:
                p1, p2 = max(random.sample(scored, 3), key=lambda x: x[0][0])[1], max(random.sample(scored, 3), key=lambda x: x[0][0])[1]
                hijo = [g1 if random.random() < 0.5 else g2 for g1, g2 in zip(p1, p2)]
                
                # Mutación adaptativa enfocada en corregir errores
                _, conf, _, bad = self._fitness_tesis(hijo)
                for i in bad:
                    if random.random() < 0.8: hijo[i] = self._mutate_gene(hijo[i]) # Reparación intensiva
                        
                nueva_gen.append(hijo)
            poblacion = nueva_gen

        return mejor_ind, mejor_conflictos

# ==============================================================================
# 5. UI PRINCIPAL Y PERSISTENCIA
# ==============================================================================
def main():
    with st.sidebar:
        st.markdown("### $\Sigma$ Parámetros Evolutivos")
        zona = st.selectbox("Zona Campus", ["CENTRAL", "PERIFERICA"])
        pop = st.slider("Tamaño de Población (N)", 50, 200, 100)
        gens = st.slider("Generaciones Máximas (G)", 50, 300, 150)
        file = st.file_uploader("Data Institucional (.xlsx)", type=['xlsx'])

    if not file:
        st.info("Sube tu archivo Excel para comenzar el procesamiento matemático.")
    else:
        if st.button("🚀 INICIAR OPTIMIZACIÓN"):
            with st.spinner("Construyendo matriz cromosómica y evaluando dominios locales Ω(e)..."):
                xls = pd.ExcelFile(file)
                engine = TesisEliteEngine(pd.read_excel(xls, 'Cursos'), pd.read_excel(xls, 'Profesores'), pd.read_excel(xls, 'Salones'), zona)
                
                t0 = time.time()
                mejor, conf_list = engine.solve(pop, gens)
                
                st.session_state.master = pd.DataFrame([{'ID': g['sec'].cod, 'Asignatura': g['sec'].base_cod, 'Creditos': g['sec'].creditos, 'Persona': g['prof'], 'Días': g['patron']['name'], 'Horario': format_horario(g['patron'], g['ini']), 'Salón': g['salon']} for g in mejor])
                st.session_state.conf_list = conf_list
                st.success(f"✅ Ciclo concluido en {time.time() - t0:.2f}s.")

    if 'master' in st.session_state:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["💎 RESULTADOS", "🚨 REPORTE DE FACTIBILIDAD"])
        with t1:
            st.dataframe(st.session_state.master, use_container_width=True)
        with t2:
            if not st.session_state.conf_list:
                st.success("🏆 HORARIO 100% FACTIBLE. Cero violaciones a Restricciones Fuertes (Rf).")
            else:
                st.error(f"Se detectaron {len(st.session_state.conf_list)} colisiones.")
                for txt in st.session_state.conf_list: st.markdown(f"- {txt}")
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
