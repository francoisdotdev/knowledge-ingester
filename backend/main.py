from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session
from typing import List
import requests
from bs4 import BeautifulSoup
import os
import google.generativeai as genai
from fastapi.middleware.cors import CORSMiddleware
from playwright.sync_api import sync_playwright
import time

import crud
import models
from database import engine

# Configuration Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_session():
    with Session(engine) as session:
        yield session


app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    models.SQLModel.metadata.create_all(engine)


def extract_article_content(html_content):
    """Extrait le contenu principal de l'article"""
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Supprimer les scripts et styles
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Chercher des tags
    article = soup.find("article") or soup.find("main") or soup.find("div", class_=["content", "post", "article"])
    
    if article:
        text = article.get_text()
    else:
        text = soup.get_text()
    

    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)
    
    return text[:3000]  # Limiter à 3000 caractères pour Gemini ! IMPORTANT !


def generate_title_and_description(url: str, article_content: str):
    """Utilise Gemini pour générer un titre et une description pertinents"""
    try:
        import json
        import re
        
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        prompt = f"""Tu es un assistant qui résume des articles web de manière concise et pertinente.

URL: {url}

Contenu de la page:
{article_content}

INSTRUCTIONS STRICTES:
1. Génère un titre COURT (3-8 mots maximum) qui capture l'essence de l'article
2. Génère une description CONCISE (1-2 phrases, max 150 caractères) 
3. Extrait 2-4 CATÉGORIES GÉNÉRALES (pas de mots spécifiques). Exemples de bonnes catégories:
   - Technologie: backend, frontend, devops, cloud, mobile, web, ia, data
   - Développement: tutorial, guide, documentation, tips
   - Domaine: software, hardware, design, business, productivity
   - Thème: security, performance, architecture, testing
4. Sois DIRECT et FACTUEL, pas de formulations marketing
5. Les tags doivent être GÉNÉRIQUES et RÉUTILISABLES (pas de noms propres, pas de mots trop spécifiques)

IMPORTANT: Réponds UNIQUEMENT avec ce JSON (sans ```json ni backticks):
{{"title": "votre titre ici", "description": "votre description ici", "tags": ["categorie1", "categorie2", "categorie3"]}}"""
        
        response = model.generate_content(prompt)
        print(f"Gemini raw response: {response.text}")
        
        response_text = response.text.strip()
        
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*', '', response_text)
        
        result = json.loads(response_text)
        print(f"Gemini parsed result: {result}")
        return result
    except json.JSONDecodeError as e:
        print(f"Erreur parsing JSON: {e}")
        print(f"Raw text: {response.text if 'response' in locals() else 'N/A'}")
        try:
            import ast
            cleaned = response_text.replace('\\"', '"').replace("'", '"')
            result = json.loads(cleaned)
            return result
        except:
            print(f"Article content preview: {article_content[:200]}")
            return None
    except Exception as e:
        print(f"Erreur Gemini: {e}")
        print(f"Article content preview: {article_content[:200]}")
        return None


def scrape_with_playwright(url: str) -> str:
    """Scrape une page dynamique avec Playwright (pour Twitter/X, etc.)"""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = context.new_page()
            
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            time.sleep(3)
            
            html_content = page.content()
            browser.close()
            return html_content
    except Exception as e:
        print(f"Erreur Playwright: {e}")
        return None


def generate_resource_metadata(url: str, article_content: str, custom_description: str = None):
    """Génère des métadonnées simples pour une ressource (repo, software, tool)"""
    try:
        import json
        import re
        
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Si une description personnalisée est fournie, on l'utilise
        desc_info = f"\nDescription fournie par l'utilisateur: {custom_description}" if custom_description else ""
        
        prompt = f"""Tu es un assistant qui catégorise des ressources techniques (repos GitHub, software, outils, etc.).

URL: {url}{desc_info}

Contenu de la page:
{article_content[:1000]}

INSTRUCTIONS:
1. Génère un titre TRÈS SIMPLE et COURT (3-6 mots max) qui identifie la ressource
   Exemples: "Repo GitHub Rust", "VSCode Extension", "PostgreSQL Database", "Docker Tool"
2. Génère une description CONCISE (1 phrase courte, max 100 caractères)
3. Attribue 1-3 catégories GÉNÉRIQUES parmi:
   - Type: repo, tool, software, library, framework, extension
   - Techno: backend, frontend, database, devops, cloud, mobile
   - Domaine: development, productivity, security, data, ai

IMPORTANT: Réponds UNIQUEMENT avec ce JSON (sans ```json ni backticks):
{{"title": "titre simple", "description": "description courte", "tags": ["categorie1", "categorie2"]}}"""
        
        response = model.generate_content(prompt)
        print(f"Gemini resource response: {response.text}")
        
        # Extraire le JSON
        response_text = response.text.strip()
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*', '', response_text)
        
        result = json.loads(response_text)
        print(f"Gemini resource result: {result}")
        return result
    except Exception as e:
        print(f"Erreur Gemini resource: {e}")
        return None


@app.get("/")
def read_root():
    return {"message": "Knowledge Ingester is running!"}


@app.post("/ingest/", response_model=models.LinkRead)
def ingest_link(link: models.LinkCreate, session: Session = Depends(get_session)):
    # Déterminer si on doit use Playwright (sites JS comme twitter)
    use_playwright = any(domain in link.url for domain in ["twitter.com", "x.com", "instagram.com"])
    
    html_content = None
    
    if use_playwright:
        print(f"Using Playwright for: {link.url}")
        html_content = scrape_with_playwright(link.url)
        
        if not html_content:
            print("Playwright failed, trying requests as fallback...")
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.get(link.url, timeout=10, headers=headers)
                response.raise_for_status()
                html_content = response.content
            except:
                # Si les deux échouent, on génère du contenu minimal avec Gemini basé sur l'URL
                print("Both Playwright and requests failed, using URL-based generation")
                html_content = f"<html><body><p>URL: {link.url}</p></body></html>".encode()
    else:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(link.url, timeout=10, headers=headers)
            response.raise_for_status()
            html_content = response.content
        except requests.RequestException as e:
            raise HTTPException(status_code=400, detail=f"Could not fetch URL: {e}")

    article_content = extract_article_content(html_content)
    
    print(f"URL: {link.url}")
    print(f"Article content length: {len(article_content)}")
    
    # Générer titre/description avec Gemini
    # Pour les ressources on utilise un prompt plus simple
    if link.resource_type == "resource":
        ai_result = generate_resource_metadata(link.url, article_content, link.description)
    else:
        ai_result = generate_title_and_description(link.url, article_content)
    
    if ai_result:
        title = ai_result.get("title")
        description = ai_result.get("description")
        tags = ai_result.get("tags", [])
        print(f"AI generated - Title: {title}, Description: {description}")
    else:
        # Fallback sur la méthode classique si Gemini échoue
        soup = BeautifulSoup(html_content, "html.parser")
        title = soup.title.string if soup.title else "No title found"
        description_tag = soup.find("meta", attrs={"name": "description"})
        description = description_tag["content"] if description_tag else "No description"
        tags = ["web"]
        print(f"Fallback - Title: {title}, Description: {description}")

    db_link = models.Link(
        url=link.url,
        title=title,
        description=description,
        tags=tags,
        source=link.source,
        resource_type=link.resource_type
    )
    
    db_link = crud.create_link(session=session, link=db_link)
    return db_link


@app.get("/links/", response_model=List[models.LinkRead])
def read_links(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    links = crud.get_links(session, skip=skip, limit=limit)
    return links


@app.get("/links/{link_id}", response_model=models.LinkRead)
def read_link(link_id: int, session: Session = Depends(get_session)):
    db_link = crud.get_link_by_id(session, link_id=link_id)
    if db_link is None:
        raise HTTPException(status_code=404, detail="Link not found")
    return db_link


@app.delete("/links/{link_id}")
def delete_link(link_id: int, session: Session = Depends(get_session)):
    success = crud.delete_link(session, link_id=link_id)
    if not success:
        raise HTTPException(status_code=404, detail="Link not found")
    return {"message": "Link deleted successfully"}
