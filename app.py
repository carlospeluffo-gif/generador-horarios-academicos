import streamlit as st
import pandas as pd
import numpy as np
import random
import copy
import time
import io
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ==============================================================================
# 1. ESTÉTICA PLATINUM
# ==============================================================================
st.set_page_config(page_title="UPRM Scheduler Platinum", page_icon="🏛️", layout="wide")

st.markdown("""
<style>
    .stApp {
        background-color: #000000;
        background-image: linear-gradient(rgba(15, 15, 15, 0.50), rgba(15, 15, 15, 0.50)),
            url("https://www.transparenttextures.com/patterns/cubes.png");
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
    [data-testid="stSidebar"] { background-color: #080808; border-right: 1px solid #333; }
    .stButton>button {
        background: linear-gradient(90deg, #B8860B, #FFD700);
        color: #000 !important;
        font-weight: 800; border: none; border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. FUNCIONES DE APOYO Y TIEMPO
# ==============================================================================
def generar_bloques_por_zona(zona):
    bloques = {}
    horas_inicio = [h*60 + 30 for h in range(7, 20)] if zona == "CENTRAL" else [h*60 for h in range(7, 20)]

    def add_b(id_base, dias, dur, lbl):
        for h in horas_inicio:
            if h + dur > 1320: continue 
            bloques[f"{id_base}_{h}"] = {'id_base': id_base, 'dias': dias, 'inicio': h, 'duracion': dur, 'label': lbl}

    # Bloques comunes
    add_b(1, ['Lu', 'Mi', 'Vi'], 50, "LMV")
    add_b(2, ['Ma', 'Ju'], 80, "MJ")
    add_b(8, ['Lu','Ma','Mi','Ju'], 50, "LMWJ")
    add_b(13, ['Lu', 'Mi'], 110, "LW (Largo)")
    add_b(15, ['Ma', 'Ju'], 110, "MJ (Largo)")
    return bloques

def mins_to_str(minutes):
    h, m = divmod(int(minutes), 60)
    ampm = "AM" if h < 12 else "PM"
    h = h if h <= 12 else h - 12
    if h == 0: h = 12
    return f"{h:02d}:{m:02d} {ampm}"

# ==============================================================================
# 3. CLASES DE ESTRUCTURA
# ==============================================================================
class Seccion:
    def __init__(self, uid, codigo, nombre, creditos, cupo, candidatos, tipo_req):
        self.uid = uid
        self.codigo = str(codigo).upper()
        self.nombre = str(nombre)
        self.creditos = int(creditos)
        self.cupo = int(cupo)
        self.tipo_salon_req = str(tipo_req).upper()
        self.candidatos = [c.strip().upper() for c in str(candidatos).split(',') if c.strip()] if pd.notna(candidatos) else []

class Profesor:
    def __init__(self, nombre, carga_min, carga_max):
        self.nombre = str(nombre).upper()
        self.carga_min = float(carga_min)
        self.carga_max = float(carga_max)

# ==============================================================================
# 4. MOTOR PLATINUM CON RESTRICCIONES DINÁMICAS
# ==============================================================================
class PlatinumEngine:
    def __init__(self, secciones, profesores, salones, zona, restricciones_interfaz):
        self.secciones = secciones
        self.profesores_dict = {p.nombre: p for p in profesores}
        self.salones = salones
        self.bloques = generar_bloques_por_zona(zona)
        self.restricciones = restricciones_interfaz
        self.hora_univ = (630, 750) if zona == "CENTRAL" else (600, 720)

    def es_valido(self, bloque_key, prof_nombre, salon, oc_prof, oc_salon):
        b = self.bloques[bloque_key]
        ini, fin = b['inicio'], b['inicio'] + b['duracion']

        # 1. Choque Hora Universal (Ma/Ju)
        if any(d in ['Ma', 'Ju'] for d in b['dias']):
            if max(ini, self.hora_univ[0]) < min(fin, self.hora_univ[1]): return False

        # 2. RESTRICCIONES DE LA APLICACIÓN (Interfaz)
        if prof_nombre in self.restricciones:
            for res in self.restricciones[prof_nombre]:
                if res['dia'] in b['dias']:
                    if max(ini, res['ini']) < min(fin, res['fin']): return False

        # 3. Choques de Horario (Salón y Profesor)
        for d in b['dias']:
            for ocup in oc_salon.get((salon.codigo, d), []):
                if max(ini, ocup[0]) < min(fin, ocup[1]): return False
            if prof_nombre != "TBA":
                for ocup in oc_prof.get((prof_nombre, d), []):
                    if max(ini, ocup[0]) < min(fin, ocup[1]): return False
        return True

    def generar_solucion(self):
        solucion = []
        oc_p, oc_s = {}, {}
        cargas = {p: 0 for p in self.profesores_dict}
        
        for sec in sorted(self.secciones, key=lambda x: x.cupo, reverse=True):
            # Buscar profesor disponible (priorizando carga mínima)
            candidatos = [c for c in sec.candidatos if c in self.profesores_dict and (cargas[c] + sec.creditos) <= self.profesores_dict[c].carga_max]
            candidatos.sort(key=lambda c: (cargas[c] >= self.profesores_dict[c].carga_min, cargas[c]))
            prof = candidatos[0] if candidatos else "TBA"

            # Buscar espacio
            asignado = False
            pool_b = list(self.bloques.keys())
            random.shuffle(pool_b)
            
            # Filtrar salones por capacidad
            pool_s = [s for s in self.salones if s.capacidad >= sec.cupo]
            random.shuffle(pool_s)

            for s in pool_s:
                for bk in pool_b:
                    if self.es_valido(bk, prof, s, oc_p, oc_s):
                        if prof != "TBA": cargas[prof] += sec.creditos
                        # Registrar ocupación
                        b = self.bloques[bk]
                        for d in b['dias']:
                            ks, kp = (s.codigo, d), (prof, d)
                            oc_s.setdefault(ks, []).append((b['inicio'], b['inicio']+b['duracion']))
                            if prof != "TBA": oc_p.setdefault(kp, []).append((b['inicio'], b['inicio']+b['duracion']))
                        
                        solucion.append({'sec': sec, 'prof': prof, 'bloque': bk, 'salon': s.codigo})
                        asignado = True; break
                if asignado: break
        return solucion

# ==============================================================================
# 5. INTERFAZ DE USUARIO (STREAMLIT)
# ==============================================================================
def main():
    st.title("🏛️ UPRM Platinum Scheduler")
    
    if 'restricciones' not in st.session_state: st.session_state.restricciones = {}
    if 'resultado' not in st.session_state: st.session_state.resultado = None

    with st.sidebar:
        st.header("⚙️ Configuración")
        zona = st.selectbox("Zona", ["CENTRAL", "PERIFERICA"])
        file = st.file_uploader("Subir Excel (456.xlsx)", type=["xlsx"])

    if file:
        xls = pd.ExcelFile(file)
        df_p = pd.read_excel(xls, 'Profesores')
        df_c = pd.read_excel(xls, 'Cursos')
        df_s = pd.read_excel(xls, 'Salones')

        # SECCIÓN DE RESTRICCIONES EN LA APP
        with st.expander("🚫 GESTOR DE RESTRICCIONES DOCENTES", expanded=True):
            cols = st.columns([3, 2, 2, 2, 1])
            profes_lista = sorted(df_p['Nombre'].unique())
            
            with cols[0]: p_sel = st.selectbox("Seleccionar Profesor", profes_lista)
            with cols[1]: d_sel = st.selectbox("Día", ["Lu", "Ma", "Mi", "Ju", "Vi"])
            with cols[2]: t_ini = st.time_input("Desde", datetime.strptime("08:00", "%H:%M"))
            with cols[3]: t_fin = st.time_input("Hasta", datetime.strptime("12:00", "%H:%M"))
            with cols[4]: 
                st.write(" ")
                if st.button("➕"):
                    if p_sel not in st.session_state.restricciones: st.session_state.restricciones[p_sel] = []
                    st.session_state.restricciones[p_sel].append({
                        'dia': d_sel, 
                        'ini': t_ini.hour*60 + t_ini.minute, 
                        'fin': t_fin.hour*60 + t_fin.minute
                    })

            # Mostrar restricciones activas
            if st.session_state.restricciones:
                st.markdown("---")
                for prof, res_list in st.session_state.restricciones.items():
                    for i, r in enumerate(res_list):
                        c1, c2 = st.columns([8, 1])
                        c1.caption(f"📌 **{prof}**: {r['dia']} ({mins_to_str(r['ini'])} - {mins_to_str(r['fin'])})")
                        if c2.button("🗑️", key=f"del_{prof}_{i}"):
                            st.session_state.restricciones[prof].pop(i)
                            st.rerun()

        if st.button("🚀 GENERAR HORARIO", use_container_width=True):
            # Preparar Objetos
            profs = [Profesor(r['Nombre'], r['Carga_Min'], r['Carga_Max']) for _, r in df_p.iterrows()]
            salones = [type('Salon', (), {'codigo': r['CODIGO'], 'capacidad': r['CAPACIDAD']}) for _, r in df_s.iterrows()]
            secciones = []
            for _, r in df_c.iterrows():
                for i in range(int(r['CANTIDAD_SECCIONES'])):
                    secciones.append(Seccion(f"{r['CODIGO']}-{i+1}", r['CODIGO'], r['NOMBRE'], r['CREDITOS'], r['CUPO'], r['CANDIDATOS'], r['TIPO_SALON']))

            engine = PlatinumEngine(secciones, profs, salones, zona, st.session_state.restricciones)
            with st.spinner("Optimizando..."):
                st.session_state.resultado = engine.generar_solucion()
                st.success("¡Horario Generado!")

        if st.session_state.resultado:
            res = st.session_state.resultado
            bloques_ref = generar_bloques_por_zona(zona)
            
            final_data = []
            for item in res:
                b = bloques_ref[item['bloque']]
                final_data.append({
                    'Sección': item['sec'].uid,
                    'Curso': item['sec'].nombre,
                    'Profesor': item['prof'],
                    'Días': "".join(b['dias']),
                    'Horario': f"{mins_to_str(b['inicio'])} - {mins_to_str(b['inicio']+b['duracion'])}",
                    'Salón': item['salon']
                })
            
            st.dataframe(pd.DataFrame(final_data), use_container_width=True)

if __name__ == "__main__":
    main()
