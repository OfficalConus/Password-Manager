import string
from .lang import tr_strength


def calculate_strength(password: str):
    length = len(password)
    score = 0
    if length >= 8: score += 1
    if length >= 12: score += 1
    if length >= 16: score += 1
    if length >= 24: score += 1
    if any(c.islower() for c in password) and any(c.isupper() for c in password): score += 1
    if any(c.isdigit() for c in password): score += 1
    if any(c in string.punctuation for c in password): score += 1
    ratio = len(set(password)) / len(password)
    if ratio > 0.6: score += 1
    if ratio > 0.8: score += 1

    colors = ["#f44336", "#ff9800", "#4caf50", "#2196f3"]
    idx = min(score // 2, 3)
    return tr_strength(idx), colors[idx], (idx + 1) * 25
