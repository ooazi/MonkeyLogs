import os
import json
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager, rcParams

# Paths
LOG_PATH = os.path.expanduser("~/monkeylogger/monkeylogs/log/log.jsonc")
GRAPH_DIR = os.path.expanduser("~/monkeylogger/monkeylogs/static/graphs/")

# Ensure the graph directory exists
if not os.path.exists(GRAPH_DIR):
    os.makedirs(GRAPH_DIR)

# 🔍 Force Matplotlib to use JetBrains Mono if installed
font_path = None
for font in font_manager.findSystemFonts():
    if "JetBrainsMono" in font or "JetBrains Mono" in font:
        font_path = font
        break

if font_path:
    font_prop = font_manager.FontProperties(fname=font_path)
    rcParams["font.family"] = font_prop.get_name()
else:
    print("⚠️ JetBrains Mono not found. Using default font.")

# 🖌️ One Dark Theme for Matplotlib
rcParams["axes.facecolor"] = "#282c34"
rcParams["figure.facecolor"] = "#282c34"
rcParams["axes.edgecolor"] = "#abb2bf"
rcParams["axes.labelcolor"] = "#abb2bf"
rcParams["xtick.color"] = "#abb2bf"
rcParams["ytick.color"] = "#abb2bf"
rcParams["grid.color"] = "#4b5263"
rcParams["legend.edgecolor"] = "#abb2bf"

# 🎨 One Dark Color Scheme
COLORS = {
    "blue": "#61afef",
    "red": "#e06c75",
    "yellow": "#e5c07b",
    "green": "#98c379",
    "purple": "#c678dd",
    "cyan": "#56b6c2",
    "gray": "#5c6370"
}

def clear_old_graphs():
    """🗑️ Deletes all old graphs before generating new ones."""
    for filename in os.listdir(GRAPH_DIR):
        file_path = os.path.join(GRAPH_DIR, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

def load_typing_data():
    """📂 Loads typing session data from log file."""
    if not os.path.exists(LOG_PATH):
        return []

    try:
        with open(LOG_PATH, "r") as f:
            data = json.load(f)
            return data.get("sessions", [])
    except json.JSONDecodeError:
        return []

def plot_wpm_trend(data):
    """📊 Saves WPM trend graph as an image."""
    timestamps = [s["timestamp"] for s in data]
    wpm_values = [s["wpm"] for s in data]
    dates = [time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts)) for ts in timestamps]

    plt.figure(figsize=(10, 5))
    plt.plot(dates, wpm_values, marker="o", linestyle="-", label="WPM", color=COLORS["blue"], linewidth=2, markersize=6)
    plt.xticks(rotation=45, ha="right", fontsize=8)
    plt.xlabel("Time", fontsize=10)
    plt.ylabel("Words Per Minute", fontsize=10)
    plt.title("Typing Speed Over Time", fontsize=12, color=COLORS["yellow"])
    plt.legend(facecolor="#3e4451", edgecolor=COLORS["gray"])
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.savefig(os.path.join(GRAPH_DIR, "wpm_trend.png"), dpi=300, bbox_inches="tight")
    plt.close()

def plot_session_duration_vs_wpm(data):
    """📊 Saves session duration vs. WPM scatter plot as an image."""
    durations = [s["session_duration"] for s in data]
    wpm_values = [s["wpm"] for s in data]

    plt.figure(figsize=(7, 5))
    plt.scatter(durations, wpm_values, color=COLORS["red"], alpha=0.7, edgecolor=COLORS["gray"], linewidth=1)
    plt.xlabel("Session Duration (s)", fontsize=10)
    plt.ylabel("Words Per Minute", fontsize=10)
    plt.title("Session Duration vs. WPM", fontsize=12, color=COLORS["yellow"])
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.savefig(os.path.join(GRAPH_DIR, "session_duration_vs_wpm.png"), dpi=300, bbox_inches="tight")
    plt.close()

def generate_all_graphs():
    """🛠️ Deletes old graphs and generates fresh ones."""
    data = load_typing_data()
    if not data:
        print("⚠️ No typing data available.")
        return
    
    print("🗑️ Deleting old graphs...")
    clear_old_graphs()  # **Delete all old graphs**
    
    print("📊 Generating new graphs...")
    plot_wpm_trend(data)
    plot_session_duration_vs_wpm(data)

    print("✅ Graphs updated successfully.")

if __name__ == "__main__":
    generate_all_graphs()