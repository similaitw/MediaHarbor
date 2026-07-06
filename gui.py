import argparse
import contextlib
import io
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import downloader


class QueueWriter(io.TextIOBase):
    def __init__(self, log_queue):
        self.log_queue = log_queue

    def write(self, text):
        if text:
            self.log_queue.put(("log", text))
        return len(text)

    def flush(self):
        return None


class MediaHarborGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MediaHarbor")
        self.geometry("940x760")
        self.minsize(820, 640)

        self.log_queue = queue.Queue()
        self.worker = None

        self.mode_var = tk.StringVar(value="batch")
        self.method_var = tk.StringVar(value="yt-dlp")
        self.url_var = tk.StringVar()
        self.output_dir_var = tk.StringVar(value=str(Path.cwd() / "downloads"))
        self.title_var = tk.StringVar()
        self.from_var = tk.StringVar()
        self.to_var = tk.StringVar()
        self.quality_var = tk.StringVar(value="1")
        self.overwrite_var = tk.BooleanVar(value=False)
        self.base_url_var = tk.StringVar()
        self.begin_var = tk.StringVar(value="0")
        self.end_var = tk.StringVar()
        self.counter_prefix_var = tk.StringVar(value="6")
        self.extension_var = tk.StringVar(value=".ts")
        self.merge_var = tk.StringVar()
        self.current_file_var = tk.StringVar(value="-")
        self.percent_var = tk.StringVar(value="-")
        self.speed_var = tk.StringVar(value="-")
        self.eta_var = tk.StringVar(value="-")
        self.progress_var = tk.DoubleVar(value=0)

        self._build_ui()
        self._on_mode_change()
        self.after(100, self._drain_log_queue)

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        mode_frame = ttk.LabelFrame(self, text="Mode")
        mode_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        for column, (label, value) in enumerate(
            [
                ("Batch episodes", "batch"),
                ("Single episode", "gimy"),
                ("UB1818 video", "ub1818"),
                ("YouTube", "youtube"),
                ("Manual segments", "segments"),
            ]
        ):
            button = ttk.Radiobutton(
                mode_frame,
                text=label,
                value=value,
                variable=self.mode_var,
                command=self._on_mode_change,
            )
            button.grid(row=0, column=column, padx=10, pady=8, sticky="w")

        self.form_frame = ttk.LabelFrame(self, text="Download Settings")
        self.form_frame.grid(row=1, column=0, sticky="ew", padx=16, pady=8)
        self.form_frame.columnconfigure(1, weight=1)

        self.url_label = ttk.Label(self.form_frame, text="Gimy URL")
        self.url_entry = ttk.Entry(self.form_frame, textvariable=self.url_var)
        self.base_url_label = ttk.Label(self.form_frame, text="Base URL")
        self.base_url_entry = ttk.Entry(self.form_frame, textvariable=self.base_url_var)

        ttk.Label(self.form_frame, text="Output folder").grid(row=1, column=0, padx=10, pady=6, sticky="w")
        ttk.Entry(self.form_frame, textvariable=self.output_dir_var).grid(row=1, column=1, padx=10, pady=6, sticky="ew")
        ttk.Button(self.form_frame, text="Browse", command=self._browse_output_dir).grid(
            row=1, column=2, padx=10, pady=6
        )

        self.method_label = ttk.Label(self.form_frame, text="Method")
        self.method_combo = ttk.Combobox(
            self.form_frame,
            textvariable=self.method_var,
            values=["yt-dlp", "segments"],
            state="readonly",
            width=14,
        )

        self.title_label = ttk.Label(self.form_frame, text="Title override")
        self.title_entry = ttk.Entry(self.form_frame, textvariable=self.title_var)
        self.quality_label = ttk.Label(self.form_frame, text="Quality")
        self.quality_entry = ttk.Entry(self.form_frame, textvariable=self.quality_var, width=8)

        self.range_frame = ttk.Frame(self.form_frame)
        ttk.Label(self.range_frame, text="From").grid(row=0, column=0, padx=(0, 6), sticky="w")
        ttk.Entry(self.range_frame, textvariable=self.from_var, width=8).grid(row=0, column=1, padx=(0, 12))
        ttk.Label(self.range_frame, text="To").grid(row=0, column=2, padx=(0, 6), sticky="w")
        ttk.Entry(self.range_frame, textvariable=self.to_var, width=8).grid(row=0, column=3)

        self.manual_frame = ttk.Frame(self.form_frame)
        for column in range(6):
            self.manual_frame.columnconfigure(column, weight=1)
        ttk.Label(self.manual_frame, text="Begin").grid(row=0, column=0, padx=4, pady=4, sticky="w")
        ttk.Entry(self.manual_frame, textvariable=self.begin_var, width=8).grid(row=0, column=1, padx=4, pady=4)
        ttk.Label(self.manual_frame, text="End").grid(row=0, column=2, padx=4, pady=4, sticky="w")
        ttk.Entry(self.manual_frame, textvariable=self.end_var, width=8).grid(row=0, column=3, padx=4, pady=4)
        ttk.Label(self.manual_frame, text="Padding").grid(row=0, column=4, padx=4, pady=4, sticky="w")
        ttk.Entry(self.manual_frame, textvariable=self.counter_prefix_var, width=8).grid(row=0, column=5, padx=4, pady=4)
        ttk.Label(self.manual_frame, text="Extension").grid(row=1, column=0, padx=4, pady=4, sticky="w")
        ttk.Entry(self.manual_frame, textvariable=self.extension_var, width=8).grid(row=1, column=1, padx=4, pady=4)
        ttk.Label(self.manual_frame, text="Merge file").grid(row=1, column=2, padx=4, pady=4, sticky="w")
        ttk.Entry(self.manual_frame, textvariable=self.merge_var).grid(
            row=1, column=3, columnspan=3, padx=4, pady=4, sticky="ew"
        )

        ttk.Checkbutton(self.form_frame, text="Overwrite existing files", variable=self.overwrite_var).grid(
            row=7, column=1, padx=10, pady=6, sticky="w"
        )

        action_frame = ttk.Frame(self.form_frame)
        action_frame.grid(row=8, column=0, columnspan=3, padx=10, pady=12, sticky="ew")
        action_frame.columnconfigure(0, weight=1)
        self.start_button = ttk.Button(action_frame, text="Start Download", command=self._start_download)
        self.start_button.grid(row=0, column=1, padx=(8, 0))
        ttk.Button(action_frame, text="Clear Log", command=self._clear_log).grid(row=0, column=2, padx=(8, 0))

        progress_frame = ttk.LabelFrame(self, text="Progress")
        progress_frame.grid(row=2, column=0, sticky="ew", padx=16, pady=8)
        progress_frame.columnconfigure(1, weight=1)
        ttk.Label(progress_frame, text="Current file").grid(row=0, column=0, padx=10, pady=4, sticky="w")
        ttk.Label(progress_frame, textvariable=self.current_file_var).grid(row=0, column=1, columnspan=5, padx=10, pady=4, sticky="ew")
        ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100).grid(
            row=1, column=0, columnspan=6, padx=10, pady=6, sticky="ew"
        )
        ttk.Label(progress_frame, text="Percent").grid(row=2, column=0, padx=10, pady=4, sticky="w")
        ttk.Label(progress_frame, textvariable=self.percent_var).grid(row=2, column=1, padx=10, pady=4, sticky="w")
        ttk.Label(progress_frame, text="Speed").grid(row=2, column=2, padx=10, pady=4, sticky="w")
        ttk.Label(progress_frame, textvariable=self.speed_var).grid(row=2, column=3, padx=10, pady=4, sticky="w")
        ttk.Label(progress_frame, text="ETA").grid(row=2, column=4, padx=10, pady=4, sticky="w")
        ttk.Label(progress_frame, textvariable=self.eta_var).grid(row=2, column=5, padx=10, pady=4, sticky="w")

        log_frame = ttk.LabelFrame(self, text="Log")
        log_frame.grid(row=3, column=0, sticky="nsew", padx=16, pady=(8, 16))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        self.log_text = tk.Text(log_frame, wrap="word", height=18)
        self.log_text.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.log_text.configure(yscrollcommand=scrollbar.set)

    def _on_mode_change(self):
        for widget in [
            self.url_label,
            self.url_entry,
            self.base_url_label,
            self.base_url_entry,
            self.method_label,
            self.method_combo,
            self.title_label,
            self.title_entry,
            self.quality_label,
            self.quality_entry,
            self.range_frame,
            self.manual_frame,
        ]:
            widget.grid_forget()

        mode = self.mode_var.get()
        if mode in {"batch", "gimy", "ub1818", "youtube"}:
            label_by_mode = {
                "ub1818": "UB1818 URL",
                "youtube": "YouTube URL",
            }
            self.url_label.configure(text=label_by_mode.get(mode, "Gimy URL"))
            self.url_label.grid(row=0, column=0, padx=10, pady=6, sticky="w")
            self.url_entry.grid(row=0, column=1, columnspan=2, padx=10, pady=6, sticky="ew")
            if mode != "youtube":
                self.method_label.grid(row=2, column=0, padx=10, pady=6, sticky="w")
                self.method_combo.grid(row=2, column=1, padx=10, pady=6, sticky="w")
        else:
            self.base_url_label.grid(row=0, column=0, padx=10, pady=6, sticky="w")
            self.base_url_entry.grid(row=0, column=1, columnspan=2, padx=10, pady=6, sticky="ew")
            self.manual_frame.grid(row=4, column=1, columnspan=2, padx=6, pady=4, sticky="ew")

        if mode == "batch":
            self.range_frame.grid(row=3, column=1, padx=10, pady=6, sticky="w")
        elif mode == "gimy":
            self.title_label.grid(row=3, column=0, padx=10, pady=6, sticky="w")
            self.title_entry.grid(row=3, column=1, columnspan=2, padx=10, pady=6, sticky="ew")
        elif mode == "ub1818":
            self.title_label.grid(row=3, column=0, padx=10, pady=6, sticky="w")
            self.title_entry.grid(row=3, column=1, columnspan=2, padx=10, pady=6, sticky="ew")
            self.quality_label.grid(row=4, column=0, padx=10, pady=6, sticky="w")
            self.quality_entry.grid(row=4, column=1, padx=10, pady=6, sticky="w")
        elif mode == "youtube":
            self.title_label.grid(row=3, column=0, padx=10, pady=6, sticky="w")
            self.title_entry.grid(row=3, column=1, columnspan=2, padx=10, pady=6, sticky="ew")

    def _browse_output_dir(self):
        directory = filedialog.askdirectory(initialdir=self.output_dir_var.get() or str(Path.cwd()))
        if directory:
            self.output_dir_var.set(directory)

    def _start_download(self):
        if self.worker and self.worker.is_alive():
            return

        try:
            args = self._build_args()
        except ValueError as exc:
            messagebox.showerror("Invalid input", str(exc))
            return

        self.start_button.configure(state="disabled")
        self._reset_progress()
        self._append_log("[I] Starting download\n")
        self.worker = threading.Thread(target=self._run_download, args=(args,), daemon=True)
        self.worker.start()

    def _build_args(self):
        mode = self.mode_var.get()
        output_dir = self.output_dir_var.get().strip()
        if not output_dir:
            raise ValueError("Output folder is required.")

        if mode == "batch":
            url = self.url_var.get().strip()
            if not url:
                raise ValueError("Gimy URL is required.")
            return argparse.Namespace(
                command="batch",
                url=url,
                output_dir=output_dir,
                from_episode=self._optional_int(self.from_var.get(), "From"),
                to_episode=self._optional_int(self.to_var.get(), "To"),
                method=self.method_var.get(),
                overwrite=self.overwrite_var.get(),
                progress_callback=self._queue_progress,
                func=downloader.download_batch,
            )

        if mode == "gimy":
            url = self.url_var.get().strip()
            if not url:
                raise ValueError("Gimy URL is required.")
            return argparse.Namespace(
                command="gimy",
                url=url,
                output_dir=output_dir,
                title=self.title_var.get().strip() or None,
                method=self.method_var.get(),
                overwrite=self.overwrite_var.get(),
                progress_callback=self._queue_progress,
                func=downloader.download_gimy_page,
            )

        if mode == "ub1818":
            url = self.url_var.get().strip()
            if not url:
                raise ValueError("UB1818 URL is required.")
            return argparse.Namespace(
                command="ub1818",
                url=url,
                output_dir=output_dir,
                title=self.title_var.get().strip() or None,
                quality=self._required_int(self.quality_var.get(), "Quality"),
                method=self.method_var.get(),
                overwrite=self.overwrite_var.get(),
                progress_callback=self._queue_progress,
                func=downloader.download_ub1818_page,
            )

        if mode == "youtube":
            url = self.url_var.get().strip()
            if not url:
                raise ValueError("YouTube URL is required.")
            return argparse.Namespace(
                command="youtube",
                url=url,
                output_dir=output_dir,
                title=self.title_var.get().strip() or None,
                overwrite=self.overwrite_var.get(),
                progress_callback=self._queue_progress,
                func=downloader.download_youtube,
            )

        base_url = self.base_url_var.get().strip()
        if not base_url:
            raise ValueError("Base URL is required.")
        return argparse.Namespace(
            command="segments",
            base_url=base_url,
            begin=self._required_int(self.begin_var.get(), "Begin"),
            end=self._required_int(self.end_var.get(), "End"),
            counter_prefix=self._required_int(self.counter_prefix_var.get(), "Padding"),
            extension=self.extension_var.get().strip() or ".ts",
            output_dir=output_dir,
            merge=self.merge_var.get().strip() or None,
            overwrite=self.overwrite_var.get(),
            func=downloader.download_manual_segments,
        )

    def _optional_int(self, value, label):
        value = value.strip()
        if not value:
            return None
        return self._required_int(value, label)

    def _required_int(self, value, label):
        try:
            return int(value)
        except ValueError as exc:
            raise ValueError(f"{label} must be a number.") from exc

    def _run_download(self, args):
        writer = QueueWriter(self.log_queue)
        try:
            with contextlib.redirect_stdout(writer), contextlib.redirect_stderr(writer):
                result = args.func(args)
                exit_code = result if isinstance(result, int) else 0
                print(f"[I] Finished with exit code {exit_code}")
        except Exception as exc:
            writer.write(f"[E] {exc}\n")
        finally:
            self.log_queue.put(("done", None))

    def _drain_log_queue(self):
        while True:
            try:
                kind, payload = self.log_queue.get_nowait()
            except queue.Empty:
                break
            if kind == "log":
                self._append_log(payload)
            elif kind == "progress":
                self._apply_progress(payload)
            elif kind == "done":
                self.start_button.configure(state="normal")
        self.after(100, self._drain_log_queue)

    def _append_log(self, text):
        self.log_text.insert("end", text)
        self.log_text.see("end")

    def _clear_log(self):
        self.log_text.delete("1.0", "end")

    def _queue_progress(self, progress):
        self.log_queue.put(("progress", progress))

    def _reset_progress(self):
        self.current_file_var.set("-")
        self.percent_var.set("-")
        self.speed_var.set("-")
        self.eta_var.set("-")
        self.progress_var.set(0)

    def _apply_progress(self, progress):
        filename = Path(progress.get("filename") or "").name
        if filename:
            self.current_file_var.set(filename)

        percent = progress.get("percent") or "-"
        self.percent_var.set(percent)
        percent_float = progress.get("percent_float")
        if percent_float is not None:
            self.progress_var.set(max(0, min(100, percent_float)))
        elif progress.get("status") == "finished":
            self.progress_var.set(100)

        self.speed_var.set(progress.get("speed") or "-")
        self.eta_var.set(progress.get("eta") or "-")


if __name__ == "__main__":
    app = MediaHarborGui()
    app.mainloop()
