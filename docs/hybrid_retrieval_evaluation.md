# Hybrid Retrieval Evaluation

## 1. Experiment Overview

This experiment evaluates and compares three information retrieval approaches implemented in EduRAG-X:

1. Semantic Retrieval
2. BM25 Keyword Retrieval
3. Hybrid Retrieval using Reciprocal Rank Fusion (RRF)

The objective is to investigate how combining semantic and keyword-based retrieval affects retrieval effectiveness and execution time.

## 2. Experimental Setup

### Dataset

- Sample PDF documents: 2
- Total indexed chunks: 8
- Total test queries: 5
- Relevant queries: 4
- Unrelated queries: 1
- Retrieval cutoff: Top-K = 3
- RRF parameter: k = 60

### Documents

1. dbms_sample.pdf
2. dbms_transactions_sample.pdf

### Retrieval Methods

**Semantic Retrieval**

Uses Gemini embeddings and FAISS similarity search to retrieve semantically relevant document chunks.

**BM25 Keyword Retrieval**

Uses the BM25Okapi algorithm to rank document chunks based on keyword relevance.

**Hybrid Retrieval**

Combines semantic and keyword retrieval results using Reciprocal Rank Fusion.

## 3. Evaluation Metrics

The following metrics were used:

- Precision@3: Proportion of retrieved chunks that are relevant among the top three results.
- Recall@3: Proportion of all known relevant chunks retrieved among the top three results.
- Mean Reciprocal Rank (MRR): Average reciprocal rank of the first relevant result.
- Retrieval Time: Time taken by the retrieval method to return results.

Metrics were averaged across the four relevant queries. The unrelated query was analysed separately.

## 4. Experimental Results

| Metric | Semantic | BM25 | Hybrid |
|---|---:|---:|---:|
| Average Precision@3 | 0.4167 | 0.3333 | 0.4167 |
| Average Recall@3 | 1.0000 | 0.8750 | 1.0000 |
| Average MRR | 0.8750 | 0.8750 | 0.8750 |
| Average Retrieval Time (seconds) | 0.6506 | 0.0008 | 0.6335 |

## 5. Results Analysis

### 5.1 Semantic Retrieval

Semantic Retrieval achieved:

- Precision@3: 0.4167
- Recall@3: 1.0000
- MRR: 0.8750

It retrieved all known relevant chunks across the four relevant queries.

### 5.2 BM25 Retrieval

BM25 achieved:

- Precision@3: 0.3333
- Recall@3: 0.8750
- MRR: 0.8750

BM25 demonstrated very low retrieval time. However, it missed one relevant chunk in the duplicate-data query.

### 5.3 Hybrid Retrieval

Hybrid Retrieval achieved:

- Precision@3: 0.4167
- Recall@3: 1.0000
- MRR: 0.8750

Its overall retrieval metrics matched Semantic Retrieval in this preliminary experiment.

The results do not yet demonstrate a measurable improvement in retrieval effectiveness from combining the two methods.

## 6. Unrelated Query Analysis

The unrelated query was:

"Explain the process of photosynthesis."

Results:

| Method | Retrieved Chunks |
|---|---:|
| Semantic | 3 |
| BM25 | 3 |
| Hybrid | 3 |

All three methods returned three chunks despite the absence of relevant content in the indexed documents.

This indicates that retrieval ranking alone does not reliably reject unrelated queries.

Further investigation of relevance thresholds and evidence-based filtering is required.

## 7. Key Observations

1. Semantic Retrieval achieved complete recall on the current relevant-query dataset.
2. BM25 demonstrated substantially lower retrieval time.
3. Hybrid Retrieval matched Semantic Retrieval on the measured effectiveness metrics.
4. The hybrid approach did not demonstrate a measurable overall improvement in this experiment.
5. All three approaches returned results for the unrelated query.
6. Relevance filtering and abstention mechanisms require further evaluation.

## 8. Limitations

This experiment is preliminary and has the following limitations:

- Only two synthetic sample PDFs were used.
- The indexed collection contained eight chunks.
- Only four relevant queries were evaluated.
- Only one unrelated query was evaluated.
- Retrieval time was measured in a single run per query.
- Semantic and Hybrid retrieval include query embedding API latency, whereas BM25 operates locally.
- Retrieval latency measurements are therefore not a direct comparison of algorithmic computation alone.
- Results may vary across repeated API calls and execution environments.

## 9. Conclusion

The preliminary experiment shows that Semantic Retrieval and Hybrid Retrieval achieved identical Precision@3, Recall@3, and MRR on the current dataset.

BM25 demonstrated significantly lower retrieval time but slightly lower overall retrieval effectiveness.

The experiment does not establish that Hybrid Retrieval is universally superior. Larger datasets, more diverse queries, repeated measurements, and additional evaluation metrics are required to determine its effectiveness more reliably.

## 10. Output File

Detailed query-level results are available in:

`docs/hybrid_retrieval_evaluation_results.csv`

The experiment can be reproduced using:

`python -m scripts.evaluate_hybrid_retrieval`