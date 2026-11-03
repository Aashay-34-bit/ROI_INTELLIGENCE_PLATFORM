def score_output(output: str, expected: str) -> float:
    return float(expected.lower() in output.lower())
