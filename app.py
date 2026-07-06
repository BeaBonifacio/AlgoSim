import random
import tkinter as tk
from tkinter import ttk, messagebox

from process import Process
from scheduler import Scheduler

# ----------------------------
# Process row helper widget
# ----------------------------
class ProcessRow:
    def __init__(self, parent, on_remove=None):
        self.on_remove = on_remove
        self.frame = tk.Frame(parent, bg="#fff5fa")
        for col in range(5):
            self.frame.grid_columnconfigure(col, weight=1, uniform="input_cols")

        self.pid_entry = tk.Entry(self.frame, width=12, justify="center", bg="#fffafd", fg="#7a2459", insertbackground="#7a2459", relief="solid", bd=1)
        self.arrival_entry = tk.Entry(self.frame, width=12, justify="center", bg="#fffafd", fg="#7a2459", insertbackground="#7a2459", relief="solid", bd=1)
        self.burst_entry = tk.Entry(self.frame, width=12, justify="center", bg="#fffafd", fg="#7a2459", insertbackground="#7a2459", relief="solid", bd=1)
        self.priority_entry = tk.Entry(self.frame, width=12, justify="center", bg="#fffafd", fg="#7a2459", insertbackground="#7a2459", relief="solid", bd=1)
        self.remove_button = ttk.Button(self.frame, text="Remove", command=self._handle_remove)

        self.pid_entry.grid(row=0, column=0, padx=3, pady=3, sticky="ew")
        self.arrival_entry.grid(row=0, column=1, padx=3, pady=3, sticky="ew")
        self.burst_entry.grid(row=0, column=2, padx=3, pady=3, sticky="ew")
        self.priority_entry.grid(row=0, column=3, padx=3, pady=3, sticky="ew")
        self.remove_button.grid(row=0, column=4, padx=3, pady=3, sticky="ew")

    def grid(self, row: int):
        self.frame.grid(row=row, column=0, columnspan=5, sticky="ew", padx=0, pady=2)

    def _handle_remove(self) -> None:
        if self.on_remove:
            self.on_remove()

    def get_process(self) -> Process:
        pid = self.pid_entry.get().strip()
        if not pid:
            raise ValueError("Process ID cannot be empty")

        arrival_time = int(self.arrival_entry.get().strip())
        burst_time = int(self.burst_entry.get().strip())
        priority = int(self.priority_entry.get().strip() or 0)

        if arrival_time < 0 or burst_time <= 0:
            raise ValueError("Arrival time must be >= 0 and burst time must be > 0")

        return Process(pid=pid, arrival_time=arrival_time, burst_time=burst_time, priority=priority)

    def set_values(self, pid: str, arrival: str, burst: str, priority: str = "") -> None:
        self.pid_entry.delete(0, tk.END)
        self.pid_entry.insert(0, pid)
        self.arrival_entry.delete(0, tk.END)
        self.arrival_entry.insert(0, arrival)
        self.burst_entry.delete(0, tk.END)
        self.burst_entry.insert(0, burst)
        self.priority_entry.delete(0, tk.END)
        self.priority_entry.insert(0, priority)

    def destroy(self) -> None:
        self.frame.destroy()

# ----------------------------
# Main application window
# ----------------------------
class SchedulingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CPU Scheduling Algorithm Simulator")
        self.geometry("1120x800")
        self.minsize(960, 720)
        self.configure(padx=10, pady=10)
        self.process_rows: list[ProcessRow] = []
        self.color_map = {}
        self.tooltip = None
        self.create_widgets()

    def create_widgets(self) -> None:
        # ----------------------------
        # App styling and theme
        # ----------------------------
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TLabelframe", padding=10, background="#fff5fa", borderwidth=0, relief="flat")
        style.configure("TLabelframe.Label", foreground="#7a2459", font=("Segoe UI", 10, "bold"), background="#fff5fa")
        style.configure("TButton", padding=(10, 6), font=("Segoe UI", 9))
        style.configure("TEntry", fieldbackground="#fffafd", foreground="#7a2459")
        style.configure("TCombobox", fieldbackground="#fffafd", foreground="#7a2459")
        style.map("TButton", background=[("active", "#d96ba8")], foreground=[("active", "white")])
        style.configure("Treeview", rowheight=24, fieldbackground="#fffafd", background="#fffafd")
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), background="#f3d6e6")

        self.configure(bg="#fff5fa")
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        banner = tk.Frame(self, bg="#b3366f", height=78, bd=2, relief="solid")
        banner.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        banner.pack_propagate(False)
        tk.Label(
            banner,
            text="CPU Scheduling Algorithm Simulator",
            fg="white",
            bg="#b3366f",
            font=("Segoe UI", 19, "bold"),
            anchor="center",
        ).place(relx=0.5, rely=0.5, anchor="center")

        # ----------------------------
        # Top banner and scrollable content area
        # ----------------------------
        self.canvas = tk.Canvas(self, bg="#fff5fa", highlightthickness=0)
        self.canvas.grid(row=1, column=0, sticky="nsew")
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollbar.grid(row=1, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollable_frame = ttk.Frame(self.canvas)
        for col in range(2):
            self.scrollable_frame.columnconfigure(col, weight=1)
        self.canvas_frame_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.scrollable_frame.bind("<Configure>", lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # ----------------------------
        # Process input section
        # ----------------------------
        input_frame = ttk.LabelFrame(self.scrollable_frame, text="")
        input_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=(0, 10))
        input_frame.configure(style="TLabelframe")
        input_frame.columnconfigure(0, weight=1)

        tk.Label(input_frame, text="Process Input", font=("Segoe UI", 13, "bold"), fg="#9b2c62", bg="#ffe8f2").grid(row=0, column=0, sticky="ew", padx=6, pady=(0, 8))

        header = tk.Frame(input_frame, bg="#fff5fa")
        header.grid(row=1, column=0, sticky="ew", padx=6, pady=(0, 4))
        for col in range(5):
            header.grid_columnconfigure(col, weight=1, uniform="header_cols")
        for col, text in enumerate(["PID", "Arrival", "Burst", "Priority", ""]):
            tk.Label(header, text=text, width=12, anchor="w", bg="#fff5fa", fg="#a14174", font=("Segoe UI", 10, "bold")).grid(row=0, column=col, padx=3, sticky="ew")

        self.rows_frame = tk.Frame(input_frame, bg="#fff5fa")
        self.rows_frame.grid(row=2, column=0, sticky="ew", padx=6, pady=3)
        for col in range(1):
            self.rows_frame.grid_columnconfigure(col, weight=1, uniform="input_cols")

        for _ in range(1):
            self.add_process_row()

        button_frame = tk.Frame(input_frame, bg="#fff5fa")
        button_frame.grid(row=3, column=0, sticky="ew", padx=6, pady=6)
        ttk.Button(button_frame, text="Add Row", command=self.add_process_row).pack(side="left", padx=3)
        ttk.Button(button_frame, text="Use Sample", command=self.use_sample).pack(side="left", padx=3)
        ttk.Button(button_frame, text="Clear Rows", command=self.clear_rows).pack(side="left", padx=3)

        # ----------------------------
        # Scheduling controls section
        # ----------------------------
        control_frame = ttk.LabelFrame(self.scrollable_frame, text="")
        control_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0), pady=(0, 10))
        control_frame.configure(style="TLabelframe")
        control_frame.columnconfigure(0, weight=0)

        tk.Label(control_frame, text="Scheduling Options", font=("Segoe UI", 13, "bold"), fg="#9b2c62", bg="#ffe8f2").grid(row=0, column=0, columnspan=5, sticky="ew", padx=6, pady=(0, 8))

        ttk.Label(control_frame, text="Algorithm:").grid(row=1, column=0, padx=6, pady=6, sticky="w")
        self.algorithm_combo = ttk.Combobox(
            control_frame,
            values=["FCFS", "SJF", "SRTF", "Round Robin"],
            state="readonly",
            width=18,
        )
        self.algorithm_combo.current(0)
        self.algorithm_combo.grid(row=1, column=1, padx=6, pady=6, sticky="w")
        self.algorithm_combo.bind("<<ComboboxSelected>>", self.toggle_quantum)

        ttk.Label(control_frame, text="Quantum:").grid(row=1, column=2, padx=6, pady=6, sticky="w")
        self.quantum_entry = ttk.Entry(control_frame, width=10)
        self.quantum_entry.grid(row=1, column=3, padx=6, pady=6, sticky="w")
        self.quantum_entry.insert(0, "2")

        ttk.Button(control_frame, text="Run Scheduling", command=self.run_scheduling).grid(
            row=1, column=4, padx=10, pady=6, sticky="e"
        )

        self.toggle_quantum()

        # ----------------------------
        # Results table section
        # ----------------------------
        results_frame = ttk.LabelFrame(self.scrollable_frame, text="")
        results_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        results_frame.configure(style="TLabelframe")
        results_frame.rowconfigure(0, weight=1)
        results_frame.columnconfigure(0, weight=1)

        tk.Label(results_frame, text="Results", font=("Segoe UI", 13, "bold"), fg="#9b2c62", bg="#ffe8f2").grid(row=0, column=0, columnspan=2, sticky="ew", padx=6, pady=(0, 8))

        self.tree = ttk.Treeview(
            results_frame,
            columns=("pid", "arrival", "burst", "priority", "completion", "turnaround", "waiting"),
            show="headings",
            selectmode="browse",
            height=7,
        )
        for key, text in [
            ("pid", "PID"),
            ("arrival", "Arrival"),
            ("burst", "Burst"),
            ("priority", "Priority"),
            ("completion", "End"),
            ("turnaround", "Turnaround"),
            ("waiting", "Waiting"),
        ]:
            self.tree.heading(key, text=text)
            self.tree.column(key, width=90, anchor="center")

        tree_scroll = ttk.Scrollbar(results_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)

        self.tree.grid(row=1, column=0, sticky="nsew", padx=(6, 0), pady=6)
        tree_scroll.grid(row=1, column=1, sticky="ns", pady=6)

        self.stats_var = tk.StringVar(value="Ready to simulate.")
        self.avg_waiting_var = tk.StringVar(value="Average Waiting Time: --")
        self.avg_turnaround_var = tk.StringVar(value="Average Turnaround Time: --")
        self.avg_calc_var = tk.StringVar(value="Calculation details will appear here after a run.")
        self.avg_breakdown_var = tk.StringVar(value="")

        stats_frame = tk.Frame(results_frame, bg="#fff5fa")
        stats_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=6, pady=(0, 6))
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)

        tk.Label(
            stats_frame,
            textvariable=self.stats_var,
            bg="#fff5fa",
            fg="#7a2459",
            font=("Segoe UI", 10, "bold"),
            anchor="w",
            justify="left",
        ).grid(row=0, column=0, sticky="ew", padx=(0, 8))

        calc_frame = tk.Frame(results_frame, bg="#fff5fa", bd=1, relief="solid")
        calc_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=6, pady=(0, 6))
        calc_frame.columnconfigure(0, weight=1)

        tk.Label(
            calc_frame,
            text="Average Computations",
            bg="#fff5fa",
            fg="#9b2c62",
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        tk.Label(
            calc_frame,
            textvariable=self.avg_waiting_var,
            bg="#fff5fa",
            fg="#7a2459",
            font=("Segoe UI", 9),
            anchor="w",
            justify="left",
        ).grid(row=1, column=0, sticky="ew", padx=8, pady=2)
        tk.Label(
            calc_frame,
            textvariable=self.avg_turnaround_var,
            bg="#fff5fa",
            fg="#7a2459",
            font=("Segoe UI", 9),
            anchor="w",
            justify="left",
        ).grid(row=2, column=0, sticky="ew", padx=8, pady=2)
        tk.Label(
            calc_frame,
            textvariable=self.avg_calc_var,
            bg="#fff5fa",
            fg="#7a2459",
            font=("Segoe UI", 9),
            anchor="w",
            justify="left",
        ).grid(row=3, column=0, sticky="ew", padx=8, pady=(2, 4))
        tk.Label(
            calc_frame,
            textvariable=self.avg_breakdown_var,
            bg="#fff5fa",
            fg="#7a2459",
            font=("Segoe UI", 9),
            anchor="w",
            justify="left",
        ).grid(row=4, column=0, sticky="ew", padx=8, pady=(0, 8))

        # ----------------------------
        # Gantt chart section
        # ----------------------------
        gantt_frame = ttk.LabelFrame(self.scrollable_frame, text="")
        gantt_frame.grid(row=2, column=0, columnspan=2, sticky="nsew")
        gantt_frame.rowconfigure(0, weight=1)
        gantt_frame.columnconfigure(0, weight=1)

        tk.Label(gantt_frame, text="Gantt Chart", font=("Segoe UI", 13, "bold"), fg="#9b2c62", bg="#ffe8f2").grid(row=0, column=0, columnspan=2, sticky="ew", padx=6, pady=(0, 8))

        self.gantt_canvas = tk.Canvas(gantt_frame, bg="#fffafd", highlightthickness=1, highlightbackground="#f3d6e6")
        self.gantt_canvas.grid(row=1, column=0, sticky="nsew")
        self.gantt_canvas.bind("<Configure>", self.redraw_gantt)

        x_scroll = ttk.Scrollbar(gantt_frame, orient="horizontal", command=self.gantt_canvas.xview)
        y_scroll = ttk.Scrollbar(gantt_frame, orient="vertical", command=self.gantt_canvas.yview)
        self.gantt_canvas.configure(xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)
        x_scroll.grid(row=2, column=0, sticky="ew")
        y_scroll.grid(row=1, column=1, sticky="ns")

        self.gantt_data = []

    # ----------------------------
    # Scroll and layout helpers
    # ----------------------------
    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_frame_id, width=event.width)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ----------------------------
    # Process row actions
    # ----------------------------
    def add_process_row(self) -> None:
        row = ProcessRow(self.rows_frame, on_remove=lambda: self.remove_process_row(row))
        row.grid(len(self.process_rows))
        self.process_rows.append(row)

    def remove_process_row(self, row: ProcessRow) -> None:
        if row not in self.process_rows:
            return

        self.process_rows.remove(row)
        row.destroy()

        for index, remaining_row in enumerate(self.process_rows):
            remaining_row.grid(index)

    def clear_rows(self, count: int = 1) -> None:
        for row in list(self.process_rows):
            row.destroy()
        self.process_rows.clear()
        for _ in range(count):
            self.add_process_row()

    def use_sample(self) -> None:
        current_rows = len(self.process_rows)
        self.clear_rows(count=current_rows)
        for index in range(1, current_rows + 1):
            arrival = random.randint(0, 9)
            burst = random.randint(2, 10)
            priority = random.randint(0, 5)
            row = self.process_rows[index - 1]
            row.set_values(f"P{index}", str(arrival), str(burst), str(priority))

    # ----------------------------
    # Scheduling actions
    # ----------------------------
    def toggle_quantum(self, event=None) -> None:
        algorithm = self.algorithm_combo.get()
        self.quantum_entry.configure(state="normal" if algorithm == "Round Robin" else "disabled")

    def run_scheduling(self) -> None:
        try:
            processes = []
            for row in self.process_rows:
                pid = row.pid_entry.get().strip()
                arrival = row.arrival_entry.get().strip()
                burst = row.burst_entry.get().strip()
                if not pid and not arrival and not burst:
                    continue
                processes.append(row.get_process())

            if not processes:
                raise ValueError("Please provide at least one process.")

            scheduler = Scheduler(processes)
            algorithm = self.algorithm_combo.get()
            if algorithm == "FCFS":
                results = scheduler.fcfs()
            elif algorithm == "SJF":
                results = scheduler.sjf()
            elif algorithm == "SRTF":
                results = scheduler.srtf()
            else:
                quantum = int(self.quantum_entry.get().strip())
                if quantum <= 0:
                    raise ValueError("Quantum must be greater than 0.")
                results = scheduler.round_robin(quantum)

            self.show_results(algorithm, results, scheduler)
        except ValueError as exc:
            messagebox.showerror("Input Error", str(exc))
        except Exception as exc:
            messagebox.showerror("Error", f"Unexpected error: {exc}")

    # ----------------------------
    # Display results and chart
    # ----------------------------
    def show_results(self, algorithm: str, results: list[Process], scheduler: Scheduler) -> None:
        self.tree.delete(*self.tree.get_children())
        for process in results:
            self.tree.insert(
                "",
                "end",
                values=(
                    process.pid,
                    process.arrival_time,
                    process.burst_time,
                    process.priority,
                    process.completion_time,
                    process.turnaround_time,
                    process.waiting_time,
                ),
            )

        self.gantt_data = scheduler.gantt_chart
        self.color_map = {
            process.pid: process.color
            for process in scheduler.processes
            if getattr(process, "color", None)
        }
        self.redraw_gantt()
        total_waiting = sum(process.waiting_time for process in scheduler.processes)
        total_turnaround = sum(process.turnaround_time for process in scheduler.processes)
        process_count = len(scheduler.processes)
        avg_waiting = total_waiting / process_count if process_count else 0
        avg_turnaround = total_turnaround / process_count if process_count else 0

        self.stats_var.set(
            f"{algorithm} completed • Average Waiting Time: {scheduler.avg_waiting:.2f} ms • Average Turnaround Time: {scheduler.avg_turnaround:.2f} ms"
        )
        waiting_terms = [str(p.waiting_time) for p in scheduler.processes]
        turnaround_terms = [str(p.turnaround_time) for p in scheduler.processes]

        self.avg_waiting_var.set(
            f"Average Waiting Time = Σ({'+'.join(waiting_terms)}) / {process_count} = {avg_waiting:.2f} ms"
        )
        self.avg_turnaround_var.set(
            f"Average Turnaround Time = Σ({'+'.join(turnaround_terms)}) / {process_count} = {avg_turnaround:.2f} ms"
        )
        self.avg_calc_var.set(
            f"Calculation basis: {process_count} process{'es' if process_count != 1 else ''} • Sum of Waiting = {total_waiting:.2f} ms • Sum of Turnaround = {total_turnaround:.2f} ms"
        )
        self.avg_breakdown_var.set("")

    def redraw_gantt(self, event=None) -> None:
        self.gantt_canvas.delete("all")
        if not self.gantt_data:
            self.gantt_canvas.create_text(
                10, 10,
                anchor="nw",
                text="Run a scheduling algorithm to display the Gantt chart.",
                fill="#666666",
                font=("Segoe UI", 11),
            )
            return

        chart_width = max(800, self.gantt_canvas.winfo_width())
        chart_height = max(220, self.gantt_canvas.winfo_height())
        left_margin = 110
        top_margin = 70
        bar_height = 24
        max_time = max(segment.get("end", 0) for segment in self.gantt_data)
        if max_time <= 0:
            max_time = 1

        scale = max(20, min(60, (chart_width - left_margin - 30) / max_time))

        self.gantt_canvas.create_rectangle(10, 12, chart_width - 12, chart_height - 12, outline="#f3d6e6", width=2, fill="#fff5fa")
        self.gantt_canvas.create_line(left_margin, top_margin - 10, chart_width - 20, top_margin - 10, fill="#a14174")
        self.gantt_canvas.create_text(left_margin - 8, top_margin - 10, text="Time", anchor="e", font=("Segoe UI", 10, "bold"))

        for tick in range(0, max_time + 1):
            x = left_margin + tick * scale
            self.gantt_canvas.create_line(x, top_margin - 10, x, top_margin + 10, fill="#f1c5dc")
            self.gantt_canvas.create_text(x, top_margin + 24, text=str(tick), font=("Segoe UI", 9), fill="#8a3b63")

        palette = ["#2563eb", "#059669", "#dc2626", "#7c3aed", "#ea580c", "#0891b2", "#be185d"]
        for index, segment in enumerate(self.gantt_data):
            pid = segment.get("pid", "Unknown")
            start = segment.get("start", 0)
            end = segment.get("end", 0)
            x0 = left_margin + start * scale
            x1 = left_margin + end * scale
            color = self.color_map.get(pid, palette[index % len(palette)])
            if pid == "Idle":
                color = "#d6c2cc"
            rect = self.gantt_canvas.create_rectangle(x0, top_margin - bar_height // 2, x1, top_margin + bar_height // 2, fill=color, outline="#7a2459", width=1)
            self.gantt_canvas.create_text((x0 + x1) / 2, top_margin, text=pid, fill="white", font=("Segoe UI", 9, "bold"))
            self.gantt_canvas.tag_bind(rect, "<Enter>", lambda event, s=segment, row=pid: self.show_tooltip(event, s, row))
            self.gantt_canvas.tag_bind(rect, "<Leave>", self.hide_tooltip)

        self.gantt_canvas.configure(scrollregion=(0, 0, max(chart_width, left_margin + max_time * scale + 30), max(chart_height, top_margin + 60)))

    # ----------------------------
    # Tooltip helpers
    # ----------------------------
    def show_tooltip(self, event, segment, pid):
        if self.tooltip is not None:
            self.gantt_canvas.delete(self.tooltip)
        x, y = event.x + 10, event.y + 10
        self.tooltip = self.gantt_canvas.create_text(
            x,
            y,
            text=f"{pid}: {segment['start']} -> {segment['end']}",
            anchor="nw",
            fill="#111827",
            font=("Segoe UI", 9),
            tags="tooltip",
        )

    def hide_tooltip(self, event=None):
        if self.tooltip is not None:
            self.gantt_canvas.delete(self.tooltip)
            self.tooltip = None

if __name__ == "__main__":
    app = SchedulingApp()
    app.mainloop()
