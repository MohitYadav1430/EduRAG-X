import re


class CitationValidator:

    BRACKET_PATTERN = re.compile(r"\[([^\]]*)\]")

    SOURCE_PATTERN = re.compile(
        r"^\s*Source:\s*(.+?),\s*Pages?:\s*(.+?)\s*$",
        re.IGNORECASE
    )

    PAGE_NUMBER_PATTERN = re.compile(
        r"\d+\s*-\s*\d+|\d+"
    )

    def validate(self, answer, retrieved_chunks):

        available_pages = {}

        for chunk in retrieved_chunks:
            source = chunk["source"]
            page = chunk["page_number"]
            available_pages.setdefault(source, set()).add(page)

        results = []

        for bracket_content in self.BRACKET_PATTERN.findall(answer):

            citation_parts = re.split(
                r";\s*(?=Source\s*:)",
                bracket_content,
                flags=re.IGNORECASE
            )

            for citation_part in citation_parts:

                match = self.SOURCE_PATTERN.match(citation_part)

                if not match:
                    continue

                source = match.group(1).strip()
                page_text = match.group(2).strip()

                cited_pages = set()

                for token in self.PAGE_NUMBER_PATTERN.findall(page_text):

                    if "-" in token:
                        start, end = map(int, token.split("-"))

                        if end >= start:
                            cited_pages.update(range(start, end + 1))
                    else:
                        cited_pages.add(int(token))

                valid_source = source in available_pages

                valid_pages = (
                    valid_source
                    and bool(cited_pages)
                    and cited_pages.issubset(available_pages[source])
                )

                results.append({
                    "source": source,
                    "pages": sorted(cited_pages),
                    "valid": valid_source and valid_pages
                })

        return {
            "total_citations": len(results),
            "valid_citations": sum(
                1 for item in results if item["valid"]
            ),
            "invalid_citations": sum(
                1 for item in results if not item["valid"]
            ),
            "missing_citations": len(results) == 0,
            "citations": results,
            "all_valid": (
                len(results) > 0
                and all(item["valid"] for item in results)
            )
        }
