# Adobe Stock & Freepik Automator

Outil automatisé de génération, d'optimisation et de publication multi-plateforme d'images de stock. Prend en charge Codex CLI (abonnement ChatGPT) ou plusieurs moteurs de génération d'images comme OpenAI/Stability/Replicate, produisant automatiquement des images et des métadonnées conformes aux spécifications d'Adobe Stock et Freepik, avec téléchargement via FTPS ou automatisation web CloakBrowser.

## Pipeline

```
Prompt ──> Génération IA ──> Upscale 6MP ──> CSV Métadonnées (Adobe / Freepik) ──> Téléchargement automatique Web/FTP/FTPS
```

## Fonctionnalités

*   **Support CSV Multi-Plateforme** :
    *   **Adobe Stock** : Génère un CSV séparé par des virgules, convertit automatiquement les noms de catégories en IDs numériques Adobe Stock.
    *   **Freepik** : Génère un CSV séparé par des points-virgules (`;`) (champs : `File name;Title;Keywords;Prompt;Model`). Le contenu généré par IA ajoute automatiquement `_ai_generated` à la fin des mots-clés. La longueur du titre est automatiquement tronquée à 100 caractères pour éviter les erreurs.
*   **Optimisation Automatique de la Résolution (Upscale)** : Détecte automatiquement la résolution de l'image. Si elle est inférieure à la limite de 6MP, utilise le filtre Lanczos pour un agrandissement sans perte à 6MP+ (3000x2000), garantissant une validation à 100% par la plateforme de stock.
*   **Téléchargement Web Automatique Robuste (CloakBrowser)** : Utilise Stealth Chromium pour contourner les mécanismes anti-bot de Cloudflare. Prend en charge la persistance de connexion manuelle/par cookies, le téléchargement d'images par glisser-déposer, et guide les utilisateurs vers l'import en un clic du `metadata_freepik.csv` dédié pour une application par lots.
*   **Connexion FTPS Sécurisée** : Prend en charge le téléchargement groupé à haute vitesse via FTPS (Explicit TLS) pour les comptes Freepik de niveau 3 et supérieur.

## Démarrage Rapide

```bash
# Installer les dépendances
pip install -r requirements.txt

# Initialiser le fichier de configuration
cp config.example.yaml config.yaml
# Renseigner les identifiants du compte de stock ou les clés API dans config.yaml

# Tester la génération d'images (mode dummy sans clé API, génère les infos Adobe et Freepik)
python3 main.py generate "neon retro synthwave sunset" -n 1 -p dummy --freepik

# Télécharger toutes les images JPEG existantes dans le répertoire output (exemple de téléchargement web Freepik)
python3 main.py upload --platform freepik
```

## Commandes CLI

| Commande | Description |
|----------|-------------|
| `generate` | Génération IA → Upscale 6MP → Génération CSV → Téléchargement web (utilisez `--freepik` pour générer aussi la sortie Freepik) |
| `upload` | Télécharge toutes les images existantes dans le répertoire output via CloakBrowser (prend en charge adobe-stock, freepik) |
| `cloak` | Flux de travail intégré "génération + téléchargement web automatique" via CloakBrowser |
| `portal_upload` | Module de téléchargement dédié à Adobe Stock Portal |
| `batch` | Traitement par lots des fichiers de prompts |
| `requirements` | Affiche les spécifications d'images des plateformes de stock |

### Génération par Lots (50 Images)

```bash
bash run_50.sh
```

Utilise `dashboard/scripts/codex-gen-wrapper.sh` pour exécuter la génération parallèle avec Codex CLI, 10 images par lot, terminant 50 images en environ 3 à 5 minutes.
Après la génération, exécutez `./gen_metadata.py` pour régénérer et mettre à jour tous les CSV.

## Structure du Projet

```
adobe-stock-automator/
├── main.py                     # Point d'entrée CLI (Click)
├── src/
│   ├── config.py               | Chargement de la configuration YAML avec remplacement par variables d'environnement
│   ├── generate.py             # Génération d'images (dummy/openai/stability/replicate/local)
│   ├── image_utils.py          # Détection de résolution et optimisation Lanczos 6MP+
│   ├── metadata.py             # Génération de métadonnées et sortie CSV double Adobe/Freepik
│   ├── upload.py               # Logique de téléchargement FTP / FTPS (Explicit TLS)
│   ├── submit_browser.py       # Automatisation de navigateur Playwright
│   ├── portal_upload.py        # Téléchargement dédié Adobe Portal
│   └── upload_cloak.py         # Téléchargement Stealth CloakBrowser (Adobe Stock / Freepik)
├── config.example.yaml
├── prompts_50.txt              # 50 modèles de prompts commerciaux
├── gen_metadata.py             # Outil d'optimisation par lots et de régénération des métadonnées
├── run_50.sh                   # Script de génération et d'optimisation par lots de 50 images
├── README.md                   # Original (Chinois traditionnel)
├── README.en.md                # Anglais
├── README.ja.md                # Japonais
├── README.ko.md                # Coréen
├── README.es.md                # Espagnol
└── README.fr.md                # Français
```

## Support des Plateformes

| Plateforme | Automatisation Web (CloakBrowser) | Téléchargement FTP / FTPS | Remarques |
|-----------|----------------------------------|--------------------------|-----------|
| **Adobe Stock** | ✅ Remplissage automatique des champs et étiquettes IA | ❌ Plus actif officiellement | Mode Web ou import CSV recommandé |
| **Freepik** | ✅ Glisser-déposer automatique + import CSV en un clic | ✅ Prend en charge FTPS (Explicit TLS) | Comptes de niveau inférieur à 3 utilisent le mode Web ; niveau 3 et supérieur peuvent utiliser FTPS |

## Confidentialité et Sécurité

- `config.yaml` contient vos identifiants personnels → ajouté à `.gitignore`
- Cache de cookies dans `.cookies/` → ajouté à `.gitignore`
- Images générées dans `output/` → ajouté à `.gitignore`

## Licence

MIT — Laban Chen
