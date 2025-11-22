# Knowledge Ingester

Un système personnel de gestion des connaissances. Ingérez, traitez, stockez et affichez des liens via un bot Discord, une API FastAPI, et une application web Next.js.

## 🏗️ Architecture

- **Backend**: FastAPI + SQLModel + PostgreSQL
- **Frontend**: Next.js 16 + React 19 + Tailwind CSS
- **Bot**: Discord.py
- **IA**: Google Gemini API pour la génération de métadonnées

## 📋 Prérequis

- Python 3.9+
- Node.js 18+
- Docker et Docker Compose (optionnel)
- Compte Discord et token bot
- Clé API Google Gemini

## 🚀 Installation Rapide

### 1️⃣ Base de Données

**Managed Service**

- [Supabase](https://supabase.com)
- [Neon](https://neon.tech)
- [ElephantSQL](https://www.elephantsql.com)

### 2️⃣ Backend

```bash
cd backend

# Virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Dependencies
pip install -r requirements.txt

# Configuration
cat > .env << EOF
DATABASE_URL="postgresql://user:password@localhost:5432/knowledge_ingester"
GEMINI_API_KEY="your_gemini_api_key_here"
EOF

# Migration (si nécessaire)
python migrate.py

# Démarrage
uvicorn main:app --reload
```

**API disponible**: `http://127.0.0.1:8000`

### 3️⃣ Bot Discord

```bash
cd bot

# Virtual environment
python3 -m venv venv
source venv/bin/activate

# Dependencies
pip install -r requirements.txt

# Configuration
cat > .env << EOF
DISCORD_TOKEN="your_discord_bot_token"
BACKEND_URL="http://127.0.0.1:8000"
EOF

# Démarrage
python bot.py
```

### 4️⃣ Frontend

```bash
cd frontend

# Dependencies
npm install

# Configuration
cat > .env.local << EOF
NEXT_PUBLIC_API_URL="http://127.0.0.1:8000"
EOF

# Démarrage
npm run dev
```

**Interface disponible**: `http://localhost:3000`

---

## 📚 Utilisation

### Via Bot Discord

```
/add <url>
  → Ajoute un article

/tool <url> [description]
  → Ajoute un outil/ressource

/list
  → Affiche les 10 derniers liens
```

### Via API REST

**Ajouter un lien**:

```bash
curl -X POST "http://127.0.0.1:8000/ingest/" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "source": "manual",
    "resource_type": "article"
  }'
```

**Récupérer les liens**:

```bash
curl "http://127.0.0.1:8000/links/?limit=50"
```

**Supprimer un lien**:

```bash
curl -X DELETE "http://127.0.0.1:8000/links/1"
```

---

## 🗂️ Structure du Projet

```
knowledge-ingester/
├── backend/
│   ├── main.py           # API FastAPI
│   ├── models.py         # Schéma SQLModel
│   ├── crud.py           # Opérations DB
│   ├── database.py       # Configuration DB
│   ├── migrate.py        # Scripts de migration
│   ├── requirements.txt
│   └── .env
├── bot/
│   ├── bot.py            # Discord bot
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── app/          # Pages Next.js
│   │   ├── lib/          # Utilitaires API
│   │   └── types.ts      # Types TypeScript
│   ├── public/           # Fichiers statiques
│   ├── package.json
│   └── .env.local
├── ARCHITECTURE.md
├── README.md
└── docker-compose.yml    # (optionnel)
```

---

## 🎨 Fonctionnalités Frontend

- ✅ Recherche en temps réel
- ✅ Filtrage par type (articles/ressources)
- ✅ Filtrage par tags
- ✅ Tri par date ou titre
- ✅ Suppression de liens
- ✅ Design néo-brutaliste
- ✅ Design responsive

---

## 🤖 Flux de Traitement

1. **Bot/API**: Reçoit une URL
2. **Scraping**: Récupère le contenu (requests ou Playwright pour sites JS)
3. **IA**: Génère titre, description et tags via Gemini API
4. **Stockage**: Sauvegarde en base de données PostgreSQL
5. **Frontend**: Affiche les données avec filtres et recherche

---

## 🛠️ Variables d'Environnement

### Backend (`.env`)

```env
DATABASE_URL=postgresql://user:password@host:5432/db
GEMINI_API_KEY=your_api_key
```

### Bot (`.env`)

```env
DISCORD_TOKEN=your_token
BACKEND_URL=http://127.0.0.1:8000
```

### Frontend (`.env.local`)

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

---

## 📦 Scripts Disponibles

### Backend

```bash
# Démarrage
uvicorn main:app --reload

# Migration DB
python migrate.py
```

### Frontend

```bash
npm run dev      # Développement
npm run build    # Production
npm run start    # Serveur production
npm run lint     # ESLint
```

---

## 🐛 Dépannage

**"Could not fetch URL"**
→ Vérifiez que l'URL est valide et accessible

**"Database connection failed"**
→ Vérifiez `DATABASE_URL` et que PostgreSQL est actif

**"Discord bot not responding"**
→ Vérifiez `DISCORD_TOKEN` et les permissions du bot

**"Gemini API error"**
→ Vérifiez `GEMINI_API_KEY` et le quota API

---

## 📝 Licence

MIT

---

## 👨‍💻 Auteur

Your Name
