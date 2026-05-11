import sys
import time
import psutil


DELTA = 30
ALPHA = {
    "A": {"A": 0, "C": 110, "G": 48, "T": 94},
    "C": {"A": 110, "C": 0, "G": 118, "T": 48},
    "G": {"A": 48, "C": 118, "G": 0, "T": 110},
    "T": {"A": 94, "C": 48, "G": 110, "T": 0},
}


def parse_input(file_path):
    with open(file_path, "r", encoding="utf-8") as input_file:
        lines = [line.strip() for line in input_file if line.strip()]

    base_strings = []
    index_groups = []

    for line in lines:
        if all(ch in "ACGT" for ch in line):
            base_strings.append(line)
            index_groups.append([])
        elif line.isdigit():
            index_groups[-1].append(int(line))

    return (
        generate_string(base_strings[0], index_groups[0]),
        generate_string(base_strings[1], index_groups[1]),
    )


def generate_string(base, indices):
    result = base
    for index in indices:
        result = result[: index + 1] + result + result[index + 1 :]
    return result


def alignment_cost(aligned_x, aligned_y):
    total = 0
    for a, b in zip(aligned_x, aligned_y):
        if a == "_" or b == "_":
            total += DELTA
        else:
            total += ALPHA[a][b]
    return total


def base_dp_alignment(x, y):
    m = len(x)
    n = len(y)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        dp[i][0] = i * DELTA
    for j in range(1, n + 1):
        dp[0][j] = j * DELTA

    for i in range(1, m + 1):
        xi = x[i - 1]
        for j in range(1, n + 1):
            dp[i][j] = min(
                dp[i - 1][j - 1] + ALPHA[xi][y[j - 1]],
                dp[i - 1][j] + DELTA,
                dp[i][j - 1] + DELTA,
            )

    aligned_x = []
    aligned_y = []
    i = m
    j = n

    while i > 0 and j > 0:
        mismatch = ALPHA[x[i - 1]][y[j - 1]]
        if dp[i][j] == dp[i - 1][j - 1] + mismatch:
            aligned_x.append(x[i - 1])
            aligned_y.append(y[j - 1])
            i -= 1
            j -= 1
        elif dp[i][j] == dp[i - 1][j] + DELTA:
            aligned_x.append(x[i - 1])
            aligned_y.append("_")
            i -= 1
        else:
            aligned_x.append("_")
            aligned_y.append(y[j - 1])
            j -= 1

    while i > 0:
        aligned_x.append(x[i - 1])
        aligned_y.append("_")
        i -= 1

    while j > 0:
        aligned_x.append("_")
        aligned_y.append(y[j - 1])
        j -= 1

    return "".join(reversed(aligned_x)), "".join(reversed(aligned_y))


def linear_bottom_up(x, y):
    n = len(y)
    previous = [j * DELTA for j in range(n + 1)]
    current = [0] * (n + 1)

    for i, xi in enumerate(x, start=1):
        current[0] = i * DELTA
        for j, yj in enumerate(y, start=1):
            current[j] = min(
                previous[j - 1] + ALPHA[xi][yj],
                previous[j] + DELTA,
                current[j - 1] + DELTA,
            )
        previous, current = current, previous

    return previous


def efficient_alignment(x, y):
    if len(x) == 0:
        return "_" * len(y), y
    if len(y) == 0:
        return x, "_" * len(x)
    if len(x) * len(y) <= 2_000_000:
        return base_dp_alignment(x, y)

    mid = len(x) // 2
    x_left = x[:mid]
    x_right = x[mid:]

    forward = linear_bottom_up(x_left, y)
    backward = linear_bottom_up(x_right[::-1], y[::-1])

    split = min(
        range(len(y) + 1),
        key=lambda q: forward[q] + backward[len(y) - q],
    )

    left_x, left_y = efficient_alignment(x_left, y[:split])
    right_x, right_y = efficient_alignment(x_right, y[split:])

    return left_x + right_x, left_y + right_y


def memory_kb():
    process = psutil.Process()
    memory_info = process.memory_info()
    return int(memory_info.rss / 1024)


def write_output(output_path, cost, aligned_x, aligned_y, time_ms, used_memory_kb):
    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write(f"{cost}\n")
        output_file.write(f"{aligned_x}\n")
        output_file.write(f"{aligned_y}\n")
        output_file.write(f"{time_ms}\n")
        output_file.write(f"{used_memory_kb}\n")


def main():
    if len(sys.argv) != 3:
        sys.exit(1)

    x, y = parse_input(sys.argv[1])

    start = time.time()
    aligned_x, aligned_y = efficient_alignment(x, y)
    end = time.time()

    cost = alignment_cost(aligned_x, aligned_y)
    used_memory_kb = memory_kb()
    write_output(sys.argv[2], cost, aligned_x, aligned_y, (end - start) * 1000, used_memory_kb)


if __name__ == "__main__":
    main()
