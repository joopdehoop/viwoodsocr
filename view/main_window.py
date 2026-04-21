import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from controller.app_controller import AppController
from controller.export_controller import ExportController
from controller.ocr_controller import OCRController
from services.document_file_namer import DocumentFileNamer
from services.job_queue import JobQueue
from services.pdf_renderer import PDFRenderer
from services.searchable_pdf_writer import SearchablePDFWriter
from services.secrets_loader import SecretsLoader


class MainWindow:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Viwoods OCR Scanner")
        self.root.geometry("860x580")

        self.secrets = SecretsLoader()
        self.app_controller = AppController(self.secrets)
        self.ocr_controller = OCRController(PDFRenderer())
        self.export_controller = ExportController(SearchablePDFWriter())
        self.file_namer = DocumentFileNamer(self.secrets)
        self.jobs = JobQueue(max_workers=1)

        self.selected_pdfs: list[Path] = []
        self.scan_result = None
        self.scan_future = None

        self.provider_var = tk.StringVar(value="openai")
        self.language_var = tk.StringVar(value="nl")
        self.dpi_var = tk.IntVar(value=300)
        self.status_var = tk.StringVar(value="Klaar")

        self._build_ui()

    def _build_ui(self) -> None:
        top = ttk.Frame(self.root, padding=12)
        top.pack(fill="x")

        self.choose_btn = ttk.Button(top, text="Kies PDF(s)", command=self.choose_pdfs)
        self.choose_btn.pack(side="left")

        self.choose_folder_btn = ttk.Button(top, text="Kies map", command=self.choose_folder)
        self.choose_folder_btn.pack(side="left", padx=(6, 0))

        ttk.Label(top, text="  Provider:").pack(side="left")
        ttk.Combobox(top, textvariable=self.provider_var, values=["openai", "azure", "google"], width=10, state="readonly").pack(side="left")

        ttk.Label(top, text="  Taal:").pack(side="left")
        ttk.Entry(top, textvariable=self.language_var, width=6).pack(side="left")

        ttk.Label(top, text="  DPI:").pack(side="left")
        ttk.Spinbox(top, from_=150, to=600, increment=50, textvariable=self.dpi_var, width=6).pack(side="left")

        self.scan_btn = ttk.Button(top, text="Scannen + auto opslaan", command=self.scan)
        self.scan_btn.pack(side="left", padx=8)

        self.progress = ttk.Progressbar(self.root, mode="determinate")
        self.progress.pack(fill="x", padx=12, pady=(8, 4))

        ttk.Label(self.root, textvariable=self.status_var).pack(anchor="w", padx=12)

        self.text = tk.Text(self.root, wrap="word")
        self.text.pack(fill="both", expand=True, padx=12, pady=12)

    def _set_busy(self, busy: bool) -> None:
        state = "disabled" if busy else "normal"
        self.scan_btn.config(state=state)
        self.choose_btn.config(state=state)
        self.choose_folder_btn.config(state=state)

    def choose_pdfs(self) -> None:
        paths = filedialog.askopenfilenames(filetypes=[("PDF", "*.pdf")])
        if paths:
            self.selected_pdfs = [Path(path) for path in paths]
            self.status_var.set(f"Gekozen: {len(self.selected_pdfs)} PDF-bestanden")

    def choose_folder(self) -> None:
        folder = filedialog.askdirectory()
        if not folder:
            return
        base = Path(folder)
        pdfs = sorted([*base.glob("*.pdf"), *base.glob("*.PDF")])
        if not pdfs:
            messagebox.showwarning("Geen PDF", "In deze map zijn geen PDF-bestanden gevonden.")
            return
        self.selected_pdfs = pdfs
        self.status_var.set(f"Map gekozen: {base} ({len(self.selected_pdfs)} PDF-bestanden)")

    def scan(self) -> None:
        if not self.selected_pdfs:
            messagebox.showwarning("Geen bestand", "Kies eerst één of meerdere PDF-bestanden, of een map.")
            return
        try:
            provider = self.app_controller.build_provider(self.provider_var.get())
            config = self.app_controller.make_config(
                self.provider_var.get(),
                self.language_var.get(),
                dpi=int(self.dpi_var.get()),
            )

            self._set_busy(True)
            self.status_var.set("Batch scan gestart...")
            self.text.delete("1.0", tk.END)
            self.progress["value"] = 0
            self.scan_future = self.jobs.submit(self._scan_batch, list(self.selected_pdfs), provider, config)
            self.root.after(100, self._poll_scan_future)
        except Exception as exc:
            messagebox.showerror("Scan fout", str(exc))

    def _scan_batch(self, pdf_paths: list[Path], provider, config) -> list[tuple[Path, Path, str]]:
        summary: list[tuple[Path, Path, str]] = []
        total_files = len(pdf_paths)

        for file_index, pdf_path in enumerate(pdf_paths, start=1):
            def on_progress(done: int, total: int):
                def update():
                    base_progress = (file_index - 1) / total_files
                    page_progress = (done / total) / total_files
                    self.progress["maximum"] = 1.0
                    self.progress["value"] = base_progress + page_progress
                    self.status_var.set(
                        f"Bestand {file_index}/{total_files}: {pdf_path.name} | pagina {done}/{total}"
                    )

                self.root.after(0, update)

            result = self.ocr_controller.scan_document(pdf_path, provider, config, on_progress=on_progress)
            suggested_name = self.file_namer.suggest_filename(pdf_path, result.combined_text())
            target = self.file_namer.ensure_unique_path(pdf_path.with_name(suggested_name))
            self.export_controller.export_searchable_pdf(pdf_path, result, target)
            preview = result.combined_text()[:3000]
            summary.append((pdf_path, target, preview))

        return summary

    def _poll_scan_future(self) -> None:
        if not self.scan_future:
            return
        if not self.scan_future.done():
            self.root.after(100, self._poll_scan_future)
            return

        self._set_busy(False)
        try:
            batch_summary = self.scan_future.result()
            lines = ["Scan afgerond. Bestanden opgeslagen met LLM-bestandsnaam:\n"]
            for pdf_path, target, preview in batch_summary:
                lines.append(f"- {pdf_path.name} -> {target.name}")
                if preview:
                    lines.append("  Preview:")
                    lines.append(preview.replace("\n", " ")[:400])
                    lines.append("")
            self.text.delete("1.0", tk.END)
            self.text.insert(tk.END, "\n".join(lines))
            self.status_var.set(f"Batch voltooid ({len(batch_summary)} bestand(en))")
            self.progress["value"] = 1.0
        except Exception as exc:
            messagebox.showerror("Scan fout", str(exc))
            self.status_var.set("Scannen mislukt")

    def run(self) -> None:
        self.root.mainloop()
