import streamlit as st
import pandas as pd
import numpy as np
import random
import copy
import time
import io
import plotly.express as px

# ==============================================================================
# 1. CONFIGURACIÓN ESTRUCTURAL (TABLAS DE LA TESIS)
# ==============================================================================

st.set_page_config(page_title="UPRM Scheduler V4.0 (Thesis Logic)", page_icon="🎓", layout="wide")

# --- TABLA 4.6: COMBINACIÓN DE DÍAS Y CRÉDITOS ---
# Se definen los bloques exactos descritos en el documento.
# Formato: ID_TESIS: {dias, duracion_minutos, etiqueta}
# Nota: Asumimos inicio de horas estándar.

BLOQUES_TIEMPO = {}

def crear_bloque(id_tesis, dias, duracion, label):
    # Generamos variantes de hora para cada patrón (de 7:00 AM a 8:00 PM)
    # Granularidad de 30 min como dice la Tabla 4.7
    horas_inicio = [420, 450, 480, 510, 540, 570, 600, 630, 660, 690, 720, 750, 780, 810, 840, 870, 900, 930, 960, 990, 1020, 1050, 1080, 1110, 1140]
    
    for h in horas_inicio:
        # Filtrar horas imposibles (que terminen después de las 10pm / 22:00 = 1320 min)
        if h + duracion > 1320: continue
        
        # ID único combinando patrón y hora
        key = f"{id_tesis}_{h}"
        h_str = f"{h//60:02d}:{h%60:02d}"
        
        BLOQUES_TIEMPO[key] = {
            'id_tesis': id_tesis,
            'dias': dias,
            'inicio': h,
            'duracion': duracion,
            'label': f"{label} ({h_str})"
        }

# --- 3 CREDITOS (3 horas contacto) ---
# Patrón 1: Lu-Mi-Vi (50 min cada uno = 1 hora académica)
crear_bloque(1, ['Lu', 'Mi', 'Vi'], 50, "LMV (3 Cr)")
# Patrón 2: Ma-Ju (1h 20min = 80 min)
crear_bloque(2, ['Ma', 'Ju'], 80, "MJ (3 Cr)")
# Patrones 3-7: Intensivos (1 dia x 3 horas = 170 min aprox con pausas, usaremos 180 standard o 150 académico. Usaremos 170 min)
crear_bloque(3, ['Lu'], 170, "Lu Intensivo")
crear_bloque(4, ['Ma'], 170, "Ma Intensivo")
crear_bloque(5, ['Mi'], 170, "Mi Intensivo")
crear_bloque(6, ['Ju'], 170, "Ju Intensivo")
crear_bloque(7, ['Vi'], 170, "Vi Intensivo")

# --- 4 CREDITOS (4 horas contacto) ---
# Patrón 8-12: 4 días x 50 min
crear_bloque(8, ['Lu','Ma','Mi','Ju'], 50, "LMWJ (4 Cr)")
crear_bloque(9, ['Lu','Ma','Mi','Vi'], 50, "LMWV (4 Cr)")
crear_bloque(10,['Lu','Ma','Ju','Vi'], 50, "LMJV (4 Cr)")
crear_bloque(11,['Lu','Mi','Ju','Vi'], 50, "LWJV (4 Cr)")
crear_bloque(12,['Ma','Mi','Ju','Vi'], 50, "MJWV (4 Cr)")
# Patrones 13-16: 2 días x 2 horas (110 min aprox)
crear_bloque(13, ['Lu', 'Mi'], 110, "LW (4 Cr)")
crear_bloque(14, ['Lu', 'Vi'], 110, "LV (4 Cr)")
crear_bloque(15, ['Ma', 'Ju'], 110, "MJ (4 Cr Largo)")
crear_bloque(16, ['Mi', 'Vi'], 110, "WV (4 Cr)")

# --- 5 CREDITOS ---
# Patrón 17: Diario
crear_bloque(17, ['Lu','Ma','Mi','Ju','Vi'], 50, "Diario (5 Cr)")

def mins_to_str(minutes):
    h, m = minutes // 60, minutes % 60
    am_pm = "AM" if h < 12 else "PM"
    h_disp = h if h <= 12 else h - 12
    return f"{h_disp:02d}:{m:02d} {am_pm}"

# ==============================================================================
# 2. LOGICA DE COMPENSACIÓN (TABLA 4.12)
# ==============================================================================

def calcular_creditos_reales(creditos_base, cupo):
    """
    Implementa la Tabla 4.12 de la tesis.
    Calcula créditos a pagar al profesor basándose en el tamaño de la sección.
    Asumimos Horas Contacto ≈ Créditos Base.
    """
    comp = 0.0
    
    # Lógica simplificada de la tabla para 3 créditos (Fila más común)
    if creditos_base == 3:
        if cupo <= 34: comp = 0.0
        elif cupo <= 44: comp = 0.5
        elif cupo <= 54: comp = 1.0
        elif cupo <= 64: comp = 1.5
        elif cupo <= 74: comp = 2.0
        elif cupo <= 84: comp = 2.5
        elif cupo <= 94: comp = 3.0
        else: comp = 3.5 # Y sigue...
        
    # Lógica para 4 créditos
    elif creditos_base == 4:
        if cupo <= 33: comp = 0.0
        elif cupo <= 41: comp = 0.5
        elif cupo <= 48: comp = 1.0
        elif cupo <= 56: comp = 1.5
        else: comp = 2.0
        
    # Default (sin compensación si no coincide o es pequeño)
    return creditos_base + comp

# ==============================================================================
# 3. CLASES Y ESTRUCTURAS
# ==============================================================================

class Seccion:
    def __init__(self, uid, codigo, nombre, creditos, cupo, candidatos, tipo_salon_req):
        self.uid = uid
        self.codigo = str(codigo).strip().upper()
        self.nombre = str(nombre).strip()
        self.creditos = int(creditos)
        self.cupo = int(cupo)
        self.tipo_salon_req = str(tipo_salon_req).strip().upper()
        
        # Normalización de Candidatos
        if pd.isna(candidatos) or str(candidatos).strip() == '':
            self.candidatos = []
        else:
            self.candidatos = [str(c).strip().upper() for c in str(candidatos).split(',') if str(c).strip()]
            
        # Flag para algoritmo de asignación (Sección grande o única)
        self.es_grande = (self.cupo >= 85)

class Profesor:
    def __init__(self, nombre, carga_min, carga_max):
        self.nombre = str(nombre).strip().upper()
        self.carga_min = float(carga_min)
        self.carga_max = float(carga_max)
        self.carga_actual = 0.0

class Salon:
    def __init__(self, codigo, capacidad, tipo):
        self.codigo = str(codigo).strip().upper()
        self.capacidad = int(capacidad)
        self.tipo = str(tipo).strip().upper()

class HorarioGen:
    def __init__(self, seccion, profesor_nombre, bloque_key, salon_obj):
        self.seccion = seccion
        self.profesor_nombre = profesor_nombre
        self.bloque_key = bloque_key
        self.salon_obj = salon_obj

# ==============================================================================
# 4. MOTOR INTELIGENTE V4 (CONSTRAINTS & REPAIR)
# ==============================================================================

class ThesisSchedulerEngine:
    def __init__(self, secciones, profesores, salones):
        self.secciones = secciones
        self.profesores_dict = {p.nombre: p for p in profesores}
        self.salones = salones
        
        # Clasificar claves de bloques por créditos para acceso rápido
        self.bloques_keys_3cr = [k for k, v in BLOQUES_TIEMPO.items() if v['id_tesis'] <= 7]
        self.bloques_keys_4cr = [k for k, v in BLOQUES_TIEMPO.items() if 8 <= v['id_tesis'] <= 16]
        self.bloques_keys_5cr = [k for k, v in BLOQUES_TIEMPO.items() if v['id_tesis'] >= 17]
        
        # Pre-calcular salones válidos (Dominio)
        self.dominios_salones = {}
        for sec in secciones:
            validos = [s for s in salones if s.capacidad >= sec.cupo]
            if sec.tipo_salon_req != 'GENERAL':
                validos = [s for s in validos if s.tipo == sec.tipo_salon_req]
            self.dominios_salones[sec.uid] = validos if validos else salones

    def es_compatible(self, bloque_key, profesor, salon_obj, ocupacion_profesores, ocupacion_salones):
        """Verifica choques de hora, salón y HORA UNIVERSAL"""
        bloque = BLOQUES_TIEMPO[bloque_key]
        inicio = bloque['inicio']
        fin = inicio + bloque['duracion']
        
        # 0. RESTRICCIÓN HORA UNIVERSAL (Ma y Ju 10:30 - 12:00 = 630 min - 720 min)
        # Si el bloque toca este intervalo en Martes o Jueves, es inválido (Hard Constraint)
        hora_univ_inicio = 630
        hora_univ_fin = 720
        if 'Ma' in bloque['dias'] or 'Ju' in bloque['dias']:
            # Si hay solapamiento con la hora universal
            if max(inicio, hora_univ_inicio) < min(fin, hora_univ_fin):
                return False

        # 1. Verificar Salón
        for dia in bloque['dias']:
            key_s = (salon_obj.codigo, dia)
            if key_s in ocupacion_salones:
                for (t1, t2) in ocupacion_salones[key_s]:
                    if max(inicio, t1) < min(fin, t2): return False # Choque
        
        # 2. Verificar Profesor
        if profesor != "TBA":
            for dia in bloque['dias']:
                key_p = (profesor, dia)
                if key_p in ocupacion_profesores:
                    for (t1, t2) in ocupacion_profesores[key_p]:
                        if max(inicio, t1) < min(fin, t2): return False # Choque
                        
        return True

    def generar_individuo_tesis(self):
        """Implementación del Algoritmo 2 de la Tesis (Asignación Dirigida)"""
        genes = []
        
        # Mapas temporales de ocupación
        oc_prof = {}
        oc_salon = {}
        cargas_temp = {p: 0.0 for p in self.profesores_dict}
        
        # Ordenar secciones según prioridad de la tesis:
        # 1. Secciones Únicas (o raras) -> En este MVP usamos el orden de entrada o aleatorio con sesgo
        # 2. Secciones Grandes
        secciones_ordenadas = sorted(self.secciones, key=lambda x: (not x.es_grande, random.random()))
        
        for sec in secciones_ordenadas:
            # Seleccionar Profesor (Logica SuitProf)
            prof_selec = "TBA"
            candidates = sec.candidatos
            
            # Intentar asignar a candidato si tiene carga disponible
            if candidates:
                # Ordenar candidatos por quién tiene menos carga actual (Balanceo)
                candidates.sort(key=lambda c: cargas_temp.get(c, 0))
                for cand in candidates:
                    creditos_pago = calcular_creditos_reales(sec.creditos, sec.cupo)
                    prof_obj = self.profesores_dict.get(cand)
                    if prof_obj and (cargas_temp[cand] + creditos_pago <= prof_obj.carga_max):
                        prof_selec = cand
                        cargas_temp[cand] += creditos_pago
                        break
            
            # Seleccionar Bloque y Salón (Greedy con Reparación implícita)
            salon_pool = self.dominios_salones[sec.uid]
            
            if sec.creditos == 3: b_pool = self.bloques_keys_3cr
            elif sec.creditos == 4: b_pool = self.bloques_keys_4cr
            else: b_pool = self.bloques_keys_5cr
            
            # Si no hay bloques específicos (fallback), usar todos
            if not b_pool: b_pool = list(BLOQUES_TIEMPO.keys())
            
            random.shuffle(salon_pool)
            random.shuffle(b_pool)
            
            asignado = False
            
            # Búsqueda Greedy de espacio libre
            for s in salon_pool:
                for b in b_pool:
                    if self.es_compatible(b, prof_selec, s, oc_prof, oc_salon):
                        # Asignar
                        bd = BLOQUES_TIEMPO[b]
                        ini, end = bd['inicio'], bd['inicio'] + bd['duracion']
                        
                        for d in bd['dias']:
                            ks = (s.codigo, d)
                            if ks not in oc_salon: oc_salon[ks] = []
                            oc_salon[ks].append((ini, end))
                            
                            if prof_selec != "TBA":
                                kp = (prof_selec, d)
                                if kp not in oc_prof: oc_prof[kp] = []
                                oc_prof[kp].append((ini, end))
                        
                        genes.append(HorarioGen(sec, prof_selec, b, s))
                        asignado = True
                        break
                if asignado: break
            
            if not asignado:
                # Si falla, asignar random (se penalizará)
                genes.append(HorarioGen(sec, prof_selec, random.choice(b_pool), random.choice(salon_pool)))

        return genes

    def detectar_conflictos(self, genes):
        conflictos = []
        oc_prof = {}
        oc_salon = {}
        
        for idx, gen in enumerate(genes):
            bloque = BLOQUES_TIEMPO[gen.bloque_key]
            ini, end = bloque['inicio'], bloque['inicio'] + bloque['duracion']
            
            # Validar Hora Universal
            hora_univ_inicio, hora_univ_fin = 630, 720
            if ('Ma' in bloque['dias'] or 'Ju' in bloque['dias']) and \
               (max(ini, hora_univ_inicio) < min(end, hora_univ_fin)):
                   conflictos.append(idx)
                   continue

            for dia in bloque['dias']:
                # Salón
                ks = (gen.salon_obj.codigo, dia)
                if ks not in oc_salon: oc_salon[ks] = []
                for (t1, t2, o_idx) in oc_salon[ks]:
                    if max(ini, t1) < min(end, t2):
                        conflictos.append(idx)
                        conflictos.append(o_idx)
                oc_salon[ks].append((ini, end, idx))
                
                # Prof
                if gen.profesor_nombre != "TBA":
                    kp = (gen.profesor_nombre, dia)
                    if kp not in oc_prof: oc_prof[kp] = []
                    for (t1, t2, o_idx) in oc_prof[kp]:
                        if max(ini, t1) < min(end, t2):
                            conflictos.append(idx)
                            conflictos.append(o_idx)
                    oc_prof[kp].append((ini, end, idx))
                    
        return list(set(conflictos))

    def reparar_individuo(self, genes):
        indices_rotos = self.detectar_conflictos(genes)
        if not indices_rotos: return genes
        
        # Construir estado ocupado por los sanos
        oc_prof = {}
        oc_salon = {}
        
        for i, gen in enumerate(genes):
            if i in indices_rotos: continue
            
            bd = BLOQUES_TIEMPO[gen.bloque_key]
            ini, end = bd['inicio'], bd['inicio'] + bd['duracion']
            for d in bd['dias']:
                if gen.profesor_nombre != "TBA":
                    kp = (gen.profesor_nombre, d)
                    if kp not in oc_prof: oc_prof[kp] = []
                    oc_prof[kp].append((ini, end))
                
                ks = (gen.salon_obj.codigo, d)
                if ks not in oc_salon: oc_salon[ks] = []
                oc_salon[ks].append((ini, end))

        # Intentar arreglar rotos
        random.shuffle(indices_rotos)
        for i in indices_rotos:
            gen = genes[i]
            
            # Determinar pool de bloques correcto
            if gen.seccion.creditos == 3: b_pool = self.bloques_keys_3cr
            elif gen.seccion.creditos == 4: b_pool = self.bloques_keys_4cr
            else: b_pool = self.bloques_keys_5cr
            if not b_pool: b_pool = list(BLOQUES_TIEMPO.keys())
            
            salones = self.dominios_salones[gen.seccion.uid]
            
            random.shuffle(b_pool)
            random.shuffle(salones)
            
            reparado = False
            for s in salones:
                for b in b_pool:
                    if self.es_compatible(b, gen.profesor_nombre, s, oc_prof, oc_salon):
                        # Aplicar cambio
                        gen.bloque_key = b
                        gen.salon_obj = s
                        
                        # Actualizar mapas
                        bd = BLOQUES_TIEMPO[b]
                        ini, end = bd['inicio'], bd['inicio'] + bd['duracion']
                        for d in bd['dias']:
                            ks = (s.codigo, d)
                            if ks not in oc_salon: oc_salon[ks] = []
                            oc_salon[ks].append((ini, end))
                            if gen.profesor_nombre != "TBA":
                                kp = (gen.profesor_nombre, d)
                                if kp not in oc_prof: oc_prof[kp] = []
                                oc_prof[kp].append((ini, end))
                        
                        reparado = True
                        break
                if reparado: break
        
        return genes

    def ejecutar(self, pop_size, generaciones, callback):
        # Población inicial usando el Algoritmo de Tesis (Asignación Dirigida)
        poblacion = [self.generar_individuo_tesis() for _ in range(pop_size)]
        
        mejor_genoma = None
        mejor_score = -float('inf')
        
        for g in range(generaciones):
            scores = []
            for ind in poblacion:
                conf = self.detectar_conflictos(ind)
                fit = -len(conf)
                scores.append((fit, ind))
                
                if fit > mejor_score:
                    mejor_score = fit
                    mejor_genoma = copy.deepcopy(ind)
            
            if mejor_score == 0:
                callback(g, generaciones, 0)
                return mejor_genoma, 0
                
            callback(g, generaciones, abs(mejor_score))
            
            # Selección y Reparación
            scores.sort(key=lambda x: x[0], reverse=True)
            nueva_pop = [scores[0][1], scores[1][1]] # Elitismo
            
            while len(nueva_pop) < pop_size:
                # Cruce simple (copiar padre y reparar)
                # En V4, la "mutación" es 100% reparación inteligente
                padre = random.choice(scores[:pop_size//2])[1]
                hijo = copy.deepcopy(padre)
                hijo = self.reparar_individuo(hijo)
                nueva_pop.append(hijo)
            
            poblacion = nueva_pop
            
        return mejor_genoma, abs(mejor_score)

# ==============================================================================
# 5. INTERFAZ
# ==============================================================================

def main():
    st.markdown("## 🎓 UPRM Scheduler V4: Thesis Edition")
    st.markdown("""
    **Características Activadas:**
    - Bloques de tiempo UPRM (3, 4, 5 créditos).
    - Restricción de Hora Universal (Ma/Ju 10:30-12:00).
    - Cálculo de Compensación de Créditos (Tabla 4.12).
    - Algoritmo de Reparación Inteligente.
    """)
    
    file = st.sidebar.file_uploader("Excel Data", type=['xlsx'])
    
    if file:
        try:
            xls = pd.ExcelFile(file)
            df_cur = pd.read_excel(xls, 'Cursos')
            df_pro = pd.read_excel(xls, 'Profesores')
            df_sal = pd.read_excel(xls, 'Salones')
            
            secciones = []
            for _, row in df_cur.iterrows():
                qty = int(row.get('CANTIDAD_SECCIONES', 1))
                for i in range(qty):
                    secciones.append(Seccion(f"{row['CODIGO']}-{i+1}", row['CODIGO'], row.get('NOMBRE',''), row['CREDITOS'], row['CUPO'], row.get('CANDIDATOS'), row.get('TIPO_SALON','GENERAL')))
            
            profesores = [Profesor(row['Nombre'], row['Carga_Min'], row['Carga_Max']) for _, row in df_pro.iterrows()]
            salones = [Salon(row['CODIGO'], row['CAPACIDAD'], row['TIPO']) for _, row in df_sal.iterrows()]
            
            if st.sidebar.button("Ejecutar Scheduler"):
                engine = ThesisSchedulerEngine(secciones, profesores, salones)
                
                bar = st.progress(0)
                st_stat = st.empty()
                
                def cb(g, tot, fit):
                    bar.progress((g+1)/tot)
                    st_stat.metric("Conflictos", fit, delta_color="inverse")
                
                res, conflicts = engine.ejecutar(40, 60, cb)
                
                if conflicts == 0:
                    st.success("✅ Horario Óptimo Generado")
                else:
                    st.warning(f"⚠️ Se encontraron {conflicts} conflictos irreducibles.")
                
                # Reporte
                rows = []
                for g in res:
                    bd = BLOQUES_TIEMPO[g.bloque_key]
                    rows.append({
                        'Curso': g.seccion.codigo,
                        'Sec': g.seccion.uid.split('-')[1],
                        'Profesor': g.profesor_nombre,
                        'Días': "".join(bd['dias']),
                        'Horario': bd['label'],
                        'Salón': g.salon_obj.codigo,
                        'Cupo': g.seccion.cupo
                    })
                df = pd.DataFrame(rows).sort_values('Curso')
                st.dataframe(df)
                
                # Download
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer) as writer: df.to_excel(writer, index=False)
                st.download_button("Descargar Excel", buffer.getvalue(), "Horario_Tesis.xlsx")
                
        except Exception as e:
            st.error(f"Error: {e}")

if __name__ == "__main__":
    main()
