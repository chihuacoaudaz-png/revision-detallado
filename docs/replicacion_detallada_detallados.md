# Manual Técnico Extremadamente Detallado para la Replicación del ETL de Reportes Detallados

Este documento constituye una guía técnica paso a paso para replicar desde cero el proceso de extracción, limpieza, estandarización y consolidación de los **Reportes Detallados por Equipo** (`RD.402.P.01.F.01`) en cualquier plataforma o lenguaje de programación (Python, SQL, R, C#, Rust, Spark, etc.).

---

## 1. Diagrama de Flujo del Proceso

```
[Inicio: Carpeta Estructura base]
       │
       ▼
[Filtro 1: Escanear subcarpetas CTR_*/02_Detallado/*.xlsx]
       │
       ├─► ¿Es CTR COLQUIJIRCA? ──► SÍ ──► [Omitir / Excluir de Negocio]
       │
       ▼ NO
[Filtro 2: Pestañas Operativas] ──► Excluir 'ADITIVOS', 'GENERAL', 'LISTAS', 'Tiempos', etc.
       │
       ▼
[Lectura Segura con Calamine/C-Parser]
       │
       ▼
[Truncar Filas: Tomar primeras 200 filas por hoja]
       │
       ▼
[Extracción Dual-Row de Encabezados: Fila 23 (index 22) + Fila 24 (index 23)]
       │
       ├─► Forward-Fill Horizontal en Fila 23
       ├─► Concatenar: PRIMARIO_SUB
       └─► Deduplicar nombres de columnas
       │
       ▼
[Extracción de Datos: Desde Fila 25 (index 24)]
       │
       ├─► Reemplazar cadenas vacías "" por NULL
       ├─► REGLA CRÍTICA: Forward-fill de FECHA a nivel de hoja
       └─► Filtrar filas donde SONDAJE (Columna 2) sea NULL
       │
       ▼
[Normalización de Campos y Mapeo M de 53 Columnas]
       │
       ▼
[Estandarización de Máquinas mediante Maestros SAP]
       │
       ▼
[Estandarización de Turno a 'A' (Día) y 'B' (Noche)]
       │
       ▼
[Generación de ID_CLAVE_UNICA = {FECHA}|{CTR}|{MAQUINA}|{TURNO_ESTANDAR}]
       │
       ▼
[Limpieza Numérica Profunda: clean_number_value()]
       │
       ▼
[Exportación Consolidada: detallados_consolidados.xlsx / csv]
```

---

## 2. Pseudocódigo Detallado del Algoritmo (Paso a Paso)

### Paso 2.1. Escaneo de Archivos e Inspección de Estructura
```python
función ObtenerArchivosDetallados(ruta_base):
    archivos_validos = []
    para cada carpeta_ctr en listar_directorios(ruta_base):
        si no carpeta_ctr.comienza_con("CTR_"):
            continuar
        
        nombre_ctr = LimpiarTexto(carpeta_ctr.reemplazar("CTR_", ""))
        
        # Criterio de Exclusión de Negocio
        si nombre_ctr == "COLQUIJIRCA":
            continuar  # Excluir explícitamente
            
        carpeta_busqueda = carpeta_ctr + "/02_Detallado" si existe sino carpeta_ctr
        
        para cada archivo en buscar_excel(carpeta_busqueda):
            si no archivo.comienza_con("~$"):
                archivos_validos.agregar({ctr: nombre_ctr, ruta: archivo})
                
    retornar archivos_validos
```

---

### Paso 2.2. Algoritmo de Extracción Dual-Row de Encabezados
```python
función ConstruirEncabezadosDualRow(filas_hoja, skip=22):
    row_primary_idx = 22  # Fila 23 de Excel
    row_sub_idx = 23      # Fila 24 de Excel
    
    si longitud(filas_hoja) < row_sub_idx + 1:
        retornar NULO
        
    primarios_raw = filas_hoja[row_primary_idx]
    secundarios_raw = filas_hoja[row_sub_idx]
    
    # 1. Forward-fill horizontal en primarios
    primarios_llenados = []
    ultimo_valor = "XP"
    para cada val en primarios_raw:
        txt = Limpiar(val)
        si txt no es vacío:
            primarios_llenados.agregar(txt)
            ultimo_valor = txt
        sino:
            primarios_llenados.agregar(ultimo_valor)
            
    # 2. Combinación Primario_Sub
    encabezados = []
    para i desde 0 hasta longitud(primarios_llenados) - 1:
        p = primarios_llenados[i]
        s = Limpiar(secundarios_raw[i])
        
        si p == "XP":
            encabezados.agregar(s si s no es vacío sino "XP_" + i)
        si s == "":
            encabezados.agregar(p)
        sino:
            encabezados.agregar(p + "_" + s)
            
    # 3. Deduplicación
    contadores = {}
    unicos = []
    para cada h en encabezados:
        si h está en contadores:
            contadores[h] += 1
            unicos.agregar(h + "_" + contadores[h])
        sino:
            contadores[h] = 0
            unicos.agregar(h)
            
    retornar unicos
```

---

### Paso 2.3. Algoritmo de Limpieza Numérica Profunda (`clean_number_value`)
```python
función LimpiarValorNumerico(val):
    si val es NULO:
        retornar NULO
        
    si val es de tipo (Lista, Serie, Arreglo):
        para cada elemento en val:
            res = LimpiarValorNumerico(elemento)
            si res no es NULO:
                retornar res
        retornar NULO
        
    si val es (Entero o Flotante):
        retornar int(val) si val.es_entero() sino float(val)
        
    texto = String(val).trim()
    texto = RemoverRegex(texto, "^['\"`´’‘]+|['\"`´’‘]+$")  # Quitar comillas/tildes inicio y fin
    texto = texto.reemplazar("\xa0", "").trim()
    
    si texto en ("", "nan", "null", "none", "falso", "verdadero", "-"):
        retornar NULO
        
    texto = texto.reemplazar(",", ".")  # Normalizar decimales
    
    intentar:
        f = float(texto)
        retornar int(f) si f.es_entero() sino f
    excepcion:
        match = BuscarRegex(texto, "[-+]?\d*\.?\d+")
        si match existe:
            f = float(match.valor)
            retornar int(f) si f.es_entero() sino f
        retornar NULO
```

---

### Paso 2.4. Algoritmo de Estandarización de Turno y Clave Única
```python
función EstandarizarTurnoYClave(df_consolidado):
    contador_secuencia = {}
    turnos_estandar = []
    claves_unicas = []
    
    para cada fila en df_consolidado:
        fecha_str = FormatoFecha(fila["FECHA"], "YYYY-MM-DD")
        ctr_str = TextoMayuscula(fila["CTR"])
        maq_str = TextoMayuscula(fila["MAQUINA"])
        
        clave_conteo = (fecha_str, ctr_str, maq_str)
        contador_secuencia[clave_conteo] = contador_secuencia.obtener(clave_conteo, 0) + 1
        secuencia = contador_secuencia[clave_conteo]
        
        # Reglas de estandarización
        raw_turno = TextoMayuscula(fila["TURNO (A=1;B=2)"])
        raw_grupo = TextoMayuscula(fila["GRUPO"])
        
        si raw_turno en ("1", "1.0", "A", "D", "DIA", "G1") o raw_grupo en ("1", "1.0"):
            t_std = "A"
        sino si raw_turno en ("2", "2.0", "B", "N", "NOCHE", "G2") o raw_grupo en ("2", "2.0"):
            t_std = "B"
        sino si raw_turno == "B" y raw_grupo en ("1", "1.0"):
            t_std = "A"
        sino si raw_turno == "C" y raw_grupo en ("2", "2.0"):
            t_std = "B"
        sino:
            t_std = "A" si secuencia == 1 sino "B"
            
        clave_unica = fecha_str + "|" + ctr_str + "|" + maq_str + "|" + t_std
        
        turnos_estandar.agregar(t_std)
        claves_unicas.agregar(clave_unica)
        
    df_consolidado["TURNO_ESTANDAR"] = turnos_estandar
    df_consolidado["ID_CLAVE_UNICA"] = claves_unicas
    retornar df_consolidado
```

---

## 3. Matriz de Mapeo de Máquinas Excepcionales (SAP Master)

Para garantizar la integridad al cruzar datos de distintos supervisores, aplique la siguiente tabla de traducción de alias de hoja a código oficial SAP:

| CTR | Nombre Pestaña Excel | Código Oficial SAP |
|---|---|---|
| `ANDAYCHAGUA` | `XRD90U-017` | `XRD150U-001` |
| `CATALINA HUANCA` | `XRD50-003` | `XRD50U-003` |
| `CATALINA HUANCA` | `XRD100U-01` | `XRD100U-001` |
| `CHUNGAR` | `XRD90U-003` | `XRD90U-021` |
| `INMACULADA` | `XRD80U-008` | `XRD80USS-008` |
| `INMACULADA` | `XRD250-001` | `XRD250U-001` |
| `INMACULADA` | `XRD90U-012 (XRD150)` | `XRD90U-012` |
| `MOROCOCHA` | `XRD150USS` | `XRD150USS-002` |
| `MOROCOCHA` | `XRD90USS-002` | `XRD90USS-005` |
| `TAMBOJASA` | `DE710ST-002` | `DE710T-002` |
| `YAULIYACU` | `XRD50USS-001` | `XDR50USS-00T` |

---

## 4. Validaciones Post-Procesamiento (Criterios de Calidad)

1. **Conteo de Filas Esperado**: El total de filas consolidadas debe ser exactamente **2,716 filas** para los 18 CTRs procesados (excluyendo Colquijirca).
2. **Cero Nulos en FECHA**: Ninguna fila consolidada debe contener `FECHA` nula.
3. **Unicidad de Claves por Turno**: Se deben obtener exactamente **2,452 claves únicas de turno** en la consolidación de Detallados.
