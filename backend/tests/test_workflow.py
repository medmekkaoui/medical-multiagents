import unittest

from fastapi.testclient import TestClient

from backend.app.api import app
from backend.app.tools.care_tools import recommend_interim_care


class MedicalWorkflowTest(unittest.TestCase):
    def test_mcp_interim_care_tool(self):
        recommendation = recommend_interim_care(["toux", "essoufflement"])
        self.assertIn("MCP", recommendation)
        self.assertIn("medecin", recommendation)

    def test_complete_api_workflow(self):
        client = TestClient(app)

        response = client.post(
            "/consultation/start",
            json={"patient_case": "Patient avec toux et fievre depuis trois jours."},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["type"], "patient_question")
        thread_id = payload["thread_id"]

        answers = [
            "Depuis 3 jours",
            "Oui, environ 38.5",
            "Toux et fatigue, pas d'essoufflement",
            "Aucun medicament",
            "Aucun antecedent important",
        ]

        for answer in answers:
            response = client.post(
                "/consultation/resume",
                json={"thread_id": thread_id, "answer": answer},
            )
            self.assertEqual(response.status_code, 200)

        payload = response.json()
        self.assertEqual(payload["type"], "physician_review")
        self.assertIn("diagnostic_summary", payload["physician_review"])

        response = client.post(
            "/consultation/resume",
            json={
                "thread_id": thread_id,
                "answer": "Surveillance, traitement symptomatique et consultation si aggravation.",
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "completed")
        self.assertIn("Ce systeme ne remplace pas une consultation medicale", payload["final_report"])

        report_response = client.get(f"/consultation/{thread_id}/report")
        self.assertEqual(report_response.status_code, 200)
        self.assertTrue(report_response.json()["final_report"])

    def test_invalid_patient_answer_repeats_same_question(self):
        client = TestClient(app)

        response = client.post(
            "/consultation/start",
            json={"patient_case": "Patient avec fatigue."},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        thread_id = payload["thread_id"]
        first_question = payload["question"]

        response = client.post(
            "/consultation/resume",
            json={"thread_id": thread_id, "answer": "azerty"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertEqual(payload["type"], "patient_question")
        self.assertEqual(payload["question_count"], 0)
        self.assertIn(first_question, payload["question"])
        self.assertIn("Reponse non exploitable", payload["question"])


if __name__ == "__main__":
    unittest.main()
