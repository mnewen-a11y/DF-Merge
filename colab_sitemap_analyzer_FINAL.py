# SITEMAP CONTENT ANALYZER - FINALE VERSION
# Mit wissenschaftlich korrektem HIX, Content-Typen, Keywords, Verlinkungen
# Für Migrations-Aufwandsschätzung: civic-innovation.de + ki-observatorium.de → denkfabrik-bmas.de

import re
import requests
from bs4 import BeautifulSoup
import time
from collections import Counter
from urllib.parse import urlparse

print("🚀 Installiere benötigte Bibliotheken...")
import sys
!{sys.executable} -m pip install spacy pyphen --quiet
!{sys.executable} -m spacy download de_core_news_sm --quiet

import spacy
from pyphen import Pyphen
import numpy as np

print("✅ Setup abgeschlossen\n")

# Lade Sprachmodell
nlp = spacy.load('de_core_news_sm')
pyphen_de = Pyphen(lang='de_DE')

# ============================================================
# KONFIGURATION
# ============================================================

SITEMAP_FILES = {
    'KI-Observatorium': 'sitemaps/kio-sitemap.xml',
    'Civic Innovation Platform': 'sitemaps/cip-sitemap.xml',
    'Denkfabrik BMAS': 'sitemaps/denkfabrik-sitemap.xml'
}

GERMAN_STOPWORDS = set([
    'der', 'die', 'das', 'und', 'in', 'zu', 'den', 'für', 'von', 'mit', 'ist',
    'im', 'des', 'sich', 'auf', 'eine', 'auch', 'werden', 'an', 'wie', 'oder',
    'einem', 'einer', 'bei', 'nach', 'um', 'über', 'zum', 'zur', 'aus', 'dem',
    'als', 'sie', 'sind', 'noch', 'mehr', 'kann', 'wurde', 'wird', 'haben',
    'hat', 'war', 'durch', 'vor', 'bis', 'sein', 'nicht', 'nur', 'wenn', 'dass',
    'können', 'welche', 'welcher', 'welches', 'dieser', 'diese', 'dieses',
    'ihrer', 'seinem', 'seinen', 'innen', 'außen', 'sowie', 'dabei', 'dazu',
    'bereits', 'sehr', 'heute', 'immer', 'etwa', 'meist', 'gegen', 'unter',
    'zwischen', 'seit', 'während', 'denn', 'weil', 'obwohl', 'sodass',
    'worden', 'werden', 'konnte', 'sollte', 'würde', 'könnte', 'müsste',
    'alle', 'allem', 'allen', 'aller', 'alles', 'manche', 'mancher', 'manches',
    'jede', 'jeder', 'jedes', 'einige', 'einigen', 'einiger', 'einiges',
    'viele', 'vielen', 'vieler', 'vieles', 'wenige', 'wenigen', 'weniger',
    'andere', 'anderen', 'anderer', 'anderes', 'mehrere', 'mehreren', 'mehrerer',
    'ihre', 'ihrem', 'ihren', 'ihrer', 'ihres', 'unsere', 'unserem', 'unseren',
    'gibt', 'geben', 'gegeben', 'geht', 'gehen', 'gegangen', 'macht', 'machen',
    'gemacht', 'sagt', 'sagen', 'gesagt', 'kommt', 'kommen', 'gekommen',
    'steht', 'stehen', 'gestanden', 'liegt', 'liegen', 'gelegen', 'einsatz',
    'projekt', 'beschäftigten', 'arbeit', 'unternehmen'
])

# ============================================================
# HIX-FUNKTIONEN (Wissenschaftlich korrekt)
# ============================================================

def count_syllables_accurate(word):
    return len(pyphen_de.inserted(word).split('-'))

def extract_text_parameters(text):
    doc = nlp(text)
    sentences = list(doc.sents)
    num_sentences = len(sentences)
    if num_sentences == 0:
        return None
    words = [token.text for token in doc if token.is_alpha]
    num_words = len(words)
    if num_words == 0:
        return None
    asl = num_words / num_sentences
    syllable_counts = [count_syllables_accurate(word) for word in words]
    total_syllables = sum(syllable_counts)
    asw = total_syllables / num_words
    long_words = [w for w in words if len(w) > 6]
    iw = (len(long_words) / num_words) * 100
    polysyllabic = [w for w in words if count_syllables_accurate(w) >= 3]
    ms = (len(polysyllabic) / num_words) * 100
    monosyllabic = [w for w in words if count_syllables_accurate(w) == 1]
    es = (len(monosyllabic) / num_words) * 100
    polysyllables_per_30 = (len(polysyllabic) / num_sentences) * 30 if num_sentences > 0 else 0
    return {'asl': asl, 'asw': asw, 'iw': iw, 'ms': ms, 'es': es, 'polysyllables_per_30': polysyllables_per_30}

def calculate_amstad(params):
    return 180 - params['asl'] - (58.5 * params['asw'])

def calculate_wsf1(params):
    return (0.1935 * params['ms'] + 0.1672 * params['asl'] + 0.1297 * params['iw'] - 0.0327 * params['es'] - 0.875)

def calculate_smog(params):
    return 3 + np.sqrt(params['polysyllables_per_30'])

def calculate_lix(params):
    return params['asl'] + params['iw']

def scale_to_0_10(value, min_easy, max_hard, inverse=False):
    if inverse:
        if value <= min_easy:
            return 10.0
        elif value >= max_hard:
            return 0.0
        else:
            return 10.0 - ((value - min_easy) / (max_hard - min_easy)) * 10.0
    else:
        if value >= min_easy:
            return 10.0
        elif value <= max_hard:
            return 0.0
        else:
            return ((value - max_hard) / (min_easy - max_hard)) * 10.0

def calculate_hix_scientific(text):
    params = extract_text_parameters(text)
    if params is None:
        return 0
    amstad = calculate_amstad(params)
    wsf1 = calculate_wsf1(params)
    smog = calculate_smog(params)
    lix = calculate_lix(params)
    amstad_scaled = scale_to_0_10(amstad, min_easy=70, max_hard=30, inverse=False)
    wsf1_scaled = scale_to_0_10(wsf1, min_easy=6, max_hard=15, inverse=True)
    smog_scaled = scale_to_0_10(smog, min_easy=10, max_hard=18, inverse=True)
    lix_scaled = scale_to_0_10(lix, min_easy=40, max_hard=60, inverse=True)
    hix = (amstad_scaled + wsf1_scaled + smog_scaled + lix_scaled) / 4 * 2
    return hix

def interpret_hix(hix_value):
    if hix_value >= 18:
        return "Leichte Sprache / Boulevard"
    elif hix_value >= 16:
        return "Gute Webtexte / breites Publikum"
    elif hix_value >= 14:
        return "Gebildetes Publikum / Sachbücher"
    elif hix_value >= 10:
        return "Fachartikel, Behördentexte"
    else:
        return "Wissenschaftlich, expertenlastig"

# ============================================================
# CONTENT-ANALYSE FUNKTIONEN
# ============================================================

def extract_urls_from_html_sitemap(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    url_pattern = r'https?://[^\s<>"\'()]+'
    all_urls = re.findall(url_pattern, content)
    unique_urls = []
    seen = set()
    for url in all_urls:
        clean_url = url.rstrip('/')
        if 'w3.org' in url or clean_url in seen:
            continue
        seen.add(clean_url)
        unique_urls.append(url)
    return unique_urls

def filter_article_urls(urls):
    exclude_keywords = [
        '404', 'impressum', 'datenschutz', 'kontakt', 'suche', 
        'search', 'kategorie', 'category', 'tag', 'author', 'page', 'feed',
        'sitemap', 'login', 'register', 'profil', 'ueber-uns',
        '/start', '/home', 'startseite'
    ]
    article_urls = []
    for url in urls:
        if url.count('/') < 4:
            continue
        url_lower = url.lower()
        if any(keyword in url_lower for keyword in exclude_keywords):
            continue
        article_urls.append(url)
    return article_urls

def fetch_article_content(url, timeout=10):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.text
    except:
        return None

def extract_text_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form']):
        tag.decompose()
    main_content = None
    for selector in ['article', 'main', '.content', '.post', '.entry-content', '#content']:
        main_content = soup.select_one(selector)
        if main_content:
            break
    if not main_content:
        main_content = soup.body
    if not main_content:
        return ""
    text = main_content.get_text(separator=' ', strip=True)
    text = re.sub(r'\s+', ' ', text)
    return text

def detect_content_type(url, html_content, text):
    url_lower = url.lower()
    if any(keyword in url_lower for keyword in ['projekt', 'project', 'fallstudie', 'case']):
        return 'Projekt/Fallstudie'
    elif any(keyword in url_lower for keyword in ['news', 'presse', 'aktuell']):
        return 'News/Presse'
    elif any(keyword in url_lower for keyword in ['publikation', 'download', 'studie', 'bericht']):
        return 'Publikation'
    soup = BeautifulSoup(html_content, 'html.parser')
    images = len(soup.find_all('img'))
    downloads = len(soup.find_all('a', href=re.compile(r'\.(pdf|docx?|xlsx?|pptx?)$', re.I)))
    word_count = len(re.findall(r'\b\w+\b', text))
    if downloads > 2:
        return 'Publikation'
    elif word_count > 1000 and images > 3:
        return 'Artikel/Blog'
    elif word_count > 500:
        return 'Projekt/Fallstudie'
    elif word_count < 500:
        return 'Seite/Statisch'
    else:
        return 'Artikel/Blog'

def extract_ngrams(text, n=2, top_k=15):
    words = re.findall(r'\b\w+\b', text.lower())
    words = [w for w in words if w not in GERMAN_STOPWORDS and len(w) > 3]
    ngrams = []
    for i in range(len(words) - n + 1):
        ngram = ' '.join(words[i:i+n])
        ngrams.append(ngram)
    ngram_freq = Counter(ngrams)
    return ngram_freq.most_common(top_k)

def extract_keywords_combined(text, top_k=15):
    bigrams = extract_ngrams(text, n=2, top_k=10)
    words = re.findall(r'\b\w+\b', text.lower())
    words = [w for w in words if w not in GERMAN_STOPWORDS and len(w) > 5]
    technical_words = []
    for word in words:
        if any(word.endswith(suffix) for suffix in ['ung', 'heit', 'keit', 'ismus', 'ation', 'ität']):
            technical_words.append(word)
        elif len(word) > 10:
            technical_words.append(word)
    tech_freq = Counter(technical_words)
    combined = []
    for ngram, count in bigrams:
        combined.append((ngram, count, 'bigram'))
    for word, count in tech_freq.most_common(5):
        if count >= 3:
            combined.append((word, count, 'term'))
    return combined[:top_k]

def extract_internal_links(html_content, base_domain):
    soup = BeautifulSoup(html_content, 'html.parser')
    internal_links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if base_domain in href or href.startswith('/'):
            if href.startswith('/'):
                href = f"https://{base_domain}{href}"
            internal_links.append(href)
    return internal_links

def calculate_complexity(text):
    if not text:
        return 1
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if not sentences:
        return 1
    words = re.findall(r'\b\w+\b', text)
    if not words:
        return 1
    avg_sentence_length = len(words) / len(sentences)
    long_words = [w for w in words if len(w) > 10]
    long_word_ratio = len(long_words) / len(words)
    technical_patterns = [r'\w+ung\b', r'\w+heit\b', r'\w+keit\b', r'\w+ismus\b', r'\w+ation\b', r'\w+ität\b', r'\w+ieren\b']
    technical_words = 0
    for pattern in technical_patterns:
        technical_words += len(re.findall(pattern, text, re.IGNORECASE))
    technical_ratio = technical_words / len(words)
    score = 0
    if avg_sentence_length > 25:
        score += 2
    elif avg_sentence_length > 15:
        score += 1
    if long_word_ratio > 0.20:
        score += 2
    elif long_word_ratio > 0.10:
        score += 1
    if technical_ratio > 0.15:
        score += 2
    elif technical_ratio > 0.05:
        score += 1
    if score <= 1:
        return 1
    elif score <= 3:
        return 2
    else:
        return 3

def count_words(text):
    words = re.findall(r'\b\w+\b', text)
    return len(words)

# ============================================================
# HAUPTANALYSE
# ============================================================

def analyze_sitemap(filepath, sitemap_name):
    print(f"\n{'='*70}")
    print(f"📊 Analysiere: {sitemap_name}")
    print(f"{'='*70}")
    all_urls = extract_urls_from_html_sitemap(filepath)
    article_urls = filter_article_urls(all_urls)
    print(f"✓ Gefundene URLs gesamt: {len(all_urls)}")
    print(f"✓ Davon Artikel-URLs: {len(article_urls)}")
    if article_urls:
        print(f"\n📋 Erste 3 Artikel-URLs:")
        for url in article_urls[:3]:
            print(f"   - {url}")
        base_domain = urlparse(article_urls[0]).netloc
    else:
        base_domain = ""
    print(f"\n⏳ Lade Artikel herunter und analysiere...")
    print(f"   (Geschätzte Dauer: ~{len(article_urls) * 0.5 / 60:.1f} Minuten)\n")
    word_counts, complexities, hix_scores, content_types, all_keywords, internal_links_data, failed_count = [], [], [], [], [], [], 0
    for i, url in enumerate(article_urls, 1):
        if i % 5 == 0 or i == 1:
            print(f"   📝 {i}/{len(article_urls)} Artikel analysiert... ({i/len(article_urls)*100:.1f}%)")
        html = fetch_article_content(url)
        if not html:
            failed_count += 1
            continue
        text = extract_text_from_html(html)
        if len(text) < 100:
            failed_count += 1
            continue
        word_count = count_words(text)
        complexity = calculate_complexity(text)
        hix = calculate_hix_scientific(text)
        content_type = detect_content_type(url, html, text)
        keywords = extract_keywords_combined(text, top_k=15)
        internal_links = extract_internal_links(html, base_domain)
        word_counts.append(word_count)
        complexities.append(complexity)
        hix_scores.append(hix)
        content_types.append(content_type)
        all_keywords.extend([kw for kw, count, kw_type in keywords])
        internal_links_data.append({'url': url, 'link_count': len(internal_links), 'links': internal_links})
        time.sleep(0.5)
    print(f"   ✓ Fertig: {len(word_counts)}/{len(article_urls)} Artikel erfolgreich analysiert")
    if failed_count > 0:
        print(f"   ⚠️  {failed_count} Artikel konnten nicht geladen werden\n")
    else:
        print()
    keyword_freq = Counter(all_keywords)
    top_themes = keyword_freq.most_common(15)
    results = {
        'sitemap_name': sitemap_name,
        'total_articles': len(article_urls),
        'successful_analyses': len(word_counts),
        'failed_urls': failed_count,
        'avg_word_count': sum(word_counts) / len(word_counts) if word_counts else 0,
        'avg_complexity': sum(complexities) / len(complexities) if complexities else 0,
        'avg_hix': sum(hix_scores) / len(hix_scores) if hix_scores else 0,
        'complexity_distribution': {1: complexities.count(1), 2: complexities.count(2), 3: complexities.count(3)},
        'hix_scores': hix_scores,
        'content_types': Counter(content_types),
        'top_themes': top_themes,
        'internal_links': internal_links_data,
        'avg_internal_links': sum(item['link_count'] for item in internal_links_data) / len(internal_links_data) if internal_links_data else 0
    }
    return results

def analyze_thematic_overlap(all_results):
    print("\n" + "="*70)
    print("🔍 THEMATISCHE ÜBERSCHNEIDUNGEN (Cross-Site)")
    print("="*70)
    site_themes = {}
    for result in all_results:
        site_name = result['sitemap_name']
        themes = set([theme for theme, count in result['top_themes']])
        site_themes[site_name] = themes
    site_names = list(site_themes.keys())
    if len(site_names) >= 2:
        print("\n📊 Gemeinsame Themen zwischen Sitemaps:")
        for i in range(len(site_names)):
            for j in range(i+1, len(site_names)):
                site1, site2 = site_names[i], site_names[j]
                overlap = site_themes[site1] & site_themes[site2]
                if overlap:
                    print(f"\n   {site1} ↔ {site2}:")
                    print(f"   Gemeinsame Keywords: {len(overlap)}")
                    print(f"   Beispiele: {', '.join(list(overlap)[:5])}")
                else:
                    print(f"\n   {site1} ↔ {site2}: Keine signifikanten Überschneidungen")

# ============================================================
# HAUPTPROGRAMM
# ============================================================

print("🚀 SITEMAP CONTENT ANALYZER - FINALE VERSION")
print("="*70)
print("\n✅ Wissenschaftlich korrekter HIX (0-20 Skala)")
print("✅ Verbesserte Keywords (Bi-Gramme + Fachbegriffe)")
print("\nGeschätzte Dauer: 10-15 Minuten\n")

all_results = []
for name, filename in SITEMAP_FILES.items():
    try:
        result = analyze_sitemap(filename, name)
        all_results.append(result)
    except FileNotFoundError:
        print(f"❌ FEHLER: Datei '{filename}' nicht gefunden!\n")
    except Exception as e:
        print(f"❌ FEHLER bei {name}: {e}\n")

if all_results:
    print("\n" + "="*70)
    print("📈 ZUSAMMENFASSUNG DER ERGEBNISSE")
    print("="*70)
    total_articles = sum(r['total_articles'] for r in all_results)
    total_analyzed = sum(r['successful_analyses'] for r in all_results)
    print(f"\n🔢 GESAMTSTATISTIK:")
    print(f"   Gesamtanzahl Artikel: {total_articles}")
    print(f"   Erfolgreich analysiert: {total_analyzed}")
    print(f"   Fehlgeschlagen: {total_articles - total_analyzed}")
    for result in all_results:
        print(f"\n" + "="*70)
        print(f"📁 {result['sitemap_name']}")
        print("="*70)
        if result['successful_analyses'] > 0:
            print(f"\n   📊 BASIS-METRIKEN:")
            print(f"      Artikel gesamt: {result['total_articles']}")
            print(f"      Ø Wortanzahl: {result['avg_word_count']:.0f} Wörter")
            print(f"      Ø Komplexität: {result['avg_complexity']:.2f}/3")
            print(f"      Ø HIX-Score: {result['avg_hix']:.1f}/20 ({interpret_hix(result['avg_hix'])})")
            print(f"\n   📝 CONTENT-TYPEN:")
            for content_type, count in result['content_types'].most_common():
                percentage = (count / result['successful_analyses']) * 100
                print(f"      {content_type}: {count} Artikel ({percentage:.1f}%)")
            print(f"\n   🏷️  TOP-THEMEN (Bi-Gramme + Fachbegriffe):")
            for theme, count in result['top_themes'][:10]:
                print(f"      {theme}: {count}x")
            print(f"\n   🔗 INTERNE VERLINKUNGEN:")
            print(f"      Ø Links pro Artikel: {result['avg_internal_links']:.1f}")
            top_linked = sorted(result['internal_links'], key=lambda x: x['link_count'], reverse=True)[:3]
            if top_linked and top_linked[0]['link_count'] > 0:
                print(f"      Am stärksten verlinkt:")
                for item in top_linked:
                    if item['link_count'] > 0:
                        print(f"         {item['link_count']} Links: {item['url'][:60]}...")
        else:
            print(f"   ⚠️  Keine Artikel konnten analysiert werden")
    analyze_thematic_overlap(all_results)
    if total_analyzed > 0:
        total_words = sum(r['avg_word_count'] * r['successful_analyses'] for r in all_results)
        total_hix = sum(r['avg_hix'] * r['successful_analyses'] for r in all_results)
        print(f"\n" + "="*70)
        print(f"📊 GESAMTDURCHSCHNITT (alle drei Sitemaps):")
        print(f"   Ø Wortanzahl: {total_words / total_analyzed:.0f} Wörter pro Artikel")
        overall_hix = total_hix / total_analyzed
        print(f"   Ø HIX-Score: {overall_hix:.1f}/20 ({interpret_hix(overall_hix)})")
        print("="*70)
        print(f"\n💡 MIGRATIONS-HINWEISE:")
        all_content_types = set()
        for result in all_results:
            all_content_types.update(result['content_types'].keys())
        print(f"\n   Content-Typ-Diversität:")
        print(f"   → {len(all_content_types)} verschiedene Content-Typen")
        print(f"   → Empfehlung: Einheitliche Taxonomie definieren")
        avg_links_overall = sum(r['avg_internal_links'] * r['successful_analyses'] for r in all_results) / total_analyzed
        print(f"\n   Verlinkungskomplexität:")
        print(f"   → Ø {avg_links_overall:.1f} interne Links pro Artikel")
        if avg_links_overall > 5:
            print(f"   → Redirect-Strategie wichtig!")
        else:
            print(f"   → Überschaubare Redirects")
    print("\n✅ Analyse erfolgreich abgeschlossen!")
else:
    print("\n❌ Keine Sitemaps konnten analysiert werden.")
