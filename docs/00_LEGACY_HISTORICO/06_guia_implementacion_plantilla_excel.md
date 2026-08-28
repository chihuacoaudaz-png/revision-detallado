# 🎨 06. Guía de Implementación Visual y Estilos de la Plantilla Excel

## 🏛️ Directrices de Diseño y Experiencia de Usuario (UI/UX)

1. **Tipografía Estándar:** `Segoe UI` o `Calibri`, tamaño 9pt para datos, 10pt para encabezados de columna (Fila 24) y 11pt negrita para categorías mayores (Fila 23).
2. **Paleta de Colores Corporativa:**
   - Encabezados Generales (Cols 1-10): Azul Petróleo (`#1F4E79`), texto blanco.
   - Sondaje y Metraje (Cols 11-22): Azul Noche (`#2F5597`), texto blanco.
   - Herramientas (Cols 24-30): Gris Oscuro (`#595959`), texto blanco.
   - Consumo de Aditivos (Cols 31-54): Verde Suave (`#548235`), texto blanco.
   - Actividades Efectivas (Col 55): Verde Brillante (`#C6EFCE`), texto verde oscuro.
   - Actividades Operativas (Cols 56-88): Azul Claro / Celeste (`#DDEBF7`).
   - Mantenimiento (Cols 86, 102-106): Salmón / Naranja Suave (`#FCE4D6`).
   - Stand By Inoperativo (Cols 89, 107-115): Amarillo Claro (`#FFF2CC`).
   - Stand By Cliente (Cols 90-101, 116-136): Naranja Claro (`#F8CBAD`).
3. **Inmovilización de Paneles (*Freeze Panes*):**
   - Inmovilizar en celda `K25` (Filas 1 a 24 y Columnas A a J visibles al desplazarse horizontal y verticalmente).
4. **Validación de Datos (Listas Desplegables):**
   - `ZONA`: `CENTRO`, `SUR`, `NORTE`
   - `TURNO`: `1`, `2`, `A`, `B`
   - `LINEA`: `NQ`, `HQ`, `BQ`, `PQ`, `HWT`
   - `ESTADO DE LA BROCA`: `NUEVA`, `USADA`, `DESCARTE`, `PULIDA`
   - `CAMBIO BROCA`: `SI`, `NO`
