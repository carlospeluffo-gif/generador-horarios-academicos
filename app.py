import streamlit as st
import pandas as pd
import random
import json
import numpy as np
from datetime import datetime
import io

# ========================================================
# CONFIGURACIÓN Y UTILIDADES
# ========================================================

def generar_salones_por_defecto():
    return {
        "QUIM": [f"Química {i+1}" for i in range(40)],
        "MATE": [f"Matemática {i+1}" for i in range(33)],
        "FIS": [f"Física {i+1}" for i in range(28)],
        "BIO": [f"Biología {i+1}" for i in range(25)],
    }

def cargar_salones_desde_excel(file):
    salones_por_depto = {}
    df = pd.read_excel(file)
    columnas = {c.lower().strip(): c for c in df.columns}

    col_departamento = columnas.get("departamento")
    col_salon = columnas.get("salon") or columnas.get("salón") or columnas.get("room")

    if not col_departamento or not col_salon:
        st.warning("No se encontraron columnas 'Departamento' y 'Salon' en el Excel. Se usarán los salones por defecto.")
        return salones_por_depto

    for _, row in df.iterrows():
        depto = str(row[col_departamento]).strip().upper()
        salon = str(row[col_salon]).strip()
        if depto and salon:
            salones_por_depto.setdefault(depto, []).append(salon)

    return salones_por_depto

def a_minutos(hhmm):
    h, m = map(int, hhmm.split(":"))
    return h * 60 + m

def es_bloque_tres_horas_valido(dia, hora_inicio, duracion, creditos):
    if creditos == 3 and duracion == 3 and dia in ["Lu", "Ma", "Mi", "Ju", "Vi"]:
        return a_minutos(hora_inicio) >= a_minutos("15:30")
    return True

tabla_creditos = {
    1: [(1,44,0),(45,74,0.5),(75,104,1),(105,134,1.5),(135,164,2),(165,194,2.5),
        (195,224,3),(225,254,3.5),(255,284,4),(285,314,4.5),(315,344,5),(345,374,5.5),
        (375,404,6),(405,434,6.5),(435,464,7),(465,494,7.5),(495,524,8)],
    2: [(1,37,0),(38,52,0.5),(53,67,1),(68,82,1.5),(83,97,2),(98,112,2.5),
        (113,127,3),(128,142,3.5),(143,157,4),(158,172,4.5),(173,187,5),(188,202,5.5),
        (203,217,6),(218,232,6.5),(233,247,7),(248,262,7.5),(263,277,8)],
    3: [(1,34,0),(35,44,0.5),(45,54,1),(55,64,1.5),(65,74,2),(75,84,2.5),
        (85,94,3),(95,104,3.5),(105,114,4),(115,124,4.5),(125,134,5),(135,144,5.5),
        (145,154,6),(155,164,6.5),(165,174,7),(175,184,7.5),(185,194,8)],
    4: [(1,33,0),(34,41,0.5),(42,48,1),(49,56,1.5),(57,63,2),(64,71,2.5),
        (72,78,3),(79,86,3.5),(87,93,4),(94,101,4.5),(102,108,5),(109,116,5.5),
        (117,123,6),(124,131,6.5),(132,138,7),(139,146,7.5),(147,153,8)],
    5: [(1,32,0),(33,38,0.5),(39,44,1),(45,50,1.5),(51,56,2),(57,63,2.5),
        (64,69,3),(70,75,3.5),(76,81,4),(82,88,4.5),(89,93,5),(94,99,5.5),
        (100,104,6),(105,110,6.5),(111,116,7),(117,122,7.5),(123,128,8)],
    6: [(1,32,0),(33,37,0.5),(38,42,1),(43,47,1.5),(48,52,2),(53,57,2.5),
        (58,62,3),(63,67,3.5),(68,72,4),(73,77,4.5),(78,82,5),(83,87,5.5),
        (88,92,6),(93,97,6.5),(98,102,7),(103,107,7.5),(108,112,8)]
}

def calcular_creditos_adicionales(horas_contacto, estudiantes):
    rangos = tabla_creditos.get(horas_contacto, [])
    for minimo, maximo, creditos in rangos:
        if minimo <= estudiantes <= maximo:
            return creditos
    return 0

def generar_bloques():
    bloques = []
    id_counter = 1
    combinaciones_4dias = [
        ["Lu","Ma","Mi","Ju"],
        ["Lu","Ma","Mi","Vi"],
        ["Lu","Ma","Ju","Vi"],
        ["Lu","Mi","Ju","Vi"],
        ["Ma","Mi","Ju","Vi"],
    ]
    for dias in combinaciones_4dias:
        bloques.append({"id": id_counter, "dias": dias, "horas": [1]*4, "creditos": 4})
        id_counter += 1

    combinaciones_2dias = [["Lu","Mi"],["Lu","Vi"],["Ma","Ju"],["Mi","Vi"]]
    for dias in combinaciones_2dias:
        bloques.append({"id": id_counter, "dias": dias, "horas": [2,2], "creditos": 4})
        id_counter += 1

    bloques.append({"id": id_counter, "dias": ["Lu","Mi","Vi"], "horas": [1,1,1], "creditos": 3}); id_counter += 1
    bloques.append({"id": id_counter, "dias": ["Ma","Ju"], "horas": [1.5,1.5], "creditos": 3}); id_counter += 1

    combinaciones_5creditos = [
        (["Lu","Mi","Vi"], [2,2,1]),
        (["Lu","Ma","Mi","Vi"], [1,1,1,2]),
        (["Lu","Ma","Ju","Vi"], [1,1,1,2]),
        (["Lu","Mi","Ju","Vi"], [1,1,1,2]),
        (["Ma","Mi","Ju","Vi"], [1,1,1,2]),
        (["Ma","Ju","Vi"], [1.5,1.5,2]),
        (["Lu","Ma","Mi","Ju","Vi"], [1,1,1,1,1]),
        (["Lu","Ma","Mi"], [2,1,2]),
    ]
    for dias, horas in combinaciones_5creditos:
        bloques.append({"id": id_counter, "dias": dias, "horas": horas, "creditos": 5})
        id_counter += 1

    for dia in ["Lu","Ma","Mi","Ju","Vi"]:
        bloques.append({"id": id_counter, "dias": [dia], "horas": [3], "creditos": 3})
        id_counter += 1

    return bloques

horas_inicio = []
for h in range(7, 20):
    for m in [0, 30]:
        if h == 19 and m > 20:
            break
        horas_inicio.append(f"{h:02d}:{m:02d}")

# ========================================================
# CONFIGURACIÓN DEL SISTEMA
# ========================================================

class ConfiguracionSistema:
    def __init__(self):
        self.profesores_config = {}
        self.salones = []
        self.cursos_df = None
        self.restricciones_globales = {
            "horarios_prohibidos": {"Ma": [("10:30", "12:30")], "Ju": [("10:30", "12:30")]},
            "hora_inicio_min": "07:30",
            "hora_fin_max": "19:30",
            "creditos_max_profesor": 15,
            "creditos_min_profesor": 8,
            "estudiantes_max_salon": 50,
            "horas_max_dia": 8,
            "dias_max_profesor": 5
        }
        self.pesos_restricciones = {
            "horario_preferido": 30,
            "compactacion_horario": 20,
            "equilibrio_creditos": 25,
            "utilizacion_salones": 15,
            "estudiantes_por_salon": 10,
            "horas_consecutivas": 18,
            "distribucion_semanal": 12,
            "evitar_horas_pico": 8
        }

    def cargar_cursos(self, archivo_excel, depto, programa):
        try:
            excel_data = pd.read_excel(archivo_excel, sheet_name=None)
            hoja_cursos = None
            for nombre_hoja, df in excel_data.items():
                columnas_lower = [c.lower().strip() for c in df.columns]
                if any("profesor" in c or "docente" in c for c in columnas_lower) and \
                   any("curso" in c or "materia" in c or "asignatura" in c for c in columnas_lower):
                    hoja_cursos = df.copy()
                    break

            if hoja_cursos is None:
                st.error("No se encontró una hoja válida con datos de cursos.")
                return False

            hoja_cursos.columns = [c.lower().strip().replace(" ", "_") for c in hoja_cursos.columns]
            mapeo = {
                "profesor": ["profesor", "docente", "teacher", "instructor"],
                "curso": ["curso", "materia", "asignatura", "subject", "course"],
                "creditos": ["creditos", "créditos", "credits", "horas"],
                "estudiantes": ["estudiantes", "alumnos", "students", "enrollment", "seccion"],
                "departamento": ["departamento", "department", "area", "siglas"],
                "programa": ["programa", "program", "carrera", "major"]
            }

            cols = {}
            for campo, opciones in mapeo.items():
                for col in hoja_cursos.columns:
                    if any(op in col for op in opciones):
                        cols[campo] = col
                        break

            if "profesor" not in cols or "curso" not in cols:
                st.error("No se encontraron columnas básicas (Profesor, Curso).")
                return False

            if "creditos" not in cols:
                hoja_cursos["creditos_default"] = 3
                cols["creditos"] = "creditos_default"

            if "estudiantes" not in cols:
                hoja_cursos["estudiantes_default"] = 30
                cols["estudiantes"] = "estudiantes_default"

            hoja_cursos = hoja_cursos.dropna(subset=[cols["profesor"], cols["curso"]])
            hoja_cursos[cols["profesor"]] = hoja_cursos[cols["profesor"]].astype(str).str.strip()
            hoja_cursos[cols["curso"]] = hoja_cursos[cols["curso"]].astype(str).str.strip()

            if "departamento" in cols:
                hoja_cursos[cols["departamento"]] = hoja_cursos[cols["departamento"]].astype(str).str.strip().str.upper()
                hoja_cursos = hoja_cursos[hoja_cursos[cols["departamento"]] == depto]

            if "programa" in cols and programa:
                hoja_cursos[cols["programa"]] = hoja_cursos[cols["programa"]].astype(str).str.strip().str.upper()
                hoja_cursos = hoja_cursos[hoja_cursos[cols["programa"]] == programa]

            programas_detectados = []
            if "programa" in cols:
                programas_detectados = sorted(hoja_cursos[cols["programa"]].dropna().unique())

            if hoja_cursos.empty:
                st.error("No se encontraron cursos que coincidan con el filtro.")
                return False

            self.profesores_config = {}
            for profesor, df_prof in hoja_cursos.groupby(cols["profesor"]):
                cursos = []
                creditos_totales = 0
                for _, row in df_prof.iterrows():
                    try:
                        creditos = int(float(row[cols["creditos"]]))
                    except (ValueError, TypeError):
                        creditos = 3
                    try:
                        estudiantes = int(float(row[cols["estudiantes"]]))
                    except (ValueError, TypeError):
                        estudiantes = 30
                    nombre = str(row[cols["curso"]]).strip()
                    if nombre:
                        cursos.append({"nombre": nombre, "creditos": creditos, "estudiantes": estudiantes})
                        creditos_totales += creditos
                if cursos:
                    self.profesores_config[profesor] = {
                        "cursos": cursos,
                        "creditos_totales": creditos_totales,
                        "horario_preferido": {},
                        "horario_no_disponible": {}
                    }

            if not self.profesores_config:
                st.error("No se pudieron construir configuraciones para profesores.")
                return False

            total_cursos = sum(len(cfg["cursos"]) for cfg in self.profesores_config.values())
            num_salones = max(3, min(10, total_cursos // 3))
            self.salones = [f"Salón {i+1}" for i in range(num_salones)]
            self.cursos_df = hoja_cursos
            return True, programas_detectados
        except Exception as e:
            st.error(f"Error al cargar cursos: {e}")
            return False

    def establecer_salones(self, salones):
        self.salones = salones

def horario_valido(dia, hora_inicio, duracion, config, profesor=None, creditos=None):
    ini_min = a_minutos(hora_inicio)
    fin_min = ini_min + int(duracion * 60)

    if fin_min > a_minutos(config.restricciones_globales["hora_fin_max"]):
        return False
    if ini_min < a_minutos(config.restricciones_globales["hora_inicio_min"]):
        return False
    if creditos and not es_bloque_tres_horas_valido(dia, hora_inicio, duracion, creditos):
        return False

    restriccion_dia = config.restricciones_globales["horarios_prohibidos"].get(dia, [])
    for r_ini, r_fin in restriccion_dia:
        if not (fin_min <= a_minutos(r_ini) or ini_min >= a_minutos(r_fin)):
            return False

    if profesor and profesor in config.profesores_config:
        prof_conf = config.profesores_config[profesor]["horario_no_disponible"]
        if dia in prof_conf:
            for r_ini, r_fin in prof_conf[dia]:
                if not (fin_min <= a_minutos(r_ini) or ini_min >= a_minutos(r_fin)):
                    return False

    return True

def cumple_horario_preferido(dia, hora_inicio, duracion, config, profesor):
    prof_conf = config.profesores_config.get(profesor, {})
    preferencias = prof_conf.get("horario_preferido", {}).get(dia, [])
    if not preferencias:
        return False
    ini = a_minutos(hora_inicio)
    fin = ini + int(duracion * 60)
    for pref_ini, pref_fin in preferencias:
        if ini >= a_minutos(pref_ini) and fin <= a_minutos(pref_fin):
            return True
    return False

class AsignacionClase:
    def __init__(self, curso_info, profesor, bloque, hora_inicio, salon):
        self.curso_nombre = curso_info["nombre"]
        self.profesor = profesor
        self.bloque = bloque
        self.hora_inicio = hora_inicio
        self.estudiantes = curso_info["estudiantes"]
        self.salon = salon
        self.creditos = curso_info["creditos"]
        self.horas_contacto = int(sum(bloque["horas"]))
        self.creditos_extra = calcular_creditos_adicionales(self.horas_contacto, self.estudiantes)

    def get_horario_detallado(self):
        horarios = []
        for dia, duracion in zip(self.bloque["dias"], self.bloque["horas"]):
            fin_min = a_minutos(self.hora_inicio) + int(duracion * 60)
            hora_fin = f"{fin_min//60:02d}:{fin_min%60:02d}"
            es_tres_horas = (self.creditos == 3 and duracion == 3)
            horarios.append({
                "Curso": self.curso_nombre,
                "Profesor": self.profesor,
                "Bloque": self.bloque["id"],
                "Dia": dia,
                "Hora Inicio": self.hora_inicio,
                "Hora Fin": hora_fin,
                "Duración": duracion,
                "Créditos": self.creditos,
                "Créditos Extra": self.creditos_extra,
                "Estudiantes": self.estudiantes,
                "Salon": self.salon,
                "3h Consecutivas": "SÍ" if es_tres_horas else "NO",
                "Restricción 15:30": "CUMPLE" if (not es_tres_horas or a_minutos(self.hora_inicio) >= a_minutos("15:30")) else "VIOLA"
            })
        return horarios

def hay_conflictos(nueva_asignacion, asignaciones):
    for asignacion in asignaciones:
        for dia_nuevo, dur_nuevo in zip(nueva_asignacion.bloque["dias"], nueva_asignacion.bloque["horas"]):
            ini_nuevo = a_minutos(nueva_asignacion.hora_inicio)
            fin_nuevo = ini_nuevo + int(dur_nuevo * 60)
            for dia_exist, dur_exist in zip(asignacion.bloque["dias"], asignacion.bloque["horas"]):
                if dia_nuevo != dia_exist:
                    continue
                ini_exist = a_minutos(asignacion.hora_inicio)
                fin_exist = ini_exist + int(dur_exist * 60)
                if not (fin_nuevo <= ini_exist or ini_nuevo >= fin_exist):
                    if nueva_asignacion.profesor == asignacion.profesor or nueva_asignacion.salon == asignacion.salon:
                        return True
    return False

def generar_horario_valido(config, bloques):
    asignaciones = []
    for profesor, datos in config.profesores_config.items():
        cursos_asignados = 0
        intentos = 0
        max_intentos = 3000
        while cursos_asignados < len(datos["cursos"]) and intentos < max_intentos:
            intentos += 1
            curso_info = datos["cursos"][cursos_asignados]
            compatibles = [b for b in bloques if b["creditos"] == curso_info["creditos"]]
            if not compatibles:
                compatibles = sorted(bloques, key=lambda x: abs(x["creditos"] - curso_info["creditos"]))[:5]
            bloque = random.choice(compatibles)
            hora = random.choice(horas_inicio)
            salon = random.choice(config.salones)
            if all(horario_valido(d, hora, dur, config, profesor, curso_info["creditos"]) for d, dur in zip(bloque["dias"], bloque["horas"])):
                nueva = AsignacionClase(curso_info, profesor, bloque, hora, salon)
                if not hay_conflictos(nueva, asignaciones):
                    asignaciones.append(nueva)
                    cursos_asignados += 1
        if cursos_asignados < len(datos["cursos"]):
            return None
    return asignaciones

def evaluar_horario(config, asignaciones):
    if asignaciones is None:
        return -float("inf")
    penalizacion = 0
    bonus = 0
    for profesor, datos in config.profesores_config.items():
        asignados = sum(1 for a in asignaciones if a.profesor == profesor)
        if asignados != len(datos["cursos"]):
            penalizacion += abs(asignados - len(datos["cursos"])) * 2000
    creditos_prof = {}
    for a in asignaciones:
        creditos_prof[a.profesor] = creditos_prof.get(a.profesor, 0) + a.creditos
    for profesor, datos in config.profesores_config.items():
        actual = creditos_prof.get(profesor, 0)
        objetivo = datos["creditos_totales"]
        if actual > config.restricciones_globales["creditos_max_profesor"]:
            penalizacion += (actual - config.restricciones_globales["creditos_max_profesor"]) * 1000
        if actual < config.restricciones_globales["creditos_min_profesor"]:
            penalizacion += (config.restricciones_globales["creditos_min_profesor"] - actual) * 1000
        if actual != objetivo:
            penalizacion += abs(actual - objetivo) * 200
    for i in range(len(asignaciones)):
        for j in range(i+1, len(asignaciones)):
            if hay_conflictos(asignaciones[i], [asignaciones[j]]):
                penalizacion += 5000
    for asig in asignaciones:
        for dia, dur in zip(asig.bloque["dias"], asig.bloque["horas"]):
            if not es_bloque_tres_horas_valido(dia, asig.hora_inicio, dur, asig.creditos):
                penalizacion += 10000
            if cumple_horario_preferido(dia, asig.hora_inicio, dur, config, asig.profesor):
                bonus += config.pesos_restricciones["horario_preferido"]
        if asig.estudiantes > config.restricciones_globales["estudiantes_max_salon"]:
            penalizacion += config.pesos_restricciones["estudiantes_por_salon"] * (asig.estudiantes - config.restricciones_globales["estudiantes_max_salon"])
    return bonus - penalizacion

def buscar_mejor_horario(config, bloques, intentos, progress_placeholder):
    mejor_asignaciones = None
    mejor_score = -float("inf")
    for i in range(intentos):
        progress_placeholder.progress((i + 1) / intentos)
        progress_placeholder.text(f"Generando horarios... {i + 1}/{intentos}")
        asignaciones = generar_horario_valido(config, bloques)
        score = evaluar_horario(config, asignaciones)
        if score > mejor_score:
            mejor_score = score
            mejor_asignaciones = asignaciones
    progress_placeholder.text(f"Generación completada. Mejor puntuación: {mejor_score}")
    return mejor_asignaciones, mejor_score

def exportar_horario(asignaciones):
    registros = []
    for asig in asignaciones:
        registros.extend(asig.get_horario_detallado())
    return pd.DataFrame(registros)

# ========================================================
# INTERFAZ STREAMLIT
# ========================================================

def main():
    st.set_page_config(page_title="Generador de Horarios", page_icon="📅", layout="wide")
    st.title("📅 Generador de Horarios Académicos")
    st.markdown("### Sistema de optimización con Algoritmos Heurísticos")

    if "paso" not in st.session_state:
        st.session_state.paso = "login"

    if "salones_catalogo" not in st.session_state:
        st.session_state.salones_catalogo = generar_salones_por_defecto()

    config = st.session_state.get("configuracion") or ConfiguracionSistema()

    if st.session_state.paso == "login":
        st.subheader("Identificación")
        siglas = st.text_input("Siglas del departamento", max_chars=10, placeholder="Ej: QUIM").upper()
        programa = st.text_input("Programa", max_chars=60, placeholder="Ej: INGENIERÍA QUÍMICA").upper()

        if st.button("Continuar"):
            if len(siglas) < 2 or len(programa) < 2:
                st.warning("Ingresa siglas y programa válidos (mínimo 2 caracteres).")
            else:
                st.session_state.siglas = siglas
                st.session_state.programa = programa
                st.session_state.paso = "principal"
                st.experimental_rerun()
        return

    st.sidebar.header("⚙️ Configuración")
    st.sidebar.write(f"**Departamento**: {st.session_state.siglas}")
    st.sidebar.write(f"**Programa**: {st.session_state.programa}")

    uploaded_cursos = st.sidebar.file_uploader(
        "📁 Cargar Excel de cursos",
        type=["xlsx", "xls"],
        help="Debe contener columnas como Profesor, Curso/Materia, Créditos, Estudiantes."
    )
    uploaded_salones = st.sidebar.file_uploader(
        "🏫 Cargar Excel de salones (opcional)",
        type=["xlsx", "xls"],
        help="Columnas sugeridas: Departamento, Salon"
    )

    if uploaded_salones is not None:
        nuevos_salones = cargar_salones_desde_excel(uploaded_salones)
        if nuevos_salones:
            st.session_state.salones_catalogo.update(nuevos_salones)
            st.success("Catálogo de salones actualizado desde Excel.")

    if uploaded_cursos is not None:
        with open("temp_cursos.xlsx", "wb") as f:
            f.write(uploaded_cursos.getbuffer())
        resultado = config.cargar_cursos("temp_cursos.xlsx", st.session_state.siglas, st.session_state.programa)
        if resultado:
            ok, programas_detectados = resultado
            config.establecer_salones(
                st.session_state.salones_catalogo.get(st.session_state.siglas, ["Salón General 1", "Salón General 2"])
            )
            st.session_state.configuracion = config
            st.session_state.programas_detectados = programas_detectados
            st.success("Datos de cursos cargados correctamente.")
        else:
            st.session_state.configuracion = None

    if st.session_state.get("configuracion") is None:
        st.info("Carga un Excel de cursos para continuar.")
        return

    config = st.session_state.configuracion

    with st.expander("📋 Resumen de datos cargados", expanded=True):
        col1, col2, col3 = st.columns(3)
        col1.metric("Profesores", len(config.profesores_config))
        col2.metric("Cursos", sum(len(p["cursos"]) for p in config.profesores_config.values()))
        col3.metric("Salones disponibles", len(config.salones))

        if st.session_state.get("programas_detectados"):
            st.write("Programas detectados en el archivo:")
            st.write(", ".join(st.session_state.programas_detectados))

    intentos = st.sidebar.slider("Número de iteraciones", 50, 500, 200, 50)
    st.sidebar.subheader("Restricciones globales")
    config.restricciones_globales["hora_inicio_min"] = st.sidebar.time_input(
        "Hora inicio mínima", datetime.strptime(config.restricciones_globales["hora_inicio_min"], "%H:%M").time()
    ).strftime("%H:%M")
    config.restricciones_globales["hora_fin_max"] = st.sidebar.time_input(
        "Hora fin máxima", datetime.strptime(config.restricciones_globales["hora_fin_max"], "%H:%M").time()
    ).strftime("%H:%M")
    config.restricciones_globales["creditos_max_profesor"] = st.sidebar.number_input(
        "Créditos máximos por profesor", 1, 40, config.restricciones_globales["creditos_max_profesor"]
    )
    config.restricciones_globales["estudiantes_max_salon"] = st.sidebar.number_input(
        "Estudiantes máximos por salón", 20, 200, config.restricciones_globales["estudiantes_max_salon"]
    )

    if st.button("🚀 Generar horario optimizado", use_container_width=True):
        with st.spinner("Generando horario optimizado..."):
            progress = st.empty()
            bloques = generar_bloques()
            mejor, score = buscar_mejor_horario(config, bloques, intentos, progress)
            if mejor is None:
                st.error("No se pudo generar un horario válido. Ajusta las restricciones o intenta de nuevo.")
            else:
                st.success(f"Horario generado (score: {score})")
                df_horario = exportar_horario(mejor)
                st.session_state.df_horario = df_horario
                st.session_state.score = score

    if st.session_state.get("df_horario") is not None:
        df_horario = st.session_state.df_horario
        score = st.session_state.score
        st.subheader("📊 Horario completo")
        st.dataframe(df_horario, use_container_width=True)

        csv = df_horario.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="💾 Descargar horario (CSV)",
            data=csv,
            file_name=f"horario_{st.session_state.siglas}_{st.session_state.programa}.csv",
            mime="text/csv"
        )

        with st.expander("👨‍🏫 Horario por profesor"):
            for profesor in config.profesores_config.keys():
                df_prof = df_horario[df_horario["Profesor"] == profesor]
                if not df_prof.empty:
                    st.write(f"**{profesor}**")
                    st.dataframe(df_prof, use_container_width=True)

        with st.expander("🏫 Horario por salón"):
            for salon in config.salones:
                df_salon = df_horario[df_horario["Salon"] == salon]
                if not df_salon.empty:
                    st.write(f"**{salon}**")
                    st.dataframe(df_salon, use_container_width=True)

        with st.expander("📈 Estadísticas"):
            col1, col2 = st.columns(2)
            with col1:
                st.write("Distribución de créditos por profesor:")
                st.bar_chart(df_horario.groupby("Profesor")["Créditos"].sum())
            with col2:
                st.write("Uso de salones (conteo de sesiones):")
                st.bar_chart(df_horario.groupby("Salon").size())

            clases_3h = df_horario[df_horario["3h Consecutivas"] == "SÍ"]
            if not clases_3h.empty:
                cumple = clases_3h[clases_3h["Restricción 15:30"] == "CUMPLE"]
                viola = clases_3h[clases_3h["Restricción 15:30"] == "VIOLA"]
                st.metric("Cumplen restricción 15:30", len(cumple))
                st.metric("Violan restricción 15:30", len(viola))
                if not viola.empty:
                    st.warning("Las siguientes clases violan la restricción de 3 horas después de las 15:30:")
                    st.dataframe(viola, use_container_width=True)

    if st.sidebar.button("🔄 Reiniciar", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()

if __name__ == "__main__":
    main()
