"""
ResQAI TN — AI Team Assignment Engine
assign_team(report, teams) → ranked list of up to 3 best teams
"""
import math

DISASTER_TEAM_MATCH = {
    "Flood":      ["Flood", "General"],
    "Cyclone":    ["Flood", "General"],
    "Fire":       ["Fire", "General"],
    "Landslide":  ["General", "Medical"],
    "Earthquake": ["General", "Medical"],
    "Tsunami":    ["Flood", "General", "Medical"],
}

PRIORITY_URGENCY = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}


def _haversine(lat1, lon1, lat2, lon2) -> float:
    """Distance in km between two lat/lon points."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))


def assign_team(report: dict, teams: list[dict]) -> list[dict]:
    """
    Returns up to 3 ranked team suggestions, each dict contains:
    - team (original team dict)
    - distance_km
    - score
    - reason (human-readable)
    """
    disaster = report.get("disaster", "")
    priority = report.get("priority", "MEDIUM")
    r_lat = float(report.get("lat", 0))
    r_lon = float(report.get("lon", 0))

    preferred_types = DISASTER_TEAM_MATCH.get(disaster, ["General"])
    urgency = PRIORITY_URGENCY.get(priority, 2)

    scored = []
    for team in teams:
        if not team.get("is_available", False):
            continue

        t_lat = float(team.get("lat", 0))
        t_lon = float(team.get("lon", 0))
        dist = _haversine(r_lat, r_lon, t_lat, t_lon)

        # Type match bonus
        type_bonus = 0
        t_type = team.get("type", "General")
        if t_type == preferred_types[0]:
            type_bonus = 3
        elif len(preferred_types) > 1 and t_type == preferred_types[1]:
            type_bonus = 2
        elif t_type == "General":
            type_bonus = 1

        # Distance score (closer = higher score, max 5 pts for <10 km)
        if dist < 10:   dist_score = 5
        elif dist < 30: dist_score = 4
        elif dist < 60: dist_score = 3
        elif dist < 100:dist_score = 2
        else:           dist_score = 1

        total_score = dist_score + type_bonus + urgency

        # Build reason string
        type_match = "✅ Exact type match" if type_bonus == 3 else ("🔵 Compatible type" if type_bonus >= 1 else "⚠️ General unit")
        dist_label = f"{dist:.1f} km away"
        reason = f"{type_match} · {dist_label} · Priority urgency +{urgency}"

        scored.append({
            "team": team,
            "distance_km": round(dist, 1),
            "score": total_score,
            "reason": reason,
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:3]
