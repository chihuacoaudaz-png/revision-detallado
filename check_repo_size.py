"""
Verificar tamaño de archivos en la carpeta de proyectos
"""
from pathlib import Path

root = Path(r"c:\Proyectos Python\Detallados")
large_files = []

for f in root.glob("**/*"):
    if f.is_file() and not str(f).startswith(str(root / ".git")) and not str(f).startswith(str(root / "tools")):
        size_mb = f.stat().st_size / (1024 * 1024)
        if size_mb > 5:
            large_files.append((f.relative_to(root), size_mb))

large_files.sort(key=lambda x: x[1], reverse=True)
print("Archivos de más de 5MB:")
for rel, size in large_files[:20]:
    print(f"  {size:6.2f} MB - {rel}")
