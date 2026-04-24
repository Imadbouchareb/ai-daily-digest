"""
Rapport quotidien de veille IA — envoyé par mail chaque matin.

Profil cible : diplômé master Data/IA cherchant à rester pertinent sur le marché.
Focus : percées techniques, stack/outillage, signaux marché, compétence du jour.
"""

import os
import smtplib
import ssl
from datetime import datetime, timezone
from email.message import EmailMessage

from anthropic import Anthropic

# -------- Configuration depuis les variables d'environnement --------
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
GMAIL_USER = os.environ["GMAIL_USER"]          # ex: toi@gmail.com
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]  # mot de passe d'application
RECIPIENT = os.environ.get("RECIPIENT", GMAIL_USER)

MODEL = "claude-opus-4-5"  # à ajuster selon ce qui est dispo sur ton compte

# -------- Prompt de veille --------
SYSTEM_PROMPT = """Tu es un analyste de veille IA qui rédige un brief quotidien pour un \
diplômé de master Data/IA. L'objectif du lecteur : rester à jour techniquement et \
identifier les compétences à développer pour saisir de nouvelles opportunités \
professionnelles dans les 6-12 prochains mois.

Règles impératives :
- Signal > bruit. Ne remplis pas pour remplir. Si une section n'a rien de notable \
  dans les dernières 24-48h, écris "Rien de significatif aujourd'hui" et passe à la suite.
- Pas de hype creuse. Chaque item doit expliquer *pourquoi ça compte* pour un praticien.
- Source systématique avec lien, format markdown.
- Français. Ton direct, pas de formules marketing."""

USER_PROMPT = f"""Produis le brief IA du {datetime.now().strftime('%A %d %B %Y')}.

Structure en 4 sections markdown :

## 1. Percées techniques (24-48h)
Nouveaux modèles, architectures, benchmarks, papers arXiv marquants. \
Pour chaque item : 2-3 lignes sur *ce qui est nouveau techniquement* et l'impact pratique.

## 2. Stack & outillage
Frameworks, libs, patterns en adoption (agents, RAG, inference, fine-tuning, eval, \
orchestration...). Ce qui apparaît dans les repos actifs, les blogs d'ingé, les \
release notes récentes.

## 3. Signaux marché
Levées, embauches stratégiques, pivots des gros acteurs (OpenAI, Anthropic, Meta, \
Google, Mistral, startups). Ce qui indique *où seront les jobs dans 6-12 mois*.

## 4. Compétence du jour
UNE seule recommandation actionnable aujourd'hui : un concept, un outil, un paper, \
un tuto à creuser. Explique pourquoi, et donne un point d'entrée concret \
(lien GitHub, paper, doc).

Recherche avec plusieurs requêtes ciblées. Privilégie sources primaires \
(arXiv, blogs de labos, release notes) aux agrégateurs."""


def generate_digest() -> str:
    """Appelle Claude avec web_search pour générer le rapport."""
    client = Anthropic(api_key=ANTHROPIC_API_KEY)

    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": USER_PROMPT}],
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 8,
        }],
    )

    # La réponse contient plusieurs blocs : server_tool_use, web_search_tool_result, text.
    # On ne garde que les blocs texte finaux.
    parts = [block.text for block in response.content if block.type == "text"]
    return "\n\n".join(parts).strip()


def send_email(body_markdown: str) -> None:
    """Envoie le rapport par SMTP Gmail."""
    today = datetime.now().strftime("%d/%m/%Y")
    msg = EmailMessage()
    msg["Subject"] = f"🧠 Veille IA — {today}"
    msg["From"] = GMAIL_USER
    msg["To"] = RECIPIENT

    # Version texte + version HTML simple (rendu markdown minimal côté client)
    msg.set_content(body_markdown)
    html_body = _markdown_to_html(body_markdown)
    msg.add_alternative(html_body, subtype="html")

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        smtp.send_message(msg)


def _markdown_to_html(md: str) -> str:
    """Conversion markdown minimale — évite une dépendance en plus."""
    try:
        import markdown
        body = markdown.markdown(md, extensions=["extra"])
    except ImportError:
        # Fallback très basique si markdown n'est pas installé
        body = "<pre style='font-family: system-ui; white-space: pre-wrap;'>" + \
               md.replace("<", "&lt;").replace(">", "&gt;") + "</pre>"

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"></head>
<body style="font-family: -apple-system, system-ui, sans-serif; max-width: 720px; \
margin: 0 auto; padding: 16px; line-height: 1.6; color: #222;">
{body}
<hr style="margin-top: 32px; border: none; border-top: 1px solid #eee;">
<p style="color: #888; font-size: 12px;">Généré automatiquement par Claude API — \
{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</p>
</body></html>"""


if __name__ == "__main__":
    print("→ Génération du rapport...")
    digest = generate_digest()
    print(f"→ Rapport généré ({len(digest)} caractères)")
    print("→ Envoi du mail...")
    send_email(digest)
    print("✓ Mail envoyé à", RECIPIENT)
