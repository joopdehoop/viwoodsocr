# viwoodsocr

OCR PDF's van de Viwoods AI Paper Mini en sla de herkende tekst op in een doorzoekbare PDF.

## Features

- MVC-opzet (Model/View/Controller)
- Windows GUI (`tkinter`) met:
  - meerdere PDF's kiezen
  - of een complete map met PDF's kiezen
  - provider kiezen: OpenAI / Azure / Google
  - taalhint + DPI
  - scan-progress + tekstpreview
- Secrets buiten code via `.env`
- Onzichtbare tekstlaag per pagina (woord-bbox indien provider die teruggeeft)
- Automatische output per bestand als `filename_searchable.pdf`
- OCR-woorden worden teruggeschreven op dezelfde positie op de pagina (bbox-schaal van OCR-image naar PDF), zodat zoeken de juiste woorden op de juiste plek markeert

## Installatie

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Vul daarna je secrets in `.env` in.

## Starten

```bash
python app.py
```

## Werking batch scan

1. Kies losse PDF's via **Kies PDF(s)**, of kies een map via **Kies map**.
2. Klik op **Scannen + auto opslaan**.
3. Elk bestand wordt direct opgeslagen als `originele_naam_searchable.pdf` in dezelfde map.

## Provider-notities

- **OpenAI**: gebruikt de Responses API met afbeelding-input.
- **Azure**: gebruikt Document Intelligence `prebuilt-read` en pollt async analyse.
- **Google**: gebruikt Vision API `DOCUMENT_TEXT_DETECTION` met service account credentials.

## Belangrijk

- API-calls kosten geld en vereisen geldige cloud-configuratie.
- Als een provider geen woord-bounding-boxes teruggeeft, wordt fallback gebruikt met pagina-brede onzichtbare tekstlaag.
