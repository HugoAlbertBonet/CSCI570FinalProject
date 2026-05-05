import os  # Provides access to the current process id for memory measurement.
import resource  # Provides a fallback way to measure memory usage.
import sys  # Provides command-line arguments and program exit.
import time  # Provides wall-clock timing for the algorithm.


DELTA = 30  # Gap penalty used whenever one character is aligned with "_".
ALPHA = {  # Mismatch/match penalty table required by the project.
    "A": {"A": 0, "C": 110, "G": 48, "T": 94},  # Costs for aligning A with A/C/G/T.
    "C": {"A": 110, "C": 0, "G": 118, "T": 48},  # Costs for aligning C with A/C/G/T.
    "G": {"A": 48, "C": 118, "G": 0, "T": 110},  # Costs for aligning G with A/C/G/T.
    "T": {"A": 94, "C": 48, "G": 110, "T": 0},  # Costs for aligning T with A/C/G/T.
}  # End of scoring table.


def parse_input(file_path):  # Reads the compressed input file and returns the two generated strings.
    with open(file_path, "r", encoding="utf-8") as input_file:  # Opens the input file safely.
        lines = [line.strip() for line in input_file if line.strip()]  # Removes empty lines and whitespace.

    base_strings = []  # Stores the two base strings found in the file.
    index_groups = []  # Stores one list of insertion indices for each base string.
    current_indices = None  # Points to the index list currently being filled.

    for line in lines:  # Processes each non-empty line in order.
        if all(ch in "ACGT" for ch in line):  # Detects a base DNA string.
            base_strings.append(line)  # Saves the base string.
            current_indices = []  # Starts a new index list for this base string.
            index_groups.append(current_indices)  # Saves that index list.
        elif line.isdigit() and current_indices is not None:  # Detects an insertion index.
            current_indices.append(int(line))  # Adds the index to the active base string.
        else:  # Handles invalid lines.
            raise ValueError("Invalid input format")  # Stops if the input does not match the expected format.

    if len(base_strings) != 2:  # Verifies that exactly two base strings were provided.
        raise ValueError("Input must contain exactly two base strings")  # Stops on malformed input.

    return (  # Returns the final expanded strings.
        generate_string(base_strings[0], index_groups[0]),  # Generates the first final string.
        generate_string(base_strings[1], index_groups[1]),  # Generates the second final string.
    )  # End of return tuple.


def generate_string(base, indices):  # Expands one base string using its insertion indices.
    result = base  # Starts with the original base string.
    for index in indices:  # Applies every insertion operation in order.
        result = result[: index + 1] + result + result[index + 1 :]  # Inserts a copy after index i.
    return result  # Returns the fully generated string.


def alpha_cost(a, b):  # Looks up the cost of aligning two DNA characters.
    return ALPHA[a][b]  # Returns the value from the mismatch table.


def basic_alignment(x, y):  # Computes an optimal alignment using the full DP matrix.
    m = len(x)  # Stores the length of the first generated string.
    n = len(y)  # Stores the length of the second generated string.
    dp = [[0] * (n + 1) for _ in range(m + 1)]  # Allocates the full (m+1) by (n+1) DP table.

    for i in range(1, m + 1):  # Initializes the first column for aligning prefixes of x with gaps.
        dp[i][0] = i * DELTA  # Cost of aligning i characters of x with i gaps.
    for j in range(1, n + 1):  # Initializes the first row for aligning prefixes of y with gaps.
        dp[0][j] = j * DELTA  # Cost of aligning j characters of y with j gaps.

    # DP formula used:
    # dp[i][j] = min(
    #     dp[i-1][j-1] + alpha[x[i-1]][y[j-1]],  # align both characters
    #     dp[i-1][j] + delta,                    # align x[i-1] with "_"
    #     dp[i][j-1] + delta                     # align "_" with y[j-1]
    # )
    for i in range(1, m + 1):  # Fills the table row by row.
        xi = x[i - 1]  # Caches the current character from x.
        for j in range(1, n + 1):  # Fills every column in the current row.
            dp[i][j] = min(  # Chooses the cheapest of match/mismatch, x-gap, and y-gap.
                dp[i - 1][j - 1] + alpha_cost(xi, y[j - 1]),  # Cost of aligning x[i-1] with y[j-1].
                dp[i - 1][j] + DELTA,  # Cost of aligning x[i-1] with a gap.
                dp[i][j - 1] + DELTA,  # Cost of aligning a gap with y[j-1].
            )  # End of recurrence calculation.

    aligned_x = []  # Stores the reconstructed alignment for x in reverse order.
    aligned_y = []  # Stores the reconstructed alignment for y in reverse order.
    i = m  # Starts backtracking at the last row.
    j = n  # Starts backtracking at the last column.

    while i > 0 and j > 0:  # Backtracks while both strings still have characters left.
        mismatch = alpha_cost(x[i - 1], y[j - 1])  # Computes the diagonal transition cost.
        if dp[i][j] == dp[i - 1][j - 1] + mismatch:  # Checks whether the optimal move was diagonal.
            aligned_x.append(x[i - 1])  # Adds the current x character.
            aligned_y.append(y[j - 1])  # Adds the current y character.
            i -= 1  # Moves one row up.
            j -= 1  # Moves one column left.
        elif dp[i][j] == dp[i - 1][j] + DELTA:  # Checks whether the optimal move came from above.
            aligned_x.append(x[i - 1])  # Adds the current x character.
            aligned_y.append("_")  # Aligns that x character with a gap.
            i -= 1  # Moves one row up.
        else:  # Uses the left move when diagonal and above were not selected.
            aligned_x.append("_")  # Aligns a gap with the current y character.
            aligned_y.append(y[j - 1])  # Adds the current y character.
            j -= 1  # Moves one column left.

    while i > 0:  # Handles leftover x characters after y is exhausted.
        aligned_x.append(x[i - 1])  # Adds the remaining x character.
        aligned_y.append("_")  # Aligns it with a gap.
        i -= 1  # Moves to the previous x character.

    while j > 0:  # Handles leftover y characters after x is exhausted.
        aligned_x.append("_")  # Aligns a gap with the remaining y character.
        aligned_y.append(y[j - 1])  # Adds the remaining y character.
        j -= 1  # Moves to the previous y character.

    used_memory_kb = memory_kb()  # Measures memory while the DP table still exists.
    return dp[m][n], "".join(reversed(aligned_x)), "".join(reversed(aligned_y)), used_memory_kb  # Returns cost, alignments, and memory.


def alignment_cost(aligned_x, aligned_y):  # Recomputes the cost from the final aligned strings.
    total = 0  # Starts the accumulated cost at zero.
    for a, b in zip(aligned_x, aligned_y):  # Visits every aligned character pair.
        if a == "_" or b == "_":  # Detects a gap in either alignment string.
            total += DELTA  # Adds the gap penalty.
        else:  # Handles character-to-character alignment.
            total += alpha_cost(a, b)  # Adds the mismatch or match penalty.
    return total  # Returns the final alignment cost.


def memory_kb():  # Returns the current process memory usage in kilobytes.
    try:  # Tries the preferred psutil method first.
        import psutil  # Imports psutil only if it is installed.

        process = psutil.Process(os.getpid())  # Creates a process object for this Python program.
        return process.memory_info().rss / 1024.0  # Converts resident memory bytes to KB.
    except ImportError:  # Falls back when psutil is unavailable.
        usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss  # Gets max resident set size.
        if sys.platform == "darwin":  # macOS reports ru_maxrss in bytes.
            return usage / 1024.0  # Converts macOS bytes to KB.
        return float(usage)  # Linux already reports ru_maxrss in KB.


def write_output(output_path, cost, aligned_x, aligned_y, time_ms, used_memory_kb):  # Writes the required 5-line output file.
    with open(output_path, "w", encoding="utf-8") as output_file:  # Creates or overwrites the output file.
        output_file.write(f"{cost}\n")  # Line 1: optimal alignment cost.
        output_file.write(f"{aligned_x}\n")  # Line 2: first aligned string.
        output_file.write(f"{aligned_y}\n")  # Line 3: second aligned string.
        output_file.write(f"{time_ms}\n")  # Line 4: algorithm time in milliseconds.
        output_file.write(f"{used_memory_kb}\n")  # Line 5: memory usage in kilobytes.


def main():  # Program entry point.
    if len(sys.argv) != 3:  # Requires exactly input path and output path.
        sys.exit(1)  # Exits silently if arguments are missing or extra.

    x, y = parse_input(sys.argv[1])  # Reads and expands both input strings.

    start = time.time()  # Starts timing immediately before the alignment algorithm.
    _, aligned_x, aligned_y, used_memory_kb = basic_alignment(x, y)  # Runs full-matrix DP alignment.
    end = time.time()  # Stops timing immediately after the algorithm finishes.

    cost = alignment_cost(aligned_x, aligned_y)  # Computes cost from the produced alignment.
    write_output(sys.argv[2], cost, aligned_x, aligned_y, (end - start) * 1000, used_memory_kb)  # Writes the final result.


if __name__ == "__main__":  # Runs main only when this file is executed directly.
    main()  # Starts the program.
