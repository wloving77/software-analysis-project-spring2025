_seen_seeds = set()

def is_novel_seed(seed: str) -> bool:
    return seed not in _seen_seeds

def store_seed(seed: str):
    _seen_seeds.add(seed)
