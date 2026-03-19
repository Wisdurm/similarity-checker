from difflib import SequenceMatcher
from itertools import combinations
from pathlib import Path
import copy

def compare_all_files(files: list[Path], threshold: float) -> dict[Path, dict[Path, float]]:
    """
    Compare all files in the list against eachother

    :returns: A dict which tells the similarity between all files compared to one
    """
    results: dict[Path, dict[Path, float]] = {}

    for com in combinations(files, 2):
        try:
            diff: float = file_difference(com)
        except FileNotFoundError:
            print(f'ERROR: {com[0]} and {com[1]}')
            continue
        if diff >= threshold:
            file1 = com[0]
            file2 = com[1]
            # Initialize empty dict
            try:
                results[file1]
            except:
                results[file1] = {}
            # Write results
            results[file1][file2] = diff

    # Duplicate identical results
    d_results = copy.deepcopy(results)
    for k1, v1 in results.items():
        for k2, v2 in v1.items():
            try:
                d_results[k2][k1] = v2
            except KeyError:
                d_results[k2] = {}
                d_results[k2][k1] = v2
    # Sort by value
    sorted_results = {}
    for key, value in d_results.items():
        sorted_results[key] = dict(sorted(value.items(), key=lambda item: item[1], reverse=True))

    return sorted_results

def file_difference(files: tuple[Path, Path]) -> float:
    """
    Calculate the percentage difference between two files
    """
    txt1: str = ""
    txt2: str = ""

    with open(files[0]) as f:
        txt1 = f.read()
    with open(files[1]) as f:
        txt2 = f.read()

    return SequenceMatcher(None, txt1, txt2).ratio()
