import streamlit as st
import pandas as pd
import numpy as np
import random
import copy
import io
from datetime import datetime

# ==============================================================================
# [EL INICIO Y MODELOS SE MANTIENEN IGUAL - OMITIDO POR ESPACIO PERO DEBEN ESTAR]
# ==============================================================================
# (Mantén tus clases Seccion, Profesor, Salon, HorarioGen y generar_bloques)

# ... (Insertar clases Seccion, Profesor, Salon, HorarioGen aquí) ...

def generar_bloques(zona):
    bloques = {}
    offset = 30 if zona == "CENTRAL" else 0
    for h in range(7, 20):
        inicio = h * 60 + offset
        bloques[f"LMV_{inicio}"] = {'dias': ['Lu', 'Mi', 'Vi'], 'inicio': inicio, 'dur': 50}
        bloques[f"MJ_{inicio}"] = {'dias': ['Ma', 'Ju'], 'inicio': inicio, 'dur': 80}
    return bloques

def mins_to_str(m):
    h, mins = divmod(int(m), 60)
    ampm = "AM" if h < 12 else "PM"
    h_disp = h if h <= 12 else h - 12
    if h_disp == 0: h_disp = 12
    return f"{h_disp:02d}:{mins:02d} {ampm}"

# ==============================================================================
# 4. MOTOR MEJORADO CON DIAGNÓSTICO
# ==============================================================================

class EngineThesis:
    def __init__(self, secciones, profesores, salones, zona):
        self.secciones = secciones
        self.profesores_dict = {p.nombre: p for p in profesores}
        self.salones = salones
        self.bloques = generar_bloques(zona)
        self.u_ini, self.u_fin = (630, 750) if zona == "CENTRAL" else (600, 720)

    def analizar_conflictos(self, genes):
        """Devuelve la lista detallada de errores"""
        errores = []
        oc_salon = {}
        oc_prof = {}
        horario_estudiante = {}
        cargas = {p: 0 for p in self.profesores_dict}

        # 1. Mapa de clases que RECIBEN los graduados
        for g in genes:
            bloque = self.bloques[g.bloque_key]
            for est_id in g.seccion.matriculados:
                for d in bloque['dias']:
                    key = (est_id, d)
                    if key not in horario_estudiante: horario_estudiante[key] = []
                    horario_estudiante[key].append((bloque['inicio'], bloque['inicio']+bloque['dur'], g.seccion.uid))

        # 2. Validación de clases que DICTAN
        for g in genes:
            b = self.bloques[g.bloque_key]
            ini, fin = b['inicio'], b['inicio'] + b['dur']
            
            # Conflictos de Salón
            for d in b['dias']:
                ks = (g.salon_obj.codigo, d)
                if ks in oc_salon:
                    for (t1, t2, id_conflicto) in oc_salon[ks]:
                        if max(ini, t1) < min(fin, t2):
                            errores.append(f"SALÓN: {g.salon_obj.codigo} choca entre {g.seccion.uid} y {id_conflicto} el {d}")
                if ks not in oc_salon: oc_salon[ks] = []
                oc_salon[ks].append((ini, fin, g.seccion.uid))

            # Conflictos de Profesor / Doble Rol
            if g.profesor_nombre != "TBA":
                p_obj = self.profesores_dict[g.profesor_nombre]
                cargas[g.profesor_nombre] += g.seccion.creditos
                for d in b['dias']:
                    kp = (g.profesor_nombre, d)
                    if kp in oc_prof:
                        for (t1, t2, id_conflicto) in oc_prof[kp]:
                            if max(ini, t1) < min(fin, t2):
                                errores.append(f"PROFESOR: {g.profesor_nombre} choca entre {g.seccion.uid} y {id_conflicto} el {d}")
                    if kp not in oc_prof: oc_prof[kp] = []
                    oc_prof[kp].append((ini, fin, g.seccion.uid))
                    
                    if p_obj.es_graduado:
                        ke = (p_obj.estudiante_id, d)
                        if ke in horario_estudiante:
                            for (t1, t2, id_clase_toma) in horario_estudiante[ke]:
                                if max(ini, t1) < min(fin, t2):
                                    errores.append(f"DOBLE ROL: {g.profesor_nombre} dicta {g.seccion.uid} pero toma {id_clase_toma} el {d}")

            # Hora Universal
            if any(d in ['Ma', 'Ju'] for d in b['dias']):
                if max(ini, self.u_ini) < min(fin, self.u_fin):
                    errores.append(f"HORA UNIVERSAL: {g.seccion.uid} invade el bloque de asamblea.")

        # Cargas
        for p_nombre, carga in cargas.items():
            p = self.profesores_dict[p_nombre]
            if carga > p.carga_max:
                errores.append(f"CARGA: {p_nombre} tiene {carga} créditos (Máx: {p.carga_max})")
            elif carga < p.carga_min:
                errores.append(f"CARGA: {p_nombre} tiene {carga} créditos (Mín: {p.carga_min})")

        return errores

    def calcular_fitness(self, genes):
        return -len(self.analizar_conflictos(genes))

    def generar_individuo(self):
        genes = []
        for sec in self.secciones:
            prof = random.choice(sec.candidatos) if sec.candidatos else "TBA"
            bloque = random.choice(list(self.bloques.keys()))
            salon = random.choice([s for s in self.salones if s.capacidad >= sec.cupo] or self.salones)
            genes.append(HorarioGen(sec, prof, bloque, salon))
        return genes

    def evolucionar(self, pop_size, gens, callback):
        poblacion = [self.generar_individuo() for _ in range(pop_size)]
        
        for g in range(gens):
            scores = [(self.calcular_fitness(ind), ind) for ind in poblacion]
            scores.sort(key=lambda x: x[0], reverse=True)
            
            callback(g, gens, abs(scores[0][0]), scores[0][1])
            if scores[0][0] == 0: break

            # Evolución
            nueva_gen = [scores[0][1], scores[1][1]] # Elitismo
            while len(nueva_gen) < pop_size:
                padre = copy.deepcopy(random.choice(scores[:10])[1])
                # Mutación dirigida: cambiar un curso al azar
                idx = random.randint(0, len(padre)-1)
                padre[idx].bloque_key = random.choice(list(self.bloques.keys()))
                nueva_gen.append(padre)
            poblacion = nueva_gen
            
        return scores[0][1], abs(scores[0][0])

# ==============================================================================
# [FUNCIONES DE EXCEL SE MANTIENEN IGUAL]
# ==============================================================================

def explotar_secciones(df_cursos):
    secciones = []
    for _, row in df_cursos.iterrows():
        demanda = int(row['DEMANDA_TOTAL'])
        reglas = str(row['REGLAS']).split(',')
        atendido, idx = 0, 1
        for r in reglas:
            r = r.strip().upper()
            if 'X' in r:
                cant, cap = map(int, r.split('X'))
                for _ in range(cant):
                    if atendido < demanda:
                        secciones.append(Seccion(f"{row['CODIGO']}-{idx:03d}", row['CODIGO'], row['NOMBRE'], row['CREDITOS'], cap, row['CANDIDATOS'], row['TIPO_SALON'], row.get('MATRICULADOS')))
                        atendido += cap; idx += 1
            elif r.startswith('R'):
                cap = int(r[1:])
                while atendido < demanda:
                    secciones.append(Seccion(f"{row['CODIGO']}-{idx:03d}", row['CODIGO'], row['NOMBRE'], row['CREDITOS'], cap, row['CANDIDATOS'], row['TIPO_SALON'], row.get('MATRICULADOS')))
                    atendido += cap; idx += 1
    return secciones

def main():
    st.title("🏛️ UPRM Scheduler - Monitor de Tesis")
    
    with st.sidebar:
        zona = st.selectbox("Zona", ["CENTRAL", "PERIFERICA"])
        file = st.file_uploader("Excel", type=['xlsx'])
        pop = st.slider("Población", 20, 200, 100)
        gens = st.slider("Generaciones", 10, 1000, 200)

    if file:
        xls = pd.ExcelFile(file)
        df_cur = pd.read_excel(xls, 'Cursos')
        df_pro = pd.read_excel(xls, 'Profesores')
        df_sal = pd.read_excel(xls, 'Salones')

        if st.button("🚀 OPTIMIZAR"):
            secciones = explotar_secciones(df_cur)
            profesores = [Profesor(r['Nombre'], r['Carga_Min'], r['Carga_Max'], r.get('ES_GRADUADO'), r.get('ESTUDIANTE_ID')) for _, r in df_pro.iterrows()]
            salones = [Salon(r['CODIGO'], r['CAPACIDAD'], r['TIPO']) for _, r in df_sal.iterrows()]

            engine = EngineThesis(secciones, profesores, salones, zona)
            
            bar = st.progress(0)
            status = st.empty()
            error_monitor = st.expander("🔍 Ver detalles de conflictos en tiempo real", expanded=True)

            def update(g, t, f, mejor_ind):
                bar.progress((g+1)/t)
                status.write(f"🧬 Gen {g}/{t} | Conflictos actuales: **{f}**")
                if f > 0:
                    lista_err = engine.analizar_conflictos(mejor_ind)
                    with error_monitor:
                        st.write(lista_err[:10]) # Mostrar solo los primeros 10 para no saturar

            mejor_ind, conflictos = engine.evolucionar(pop, gens, update)

            if conflictos == 0:
                st.balloons()
                st.success("¡Horario perfecto generado!")
            else:
                st.warning(f"Se terminó con {conflictos} conflictos. Revisa el monitor arriba.")

            # Mostrar Tabla Final
            res_data = []
            for g in mejor_ind:
                b = engine.bloques[g.bloque_key]
                res_data.append({
                    "ID": g.seccion.uid, "Curso": g.seccion.nombre, "Prof": g.profesor_nombre,
                    "Dias": "".join(b['dias']), "Hora": f"{mins_to_str(b['inicio'])}", "Salon": g.salon_obj.codigo
                })
            st.dataframe(pd.DataFrame(res_data))

# Clases base faltantes para que el código sea funcional al copiar
class Seccion:
    def __init__(self, uid, codigo_base, nombre, creditos, cupo, candidatos, tipo_salon, matriculados=None):
        self.uid, self.codigo_base, self.nombre, self.creditos, self.cupo = uid, codigo_base, nombre, creditos, cupo
        self.tipo_salon_req = str(tipo_salon).upper()
        self.candidatos = [c.strip().upper() for c in str(candidatos).split(',') if c.strip()]
        self.matriculados = [m.strip().upper() for m in str(matriculados).split(',') if m.strip()] if not pd.isna(matriculados) else []

class Profesor:
    def __init__(self, nombre, c_min, c_max, es_graduado=False, estudiante_id=None):
        self.nombre = str(nombre).strip().upper()
        self.carga_min, self.carga_max = float(c_min), float(c_max)
        self.es_graduado = str(es_graduado).upper() == "SI"
        self.estudiante_id = str(estudiante_id).strip().upper() if not pd.isna(estudiante_id) else None

class Salon:
    def __init__(self, codigo, capacidad, tipo):
        self.codigo, self.capacidad, self.tipo = str(codigo).upper(), int(capacidad), str(tipo).upper()

class HorarioGen:
    def __init__(self, seccion, profesor_nombre, bloque_key, salon_obj):
        self.seccion, self.profesor_nombre, self.bloque_key, self.salon_obj = seccion, profesor_nombre, bloque_key, salon_obj

if __name__ == "__main__":
    main()
