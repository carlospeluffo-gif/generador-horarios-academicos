import streamlit as st
import pandas as pd
import numpy as np
import random
import copy
import io
import plotly.express as px
from datetime import datetime

# ==============================================================================
# 1. ESTÉTICA PLATINUM ORIGINAL (RESTAURADA)
# ==============================================================================
st.set_page_config(page_title="UPRM Scheduler Platinum", page_icon="🏛️", layout="wide")

st.markdown("""
<style>
    .stApp { 
        background-color: #000000; 
        background-image: linear-gradient(rgba(15, 15, 15, 0.50), rgba(15, 15, 15, 0.50)), url("https://www.transparenttextures.com/patterns/cubes.png"); 
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
    [data-testid="stDataFrame"] { 
        background-color: #111; 
        border: 1px solid #333; 
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. ESTRUCTURAS DE DATOS (NUEVAS CAPACIDADES)
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
        self.es_graduado_req = "GRADUADOS" in self.cands_list
        self.es_lab = "LAB" in self.uid or "LAB" in self.cod_base

class Profesor:
    def __init__(self, nombre, c_min, c_max, es_graduado=False, recibe=None):
        self.nombre = str(nombre).strip().upper()
        self.c_min, self.c_max = float(c_min), float(c_max)
        self.es_graduado = es_graduado
        self.recibe = recibe if recibe else []

# ==============================================================================
# 3. MOTOR DE PLANIFICACIÓN (TESIS COMPLIANT)
# ==============================================================================
class PlatinumEngine:
    def __init__(self, secciones, profesores, salones, zona):
        self.secciones = secciones
        self.profes_dict = {p.nombre: p for p in profesores}
        self.salones = salones
        self.zona = zona
        self.h_univ = (630, 750) if zona == "CENTRAL" else (600, 720)
        self.bloques = self._generar_bloques(zona)

    def _generar_bloques(self, zona):
        b = {}
        h_ini = [h*60 + 30 for h in range(7, 20)] if zona == "CENTRAL" else [h*60 for h in range(7, 20)]
        for h in h_ini:
            b[f"LMV_{h}"] = {'dias': ['Lu','Mi','Vi'], 'ini': h, 'fin': h+50}
            b[f"MJ_{h}"] = {'dias': ['Ma','Ju'], 'ini': h, 'fin': h+80}
        return b

    def ejecutar(self):
        res, oc_p, oc_s, cargas = [], {}, {}, {p: 0 for p in self.profes_dict}
        mapa_teoria = {}
        tba_report = []

        # Prioridad: Teorías -> Labs (Para que el lab sepa cuándo fue la teoría)
        sec_ord = sorted(self.secciones, key=lambda x: (x.es_lab, not x.es_graduado_req))

        for sec in sec_ord:
            # Selección de Candidatos (Lógica de Graduados incluida)
            if sec.es_graduado_req:
                pool_p = [p.nombre for p in self.profes_dict.values() if p.es_graduado]
            else:
                pool_p = [c for c in sec.cands_list if c in self.profes_dict]

            prof = "TBA"
            if pool_p:
                validos = [c for c in pool_p if cargas[c] + sec.creditos <= self.profes_dict[c].c_max]
                if validos:
                    validos.sort(key=lambda c: (cargas[c] >= self.profes_dict[c].c_min, cargas[c]))
                    prof = validos[0]
                else: tba_report.append(f"Sección {sec.uid}: Candidatos sin carga disponible.")

            # Selección de Bloque y Salón
            pool_b = list(self.bloques.keys())
            if sec.es_lab:
                # Regla de Lab: Buscar horario después de la teoría si existe
                teoria_key = sec.cod_base.replace(" LAB", "").strip()
                if teoria_key in mapa_teoria:
                    h_teoria = mapa_teoria[teoria_key]['ini']
                    pool_b = [k for k in pool_b if self.bloques[k]['ini'] >= h_teoria] or pool_b

            asignado = False
            random.shuffle(pool_b)
            for bk in pool_b:
                b = self.bloques[bk]
                
                # Bloqueo por clases que el graduado RECIBE
                p_obj = self.profes_dict.get(prof)
                if p_obj and p_obj.recibe:
                    skip = False
                    # (Lógica simplificada de choque con sus clases recibidas)
                    if any(c in sec.cod_base for c in p_obj.recibe): skip = True # No puede dar la que recibe
                    if skip: continue

                # Filtro Salón
                s_validos = [s for s in self.salones if s.capacidad >= sec.cupo and (s.tipo == sec.tipo_salon or sec.tipo_salon == 'GENERAL')]
                random.shuffle(s_validos)
                
                for s in s_validos:
                    # Validar choques físicos
                    choque = False
                    for d in b['dias']:
                        if (s.codigo, d) in oc_s or (prof != "TBA" and (prof, d) in oc_p):
                            choque = True; break
                    
                    if not choque:
                        cargas[prof] += sec.creditos
                        for d in b['dias']:
                            oc_s[(s.codigo, d)] = True
                            if prof != "TBA": oc_p[(prof, d)] = True
                        
                        res.append({'Sección': sec.uid, 'Candidato': prof, 'Días': "".join(b['dias']), 'Hora': f"{int(b['ini']//60):02d}:{int(b['ini']%60):02d}", 'Salón': s.codigo})
                        if not sec.es_lab: mapa_teoria[sec.cod_base] = b
                        asignado = True; break
                if asignado: break
            
            if not asignado:
                res.append({'Sección': sec.uid, 'Candidato': "TBA", 'Días': "N/A", 'Hora': "N/A", 'Salón': "N/A"})

        return pd.DataFrame(res), tba_report, cargas

# ==============================================================================
# 4. INTERFAZ (IGUAL A LA ORIGINAL)
# ==============================================================================
def main():
    st.title("🏛️ UPRM Scheduler Platinum")
    
    with st.sidebar:
        st.header("Parámetros")
        zona = st.selectbox("📍 Zona", ["CENTRAL", "PERIFERICA"])
        excel_file = st.file_uploader("📂 Cargar Excel Maestro", type=['xlsx'])
        st.markdown("---")
        st.info("Nota: Use la pestaña 'Graduados' para especificar las clases que reciben.")

    if excel_file:
        try:
            xls = pd.ExcelFile(excel_file)
            df_cur = pd.read_excel(xls, 'Cursos')
            df_pro = pd.read_excel(xls, 'Profesores')
            df_sal = pd.read_excel(xls, 'Salones')
            df_gra = pd.read_excel(xls, 'Graduados') if 'Graduados' in xls.sheet_names else pd.DataFrame()

            # Procesar datos
            profesores = [Profesor(r['Nombre'], r['Carga_Min'], r['Carga_Max']) for _, r in df_pro.iterrows()]
            if not df_gra.empty:
                for _, r in df_gra.iterrows():
                    recibe = [c.strip().upper() for c in str(r.get('CLASES A RECIBIR','')).split(',') if c.strip()]
                    profesores.append(Profesor(r['NOMBRE'], 0, r['CREDITOS'], True, recibe))

            secciones = []
            for _, r in df_cur.iterrows():
                cupo_t = int(r['CUPO'])
                # Si CANTIDAD_SECCIONES existe, la usamos, si no calculamos por 30
                try: 
                    n_sec = int(r['CANTIDAD_SECCIONES'])
                except: 
                    n_sec = max(1, cupo_t // 30)
                
                for i in range(1, n_sec + 1):
                    secciones.append(Seccion(f"{r['CODIGO']}-{i:02d}", r['CODIGO'], r['CREDITOS'], cupo_t//n_sec, r['CANDIDATOS'], r.get('TIPO_SALON','GENERAL')))

            salones = [type('S',(),{'codigo':str(r['CODIGO']), 'capacidad':int(r['CAPACIDAD']), 'tipo':str(r['TIPO']).upper()}) for _,r in df_sal.iterrows()]

            if st.button("🚀 GENERAR HORARIO"):
                engine = PlatinumEngine(secciones, profesores, salones, zona)
                df_final, tbas, cargas_f = engine.ejecutar()

                # Visualización
                st.subheader("🗓️ Horario Resultante")
                st.dataframe(df_final, use_container_width=True, hide_index=True)

                # Reporte de Tesis (Recomendación del Asesor)
                if tbas:
                    with st.expander("⚠️ Reporte de Carga Pendiente"):
                        for t in tbas: st.write(f"- {t}")

                # Descarga
                csv = df_final.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Descargar Planificación", csv, "plan_academico.csv", "text/csv")

        except Exception as e:
            st.error(f"Error en la estructura del Excel: {e}")

if __name__ == "__main__":
    main()
