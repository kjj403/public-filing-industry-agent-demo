import re
from dataclasses import asdict, dataclass


CATALOG = [
    {
        "code": "D-2611",
        "label": "전자부품 제조",
        "keywords": ["반도체", "센서", "전자부품", "모듈", "제조"],
    },
    {
        "code": "D-4652",
        "label": "전자장비 도매",
        "keywords": ["도매", "유통", "판매", "수출", "전자장비"],
    },
    {
        "code": "D-7212",
        "label": "공학 연구개발",
        "keywords": ["연구", "개발", "설계", "시험", "기술"],
    },
    {
        "code": "D-6201",
        "label": "소프트웨어 개발",
        "keywords": ["소프트웨어", "플랫폼", "솔루션", "데이터", "클라우드"],
    },
]


@dataclass
class Candidate:
    code: str
    label: str
    score: float
    matched_keywords: list[str]
    evidence: str


def split_sentences(text: str) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return []
    return [s.strip() for s in re.split(r"(?<=[.!?다])\s+|\n+", cleaned) if s.strip()]


def extract_activities(text: str) -> list[dict]:
    activities = []
    for index, sentence in enumerate(split_sentences(text), start=1):
        candidates = []
        for item in CATALOG:
            matches = [word for word in item["keywords"] if word in sentence]
            if not matches:
                continue
            score = min(0.98, 0.48 + 0.11 * len(matches))
            candidates.append(
                Candidate(
                    code=item["code"],
                    label=item["label"],
                    score=round(score, 2),
                    matched_keywords=matches,
                    evidence=sentence,
                )
            )
        if candidates:
            candidates.sort(key=lambda x: (-x.score, x.code))
            activities.append(
                {
                    "activity_id": f"ACT-{index:02d}",
                    "source_sentence": sentence,
                    "candidates": [asdict(candidate) for candidate in candidates[:3]],
                }
            )
    return activities


def analyze_document(company_id: str, company_name: str, text: str) -> dict:
    return {
        "company_id": company_id,
        "company_name": company_name,
        "source_type": "synthetic_public_filing",
        "activities": extract_activities(text),
        "notice": "Demo candidates require human review and are not official classifications.",
    }


def attach_reviews(result: dict, reviews: list[dict]) -> dict:
    valid_actions = {"approve", "modify", "hold"}
    review_map = {}
    for review in reviews:
        if review.get("action") not in valid_actions:
            raise ValueError("action must be approve, modify, or hold")
        review_map[review["activity_id"]] = {
            "action": review["action"],
            "selected_code": review.get("selected_code", ""),
            "note": review.get("note", "").strip(),
        }
    enriched = {**result, "activities": []}
    for activity in result["activities"]:
        enriched["activities"].append(
            {**activity, "human_review": review_map.get(activity["activity_id"])}
        )
    return enriched

