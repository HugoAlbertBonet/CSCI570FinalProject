"""
Script with everyting needed to run the memory-inefficient algorithm (just DP):
- Read the input:
    - Follow rules to generate the two strings from the input file
- Run the algorithm:
    - Bottom-up 
    - Top-down
- Write the output:
    1. Cost of the alignment (Integer)
    2. First string alignment ( Consists of A, C, T, G, _ (gap) characters)
    3. Second string alignment ( Consists of A, C, T, G, _ (gap) characters )
    4. Time in Milliseconds (Float)
    5. Memory in Kilobytes (Float)

"""

# Hard coded costs
COST = {
        'A': {'A': 0, 'C': 110, 'G': 48, 'T': 94},
        'C': {'A': 110, 'C': 0, 'G': 118, 'T': 48},
        'G': {'A': 48, 'C': 118, 'G': 0, 'T': 110},
        'T': {'A': 94, 'C': 48, 'G': 110, 'T': 0}
    }

class InputParser:
    """
    Class to parse the input file and generate the two strings to be aligned.
    """
    def __init__(self, file_path):
        pass
    
    def parse_input(self):
        pass

class DPAlgorithm:
    """
    Class to implement the memory-inefficient algorithm (just DP):
    - bottom-up
    - top-down
    """
    def __init__(self, string1, string2):
        pass

    def bottom_up(self):
        pass

    def top_down(self):
        pass

class OutputWriter:
    """
    Class to write the output to a file.
    """
    def __init__(self, cost, alignment1, alignment2, time_taken, memory_consumed):
        pass

    def write_output(self):
        pass