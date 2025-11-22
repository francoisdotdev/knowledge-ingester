# 🏗️ Architecture - Knowledge Ingester

Document décrivant l'architecture complète du système Knowledge Ingester.

---

## 📊 Modèle de Données (Schéma Base de Données)

La base de données contient une table principale : `link`

### Colonnes

| Colonne         | Type        | Description                          |
| --------------- | ----------- | ------------------------------------ |
| `id`            | `INTEGER`   | Clé primaire, auto-incrémentée       |
| `url`           | `VARCHAR`   | URL unique, obligatoire              |
| `title`         | `VARCHAR`   | Titre de l'article/ressource         |
| `description`   | `TEXT`      | Description/résumé                   |
| `tags`          | `JSON`      | Array de tags (ex: ["ai", "python"]) |
| `source`        | `VARCHAR`   | Source (discord, manual, etc.)       |
| `resource_type` | `VARCHAR`   | Type (article ou resource)           |
| `created_at`    | `TIMESTAMP` | Date de création (UTC)               |
| `read`          | `BOOLEAN`   | Marqué comme lu (défaut: false)      |

---

## 🔄 Flux Bot → Backend → DB

### Étape par étape

1. **Utilisateur Discord** : Envoie `/add https://example.com`
2. **Bot Discord** : Valide l'URL et envoie POST à `/ingest/`
3. **Backend FastAPI** : Reçoit la requête
4. **Web Scraping** :
   - Utilise `requests` pour récupérer le contenu
   - Utilise `Playwright` pour les sites JavaScript
   - Fallback sur `BeautifulSoup` pour parser le HTML
5. **Extraction métadonnées** :
   - Récupère title et meta description
   - Fallback sur le premier paragraphe
6. **IA (Gemini API)** :
   - Génère un titre amélioré
   - Génère une description complète
   - Génère les tags automatiquement
7. **Stockage DB** : Insère dans PostgreSQL via SQLModel
8. **Réponse** : Retourne le lien créé au bot
9. **Utilisateur** : Reçoit confirmation sur Discord

---

## 🛠️ Stack Technologique

### Backend

- **Framework** : FastAPI (async)
- **ORM** : SQLModel (SQLAlchemy + Pydantic)
- **Base de données** : PostgreSQL 14+
- **Web Scraping** : requests, BeautifulSoup4, Playwright
- **IA** : Google Generative AI (Gemini)
- **Serveur** : Uvicorn

### Bot Discord

- **Librairie** : discord.py 2.6+
- **Commands** : Slash commands (app_commands)
- **API Client** : requests

### Frontend

- **Framework** : Next.js 16 (React 19)
- **UI** : Tailwind CSS
- **Styling** : Neo-brutalisme
- **État** : React hooks
- **API Client** : fetch API + TypeScript

### Infrastructure

- **Base de données** : PostgreSQL (Supabase, Neon, ou local Docker)
- **Déploiement** : Docker/Docker Compose (optionnel)

---

## 📡 Architecture Générale

```
┌──────────────────────────────────────────────────────────────┐
│                     UTILISATEUR DISCORD                      │
└────────────────┬─────────────────────────────┬───────────────┘
                 │                             │
         ┌───────▼────────┐         ┌──────────▼─────────┐
         │   BOT DISCORD  │         │  FRONTEND NEXT.JS  │
         │  Slash Commands│         │   React Interface  │
         └────────┬───────┘         └──────────┬─────────┘
                  │                           │
                  └───────────┬───────────────┘
                              │
                    ┌─────────▼──────────┐
                    │  BACKEND FASTAPI   │
                    │  - /ingest/        │
                    │  - /links/         │
                    │  - Scraping        │
                    │  - Gemini AI       │
                    └─────────┬──────────┘
                              │
                    ┌─────────▼──────────┐
                    │  POSTGRESQL DB     │
                    │  - Stockage liens  │
                    │  - Métadonnées     │
                    └────────────────────┘
```

---

## 🔐 Gestion des Erreurs

### Erreurs Utilisateur

| Erreur           | Réponse Bot              | Action              |
| ---------------- | ------------------------ | ------------------- |
| URL invalide     | ❌ "URL invalide"        | Valide le format    |
| URL inaccessible | ⚠️ "Page non accessible" | Enregistre l'erreur |

### Erreurs Backend

| Erreur          | Handling               | Fallback                   |
| --------------- | ---------------------- | -------------------------- |
| Scrapage échoue | Log + essai Playwright | URL brute sans métadonnées |
| IA indisponible | Retry 3x               | Tags par défaut            |
| DB déconnectée  | Rollback + reconnect   | Message d'erreur au bot    |

---

## 🔌 Endpoints API Backend

### POST `/ingest/`

```json
{
  "url": "https://example.com",
  "source": "discord",
  "resource_type": "article",
  "title": "(optionnel)",
  "description": "(optionnel)"
}
```

**Réponse** :

```json
{
  "id": 1,
  "url": "https://example.com",
  "title": "Example Article",
  "description": "...",
  "tags": ["tech", "ai"],
  "source": "discord",
  "resource_type": "article",
  "created_at": "2025-11-22T12:00:00Z",
  "read": false
}
```

### GET `/links/`

**Paramètres** : `skip=0`, `limit=100`

**Réponse** : Array de liens

### DELETE `/links/{link_id}`

**Réponse** : `200 OK`

---

## 💾 Base de Données

### Choix : PostgreSQL

- ✅ Type JSON pour les tags
- ✅ ACID compliance
- ✅ Scaling horizontal
- ✅ Support des timestamps précis

### Managed Services Recommandés

- [Supabase](https://supabase.com) - PostgreSQL managé
- [Neon](https://neon.tech) - PostgreSQL serverless
- [Render](https://render.com) - PostgreSQL simple

---

## 🚀 Performance & Scalabilité

### Optimisations

- `pool_pre_ping=True` : Vérifie les connexions DB
- `pool_recycle=3600` : Recycle les connexions
- Timeout scraping : 30 secondes
- Retry automatique : 3 tentatives

### Bottlenecks Potentiels

1. **Scraping** : Sites lents → Timeout
2. **IA** : Rate limiting Gemini → Queue
3. **DB** : Connections → Connection pooling

---

## 📝 Conventions de Code

- **Naming** : snake_case pour Python, camelCase pour TypeScript
- **Types** : Pydantic models + SQLModel
- **Errors** : Exception handling explicite
- **Logs** : INFO/ERROR avec contexte
