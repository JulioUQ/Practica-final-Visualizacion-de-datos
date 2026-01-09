import re
import subprocess

# --- CONFIGURA AQUÍ TU ARCHIVO .py ---
python_file = r"C:\Users\usuario\Desktop\Practica-final-Visualizacion-de-datos\dashboard_flota.py"
output_file = r"C:\Users\usuario\Desktop\Practica-final-Visualizacion-de-datos\requirements.txt"

# Leer el código
with open(python_file, "r", encoding="utf-8") as f:
    code = f.read()

# Buscar todas las importaciones
imports = re.findall(r'^\s*(?:import|from)\s+([a-zA-Z0-9_\.]+)', code, flags=re.MULTILINE)

# Limpiar nombres (quitar submódulos: 'plotly.express' -> 'plotly')
packages = set([imp.split('.')[0] for imp in imports])

# Opcional: mapear nombres a PyPI si son distintos
package_map = {
    'PIL': 'pillow',  # Pillow en PyPI
}

packages = [package_map.get(p, p) for p in packages]

# Guardar en requirements.txt usando la versión instalada actualmente
with open(output_file, "w", encoding="utf-8") as f:
    for package in packages:
        try:
            # Obtener la versión instalada
            version = subprocess.check_output(
                ["pip", "show", package],
                text=True
            )
            ver_match = re.search(r"Version:\s*(.+)", version)
            if ver_match:
                f.write(f"{package}=={ver_match.group(1)}\n")
            else:
                f.write(f"{package}\n")
        except subprocess.CalledProcessError:
            # Si no se encuentra la librería instalada, solo escribe el nombre
            f.write(f"{package}\n")

print(f"Archivo '{output_file}' generado con los paquetes detectados:")
print("\n".join(packages))
