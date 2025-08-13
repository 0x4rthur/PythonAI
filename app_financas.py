import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import pandas as pd
import re
import math
from matplotlib.patches import PathPatch, Path

# Data parsing function
def parse_value(v):
    if pd.isna(v) or v == '':
        return 0.0
    v = re.sub(r'[R$ ]', '', str(v))
    v = v.replace('.', '').replace(',', '.')
    return float(v)

# Load data using Pandas
data_str = """Data,BTG,Inter,Itaú,Mercado Pago,Nubank,Apartamento,Faculdade,Total
06/2025,,,"R$ 897,74",,"R$ 788,73","R$ 1.000,00","R$ 320,00","R$ 3.006,47"
07/2025,,,"R$ 900,70","R$ 175,24","R$ 1.006,24","R$ 1.000,00","R$ 320,00","R$ 3.402,18"
08/2025,,,"R$ 605,81","R$ 175,24","R$ 613,79","R$ 1.000,00","R$ 320,00","R$ 2.714,84"
"""
df = pd.read_csv(pd.compat.StringIO(data_str))
df = df.apply(lambda x: x.map(parse_value) if x.dtype == 'object' else x)
df['Balance'] = 4185 - df['Total']

# Calculations
categories = ['BTG', 'Inter', 'Itaú', 'Mercado Pago', 'Nubank', 'Apartamento', 'Faculdade']
avg_cats = df[categories].mean()
suggestions = avg_cats[avg_cats > 500].index.tolist()

latest_balance = df['Balance'].iloc[-1]
latest_percent_saved = (latest_balance / 4185) * 100
avg_balance = df['Balance'].mean()

# Forecast calculations
avg_savings = avg_balance
projected_savings = [avg_savings * i for i in range(1, 5)]  # 2025-2028
years = ['2025', '2026', '2027', '2028']
forecast_descriptions = [
    "Stable savings growth",
    f"+{int(latest_percent_saved)}% avg save",
    "Reduce fixed costs",
    "Financial stability"
]

# UI Setup
root = tk.Tk()
root.title("Personal Finance Dashboard")
root.geometry("1200x800")
root.config(bg='#e0f7fa')  # Gradient-like light teal background

# Custom style for cards
style = ttk.Style()
style.configure("Card.TFrame", background="#ffffff", relief="flat", borderwidth=2)

# Expense Statistics Card (Dark gradient, top-left)
stats_frame = ttk.Frame(root, style="Card.TFrame")
stats_frame.place(x=50, y=50, width=500, height=300)
tk.Label(stats_frame, text="Expense Statistics", bg="#1a1a1a", fg="white", font=("Arial", 16, "bold"), padx=10, pady=5).pack()
tk.Label(stats_frame, text="Updated today", bg="#1a1a1a", fg="gray", font=("Arial", 10), padx=10).pack()

# Bar chart for monthly totals (animated)
fig_bar, ax_bar = plt.subplots(figsize=(4.5, 2.5), facecolor='#1a1a1a')
ax_bar.set_facecolor('#1a1a1a')
months = df['Data'].tolist()
totals = df['Total'].tolist()
bars = ax_bar.bar(months, [0]*len(months), color=['#90ee90', '#dda0dd', '#90ee90'])
ax_bar.set_ylim(0, max(totals)*1.2)
ax_bar.tick_params(colors='white', labelsize=10)
ax_bar.spines['top'].set_visible(False)
ax_bar.spines['right'].set_visible(False)
ax_bar.spines['bottom'].set_color('white')
ax_bar.spines['left'].set_color('white')

def animate_bar(frame):
    for i, bar in enumerate(bars):
        bar.set_height(totals[i] * (frame / 50))
    return bars

anim_bar = FuncAnimation(fig_bar, animate_bar, frames=50, interval=20, blit=True, repeat=False)

canvas_bar = FigureCanvasTkAgg(fig_bar, master=stats_frame)
canvas_bar.draw()
canvas_bar.get_tk_widget().pack(pady=10)

# Pie chart for categories
fig_pie, ax_pie = plt.subplots(figsize=(4.5, 2.5), facecolor='#1a1a1a')
latest_cats = df[categories].iloc[-1].tolist()
latest_labels = [cat for cat, val in zip(categories, latest_cats) if val > 0]
latest_cats = [val for val in latest_cats if val > 0]
ax_pie.pie(latest_cats, labels=latest_labels, autopct='%1.1f%%', colors=['#90ee90', '#dda0dd', '#add8e6', '#ffb6c1', '#eee8aa'], startangle=90)
ax_pie.axis('equal')
ax_pie.set_facecolor('#1a1a1a')
canvas_pie = FigureCanvasTkAgg(fig_pie, master=stats_frame)
canvas_pie.draw()
canvas_pie.get_tk_widget().pack(pady=10)

# Current Balance Card (Green gradient, bottom-left)
balance_frame = ttk.Frame(root, style="Card.TFrame")
balance_frame.place(x=50, y=370, width=500, height=300)
tk.Label(balance_frame, text="Current Balance", bg="#90ee90", fg="black", font=("Arial", 16, "bold"), padx=10, pady=5).pack()

# Gauge for % saved (animated with PathPatch)
fig_gauge, ax_gauge = plt.subplots(figsize=(4.5, 2.5), subplot_kw={'polar': True}, facecolor='#90ee90')
ax_gauge.set_ylim(0, 1)
ax_gauge.set_yticks([])
ax_gauge.set_xticks([])
ax_gauge.spines['polar'].set_visible(False)
gauge_patch = None

def animate_gauge(frame):
    global gauge_patch
    if gauge_patch:
        gauge_patch.remove()
    theta = math.radians(180 * (latest_percent_saved / 100) * (frame / 50))
    path = Path([(0, 0), (theta, 0), (theta, 1), (0, 1)], [1, 2, 2, 2])
    gauge_patch = PathPatch(path, facecolor='#1a1a1a', alpha=0.8, transform=ax_gauge.transData._b)
    ax_gauge.add_patch(gauge_patch)
    return gauge_patch,

anim_gauge = FuncAnimation(fig_gauge, animate_gauge, frames=50, interval=20, blit=False, repeat=False)

canvas_gauge = FigureCanvasTkAgg(fig_gauge, master=balance_frame)
canvas_gauge.draw()
canvas_gauge.get_tk_widget().pack(pady=10)

tk.Label(balance_frame, text=f"{latest_percent_saved:.1f}% ↑", bg="#90ee90", fg="black", font=("Arial", 14), pady=5).pack()
tk.Label(balance_frame, text=f"{latest_balance:.2f} R$", bg="#90ee90", fg="black", font=("Arial", 24, "bold"), pady=5).pack()
tk.Label(balance_frame, text=f"Avg balance: {avg_balance:.2f} R$", bg="#90ee90", fg="black", font=("Arial", 10), pady=5).pack()

# Recent Transactions Card (Gray gradient, top-right)
trans_frame = ttk.Frame(root, style="Card.TFrame")
trans_frame.place(x=600, y=50, width=500, height=150)
tk.Label(trans_frame, text="Recent Categories", bg="#c0c0c0", fg="black", font=("Arial", 14, "bold"), padx=10, pady=5).pack()
for cat, val in df[categories].iloc[-1].items():
    if val > 0:
        tk.Label(trans_frame, text=f"{cat}: {val:.2f} R$", bg="#c0c0c0", fg="black", padx=10).pack()

# Savings Forecast Card (Green gradient, right)
forecast_frame = ttk.Frame(root, style="Card.TFrame")
forecast_frame.place(x=600, y=220, width=500, height=400)
tk.Label(forecast_frame, text="Savings Forecast", bg="#90ee90", fg="black", font=("Arial", 16, "bold"), padx=10, pady=5).pack()

# Timeline chart (animated line)
fig_forecast, ax_forecast = plt.subplots(figsize=(4.5, 3.5), facecolor='#90ee90')
ax_forecast.set_facecolor('#90ee90')
line, = ax_forecast.plot([], [], color='#1a1a1a', marker='o', markersize=8)
ax_forecast.set_xlim(0, len(years)-1)
ax_forecast.set_ylim(0, max(projected_savings)*1.2)
ax_forecast.set_xticks(range(len(years)))
ax_forecast.set_xticklabels(years, fontsize=10)
ax_forecast.tick_params(colors='#1a1a1a')
for i, desc in enumerate(forecast_descriptions):
    ax_forecast.text(i, projected_savings[i-1] if i>0 else 0, desc, fontsize=9, color='#1a1a1a', ha='center')

def animate_forecast(frame):
    x = range(0, min(frame//10 + 1, len(years)))
    y = projected_savings[:len(x)]
    line.set_data(x, y)
    return line,

anim_forecast = FuncAnimation(fig_forecast, animate_forecast, frames=50, interval=50, blit=True, repeat=False)

canvas_forecast = FigureCanvasTkAgg(fig_forecast, master=forecast_frame)
canvas_forecast.draw()
canvas_forecast.get_tk_widget().pack(pady=10)

tk.Label(forecast_frame, text=f"Projected 2028: {projected_savings[-1]:.0f} R$", bg="#90ee90", fg="black", font=("Arial", 14), pady=5).pack()

# Suggestions Section (Purple gradient, bottom-right)
suggest_frame = ttk.Frame(root, style="Card.TFrame")
suggest_frame.place(x=600, y=630, width=500, height=150)
tk.Label(suggest_frame, text="Suggestions", bg="#dda0dd", fg="black", font=("Arial", 14, "bold"), padx=10, pady=5).pack()
tk.Label(suggest_frame, text="Reduce spending in:", bg="#dda0dd", fg="black", padx=10).pack()
tk.Label(suggest_frame, text=', '.join(suggestions), bg="#dda0dd", fg="black", padx=10, pady=5).pack()

root.mainloop()