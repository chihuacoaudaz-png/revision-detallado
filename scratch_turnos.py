import pandas as pd

def normalize_turno_val(val: any) -> str:
    s = str(val or "").strip().upper()
    if s in ("1", "1.0", "1,0", "A", "D", "DIA", "G1"): return "A"
    if s in ("2", "2.0", "2,0", "B", "N", "NOCHE", "G2"): return "B"
    if s in ("3", "3.0", "3,0", "C", "G3"): return "C"
    return s

def assign_daily_turnos_fast(grupos_list: list, turnos_list: list, perfs_list: list) -> list:
    n = len(turnos_list)
    if n == 0: return []

    raw_turnos = [normalize_turno_val(t) for t in turnos_list]
    raw_grupos = [str(g).strip().replace(".0", "") if pd.notna(g) and str(g).strip() not in ("", "nan", "None", "0.0", "0") else "" for g in grupos_list]
    raw_perfs = [str(p or "").strip().upper() if str(p or "").strip().upper() not in ("FALSO", "0.0", "NAN", "NONE", "0") else "" for p in perfs_list]

    for i in range(1, n):
        if not raw_turnos[i]: raw_turnos[i] = raw_turnos[i-1]
        if not raw_grupos[i]: raw_grupos[i] = raw_grupos[i-1]
        if not raw_perfs[i]: raw_perfs[i] = raw_perfs[i-1]

    # If we have fully populated explicitly 'A' and 'B' in raw_turnos after ffill, we should just use them.
    # What if they are all 'A'? That means the user only filled 'A'. We might still need to infer 'B'.
    # So if there's both 'A' and 'B', return raw_turnos.
    if "A" in raw_turnos and "B" in raw_turnos:
        # Check if they are valid
        valid = True
        for t in raw_turnos:
            if t not in ("A", "B"):
                valid = False
        if valid:
            return raw_turnos
            
    # Fallback to group transition
    if any(g != "" for g in raw_grupos):
        g0 = next((g for g in raw_grupos if g != ""), "")
        if g0 != "":
            for i in range(1, n):
                gi = raw_grupos[i]
                if gi != "" and gi != g0:
                    return ["A" if idx < i else "B" for idx in range(n)]

    # Reparto secuencial
    split = max(1, n // 2)
    return ["A" if i < split else "B" for i in range(n)]

print(assign_daily_turnos_fast(["", "", ""], ["1", "", "2"], ["", "", ""]))
print(assign_daily_turnos_fast(["G1", "", "G2"], ["", "", ""], ["", "", ""]))
