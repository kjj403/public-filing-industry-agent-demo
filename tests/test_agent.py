import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent import analyze_document, attach_reviews, split_sentences


class AgentTest(unittest.TestCase):
    def test_sentence_split_and_multiple_activities(self):
        text = "전자부품을 제조합니다. 소프트웨어 플랫폼을 개발합니다."
        self.assertEqual(len(split_sentences(text)), 2)
        result = analyze_document("SYN-1", "합성기업", text)
        self.assertEqual(len(result["activities"]), 2)

    def test_candidate_contains_explainable_evidence(self):
        result = analyze_document("SYN-2", "합성기업", "반도체 센서 모듈을 제조합니다.")
        candidate = result["activities"][0]["candidates"][0]
        self.assertIn("반도체", candidate["matched_keywords"])
        self.assertEqual(candidate["evidence"], "반도체 센서 모듈을 제조합니다.")

    def test_human_review_is_attached(self):
        result = analyze_document("SYN-3", "합성기업", "전자장비를 판매합니다.")
        reviewed = attach_reviews(result, [{"activity_id": "ACT-01", "action": "approve", "selected_code": "D-4652", "note": "근거 확인"}])
        self.assertEqual(reviewed["activities"][0]["human_review"]["action"], "approve")


if __name__ == "__main__":
    unittest.main()

