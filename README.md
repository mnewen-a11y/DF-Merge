# Sitemap-Analyse für Content-Migration

Dieses Repository enthält Tools zur Analyse von Sitemaps für die geplante Migration von **civic-innovation.de** und **ki-observatorium.de** in die **denkfabrik-bmas.de**.

## 📁 Repository-Struktur

```
sitemap-analyse/
├── sitemaps/
│   ├── kio-sitemap.xml
│   ├── cip-sitemap.xml
│   └── denkfabrik-sitemap.xml
├── colab_sitemap_analyzer_extended.py
└── README.md
```

## 🚀 Verwendung mit Google Colab

### Schritt 1: Neues Colab-Notebook erstellen
Gehen Sie zu https://colab.research.google.com und erstellen Sie ein neues Notebook.

### Schritt 2: Repository klonen
Führen Sie in einer Code-Zelle aus:

```python
!git clone https://github.com/IhrUsername/sitemap-analyse.git
%cd sitemap-analyse
```

### Schritt 3: Script ausführen
Kopieren Sie den Inhalt von `colab_sitemap_analyzer_extended.py` in eine neue Code-Zelle und führen Sie ihn aus.

**ODER** führen Sie das Script direkt aus:

```python
!python colab_sitemap_analyzer_extended.py
```

### Schritt 4: Ergebnisse ansehen
Die Analyse läuft automatisch und zeigt Ihnen:
- Artikelanzahl und Wortanzahl
- HIX-Score (Verständlichkeit)
- Content-Typen-Verteilung
- Thematische Cluster
- Interne Verlinkungen
- Cross-Site Überschneidungen

## 📊 Was wird analysiert?

### Basis-Metriken
- **Artikelanzahl**: Gesamtzahl der Artikel pro Sitemap
- **Wortanzahl**: Durchschnittliche Länge der Artikel
- **Komplexität**: Bewertung 1-3 basierend auf Satzlänge und Fachbegriffen
- **HIX-Score**: Hohenheimer Verständlichkeitsindex (0-100)

### Content-Struktur
- **Content-Typen**: Artikel, Projekte, Publikationen, News, etc.
- **Thematische Cluster**: Top-Keywords pro Sitemap
- **Interne Verlinkungen**: Durchschnittliche Verlinkungsdichte
- **Cross-Site Überschneidungen**: Gemeinsame Themen zwischen den Sites

## 💼 Für Migrations-Aufwandsschätzung

Die Analyse liefert Ihnen:

✅ **Content-Volumen**: Wie viel muss migriert werden?
✅ **Content-Diversität**: Welche verschiedenen Typen gibt es?
✅ **Thematische Redundanz**: Wo können Inhalte zusammengeführt werden?
✅ **Technische Abhängigkeiten**: Wie viele Redirects sind nötig?

## ⏱️ Dauer

Die komplette Analyse dauert ca. **10-15 Minuten** für alle drei Sitemaps (~481 Artikel).

## 🔄 Sitemaps aktualisieren

Falls die Sitemaps aktualisiert werden müssen:

1. Neue XML-Dateien in den `sitemaps/` Ordner legen
2. Commit & Push zu GitHub
3. In Colab: Repository neu klonen oder pullen:
   ```python
   %cd sitemap-analyse
   !git pull
   ```

## 📝 Anpassungen

Falls die Sitemap-Dateien anders heißen, passen Sie die Pfade in Zeile 14-18 der Datei `colab_sitemap_analyzer_extended.py` an:

```python
SITEMAP_FILES = {
    'KI-Observatorium': 'sitemaps/ihre-datei.xml',
    'Civic Innovation Platform': 'sitemaps/ihre-datei.xml',
    'Denkfabrik BMAS': 'sitemaps/ihre-datei.xml'
}
```

## 🆘 Support

Bei Fragen oder Problemen:
1. Prüfen Sie, ob alle Dateien im `sitemaps/` Ordner liegen
2. Stellen Sie sicher, dass Sie im richtigen Verzeichnis sind (`%cd sitemap-analyse`)
3. Prüfen Sie die Dateinamen in der SITEMAP_FILES-Konfiguration

## 📄 Lizenz

Internes Tool für BMAS-Projekte.
