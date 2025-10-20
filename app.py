import streamlit as st
import pandas as pd
import random
import json
import numpy as np
from datetime import datetime, timedelta
import io
import os
from pathlib import Path

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

# ========================================================
# CSS Global & Scrollbar Styles (accessibility-conscious)
# ========================================================
GLOBAL_CSS = """
<style>
/* Base layout tweaks */
.main > div { padding-top: 1.25rem; }

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] { gap: 2px; }
.stTabs [data-baseweb="tab"] {
    height: 48px;
    padding: 0 16px;
    background-color: #f0f2f6;
    border-radius: 8px 8px 0 0;
    color: #2C3E50;
}
.stTabs [aria-selected="true"] { background-color: #667eea; color: #fff; }

/* Header banner */
.app-header {
  text-align: center;
  padding: 1.25rem 0;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  margin-bottom: 1rem;
}
.app-header h1 {
  color: white; margin: 0; font-size: 2rem;
}
.app-header p {
  color: white; margin: 0.3rem 0 0 0; font-size: 1rem;
}

/* Cards & accents */
.card {
  border: 1px solid rgba(102,126,234,0.35);
  border-radius: 8px;
  padding: 0.8rem;
  margin: 0.3rem 0;
  background: linear-gradient(135deg, rgba(102,126,234,0.15), rgba(118,75,162,0.08));
}

/* Color legend item */
.legend-item {
  display:flex; align-items:center; margin:5px 0; padding:8px; border-radius:5px;
}

/* Accessible outline buttons on low-contrast backgrounds */
button[kind="outline"] {
  background: transparent !important;
}

/* Custom thin scrollbars (WebKit) */
*::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}
*::-webkit-scrollbar-track {
  background: #f0f2f6;
}
*::-webkit-scrollbar-thumb {
  background: #667eea;
  border-radius: 8px;
  border: 2px solid #f0f2f6;
}
*::-webkit-scrollbar-thumb:hover {
  background: #5a67d8;
}

/* Firefox scrollbar */
* {
  scrollbar-width: thin;
  scrollbar-color: #667eea #f0f2f6;
}

/* Respect reduced motion */
@media (prefers-reduced-motion: reduce) {
  * {
    scroll-behavior: auto !important;
    transition: none !important;
    animation: none !important;
  }
}
</style>
"""

# ========================================================
# LISTA FIJA DE SALONES AE (Administración de Empresas)
# ========================================================
AE_SALONES_FIJOS = [
    "AE 102","AE 103","AE 104","AE 105","AE 106","AE 203C","AE 236",
    "AE 302","AE 303","AE 304","AE 305","AE 306","AE 338","AE 340",
    "AE 341","AE 402","AE 403","AE 404",
]

# ========================================================
# SISTEMA DE RESERVAS DE SALONES (JSON local)
# ========================================================
class SistemaReservasSalones:
    def __init__(self, archivo_reservas="reservas_salones_ae.json"):
        self.archivo_reservas = archivo_reservas
        self.reservas = self.cargar_reservas()

    def cargar_reservas(self):
        if os.path.exists(self.archivo_reservas):
            try:
                with open(self.archivo_reservas, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                st.warning(f"Error al cargar reservas: {e}")
                return {}
        return {}

    def guardar_reservas(self):
        try:
            with open(self.archivo_reservas, "w", encoding="utf-8") as f:
                json.dump(self.reservas, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            st.error(f"Error al guardar reservas: {e}")
            return False

    def a_minutos(self, hhmm):
        h, m = map(int, hhmm.split(":"))
        return h * 60 + m

    def verificar_disponibilidad(self, salon, dia, hora_inicio, hora_fin, programa_solicitante):
        """Bloquea cualquier solapamiento en el mismo salón y día."""
        for reserva_key, reserva_info in self.reservas.items():
            if reserva_info.get("salon") == salon and reserva_info.get("dia") == dia:
                res_inicio = reserva_info["hora_inicio"]
                res_fin = reserva_info["hora_fin"]
                inicio_min = self.a_minutos(hora_inicio)
                fin_min = self.a_minutos(hora_fin)
                res_inicio_min = self.a_minutos(res_inicio)
                res_fin_min = self.a_minutos(res_fin)
                if not (fin_min <= res_inicio_min or inicio_min >= res_fin_min):
                    programa_reserva = reserva_info.get("programa", "")
                    return False, programa_reserva
        return True, None

    def reservar_salon(self, salon, dia, hora_inicio, hora_fin, programa, curso, profesor):
        clave_reserva = f"{salon}_{dia}_{hora_inicio}_{hora_fin}"
        self.reservas[clave_reserva] = {
            "salon": salon,
            "dia": dia,
            "hora_inicio": hora_inicio,
            "hora_fin": hora_fin,
            "programa": programa,
            "curso": curso,
            "profesor": profesor,
            "fecha_reserva": datetime.now().isoformat(),
        }
        return self.guardar_reservas()

    def liberar_reservas_programa(self, programa):
        eliminar = [k for k, r in self.reservas.items() if r.get("programa") == programa]
        for k in eliminar:
            del self.reservas[k]
        return self.guardar_reservas()

    def obtener_salones_disponibles(self, dia, hora_inicio, hora_fin, programa, lista_salones):
        salones_disponibles = []
        for salon in lista_salones:
            ok, _ = self.verificar_disponibilidad(salon, dia, hora_inicio, hora_fin, programa)
            if ok:
                salones_disponibles.append(salon)
        return salones_disponibles

    def obtener_estadisticas_uso(self):
        stats = {
            "total_reservas": len(self.reservas),
            "programas_activos": len(set(r.get("programa", "") for r in self.reservas.values())),
            "salones_en_uso": len(set(r.get("salon", "") for r in self.reservas.values())),
            "reservas_por_programa": {},
            "reservas_por_salon": {},
        }
        for reserva in self.reservas.values():
            prog = reserva.get("programa", "Sin programa")
            sal = reserva.get("salon", "Sin salón")
            stats["reservas_por_programa"][prog] = stats["reservas_por_programa"].get(prog, 0) + 1
            stats["reservas_por_salon"][sal] = stats["reservas_por_salon"].get(sal, 0) + 1
        return stats

# ========================================================
# CONFIGURACIÓN RUM (Programas por colegio y nivel)
# ========================================================
PROGRAMAS_RUM = {
    "COLEGIO DE ADMINISTRACIÓN DE EMPRESAS": {
        "color": "#FF6B6B",
        "salones_compartidos": len(AE_SALONES_FIJOS),
        "prefijo_salon": "AE",
        "sistema_reservas": True,
        "niveles": {
            "Bachilleratos en Administración de Empresas": [
                "Contabilidad","Finanzas","Gerencia de Recursos Humanos","Mercadeo","Gerencia de Operaciones",
                "Sistemas Computadorizados de Información","Administración de Oficinas"
            ],
            "Maestrías en Administración de Empresas": [
                "Administración de Empresas (Programa General)","Finanzas","Gerencia Industrial","Recursos Humanos"
            ],
        },
    },
    "COLEGIO DE ARTES Y CIENCIAS": {
        "color": "#4ECDC4",
        "salones_compartidos": 25,
        "prefijo_salon": "AC",
        "sistema_reservas": False,
        "niveles": {
            "Bachilleratos en Artes": [
                "Literatura Comparada","Economía","Inglés","Historia","Lengua y Literatura Francesa","Estudios Hispánicos",
                "Filosofía","Educación Física – Enseñanza","Educación Física – Adiestramiento y Arbitraje",
                "Artes Plásticas","Ciencias Políticas","Psicología","Ciencias Sociales","Sociología","Teoría del Arte"
            ],
            "Bachilleratos en Ciencias": [
                "Biología","Microbiología Industrial","Pre-Médica","Biotecnología Industrial","Química","Geología","Matemáticas",
                "Matemáticas – Ciencias de la Computación","Educación Matemática","Enfermería","Física","Ciencias Físicas"
            ],
            "Maestrías en Artes": [
                "Estudios Culturales y Humanísticos","Estudios Hispánicos","Educación en Inglés","Kinesiología"
            ],
            "Maestrías en Ciencias": [
                "Biología","Química","Geología","Ciencias Marinas","Física","Matemáticas Aplicadas","Matemática Estadística",
                "Matemática Pura","Enseñanza de las Matemáticas a nivel preuniversitario","Computación Científica","Psicología Escolar"
            ],
            "Doctorados en Filosofía": [
                "Ciencias Marinas","Química Aplicada","Psicología Escolar"
            ],
        },
    },
    "COLEGIO DE CIENCIAS AGRÍCOLAS": {
        "color": "#96CEB4",
        "salones_compartidos": 15,
        "prefijo_salon": "CA",
        "sistema_reservas": False,
        "niveles": {
            "Bachilleratos en Ciencias Agrícolas": [
                "Ciencias Agrícolas","Agronomía","Economía Agrícola","Horticultura","Ciencia Animal","Protección de Cultivos",
                "Agronegocios","Educación Agrícola","Extensión Agrícola","Suelos","Sistemas Agrícolas y Ambientales",
                "Pre-Veterinaria (No conducente a grado)"
            ],
            "Maestrías en Ciencias": [
                "Agronomía","Ciencias y Tecnología de Alimentos","Economía Agrícola","Educación Agrícola","Extensión Agrícola",
                "Horticultura","Ciencia Animal","Protección de Cultivos","Suelos"
            ],
        },
    },
    "COLEGIO DE INGENIERÍA": {
        "color": "#FFEAA7",
        "salones_compartidos": 20,
        "prefijo_salon": "ING",
        "sistema_reservas": False,
        "niveles": {
            "Bachilleratos en Ingeniería": [
                "Ingeniería Química","Ingeniería Civil","Ingeniería de Computadoras","Ciencias e Ingeniería de la Computación",
                "Ingeniería Eléctrica","Ingeniería Industrial","Ingeniería Mecánica","Ingeniería de Software","Agrimensura y Topografía"
            ],
            "Maestrías en Ciencias": [
                "Bioingeniería","Ingeniería Química","Ingeniería Civil","Ingeniería de Computadoras","Ingeniería Eléctrica",
                "Ingeniería Industrial","Ciencia e Ingeniería de Materiales","Ingeniería Mecánica"
            ],
            "Maestrías en Ingeniería": [
                "Bioingeniería","Ingeniería Química","Ingeniería Civil","Ingeniería de Computadoras","Ingeniería Eléctrica",
                "Ingeniería Industrial","Ciencia e Ingeniería de Materiales","Ingeniería Mecánica"
            ],
            "Doctorados en Filosofía": [
                "Bioingeniería","Ingeniería Química","Ingeniería Civil","Ingeniería Eléctrica","Ingeniería Mecánica",
                "Ciencias e Ingeniería de la Información y la Computación"
            ],
        },
    },
}

# ========================================================
# UTILS DE TIEMPO Y BLOQUES
# ========================================================
def a_minutos(hhmm):
    h, m = map(int, hhmm.split(":"))
    return h * 60 + m

def obtener_prefijo_salon(salon_str):
    if not salon_str: return "SALON"
    if " " in salon_str: return salon_str.split(" ")[0].strip()
    if "-" in salon_str: return salon_str.split("-")[0].strip()
    return salon_str.split()[0].strip()

# Horario de 7:00 a 19:20 en intervalos de 30 min
horas_inicio = []
for h in range(7, 20):
    for m in [0, 30]:
        if h == 19 and m > 20: break
        horas_inicio.append(f"{h:02d}:{m:02d}")

def generar_bloques():
    bloques = []; id_counter = 1
    combinaciones_4dias = [["Lu","Ma","Mi","Ju"],["Lu","Ma","Mi","Vi"],["Lu","Ma","Ju","Vi"],["Lu","Mi","Ju","Vi"],["Ma","Mi","Ju","Vi"]]
    for dias in combinaciones_4dias:
        bloques.append({"id": id_counter, "dias": dias, "horas": [1]*4, "creditos": 4}); id_counter += 1
    combinaciones_2dias = [["Lu","Mi"],["Lu","Vi"],["Ma","Ju"],["Mi","Vi"]]
    for dias in combinaciones_2dias:
        bloques.append({"id": id_counter, "dias": dias, "horas": [2,2], "creditos": 4}); id_counter += 1
    bloques.append({"id": id_counter, "dias": ["Lu","Mi","Vi"], "horas": [1,1,1], "creditos": 3}); id_counter += 1
    bloques.append({"id": id_counter, "dias": ["Ma","Ju"], "horas": [1.5,1.5], "creditos": 3}); id_counter += 1
    combinaciones_5creditos = [
        (["Lu","Mi","Vi"], [2,2,1]), (["Lu","Ma","Mi","Vi"], [1,1,1,2]), (["Lu","Ma","Ju","Vi"], [1,1,1,2]),
        (["Lu","Mi","Ju","Vi"], [1,1,1,2]), (["Ma","Mi","Ju","Vi"], [1,1,1,2]), (["Ma","Ju","Vi"], [1.5,1.5,2]),
        (["Lu","Ma","Mi","Ju","Vi"], [1,1,1,1,1]), (["Lu","Ma","Mi"], [2,1,2]),
    ]
    for dias, horas in combinaciones_5creditos:
        bloques.append({"id": id_counter, "dias": dias, "horas": horas, "creditos": 5}); id_counter += 1
    for dia in ["Lu","Ma","Mi","Ju","Vi"]:
        bloques.append({"id": id_counter, "dias": [dia], "horas": [3], "creditos": 3}); id_counter += 1
    return bloques

# Tabla de créditos adicionales por tamaño de sección
tabla_creditos = {
    1: [(1,44,0),(45,74,0.5),(75,104,1),(105,134,1.5),(135,164,2),(165,194,2.5),(195,224,3),(225,254,3.5),(255,284,4),(285,314,4.5),(315,344,5),(345,374,5.5),(375,404,6),(405,434,6.5),(435,464,7),(465,494,7.5),(495,524,8)],
    2: [(1,37,0),(38,52,0.5),(53,67,1),(68,82,1.5),(83,97,2),(98,112,2.5),(113,127,3),(128,142,3.5),(143,157,4),(158,172,4.5),(173,187,5),(188,202,5.5),(203,217,6),(218,232,6.5),(233,247,7),(248,262,7.5),(263,277,8)],
    3: [(1,34,0),(35,44,0.5),(45,54,1),(55,64,1.5),(65,74,2),(75,84,2.5),(85,94,3),(95,104,3.5),(105,114,4),(115,124,4.5),(125,134,5),(135,144,5.5),(145,154,6),(155,164,6.5),(165,174,7),(175,184,7.5),(185,194,8)],
    4: [(1,33,0),(34,41,0.5),(42,48,1),(49,56,1.5),(57,63,2),(64,71,2.5),(72,78,3),(79,86,3.5),(87,93,4),(94,101,4.5),(102,108,5),(109,116,5.5),(117,123,6),(124,131,6.5),(132,138,7),(139,146,7.5),(147,153,8)],
    5: [(1,32,0),(33,38,0.5),(39,44,1),(45,50,1.5),(51,56,2),(57,63,2.5),(64,69,3),(70,75,3.5),(76,81,4),(82,88,4.5),(89,93,5),(94,99,5.5),(100,104,6),(105,110,6.5),(111,116,7),(117,122,7.5),(123,128,8)],
    6: [(1,32,0),(33,37,0.5),(38,42,1),(43,47,1.5),(48,52,2),(53,57,2.5),(58,62,3),(63,67,3.5),(68,72,4),(73,77,4.5),(78,82,5),(83,87,5.5),(88,92,6),(93,97,6.5),(98,102,7),(103,107,7.5),(108,112,8)],
}

def calcular_creditos_adicionales(horas_contacto, estudiantes):
    if horas_contacto not in tabla_creditos:
        return 0
    for minimo, maximo, creditos in tabla_creditos[horas_contacto]:
        if minimo <= estudiantes <= maximo:
            return creditos
    return 0

def es_bloque_tres_horas_valido(dia, hora_inicio, duracion, creditos):
    """Clases 3 créditos con 3 horas consecutivas solo después de 15:30."""
    if creditos == 3 and duracion == 3:
        dias_semana = ["Lu", "Ma", "Mi", "Ju", "Vi"]
        if dia in dias_semana:
            inicio_minutos = a_minutos(hora_inicio)
            restriccion_minutos = a_minutos("15:30")
            if inicio_minutos < restriccion_minutos:
                return False
    return True

# ========================================================
# CONFIGURACIÓN DEL SISTEMA (Excel + reservas)
# ========================================================
class ConfiguracionSistema:
    def __init__(self, archivo_excel=None, programa_actual=None, colegio_actual=None):
        self.archivo_excel = archivo_excel
        self.programa_actual = programa_actual
        self.colegio_actual = colegio_actual
        self.profesores_config = {}
        self.salones = []
        self.cursos_df = None

        self.usa_reservas = False
        self.sistema_reservas = None
        if colegio_actual and colegio_actual in PROGRAMAS_RUM:
            self.usa_reservas = PROGRAMAS_RUM[colegio_actual].get("sistema_reservas", False)
            self.sistema_reservas = SistemaReservasSalones() if self.usa_reservas else None

        self.restricciones_globales = {
            "horarios_prohibidos": {"Ma": [("10:30", "12:30")], "Ju": [("10:30", "12:30")]},
            "hora_inicio_min": "07:30",
            "hora_fin_max": "19:30",
            "creditos_max_profesor": 15,
            "creditos_min_profesor": 8,
            "estudiantes_max_salon": 50,
            "horas_max_dia": 8,
            "dias_max_profesor": 5,
        }

        self.pesos_restricciones = {
            "horario_preferido": 30,
            "compactacion_horario": 20,
            "equilibrio_creditos": 25,
            "utilizacion_salones": 15,
            "estudiantes_por_salon": 10,
            "horas_consecutivas": 18,
            "distribucion_semanal": 12,
            "evitar_horas_pico": 8,
        }

        if archivo_excel:
            self.cargar_desde_excel()

    def cargar_desde_excel(self):
        try:
            excel_data = pd.read_excel(self.archivo_excel, sheet_name=None)
            st.write(f"📊 Hojas disponibles en el Excel: {list(excel_data.keys())}")

            hoja_cursos = None
            for nombre_hoja, df in excel_data.items():
                st.write(f"\n🔍 Analizando hoja '{nombre_hoja}':")
                st.write(f"Columnas: {list(df.columns)}")
                columnas_df = [col.lower().strip() for col in df.columns]
                if any("profesor" in col or "docente" in col for col in columnas_df) and \
                   any("curso" in col or "materia" in col or "asignatura" in col for col in columnas_df):
                    hoja_cursos = df
                    st.success(f"✅ Hoja '{nombre_hoja}' seleccionada como fuente de datos")
                    break

            if hoja_cursos is None:
                st.error("❌ No se encontró una hoja con datos de cursos válidos")
                return

            self.cursos_df = hoja_cursos
            self.procesar_datos_excel()
        except Exception as e:
            st.error(f"❌ Error al cargar el archivo Excel: {e}")
            st.info("ℹ️ Usando configuración por defecto")

    def procesar_datos_excel(self):
        if self.cursos_df is None:
            return
        df = self.cursos_df.copy()
        df.columns = [col.lower().strip().replace(" ", "_") for col in df.columns]

        mapeo = {
            "profesor": ["profesor","docente","teacher","instructor"],
            "curso": ["curso","materia","asignatura","subject","course"],
            "creditos": ["creditos","créditos","credits","horas"],
            "estudiantes": ["estudiantes","alumnos","students","enrollment","seccion"],
        }
        cols_finales = {}
        for campo, posibles in mapeo.items():
            for col in df.columns:
                if any(pos in col for pos in posibles):
                    cols_finales[campo] = col
                    break

        st.write(f"🔗 Mapeo de columnas: {cols_finales}")
        if "profesor" not in cols_finales or "curso" not in cols_finales:
            st.error("❌ Error: No se encontraron las columnas básicas (profesor, curso)")
            return

        if "creditos" not in cols_finales:
            df["creditos_default"] = 3
            cols_finales["creditos"] = "creditos_default"
            st.warning("⚠️ No se encontró columna de créditos, usando 3 por defecto")
        if "estudiantes" not in cols_finales:
            df["estudiantes_default"] = 30
            cols_finales["estudiantes"] = "estudiantes_default"
            st.warning("⚠️ No se encontró columna de estudiantes, usando 30 por defecto")

        df = df.dropna(subset=[cols_finales["profesor"], cols_finales["curso"]])
        profesores_unicos = df[cols_finales["profesor"]].unique()
        st.info(f"👨‍🏫 Profesores encontrados: {len(profesores_unicos)}")

        for profesor in profesores_unicos:
            if pd.isna(profesor) or str(profesor).strip() == "": continue
            profesor = str(profesor).strip()
            cursos_profesor = df[df[cols_finales["profesor"]] == profesor]
            cursos_lista = []; creditos_totales = 0
            for _, fila in cursos_profesor.iterrows():
                curso_nombre = str(fila[cols_finales["curso"]]).strip()
                try: creditos = int(float(fila[cols_finales["creditos"]]))
                except (ValueError, TypeError): creditos = 3
                try: estudiantes = int(float(fila[cols_finales["estudiantes"]]))
                except (ValueError, TypeError): estudiantes = 30
                if curso_nombre and curso_nombre != "nan":
                    cursos_lista.append({"nombre": curso_nombre, "creditos": creditos, "estudiantes": estudiantes})
                    creditos_totales += creditos
            if cursos_lista:
                self.profesores_config[profesor] = {
                    "cursos": cursos_lista,
                    "creditos_totales": creditos_totales,
                    "horario_preferido": {},
                    "horario_no_disponible": {},
                }
                st.write(f"📚 {profesor}: {len(cursos_lista)} cursos, {creditos_totales} créditos totales")

        # Salones según colegio
        if self.colegio_actual and self.colegio_actual in PROGRAMAS_RUM:
            info = PROGRAMAS_RUM[self.colegio_actual]
            if self.colegio_actual == "COLEGIO DE ADMINISTRACIÓN DE EMPRESAS":
                self.salones = AE_SALONES_FIJOS.copy()
            else:
                num_salones = info.get("salones_compartidos", 15)
                prefijo = info.get("prefijo_salon", "SALON")
                self.salones = [f"{prefijo}-{i+1:02d}" for i in range(num_salones)]
        else:
            self.salones = [f"Salon {i+1}" for i in range(15)]

        st.success(f"✅ Configuración completada: {len(self.profesores_config)} profesores, {len(self.salones)} salones")

# ========================================================
# VALIDACIONES DE HORARIO
# ========================================================
def horario_valido(dia, hora_inicio, duracion, profesor=None, creditos=None, config=None):
    ini_min = a_minutos(hora_inicio); fin_min = ini_min + int(duracion * 60)
    if fin_min > a_minutos(config.restricciones_globales["hora_fin_max"]): return False
    if ini_min < a_minutos(config.restricciones_globales["hora_inicio_min"]): return False
    if creditos and not es_bloque_tres_horas_valido(dia, hora_inicio, duracion, creditos): return False

    restricciones_horario = config.restricciones_globales["horarios_prohibidos"]
    if dia in restricciones_horario:
        for r_ini, r_fin in restricciones_horario[dia]:
            r_ini_min = a_minutos(r_ini); r_fin_min = a_minutos(r_fin)
            if not (fin_min <= r_ini_min or ini_min >= r_fin_min): return False

    if profesor and profesor in config.profesores_config:
        prof_config = config.profesores_config[profesor]
        if dia in prof_config["horario_no_disponible"]:
            for r_ini, r_fin in prof_config["horario_no_disponible"][dia]:
                r_ini_min = a_minutos(r_ini); r_fin_min = a_minutos(r_fin)
                if not (fin_min <= r_ini_min or ini_min >= r_fin_min): return False
    return True

def cumple_horario_preferido(dia, hora_inicio, duracion, profesor, config):
    if profesor not in config.profesores_config: return False
    prof_config = config.profesores_config[profesor]
    if dia not in prof_config["horario_preferido"]: return False
    ini_min = a_minutos(hora_inicio); fin_min = ini_min + int(duracion * 60)
    for pref_ini, pref_fin in prof_config["horario_preferido"][dia]:
        pref_ini_min = a_minutos(pref_ini); pref_fin_min = a_minutos(pref_fin)
        if ini_min >= pref_ini_min and fin_min <= pref_fin_min: return True
    return False

# ========================================================
# REPRESENTACIÓN DE ASIGNACIÓN
# ========================================================
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
        registros = []
        for dia, duracion in zip(self.bloque["dias"], self.bloque["horas"]):
            hora_fin_min = a_minutos(self.hora_inicio) + int(duracion * 60)
            hora_fin = f"{hora_fin_min//60:02d}:{hora_fin_min%60:02d}"
            bloque_prefijo = obtener_prefijo_salon(self.salon)
            registros.append({
                "Curso": self.curso_nombre, "Profesor": self.profesor, "Bloque": bloque_prefijo,
                "Dia": dia, "Hora Inicio": self.hora_inicio, "Hora Fin": hora_fin,
                "Duración": duracion, "Créditos": self.creditos, "Créditos Extra": self.creditos_extra,
                "Estudiantes": self.estudiantes, "Salon": self.salon
            })
        return registros

# ========================================================
# GENERADORES DE HORARIO (con/sin reservas)
# ========================================================
def hay_conflictos(nueva_asignacion, asignaciones_existentes):
    for asignacion in asignaciones_existentes:
        for dia_nuevo, dur_nuevo in zip(nueva_asignacion.bloque["dias"], nueva_asignacion.bloque["horas"]):
            ini_nuevo = a_minutos(nueva_asignacion.hora_inicio); fin_nuevo = ini_nuevo + int(dur_nuevo * 60)
            for dia_exist, dur_exist in zip(asignacion.bloque["dias"], asignacion.bloque["horas"]):
                if dia_nuevo == dia_exist:
                    ini_exist = a_minutos(asignacion.hora_inicio); fin_exist = ini_exist + int(dur_exist * 60)
                    if not (fin_nuevo <= ini_exist or ini_nuevo >= fin_exist):
                        if nueva_asignacion.profesor == asignacion.profesor: return True
                        if nueva_asignacion.salon == asignacion.salon: return True
    return False

def generar_horario_valido_con_reservas(config, bloques, horas_inicio):
    asignaciones = []
    for profesor, prof_config in config.profesores_config.items():
        cursos_asignados = 0; intentos = 0; max_intentos = 4000
        while cursos_asignados < len(prof_config["cursos"]) and intentos < max_intentos:
            intentos += 1
            curso_info = prof_config["cursos"][cursos_asignados]
            compatibles = [b for b in bloques if b["creditos"] == curso_info["creditos"]]
            if not compatibles:
                compatibles = sorted(bloques, key=lambda x: abs(x["creditos"] - curso_info["creditos"]))[:5]
            bloque = random.choice(compatibles)
            hora_inicio = random.choice(horas_inicio)
            salones_disponibles = []
            for dia, duracion in zip(bloque["dias"], bloque["horas"]):
                hora_fin_min = a_minutos(hora_inicio) + int(duracion * 60)
                hora_fin = f"{hora_fin_min//60:02d}:{hora_fin_min%60:02d}"
                salones_dia = config.sistema_reservas.obtener_salones_disponibles(
                    dia, hora_inicio, hora_fin, config.programa_actual, config.salones
                )
                if not salones_disponibles:
                    salones_disponibles = salones_dia
                else:
                    salones_disponibles = list(set(salones_disponibles) & set(salones_dia))
            if not salones_disponibles: continue
            salon = random.choice(salones_disponibles)
            valido = True
            for dia, duracion in zip(bloque["dias"], bloque["horas"]):
                if not horario_valido(dia, hora_inicio, duracion, profesor, curso_info["creditos"], config):
                    valido = False; break
            if not valido: continue
            nueva = AsignacionClase(curso_info, profesor, bloque, hora_inicio, salon)
            if not hay_conflictos(nueva, asignaciones):
                asignaciones.append(nueva); cursos_asignados += 1
        if cursos_asignados < len(prof_config["cursos"]): return None
    return asignaciones

def generar_horario_valido(config, bloques, horas_inicio):
    asignaciones = []
    for profesor, prof_config in config.profesores_config.items():
        cursos_asignados = 0; intentos = 0; max_intentos = 3000
        while cursos_asignados < len(prof_config["cursos"]) and intentos < max_intentos:
            intentos += 1
            curso_info = prof_config["cursos"][cursos_asignados]
            compatibles = [b for b in bloques if b["creditos"] == curso_info["creditos"]]
            if not compatibles:
                compatibles = sorted(bloques, key=lambda x: abs(x["creditos"] - curso_info["creditos"]))[:5]
            bloque = random.choice(compatibles)
            hora_inicio = random.choice(horas_inicio)
            salon = random.choice(config.salones)
            valido = True
            for dia, duracion in zip(bloque["dias"], bloque["horas"]):
                if not horario_valido(dia, hora_inicio, duracion, profesor, curso_info["creditos"], config):
                    valido = False; break
            if not valido: continue
            nueva = AsignacionClase(curso_info, profesor, bloque, hora_inicio, salon)
            if not hay_conflictos(nueva, asignaciones):
                asignaciones.append(nueva); cursos_asignados += 1
        if cursos_asignados < len(prof_config["cursos"]): return None
    return asignaciones

def evaluar_horario(asignaciones, config):
    if asignaciones is None: return -float("inf")
    penalizacion = 0; bonus = 0
    for profesor, prof_config in config.profesores_config.items():
        asignados = sum(1 for a in asignaciones if a.profesor == profesor)
        requeridos = len(prof_config["cursos"])
        if asignados != requeridos:
            penalizacion += abs(asignados - requeridos) * 2000
    creditos_por_prof = {}
    for asig in asignaciones:
        creditos_por_prof.setdefault(asig.profesor, 0)
        creditos_por_prof[asig.profesor] += asig.creditos
    for profesor, prof_config in config.profesores_config.items():
        actuales = creditos_por_prof.get(profesor, 0)
        objetivo = prof_config["creditos_totales"]
        if actuales > config.restricciones_globales["creditos_max_profesor"]:
            penalizacion += (actuales - config.restricciones_globales["creditos_max_profesor"]) * 1000
        if actuales < config.restricciones_globales["creditos_min_profesor"]:
            penalizacion += (config.restricciones_globales["creditos_min_profesor"] - actuales) * 1000
        if actuales != objetivo:
            penalizacion += abs(actuales - objetivo) * 200
    for i, a1 in enumerate(asignaciones):
        for j, a2 in enumerate(asignaciones):
            if i >= j: continue
            if hay_conflictos(a1, [a2]): penalizacion += 5000
    for asig in asignaciones:
        for dia, duracion in zip(asig.bloque["dias"], asig.bloque["horas"]):
            if not es_bloque_tres_horas_valido(dia, asig.hora_inicio, duracion, asig.creditos):
                penalizacion += 10000
    pesos = config.pesos_restricciones
    for asig in asignaciones:
        for dia, duracion in zip(asig.bloque["dias"], asig.bloque["horas"]):
            if cumple_horario_preferido(dia, asig.hora_inicio, duracion, asig.profesor, config):
                bonus += pesos["horario_preferido"]
        if asig.estudiantes > config.restricciones_globales["estudiantes_max_salon"]:
            penalizacion += pesos["estudiantes_por_salon"] * (asig.estudiantes - config.restricciones_globales["estudiantes_max_salon"])
    return bonus - penalizacion

def buscar_mejor_horario(config, bloques, horas_inicio, intentos=200):
    mejor_asign = None; mejor_score = -float("inf")
    progress_bar = st.progress(0); status_text = st.empty()
    for i in range(intentos):
        progress_bar.progress((i + 1) / intentos)
        status_text.text(f"🔄 Generando horarios... {i+1}/{intentos}")
        asignaciones = generar_horario_valido_con_reservas(config, bloques, horas_inicio) if config.usa_reservas else generar_horario_valido(config, bloques, horas_inicio)
        score = evaluar_horario(asignaciones, config)
        if score > mejor_score:
            mejor_score = score; mejor_asign = asignaciones
    status_text.text(f"✅ Generación completada. Mejor puntuación: {mejor_score}")
    return mejor_asign, mejor_score

def exportar_horario(asignaciones):
    registros = []
    for asig in asignaciones:
        registros.extend(asig.get_horario_detallado())
    df = pd.DataFrame(registros)
    for col in ["3h Consecutivas","Restricción 15:30"]:
        if col in df.columns:
            df = df.drop(columns=[col])
    return df

def _nombre_archivo_horario(programa):
    safe_prog = "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in (programa or "programa"))
    return f"horario_{safe_prog}.json"

def guardar_horario_json(df_horario, programa):
    try:
        ruta = _nombre_archivo_horario(programa)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(df_horario.to_dict(orient="records"), f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"Error al guardar horario: {e}")
        return False

def cargar_horario_json(programa):
    ruta = _nombre_archivo_horario(programa)
    if os.path.exists(ruta):
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                data = json.load(f)
            return pd.DataFrame(data)
        except Exception as e:
            st.warning(f"Error al cargar horario guardado: {e}")
            return None
    return None

def guardar_reservas_horario(asignaciones, programa, config):
    if not config or not config.usa_reservas or not config.sistema_reservas:
        return True
    config.sistema_reservas.liberar_reservas_programa(programa)
    for asig in asignaciones:
        for dia, duracion in zip(asig.bloque["dias"], asig.bloque["horas"]):
            hora_fin_min = a_minutos(asig.hora_inicio) + int(duracion * 60)
            hora_fin = f"{hora_fin_min//60:02d}:{hora_fin_min%60:02d}"
            config.sistema_reservas.reservar_salon(
                salon=asig.salon, dia=dia, hora_inicio=asig.hora_inicio, hora_fin=hora_fin,
                programa=programa, curso=asig.curso_nombre, profesor=asig.profesor
            )
    return True

# ========================================================
# VISUALIZACIÓN: Calendario estilo Google Calendar (Plotly)
# ========================================================
def generar_colores_cursos(df_horario):
    cursos_unicos = df_horario["Curso"].unique()
    colores_base = [
        "#FF6B6B","#4ECDC4","#45B7D1","#96CEB4","#FFEAA7","#DDA0DD","#98D8C8","#F7DC6F","#BB8FCE","#85C1E9",
        "#F8C471","#82E0AA","#F1948A","#85C1E9","#D5A6BD","#AED6F1","#A9DFBF","#F9E79F","#D7BDE2","#A3E4D7",
    ]
    return {curso: colores_base[i % len(colores_base)] for i, curso in enumerate(cursos_unicos)}

def crear_calendario_interactivo(df_horario, profesor_filtro=None):
    if profesor_filtro and profesor_filtro != "Todos los profesores":
        df_filtrado = df_horario[df_horario["Profesor"] == profesor_filtro]
        titulo_calendario = f"📅 Calendario de {profesor_filtro}"
    else:
        df_filtrado = df_horario
        titulo_calendario = "📅 Calendario Semanal de Clases - Vista Completa"

    colores_cursos = generar_colores_cursos(df_horario)
    dias_map = {"Lu":1,"Ma":2,"Mi":3,"Ju":4,"Vi":5}
    dias_nombres = ["","Lunes","Martes","Miércoles","Jueves","Viernes"]

    salones_por_dia = {}
    for dia in dias_map.keys():
        salones_unicos = df_filtrado[df_filtrado["Dia"] == dia]["Salon"].unique().tolist()
        salones_por_dia[dia] = sorted(salones_unicos)

    fig = go.Figure()
    for _, fila in df_filtrado.iterrows():
        dia = fila["Dia"]; dia_num = dias_map[dia]
        salones_dia = salones_por_dia.get(dia, [])
        total_cols = max(len(salones_dia), 1)
        salon_idx = salones_dia.index(fila["Salon"]) if fila["Salon"] in salones_dia else 0
        dia_ancho_total = 0.9
        col_ancho = dia_ancho_total / total_cols
        x_center = (dia_num - 0.45) + (salon_idx + 0.5) * col_ancho
        x0 = x_center - (col_ancho * 0.45); x1 = x_center + (col_ancho * 0.45)
        hora_inicio_min = a_minutos(fila["Hora Inicio"]); hora_fin_min = a_minutos(fila["Hora Fin"])

        fig.add_shape(type="rect", x0=x0, y0=hora_inicio_min, x1=x1, y1=hora_fin_min,
                      fillcolor=colores_cursos.get(fila["Curso"], "#667eea"), opacity=0.85,
                      line=dict(color="#222", width=1))
        texto_clase = (
            f"<b>{fila['Curso']}</b><br>👨‍🏫 {fila['Profesor']}<br>🏫 {fila['Salon']}<br>"
            f"👥 {fila['Estudiantes']} estudiantes<br>⏰ {fila['Hora Inicio']} - {fila['Hora Fin']}<br>"
            f"📚 {fila['Créditos']} créditos"
        )
        fig.add_annotation(
            x=x_center, y=(hora_inicio_min + hora_fin_min) / 2,
            text=f"<b>{fila['Curso']}</b><br>{fila['Hora Inicio']}-{fila['Hora Fin']}<br>{fila['Salon']}",
            showarrow=False, font=dict(color="white", size=12, family="Arial Black"),
            bgcolor="rgba(0,0,0,0.7)", bordercolor="white", borderwidth=1, borderpad=4, hovertext=texto_clase
        )

    fig.update_layout(
        title={'text': titulo_calendario, 'x': 0.5, 'xanchor': 'center', 'font': {'size': 24, 'color': '#2C3E50'}},
        xaxis=dict(tickmode='array', tickvals=[1,2,3,4,5], ticktext=dias_nombres[1:], range=[0.5, 5.5],
                   showgrid=True, gridcolor='lightgray', title="Días de la Semana",
                   title_font=dict(size=16, color='#34495E')),
        yaxis=dict(tickmode='array', tickvals=[i*60 for i in range(7, 21)], ticktext=[f"{i:02d}:00" for i in range(7, 21)],
                   range=[7*60, 20*60], showgrid=True, gridcolor='lightgray', title="Hora del Día",
                   title_font=dict(size=16, color='#34495E'), autorange='reversed'),
        plot_bgcolor='white', paper_bgcolor='#F8F9FA', width=1400, height=900, showlegend=False,
        margin=dict(l=60, r=60, t=80, b=60)
    )
    for hora in range(8, 20):
        fig.add_hline(y=hora*60, line_dash="dot", line_color="gray", opacity=0.5)
    return fig, colores_cursos

def mostrar_leyenda_cursos(colores_cursos, df_horario, profesor_filtro=None):
    if profesor_filtro and profesor_filtro != "Todos los profesores":
        cursos_filtrados = df_horario[df_horario["Profesor"] == profesor_filtro]["Curso"].unique()
        colores_mostrar = {curso: color for curso, color in colores_cursos.items() if curso in cursos_filtrados}
        st.subheader(f"🎨 Cursos de {profesor_filtro}")
    else:
        colores_mostrar = colores_cursos
        st.subheader("🎨 Leyenda de Colores por Curso")
    num_cols = 3; cols = st.columns(num_cols)
    for i, (curso, color) in enumerate(colores_mostrar.items()):
        with cols[i % num_cols]:
            st.markdown(
                f'<div class="legend-item" style="background-color: {color}20; border-left: 4px solid {color};">'
                f'<div style="width:20px;height:20px;background-color:{color};margin-right:10px;border-radius:3px;"></div>'
                f'<span style="font-weight:500;color:#2C3E50;">{curso}</span></div>',
                unsafe_allow_html=True
            )

def mostrar_estado_reservas(config):
    if not config or not config.usa_reservas or not config.sistema_reservas: return
    st.subheader("🏫 Estado Actual de Reservas de Salones")
    stats = config.sistema_reservas.obtener_estadisticas_uso()
    col1,col2,col3,col4 = st.columns(4)
    with col1: st.metric("📋 Total Reservas", stats["total_reservas"])
    with col2: st.metric("📚 Programas Activos", stats["programas_activos"])
    with col3: st.metric("🏫 Salones en Uso", stats["salones_en_uso"])
    with col4:
        disponibles = (len(config.salones) if config.salones else 0) - stats["salones_en_uso"]
        st.metric("✅ Salones Disponibles", max(disponibles, 0))
    if stats["reservas_por_programa"]:
        st.write("**📊 Reservas por Programa:**")
        for programa, cantidad in stats["reservas_por_programa"].items():
            st.write(f"• {programa}: {cantidad} reservas")
    with st.expander("🔍 Ver todas las reservas activas"):
        if config.sistema_reservas.reservas:
            reservas_df = []
            for _, reserva in config.sistema_reservas.reservas.items():
                reservas_df.append({
                    "Salón": reserva["salon"], "Día": reserva["dia"],
                    "Hora Inicio": reserva["hora_inicio"], "Hora Fin": reserva["hora_fin"],
                    "Programa": reserva["programa"], "Curso": reserva["curso"], "Profesor": reserva["profesor"]
                })
            st.dataframe(pd.DataFrame(reservas_df), use_container_width=True)
        else:
            st.info("No hay reservas activas")

# ========================================================
# ICS EXPORT & GOOGLE CALENDAR (Opcional)
# ========================================================
def df_to_ics(df_horario, calendar_name="RUM Horarios"):
    """Genera contenido ICS básico desde el DataFrame."""
    def dtstamp():
        return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    ics_lines = [
        "BEGIN:VCALENDAR","VERSION:2.0","PRODID:-//RUM Horarios//mxm.dk//",
        f"X-WR-CALNAME:{calendar_name}",
    ]
    # Evento por fila: se asume mismo día semanal sin fechas específicas -> usar fecha ficticia próxima semana
    dias_map_real = {"Lu": 0, "Ma": 1, "Mi": 2, "Ju": 3, "Vi": 4}
    today = datetime.today()
    monday = today - timedelta(days=today.weekday())  # inicio semana (lunes)
    for _, row in df_horario.iterrows():
        dia = row["Dia"]; if dia not in dias_map_real: continue
        start_date = monday + timedelta(days=dias_map_real[dia])
        h_i, m_i = map(int, row["Hora Inicio"].split(":"))
        h_f, m_f = map(int, row["Hora Fin"].split(":"))
        dt_start = start_date.replace(hour=h_i, minute=m_i, second=0)
        dt_end = start_date.replace(hour=h_f, minute=m_f, second=0)
        uid = f"{row['Curso']}-{row['Profesor']}-{row['Salon']}-{dia}-{row['Hora Inicio']}".replace(" ", "_")
        ics_lines += [
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{dtstamp()}",
            f"DTSTART:{dt_start.strftime('%Y%m%dT%H%M%S')}",
            f"DTEND:{dt_end.strftime('%Y%m%dT%H%M%S')}",
            f"SUMMARY:{row['Curso']} ({row['Salon']})",
            f"DESCRIPTION:Profesor {row['Profesor']} | Estudiantes {row['Estudiantes']} | Créditos {row['Créditos']}",
            "END:VEVENT",
        ]
    ics_lines.append("END:VCALENDAR")
    return "\r\n".join(ics_lines)

def calendario_ui_export(df_horario):
    st.markdown("### 📆 Exportar a Google Calendar / ICS")
    col_a, col_b = st.columns(2)
    with col_a:
        ics_content = df_to_ics(df_horario, calendar_name=f"RUM - {st.session_state.get('programa_seleccionado','Programa')}")
        st.download_button(
            label="📥 Descargar archivo .ics",
            data=ics_content, file_name="horario.ics", mime="text/calendar"
        )
        st.info("Abre el .ics con Google Calendar para importar los eventos.")
    with col_b:
        st.warning("Integración directa con Google Calendar requiere credenciales OAuth locales (client_secret.json).")
        st.write("Si agregas 'client_secret.json' y ejecutas localmente, podrás autorizar y subir eventos.")

# ========================================================
# PERSISTENCIA DE VISTA Y TABS
# ========================================================
def _creditos_unicos_por_profesor(df):
    if df.empty: return 0
    df_unique = df[["Profesor","Curso","Créditos"]].drop_duplicates()
    return df_unique.groupby("Profesor")["Créditos"].sum()

def _mostrar_tabs_horario(df_horario):
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📅 Calendario Visual","📊 Horario Completo","👨‍🏫 Por Profesor","🏫 Por Salón","📈 Estadísticas"])
    with tab1:
        st.subheader("📅 Vista de Calendario Interactivo")
        st.info("Los bloques se distribuyen por columnas de salón para evitar superposición.")
        profesores_disponibles = ["Todos los profesores"] + sorted(df_horario["Profesor"].unique().tolist())
        profesor_filtro = st.selectbox("👨‍🏫 Filtrar por profesor:", profesores_disponibles, key="filtro_profesor_calendario")
        # Persistencia: no se borra el horario base; solo cambiamos la visualización
        fig_calendario, colores_cursos = crear_calendario_interactivo(df_horario, profesor_filtro)
        st.plotly_chart(fig_calendario, use_container_width=True)
        mostrar_leyenda_cursos(colores_cursos, df_horario, profesor_filtro)
        st.info("💡 Tip: Pasa el mouse sobre los bloques para ver detalles. Usa herramientas de Plotly para zoom.")

    with tab2:
        st.subheader("📊 Horario Completo")
        st.dataframe(df_horario, use_container_width=True)
        csv = df_horario.to_csv(index=False)
        st.download_button(
            label="💾 Descargar horario (CSV)",
            data=csv,
            file_name=f"horario_{(st.session_state.programa_seleccionado or 'programa').replace(' ', '_')}.csv",
            mime="text/csv",
            key="download_csv_horario"
        )
        calendario_ui_export(df_horario)

    with tab3:
        st.subheader("👨‍🏫 Horario por Profesor")
        profesor_individual = st.selectbox("Seleccionar profesor:", sorted(df_horario["Profesor"].unique()), key="selector_profesor_individual")
        if profesor_individual:
            df_prof = df_horario[df_horario["Profesor"] == profesor_individual]
            if not df_prof.empty:
                fig_prof, _ = crear_calendario_interactivo(df_horario, profesor_individual)
                st.plotly_chart(fig_prof, use_container_width=True)
                st.dataframe(df_prof, use_container_width=True)
                creditos_total_prof = int(_creditos_unicos_por_profesor(df_prof).get(profesor_individual, 0))
                col1_prof, col2_prof, col3_prof = st.columns(3)
                with col1_prof: st.metric("📚 Total Cursos", df_prof["Curso"].nunique())
                with col2_prof: st.metric("⏰ Horas Semanales", f"{df_prof['Duración'].sum():.1f}")
                with col3_prof: st.metric("🎓 Créditos Totales", creditos_total_prof)
            else:
                st.warning(f"No se encontraron clases para {profesor_individual}")

    with tab4:
        st.subheader("🏫 Horario por Salón")
        salones_usados = df_horario["Salon"].unique()
        for salon in sorted(salones_usados):
            with st.expander(f"Horario del {salon}"):
                df_salon = df_horario[df_horario["Salon"] == salon]
                st.dataframe(df_salon, use_container_width=True)
                horas_uso = df_salon["Duración"].sum()
                st.metric("⏰ Horas de uso semanal", f"{horas_uso:.1f}h")
        st.write(f"**🏫 Salones utilizados:** {len(salones_usados)}")

    with tab5:
        st.subheader("📈 Estadísticas del Horario")
        col1_met, col2_met, col3_met, col4_met = st.columns(4)
        with col1_met: st.metric("📚 Total Clases (filas)", len(df_horario))
        with col2_met: st.metric("👨‍🏫 Profesores", df_horario["Profesor"].nunique())
        with col3_met: st.metric("🏫 Salones Usados", df_horario["Salon"].nunique())
        with col4_met: st.metric("👥 Total Estudiantes", int(df_horario["Estudiantes"].sum()))
        creditos_prof = _creditos_unicos_por_profesor(df_horario)
        fig_creditos = px.bar(x=list(creditos_prof.index), y=list(creditos_prof.values),
                              title="Créditos por Profesor (por curso único)",
                              color=list(creditos_prof.values), color_continuous_scale="viridis")
        fig_creditos.update_layout(showlegend=False)
        st.plotly_chart(fig_creditos, use_container_width=True)
        uso_salones = df_horario.groupby("Salon").size()
        fig_salones = px.pie(values=uso_salones.values, names=uso_salones.index, title="Uso de Salones")
        st.plotly_chart(fig_salones, use_container_width=True)

def _mostrar_botones_persistencia(df_horario, config):
    st.markdown("---")
    colg1, colg2, colg3 = st.columns(3)
    with colg1:
        if st.button("💾 Guardar horario", type="primary", use_container_width=True, key="btn_guardar_horario"):
            if df_horario is None or df_horario.empty:
                st.error("No hay horario para guardar.")
            else:
                ok = guardar_horario_json(df_horario, st.session_state.programa_seleccionado)
                if ok:
                    if config and config.usa_reservas and "asignaciones_actuales" in st.session_state:
                        guardar_reservas_horario(st.session_state.asignaciones_actuales, st.session_state.programa_seleccionado, config)
                    st.success("✅ Horario guardado correctamente. Se cargará automáticamente al reiniciar.")
                else:
                    st.error("❌ Error al guardar el horario.")
    with colg2:
        if st.button("🧠 Generar nuevo horario", use_container_width=True, key="btn_generar_nuevo"):
            if not os.path.exists("temp_excel.xlsx"):
                st.warning("Primero carga un archivo Excel en la barra lateral para generar un nuevo horario.")
            else:
                st.session_state.generar_nuevo = True
                st.experimental_rerun()
    with colg3:
        if st.button("🗑️ Borrar horario generado", use_container_width=True, key="btn_borrar_horario"):
            st.session_state.pop("df_horario_base", None)
            st.session_state.pop("asignaciones_actuales", None)
            st.success("🗑️ Horario eliminado. Puedes generar uno nuevo cuando desees.")

# ========================================================
# LOGIN Y RESTRICCIÓN DE ACCESO
# ========================================================
def normalizar_colegio_input(usuario_input):
    """Acepta 'Administración de Empresas' y lo mapea a 'COLEGIO DE ADMINISTRACIÓN DE EMPRESAS'."""
    if not usuario_input: return None
    u = usuario_input.strip().lower()
    for colegio_key in PROGRAMAS_RUM.keys():
        ck = colegio_key.strip().lower()
        if u == ck: return colegio_key
        # Permitir sin el prefijo 'COLEGIO DE '
        sin_prefijo = ck.replace("colegio de ", "")
        if u == sin_prefijo: return colegio_key
    return None

def validar_credenciales(usuario, contrasena):
    colegio = normalizar_colegio_input(usuario)
    if not colegio: return False, None, None
    niveles = PROGRAMAS_RUM[colegio]["niveles"]
    # Contraseña = nombre de programa en cualquier nivel (case-insensitive)
    for _, programas in niveles.items():
        for prog in programas:
            if prog.strip().lower() == contrasena.strip().lower():
                return True, colegio, prog
    return False, None, None

# ========================================================
# PÁGINA PRINCIPAL: Tabs Login + Generador restringido
# ========================================================
def mostrar_generador_horarios(config, bloques):
    colegio_info = PROGRAMAS_RUM.get(st.session_state.colegio_seleccionado)
    if colegio_info:
        st.markdown(f"""
        <div class="card" style="border-left:5px solid {colegio_info['color']};">
            <h3 style="margin:0;color:#333;">📚 {st.session_state.programa_seleccionado}</h3>
            <p style="margin:0.3rem 0;color:#666;font-size:1rem;">🏛️ {st.session_state.colegio_seleccionado}</p>
            {"<p style='margin:0.3rem 0;color:#e74c3c;font-size:0.9rem;'>🔄 <strong>Sistema de Reservas Activo</strong> - Evita conflictos con otros departamentos</p>" if colegio_info.get('sistema_reservas', False) else ""}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("## 📁 Cargar Datos para Generación de Horarios")
    # Sidebar de estado y acciones
    st.sidebar.header("⚙️ Configuración")
    st.sidebar.markdown("### 📋 Estado Actual")
    st.sidebar.success(f"**Programa:** {st.session_state.programa_seleccionado}")
    st.sidebar.info(f"🏛️ **Colegio:** {st.session_state.colegio_seleccionado}")
    if colegio_info and colegio_info.get("sistema_reservas", False):
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🔄 Sistema de Reservas")
        st.sidebar.success("✅ Activo")

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Cerrar sesión", use_container_width=True, key="btn_logout"):
        for k in ["autenticado","programa_seleccionado","colegio_seleccionado","nivel_seleccionado","pagina_actual","df_horario_base","asignaciones_actuales","generar_nuevo"]:
            st.session_state.pop(k, None)
        st.success("Sesión cerrada. Vuelve a iniciar sesión en la pestaña de Login.")
        st.experimental_rerun()

    # Upload Excel
    uploaded_file = st.sidebar.file_uploader(
        "📁 Cargar archivo Excel de profesores/cursos",
        type=["xlsx","xls"],
        help="El archivo debe contener columnas: Profesor, Curso/Materia, Créditos, Estudiantes"
    )

    if uploaded_file is not None:
        with open("temp_excel.xlsx", "wb") as f:
            f.write(uploaded_file.getbuffer())
        config.archivo_excel = "temp_excel.xlsx"
        config.colegio_actual = st.session_state.colegio_seleccionado
        config.programa_actual = st.session_state.programa_seleccionado
        config.cargar_desde_excel()
        bloques[:] = generar_bloques()

        # Infraestructura
        st.sidebar.subheader("🏫 Infraestructura")
        if st.session_state.colegio_seleccionado == "COLEGIO DE ADMINISTRACIÓN DE EMPRESAS":
            st.sidebar.info("Salones fijos (AE):")
            st.sidebar.write(", ".join(AE_SALONES_FIJOS))
            config.salones = AE_SALONES_FIJOS.copy()
        else:
            num_salones_default = colegio_info.get("salones_compartidos", 15)
            num_salones = st.sidebar.number_input("Salones totales del edificio", min_value=1, max_value=100, value=num_salones_default, step=1)
            prefijo = colegio_info.get("prefijo_salon", "SALON")
            config.salones = [f"{prefijo}-{i+1:02d}" for i in range(int(num_salones))]

        if config.profesores_config:
            st.success("✅ Archivo cargado correctamente")
            col1, col2, col3 = st.columns(3)
            with col1: st.metric("👨‍🏫 Profesores", len(config.profesores_config))
            with col2: st.metric("📚 Cursos", sum(len(p["cursos"]) for p in config.profesores_config.values()))
            with col3: st.metric("🏫 Salones Totales", len(config.salones))

            with st.expander("📋 Ver datos cargados"):
                for profesor, data in config.profesores_config.items():
                    st.write(f"**{profesor}** ({data['creditos_totales']} créditos)")
                    for curso in data["cursos"]:
                        st.write(f"  - {curso['nombre']} ({curso['creditos']} créditos, {curso['estudiantes']} estudiantes)")

            # Restricciones globales (presets simples)
            st.sidebar.subheader("🔒 Restricciones Globales")
            config.restricciones_globales["hora_inicio_min"] = st.sidebar.time_input(
                "Hora inicio mínima", datetime.strptime("07:30", "%H:%M").time()
            ).strftime("%H:%M")
            config.restricciones_globales["hora_fin_max"] = st.sidebar.time_input(
                "Hora fin máxima", datetime.strptime("19:30", "%H:%M").time()
            ).strftime("%H:%M")
            config.restricciones_globales["creditos_max_profesor"] = st.sidebar.number_input(
                "Créditos máximos por profesor", 1, 20, 15
            )
            config.restricciones_globales["estudiantes_max_salon"] = st.sidebar.number_input(
                "Estudiantes máximos por salón", 20, 150, 50
            )

            st.sidebar.subheader("🎯 Optimización")
            intentos = st.sidebar.slider("Número de iteraciones", 50, 500, 200, 50)

            # Preferencias de profesores (simple)
            st.sidebar.subheader("👤 Preferencias de Profesores")
            profesor_sel = st.sidebar.selectbox("Seleccionar profesor para configurar", ["Ninguno"] + list(config.profesores_config.keys()))
            if profesor_sel != "Ninguno":
                with st.sidebar.expander(f"Configurar {profesor_sel}"):
                    dias = ["Lu","Ma","Mi","Ju","Vi"]
                    for dia in dias:
                        col1_pref, col2_pref = st.columns(2)
                        with col1_pref:
                            inicio = st.time_input(f"{dia} inicio", key=f"pref_{profesor_sel}_{dia}_inicio")
                        with col2_pref:
                            fin = st.time_input(f"{dia} fin", key=f"pref_{profesor_sel}_{dia}_fin")
                        if inicio != datetime.strptime("00:00","%H:%M").time():
                            config.profesores_config.setdefault(profesor_sel, {}).setdefault("horario_preferido", {})
                            config.profesores_config[profesor_sel]["horario_preferido"][dia] = [(inicio.strftime("%H:%M"), fin.strftime("%H:%M"))]

            # Estado de reservas (si aplica)
            if config.usa_reservas:
                mostrar_estado_reservas(config)

            # Botón de generación (persistente)
            if st.button("🚀 Generar Horario Optimizado", type="primary", key="btn_generar_horario"):
                with st.spinner("Generando horario optimizado..."):
                    mejor, score = buscar_mejor_horario(config, bloques, horas_inicio, intentos)
                    if mejor is None:
                        st.error("❌ No se pudo generar un horario válido. Ajusta las restricciones o libera algunas reservas.")
                        if config.usa_reservas:
                            st.info("💡 Algunos salones pueden estar ocupados por otros programas. Verifica el estado de reservas.")
                    else:
                        st.success(f"✅ Horario generado. Puntuación: {score}")
                        if config.usa_reservas:
                            if guardar_reservas_horario(mejor, st.session_state.programa_seleccionado, config):
                                st.success("🔄 Reservas de salones guardadas correctamente")
                            else:
                                st.warning("⚠️ Horario generado pero hubo problemas al guardar las reservas")
                        st.session_state.asignaciones_actuales = mejor
                        st.session_state.df_horario_base = exportar_horario(mejor)

    # Mostrar horario persistente (si existe), incluso sin regenerar
    df_base = st.session_state.get("df_horario_base")
    if df_base is not None and not df_base.empty:
        _mostrar_tabs_horario(df_base)
        _mostrar_botones_persistencia(df_base, config)
    else:
        st.info("📁 Carga un Excel y genera un horario para comenzar, o carga un horario guardado.")
        df_guardado = cargar_horario_json(st.session_state.programa_seleccionado)
        if df_guardado is not None and not df_guardado.empty:
            st.success("✅ Se cargó el último horario guardado para tu programa.")
            st.session_state.df_horario_base = df_guardado
            _mostrar_tabs_horario(df_guardado)
            _mostrar_botones_persistencia(df_guardado, config)

# ========================================================
# MAIN
# ========================================================
def main():
    st.set_page_config(
        page_title="Sistema de Generación de Horarios Académicos - RUM",
        page_icon="🎓", layout="wide", initial_sidebar_state="expanded"
    )
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

    # Session state init
    for k, v in {
        "autenticado": False, "programa_seleccionado": None, "colegio_seleccionado": None,
        "nivel_seleccionado": None, "pagina_actual": "login", "generar_nuevo": False
    }.items():
        if k not in st.session_state: st.session_state[k] = v

    st.markdown('<div class="app-header"><h1>🎓 Sistema de Generación de Horarios RUM</h1><p>Recinto Universitario de Mayagüez</p><p>🔄 Sistema de Reservas de Salones</p></div>', unsafe_allow_html=True)

    # Tabs: Login + Generador
    tab_login, tab_generador = st.tabs(["🔐 Iniciar Sesión", "🗓️ Generador de Horarios"])
    with tab_login:
        st.markdown("### 🏛️ Acceso por colegio/programa")
        st.info("Usuario = nombre del colegio. Contraseña = nombre del programa académico en ese colegio.")
        usuario = st.text_input("Usuario (Colegio)", placeholder="Ej.: COLEGIO DE ADMINISTRACIÓN DE EMPRESAS o Administración de Empresas")
        contrasena = st.text_input("Contraseña (Programa)", type="password", placeholder="Ej.: Contabilidad")
        if st.button("🔑 Iniciar sesión", type="primary"):
            ok, colegio, programa = validar_credenciales(usuario, contrasena)
            if ok:
                st.session_state.autenticado = True
                st.session_state.colegio_seleccionado = colegio
                st.session_state.programa_seleccionado = programa
                st.success(f"Bienvenido: {colegio} / {programa}")
                st.experimental_rerun()
            else:
                st.error("Credenciales inválidas. Verifica colegio y programa.")

        # Ayuda visual: listar colegios y programas válidos
        with st.expander("📚 Ver colegios y programas válidos"):
            for colegio, info in PROGRAMAS_RUM.items():
                st.markdown(f"**{colegio}**")
                for nivel, programas in info["niveles"].items():
                    st.write(f"- {nivel}: {', '.join(programas)}")

    with tab_generador:
        if not st.session_state.autenticado:
            st.warning("🔒 Debes iniciar sesión en la primera pestaña para acceder al generador.")
        else:
            # Inicializar config y bloques
            if "config_obj" not in st.session_state:
                st.session_state.config_obj = ConfiguracionSistema(
                    archivo_excel=None,
                    programa_actual=st.session_state.programa_seleccionado,
                    colegio_actual=st.session_state.colegio_seleccionado
                )
            if "bloques_list" not in st.session_state:
                st.session_state.bloques_list = generar_bloques()
            mostrar_generador_horarios(st.session_state.config_obj, st.session_state.bloques_list)

if __name__ == "__main__":
    main()
