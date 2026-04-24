# 🧠 Daily AI Digest

Rapport quotidien de veille IA, généré par Claude (API) avec recherche web, envoyé par Gmail chaque matin à 9h (Paris).

Orienté pour un profil Data/IA qui veut rester pertinent techniquement et identifier les opportunités marché.

## Contenu du rapport

1. **Percées techniques** — nouveaux modèles, papers, benchmarks
2. **Stack & outillage** — frameworks, libs, patterns qui émergent
3. **Signaux marché** — levées, pivots, embauches stratégiques
4. **Compétence du jour** — une reco actionnable à creuser aujourd'hui

## Setup (5 minutes)

### 1. Créer le repo GitHub
```bash
git init
git add .
git commit -m "Initial commit"
# Créer un repo privé sur github.com puis :
git remote add origin git@github.com:<toi>/ai-daily-digest.git
git push -u origin main
```

### 2. Récupérer une clé API Anthropic
- https://console.anthropic.com → API Keys → Create Key
- Vérifie que **Web Search est activé** dans Console → Settings (obligatoire)
- Ajoute quelques $ de crédit (un run coûte ~$0.05-0.20)

### 3. Créer un mot de passe d'application Gmail
⚠️ Nécessite la validation en 2 étapes activée sur ton compte Google.
- https://myaccount.google.com/apppasswords
- Crée un mot de passe, nomme-le "AI Digest"
- Copie les 16 caractères (sans espaces)

### 4. Ajouter les secrets dans GitHub
Dans ton repo : **Settings → Secrets and variables → Actions → New repository secret**

| Nom | Valeur |
|---|---|
| `ANTHROPIC_API_KEY` | `sk-ant-...` |
| `GMAIL_USER` | `tonemail@gmail.com` |
| `GMAIL_APP_PASSWORD` | les 16 caractères |
| `RECIPIENT` | destinataire (ou identique à GMAIL_USER) |

### 5. Tester
- Onglet **Actions** du repo → `Daily AI Digest` → `Run workflow`
- Vérifie tes mails dans ~1 minute

Une fois que ça marche, le cron prend le relais automatiquement.

## Coûts

- **GitHub Actions** : gratuit (le job prend ~1 min/jour, largement sous le quota)
- **API Anthropic** : ~$0.05-0.20 par run selon le nombre de recherches
  → environ **$3-6/mois**

## Personnalisation

Tout se passe dans `digest.py` :
- `SYSTEM_PROMPT` / `USER_PROMPT` — ajuster l'angle, ajouter/retirer des sections
- `MODEL` — swap vers Sonnet si tu veux réduire les coûts
- `max_uses: 8` dans le tool web_search — plus de recherches = rapport plus fouillé mais plus cher
- `max_tokens: 4096` — longueur max du rapport

Pour changer l'heure d'envoi, édite le `cron` dans `.github/workflows/daily.yml`.
Format : `"minute heure * * *"` en **UTC**.

## Debug

Si le mail n'arrive pas :
1. Onglet **Actions** → clique sur le run échoué → regarde les logs
2. Erreur Gmail 535 = mauvais mot de passe d'application
3. Erreur Anthropic 401 = clé API invalide
4. Erreur "web_search not enabled" = à activer dans la Console Anthropic
