"""
Generate tables and charts for Chapter 3 write-up.
Run after 24-hour simulation to produce:
- Table 1: Energy Consumption by Room and Appliance (24-Hour Period)
- Table 2: Savings Comparison (With vs Without SHEMS)
- Table 3: Database Statistics (Readings Logged, Events Recorded)
- Chart images for energy by room, by appliance, and savings comparison
"""
import os
import sys

# Add parent so we can import analytics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analytics

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_table1():
    """Table 1: Energy Consumption by Room and Appliance (24-Hour Period)"""
    data = analytics.get_energy_by_room()
    lines = [
        "Table 1: Energy Consumption by Room and Appliance (24-Hour Period)",
        "",
        "| Room       | AC (kWh) | Light (kWh) | Total (kWh) |",
        "|------------|----------|-------------|-------------|",
    ]
    for row in data:
        lines.append(
            f"| {row['room_id']:<10} | {row['AC']:>8.4f} | {row['Light']:>11.4f} | {row['total']:>11.4f} |"
        )
    if data:
        totals = analytics.get_energy_by_appliance()
        lines.append(f"| {'Total':<10} | {totals['AC']:>8.4f} | {totals['Light']:>11.4f} | {totals['total']:>11.4f} |")
    return "\n".join(lines)


def generate_table2():
    """Table 2: Savings Comparison (With vs Without SHEMS)"""
    s = analytics.get_savings_comparison()
    lines = [
        "Table 2: Savings Comparison (With vs Without SHEMS)",
        "",
        "| Metric              | Value    |",
        "|---------------------|----------|",
        f"| With SHEMS (kWh)    | {s['with_shems_kwh']:>8.4f} |",
        f"| Without SHEMS (kWh) | {s['without_shems_kwh']:>8.4f} |",
        f"| Saved (kWh)         | {s['saved_kwh']:>8.4f} |",
        f"| Savings (%)         | {s['savings_percent']:>7.1f}% |",
    ]
    return "\n".join(lines)


def generate_table3():
    """Table 3: Database Statistics (Readings Logged, Events Recorded)"""
    stats = analytics.get_db_statistics()
    lines = [
        "Table 3: Database Statistics (Readings Logged, Events Recorded)",
        "",
        "| Table         | Count |",
        "|---------------|-------|",
        f"| sensor_log    | {stats['sensor_log']:>5} |",
        f"| appliance_log | {stats['appliance_log']:>5} |",
        f"| energy_log    | {stats['energy_log']:>5} |",
    ]
    return "\n".join(lines)


def save_tables():
    """Write all tables to output/tables.md"""
    path = os.path.join(OUTPUT_DIR, "tables.md")
    content = "\n\n".join([generate_table1(), generate_table2(), generate_table3()])
    with open(path, "w") as f:
        f.write(content)
    print(f"Tables saved to {path}")
    return path


def save_charts():
    """Export energy charts as PNG images."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed. Run: pip install matplotlib")
        return []

    by_room = analytics.get_energy_by_room()
    by_app = analytics.get_energy_by_appliance()
    savings = analytics.get_savings_comparison()

    saved = []

    # Chart 1: Energy by room (bar)
    if by_room:
        fig, ax = plt.subplots(figsize=(8, 5))
        rooms = [r["room_id"] for r in by_room]
        ac_vals = [r["AC"] for r in by_room]
        light_vals = [r["Light"] for r in by_room]
        x = range(len(rooms))
        w = 0.35
        ax.bar([i - w / 2 for i in x], ac_vals, w, label="AC")
        ax.bar([i + w / 2 for i in x], light_vals, w, label="Light")
        ax.set_xticks(x)
        ax.set_xticklabels(rooms)
        ax.set_ylabel("Energy (kWh)")
        ax.set_title("Figure 1: Energy Consumption by Room and Appliance (24-Hour Period)")
        ax.legend()
        ax.grid(axis="y", alpha=0.3)
        p1 = os.path.join(OUTPUT_DIR, "chart_energy_by_room.png")
        plt.tight_layout()
        plt.savefig(p1, dpi=150)
        plt.close()
        saved.append(p1)
        print(f"Chart saved: {p1}")

    # Chart 2: Energy by appliance (bar)
    fig, ax = plt.subplots(figsize=(6, 4))
    apps = ["AC", "Light"]
    vals = [by_app["AC"], by_app["Light"]]
    bars = ax.bar(apps, vals, color=["#2ecc71", "#3498db"])
    ax.set_ylabel("Energy (kWh)")
    ax.set_title("Figure 2: Energy Consumption by Appliance Type")
    ax.grid(axis="y", alpha=0.3)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.05, f"{v:.2f}", ha="center", fontsize=10)
    p2 = os.path.join(OUTPUT_DIR, "chart_energy_by_appliance.png")
    plt.tight_layout()
    plt.savefig(p2, dpi=150)
    plt.close()
    saved.append(p2)
    print(f"Chart saved: {p2}")

    # Chart 3: Savings comparison (bar)
    fig, ax = plt.subplots(figsize=(6, 4))
    labels = ["With SHEMS", "Without SHEMS"]
    vals = [savings["with_shems_kwh"], savings["without_shems_kwh"]]
    colors = ["#2ecc71", "#e74c3c"]
    bars = ax.bar(labels, vals, color=colors)
    ax.set_ylabel("Energy (kWh)")
    ax.set_title("Figure 3: Savings Comparison (With vs Without SHEMS)")
    ax.grid(axis="y", alpha=0.3)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.05, f"{v:.2f}", ha="center", fontsize=10)
    p3 = os.path.join(OUTPUT_DIR, "chart_savings_comparison.png")
    plt.tight_layout()
    plt.savefig(p3, dpi=150)
    plt.close()
    saved.append(p3)
    print(f"Chart saved: {p3}")

    return saved


def main():
    print("Generating report...")
    save_tables()
    save_charts()
    print(f"\nOutput directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
