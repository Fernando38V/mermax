# Clonar el repo (solo la primera vez)
git clone https://github.com/Fernando38V/mermax.git
cd mermax

# Antes de empezar a trabajar: SIEMPRE actualizar
git pull origin main

# Ver qué archivos cambiaste
git status

# Ver los cambios línea por línea
git diff

# Agregar cambios
git add .                      # todos los archivos modificados
git add ruta/archivo.py        # un archivo específico

# Guardar los cambios (commit)
git commit -m "descripción corta de lo que hiciste"

# Subir tus cambios
git pull origin main           # de nuevo, por si alguien subió algo
git push origin main

# Ver historial de commits
git log --oneline -10