import json
from google import genai

from src.edurag_x.config.settings import GEMINI_API_KEY
from src.edurag_x.rag.evidence_reference_validator import EvidenceReferenceValidator


class EvidenceVerifier:

    def __init__(self):

        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model = "gemini-3.6-flash"

        self.reference_validator = EvidenceReferenceValidator()

    def verify(self, answer, retrieved_chunks):

        if not answer or not answer.strip():
            raise ValueError("Answer cannot be empty.")

        if not retrieved_chunks:
            return {
                "verification_status": "INSUFFICIENT_EVIDENCE",
                "claims": []
            }

        evidence_parts = []

        for chunk in retrieved_chunks:

            evidence_parts.append(
                f"""
SOURCE: {chunk['source']}
PAGE: {chunk['page_number']}

CONTENT:
{chunk['text']}
"""
            )

        evidence = "\n\n".join(evidence_parts)

        prompt = f"""
You are an independent evidence verification engine.

Verify every factual claim in the answer against
the supplied document evidence.

AI-GENERATED ANSWER:
{answer}

AVAILABLE DOCUMENT EVIDENCE:
{evidence}

RULES:

1. Break the answer into individual factual claims.
2. Evaluate each claim independently.
3. SUPPORTED means directly supported by evidence.
4. UNSUPPORTED means evidence does not support the claim.
5. UNCERTAIN means evidence is ambiguous or incomplete.
6. Do not use outside knowledge.
7. A citation does not automatically prove a claim.
8. Return only actual source filenames and page numbers
   appearing in the supplied evidence.
9. If no evidence supports a claim, return an empty array.
10. Explain your decision briefly.

Return ONLY valid JSON:

{{
    "verification_status": "COMPLETED",
    "claims": [
        {{
            "claim": "Factual statement",
            "status": "SUPPORTED",
            "evidence": [
                {{
                    "source": "filename.pdf",
                    "page": 1
                }}
            ],
            "reason": "Explanation"
        }}
    ]
}}

Allowed statuses:
SUPPORTED, UNSUPPORTED, UNCERTAIN
"""

        try:

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    "response_mime_type": "application/json"
                }
            )

            result = json.loads(response.text)

            if not isinstance(result, dict):
                raise ValueError("Invalid verification response.")

            if not isinstance(result.get("claims"), list):
                raise ValueError("Claims must be a list.")

            allowed_statuses = {
                "SUPPORTED",
                "UNSUPPORTED",
                "UNCERTAIN"
            }

            for claim in result["claims"]:

                if not isinstance(claim, dict):
                    raise ValueError("Invalid claim structure.")

                if claim.get("status") not in allowed_statuses:
                    raise ValueError("Invalid claim status.")

                if not isinstance(claim.get("evidence"), list):
                    raise ValueError("Evidence must be a list.")

            validation = self.reference_validator.validate(
                claims=result["claims"],
                retrieved_chunks=retrieved_chunks
            )

            for claim, validation_result in zip(
                result["claims"],
                validation["results"]
            ):

                claim["original_status"] = (
                    validation_result["original_status"]
                )

                claim["status"] = (
                    validation_result["final_status"]
                )

                claim["evidence_references_valid"] = (
                    validation_result["evidence_references_valid"]
                )

                claim["invalid_evidence_references"] = (
                    validation_result["invalid_references"]
                )

                if (
                    claim["original_status"] == "SUPPORTED"
                    and claim["status"] == "UNCERTAIN"
                ):

                    claim["reason"] += (
                        " The claim was downgraded because its "
                        "evidence references could not be validated."
                    )

            claims = result["claims"]

            result["total_claims"] = len(claims)

            result["supported_claims"] = sum(
                claim["status"] == "SUPPORTED"
                for claim in claims
            )

            result["unsupported_claims"] = sum(
                claim["status"] == "UNSUPPORTED"
                for claim in claims
            )

            result["uncertain_claims"] = sum(
                claim["status"] == "UNCERTAIN"
                for claim in claims
            )

            result["invalid_evidence_references"] = sum(
                len(claim["invalid_evidence_references"])
                for claim in claims
            )

            result["claims_with_invalid_evidence"] = sum(
                not claim["evidence_references_valid"]
                for claim in claims
            )

            return result

        except Exception as error:

            return {
                "verification_status": "VERIFICATION_FAILED",
                "claims": [],
                "error": str(error)
            }
