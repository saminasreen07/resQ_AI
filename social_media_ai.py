"""
ResQAI TN - Social Media Disaster Detection
Simulates real-time Twitter/X monitoring for Tamil Nadu disaster signals
"""
import random
from datetime import datetime, timedelta

# Simulated tweet templates for TN districts
TWEET_TEMPLATES = [
    {
        "user": "@tnresident_{id}",
        "text": "Heavy flooding in {district}! Water entered homes. People stranded. Need help urgently! #TamilNaduFloods #SOS",
        "type": "Flood",
        "severity": "HIGH",
        "keywords": ["flooding", "stranded", "sos"]
    },
    {
        "user": "@fisherman_{id}",
        "text": "Cyclone warning near {district} coast. Strong winds since morning. Fishermen requested not to go to sea. #CycloneAlert",
        "type": "Cyclone",
        "severity": "MEDIUM",
        "keywords": ["cyclone", "winds", "coastal"]
    },
    {
        "user": "@tnresident_{id}",
        "text": "URGENT: Building collapse in {district}. People trapped inside! Send rescue teams now! #Earthquake #TNDisaster",
        "type": "Earthquake",
        "severity": "CRITICAL",
        "keywords": ["collapse", "trapped", "urgent"]
    },
    {
        "user": "@localreporter_{id}",
        "text": "Landslide on Nilgiris highway near {district}. Traffic blocked. Few vehicles may be buried. NDRF needed.",
        "type": "Landslide",
        "severity": "HIGH",
        "keywords": ["landslide", "blocked", "buried"]
    },
    {
        "user": "@villager_{id}",
        "text": "Fire broke out in {district} market area. Spreading fast! Fire brigade not reached yet. Many shops on fire!",
        "type": "Fire",
        "severity": "HIGH",
        "keywords": ["fire", "spreading", "shops"]
    },
    {
        "user": "@tnresident_{id}",
        "text": "Unusual sea waves seen near {district} coast. People running away. Is this tsunami? Scared! #TsunamiAlert",
        "type": "Tsunami",
        "severity": "CRITICAL",
        "keywords": ["waves", "tsunami", "coast"]
    },
    {
        "user": "@newstn_{id}",
        "text": "Flash flood warning for {district} district. IMD issued red alert. Residents asked to move to higher ground. #RedAlert",
        "type": "Flood",
        "severity": "CRITICAL",
        "keywords": ["flash flood", "red alert", "evacuate"]
    },
    {
        "user": "@tnfamily_{id}",
        "text": "Our entire street in {district} is underwater. Kids and elderly cant move. Please send boats and food. #FloodRelief",
        "type": "Flood",
        "severity": "HIGH",
        "keywords": ["underwater", "kids", "elderly", "food"]
    },
    {
        "user": "@localresident_{id}",
        "text": "Power cut in entire {district} area after storm. No mobile signal. This is being sent from terrace. Send help!",
        "type": "Cyclone",
        "severity": "MEDIUM",
        "keywords": ["power cut", "storm", "signal"]
    },
    {
        "user": "@tnfarmer_{id}",
        "text": "River near {district} overflowing. Crops destroyed. Cattle washed away. Village may be submerged by night.",
        "type": "Flood",
        "severity": "HIGH",
        "keywords": ["overflowing", "submerged", "village"]
    }
]

TN_DISTRICTS = [
    "Chennai", "Cuddalore", "Nilgiris", "Thanjavur", "Kanyakumari",
    "Madurai", "Vellore", "Coimbatore", "Tirunelveli", "Salem",
    "Tiruchirappalli", "Tiruppur", "Erode", "Dindigul", "Thoothukudi",
    "Ramanathapuram", "Pudukkottai", "Nagapattinam", "Villupuram"
]


def generate_simulated_tweets(n=12):
    """Generate a list of simulated disaster-related tweets."""
    tweets = []
    now = datetime.now()

    for i in range(n):
        template = random.choice(TWEET_TEMPLATES)
        district = random.choice(TN_DISTRICTS)
        user_id = random.randint(100, 999)
        minutes_ago = random.randint(1, 120)
        timestamp = now - timedelta(minutes=minutes_ago)

        tweet = {
            "user": template["user"].format(id=user_id),
            "text": template["text"].format(district=district),
            "district": district,
            "type": template["type"],
            "severity": template["severity"],
            "keywords": template["keywords"],
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M"),
            "minutes_ago": minutes_ago,
            "likes": random.randint(5, 500),
            "retweets": random.randint(2, 200),
            "flagged": template["severity"] in ["HIGH", "CRITICAL"],
            "verified_report": random.random() > 0.7
        }
        tweets.append(tweet)

    # Sort by severity and recency
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    tweets.sort(key=lambda x: (severity_order.get(x["severity"], 3), x["minutes_ago"]))

    return tweets


def get_critical_social_alerts(tweets=None):
    """Filter only critical/high severity alerts from social feeds."""
    if tweets is None:
        tweets = generate_simulated_tweets()
    return [t for t in tweets if t["severity"] in ["CRITICAL", "HIGH"]]


def detect_trending_districts(tweets=None):
    """Detect which districts are trending in social disaster mentions."""
    if tweets is None:
        tweets = generate_simulated_tweets(20)

    district_count = {}
    for tweet in tweets:
        d = tweet["district"]
        district_count[d] = district_count.get(d, 0) + 1

    return sorted(district_count.items(), key=lambda x: x[1], reverse=True)[:5]


def get_disaster_type_distribution(tweets=None):
    """Get breakdown of disaster types from social feed."""
    if tweets is None:
        tweets = generate_simulated_tweets()

    dist = {}
    for t in tweets:
        dist[t["type"]] = dist.get(t["type"], 0) + 1
    return dist
