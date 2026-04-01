"""
ResQAI TN - Predictive Risk Analysis
Simulates weather-based risk prediction for Tamil Nadu districts
"""
import random
from datetime import datetime

# District-level base risk profiles (based on historical data knowledge)
DISTRICT_RISK_PROFILES = {
    "Chennai":         {"flood": 75, "cyclone": 70, "drought": 20, "landslide": 5,  "earthquake": 15},
    "Cuddalore":       {"flood": 80, "cyclone": 85, "drought": 15, "landslide": 10, "earthquake": 10},
    "Nagapattinam":    {"flood": 85, "cyclone": 90, "drought": 10, "landslide": 5,  "earthquake": 10},
    "Kanyakumari":     {"flood": 60, "cyclone": 65, "drought": 20, "landslide": 40, "earthquake": 20},
    "Nilgiris":        {"flood": 50, "cyclone": 30, "drought": 5,  "landslide": 90, "earthquake": 15},
    "Thanjavur":       {"flood": 70, "cyclone": 65, "drought": 25, "landslide": 5,  "earthquake": 10},
    "Madurai":         {"flood": 45, "cyclone": 35, "drought": 55, "landslide": 20, "earthquake": 20},
    "Coimbatore":      {"flood": 40, "cyclone": 25, "drought": 45, "landslide": 35, "earthquake": 25},
    "Tiruchirappalli": {"flood": 55, "cyclone": 40, "drought": 40, "landslide": 10, "earthquake": 15},
    "Vellore":         {"flood": 50, "cyclone": 35, "drought": 40, "landslide": 25, "earthquake": 20},
    "Salem":           {"flood": 45, "cyclone": 25, "drought": 50, "landslide": 30, "earthquake": 20},
    "Tirunelveli":     {"flood": 65, "cyclone": 60, "drought": 30, "landslide": 25, "earthquake": 15},
    "Thoothukudi":     {"flood": 55, "cyclone": 70, "drought": 35, "landslide": 5,  "earthquake": 10},
    "Tiruppur":        {"flood": 40, "cyclone": 20, "drought": 50, "landslide": 30, "earthquake": 20},
    "Erode":           {"flood": 45, "cyclone": 20, "drought": 55, "landslide": 25, "earthquake": 15},
    "Dindigul":        {"flood": 50, "cyclone": 30, "drought": 45, "landslide": 40, "earthquake": 20},
    "Ramanathapuram":  {"flood": 60, "cyclone": 75, "drought": 40, "landslide": 5,  "earthquake": 10},
    "Pudukkottai":     {"flood": 55, "cyclone": 50, "drought": 35, "landslide": 15, "earthquake": 10},
    "Villupuram":      {"flood": 65, "cyclone": 55, "drought": 30, "landslide": 15, "earthquake": 10},
    "Krishnagiri":     {"flood": 40, "cyclone": 20, "drought": 60, "landslide": 35, "earthquake": 20},
    "Dharmapuri":      {"flood": 40, "cyclone": 15, "drought": 65, "landslide": 30, "earthquake": 15},
    "Namakkal":        {"flood": 45, "cyclone": 20, "drought": 55, "landslide": 25, "earthquake": 15},
    "Karur":           {"flood": 50, "cyclone": 25, "drought": 45, "landslide": 15, "earthquake": 10},
    "Ariyalur":        {"flood": 60, "cyclone": 50, "drought": 35, "landslide": 10, "earthquake": 10},
    "Perambalur":      {"flood": 55, "cyclone": 40, "drought": 45, "landslide": 10, "earthquake": 10},
    "Kallakurichi":    {"flood": 55, "cyclone": 40, "drought": 35, "landslide": 20, "earthquake": 15},
    "Ranipet":         {"flood": 50, "cyclone": 35, "drought": 40, "landslide": 20, "earthquake": 20},
    "Tirupattur":      {"flood": 45, "cyclone": 25, "drought": 50, "landslide": 30, "earthquake": 20},
    "Chengalpattu":    {"flood": 65, "cyclone": 60, "drought": 25, "landslide": 15, "earthquake": 15},
    "Sivaganga":       {"flood": 55, "cyclone": 60, "drought": 45, "landslide": 10, "earthquake": 10},
    "Virudhunagar":    {"flood": 55, "cyclone": 55, "drought": 40, "landslide": 20, "earthquake": 10},
    "Tenkasi":         {"flood": 65, "cyclone": 50, "drought": 20, "landslide": 50, "earthquake": 15},
    "Tiruvarur":       {"flood": 80, "cyclone": 80, "drought": 15, "landslide": 5,  "earthquake": 10},
    "Mayiladuthurai":  {"flood": 75, "cyclone": 75, "drought": 15, "landslide": 5,  "earthquake": 10},
    "Kancheepuram":    {"flood": 65, "cyclone": 60, "drought": 25, "landslide": 15, "earthquake": 20},
    "Tiruvallur":      {"flood": 65, "cyclone": 60, "drought": 25, "landslide": 10, "earthquake": 15},
    "Tiruvannamalai":  {"flood": 50, "cyclone": 35, "drought": 45, "landslide": 25, "earthquake": 20},
    "Theni":           {"flood": 55, "cyclone": 35, "drought": 40, "landslide": 45, "earthquake": 20},
}


def get_risk_level(score):
    """Convert numeric score to risk level label."""
    if score >= 75:
        return "CRITICAL", "#FF2D2D"
    elif score >= 55:
        return "HIGH", "#FF6B00"
    elif score >= 35:
        return "MEDIUM", "#FFD700"
    else:
        return "LOW", "#00C851"


def get_simulated_weather(district):
    """Get simulated current weather data for a district."""
    # Add seasonal variation (NE monsoon - Oct to Dec)
    month = datetime.now().month
    monsoon_boost = 15 if month in [10, 11, 12] else (10 if month in [6, 7, 8, 9] else 0)

    base = DISTRICT_RISK_PROFILES.get(district, {
        "flood": 40, "cyclone": 30, "drought": 40,
        "landslide": 20, "earthquake": 10
    })

    rainfall_mm = random.randint(20, 200) + (monsoon_boost * 3)
    temp_c = random.uniform(24, 38)
    wind_kmh = random.randint(10, 90)
    humidity = random.randint(55, 95)

    return {
        "rainfall_mm": rainfall_mm,
        "temperature_c": round(temp_c, 1),
        "wind_kmh": wind_kmh,
        "humidity_pct": humidity,
        "monsoon_active": month in [6, 7, 8, 9, 10, 11, 12]
    }


def predict_district_risks(district):
    """
    Predict risk levels for a district based on weather and historical patterns.
    Returns full risk assessment.
    """
    base = DISTRICT_RISK_PROFILES.get(district, {
        "flood": 40, "cyclone": 30, "drought": 40,
        "landslide": 20, "earthquake": 10
    })
    weather = get_simulated_weather(district)

    # Adjust scores based on current weather simulation
    rainfall_factor = min(weather["rainfall_mm"] / 150, 1.0)
    wind_factor = min(weather["wind_kmh"] / 80, 1.0)

    flood_score = min(100, int(base["flood"] * (1 + rainfall_factor * 0.4)))
    cyclone_score = min(100, int(base["cyclone"] * (1 + wind_factor * 0.3)))
    landslide_score = min(100, int(base["landslide"] * (1 + rainfall_factor * 0.5)))
    earthquake_score = min(100, int(base["earthquake"] * (1 + random.uniform(0, 0.2))))
    drought_score = max(0, int(base["drought"] * (1 - rainfall_factor * 0.5)))

    risks = {
        "flood": {
            "score": flood_score,
            "level": get_risk_level(flood_score)[0],
            "color": get_risk_level(flood_score)[1]
        },
        "cyclone": {
            "score": cyclone_score,
            "level": get_risk_level(cyclone_score)[0],
            "color": get_risk_level(cyclone_score)[1]
        },
        "landslide": {
            "score": landslide_score,
            "level": get_risk_level(landslide_score)[0],
            "color": get_risk_level(landslide_score)[1]
        },
        "earthquake": {
            "score": earthquake_score,
            "level": get_risk_level(earthquake_score)[0],
            "color": get_risk_level(earthquake_score)[1]
        },
        "drought": {
            "score": drought_score,
            "level": get_risk_level(drought_score)[0],
            "color": get_risk_level(drought_score)[1]
        }
    }

    return {
        "district": district,
        "weather": weather,
        "risks": risks,
        "overall_alert": any(r["level"] in ["HIGH", "CRITICAL"] for r in risks.values())
    }


def get_statewide_risk_summary():
    """Get top at-risk districts across Tamil Nadu."""
    high_risk_districts = []
    sample_districts = list(DISTRICT_RISK_PROFILES.keys())[:15]

    for district in sample_districts:
        result = predict_district_risks(district)
        max_score = max(r["score"] for r in result["risks"].values())
        high_risk_districts.append({
            "district": district,
            "max_risk_score": max_score,
            "primary_risk": max(result["risks"].items(), key=lambda x: x[1]["score"])[0],
            "alert_level": get_risk_level(max_score)[0]
        })

    return sorted(high_risk_districts, key=lambda x: x["max_risk_score"], reverse=True)[:8]
