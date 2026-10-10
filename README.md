# **Inicializar el sitio Hugo con la plantilla Book**
Ejecuta el siguiente comando para crear un nuevo sitio Hugo y añadir la plantilla **Hugo Book** como submódulo de Git:
```bash
hugo new site BBDD --force
cd BBDD
git init -b main
git submodule add https://github.com/alex-shpak/hugo-book.git themes/hugo-book
# Crea un archivo .gitignore para excluir archivos innecesarios
echo "public/" >> .gitignore
echo "node_modules/" >> .gitignore
```

# **Configurar el archivo `config.toml`**
Edita el archivo `config.toml` para configurar el sitio:
```toml
baseURL = "https://lorenalresusta.github.io/Seguridad-y-Alta-Disponibilidad/"  # Cambia por tu URL de GitLab Pages o GitHub Pages
locale = "es-es"
title = "Seguridad y Alta Disponibilidad "
theme = "hugo-book"

# Configuración multilingüe
defaultContentLanguage = "es"

# Configuración para multilingüe
[languages]
  [languages.es]
    languageName = "Castellano"
    weight = 1
    contentDir = "content.es"

  [languages.val]
    languageName = "Valencià"
    weight = 2
    contentDir = "content.val"

[params]
  # Origen de los ficheros a renderizar
  BookSection = '/'

[caches]
  [caches.images]
    dir = ':cacheDir/images'
```

# **Crear la estructura de directorios para los idiomas**
```bash
mkdir -p content.es content.val
```

# **Crear una página de ejemplo en cada idioma**
- **Castellano**: `content.es/_index.md`
  ```markdown
  ---
  title: "Bienvenido"
  ---

  ¡Hola! Esta es la página en castellano.
  ```

- **Valenciano**: `content.val/_index.md`
  ```markdown
  ---
  title: "Benvingut"
  ---

  Hola! Aquesta és la pàgina en valencià.
  ```

---

# **Probar el sitio localmente**
Ejecuta el siguiente comando para iniciar el servidor de desarrollo de Hugo en el contenedor:
```bash
hugo server -D
```
- Abre tu navegador y ve a: [http://localhost:1313](http://localhost:1313).
- Deberías ver tu sitio web con los dos idiomas disponibles.

---
# **DESPLIEGUE EN GITLAB PAGES**
# **Configurar el archivo `.gitlab-ci.yml`**
Crea un archivo `.gitlab-ci.yml` en la raíz de tu proyecto para automatizar la generación y despliegue de la web estática:
```yaml
variables:
  # Define tool versions
  DART_SASS_VERSION: 1.104.0
  GO_VERSION: 1.27.0
  HUGO_VERSION: 0.166.0
  NODE_VERSION: 24.20.0

  # Set the build timezone
  TZ: Europe/Oslo

  # Set the build cache directory
  HUGO_CACHEDIR: ${CI_PROJECT_DIR}/.cache/hugo

  # Set the repository clone and fetch strategy
  GIT_DEPTH: 0
  GIT_STRATEGY: clone
  GIT_SUBMODULE_STRATEGY: recursive
cache:
  key: ${CI_COMMIT_REF_SLUG}
  fallback_keys:
    - ${CI_DEFAULT_BRANCH}
  paths:
    - .cache/hugo
image:
  name: buildpack-deps:bookworm
pages:
  stage: deploy
  script:
    - chmod a+x build.sh && ./build.sh
  artifacts:
    paths:
      - public
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```
- Este archivo usa la imagen de Hugo para generar el sitio estático y lo despliega en **GitLab Pages**.
- La variable `GIT_SUBMODULE_STRATEGY: recursive` asegura que el tema `hugo-book` se clona correctamente.

# **DESPLIEGUE EN GITHUB PAGES**
Para desplegar nuestra web de documentación en GitHub Pages tenemos que seguir los siguientes pasos.
1. Crear nuestro repositorio de GitHub
2. En `Settings` > `Pages` cambiar en `Source` por `Github Action`
3. Creamos la siguiente carpeta para nuestra Github Action de despliegue
```bash
mkdir -p .github/workflows
cd .github/workflows
touch hugo.yaml
```
4. Dentro del fichero `hugo.yaml` añadimos la siguiente action

```yaml
name: Build and deploy
on:
  push:
    branches:
      - main
  workflow_dispatch:
permissions:
  contents: read
  pages: write
  id-token: write
concurrency:
  group: pages
  cancel-in-progress: false
defaults:
  run:
    shell: bash
jobs:
  build:
    runs-on: ubuntu-latest
    env:
      # Define tool versions
      DART_SASS_VERSION: 1.104.0
      GO_VERSION: 1.27.0
      HUGO_VERSION: 0.166.0
      NODE_VERSION: 24.20.0

      # Set the build time zone
      TZ: Europe/Oslo
    steps:
      - name: Checkout
        uses: actions/checkout@v7
        with:
          submodules: recursive
          fetch-depth: 0
          lfs: false

      - name: Setup Pages
        id: pages
        uses: actions/configure-pages@v6

      - name: Create a local tools directory
        run: |
          mkdir -p "${HOME}/.local"

      - name: Install Go
        if: hashFiles('go.mod') != ''
        uses: actions/setup-go@v7
        with:
          go-version: ${{ env.GO_VERSION }}
          cache: false

      - name: Install Node.js
        if: hashFiles('package-lock.json') != ''
        uses: actions/setup-node@v7
        with:
          node-version: ${{ env.NODE_VERSION }}

      - name: Install Dart Sass
        run: |
          echo "Installing Dart Sass ${DART_SASS_VERSION}..."
          curl -sfL --output-dir "${{ runner.temp }}" -O "https://github.com/sass/dart-sass/releases/download/${DART_SASS_VERSION}/dart-sass-${DART_SASS_VERSION}-linux-x64.tar.gz"
          tar -C "${HOME}/.local" -xf "${{ runner.temp }}/dart-sass-${DART_SASS_VERSION}-linux-x64.tar.gz"
          echo "${HOME}/.local/dart-sass" >> "${GITHUB_PATH}"

      - name: Install Hugo
        run: |
          echo "Installing Hugo ${HUGO_VERSION}..."
          curl -sfL --output-dir "${{ runner.temp }}" -O "https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_${HUGO_VERSION}_linux-amd64.tar.gz"
          mkdir "${HOME}/.local/hugo"
          tar -C "${HOME}/.local/hugo" -xf "${{ runner.temp }}/hugo_${HUGO_VERSION}_linux-amd64.tar.gz"
          echo "${HOME}/.local/hugo" >> "${GITHUB_PATH}"

      - name: Log tool versions
        run: |
          echo "Logging tool versions..."
          command -v sass &> /dev/null && echo "Dart Sass: $(sass --version)" || echo "Dart Sass: not installed"
          command -v go &> /dev/null && echo "Go: $(go version)" || echo "Go: not installed"
          command -v hugo &> /dev/null && echo "Hugo: $(hugo version)" || echo "Hugo: not installed"
          command -v node &> /dev/null && echo "Node.js: $(node --version)" || echo "Node.js: not installed"

      - name: Configure Git
        run: |
          echo "Configuring Git..."
          git config --global core.quotepath false

      - name: Fetch full Git history
        run: |
          if [[ $(git rev-parse --is-shallow-repository) == true ]]; then
            echo "Fetching full Git history..."
            git fetch --unshallow
          fi

      - name: Initialize Git submodules
        run: |
          if [[ -f .gitmodules ]]; then
            echo "Initializing Git submodules..."
            git submodule update --init --recursive
          fi

      - name: Install Node.js dependencies
        run: |
          if [[ -f package-lock.json ]]; then
            echo "Installing Node.js dependencies..."
            npm ci
          fi

      - name: Cache restore
        id: cache-restore
        uses: actions/cache/restore@v6
        with:
          path: ${{ runner.temp }}/.cache/hugo
          key: hugo-${{ github.run_id }}
          restore-keys: hugo-

      - name: Build
        run: |
          echo "Building the project..."
          hugo build \
            --gc \
            --minify \
            --baseURL "${{ steps.pages.outputs.base_url }}/" \
            --cacheDir "${{ runner.temp }}/.cache/hugo"

      - name: Cache save
        uses: actions/cache/save@v6
        with:
          path: ${{ runner.temp }}/.cache/hugo
          key: ${{ steps.cache-restore.outputs.cache-primary-key }}

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v5
        with:
          include-hidden-files: false
          path: ./public
  deploy:
    runs-on: ubuntu-latest
    needs: build
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v5
```


---

# **Despliegue**:
   - Haz `git add .`, `git commit -m "Mensaje descriptivo"` y `git push` para actualizar el repositorio.
   - GitLab CI/CD o Github Actions (según cual se use) se encargará de generar el sitio y desplegarlo en GitLab Pages / Github Pages.
# BBDD
