"""
Script de Versionamiento y Commit Integral usando Dulwich (Pure Python Git)
Garantiza la inclusión de TODO el proyecto, contexto y documentación sin omisiones.
"""
import os
import sys
from pathlib import Path
from dulwich import porcelain
from dulwich.repo import Repo

# Forzar UTF-8
if sys.stdout.encoding != 'utf-8':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass

def commit_todo_el_proyecto():
    repo_path = Path(".").resolve()
    print("=" * 80)
    print("🚀 INICIANDO VERSIONAMIENTO INTEGRAL CON DULWICH (GIT)")
    print(f"📁 Directorio: {repo_path}")
    print("=" * 80)

    try:
        repo = Repo(str(repo_path))
    except Exception:
        repo = Repo.init(str(repo_path))

    # 1. Agregar todos los archivos
    print("📦 Indexando y agregando todos los archivos del proyecto...")
    porcelain.add(repo, paths=["."])

    # 2. Realizar Commit
    mensaje = b"feat(bi-core): Full production pipeline, Power Query M live queries, 1-to-1 reconciliation, Common Sense QA Auditor and complete conversation logs"
    author = b"Rockdrill BI Lead <bi@rockdrillgroup.com>"
    
    commit_sha = porcelain.commit(repo, message=mensaje, author=author, committer=author)
    print(f"✅ Commit realizado con exito! SHA: {commit_sha.decode('utf-8') if isinstance(commit_sha, bytes) else commit_sha}")
    
    # 3. Mostrar status
    status = porcelain.status(repo)
    print(f"📊 Archivos staged pendientes: {len(status.staged)}")
    print(f"📊 Archivos no rastreados: {len(status.untracked)}")
    print("=" * 80)

if __name__ == "__main__":
    commit_todo_el_proyecto()
