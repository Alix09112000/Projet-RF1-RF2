# Outil budget RF1 / RF2 — Canalbox Côte d'Ivoire

Application web qui remplace la construction manuelle des fichiers RF1/RF2 :
saisie des hypothèses, recalcul automatique du modèle, génération des commentaires d'écart.

- **Périmètre** : Côte d'Ivoire, une seule ville (Abidjan, code `ABJ`), segments B2C, SME, DROPE.
- **Système indépendant** : aucune connexion aux systèmes Canalbox. Les données réelles arrivent
  par dépôt de fichiers (voir `docs/`).

## Architecture

| Dossier | Contenu |
| --- | --- |
| `api/` | API Python 3.12 · FastAPI · SQLAlchemy 2 · Alembic · PostgreSQL |
| `web/` | Interface React · Vite · TypeScript · TanStack Query, servie par Caddy |
| `docs/` | Décisions techniques, backlog, format des fichiers d'import |

En production, Caddy sert l'interface et transmet `/api/*` à l'API. Tout tourne avec Docker Compose.

## Démarrer en local avec Docker

```bash
cp .env.example .env          # puis renseigner SECRET_KEY, ADMIN_EMAIL, ADMIN_PASSWORD
docker compose up --build
```

- Interface : http://localhost:8080
- Documentation de l'API : http://localhost:8080/api/docs

Au premier démarrage, l'API applique les migrations et crée les données de référence
(Abidjan, les trois segments, les versions BI26 / RF1 / RF2) et le compte administrateur.

## Développer sans Docker

```bash
# Base de données seule
docker compose up db -d

# API
cd api
python -m venv .venv && source .venv/bin/activate   # Windows : .venv\Scripts\activate
pip install -e ".[dev]"
export DATABASE_URL=postgresql+psycopg://rf:rf@localhost:5432/rf
alembic upgrade head
ADMIN_EMAIL=admin@canalbox.ci ADMIN_PASSWORD=changez-moi-1234 python -m app.seed
uvicorn app.main:app --reload

# Interface (autre terminal)
cd web
npm install
npm run dev            # http://localhost:5173, /api est relayé vers le port 8000
```

Pour exposer le port de la base en local, ajouter `ports: ["5432:5432"]` au service `db`.

## Qualité

```bash
cd api
ruff check .
mypy app
pytest
```

Les mêmes contrôles tournent sur chaque pull request (`.github/workflows/ci.yml`).

## Rôles

| Rôle | Peut |
| --- | --- |
| `contributor` | saisir les hypothèses de son périmètre |
| `controller` | contrôle de gestion : déposer les fichiers, régler les paramètres, valider les commentaires |
| `viewer` | consulter le tableau de bord et l'historique |
| `admin` | tout, plus la gestion des comptes |

## Méthode de travail

- `main` est protégée et toujours déployable.
- Une issue par besoin, une branche par issue : `feature/12-import-echus`.
- Messages de commit : `feat:`, `fix:`, `test:`, `docs:`, `refactor:`, `chore:`.
- Une version étiquetée à chaque fin de sprint (`v0.1`, `v0.2`…).

## Avancement

| Sprint | Contenu | État |
| --- | --- | --- |
| S0 | Socle, comptes et rôles | terminé (v0.1) |
| S1 | Import des fichiers Réalisés commerciaux et Échus | terminé (v0.2) |
| S2 | Saisie DRCOM (B2C1, SME1), paramètres de la ville, historique | terminé |
| S3 | Moteur de calcul B2C | **en cours** (blocs B0 à B2 fusionnés) |
| S4 | Moteur SME, DROPE, P&L pays | à faire |
| S5 | Tableau de bord, commentaires, export | à faire |
