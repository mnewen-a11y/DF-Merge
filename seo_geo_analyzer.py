# SEO + GEO + SEARCH INTENT ANALYZER
# Basierend auf Google Ranking-Systemen 2025-2026
# Helpful Content, E-E-A-T, Core Web Vitals, Local SEO, Search Intent

import sys
print("📦 Installiere Abhängigkeiten...")
!{sys.executable} -m pip install requests beautifulsoup4 spacy textstat --quiet
!{sys.executable} -m spacy download de_core_news_sm --quiet

import requests
from bs4 import BeautifulSoup
import spacy
import textstat
import re
import time
from collections import Counter
from urllib.parse import urlparse, urljoin
import json

nlp = spacy.load('de_core_news_sm')
print("✅ Setup abgeschlossen\n")

# ============================================================
# A. TECHNISCHE BASIS-SEO
# ============================================================

def analyze_technical_seo(url, soup, response):
    """Technische SEO-Signale nach Google 2026"""
    results = {}
    
    # Title
    title = soup.find('title')
    results['title'] = {
        'exists': title is not None,
        'text': title.text.strip() if title else '',
        'length': len(title.text.strip()) if title else 0,
        'optimal': 50 <= len(title.text.strip()) <= 60 if title else False
    }
    
    # Meta Description
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    desc_text = meta_desc.get('content', '') if meta_desc else ''
    results['meta_description'] = {
        'exists': meta_desc is not None,
        'text': desc_text,
        'length': len(desc_text),
        'optimal': 150 <= len(desc_text) <= 160
    }
    
    # Heading-Struktur
    headings = {}
    for i in range(1, 7):
        h_tags = soup.find_all(f'h{i}')
        headings[f'h{i}'] = {
            'count': len(h_tags),
            'texts': [h.text.strip()[:50] for h in h_tags[:3]]
        }
    results['headings'] = headings
    
    # Wortanzahl Hauptinhalt
    main_content = extract_main_content(soup)
    word_count = len(re.findall(r'\b\w+\b', main_content))
    results['word_count'] = word_count
    
    # Bilder & Alt-Texte
    images = soup.find_all('img')
    images_with_alt = [img for img in images if img.get('alt')]
    results['images'] = {
        'total': len(images),
        'with_alt': len(images_with_alt),
        'alt_ratio': len(images_with_alt) / len(images) * 100 if images else 0
    }
    
    # Links
    all_links = soup.find_all('a', href=True)
    domain = urlparse(url).netloc
    internal_links = [l for l in all_links if domain in l.get('href', '') or l.get('href', '').startswith('/')]
    external_links = [l for l in all_links if domain not in l.get('href', '') and not l.get('href', '').startswith('/') and l.get('href', '').startswith('http')]
    results['links'] = {
        'internal': len(internal_links),
        'external': len(external_links),
        'total': len(all_links)
    }
    
    # HTTPS
    results['https'] = url.startswith('https://')
    
    # Mobile-Freundlichkeit (viewport)
    viewport = soup.find('meta', attrs={'name': 'viewport'})
    results['mobile_friendly'] = viewport is not None
    
    # Ladezeit
    results['load_time'] = response.elapsed.total_seconds()
    
    # Structured Data
    structured_data = []
    # JSON-LD
    for script in soup.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(script.string)
            if isinstance(data, dict):
                structured_data.append(data.get('@type', 'Unknown'))
            elif isinstance(data, list):
                structured_data.extend([d.get('@type', 'Unknown') for d in data if isinstance(d, dict)])
        except:
            pass
    results['structured_data'] = structured_data
    
    return results

# ============================================================
# B. CONTENT QUALITÄT & E-E-A-T
# ============================================================

def analyze_content_quality(soup, main_text):
    """Content-Qualität und E-E-A-T-Indikatoren"""
    results = {}
    
    # Lesbarkeit (deutsche Formeln)
    try:
        # Flesch Reading Ease (angepasst)
        flesch = textstat.flesch_reading_ease(main_text)
        results['flesch_score'] = flesch
        results['flesch_interpretation'] = interpret_flesch(flesch)
    except:
        results['flesch_score'] = 0
        results['flesch_interpretation'] = 'Nicht berechenbar'
    
    # Named Entities (Personen, Orte, Organisationen)
    doc = nlp(main_text[:100000])  # Limit für Performance
    entities = {'PER': [], 'LOC': [], 'ORG': []}
    for ent in doc.ents:
        if ent.label_ in entities:
            entities[ent.label_].append(ent.text)
    
    results['entities'] = {
        'persons': len(set(entities['PER'])),
        'locations': len(set(entities['LOC'])),
        'organizations': len(set(entities['ORG'])),
        'examples': {
            'persons': list(set(entities['PER']))[:3],
            'locations': list(set(entities['LOC']))[:3],
            'organizations': list(set(entities['ORG']))[:3]
        }
    }
    
    # Externe Links zu Autoritäten
    all_links = soup.find_all('a', href=True)
    authority_domains = ['wikipedia.org', 'gov', 'edu', 'destatis.de', 'bundesregierung.de']
    authority_links = [l for l in all_links if any(domain in l.get('href', '').lower() for domain in authority_domains)]
    results['authority_links'] = len(authority_links)
    
    # E-A-T Signale
    eat_signals = {
        'author_box': bool(soup.find(class_=re.compile('author', re.I))),
        'about_page': bool(soup.find('a', href=re.compile(r'(about|ueber|impressum)', re.I))),
        'contact_info': bool(soup.find(text=re.compile(r'(kontakt|email|telefon)', re.I))),
        'date_published': bool(soup.find('time') or soup.find(class_=re.compile('date', re.I)))
    }
    results['eat_signals'] = eat_signals
    
    return results

# ============================================================
# C. SEARCH INTENT KLASSIFIKATION
# ============================================================

def classify_search_intent(soup, main_text):
    """Google Quality Rater Guidelines Intent-Klassifikation"""
    results = {}
    
    # Extrahiere Haupt-Keyword aus Title + H1
    title = soup.find('title')
    h1 = soup.find('h1')
    title_text = title.text if title else ''
    h1_text = h1.text if h1 else ''
    main_keyword = f"{title_text} {h1_text}".lower()
    
    results['estimated_keyword'] = title_text[:60] if title_text else 'Nicht erkennbar'
    
    # Intent-Klassifikation
    intents = {
        'know_simple': 0,
        'know_complex': 0,
        'do_transactional': 0,
        'website_navigational': 0,
        'visit_in_person': 0
    }
    
    # Know Simple: Fakten, Definitionen
    if any(word in main_keyword for word in ['was ist', 'definition', 'bedeutung', 'erkl']):
        intents['know_simple'] += 3
    
    # Know Complex: Tiefere Informationen
    if any(word in main_keyword for word in ['wie', 'warum', 'ratgeber', 'anleitung', 'guide']):
        intents['know_complex'] += 3
    
    # Do/Transactional: Handlungen, Käufe
    if any(word in main_keyword for word in ['kaufen', 'bestellen', 'download', 'anmelden', 'buchen']):
        intents['do_transactional'] += 3
    
    # Website/Navigational: Brand-Suchen
    if any(word in main_keyword for word in ['login', 'kontakt', 'impressum', 'startseite']):
        intents['website_navigational'] += 3
    
    # Visit-in-person: Lokale Suchen
    if any(word in main_keyword for word in ['in', 'bei', 'nähe', 'adresse', 'öffnungszeiten']):
        intents['visit_in_person'] += 3
    
    # Content-basierte Klassifikation
    text_lower = main_text[:2000].lower()
    
    # Know: Viele Erklärungen
    if len(re.findall(r'\b(ist|sind|bedeutet|bezeichnet|definiert)\b', text_lower)) > 5:
        intents['know_complex'] += 2
    
    # Do: Call-to-Actions
    if len(re.findall(r'\b(jetzt|hier|klicken|bestellen|kaufen|anmelden)\b', text_lower)) > 3:
        intents['do_transactional'] += 2
    
    # Visit: Lokale Infos
    if len(re.findall(r'\b(adresse|telefon|öffnungszeiten|standort|weg)\b', text_lower)) > 3:
        intents['visit_in_person'] += 2
    
    # Primärer Intent
    primary_intent = max(intents, key=intents.get)
    
    # Sekundär-Intents
    secondary_intents = [k for k, v in sorted(intents.items(), key=lambda x: x[1], reverse=True)[1:3] if v > 0]
    
    results['primary_intent'] = primary_intent.replace('_', ' ').title()
    results['secondary_intents'] = [s.replace('_', ' ').title() for s in secondary_intents]
    results['confidence_scores'] = {k.replace('_', ' ').title(): v for k, v in intents.items()}
    
    return results

# ============================================================
# D. GEO / LOCAL SEO
# ============================================================

def analyze_geo_local(soup, main_text):
    """Local SEO & GEO-Signale"""
    results = {}
    
    # NAP (Name, Address, Phone) Erkennung
    phone_pattern = r'(\+49|0)\s?(\d{2,5})[\s/-]?\d{3,8}'
    phones = re.findall(phone_pattern, main_text)
    results['phone_found'] = len(phones) > 0
    results['phone_count'] = len(phones)
    
    # Adressen (einfache Heuristik)
    address_pattern = r'\d{5}\s+[A-ZÄÖÜ][a-zäöüß]+'
    addresses = re.findall(address_pattern, main_text)
    results['address_found'] = len(addresses) > 0
    results['address_count'] = len(addresses)
    
    # Öffnungszeiten
    opening_hours = bool(re.search(r'(öffnungszeiten|geöffnet|montag|dienstag)', main_text, re.I))
    results['opening_hours_found'] = opening_hours
    
    # Google Maps Embed
    maps_embed = bool(soup.find('iframe', src=re.compile(r'google.com/maps', re.I)))
    results['google_maps_embed'] = maps_embed
    
    # Lokale Keywords
    german_cities = ['berlin', 'hamburg', 'münchen', 'köln', 'frankfurt', 'stuttgart', 'düsseldorf', 'dortmund', 'essen', 'leipzig', 'bremen', 'dresden', 'hannover', 'nürnberg', 'duisburg']
    text_lower = main_text.lower()
    found_cities = [city for city in german_cities if city in text_lower]
    results['local_keywords'] = {
        'cities_found': found_cities[:5],
        'city_count': len(found_cities),
        'has_local_context': len(found_cities) > 0
    }
    
    # Local Business Schema
    local_schemas = ['LocalBusiness', 'Restaurant', 'Store', 'Organization', 'Place']
    results['local_schema_found'] = False
    for script in soup.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(script.string)
            if isinstance(data, dict) and data.get('@type') in local_schemas:
                results['local_schema_found'] = True
                results['local_schema_type'] = data.get('@type')
        except:
            pass
    
    # GEO-Score (0-10)
    geo_score = 0
    if results['phone_found']:
        geo_score += 2
    if results['address_found']:
        geo_score += 2
    if results['opening_hours_found']:
        geo_score += 1
    if results['google_maps_embed']:
        geo_score += 2
    if results['local_keywords']['has_local_context']:
        geo_score += 2
    if results.get('local_schema_found'):
        geo_score += 1
    
    results['geo_score'] = min(geo_score, 10)
    
    return results

# ============================================================
# E. ZUSÄTZLICHE MODERNE ANALYSEN
# ============================================================

def analyze_modern_seo(soup, main_text):
    """2026-relevante SEO-Faktoren"""
    results = {}
    
    # 1. AI Overview Gefährdung
    first_para = main_text[:500]
    direct_answer_patterns = ['ist', 'sind', 'bedeutet', 'definition']
    ai_risk_score = sum(1 for p in direct_answer_patterns if p in first_para.lower())
    results['ai_overview_risk'] = 'Hoch' if ai_risk_score >= 3 else 'Mittel' if ai_risk_score >= 2 else 'Niedrig'
    
    # 2. Brand Signals
    brand_indicators = {
        'logo': bool(soup.find('img', alt=re.compile(r'logo', re.I))),
        'brand_mention': len(re.findall(r'\b[A-ZÄÖÜ][a-zäöüß]{2,}\s(GmbH|AG|eV|e\.V\.)\b', main_text)),
        'social_links': len([l for l in soup.find_all('a', href=True) if any(s in l.get('href', '') for s in ['facebook', 'twitter', 'linkedin', 'instagram'])])
    }
    results['brand_signals'] = brand_indicators
    
    # 3. UX-Elemente
    ux_elements = {
        'lists': len(soup.find_all(['ul', 'ol'])),
        'tables': len(soup.find_all('table')),
        'images': len(soup.find_all('img')),
        'videos': len(soup.find_all(['video', 'iframe']))
    }
    results['ux_elements'] = ux_elements
    
    # 4. Keyword Density (vermeidet Stuffing)
    doc = nlp(main_text[:10000])
    words = [token.text.lower() for token in doc if token.is_alpha and len(token.text) > 3]
    if words:
        word_freq = Counter(words)
        top_word = word_freq.most_common(1)[0]
        density = (top_word[1] / len(words)) * 100
        results['keyword_density'] = {
            'top_word': top_word[0],
            'density_percent': round(density, 2),
            'stuffing_risk': 'Ja' if density > 3 else 'Nein'
        }
    
    return results

# ============================================================
# HILFSFUNKTIONEN
# ============================================================

def extract_main_content(soup):
    """Extrahiert Hauptinhalt ohne Nav/Footer"""
    for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
        tag.decompose()
    
    main = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile('content', re.I))
    if main:
        return main.get_text(separator=' ', strip=True)
    return soup.get_text(separator=' ', strip=True)

def interpret_flesch(score):
    """Interpretiert Flesch Reading Ease"""
    if score >= 80:
        return "Sehr leicht"
    elif score >= 60:
        return "Leicht"
    elif score >= 40:
        return "Mittel"
    elif score >= 20:
        return "Schwer"
    else:
        return "Sehr schwer"

# ============================================================
# HAUPT-ANALYSE-FUNKTION
# ============================================================

def analyze_url(url):
    """Führt vollständige SEO + GEO Analyse durch"""
    print(f"\n{'='*70}")
    print(f"🔍 ANALYSIERE: {url}")
    print(f"{'='*70}\n")
    
    try:
        # Seite abrufen
        print("📥 Lade Seite...")
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        main_text = extract_main_content(soup)
        
        # Analysen durchführen
        print("⚙️  Führe Analysen durch...\n")
        
        tech_seo = analyze_technical_seo(url, soup, response)
        content_quality = analyze_content_quality(soup, main_text)
        search_intent = classify_search_intent(soup, main_text)
        geo_local = analyze_geo_local(soup, main_text)
        modern_seo = analyze_modern_seo(soup, main_text)
        
        # Gesamt-Score berechnen
        score = calculate_overall_score(tech_seo, content_quality, geo_local)
        
        # Report ausgeben
        print_report(url, score, tech_seo, content_quality, search_intent, geo_local, modern_seo)
        
    except Exception as e:
        print(f"❌ FEHLER: {e}")

def calculate_overall_score(tech, content, geo):
    """Berechnet Gesamt-SEO-Score (0-100)"""
    score = 0
    
    # Technisch (40 Punkte)
    if tech['title']['optimal']:
        score += 10
    if tech['meta_description']['optimal']:
        score += 10
    if tech['https']:
        score += 5
    if tech['mobile_friendly']:
        score += 5
    if tech['word_count'] >= 300:
        score += 10
    
    # Content (40 Punkte)
    if content.get('flesch_score', 0) >= 40:
        score += 10
    if content['entities']['persons'] + content['entities']['organizations'] >= 3:
        score += 10
    if content['authority_links'] > 0:
        score += 10
    if sum(content['eat_signals'].values()) >= 3:
        score += 10
    
    # GEO (20 Punkte)
    score += geo['geo_score'] * 2
    
    return min(score, 100)

def print_report(url, score, tech, content, intent, geo, modern):
    """Druckt übersichtlichen Report"""
    print("="*70)
    print("📊 SEO + GEO ANALYSE-REPORT")
    print("="*70)
    
    print(f"\n🎯 GESAMT-SCORE: {score}/100")
    if score >= 80:
        print("   ✅ Sehr gut optimiert")
    elif score >= 60:
        print("   ⚠️  Gut, aber Verbesserungspotenzial")
    elif score >= 40:
        print("   ⚠️  Durchschnittlich, deutliche Optimierung nötig")
    else:
        print("   ❌ Schwach optimiert, grundlegende Überarbeitung erforderlich")
    
    print("\n" + "-"*70)
    print("🔧 TECHNISCHE SEO")
    print("-"*70)
    print(f"Title: {'✓' if tech['title']['exists'] else '✗'} ({tech['title']['length']} Zeichen) {'[OPTIMAL]' if tech['title']['optimal'] else ''}")
    print(f"   → {tech['title']['text'][:60]}")
    print(f"Meta Description: {'✓' if tech['meta_description']['exists'] else '✗'} ({tech['meta_description']['length']} Zeichen)")
    print(f"H1: {tech['headings']['h1']['count']} vorhanden")
    if tech['headings']['h1']['texts']:
        print(f"   → {tech['headings']['h1']['texts'][0]}")
    print(f"Wortanzahl: {tech['word_count']}")
    print(f"Bilder mit Alt: {tech['images']['with_alt']}/{tech['images']['total']} ({tech['images']['alt_ratio']:.1f}%)")
    print(f"Links: {tech['links']['internal']} intern, {tech['links']['external']} extern")
    print(f"HTTPS: {'✓' if tech['https'] else '✗'}")
    print(f"Mobile-Friendly: {'✓' if tech['mobile_friendly'] else '✗'}")
    print(f"Ladezeit: {tech['load_time']:.2f}s")
    if tech['structured_data']:
        print(f"Structured Data: {', '.join(tech['structured_data'])}")
    
    print("\n" + "-"*70)
    print("📝 CONTENT-QUALITÄT & E-E-A-T")
    print("-"*70)
    print(f"Lesbarkeit (Flesch): {content.get('flesch_score', 0):.1f} ({content.get('flesch_interpretation', 'N/A')})")
    print(f"Named Entities:")
    print(f"   Personen: {content['entities']['persons']}")
    print(f"   Organisationen: {content['entities']['organizations']}")
    print(f"   Orte: {content['entities']['locations']}")
    print(f"Autoritäts-Links: {content['authority_links']}")
    print(f"E-A-T Signale:")
    for signal, present in content['eat_signals'].items():
        print(f"   {signal}: {'✓' if present else '✗'}")
    
    print("\n" + "-"*70)
    print("🎯 SEARCH INTENT KLASSIFIKATION")
    print("-"*70)
    print(f"Geschätztes Keyword: {intent['estimated_keyword']}")
    print(f"Primärer Intent: {intent['primary_intent']}")
    if intent['secondary_intents']:
        print(f"Sekundäre Intents: {', '.join(intent['secondary_intents'])}")
    print(f"Confidence Scores:")
    for int_type, score in intent['confidence_scores'].items():
        print(f"   {int_type}: {score}")
    
    print("\n" + "-"*70)
    print("📍 GEO / LOCAL SEO")
    print("-"*70)
    print(f"GEO-Score: {geo['geo_score']}/10")
    print(f"Telefon gefunden: {'✓' if geo['phone_found'] else '✗'} ({geo['phone_count']})")
    print(f"Adresse gefunden: {'✓' if geo['address_found'] else '✗'} ({geo['address_count']})")
    print(f"Öffnungszeiten: {'✓' if geo['opening_hours_found'] else '✗'}")
    print(f"Google Maps: {'✓' if geo['google_maps_embed'] else '✗'}")
    if geo['local_keywords']['cities_found']:
        print(f"Lokale Keywords: {', '.join(geo['local_keywords']['cities_found'])}")
    if geo.get('local_schema_found'):
        print(f"Local Business Schema: ✓ ({geo.get('local_schema_type', 'N/A')})")
    
    print("\n" + "-"*70)
    print("🚀 MODERNE SEO-FAKTOREN (2026)")
    print("-"*70)
    print(f"AI Overview Risiko: {modern['ai_overview_risk']}")
    print(f"Brand Signals:")
    print(f"   Logo: {'✓' if modern['brand_signals']['logo'] else '✗'}")
    print(f"   Markenerwähnungen: {modern['brand_signals']['brand_mention']}")
    print(f"   Social Links: {modern['brand_signals']['social_links']}")
    print(f"UX-Elemente:")
    print(f"   Listen: {modern['ux_elements']['lists']}, Tabellen: {modern['ux_elements']['tables']}")
    print(f"   Bilder: {modern['ux_elements']['images']}, Videos: {modern['ux_elements']['videos']}")
    if 'keyword_density' in modern:
        kd = modern['keyword_density']
        print(f"Top Keyword: '{kd['top_word']}' ({kd['density_percent']}%) - Stuffing: {kd['stuffing_risk']}")
    
    print("\n" + "="*70)
    print("💡 TOP HANDLUNGSEMPFEHLUNGEN")
    print("="*70)
    
    recommendations = []
    
    if not tech['title']['optimal']:
        recommendations.append(f"Title optimieren (aktuell {tech['title']['length']} Zeichen, optimal: 50-60)")
    if not tech['meta_description']['optimal']:
        recommendations.append(f"Meta Description optimieren (aktuell {tech['meta_description']['length']} Zeichen, optimal: 150-160)")
    if tech['word_count'] < 300:
        recommendations.append(f"Content erweitern (aktuell {tech['word_count']} Wörter, min. 300 empfohlen)")
    if tech['images']['alt_ratio'] < 80:
        recommendations.append("Alt-Texte für alle Bilder hinzufügen")
    if content['authority_links'] == 0:
        recommendations.append("Links zu Autoritätsquellen hinzufügen (Wikipedia, .gov, .edu)")
    if sum(content['eat_signals'].values()) < 3:
        recommendations.append("E-A-T stärken: Autor nennen, About-Seite, Impressum verlinken")
    if geo['geo_score'] < 5 and intent['primary_intent'] == 'Visit In Person':
        recommendations.append("Local SEO verbessern: NAP-Daten, Google Maps, Schema.org LocalBusiness")
    if not tech['structured_data']:
        recommendations.append("Structured Data (Schema.org) implementieren")
    
    for i, rec in enumerate(recommendations[:8], 1):
        print(f"{i}. {rec}")
    
    print("\n" + "="*70)
    print("✅ Analyse abgeschlossen")
    print("="*70)

# ============================================================
# BEISPIEL-VERWENDUNG
# ============================================================

print("\n🎯 SEO + GEO ANALYZER bereit!")
print("="*70)
print("\nVerwendung:")
print("  analyze_url('https://example.com/seite')")
print("\n")

# Demo-Analyse (auskommentiert - Sie können Ihre URL einsetzen)
# analyze_url('https://www.ki-observatorium.de/rubriken/wissen/einsatz-von-ki-in-kmu-steigt-aber-die-herausforderungen-fuer-die-arbeitswelt-bleiben')
