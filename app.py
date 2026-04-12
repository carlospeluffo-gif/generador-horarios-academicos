import streamlit as st
import pandas as pd
import numpy as np
import random
import io
import time
import math
from copy import deepcopy
from collections import defaultdict
import plotly.express as px
import plotly.graph_objects as go

# ------------------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA Y ESTILOS (MANTENIDOS)
# ------------------------------------------------------------------------------
st.set_page_config(page_title="UPRM Scheduler Pro", page_icon="🏛️", layout="wide")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;700;900&family=Source+Sans+Pro:wght@300;400;600&display=swap');
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #e9f0e8 100%); background-attachment: fixed; color: #1a1a1a; }
    .stApp::before { content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-image: radial-gradient(circle at 20% 30%, rgba(0,75,35,0.02) 0%, transparent 20%), radial-gradient(circle at 80% 70%, rgba(198,146,20,0.02) 0%, transparent 25%), repeating-linear-gradient(45deg, rgba(0,75,35,0.01) 0px, rgba(0,75,35,0.01) 2px, transparent 2px, transparent 8px); pointer-events: none; z-index: 0; }
    .main > div { position: relative; z-index: 1; }
    .rum-header { display: flex; justify-content: space-between; align-items: center; padding: 25px 50px; background: linear-gradient(105deg, rgba(255,255,255,0.95) 0%, rgba(248,250,248,0.98) 100%); border-bottom: 6px solid #004B23; margin-bottom: 35px; border-radius: 0 0 30px 30px; box-shadow: 0 15px 30px -10px rgba(0,75,35,0.15); backdrop-filter: blur(5px); z-index: 10; }
    .rum-header::after { content: ""; position: absolute; bottom: -8px; left: 10%; width: 80%; height: 3px; background: linear-gradient(90deg, transparent, #C69214, #E6B422, #C69214, transparent); border-radius: 50%; }
    .header-logo { display: flex; align-items: center; gap: 20px; }
    .header-logo img { height: 100px; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.05)); }
    .title-box { text-align: center; }
    .title-box h1 { font-family: 'Playfair Display', serif; background: linear-gradient(135deg, #004B23 0%, #0A6B3A 80%); -webkit-background-clip: text; background-clip: text; color: transparent; font-size: 3.2rem; margin: 5px 0; letter-spacing: 3px; font-weight: 900; }
    .title-box p { color: #2c3e50; letter-spacing: 4px; font-size: 0.9rem; text-transform: uppercase; }
    .subtitle-accent { color: #C69214; font-weight: 700; }
    .glass-card { background: rgba(255,255,255,0.7); backdrop-filter: blur(12px); border-radius: 24px; padding: 28px; border: 1px solid rgba(0,75,35,0.15); box-shadow: 0 20px 35px -8px rgba(0,75,35,0.1); margin-bottom: 25px; color: #1a1a1a; }
    .stButton > button { background: linear-gradient(145deg, #004B23 0%, #0A6B3A 100%); color: white; font-weight: 600; border-radius: 50px; width: 100%; border: none; height: 58px; font-size: 1.2rem; box-shadow: 0 8px 15px rgba(0,75,35,0.25); text-transform: uppercase; }
    .stDownloadButton > button { background: linear-gradient(145deg, #C69214 0%, #E6B422 100%); color: #1a1a1a; font-weight: 700; border-radius: 50px; box-shadow: 0 8px 15px rgba(198,146,20,0.25); height: 50px; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, rgba(255,255,255,0.95) 0%, rgba(240,245,240,0.98) 100%); border-right: 2px solid #C69214; }
    h2, h3 { color: #004B23; font-family: 'Playfair Display', serif; }
    h2 { border-left: 6px solid #C69214; padding-left: 20px; }
    .status-badge { background: rgba(0,75,35,0.08); border: 1.5px solid #004B23; color: #004B23; padding: 14px 18px; border-radius: 60px; text-align: center; font-weight: 700; }
    .stDataFrame th { background-color: #004B23 !important; color: white !important; }
    footer {visibility: hidden;}
</style>
<div class="rum-header">
    <div class="header-logo"><img src="https://www.uprm.edu/portales/wp-content/uploads/sites/55/2022/05/Tarzan_7896.png"></div>
    <div class="title-box"><h1>UPRM TIMETABLE SYSTEM</h1><p><span class="subtitle-accent">COLEGIO DE ARTES Y CIENCIAS</span> · OPTIMIZACIÓN PRO</p></div>
    <div class="header-logo"><img src="https://www.uprm.edu/portada/wp-content/uploads/sites/24/2023/08/logo-rum-200x200-1-150x150.png"></div>
    <div style="width:150px;"></div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# UTILIDADES Y TABLAS
# ------------------------------------------------------------------------------
COMPENSACION_TABLE = [
    (1,1,44,0.0),(1,45,74,0.5),(1,75,104,1.0),(1,105,134,1.5),(1,135,164,2.0),
    (2,1,37,0.0),(2,38,52,0.5),(2,53,67,1.0),(2,68,82,1.5),(2,83,97,2.0),
    (2,98,112,2.5),(2,113,127,3.0),(2,128,142,3.5),(2,143,147,4.0),
    (3,1,34,0.0),(3,35,44,0.5),(3,45,54,1.0),(3,55,64,1.5),(3,65,74,2.0),
    (3,75,84,2.5),(3,85,94,3.0),(3,95,104,3.5),(3,105,114,4.0),(3,115,124,4.5),
    (3,125,134,5.0),(3,135,144,5.5),(3,145,154,6.0),
    (4,1,33,0.0),(4,34,41,0.5),(4,42,48,1.0),(4,49,56,1.5),(4,57,63,2.0),
    (4,64,71,2.5),(4,72,78,3.0),(4,79,86,3.5),(4,87,93,4.0),(4,94,101,4.5),
    (4,102,108,5.0),(4,109,116,5.5),(4,117,123,6.0),(4,124,131,6.5),(4,132,138,7.0),
    (4,139,146,7.5),(4,147,153,8.0),
    (5,1,32,0.0),(5,33,38,0.5),(5,39,44,1.0),(5,45,50,1.5),(5,51,56,2.0),
    (5,57,62,2.5),(5,63,68,3.0),(5,69,74,3.5),(5,75,80,4.0),(5,81,86,4.5),
    (5,87,92,5.0),(5,93,98,5.5),(5,99,104,6.0),(5,105,110,6.5),(5,111,116,7.0),
    (5,117,122,7.5),(5,123,128,8.0)
]
def get_creditos_reales(cr, cupo):
    for (cb, mn, mx, ex) in COMPENSACION_TABLE:
        if cb==cr and mn<=cupo<=mx: return float(cr)+ex
    return float(cr)+max([ex for (cb,mn,mx,ex) in COMPENSACION_TABLE if cb==cr and cupo>=mn]+[0])
def mins_to_str(m):
    h,mn=divmod(int(m),60); am="AM" if h<12 else "PM"; h=h if h<=12 else h-12
    if h==0: h=12
    return f"{h:02d}:{mn:02d} {am}"
def str_to_mins(t):
    t=t.strip().upper(); parts=t.split(); hm=parts[0]; ampm=parts[1] if len(parts)>1 else "AM"
    h,m=map(int,hm.split(':'))
    if ampm=="PM" and h!=12: h+=12
    if ampm=="AM" and h==12: h=0
    return h*60+m
PATRONES = {
    3:[{"name":"Lu-Mi-Vi","days":{"Lu":1,"Mi":1,"Vi":1}},{"name":"Ma-Ju","days":{"Ma":1.5,"Ju":1.5}},
       {"name":"Ma (Intensivo)","days":{"Ma":3}},{"name":"Ju (Intensivo)","days":{"Ju":3}}],
    4:[{"name":"Lu-Ma-Mi-Ju","days":{"Lu":1,"Ma":1,"Mi":1,"Ju":1}},{"name":"Lu-Ma-Mi-Vi","days":{"Lu":1,"Ma":1,"Mi":1,"Vi":1}},
       {"name":"Lu-Ma-Ju-Vi","days":{"Lu":1,"Ma":1,"Ju":1,"Vi":1}},{"name":"Lu-Mi-Ju-Vi","days":{"Lu":1,"Mi":1,"Ju":1,"Vi":1}},
       {"name":"Ma-Mi-Ju-Vi","days":{"Ma":1,"Mi":1,"Ju":1,"Vi":1}},{"name":"Lu-Mi","days":{"Lu":2,"Mi":2}},
       {"name":"Lu-Vi","days":{"Lu":2,"Vi":2}},{"name":"Ma-Ju","days":{"Ma":2,"Ju":2}},{"name":"Mi-Vi","days":{"Mi":2,"Vi":2}}],
    5:[{"name":"Lu-Ma-Mi-Ju-Vi","days":{"Lu":1,"Ma":1,"Mi":1,"Ju":1,"Vi":1}},
       {"name":"Lu-Ma-Mi-Vi","days":{"Lu":1,"Ma":1,"Mi":1,"Vi":2}},{"name":"Lu-Ma-Ju-Vi","days":{"Lu":1,"Ma":1,"Ju":1,"Vi":2}},
       {"name":"Lu-Mi-Ju-Vi","days":{"Lu":1,"Mi":1,"Ju":1,"Vi":2}},{"name":"Ma-Mi-Ju-Vi","days":{"Ma":1,"Mi":1,"Ju":1,"Vi":2}},
       {"name":"Lu-Mi-Vi","days":{"Lu":2,"Mi":2,"Vi":1}},{"name":"Ma-Ju-Vi","days":{"Ma":1.5,"Ju":1.5,"Vi":2}},
       {"name":"Lu-Ma-Mi","days":{"Lu":2,"Ma":1,"Mi":2}}]
}
def format_horario(pat, ini):
    parts=[]
    for d,c in pat['days'].items():
        fin=ini+int(c*50)
        parts.append(f"{d}: {mins_to_str(ini)}-{mins_to_str(fin)}")
    return " | ".join(parts)
def exportar_todo(df):
    out=io.BytesIO()
    with pd.ExcelWriter(out, engine='xlsxwriter') as w:
        df.to_excel(w, sheet_name='Maestro', index=False)
        for p in df['Persona'].unique():
            if str(p) not in ["TBA","GRADUADOS"]:
                clean="".join(c for c in str(p) if c.isalnum() or c==' ')[:25]
                df[df['Persona']==p].to_excel(w, sheet_name=f"User_{clean}", index=False)
    return out.getvalue()

class Seccion:
    def __init__(self,cod,cred,cupo,cands,tipo_salon):
        self.cod=str(cod); self.creditos=int(cred); self.cupo=int(cupo)
        if isinstance(cands,list): raw=[c.strip().upper() for c in cands if c.strip()]
        else: raw=[c.strip().upper() for c in str(cands).split(',') if c.strip() and str(c).upper()!='NAN']
        self.cands=list(set(raw))
        try:
            t=float(tipo_salon)
            self.tipo_salon=3 if abs(t-1.3)<0.01 else int(round(t))
        except: self.tipo_salon=1
        base=self.cod.split('-')[0].upper().replace(" ","")
        self.es_fusionable=base in ["MATE3171","MATE3172","MATE3173"]
        self.prof_preasignado=None
        self.es_grande=self.cupo>=85

class Profesor:
    def __init__(self,nom,cmin,cmax,pdias,phoras,bdias,bini,bfin,prefs,comp,aceptag,cint):
        self.nombre=nom.upper().strip()
        self.carga_min=float(cmin) if pd.notnull(cmin) and cmin!='' else 0.0
        self.carga_max=float(cmax) if pd.notnull(cmax) and cmax!='' else 12.0
        self.pref_dias_set=set()
        if pdias and isinstance(pdias,str):
            for tok in pdias.replace(',',' ').upper().split():
                if tok in ('L','LU'): self.pref_dias_set.add('Lu')
                elif tok in ('M','MA'): self.pref_dias_set.add('Ma')
                elif tok in ('W','MI'): self.pref_dias_set.add('Mi')
                elif tok in ('J','JU'): self.pref_dias_set.add('Ju')
                elif tok in ('V','VI'): self.pref_dias_set.add('Vi')
        self.pref_horas=phoras if isinstance(phoras,str) else 'ANY'
        self.preferencias=[]
        if isinstance(prefs,list): self.preferencias=[c.upper().strip() for c in prefs if c and str(c).upper()!='NAN']
        self.compensacion=str(comp).upper().strip() in ('SI','SÍ','YES','1')
        self.acepta_grandes=int(aceptag) if pd.notnull(aceptag) and aceptag!='' else 0
        try: self.cursos_intensivos=int(cint)
        except: self.cursos_intensivos=0
        self.bloqueos=[]
        if bdias and isinstance(bdias,str) and bdias.strip():
            dmap={'L':'Lu','M':'Ma','MI':'Mi','J':'Ju','V':'Vi'}
            limpio=bdias.upper().replace(' ','').replace(',','')
            dset=set(); i=0
            while i<len(limpio):
                if limpio[i:i+2]=='MI': dset.add('Mi'); i+=2
                else:
                    if limpio[i] in dmap: dset.add(dmap[limpio[i]])
                    i+=1
            if dset:
                try:
                    s=str_to_mins(bini) if bini and pd.notnull(bini) else None
                    e=str_to_mins(bfin) if bfin and pd.notnull(bfin) else None
                    if s is not None and e is not None: self.bloqueos.append((dset,s,e))
                except: pass
    def prioridad_curso(self,cod):
        for i,p in enumerate(self.preferencias):
            if p in cod: return 1.0/(i+1)
        return 0.0

def compatible_tipo(ct,st):
    if isinstance(st,float):
        if 1.9<=st<=2.1: sc=2
        elif st>=2.9: sc=3
        else: sc=1
    else: sc=int(st)
    if ct==2: return sc==2
    if ct==3: return sc==3
    return sc!=2

# ------------------------------------------------------------------------------
# NUEVO MOTOR ULTRA-ROBUSTO
# ------------------------------------------------------------------------------
class RobustScheduler:
    def __init__(self, df_cursos, df_profes, df_salones, zona, df_grad=None):
        self.zona=zona
        # Salones
        df_salones.columns=[c.strip().upper() for c in df_salones.columns]
        self.salones=[]; self.mega_salones=set()
        for _,r in df_salones.iterrows():
            cod=str(r['CODIGO']).strip().upper()
            cap=int(r['CAPACIDAD']) if pd.notnull(r['CAPACIDAD']) else 25
            tipo=float(r['TIPO']) if pd.notnull(r['TIPO']) else 1.0
            self.salones.append({'CODIGO':cod,'CAPACIDAD':cap,'TIPO':tipo})
            if any(x in cod.replace(" ","").replace("-","") for x in ["FA","FB","FC"]): self.mega_salones.add(cod)
        self.salon_tipo={s['CODIGO']:s['TIPO'] for s in self.salones}
        self.salon_cap={s['CODIGO']:s['CAPACIDAD'] for s in self.salones}
        # Profesores
        self.profesores={}
        if df_profes is not None and not df_profes.empty:
            df_profes.columns=[c.strip().upper() for c in df_profes.columns]
            for _,r in df_profes.iterrows():
                prefs=[str(r.get(c,'')).strip().upper() for c in ['PREF1','PREF2','PREF3'] if pd.notnull(r.get(c)) and str(r.get(c)).strip().upper()!='NAN']
                p=Profesor(str(r['NOMBRE']), r.get('CARGA_MIN',0), r.get('CARGA_MAX',15),
                           r.get('PREF_DIAS',''), r.get('PREF_HORAS','ANY'),
                           r.get('BLOQUEO_DIAS',''), r.get('BLOQUEO_HORA_INI',''), r.get('BLOQUEO_HORA_FIN',''),
                           prefs, r.get('COMPENSACION','NO'), r.get('ACEPTA_GRANDES',0), r.get('CURSOS_INTENSIVOS',0))
                self.profesores[p.nombre]=p
        # Secciones
        self.secciones=[]
        df_cursos.columns=[c.strip().upper() for c in df_cursos.columns]
        agrup={}
        for _,r in df_cursos.iterrows():
            cod=str(r['CODIGO']).strip().upper()
            if cod not in agrup:
                t=r.get('TIPO_SALON',1)
                try:
                    tv=float(t); ts=3 if abs(tv-1.3)<0.01 else int(round(tv))
                except: ts=1
                agrup[cod]={'creditos':int(r['CREDITOS']),'demanda':int(r.get('DEMANDA',0)),
                            'cupo_tipico':int(r.get('CUPO',30)),'candidatos':r.get('CANDIDATOS',''),'tipo_salon':ts}
            else: agrup[cod]['demanda']+=int(r.get('DEMANDA',0))
        for cod,dat in agrup.items():
            dem=dat['demanda']; cupo_tip=dat['cupo_tipico']
            cands=[c.strip().upper() for c in str(dat['candidatos']).split(',') if c.strip() and str(c).upper()!='NAN']
            acepta_comp=any(c in self.profesores and self.profesores[c].compensacion for c in cands)
            if acepta_comp and dem>cupo_tip: cupo_ef=min(dem,85)
            else: cupo_ef=cupo_tip
            nsec=math.ceil(dem/cupo_ef) if dem>0 else 1
            est=[cupo_ef]*(nsec-1); resto=dem-sum(est); est.append(resto if resto>0 else cupo_ef)
            for i,cp in enumerate(est): self.secciones.append(Seccion(f"{cod}-{i+1:02d}",dat['creditos'],cp,dat['candidatos'],dat['tipo_salon']))
        self._preasignar_profesores_robusto()
        # Graduados
        self.grad_rec={}
        if df_grad is not None and not df_grad.empty:
            df_grad.columns=[c.strip().upper() for c in df_grad.columns]
            for _,r in df_grad.iterrows():
                nom=str(r['NOMBRE']).strip().upper()
                rec=str(r['RECIBE']) if pd.notnull(r['RECIBE']) else ''
                cods=[c.strip().upper() for c in rec.split(',') if c.strip()]
                self.grad_rec[nom]=cods
        # Límites horarios
        if zona=="CENTRAL":
            self.h_uni=(630,750); self.lim_op=(450,1110); self.bloques=list(range(450,1051,60))
        else:
            self.h_uni=(600,720); self.lim_op=(420,1080); self.bloques=list(range(420,1021,60))
        # Opciones por sección
        self.opciones_por_seccion={}
        for idx,s in enumerate(self.secciones):
            self.opciones_por_seccion[idx]=self._generar_opciones(s)

    def get_sec_creditos(self,s,prof):
        if prof in self.profesores and self.profesores[prof].compensacion:
            return get_creditos_reales(s.creditos,s.cupo)
        return float(s.creditos)

    def _preasignar_profesores_robusto(self):
        carga={p:0.0 for p in self.profesores}; carga["GRADUADOS"]=0.0; carga["TBA"]=0.0
        cap_rest={p.nombre:p.carga_max for p in self.profesores.values()}
        unicas=[]; multiples=[]
        for s in self.secciones:
            cands_val=[c for c in s.cands if c in self.profesores]
            if not cands_val:
                if "GRADUADOS" in s.cands: s.prof_preasignado="GRADUADOS"; carga["GRADUADOS"]+=self.get_sec_creditos(s,"GRADUADOS")
                else: s.prof_preasignado="TBA"; carga["TBA"]+=self.get_sec_creditos(s,"TBA")
            elif len(cands_val)==1: unicas.append(s)
            else: multiples.append(s)
        for s in unicas:
            p=s.cands[0]; cred=self.get_sec_creditos(s,p); s.prof_preasignado=p; carga[p]+=cred; cap_rest[p]-=cred
        pref={}
        for s in multiples:
            pref[s]={}
            for p in s.cands:
                if p in self.profesores:
                    pr=self.profesores[p].prioridad_curso(s.cod)
                    if s.es_grande and self.profesores[p].acepta_grandes==1: pr+=0.5
                    pref[s][p]=pr
                else: pref[s][p]=0.0
        multiples.sort(key=lambda s: (len(s.cands), -max(pref[s].values())))
        for s in multiples:
            cands_ord=sorted(s.cands, key=lambda p: pref[s].get(p,0), reverse=True)
            asig=False
            for p in cands_ord:
                if p in cap_rest and cap_rest[p]>=self.get_sec_creditos(s,p):
                    s.prof_preasignado=p; cred=self.get_sec_creditos(s,p); carga[p]+=cred; cap_rest[p]-=cred; asig=True; break
            if not asig:
                p=cands_ord[0]; s.prof_preasignado=p; cred=self.get_sec_creditos(s,p); carga[p]+=cred
                if p in cap_rest: cap_rest[p]-=cred
        # Ajuste con recocido para cargas
        def penalidad():
            pen=0
            for p,c in carga.items():
                if p in self.profesores:
                    if c<self.profesores[p].carga_min-1.5: pen+=(self.profesores[p].carga_min-c)*10
                    elif c>self.profesores[p].carga_max+1.5: pen+=(c-self.profesores[p].carga_max)*10
            return pen
        T=100.0; pen_act=penalidad()
        for _ in range(30000):
            if pen_act==0: break
            s=random.choice(self.secciones)
            p_viejo=s.prof_preasignado
            if p_viejo not in self.profesores: continue
            cands=[p for p in s.cands if p in self.profesores and p!=p_viejo]
            if not cands: continue
            p_nuevo=random.choice(cands)
            cv=self.get_sec_creditos(s,p_viejo); cn=self.get_sec_creditos(s,p_nuevo)
            carga[p_viejo]-=cv; carga[p_nuevo]+=cn
            nueva=penalidad()
            if nueva<pen_act or (T>0.01 and random.random()<math.exp((pen_act-nueva)/T)):
                pen_act=nueva; s.prof_preasignado=p_nuevo
            else: carga[p_viejo]+=cv; carga[p_nuevo]-=cn
            T*=0.995

    def _generar_opciones(self,s):
        ops=[]
        for pat in PATRONES.get(s.creditos,PATRONES[3]):
            for h in self.bloques:
                valido=True
                for d,c in pat['days'].items():
                    fin=h+int(c*50)
                    if h<self.lim_op[0] or fin>self.lim_op[1]: valido=False; break
                    if d in ["Ma","Ju"] and max(h,self.h_uni[0])<min(fin,self.h_uni[1]): valido=False; break
                    if s.creditos==3 and c>=3 and h<930: valido=False; break
                if not valido: continue
                for sal in self.salones:
                    if sal['CAPACIDAD']>=s.cupo and compatible_tipo(s.tipo_salon,sal['TIPO']):
                        ops.append((pat,h,sal['CODIGO']))
        return ops

    def _evaluar(self, ind):
        """Retorna (num_conflictos, costo_suave, carga_dict)"""
        conflictos=0; suave=0
        occ_prof=defaultdict(list); occ_sal=defaultdict(list)
        carga=defaultdict(float)
        for idx,op in enumerate(ind):
            if op is None or op>=len(self.opciones_por_seccion[idx]): conflictos+=1; continue
            s=self.secciones[idx]; prof=s.prof_preasignado
            pat,h,sal=self.opciones_por_seccion[idx][op]
            if prof=="TBA" or sal=="TBA": conflictos+=1; continue
            if prof in self.profesores:
                po=self.profesores[prof]
                if po.acepta_grandes==0 and s.es_grande: conflictos+=1
                es_int=any(c>=3 for c in pat['days'].values())
                if po.cursos_intensivos==0 and es_int: conflictos+=1
                elif po.cursos_intensivos==1 and not es_int:
                    puede_int=any(any(c>=3 for c in p['days'].values()) for p in PATRONES.get(s.creditos,PATRONES[3]))
                    if puede_int: conflictos+=1
                for (dset,st,en) in po.bloqueos:
                    for d in pat['days']:
                        if d in dset:
                            fin=h+int(pat['days'][d]*50)
                            if max(h,st)<min(fin,en): conflictos+=1
                if po.pref_horas=='AM' and h>=720: suave+=30
                elif po.pref_horas=='PM' and h<720: suave+=30
                if po.pref_dias_set:
                    for d in pat['days']:
                        if d not in po.pref_dias_set: suave+=15
            carga[prof]+=self.get_sec_creditos(s,prof)
            for d,c in pat['days'].items():
                fin=h+int(c*50)
                if prof!="GRADUADOS":
                    for (ini_ex,fin_ex) in occ_prof[(prof,d)]:
                        if max(h,ini_ex)<min(fin,fin_ex): conflictos+=1
                    occ_prof[(prof,d)].append((h,fin))
                sal_info=next(sl for sl in self.salones if sl['CODIGO']==sal)
                for (ini_ex,fin_ex,cupo_ex,fus_ex) in occ_sal[(sal,d)]:
                    if max(h,ini_ex)<min(fin,fin_ex):
                        if sal in self.mega_salones and s.es_fusionable and fus_ex:
                            if s.cupo+cupo_ex<=sal_info['CAPACIDAD']: continue
                        conflictos+=1
                occ_sal[(sal,d)].append((h,fin,s.cupo,s.es_fusionable))
        for p,c in carga.items():
            if p in self.profesores:
                po=self.profesores[p]
                if c>po.carga_max+1.5: conflictos+=1
                if c<po.carga_min-1.5: conflictos+=1
        # Doble rol graduados
        for grad,cods in self.grad_rec.items():
            dicta=[]; recibe=[]
            for idx,op in enumerate(ind):
                if op is None: continue
                s=self.secciones[idx]; prof=s.prof_preasignado
                if prof==grad: dicta.append(idx)
                codb=s.cod.split('-')[0].upper()
                if codb in cods: recibe.append(idx)
            for i_d in dicta:
                p_d,h_d,s_d=self.opciones_por_seccion[i_d][ind[i_d]]
                for i_r in recibe:
                    p_r,h_r,s_r=self.opciones_por_seccion[i_r][ind[i_r]]
                    for d_d,c_d in p_d['days'].items():
                        ini_d=h_d; fin_d=ini_d+int(c_d*50)
                        for d_r,c_r in p_r['days'].items():
                            if d_d==d_r:
                                ini_r=h_r; fin_r=ini_r+int(c_r*50)
                                if max(ini_d,ini_r)<min(fin_d,fin_r): conflictos+=1
        return conflictos, suave, dict(carga)

    def _costo_compactacion_profesores(self, ind):
        pen=0
        prof_asig=defaultdict(list)
        for idx,op in enumerate(ind):
            if op is None: continue
            s=self.secciones[idx]; prof=s.prof_preasignado
            if prof in ["TBA","GRADUADOS"] or prof not in self.profesores: continue
            pat,h,sal=self.opciones_por_seccion[idx][op]
            prof_asig[prof].append((pat,h,sal,s))
        for prof,asigs in prof_asig.items():
            dias=set(); sales=set()
            carga_tot=sum(self.get_sec_creditos(s,prof) for _,_,_,s in asigs)
            for pat,_,sal,_ in asigs:
                dias.update(pat['days'].keys()); sales.add(sal)
            if carga_tot<=9: ideal=2
            elif carga_tot<=15: ideal=3
            else: ideal=4
            exceso=len(dias)-ideal
            if exceso>0: pen+=exceso*800
            if len(sales)>1: pen+=(len(sales)-1)*600
            for d in dias:
                clases=[]
                for pat,h,_,_ in asigs:
                    if d in pat['days']:
                        ini=h; fin=ini+int(pat['days'][d]*50); clases.append((ini,fin))
                clases.sort()
                for i in range(len(clases)-1):
                    brecha=clases[i+1][0]-clases[i][1]
                    if brecha>30: pen+=brecha*3
        return pen

    def fitness(self, ind):
        c, s, _ = self._evaluar(ind)
        if c>0: return c*10000 + s
        else: return s + self._costo_compactacion_profesores(ind)

    def _reparar_local(self, ind):
        for _ in range(5):
            for idx in range(len(ind)):
                c,_,_=self._evaluar(ind)
                if c==0: break
                ops=self.opciones_por_seccion[idx]
                if not ops: continue
                mejor=ind[idx]; mejor_fit=float('inf')
                for op in range(len(ops)):
                    temp=list(ind); temp[idx]=op
                    fit=self.fitness(temp)
                    if fit<mejor_fit: mejor_fit=fit; mejor=op
                ind[idx]=mejor
        return ind

    def _ga(self, tam_pop=300, gens=500):
        def crear():
            ind=[random.randrange(len(self.opciones_por_seccion[i])) if self.opciones_por_seccion[i] else None for i in range(len(self.secciones))]
            return self._reparar_local(ind)
        pop=[crear() for _ in range(tam_pop)]
        fits=[self.fitness(ind) for ind in pop]
        best_idx=np.argmin(fits); best=pop[best_idx]; best_fit=fits[best_idx]
        for gen in range(gens):
            selec=[]
            for _ in range(tam_pop):
                i1,i2=random.sample(range(tam_pop),2)
                selec.append(pop[i1] if fits[i1]<fits[i2] else pop[i2])
            elite_n=int(tam_pop*0.2)
            idx_ord=np.argsort(fits); elite=[pop[i] for i in idx_ord[:elite_n]]
            nueva=elite[:]
            while len(nueva)<tam_pop:
                p1,p2=random.sample(selec,2)
                hijo=[]
                for i in range(len(p1)):
                    if random.random()<0.5: hijo.append(p1[i])
                    else: hijo.append(p2[i])
                if random.random()<0.3:
                    i=random.randrange(len(hijo))
                    if self.opciones_por_seccion[i]: hijo[i]=random.randrange(len(self.opciones_por_seccion[i]))
                hijo=self._reparar_local(hijo)
                nueva.append(hijo)
            pop=nueva; fits=[self.fitness(ind) for ind in pop]
            gen_best=np.argmin(fits)
            if fits[gen_best]<best_fit:
                best_fit=fits[gen_best]; best=pop[gen_best]
            if best_fit<10000: break
        return best

    def _tabu(self, ind, iters=1000):
        actual=list(ind); mejor=list(ind); mejor_fit=self.fitness(actual)
        tabu=[]; tenure=25
        for _ in range(iters):
            if mejor_fit<10000: break
            vecinos=[]
            for idx in range(len(actual)):
                ops=self.opciones_por_seccion[idx]
                if not ops: continue
                for op in range(len(ops)):
                    if (idx,op) in tabu: continue
                    vec=list(actual); vec[idx]=op
                    c,_,_=self._evaluar(vec)
                    if c>0: continue
                    fit=self.fitness(vec)
                    vecinos.append((fit,vec,(idx,op)))
            if not vecinos: break
            vecinos.sort(key=lambda x:x[0])
            fit_vec,vec,mov=vecinos[0]
            if fit_vec<mejor_fit: mejor_fit=fit_vec; mejor=vec
            actual=vec; tabu.append(mov)
            if len(tabu)>tenure: tabu.pop(0)
        return mejor

    def _sa(self, ind, temp=2000, cooling=0.99, iters=3000):
        actual=list(ind); mejor=list(ind)
        fit_act=self.fitness(actual); fit_mejor=fit_act
        for _ in range(iters):
            idx=random.randrange(len(actual))
            ops=self.opciones_por_seccion[idx]
            if not ops: continue
            op=random.randrange(len(ops))
            vec=list(actual); vec[idx]=op
            c,_,_=self._evaluar(vec)
            if c>0: continue
            fit_vec=self.fitness(vec)
            if fit_vec<fit_act or random.random()<math.exp((fit_act-fit_vec)/temp):
                actual=vec; fit_act=fit_vec
                if fit_act<fit_mejor: mejor=vec; fit_mejor=fit_act
            temp*=cooling
        return mejor

    def optimizar(self, max_intentos=3, bar=None, status=None):
        mejor_ind_global=None; mejor_fit_global=float('inf')
        historial=[]
        for intento in range(max_intentos):
            if status: status.markdown(f"**🔄 Intento {intento+1}/{max_intentos}** - GA + Reparación")
            ind=self._ga(tam_pop=300, gens=500)
            c,_,_=self._evaluar(ind)
            if c>0:
                if status: status.markdown("**🔧 Fase Tabú**")
                ind=self._tabu(ind, iters=1200)
            c,_,_=self._evaluar(ind)
            if c>0:
                if status: status.markdown("**❄️ Recocido Simulado**")
                ind=self._sa(ind, iters=3000)
            fit=self.fitness(ind)
            historial.append(fit)
            if fit<mejor_fit_global:
                mejor_fit_global=fit; mejor_ind_global=ind
            if fit<10000: break
            if bar: bar.progress((intento+1)/max_intentos)
        if mejor_ind_global is None: mejor_ind_global=ind
        # Convertir a solución
        sol=[]
        for idx,op in enumerate(mejor_ind_global):
            s=self.secciones[idx]; prof=s.prof_preasignado
            if op is None:
                pat=random.choice(PATRONES.get(s.creditos,PATRONES[3])); h=random.choice(self.bloques)
                sal=random.choice([sl['CODIGO'] for sl in self.salones if sl['CAPACIDAD']>=s.cupo]) if self.salones else "TBA"
            else: pat,h,sal=self.opciones_por_seccion[idx][op]
            sol.append({'seccion':s,'profesor':prof,'salon':sal,'patron':pat,'ini':h})
        c,_,_=self._evaluar(mejor_ind_global)
        return sol, c, historial

    def _obtener_conflictos(self, sol):
        ind=[]
        for i,asig in enumerate(sol):
            ops=self.opciones_por_seccion[i]
            encontrado=False
            for op_idx,(pat,h,sal) in enumerate(ops):
                if pat==asig['patron'] and h==asig['ini'] and sal==asig['salon']:
                    ind.append(op_idx); encontrado=True; break
            if not encontrado: ind.append(0)
        c,_,_=self._evaluar(ind)
        if c==0: return []
        return [f"Conflictos duros detectados: {c}"]

# ------------------------------------------------------------------------------
# VISUALIZACIONES (MANTENIDAS)
# ------------------------------------------------------------------------------
def generar_heatmap_plotly(sched, sol):
    dias=['Lu','Ma','Mi','Ju','Vi']; ini=sched.lim_op[0]; fin=sched.lim_op[1]
    horas=list(range(ini,fin+1,30)); matriz=np.zeros((len(horas),len(dias)))
    for a in sol:
        if a['salon']=="TBA": continue
        for d,c in a['patron']['days'].items():
            if d not in dias: continue
            di=dias.index(d); dur=int(c*50)
            for m in range(a['ini'],a['ini']+dur,30):
                if m in horas: matriz[horas.index(m),di]+=1
    porc=(matriz/len(sched.salones))*100 if sched.salones else matriz
    etq=[mins_to_str(h).replace(' AM','').replace(' PM','') for h in horas]
    fig=px.imshow(porc,labels=dict(x="Día",y="Hora",color="% Ocupación"),
                  x=dias,y=etq,color_continuous_scale='YlOrRd',aspect='auto',zmin=0,zmax=100)
    fig.update_layout(title="Ocupación de Salones",height=600)
    return fig

def generar_barras_apiladas_profesor(sol, sched):
    df=pd.DataFrame([{'Profesor':a['profesor'],'Dia':d,'Cantidad':1}
                     for a in sol if a['profesor'] not in ['TBA','GRADUADOS']
                     for d in a['patron']['days']])
    if df.empty: return go.Figure()
    piv=df.groupby(['Profesor','Dia']).size().reset_index(name='Clases')
    carga={p:0 for p in piv['Profesor'].unique()}
    for a in sol:
        if a['profesor'] in carga: carga[a['profesor']]+=sched.get_sec_creditos(a['seccion'],a['profesor'])
    profs=sorted(carga.keys(),key=lambda x:carga[x],reverse=True)
    fig=go.Figure()
    dias_u=['Lu','Ma','Mi','Ju','Vi']; cols=px.colors.qualitative.Set2[:len(dias_u)]
    for i,d in enumerate(dias_u):
        dat=piv[piv['Dia']==d]
        y=[dat[dat['Profesor']==p]['Clases'].sum() if p in dat['Profesor'].values else 0 for p in profs]
        fig.add_trace(go.Bar(name=d,x=profs,y=y,marker_color=cols[i]))
    fig.update_layout(barmode='stack',title="Clases por Profesor y Día",height=500)
    return fig

def generar_evolucion_fitness_plotly(hist):
    fit=[10000/(10000+c) for c in hist]
    fig=go.Figure()
    fig.add_trace(go.Scatter(y=fit,mode='lines+markers',line=dict(color='#D4AF37',width=3),
                             fill='tozeroy',fillcolor='rgba(212,175,55,0.2)'))
    fig.update_layout(title="Evolución del Fitness",xaxis_title="Iteración",yaxis_title="Fitness",height=450)
    return fig

def generar_calendario_visual(sol,sched,fp=None,fs=None,fc=None):
    dias=['Lu','Ma','Mi','Ju','Vi']; eventos=[]
    for a in sol:
        if fp and a['profesor']!=fp: continue
        if fs and a['salon']!=fs: continue
        if fc and fc not in a['seccion'].cod: continue
        for d,c in a['patron']['days'].items():
            ini=a['ini']; fin=ini+int(c*50)
            texto=f"<b>{a['profesor']}</b><br>{a['seccion'].cod}<br>{a['salon']}<br>{mins_to_str(ini)}-{mins_to_str(fin)}"
            eventos.append({'Dia':d,'Inicio':ini,'Fin':fin,'Profesor':a['profesor'],'Seccion':a['seccion'].cod,'Salon':a['salon'],'Texto':texto})
    if not eventos: return go.Figure()
    df=pd.DataFrame(eventos); df['Dia_idx']=df['Dia'].map({d:i for i,d in enumerate(dias)})
    profs=df['Profesor'].unique(); cols=px.colors.qualitative.Plotly[:len(profs)]
    cmap={p:cols[i%len(cols)] for i,p in enumerate(profs)}
    fig=go.Figure()
    for _,r in df.iterrows():
        fig.add_trace(go.Scatter(x=[r['Inicio'],r['Fin'],r['Fin'],r['Inicio'],r['Inicio']],
                                 y=[r['Dia_idx']-0.4,r['Dia_idx']-0.4,r['Dia_idx']+0.4,r['Dia_idx']+0.4,r['Dia_idx']-0.4],
                                 fill='toself',fillcolor=cmap[r['Profesor']],line=dict(width=1,color='black'),
                                 name=r['Profesor'],legendgroup=r['Profesor'],showlegend=False,
                                 hoverinfo='text',hovertext=r['Texto']))
    for p,c in cmap.items(): fig.add_trace(go.Scatter(x=[None],y=[None],mode='markers',marker=dict(size=10,color=c),name=p,showlegend=True))
    fig.update_layout(title="Horario Semanal",xaxis=dict(tickvals=list(range(420,1140,60)),ticktext=[mins_to_str(m).replace(' AM','').replace(' PM','') for m in range(420,1140,60)]),
                      yaxis=dict(tickvals=list(range(5)),ticktext=dias),height=600)
    return fig

def generar_reporte_pdf_html(sched,sol,cargas,master):
    total=len(sol); tba=sum(1 for a in sol if a['profesor']=='TBA')
    ctot=sum(cargas.values()); pact=len([c for c in cargas.values() if c>0])
    html=f"""<html><head><title>Reporte UPRM</title><style>body{{font-family:Segoe UI;margin:40px;}} h1{{color:#004B23;}} table{{border-collapse:collapse;width:100%;}} th,td{{border:1px solid #ddd;padding:8px;}} th{{background:#f2f2f2;}}</style></head>
    <body><h1>UPRM Scheduler - Reporte</h1><p>{time.strftime('%Y-%m-%d %H:%M:%S')}</p>
    <div style='display:flex;gap:20px;'><div><b>Total Secciones:</b> {total}</div><div><b>TBA:</b> {tba} ({tba/total*100:.1f}%)</div><div><b>Carga Total:</b> {ctot:.1f}</div><div><b>Profesores:</b> {pact}</div></div>
    <h2>Secciones TBA</h2>{master[master['Persona']=='TBA'][['ID','Asignatura','Estudiantes (Cupo)','Días','Horario','Salón']].to_html(index=False) if tba>0 else '<p>Ninguna</p>'}
    <h2>Horarios por Profesor</h2>{''.join([f'<h3>{p}</h3>{master[master["Persona"]==p][["ID","Asignatura","Días","Horario","Salón"]].to_html(index=False)}' for p in sorted(master['Persona'].unique()) if p not in ['TBA','GRADUADOS']])}
    </body></html>"""
    return html

def generar_figura_cientifica_carga(cargas,sched):
    profs=list(cargas.keys()); profs.sort(key=lambda p:cargas[p],reverse=True)
    y=[cargas[p] for p in profs]; ymin=[sched.profesores[p].carga_min for p in profs]; ymax=[sched.profesores[p].carga_max for p in profs]
    x=list(range(len(profs)))
    fig=go.Figure()
    fig.add_trace(go.Bar(x=x,y=y,name='Carga Asignada',marker=dict(color='lightgray')))
    fig.add_trace(go.Scatter(x=x,y=ymin,mode='lines+markers',name='Carga Mínima',line=dict(color='blue',dash='dot')))
    fig.add_trace(go.Scatter(x=x,y=ymax,mode='lines+markers',name='Carga Máxima',line=dict(color='orange',dash='dot')))
    fig.update_layout(title="Análisis de Carga",xaxis=dict(tickvals=x,ticktext=[f"P{i+1}" for i in x]),yaxis_title="Créditos",height=500)
    return fig

def generar_plantilla():
    out=io.BytesIO()
    with pd.ExcelWriter(out,engine='xlsxwriter') as w:
        pd.DataFrame({'CODIGO':['MATE3171'],'CREDITOS':[3],'DEMANDA':[120],'CUPO':[30],'CANDIDATOS':['PEREZ'],'TIPO_SALON':[1]}).to_excel(w,sheet_name='Cursos',index=False)
        pd.DataFrame({'NOMBRE':['PEREZ'],'CARGA_MIN':[9],'CARGA_MAX':[15],'PREF_DIAS':['LMV'],'PREF_HORAS':['AM'],'BLOQUEO_DIAS':[''],'BLOQUEO_HORA_INI':[''],'BLOQUEO_HORA_FIN':[''],'PREF1':['MATE3171'],'PREF2':[''],'PREF3':[''],'COMPENSACION':['NO'],'ACEPTA_GRANDES':[0],'CURSOS_INTENSIVOS':[0]}).to_excel(w,sheet_name='Profesores',index=False)
        pd.DataFrame({'CODIGO':['S101'],'CAPACIDAD':[30],'TIPO':[1]}).to_excel(w,sheet_name='Salones',index=False)
    return out.getvalue()

# ------------------------------------------------------------------------------
# UI PRINCIPAL
# ------------------------------------------------------------------------------
def main():
    with st.sidebar:
        st.markdown("### ⚙️ Configuración")
        zona=st.selectbox("Zona",["CENTRAL","PERIFERICA"])
        file=st.file_uploader("Subir Excel",type=['xlsx'])
        st.download_button("📥 Plantilla",generar_plantilla(),"PLANTILLA.xlsx")
    st.markdown(f"### 📍 Zona {zona}")
    if not file:
        st.markdown("<div class='glass-card'><h3>📂 Carga tu archivo Excel</h3></div>",unsafe_allow_html=True)
    else:
        if st.button("🚀 OPTIMIZAR (MODO ROBUSTO)"):
            with st.spinner("Procesando..."):
                xls=pd.ExcelFile(file)
                df_c=pd.read_excel(xls,'Cursos'); df_p=pd.read_excel(xls,'Profesores'); df_s=pd.read_excel(xls,'Salones')
                df_g=pd.read_excel(xls,'Graduados') if 'Graduados' in xls.sheet_names else None
                sched=RobustScheduler(df_c,df_p,df_s,zona,df_g)
                bar=st.progress(0); stat=st.empty()
                start=time.time()
                sol,conf,hist=sched.optimizar(max_intentos=3, bar=bar, status=stat)
                bar.progress(1.0)
                st.session_state.time=time.time()-start
                st.session_state.conf=conf; st.session_state.hist=hist; st.session_state.sched=sched; st.session_state.sol=sol
                cargas={}
                for a in sol:
                    p=a['profesor']
                    if p not in ["GRADUADOS","TBA"]: cargas[p]=cargas.get(p,0)+sched.get_sec_creditos(a['seccion'],p)
                for p in sched.profesores:
                    if p not in cargas: cargas[p]=0.0
                st.session_state.cargas=cargas
                st.session_state.master=pd.DataFrame([{
                    'ID':a['seccion'].cod,'Asignatura':a['seccion'].cod.split('-')[0],'Estudiantes (Cupo)':a['seccion'].cupo,
                    'Créditos Reales':sched.get_sec_creditos(a['seccion'],a['profesor']),'Persona':a['profesor'],
                    'Días':a['patron']['name'],'Horario':format_horario(a['patron'],a['ini']),'Salón':a['salon']
                } for a in sol])
                st.session_state.det_conf=sched._obtener_conflictos(sol)
                st.success(f"✅ Completado en {st.session_state.time:.1f}s")
    if 'master' in st.session_state:
        st.markdown("<div class='glass-card'>",unsafe_allow_html=True)
        t1,t2,t3,t4=st.tabs(["📋 Panel","🔍 Vistas","🚨 Auditoría","📊 Analíticas"])
        with t1:
            edited=st.data_editor(st.session_state.master,use_container_width=True,height=500)
            st.download_button("💾 Exportar Excel",exportar_todo(edited),"Horario_Final.xlsx")
        with t2:
            f1,f2,f3=st.tabs(["Profesor","Curso","Salón"])
            df=st.session_state.master
            with f1:
                lp=sorted([p for p in df['Persona'].unique() if p!="GRADUADOS"])
                if lp:
                    p=st.selectbox("Profesor",lp)
                    st.table(df[df['Persona']==p][['ID','Estudiantes (Cupo)','Créditos Reales','Días','Horario','Salón']])
            with f2:
                lc=sorted(df['Asignatura'].unique())
                if lc:
                    c=st.selectbox("Curso",lc)
                    st.table(df[df['Asignatura']==c][['ID','Estudiantes (Cupo)','Persona','Días','Horario','Salón']])
            with f3:
                ls=sorted(df['Salón'].unique())
                if ls:
                    s=st.selectbox("Salón",ls)
                    st.table(df[df['Salón']==s][['ID','Asignatura','Persona','Días','Horario']])
        with t3:
            if st.session_state.conf>0:
                st.error(f"⚠️ {st.session_state.conf} conflictos duros")
                for c in st.session_state.det_conf: st.write(f"- {c}")
            else: st.success("✅ Cero conflictos duros")
        with t4:
            st.plotly_chart(generar_heatmap_plotly(st.session_state.sched,st.session_state.sol),use_container_width=True)
            st.plotly_chart(generar_barras_apiladas_profesor(st.session_state.sol,st.session_state.sched),use_container_width=True)
            st.plotly_chart(generar_evolucion_fitness_plotly(st.session_state.hist),use_container_width=True)
            st.plotly_chart(generar_figura_cientifica_carga(st.session_state.cargas,st.session_state.sched),use_container_width=True)
            col1,col2,col3=st.columns(3)
            with col1: fp=st.selectbox("Filtrar Profesor",['Todos']+sorted(st.session_state.master['Persona'].unique()))
            with col2: fs=st.selectbox("Filtrar Salón",['Todos']+sorted(st.session_state.master['Salón'].unique()))
            with col3: fc=st.selectbox("Filtrar Curso",['Todos']+sorted(st.session_state.master['Asignatura'].unique()))
            fig_cal=generar_calendario_visual(st.session_state.sol,st.session_state.sched,
                                              fp if fp!='Todos' else None,fs if fs!='Todos' else None,fc if fc!='Todos' else None)
            st.plotly_chart(fig_cal,use_container_width=True)
            if st.button("📄 Generar Reporte PDF"):
                html=generar_reporte_pdf_html(st.session_state.sched,st.session_state.sol,st.session_state.cargas,st.session_state.master)
                st.components.v1.html(html,height=600,scrolling=True)
        st.markdown("</div>",unsafe_allow_html=True)

if __name__=="__main__":
    main()
