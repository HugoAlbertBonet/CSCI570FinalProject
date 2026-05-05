#!/bin/bash
# Runs basic.sh and efficient.sh on every input file in the Datapoints folder,
# collects the time and memory recorded by each algorithm into a CSV file,
# and produces line plots of the results.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATAPOINTS_DIR="$SCRIPT_DIR/CSCI570_Project_Minimum/Datapoints"
V1_DIR="$SCRIPT_DIR/V1"
RESULTS_DIR="$SCRIPT_DIR/benchmark_results"
RAW_DIR="$RESULTS_DIR/raw"
CSV_FILE="$RESULTS_DIR/results.csv"

if [ ! -d "$DATAPOINTS_DIR" ]; then
    echo "Datapoints directory not found: $DATAPOINTS_DIR" >&2
    exit 1
fi

if [ ! -f "$V1_DIR/basic.sh" ] || [ ! -f "$V1_DIR/efficient.sh" ]; then
    echo "basic.sh or efficient.sh not found in $V1_DIR" >&2
    exit 1
fi

mkdir -p "$RAW_DIR"

# Computes problem size = len(x) + len(y) where x and y are the generated strings.
problem_size() {
    python3 - "$1" <<'PYEOF'
import sys

with open(sys.argv[1]) as fh:
    lines = [line.strip() for line in fh if line.strip()]

bases = []
groups = []
current = None
for line in lines:
    if all(ch in "ACGT" for ch in line):
        bases.append(line)
        current = []
        groups.append(current)
    elif line.isdigit() and current is not None:
        current.append(int(line))

total = sum(len(b) * (2 ** len(g)) for b, g in zip(bases, groups))
print(total)
PYEOF
}

echo "input,problem_size,basic_time_ms,basic_memory_kb,efficient_time_ms,efficient_memory_kb" > "$CSV_FILE"

ls "$DATAPOINTS_DIR"/in*.txt | sort -V | while IFS= read -r input_path; do
    name=$(basename "$input_path" .txt)
    echo "Processing $name..."

    size=$(problem_size "$input_path")

    basic_out="$RAW_DIR/${name}_basic.txt"
    efficient_out="$RAW_DIR/${name}_efficient.txt"

    (cd "$V1_DIR" && bash basic.sh "$input_path" "$basic_out")
    (cd "$V1_DIR" && bash efficient.sh "$input_path" "$efficient_out")

    btime=$(sed -n '4p' "$basic_out")
    bmem=$(sed -n '5p' "$basic_out")
    etime=$(sed -n '4p' "$efficient_out")
    emem=$(sed -n '5p' "$efficient_out")

    echo "  size=$size  basic: ${btime} ms / ${bmem} KB    efficient: ${etime} ms / ${emem} KB"
    echo "$name,$size,$btime,$bmem,$etime,$emem" >> "$CSV_FILE"
done

echo ""
echo "Results written to $CSV_FILE"
echo "Generating plots..."

python3 "$SCRIPT_DIR/plot_results.py" "$CSV_FILE" "$RESULTS_DIR"

echo "Done."
