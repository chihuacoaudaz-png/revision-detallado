"""
DESCARGA PORTABLE DE REPORTES DETALLADOS (OWA ROCKDRILL)
=========================================================
Script portable para cualquier usuario de Rockdrill Group.

MODOS DE DESTINO:
  1. Modo Estructura Base (DEFAULT):
     Coloca cada archivo Excel directamente en su carpeta oficial:
     'Estructura base/Rockdrill_Control_Operaciones/CTR_{CTR}/02_Detallado/'
     eliminando previamente el reporte anterior de esa máquina/CTR.
  2. Modo Prueba (--prueba):
     Descarga todo en una carpeta temporal 'prueba correos/' para revisión manual.

REQUISITOS PREVIOS:
  1. Tener Microsoft Edge instalado.
  2. Tener sesión de correo corporativo iniciada en Edge.
  3. Ejecutar 'python descargar_detallados.py --setup' la PRIMERA VEZ
     para registrar el perfil de sesión local.

USO:
  python descargar_detallados.py --fecha 17/08/2026            # Directo a Estructura base
  python descargar_detallados.py --fecha 17/08/2026 --prueba   # A carpeta 'prueba correos'
  python descargar_detallados.py                               # Usa fecha de hoy
  python descargar_detallados.py --setup                       # Configuración inicial

REGLAS DE NEGOCIO Y SEGURIDAD:
  1. Limpieza previa del reporte anterior en la carpeta destino de cada CTR.
  2. Exactamente 1 Reporte Detallado (.xlsx/.xlsb) por CTR.
  3. Solo archivos con patrón RD.402.P.01.F.01 / 'detallado'.
  4. Excluye F.03, F.07, PDFs, Avance Diario.
  5. Conservación de nombres originales del remitente.
  6. SOLO correos de la fecha exacta indicada (received:dd/mm/yyyy).
"""

import os
import sys
import time
import re
import shutil
import zipfile
import argparse
import json
from datetime import datetime
from pathlib import Path

import pandas as pd
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

BASE_DIR = Path(__file__).parent.resolve()
SESSIONS_DIR = BASE_DIR / ".sesiones"
CONFIG_FILE = BASE_DIR / ".descargador_config.json"
PRUEBA_DIR = BASE_DIR / "prueba correos"

try:
    from config import BASE_PATH, OUTPUT_PATH
except ImportError:
    BASE_PATH = BASE_DIR / "Estructura base" / "Rockdrill_Control_Operaciones"
    OUTPUT_PATH = BASE_DIR / "output"

AUDITORIA_DESCARGAS_DIR = OUTPUT_PATH / "auditoria_descargas"
AUDITORIA_DESCARGAS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# SELECTORES BILINGÜES (Español / Inglés)
# ============================================================
SEL_SEARCH_INPUT = "#topSearchInput, input[aria-label*='Buscar'], input[aria-label*='Search']"
SEL_CLOSE_BUTTONS = (
    "button[aria-label*='Cerrar'], button[aria-label*='Close'], "
    "i[data-icon-name='Cancel'], button[title*='Cerrar'], button[title*='Close'], "
    "button[data-automation-id='closePreview'], button[data-automation-id='backButton'], "
    "i[data-icon-name='Back']"
)
SEL_DOWNLOAD_ALL = (
    "button:has-text('Descargar todo'), span:has-text('Descargar todo'), "
    "button:has-text('Download all'), span:has-text('Download all')"
)
SEL_DOWNLOAD_SINGLE = (
    "button:has-text('Descargar'), span:has-text('Descargar'), "
    "button:has-text('Download'), span:has-text('Download'), "
    "div[role='menuitem']:has-text('Descargar'), div[role='menuitem']:has-text('Download'), "
    "i[data-icon-name='Download'], "
    "button[aria-label*='Descargar'], button[aria-label*='Download']"
)
SEL_EMAIL_ITEMS = "div[role='option']"
SEL_ATTACHMENT_LOADED = (
    "div[class*='attachment'], span[class*='attachment'], "
    "button:has-text('Descargar todo'), button:has-text('Download all'), "
    "div[aria-label*='adjunt'], div[aria-label*='attach']"
)
SEL_SEARCH_RESULTS = (
    "div[role='option'], div[data-convid], "
    "div[aria-label*='Conversación'], div[aria-label*='Conversation']"
)


# ============================================================
# CONFIGURACIÓN DE LOS 18 CTRs Y RUTAS EN ESTRUCTURA BASE
# ============================================================
def build_ctrs_config(fecha: str):
    """
    Construye la configuración de los 18 CTRs canónicos con sus carpetas
    en 'Estructura base/Rockdrill_Control_Operaciones/' y queries estrictas de fecha.
    """
    return [
        {"ctr": "AMERICANA",       "aliases": ["americana"],                 "folder": "CTR_AMERICANA",       "queries": [f"AMERICANA received:{fecha}"]},
        {"ctr": "ANDAYCHAGUA",     "aliases": ["andaychagua"],               "folder": "CTR_ANDAYCHAGUA",     "queries": [f"ANDAYCHAGUA received:{fecha}"]},
        {"ctr": "CATALINA_HUANCA", "aliases": ["catalina", "huanca"],        "folder": "CTR_CATALINA_HUANCA", "queries": [f"CATALINA HUANCA received:{fecha}"]},
        {"ctr": "CERRO",           "aliases": ["cerro"],                     "folder": "CTR_CERRO",           "queries": [f"CERRO received:{fecha}"]},
        {"ctr": "CHUNGAR",         "aliases": ["chungar"],                   "folder": "CTR_CHUNGAR",         "queries": [f"CHUNGAR received:{fecha}"]},
        {"ctr": "COBRIZA",         "aliases": ["cobriza"],                   "folder": "CTR_COBRIZA",         "queries": [f"COBRIZA received:{fecha}"]},
        {"ctr": "COLQUISIRI",      "aliases": ["colquisiri", "colquijirca"], "folder": "CTR_COLQUISIRI",      "queries": [f"COLQUISIRI received:{fecha}", f"COLQUIJIRCA received:{fecha}"]},
        {"ctr": "CONDESTABLE",     "aliases": ["condestable"],               "folder": "CTR_CONDESTABLE",     "queries": [f"CONDESTABLE received:{fecha}"]},
        {"ctr": "CUCULI",          "aliases": ["cuculi"],                    "folder": "CTR_CUCULI",          "queries": [f"CUCULI received:{fecha}"]},
        {"ctr": "INMACULADA",      "aliases": ["inmaculada"],                "folder": "CTR_INMACULADA",      "queries": [f"INMACULADA received:{fecha}"]},
        {"ctr": "LA_ESTRELLA",     "aliases": ["estrella"],                  "folder": "CTR_LA_ESTRELLA",     "queries": [f"ESTRELLA received:{fecha}", f"LA ESTRELLA received:{fecha}"]},
        {"ctr": "MOROCOCHA",       "aliases": ["morococha"],                 "folder": "CTR_MOROCOCHA",       "queries": [f"MOROCOCHA received:{fecha}"]},
        {"ctr": "RAURA",           "aliases": ["raura"],                     "folder": "CTR_RAURA",           "queries": [f"RAURA received:{fecha}"]},
        {"ctr": "SAN_CRISTOBAL",   "aliases": ["san cristobal", "cristobal"],"folder": "CTR_SAN_CRISTOBAL",   "queries": [f"SAN CRISTOBAL received:{fecha}"]},
        {"ctr": "TAMBOJASA",       "aliases": ["tambojasa"],                 "folder": "CTR_TAMBOJASA",       "queries": [f"TAMBOJASA received:{fecha}"]},
        {"ctr": "TICLIO",          "aliases": ["ticlio"],                    "folder": "CTR_TICLIO",          "queries": [f"TICLIO received:{fecha}"]},
        {"ctr": "YAULIYACU",       "aliases": ["yauliyacu"],                "folder": "CTR_YAULIYACU",       "queries": [f"YAULIYACU received:{fecha}"]},
        {"ctr": "YAURICOCHA",      "aliases": ["yauricocha"],               "folder": "CTR_YAURICOCHA",      "queries": [f"YAURICOCHA received:{fecha}"]},
    ]


# ============================================================
# GESTIÓN DE SESIONES POR USUARIO (Portable)
# ============================================================
def obtener_session_dir(nombre_usuario=None):
    if nombre_usuario:
        user_dir = SESSIONS_DIR / nombre_usuario.lower().replace(" ", "_")
    else:
        config = cargar_config()
        if config and "usuario" in config:
            user_dir = SESSIONS_DIR / config["usuario"]
        else:
            print("ERROR: No hay usuario configurado.", flush=True)
            print("Ejecute primero: python descargar_detallados.py --setup", flush=True)
            sys.exit(1)
    
    user_dir.mkdir(parents=True, exist_ok=True)
    return str(user_dir)


def cargar_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return None


def guardar_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def ejecutar_setup():
    print("=" * 70, flush=True)
    print("  CONFIGURACIÓN INICIAL DEL DESCARGADOR DE DETALLADOS", flush=True)
    print("=" * 70, flush=True)
    nombre = input("Ingresa tu nombre o usuario (ej: cesar.contreras): ").strip()
    if not nombre:
        print("ERROR: Nombre requerido.", flush=True)
        sys.exit(1)
    
    nombre_safe = nombre.lower().replace(" ", "_")
    session_dir = SESSIONS_DIR / nombre_safe
    session_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nPerfil de sesión: {session_dir}")
    print("Se abrirá Microsoft Edge. Inicia sesión con tu correo corporativo.")
    input("Presiona ENTER para abrir Edge...")
    
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(session_dir),
            channel="msedge",
            headless=False,
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://outlook.office.com/mail/", wait_until="domcontentloaded")
        print("\n[ESPERANDO] Inicia sesión en OWA y luego cierra Edge...", flush=True)
        try:
            page.wait_for_event("close", timeout=300000)
        except Exception:
            pass
        try:
            context.close()
        except Exception:
            pass
    
    config = {
        "usuario": nombre_safe,
        "nombre_display": nombre,
        "fecha_setup": datetime.now().isoformat(),
        "session_dir": str(session_dir)
    }
    guardar_config(config)
    print(f"\n✅ Perfil guardado: {nombre}. Listo para descargar reportes.\n")


# ============================================================
# FILTRADO Y VALIDACIÓN DE NEGOCIO
# ============================================================
def es_detallado_para_ctr(nombre_archivo: str, aliases: list) -> bool:
    """Valida que sea estrictamente un Reporte Detallado RD.402.P.01.F.01 del CTR."""
    n = nombre_archivo.lower()
    if not any(n.endswith(ext) for ext in [".xlsx", ".xlsb", ".xls"]):
        return False
    # Excluir reportes cortos o F.03 / F.07 / CDA
    if "f.03" in n or "f03" in n or "f 03" in n or "f.07" in n or "f07" in n or "cda" in n or "corto" in n:
        return False
    # Validar alias del CTR
    if not any(alias in n for alias in aliases):
        return False
    # Confirmar que sea F.01 o Detallado
    if "detallado" in n or "f.01" in n or "f01" in n or "f 01" in n:
        return True
    return False


def limpiar_detallado_previo_ctr(target_dir: Path):
    """Limpia reportes detallados anteriores en la carpeta 02_Detallado de un CTR."""
    if target_dir.exists():
        for f in target_dir.glob("*.xls*"):
            try:
                f.unlink()
            except Exception as e:
                print(f"    [WARN] No se pudo borrar archivo previo {f.name}: {e}", flush=True)
    else:
        target_dir.mkdir(parents=True, exist_ok=True)


# ============================================================
# ACCIONES DOM OWA
# ============================================================
def esperar_resultados_busqueda(page, timeout_ms=5000):
    try:
        page.wait_for_selector(SEL_SEARCH_RESULTS, timeout=timeout_ms)
        time.sleep(0.5)
    except PlaywrightTimeout:
        time.sleep(0.5)


def esperar_correo_abierto(page, timeout_ms=4000):
    try:
        page.wait_for_selector(SEL_ATTACHMENT_LOADED, timeout=timeout_ms)
        time.sleep(0.3)
    except PlaywrightTimeout:
        time.sleep(0.5)


def cerrar_dialogos_abiertos(page):
    for _ in range(3):
        try:
            page.keyboard.press("Escape")
            time.sleep(0.15)
        except Exception:
            pass
    try:
        btns = page.locator(SEL_CLOSE_BUTTONS).all()
        for b in btns:
            if b.is_visible():
                b.click(timeout=400, force=True)
                time.sleep(0.15)
    except Exception:
        pass


def buscar_en_owa(page, query: str):
    cerrar_dialogos_abiertos(page)
    s = page.locator(SEL_SEARCH_INPUT).first
    try:
        s.wait_for(state="visible", timeout=2500)
        s.click(timeout=2500, force=True)
    except Exception:
        cerrar_dialogos_abiertos(page)
        try:
            s = page.locator(SEL_SEARCH_INPUT).first
            s.wait_for(state="visible", timeout=2500)
            s.click(timeout=2500, force=True)
        except Exception:
            try:
                page.keyboard.press("Escape")
                time.sleep(0.3)
                page.keyboard.press("Escape")
            except Exception:
                pass
            s = page.locator(SEL_SEARCH_INPUT).first
            s.wait_for(state="visible", timeout=5000)
            s.click(timeout=3000, force=True)

    s.press("Control+a")
    s.fill(query)
    page.keyboard.press("Enter")
    esperar_resultados_busqueda(page)


def descargar_via_zip(page, aliases: list, target_dir: Path, timeout_dl=8000) -> str:
    btn_todo = page.locator(SEL_DOWNLOAD_ALL).first
    if btn_todo.count() == 0 or not btn_todo.is_visible():
        return None

    try:
        print(f"    Usando 'Descargar todo / Download all'...", flush=True)
        with page.expect_download(timeout=timeout_dl) as d_info:
            btn_todo.click(timeout=2000, force=True)
        dl = d_info.value
        temp_path = target_dir / dl.suggested_filename
        dl.save_as(str(temp_path))

        if temp_path.name.lower().endswith(".zip"):
            limpiar_detallado_previo_ctr(target_dir)
            archivo_final = None
            with zipfile.ZipFile(str(temp_path), 'r') as z:
                for zname in z.namelist():
                    if es_detallado_para_ctr(zname, aliases):
                        dest_file = target_dir / Path(zname).name
                        with z.open(zname) as source, open(dest_file, "wb") as target:
                            shutil.copyfileobj(source, target)
                        archivo_final = dest_file.name
                        print(f"      [EXTRAIDO DE ZIP!] {archivo_final}", flush=True)
            try:
                temp_path.unlink()
            except Exception:
                pass
            return archivo_final
        elif es_detallado_para_ctr(dl.suggested_filename, aliases):
            limpiar_detallado_previo_ctr(target_dir)
            print(f"      [DESCARGADO!] {dl.suggested_filename}", flush=True)
            return dl.suggested_filename
    except Exception:
        pass
    return None


def descargar_adjunto_individual(page, aliases: list, target_dir: Path, timeout_dl=10000) -> str:
    elements = page.locator("button, div[role='button'], div, span, a").filter(
        has_text=re.compile(r'\.(xlsx|xlsb|xls)', re.IGNORECASE)
    ).all()

    for el in elements:
        try:
            if not el.is_visible():
                continue
            txt = el.get_attribute("aria-label") or el.get_attribute("title") or el.inner_text()
            if not txt or len(txt) > 250:
                continue
            match = re.search(r'([^\r\n/\\]+\.(xlsx|xlsb|xls))', txt, re.IGNORECASE)
            if not match:
                continue
            nom_archivo = match.group(1).strip()
            if not es_detallado_para_ctr(nom_archivo, aliases):
                continue

            # Intento 1: Hover y clic en chevron o clic derecho para abrir menú de descarga
            try:
                el.hover(timeout=1000)
                time.sleep(0.3)
                # Buscar botón de menú contextual / chevron dentro de la tarjeta
                chevron = el.locator("button[aria-label*='Más'], button[aria-label*='More'], button[aria-label*='Opciones'], i[data-icon-name='ChevronDown'], button").last
                if chevron.count() > 0 and chevron.is_visible():
                    chevron.click(timeout=1000, force=True)
                else:
                    el.click(button="right", timeout=1000, force=True)
                time.sleep(0.5)
                
                btn_down = page.locator(SEL_DOWNLOAD_SINGLE).first
                if btn_down.count() > 0 and btn_down.is_visible():
                    with page.expect_download(timeout=timeout_dl) as d_info:
                        btn_down.click(timeout=2000, force=True)
                    dl = d_info.value
                    if es_detallado_para_ctr(dl.suggested_filename, aliases):
                        limpiar_detallado_previo_ctr(target_dir)
                        dest = target_dir / dl.suggested_filename
                        dl.save_as(str(dest))
                        sz = dest.stat().st_size
                        print(f"      [DESCARGADO DE MENÚ!] {dl.suggested_filename} ({sz:,} bytes)", flush=True)
                        cerrar_dialogos_abiertos(page)
                        return dl.suggested_filename
            except Exception:
                pass

            # Intento 2: Clic directo con expect_download
            try:
                with page.expect_download(timeout=3000) as d_info:
                    el.click(timeout=1500, force=True)
                dl = d_info.value
                if es_detallado_para_ctr(dl.suggested_filename, aliases):
                    limpiar_detallado_previo_ctr(target_dir)
                    dest = target_dir / dl.suggested_filename
                    dl.save_as(str(dest))
                    sz = dest.stat().st_size
                    print(f"      [DESCARGADO DIRECTO!] {dl.suggested_filename} ({sz:,} bytes)", flush=True)
                    cerrar_dialogos_abiertos(page)
                    return dl.suggested_filename
            except Exception:
                pass

            # Intento 3: Si abrió visor online, buscar botón 'Descargar' en barra superior
            try:
                time.sleep(1.0)
                btn_preview_down = page.locator("button:has-text('Descargar'), button:has-text('Download'), button[aria-label*='Descargar']").first
                if btn_preview_down.count() > 0 and btn_preview_down.is_visible():
                    with page.expect_download(timeout=timeout_dl) as d_info:
                        btn_preview_down.click(timeout=2000, force=True)
                    dl = d_info.value
                    if es_detallado_para_ctr(dl.suggested_filename, aliases):
                        limpiar_detallado_previo_ctr(target_dir)
                        dest = target_dir / dl.suggested_filename
                        dl.save_as(str(dest))
                        sz = dest.stat().st_size
                        print(f"      [DESCARGADO DE VISOR!] {dl.suggested_filename} ({sz:,} bytes)", flush=True)
                        cerrar_dialogos_abiertos(page)
                        return dl.suggested_filename
            except Exception:
                pass
        except Exception:
            pass
    return None


# ============================================================
# EJECUCIÓN PRINCIPAL
# ============================================================
def ejecutar(fecha_objetivo: str, session_dir: str, modo_prueba: bool = False):
    t_inicio_total = time.time()
    ctrs_config = build_ctrs_config(fecha_objetivo)
    config = cargar_config()
    usuario = config.get("nombre_display", "desconocido") if config else "desconocido"

    print("=" * 85, flush=True)
    print("  DESCARGADOR AUTOMATIZADO DE DETALLADOS ROCKDRILL", flush=True)
    print(f"  Fecha objetivo:    {fecha_objetivo} (Perforación del día anterior)", flush=True)
    print(f"  Modo de destino:   {'CARPETA PRUEBA' if modo_prueba else 'ESTRUCTURA BASE DIRECTA'}", flush=True)
    print(f"  Ruta base datos:   {BASE_PATH}", flush=True)
    print(f"  Usuario activo:    {usuario}", flush=True)
    print(f"  Inicio:            {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
    print("=" * 85, flush=True)

    if modo_prueba:
        PRUEBA_DIR.mkdir(parents=True, exist_ok=True)
        for item in PRUEBA_DIR.iterdir():
            try:
                if item.is_file(): item.unlink()
                elif item.is_dir(): shutil.rmtree(item)
            except Exception: pass

    resultados_finales = []
    tiempos_por_ctr = []

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=session_dir,
            channel="msedge",
            headless=False,
            accept_downloads=True,
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
        )

        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://outlook.office.com/mail/", wait_until="domcontentloaded")
        page.wait_for_selector(SEL_SEARCH_INPUT, timeout=35000)
        time.sleep(1)

        for i, cfg in enumerate(ctrs_config):
            ctr = cfg["ctr"]
            aliases = cfg["aliases"]
            folder = cfg["folder"]
            queries = cfg["queries"]
            archivo_descargado = None
            t_inicio_ctr = time.time()

            if modo_prueba:
                target_dir = PRUEBA_DIR
            else:
                target_dir = BASE_PATH / folder / "02_Detallado"
                target_dir.mkdir(parents=True, exist_ok=True)

            print(f"\n{'─'*65}", flush=True)
            print(f"[{i+1}/{len(ctrs_config)}] CTR: {ctr} -> Destino: {target_dir.name}/", flush=True)
            print(f"{'─'*65}", flush=True)

            for query in queries:
                if archivo_descargado:
                    break

                print(f"  Buscando: '{query}'...", flush=True)
                buscar_en_owa(page, query)

                correos = page.locator(SEL_EMAIL_ITEMS).all()
                print(f"  Resultados: {len(correos)} correos.", flush=True)

                if len(correos) == 0:
                    continue

                for idx in range(min(len(correos), 5)):
                    try:
                        correos_act = page.locator(SEL_EMAIL_ITEMS).all()
                        if idx >= len(correos_act):
                            break
                        c = correos_act[idx]
                        try:
                            c_txt = re.sub(r'[^\x00-\x7f]', '', c.inner_text().replace('\n', ' '))
                            print(f"  -> Correo #{idx+1}: {c_txt[:65]}...", flush=True)
                        except Exception:
                            pass

                        try:
                            c.click(timeout=3000, force=True, no_wait_after=True)
                        except Exception:
                            try:
                                c.click(timeout=3000, force=True)
                            except Exception:
                                pass

                        esperar_correo_abierto(page)

                        # Estrategia 1: Descargar todo (ZIP)
                        archivo_descargado = descargar_via_zip(page, aliases, target_dir)

                        # Estrategia 2: Adjunto individual
                        if not archivo_descargado:
                            archivo_descargado = descargar_adjunto_individual(page, aliases, target_dir)

                        if archivo_descargado:
                            break
                    except Exception as e_item:
                        print(f"    [WARN] Error evaluando correo #{idx+1}: {e_item}", flush=True)

            t_ctr = time.time() - t_inicio_ctr

            if archivo_descargado:
                saved_file = target_dir / archivo_descargado
                sz = saved_file.stat().st_size if saved_file.exists() else 0
                print(f"  >>> [OK] '{archivo_descargado}' ({sz:,} bytes) en {target_dir.parent.name}/{target_dir.name} [{t_ctr:.1f}s]", flush=True)
                resultados_finales.append({
                    "CTR": ctr,
                    "Estado": "DESCARGADO",
                    "Archivo": archivo_descargado,
                    "Ruta_Destino": str(saved_file),
                    "Bytes": sz
                })
            else:
                print(f"  *** [NO ENCONTRADO para {fecha_objetivo}] [{t_ctr:.1f}s] ***", flush=True)
                resultados_finales.append({
                    "CTR": ctr,
                    "Estado": "FALTANTE",
                    "Archivo": f"NO ENCONTRADO ({fecha_objetivo})",
                    "Ruta_Destino": "-",
                    "Bytes": 0
                })

            tiempos_por_ctr.append({"CTR": ctr, "Tiempo_seg": round(t_ctr, 1)})

        context.close()

    # Guardar reporte de auditoría
    fecha_safe = fecha_objetivo.replace('/', '_')
    df = pd.DataFrame(resultados_finales)
    excel_map = AUDITORIA_DESCARGAS_DIR / f"_MAPEO_DESCARGAS_{fecha_safe}.xlsx"
    df.to_excel(str(excel_map), index=False)

    t_total = time.time() - t_inicio_total

    print("\n" + "=" * 90, flush=True)
    print(f"RESUMEN FINAL DE DESCARGAS - {fecha_objetivo}", flush=True)
    print(f"Tiempo total: {t_total/60:.1f} min ({t_total:.0f}s)", flush=True)
    print("=" * 90, flush=True)

    ok_count = sum(1 for r in resultados_finales if r["Estado"] == "DESCARGADO")
    fail_count = len(resultados_finales) - ok_count

    for r, t in zip(resultados_finales, tiempos_por_ctr):
        st = "OK" if r["Estado"] == "DESCARGADO" else "FALTANTE"
        print(f"  [{st:<8}] {r['CTR']:<17}: {r['Archivo'][:60]:<60} ({r['Bytes']:>10,} B) [{t['Tiempo_seg']:>5.1f}s]", flush=True)

    print(f"\n  Descargados: {ok_count}/{len(ctrs_config)} | Faltantes: {fail_count}", flush=True)
    print(f"  Auditoría guardada en: {excel_map}", flush=True)

    df_times = pd.DataFrame(tiempos_por_ctr)
    df_times.loc[len(df_times)] = {"CTR": "TOTAL", "Tiempo_seg": round(t_total, 1)}
    times_path = AUDITORIA_DESCARGAS_DIR / f"_TIEMPOS_{fecha_safe}.xlsx"
    df_times.to_excel(str(times_path), index=False)


# ============================================================
# CLI INTERACTION
# ============================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Descarga de Reportes Detallados OWA directamente a Estructura base",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--setup", action="store_true", help="Configuración inicial del perfil de usuario")
    parser.add_argument("--fecha", type=str, default=None, help="Fecha de recepción dd/mm/yyyy (default: hoy)")
    parser.add_argument("--usuario", type=str, default=None, help="Nombre del perfil de usuario")
    parser.add_argument("--prueba", action="store_true", help="Descargar a 'prueba correos' en vez de Estructura base")

    args = parser.parse_args()

    if args.setup:
        ejecutar_setup()
        sys.exit(0)

    fecha = args.fecha or datetime.now().strftime("%d/%m/%Y")
    try:
        datetime.strptime(fecha, "%d/%m/%Y")
    except ValueError:
        print(f"ERROR: Formato de fecha inválido: '{fecha}'. Use dd/mm/yyyy", flush=True)
        sys.exit(1)

    session_dir = None
    if args.usuario:
        session_dir = obtener_session_dir(args.usuario)
    else:
        config = cargar_config()
        if config and "usuario" in config:
            session_dir = obtener_session_dir(config["usuario"])
        else:
            legacy = BASE_DIR / ".edge_session"
            if legacy.exists():
                session_dir = str(legacy)
            else:
                print("ERROR: No hay perfil configurado. Ejecute: python descargar_detallados.py --setup")
                sys.exit(1)

    ejecutar(fecha, session_dir, modo_prueba=args.prueba)
