class EvidenceReferenceValidator:

    def validate(self, claims, retrieved_chunks):

        if not isinstance(claims, list):
            raise ValueError("Claims must be a list.")

        available_pages = {}

        for chunk in retrieved_chunks:

            source = chunk["source"]
            page = chunk["page_number"]

            available_pages.setdefault(source, set()).add(page)

        results = []

        for claim in claims:

            evidence = claim.get("evidence", [])
            status = claim.get("status")

            invalid_references = []

            for reference in evidence:

                source = reference.get("source")
                page = reference.get("page")

                valid = (
                    isinstance(source, str)
                    and isinstance(page, int)
                    and not isinstance(page, bool)
                    and source in available_pages
                    and page in available_pages.get(source, set())
                )

                if not valid:
                    invalid_references.append(reference)

            evidence_valid = len(invalid_references) == 0

            if status == "SUPPORTED" and not evidence:
                evidence_valid = False

            final_status = status

            if status == "SUPPORTED" and not evidence_valid:
                final_status = "UNCERTAIN"

            results.append({
                "claim": claim.get("claim"),
                "original_status": status,
                "final_status": final_status,
                "evidence_references_valid": evidence_valid,
                "invalid_references": invalid_references
            })

        return {
            "total_claims": len(results),
            "valid_claims": sum(
                item["evidence_references_valid"]
                for item in results
            ),
            "invalid_claims": sum(
                not item["evidence_references_valid"]
                for item in results
            ),
            "downgraded_claims": sum(
                item["original_status"] == "SUPPORTED"
                and item["final_status"] == "UNCERTAIN"
                for item in results
            ),
            "results": results
        }
