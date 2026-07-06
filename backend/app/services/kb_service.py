from typing import List, Dict, Any

KNOWLEDGE_BASE = [
    {
        "id": "kb_colored_water",
        "category": "water_appearance",
        "keywords": ["brown", "cloudy", "smelly", "colored", "color", "dirty", "smell", "odor", "rust", "yellow", "dark"],
        "title": "Handling Brown, Cloudy, or Smelly Water",
        "guidance": "If water is brown, cloudy, or has an unusual smell/odor, do not use it for drinking, cooking, or brushing teeth. Particles can be settled by letting the water stand in a clean, covered container. Simple boiling will kill bacteria/viruses but will NOT remove heavy metals, rust, or chemical contaminants. Use a fine cloth, sand, or ceramic filter to remove sediment, but prioritize using alternative bottled or municipal water."
    },
    {
        "id": "kb_contamination",
        "category": "contamination",
        "keywords": ["contamination", "contaminated", "poison", "chemical", "oil", "sewage", "sickness", "diarrhea", "illness", "toxic"],
        "title": "Suspected Biological or Chemical Water Contamination",
        "guidance": "If you suspect sewage, oil, chemical spill, or biological contamination: STOP using the water source immediately for all purposes, including washing hands and bathing. Boiling does NOT make chemically contaminated water safe. Store a supply of certified safe water (bottled or trucked). Alert your local health department or community water committee immediately. Keep children and animals away from the water source."
    },
    {
        "id": "kb_broken_infrastructure",
        "category": "infrastructure",
        "keywords": ["broken", "borehole", "tap", "pump", "pipe", "leak", "rupture", "dry", "well", "maintenance"],
        "title": "Broken Boreholes, Taps, Pumps, or Pipes",
        "guidance": "For physical infrastructure damage (broken pumps, leaking pipes, dry boreholes): Report the exact location and description of the damage to the local water support team or municipal service line. Conserve existing clean water stores immediately. If forced to use secondary sources like rivers or shallow wells, treat the water via boiling (1 full minute rolling boil) or chlorine tablets before consumption."
    },
    {
        "id": "kb_water_shortage",
        "category": "shortage",
        "keywords": ["shortage", "no water", "dry", "three days", "days", "rationing", "empty", "drought"],
        "title": "Water Shortages and Supply Outages",
        "guidance": "During water outages lasting one or more days: Restrict water use to essential drinking, cooking, and basic hygiene. Keep water stored in clean, tightly closed containers to prevent contamination. If you must collect water from unverified open sources, treat it by boiling or using water purification tablets. Avoid using shared water points that are showing signs of drying up."
    },
    {
        "id": "kb_queues_safety",
        "category": "safety",
        "keywords": ["queue", "queuing", "line", "unsafe", "wait", "waiting", "conflict", "crowd", "fight"],
        "title": "Safe Water Collection and Queue Management",
        "guidance": "When water points have long, unsafe queues: Avoid collecting water during late night or pre-dawn hours when security risks are highest. Coordinate collection in groups, especially for women and children. If tension or conflicts arise in the queue, report to local community leaders. Encourage the water committee to establish timed rosters or maximum limits per household to ensure equitable access."
    },
    {
        "id": "kb_escalation",
        "category": "escalation",
        "keywords": ["escalate", "authority", "health", "hospital", "doctor", "government", "committee", "emergency"],
        "title": "When to Escalate to Authorities or Health Services",
        "guidance": "Escalate immediately if: Multiple people in the community experience symptoms of waterborne illness (e.g., severe diarrhea, vomiting, stomach cramps) after drinking the water. Escalate if water quality remains poor at critical locations like schools, hospitals, or clinics. Contact the local health department, municipal water engineers, or community leaders with structured case details."
    }
]

def search_kb(query: str) -> List[Dict[str, Any]]:
    """Searches the knowledge base for articles matching query terms."""
    if not query:
        return []
    
    query_lower = query.lower()
    scored_results = []
    
    for article in KNOWLEDGE_BASE:
        score = 0
        # Direct keyword match
        for word in article["keywords"]:
            if word in query_lower:
                score += 3
        # Title words match
        for word in article["title"].lower().split():
            if len(word) > 3 and word in query_lower:
                score += 2
        # Category match
        if article["category"] in query_lower:
            score += 1
            
        if score > 0:
            scored_results.append((score, article))
            
    # Sort by score descending
    scored_results.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored_results]
