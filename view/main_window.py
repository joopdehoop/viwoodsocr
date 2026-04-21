import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from controller.app_controller import AppController
from controller.export_controller import ExportController
from controller.ocr_controller import OCRController
from services.job_queue import JobQueue
from services.pdf_renderer import PDFRenderer
from services.searchable_pdf_writer import SearchablePDFWriter
from services.secrets_loader import SecretsLoader


class MainWindow:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Viwoods OCR Scanner")
        self.root.geometry("760x560")

        self.app_controller = AppController(SecretsLoader())
        self.ocr_controller = OCRController(PDFRenderer())
        self.export_controller = ExportController(SearchablePDFWriter())
        self.jobs = JobQueue(max_workers=1)

        self.selected_pdf: Path | None = None
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

        self.choose_btn = ttk.Button(top, text="Kies PDF", command=self.choose_pdf)
        self.choose_btn.pack(side="left")

        ttk.Label(top, text="  Provider:").pack(side="left")
        ttk.Combobox(top, textvariable=self.provider_var, values=["openai", "azure", "google"], width=10, state="readonly").pack(side="left")

        ttk.Label(top, text="  Taal:").pack(side="left")
        ttk.Entry(top, textvariable=self.language_var, width=6).pack(side="left")

        ttk.Label(top, text="  DPI:").pack(side="left")
        ttk.Spinbox(top, from_=150, to=600, increment=50, textvariable=self.dpi_var, width=6).pack(side="left")

        self.scan_btn = ttk.Button(top, text="Scannen", command=self.scan)
        self.scan_btn.pack(side="left", padx=8)

        self.export_btn = ttk.Button(top, text="Exporteer searchable PDF", command=self.export_pdf)
        self.export_btn.pack(side="left")

        self.progress = ttk.Progressbar(self.root, mode="determinate")
        self.progress.pack(fill="x", padx=12, pady=(8, 4))

        ttk.Label(self.root, textvariable=self.status_var).pack(anchor="w", padx=12)

        self.text = tk.Text(self.root, wrap="word")
        self.text.pack(fill="both", expand=True, padx=12, pady=12)

    def _set_busy(self, busy: bool) -> None:
        state = "disabled" if busy else "normal"
        self.scan_btn.config(state=state)
        self.choose_btn.config(state=state)

    def choose_pdf(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if path:
            self.selected_pdf = Path(path)
            self.status_var.set(f"Gekozen: {self.selected_pdf.name}")

    def scan(self) -> None:
        if not self.selected_pdf:
            messagebox.showwarning("Geen bestand", "Kies eerst een PDF-bestand.")
            return
        try:
            provider = self.app_controller.build_provider(self.provider_var.get())
            config = self.app_controller.make_config(
                self.provider_var.get(),
                self.language_var.get(),
                dpi=int(self.dpi_var.get()),
            )

            def on_progress(done: int, total: int):
                def update():
                    self.progress["maximum"] = total
                    self.progress["value"] = done
                    self.status_var.set(f"Scannen {done}/{total}...")

                self.root.after(0, update)

            self._set_busy(True)
            self.status_var.set("Scannen gestart...")
            self.scan_future = self.jobs.submit(
                self.ocr_controller.scan_document,
                self.selected_pdf,
                provider,
                config,
                on_progress,
            )
            self.root.after(100, self._poll_scan_future)
        except Exception as exc:
            messagebox.showerror("Scan fout", str(exc))

    def _poll_scan_future(self) -> None:
        if not self.scan_future:
            return
        if not self.scan_future.done():
            self.root.after(100, self._poll_scan_future)
            return

        self._set_busy(False)
        try:
            self.scan_result = self.scan_future.result()
            self.text.delete("1.0", tk.END)
            self.text.insert(tk.END, self.scan_result.combined_text())
            self.status_var.set("Scannen voltooid")
        except Exception as exc:
            messagebox.showerror("Scan fout", str(exc))
            self.status_var.set("Scannen mislukt")

    def export_pdf(self) -> None:
        if not self.selected_pdf or not self.scan_result:
            messagebox.showwarning("Geen data", "Scan eerst een PDF voordat je exporteert.")
            return
        default_target = self.app_controller.default_output_path(self.selected_pdf)
        target = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=default_target.name)
        if not target:
            return

        try:
            output = self.export_controller.export_searchable_pdf(
                self.selected_pdf,
                self.scan_result,
                Path(target),
            )
            self.status_var.set(f"Export voltooid: {output.name}")
            messagebox.showinfo("Klaar", f"Bestand opgeslagen als:\n{output}")
        except Exception as exc:
            messagebox.showerror("Export fout", str(exc))

    def run(self) -> None:
        self.root.mainloop()
