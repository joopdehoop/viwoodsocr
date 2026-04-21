# viwoodsocr

OCR PDF's van de Viwoods AI Paper Mini en sla de herkende tekst op in een doorzoekbare PDF.

## Features

- MVC-opzet (Model/View/Controller)
- Windows GUI (`tkinter`) met:
  - PDF kiezen
  - Provider kiezen: OpenAI / Azure / Google
  - taalhint + DPI
  - scan-progress + tekstpreview
  - export naar searchable PDF
- Secrets buiten code via `.env`
- Onzichtbare tekstlaag per pagina (woord-bbox indien provider die teruggeeft)

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

## Provider-notities

- **OpenAI**: gebruikt de Responses API met afbeelding-input.
- **Azure**: gebruikt Document Intelligence `prebuilt-read` en pollt async analyse.
- **Google**: gebruikt Vision API `DOCUMENT_TEXT_DETECTION` met service account credentials.

## Belangrijk

- API-calls kosten geld en vereisen geldige cloud-configuratie.
- Als een provider geen woord-bounding-boxes teruggeeft, wordt fallback gebruikt met pagina-brede onzichtbare tekstlaag.
