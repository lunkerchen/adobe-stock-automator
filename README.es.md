# Adobe Stock & Freepik Automator

Herramienta automatizada de generación, optimización y publicación multiplataforma de imágenes de stock. Admite Codex CLI (suscripción a ChatGPT) o múltiples motores de generación de imágenes como OpenAI/Stability/Replicate, produciendo automáticamente imágenes y metadatos que cumplen con las especificaciones de Adobe Stock y Freepik, y subiendo mediante FTPS o automatización web con CloakBrowser.

## Flujo de trabajo

```
Prompt ──> Generación AI ──> Upscale 6MP ──> CSV de metadatos (Adobe / Freepik) ──> Subida automática Web/FTP/FTPS
```

## Características

*   **Soporte CSV Multiplataforma**:
    *   **Adobe Stock**: Genera CSV separado por comas, convierte automáticamente nombres de categorías a IDs numéricos de Adobe Stock.
    *   **Freepik**: Genera CSV separado por punto y coma (`;`) (campos: `File name;Title;Keywords;Prompt;Model`). El contenido generado por AI añade automáticamente `_ai_generated` al final de las palabras clave. La longitud del título se trunca automáticamente a 100 caracteres para evitar errores.
*   **Optimización Automática de Resolución (Upscale)**: Detecta automáticamente la resolución de la imagen. Si está por debajo del límite de 6MP, utiliza el filtro Lanczos para escalar sin pérdida a 6MP+ (3000x2000), garantizando el 100% de aprobación en la revisión de la plataforma de stock.
*   **Subida Web Automática Robusta (CloakBrowser)**: Utiliza Stealth Chromium para evadir los mecanismos anti-bot de Cloudflare. Soporta persistencia de inicio de sesión manual/por cookies, subida de imágenes por arrastrar y soltar, y guía a los usuarios para importar con un clic el `metadata_freepik.csv` dedicado para aplicación por lotes.
*   **Conexión FTPS Segura**: Soporta subida masiva de alta velocidad por FTPS (Explicit TLS) para cuentas Freepik de nivel 3 o superior.

## Inicio Rápido

```bash
# Instalar dependencias
pip install -r requirements.txt

# Inicializar archivo de configuración
cp config.example.yaml config.yaml
# Completa las credenciales de la cuenta de stock o las claves API en config.yaml

# Probar generación de imágenes (modo dummy sin clave API, genera info tanto de Adobe como de Freepik)
python3 main.py generate "neon retro synthwave sunset" -n 1 -p dummy --freepik

# Subir todas las imágenes JPEG existentes en el directorio output (ejemplo de subida web Freepik)
python3 main.py upload --platform freepik
```

## Comandos CLI

| Comando | Descripción |
|---------|-------------|
| `generate` | Generación AI → Upscale 6MP → Generación CSV → Subida web (usa `--freepik` para generar también salida Freepik) |
| `upload` | Sube todas las imágenes existentes en el directorio output mediante CloakBrowser (soporta adobe-stock, freepik) |
| `cloak` | Flujo de trabajo integrado "generación + subida web automática" mediante CloakBrowser |
| `portal_upload` | Módulo de subida dedicado a Adobe Stock Portal |
| `batch` | Procesamiento por lotes de archivos de prompts |
| `requirements` | Muestra las especificaciones de imagen de cada plataforma de stock |

### Generación por Lotes (50 Imágenes)

```bash
bash run_50.sh
```

Usa `dashboard/scripts/codex-gen-wrapper.sh` para ejecutar generación paralela con Codex CLI, 10 imágenes por lote, completando 50 imágenes en aproximadamente 3-5 minutos.
Después de la generación, ejecuta `./gen_metadata.py` para regenerar y actualizar todos los CSVs.

## Estructura del Proyecto

```
adobe-stock-automator/
├── main.py                     # Punto de entrada CLI (Click)
├── src/
│   ├── config.py               # Carga de configuración YAML con anulación por variables de entorno
│   ├── generate.py             # Generación de imágenes (dummy/openai/stability/replicate/local)
│   ├── image_utils.py          # Detección de resolución y optimización Lanczos 6MP+
│   ├── metadata.py             # Generación de metadatos y salida CSV dual Adobe/Freepik
│   ├── upload.py               # Lógica de subida FTP / FTPS (Explicit TLS)
│   ├── submit_browser.py       # Automatización de navegador Playwright
│   ├── portal_upload.py        # Subida dedicada a Adobe Portal
│   └── upload_cloak.py         # Subida Stealth CloakBrowser (Adobe Stock / Freepik)
├── config.example.yaml
├── prompts_50.txt              # 50 plantillas de prompts comerciales
├── gen_metadata.py             | Herramienta de optimización por lotes y regeneración de metadatos
├── run_50.sh                   # Script de generación y optimización por lotes de 50 imágenes
├── README.md                   # Original (Chino tradicional)
├── README.en.md                # Inglés
├── README.ja.md                # Japonés
├── README.ko.md                # Coreano
├── README.es.md                # Español
└── README.fr.md                # Francés
```

## Soporte de Plataformas

| Plataforma | Automatización Web (CloakBrowser) | Subida FTP / FTPS | Notas |
|-----------|----------------------------------|-------------------|-------|
| **Adobe Stock** | ✅ Relleno automático de campos y etiquetas AI | ❌ Ya no activo oficialmente | Se recomienda usar modo Web o importación CSV |
| **Freepik** | ✅ Arrastrar y soltar automático + importación CSV con un clic | ✅ Soporta FTPS (Explicit TLS) | Cuentas por debajo de nivel 3 usan modo Web; nivel 3 o superior pueden usar FTPS |

## Privacidad y Seguridad

- `config.yaml` contiene tus credenciales personales → añadido a `.gitignore`
- Caché de cookies en `.cookies/` → añadido a `.gitignore`
- Imágenes generadas en `output/` → añadido a `.gitignore`

## Licencia

MIT — Laban Chen
