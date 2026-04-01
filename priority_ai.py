"""
ResQAI TN — Priority AI Engine
Calculates report priority: LOW / MEDIUM / HIGH / CRITICAL
"""

DISASTER_BASE_SCORES = {
    "Tsunami":    5,
    "Cyclone":    4,
    "Earthquake": 4,
    "Flood":      3,
    "Fire":       3,
    "Landslide":  2,
}

def calculate_priority(report: dict) -> tuple[str, int]:
    """
    Returns (priority_label, score).
    score range: 0–14
    """
    score = 0
    disaster = report.get("disaster", "")
    score += DISASTER_BASE_SCORES.get(disaster, 1)

    people = int(report.get("people", 1))
    if people >= 500:   score += 4
    elif people >= 100: score += 3
    elif people >= 20:  score += 2
    elif people >= 5:   score += 1

    if report.get("medical", "No") == "Yes":   score += 3
    if report.get("food",    "No") == "Yes":   score += 1
    if report.get("shelter", "No") == "Yes":   score += 1

    if score >= 10:  label = "CRITICAL"
    elif score >= 7: label = "HIGH"
    elif score >= 4: label = "MEDIUM"
    else:            label = "LOW"

    return label, score


PRIORITY_COLORS = {
    "CRITICAL": "#ef4444",
    "HIGH":     "#f97316",
    "MEDIUM":   "#eab308",
    "LOW":      "#22c55e",
}

PRIORITY_RESPONSE = {
    "CRITICAL": "15–30 min",
    "HIGH":     "30–60 min",
    "MEDIUM":   "1–2 hours",
    "LOW":      "2–4 hours",
}

def get_priority_color(p: str) -> str:
    return PRIORITY_COLORS.get(p, "#64748b")

def get_priority_response(p: str) -> str:
    return PRIORITY_RESPONSE.get(p, "TBD")
