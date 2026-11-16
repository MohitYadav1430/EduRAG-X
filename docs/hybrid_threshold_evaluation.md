# Hybrid Retrieval Threshold Evaluation

## 1. Experiment Overview

This experiment investigates the effect of semantic similarity thresholds on the performance of the Hybrid Retrieval system in EduRAG-X.

The objective is to determine whether semantic similarity filtering can improve retrieval relevance and help reject unrelated queries when combined with BM25 keyword retrieval.

## 2. Experimental Setup

- Sample PDF documents: 2
- Total indexed chunks: 8
- Test queries: 5
- Relevant queries: 4
- Unrelated queries: 1
- Retrieval cutoff: Top-K = 3
- RRF parameter: k = 60

### Thresholds

Four configurations were evaluated:

1. No threshold
2. 0.50
3. 0.60
4. 0.70

### Retrieval Architecture

Semantic Retrieval uses Gemini embeddings and FAISS similarity search.

BM25 Retrieval uses keyword-based ranking through BM25Okapi.

Hybrid Retrieval combines the filtered semantic results and BM25 results using Reciprocal Rank Fusion.

The semantic and keyword retrieval results are generated once per query and reused across threshold configurations.

## 3. Evaluation Metrics

The experiment uses:

- Precision@3
- Recall@3
- Mean Reciprocal Rank (MRR)
- Relevant Query Coverage
- Unrelated Query Abstention Rate

Relevant Query Coverage measures the proportion of relevant queries for which at least one known relevant chunk was retrieved.

Unrelated Query Abstention Rate measures the proportion of unrelated queries for which the system returned no chunks.

Metrics are calculated over four relevant queries. Unrelated query abstention is evaluated separately.

## 4. Experimental Results

| Metric | No Threshold | 0.50 | 0.60 | 0.70 |
|---|---:|---:|---:|---:|
| Mean Precision@3 | 0.4167 | 0.4167 | 0.4167 | 0.3333 |
| Mean Recall@3 | 1.0000 | 1.0000 | 1.0000 | 0.8750 |
| MRR | 0.8750 | 0.8750 | 0.8750 | 0.8750 |
| Relevant Query Coverage | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Unrelated Query Abstention Rate | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

## 5. Unrelated Query Analysis

The unrelated query was:

"Explain the process of photosynthesis."

The results were:

| Threshold | Semantic Results | BM25 Results | Hybrid Results |
|---|---:|---:|---:|
| None | 3 | 3 | 3 |
| 0.50 | 3 | 3 | 3 |
| 0.60 | 0 | 3 | 3 |
| 0.70 | 0 | 3 | 3 |

At thresholds 0.60 and 0.70, semantic retrieval returned no chunks for the unrelated query.

However, BM25 continued returning three chunks. These results were included in the final hybrid ranking through Reciprocal Rank Fusion.

Therefore, semantic similarity filtering alone did not achieve unrelated-query rejection in the current hybrid architecture.

## 6. Relevant Query Analysis

Thresholds None, 0.50 and 0.60 produced identical aggregate retrieval metrics.

At threshold 0.70, average Recall@3 decreased from 1.0000 to 0.8750.

The duplicate-data query experienced a reduction in recall from 1.0 to 0.5 because one of its two expected relevant chunks was no longer present in the final Top-3 results.

This indicates that more restrictive semantic filtering can reduce relevant information retrieval.

## 7. Key Findings

1. Thresholds 0.50 and 0.60 did not change the aggregate relevant-query metrics in this experiment.
2. Threshold 0.70 reduced average Recall@3.
3. Semantic filtering rejected the unrelated query at thresholds 0.60 and 0.70.
4. BM25 results continued entering the final hybrid ranking even when semantic retrieval returned zero chunks.
5. The current Hybrid Retrieval architecture requires an additional relevance-filtering mechanism to reject unrelated queries effectively.

## 8. Limitations

- The experiment used only two sample PDFs.
- Only eight chunks were indexed.
- Only four relevant queries and one unrelated query were evaluated.
- The threshold values were evaluated on a small synthetic dataset.
- Results cannot establish a universally optimal similarity threshold.
- BM25 results were not independently filtered by a relevance threshold.
- The experiment evaluates retrieval behaviour, not final answer correctness.

## 9. Conclusion

The preliminary experiment demonstrates that semantic similarity filtering alone is insufficient for unrelated-query rejection in the current Hybrid Retrieval architecture.

Although a threshold of 0.60 eliminated semantic results for the unrelated query, BM25 continued contributing keyword matches to the final hybrid ranking.

A separate relevance-filtering mechanism is therefore required to control the inclusion of weakly relevant keyword results.

The results also indicate that overly restrictive semantic thresholds may reduce relevant information retrieval.

Larger datasets and more diverse queries are required for reliable threshold selection.

## 10. Output File

Detailed query-level results:

`docs/hybrid_threshold_evaluation_results.csv`

Reproduction command:

`python -m scripts.evaluate_hybrid_threshold`