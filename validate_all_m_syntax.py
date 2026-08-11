import os
import sys
import re

det_path = r"c:\Proyectos Python\Detallados\codigo_m\codigo_m_detallados.txt"
ci_path = r"c:\Proyectos Python\Detallados\codigo_m\codigo_m_control_interno.txt"
disc_path = r"c:\Proyectos Python\Detallados\codigo_m\codigo_m_matriz_discrepancias.txt"

def check_m_syntax(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()
    
    print(f"\n--- VALIDANDO SINTAXIS M: {os.path.basename(filepath)} ({len(code)} bytes) ---")
    
    # 1. Check matching brackets, parens, braces
    brackets = {"(": ")", "[": "]", "{": "}"}
    stack = []
    in_string = False
    string_char = None
    lines = code.split("\n")
    
    for l_idx, line in enumerate(lines, 1):
        i = 0
        while i < len(line):
            ch = line[i]
            # Check comment
            if not in_string and i < len(line)-1 and line[i:i+2] == "//":
                break
            if ch == '"':
                if not in_string:
                    in_string = True
                else:
                    # Check escaped double quote ""
                    if i < len(line)-1 and line[i+1] == '"':
                        i += 1
                    else:
                        in_string = False
            elif not in_string:
                if ch in "([{":
                    stack.append((ch, l_idx, i+1))
                elif ch in ")]}":
                    if not stack:
                        print(f"ERROR: Cierre de '{ch}' insesperado en línea {l_idx}:{i+1}")
                        return False
                    top_ch, top_l, top_c = stack.pop()
                    expected = brackets[top_ch]
                    if ch != expected:
                        print(f"ERROR: Se esperaba '{expected}' en línea {l_idx}:{i+1}, pero se encontró '{ch}' (Apertura en línea {top_l}:{top_c})")
                        return False
            i += 1
            
    if stack:
        top_ch, top_l, top_c = stack.pop()
        print(f"ERROR: Bloque '{top_ch}' sin cerrar abierto en línea {top_l}:{top_c}")
        return False
        
    print(f"[OK] Corchetes, llaves y paréntesis correctamente balanceados.")
    return True

check_m_syntax(det_path)
check_m_syntax(ci_path)
check_m_syntax(disc_path)
