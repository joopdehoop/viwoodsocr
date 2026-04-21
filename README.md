# viwoodsocr

OCR PDF's van de Viwoods AI Paper Mini en sla de herkende tekst op in een doorzoekbare PDF.

## Starter template (MVC)

Dit project bevat een starter-opzet met:

- **Model**: document- en OCR-datamodellen
- **View**: eenvoudige Windows GUI met `tkinter`
- **Controller**: scan- en exportflow
- **Services**:
  - PDF-rendering
  - Searchable-PDF export
  - Provider-abstractie voor 3 AI API's:
    - OpenAI
    - Azure Document Intelligence
    - Google Vision / Document AI

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

## Status

- De MVC-structuur en GUI-flow zijn aanwezig.
- Provider-klassen bevatten placeholders (`TODO`) voor echte API-calls.
- Export naar searchable PDF is als basis geïmplementeerd via een onzichtbare tekstlaag.
