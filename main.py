import os
import sys
import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import to_hex
from matplotlib.ticker import LinearLocator, FuncFormatter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from serialization import load_artillery_list

if getattr(sys, 'frozen', False):
    # Running as a PyInstaller executable
    base_path = sys._MEIPASS
else:
    # Running as a script
    base_path = os.path.dirname(__file__)

config_path = os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else base_path,
                           "data.json")


class Tooltip:
    def __init__(self, widget, text_func, delay=300):
        self.widget = widget
        self.text_func = text_func
        self.delay = delay
        self.tipwindow = None
        self.id = None

        widget.bind("<Enter>", self.schedule)
        widget.bind("<Leave>", self.hide)
        widget.bind("<Motion>", self.move)

    def schedule(self, event=None):
        self.id = self.widget.after(self.delay, self.show)

    def show(self):
        if self.tipwindow:
            return

        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            tw,
            text=self.text_func(),
            justify="left",
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            font=("Segoe UI", 9)
        )
        label.pack(ipadx=6, ipady=4)

    def move(self, event):
        if self.tipwindow:
            x = event.x_root + 15
            y = event.y_root + 10
            self.tipwindow.wm_geometry(f"+{x}+{y}")

    def hide(self, event=None):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None


# --------------------------
# Load artillery data
# --------------------------

# Ammo_PaK36r_F22_indirect_HE is the same as Ammo_Howz_F22_76mm.
artilleries = [
    a for a in load_artillery_list(config_path)
    if a.ammo_name != "Ammo_PaK36r_F22_indirect_HE"
]

# --------------------------
# GUI Setup
# --------------------------
root = tk.Tk()
root.title("Artillery Dispersion Plotter")
root.state("zoomed")


def on_closing():
    plt.close('all')
    root.quit()
    root.destroy()


root.protocol("WM_DELETE_WINDOW", on_closing)

style = ttk.Style()

style.configure("Mortar.TCheckbutton", foreground="blue")
style.configure("Tube.TCheckbutton", foreground="green")
style.configure("Rocket.TCheckbutton", foreground="violet")

# Dim styles for filtered-out items
style.configure("MortarDim.TCheckbutton", foreground="#9aa0a6")
style.configure("TubeDim.TCheckbutton", foreground="#9aa0a6")
style.configure("RocketDim.TCheckbutton", foreground="#9aa0a6")
style.configure("DefaultDim.TCheckbutton", foreground="#9aa0a6")

checkbox_vars = {}

ttk.Label(root, text="Select Artillery:").pack(pady=5)

# --------------------------
# Search Bar
# --------------------------
search_var = tk.StringVar()

search_frame = ttk.Frame(root)
search_frame.pack(fill="x", padx=5, pady=5)

ttk.Label(search_frame, text="Search:").pack(side="left", padx=(0, 5))

search_entry = ttk.Entry(search_frame, textvariable=search_var)
search_entry.pack(side="left", fill="x", expand=True)

placeholder_text = "Enter artillery name, not card name (e.g., S.FH 18 L/30, not HUMMEL 150mm)"

search_entry.insert(0, placeholder_text)
search_entry.config(foreground="grey")


def on_focus_in(event):
    if search_entry.get() == placeholder_text:
        search_entry.delete(0, tk.END)
        search_entry.config(foreground="black")


def on_focus_out(event):
    if not search_entry.get():
        search_entry.insert(0, placeholder_text)
        search_entry.config(foreground="grey")


search_entry.bind("<FocusIn>", on_focus_in)
search_entry.bind("<FocusOut>", on_focus_out)

frame = ttk.Frame(root)
frame.pack(fill="both", expand=False, padx=5, pady=5)

for art in artilleries:
    var = tk.BooleanVar()

    if art.artillery_type.name == "MORTAR":
        chk_style = "Mortar.TCheckbutton"
    elif art.artillery_type.name == "TUBE":
        chk_style = "Tube.TCheckbutton"
    elif art.artillery_type.name == "ROCKET":
        chk_style = "Rocket.TCheckbutton"
    else:
        chk_style = "TCheckbutton"

    chk = ttk.Checkbutton(frame, text=art.example_gun, variable=var, style=chk_style)

    checkbox_vars[art.example_gun] = {
        "var": var,
        "chk": chk,
        "style": chk_style
    }


    def make_tooltip_text(a=art):
        return (
            f"Artillery name: {a.gun_name}\n"
            f"Calibre: {a.calibre} mm\n"
            f"Aim time: {a.aim_time:.2f} s\n"
            f"Reload: {a.reload_time:.2f} s\n"
            f"Damage: {a.damage:.2f}\n"
            f"Damage radius: {a.damage_radius:.2f} m\n"
            f"Suppression: {a.suppression:.2f}\n"
            f"Suppression radius: {a.suppression_radius:.2f} m\n"
            # f"Ammo Count: {a.ammo_count}\n"
            f"Projectiles per salvo: {a.projectiles_salvo}\n"
            f"Supply cost (projectile): {a.supply_cost}\n"
            f"Radio dispersion multiplier: {a.corrected_shot_aim_time_multiplier}\n"
            f"Radio aim time multiplier: {a.corrected_shot_dispersion_multiplier}"
        )


    Tooltip(chk, make_tooltip_text)


def apply_axis_limits():
    try:
        x_min = float(x_min_var.get())
        x_max = float(x_max_var.get())
        y_min = float(y_min_var.get())
        y_max = float(y_max_var.get())

        if x_min < x_max:
            ax.set_xlim(x_min, x_max)

        if y_min < y_max:
            ax.set_ylim(y_min, y_max)

        def formatter(val, pos):
            if abs(val) < 1e-6:
                val = 0
            return ('{:.2f}'.format(val)).rstrip('0').rstrip('.')

        ax.xaxis.set_major_locator(LinearLocator(11))
        ax.yaxis.set_major_locator(LinearLocator(6))

        ax.yaxis.set_major_formatter(FuncFormatter(formatter))
        ax.xaxis.set_major_formatter(FuncFormatter(formatter))

    except ValueError:
        pass


# --------------------------
# Update hover values
# --------------------------
def update_hover_values(x_mouse):
    for name, (x, y, line) in plotted_lines.items():
        label_dict = hover_labels.get(name)
        if label_dict is None:
            continue

        label_widget = label_dict["label"]

        if x_mouse < x[0] or x_mouse > x[-1]:
            label_widget.config(text="")
            continue

        idx = (np.abs(x - x_mouse)).argmin()
        y_val = y[idx]

        if display_mode.get() == "dispersion":
            text = f"{name}: {y_val:.2f}"
        else:
            text = f"{name}: {y_val:.6f}"

        label_widget.config(text=text)


# --------------------------
# Update plot function
# --------------------------
stop_updating = False


def update_plot(*args):
    if stop_updating:
        return

    # Remember current vertical line position
    try:
        x_val = float(current_range_var.get())
    except ValueError:
        x_val = 0

    ax.clear()
    plotted_lines.clear()

    # Track which labels should remain
    active_names = [
        art.example_gun
        for art in artilleries
        if checkbox_vars[art.example_gun]["var"].get()
    ]

    # Remove color for deselected artillery
    for name in list(color_map.keys()):
        if name not in active_names:
            del color_map[name]

    # Plot active artillery
    for name in active_names:
        artillery = next(a for a in artilleries if a.example_gun == name)
        x = np.linspace(0, 15000, 1000)

        disp_values = [artillery.dispersion(d) for d in x]
        disp_values = [v if v is not None else np.nan for v in disp_values]

        if display_mode.get() == "dispersion":
            y = np.array(disp_values)
        else:
            y = np.array([np.pi * v ** 2 / 1e6 if v is not None else np.nan for v in disp_values])

        # Assign color if this artillery doesn't have one yet
        used_colors = set(color_map.values())

        if name not in color_map:
            for c in color_cycle:
                if c not in used_colors:
                    color_map[name] = c
                    break
            else:
                # fallback if all colors are used
                color_map[name] = color_cycle[len(color_map) % len(color_cycle)]

        line, = ax.plot(x, y, label=artillery.example_gun, color=color_map[name])
        plotted_lines[name] = (x, y, line)

        # Create hover label if it doesn't exist yet
        if name not in hover_labels:
            row = ttk.Frame(hover_frame)
            row.pack(fill="x", pady=1)

            color_box = tk.Canvas(row, width=12, height=12, highlightthickness=0)
            color_box.create_rectangle(0, 0, 12, 12, fill=color_map[name], outline=color_map[name])
            color_box.pack(side="left", padx=4)

            label = ttk.Label(row, text="")
            label.pack(side="left")
            hover_labels[name] = {"label": label, "row": row}

    # Remove hover labels for deselected artillery
    for name in list(hover_labels.keys()):
        if name not in active_names:
            hover_labels[name]["row"].destroy()
            del hover_labels[name]

    # Set Y-axis label
    if display_mode.get() == "dispersion":
        ax.set_ylabel("Dispersion (m)")
    else:
        ax.set_ylabel("Target Area (km²)")

    ax.set_xlabel("Range (m)")
    ax.grid(True)
    apply_axis_limits()

    # Recreate vertical line at the remembered x position
    global vertical_line
    vertical_line = ax.axvline(x_val, color='gray', linestyle='--', alpha=0.5)

    # Update hover panel values
    update_hover_values(x_val)

    canvas.draw_idle()


# --------------------------
# Mode toggle: dispersion vs target area
# --------------------------
display_mode = tk.StringVar(value="dispersion")


def smart_round(value, tol=1e-4):
    if abs(value - round(value)) < tol:
        return str(int(round(value)))

    rounded = round(value, 6)
    return f"{rounded:.6f}".rstrip("0").rstrip(".")


def on_mode_change(*args):
    try:
        y_min = float(y_min_var.get())
        y_max = float(y_max_var.get())

        if display_mode.get() == "dispersion":
            y_min_new = np.sqrt(y_min * 1e6 / np.pi)
            y_max_new = np.sqrt(y_max * 1e6 / np.pi)
        else:
            y_min_new = np.pi * y_min ** 2 / 1e6
            y_max_new = np.pi * y_max ** 2 / 1e6

        y_min_var.set(smart_round(y_min_new))
        y_max_var.set(smart_round(y_max_new))

    except ValueError:
        pass

    update_plot()

    try:
        x_val = float(current_range_var.get())
    except ValueError:
        x_val = 0
    update_hover_values(x_val)


display_mode.trace_add("write", on_mode_change)

mode_frame = ttk.Frame(root)
mode_frame.pack(pady=5)

ttk.Label(mode_frame, text="Y-axis:").pack(side="left")

ttk.Radiobutton(mode_frame, text="Dispersion Radius (m)", variable=display_mode, value="dispersion").pack(side="left",
                                                                                                          padx=5)
ttk.Radiobutton(mode_frame, text="Target Area (km²)", variable=display_mode, value="area").pack(side="left", padx=5)

# --------------------------
# Axis Range Controls
# --------------------------
range_frame = ttk.LabelFrame(root, text="Axis Ranges")
range_frame.pack(fill="x", padx=5, pady=5)

for i in range(9):  # columns 0-8 (before current range)
    range_frame.columnconfigure(i, weight=0)  # no stretching
range_frame.columnconfigure(9, weight=1)  # stretch the last column

# X Range
ttk.Label(range_frame, text="X Min:").grid(row=0, column=0, padx=5)
x_min_var = tk.StringVar(value="0")
ttk.Entry(range_frame, textvariable=x_min_var, width=8).grid(row=0, column=1)

ttk.Label(range_frame, text="X Max:").grid(row=0, column=2, padx=5)
x_max_var = tk.StringVar(value="10000")
ttk.Entry(range_frame, textvariable=x_max_var, width=8).grid(row=0, column=3)

# Y Range
ttk.Label(range_frame, text="Y Min:").grid(row=0, column=4, padx=5)
y_min_var = tk.StringVar(value="0")
ttk.Entry(range_frame, textvariable=y_min_var, width=8).grid(row=0, column=5)

ttk.Label(range_frame, text="Y Max:").grid(row=0, column=6, padx=5)
y_max_var = tk.StringVar(value="500")
ttk.Entry(range_frame, textvariable=y_max_var, width=8).grid(row=0, column=7)

# Spacer column to push Current Range to the right
ttk.Label(range_frame, text="").grid(row=0, column=8, sticky="ew")

# Current Range on the outer right
ttk.Label(range_frame, text="Current Range:").grid(row=0, column=9, padx=5, sticky="e")
current_range_var = tk.StringVar(value="0")
current_range_entry = ttk.Entry(range_frame, textvariable=current_range_var, width=8)
current_range_entry.grid(row=0, column=10, padx=(0, 90), sticky="e")
range_frame.columnconfigure(10, weight=0)

for entry in range_frame.winfo_children():
    if isinstance(entry, ttk.Entry):
        entry.bind("<Return>", lambda e: update_plot())
        entry.bind("<FocusOut>", lambda e: update_plot())

# --------------------------
# Hover + Plot + Legend layout
# --------------------------
plot_container = ttk.Frame(root)
plot_container.pack(fill="both", expand=True)

hover_container = ttk.Frame(plot_container)
hover_container.pack(side="right", fill="y")

hover_canvas = tk.Canvas(hover_container, width=240)
hover_scrollbar = ttk.Scrollbar(hover_container, orient="vertical", command=hover_canvas.yview)

hover_frame = ttk.Frame(hover_canvas)

hover_frame.bind(
    "<Configure>",
    lambda e: hover_canvas.configure(scrollregion=hover_canvas.bbox("all"))
)

hover_canvas.create_window((0, 0), window=hover_frame, anchor="nw")
hover_canvas.configure(yscrollcommand=hover_scrollbar.set)

hover_canvas.pack(side="left", fill="y", expand=True)
hover_scrollbar.pack(side="right", fill="y")


def _on_mousewheel(event):
    canvas_height = hover_canvas.winfo_height()
    content_height = hover_frame.winfo_reqheight()
    if content_height <= canvas_height:
        return

    if event.num == 5 or event.delta < 0:
        hover_canvas.yview_scroll(1, "units")
    elif event.num == 4 or event.delta > 0:
        hover_canvas.yview_scroll(-1, "units")


def bind_scroll(event):
    hover_canvas.bind_all("<MouseWheel>", _on_mousewheel)
    hover_canvas.bind_all("<Button-4>", _on_mousewheel)
    hover_canvas.bind_all("<Button-5>", _on_mousewheel)


def unbind_scroll(event):
    hover_canvas.unbind_all("<MouseWheel>")
    hover_canvas.unbind_all("<Button-4>")
    hover_canvas.unbind_all("<Button-5>")


hover_canvas.bind("<Enter>", bind_scroll)
hover_canvas.bind("<Leave>", unbind_scroll)

# Windows and Mac
hover_canvas.bind_all("<MouseWheel>", _on_mousewheel)
# Linux (scroll up / down)
hover_canvas.bind_all("<Button-4>", _on_mousewheel)
hover_canvas.bind_all("<Button-5>", _on_mousewheel)

plot_frame = ttk.Frame(plot_container)
plot_frame.pack(side="left", fill="both", expand=True)

fig, ax = plt.subplots(figsize=(12, 4), constrained_layout=True)
canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvas.get_tk_widget().pack(fill="both", expand=True)

plotted_lines = {}
color_map = {}  # name -> color
hover_labels = {}  # name -> ttk.Label
color_cycle = plt.rcParams['axes.prop_cycle'].by_key()['color'] + [to_hex(c) for c in plt.cm.tab20.colors + plt.cm.tab20b.colors + plt.cm.tab20c.colors]

# Persistent vertical line
vertical_line = ax.axvline(0, color='gray', linestyle='--', alpha=0.5)


# --------------------------
# Hover event to show all values at cursor x
# --------------------------


def on_current_range_change(event=None):
    try:
        x_val = float(current_range_var.get())

        x_min = float(x_min_var.get())
        x_max = float(x_max_var.get())
        x_val = max(min(x_val, x_max), x_min)

        vertical_line.set_xdata([x_val, x_val])

        update_hover_values(x_val)

        canvas.draw_idle()
    except ValueError:
        pass


current_range_entry.bind("<Return>", on_current_range_change)
current_range_entry.bind("<FocusOut>", on_current_range_change)


def on_motion(event):
    if event.inaxes != ax:
        vertical_line.set_xdata([0, 0])
        canvas.draw_idle()
        return

    x_mouse = event.xdata
    vertical_line.set_xdata([x_mouse, x_mouse])

    current_range_var.set(f"{x_mouse:.0f}")

    update_hover_values(x_mouse)

    canvas.draw_idle()


# --------------------------
# Select / Deselect Buttons
# --------------------------
type_button_frame = ttk.Frame(root)
type_button_frame.pack(fill="x", padx=5, pady=5)


def select_all():
    global stop_updating
    stop_updating = True

    for data in checkbox_vars.values():
        var = data["var"]
        var.set(True)

    stop_updating = False
    update_plot()


def add_type(type_name):
    global stop_updating
    stop_updating = True

    for art in artilleries:
        if art.artillery_type.name == type_name:
            checkbox_vars[art.example_gun]["var"].set(True)

    stop_updating = False
    update_plot()


def deselect_all():
    global stop_updating
    stop_updating = True

    for data in checkbox_vars.values():
        var = data["var"]
        var.set(False)

    stop_updating = False
    update_plot()


style.configure("Action.TButton", foreground="black", padding=5)
ttk.Button(type_button_frame, text="Select All", command=select_all, style="Action.TButton").pack(side="left", padx=5)
ttk.Button(type_button_frame, text="Add Mortar", command=lambda: add_type("MORTAR")).pack(side="left", padx=5)
ttk.Button(type_button_frame, text="Add Tube", command=lambda: add_type("TUBE")).pack(side="left", padx=5)
ttk.Button(type_button_frame, text="Add Rocket", command=lambda: add_type("ROCKET")).pack(side="left", padx=5)
ttk.Button(type_button_frame, text="Deselect All", command=deselect_all, style="Action.TButton").pack(side="left",
                                                                                                      padx=5)


# --------------------------
# Organize checkboxes in a dynamic grid
# --------------------------
def organize_grid(*args):
    frame.update_idletasks()
    width = frame.winfo_width()

    chk_width = 205
    columns = max(1, width // chk_width)

    search_text = search_var.get().lower().strip()
    if search_text == placeholder_text.lower():
        search_text = ""

    num_rows = (len(artilleries) + columns - 1) // columns

    for c in range(columns):
        frame.grid_columnconfigure(c, weight=1, minsize=chk_width)

    for i, art in enumerate(artilleries):
        data = checkbox_vars[art.example_gun]
        chk = data["chk"]
        original_style = data["style"]

        row = i % num_rows
        col = i // num_rows
        chk.grid(row=row, column=col, sticky="w", padx=10, pady=2)

        matches = (
                search_text in art.example_gun.lower()
                or search_text in art.gun_name.lower()
        )

        if search_text == "":
            chk.configure(style=original_style)
        elif matches:
            chk.configure(style=original_style)
        else:
            # Apply dim style
            if original_style == "Mortar.TCheckbutton":
                chk.configure(style="MortarDim.TCheckbutton")
            elif original_style == "Tube.TCheckbutton":
                chk.configure(style="TubeDim.TCheckbutton")
            elif original_style == "Rocket.TCheckbutton":
                chk.configure(style="RocketDim.TCheckbutton")
            else:
                chk.configure(style="DefaultDim.TCheckbutton")


search_var.trace_add("write", organize_grid)

frame.bind("<Configure>", organize_grid)

# --------------------------
# Attach update function to each checkbox
# --------------------------
for data in checkbox_vars.values():
    var = data["var"]
    var.trace_add('write', update_plot)

canvas.mpl_connect("motion_notify_event", on_motion)

update_plot()

root.mainloop()
