"""Generate line plots of CPU time and memory usage vs problem size.

Usage: python3 plot_results.py <results.csv> <output_dir>
"""

import csv
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def load_rows(csv_path):
    with open(csv_path, newline="") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    rows.sort(key=lambda r: int(r["problem_size"]))
    return rows


def make_plot(sizes, basic, efficient, ylabel, title, out_path):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(sizes, basic, marker="o", linewidth=2, label="Basic (Full DP)")
    ax.plot(sizes, efficient, marker="s", linewidth=2, label="Memory-Efficient")
    ax.set_xlabel("Problem Size  (m + n)")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 plot_results.py <results.csv> <output_dir>", file=sys.stderr)
        sys.exit(1)

    csv_path, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)

    rows = load_rows(csv_path)
    sizes = [int(r["problem_size"]) for r in rows]
    basic_time = [float(r["basic_time_ms"]) for r in rows]
    eff_time = [float(r["efficient_time_ms"]) for r in rows]
    basic_mem = [float(r["basic_memory_kb"]) for r in rows]
    eff_mem = [float(r["efficient_memory_kb"]) for r in rows]

    time_path = os.path.join(out_dir, "time_plot.png")
    mem_path = os.path.join(out_dir, "memory_plot.png")

    make_plot(
        sizes,
        basic_time,
        eff_time,
        ylabel="CPU Time (ms)",
        title="CPU Time vs Problem Size",
        out_path=time_path,
    )
    make_plot(
        sizes,
        basic_mem,
        eff_mem,
        ylabel="Memory (KB)",
        title="Memory Usage vs Problem Size",
        out_path=mem_path,
    )

    print(f"Saved time plot:   {time_path}")
    print(f"Saved memory plot: {mem_path}")


if __name__ == "__main__":
    main()
