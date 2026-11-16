# Chunk-Level Similarity Threshold Evaluation

## 1. Introduction

This experiment evaluates the effect of similarity threshold filtering on chunk-level retrieval performance in EduRAG-X.

The objective is to investigate whether similarity-based filtering can reduce irrelevant chunk retrieval while preserving relevant chunks.

## 2. Experimental Setup

| Parameter | Value |
|---|---|
| Embedding Model | gemini-embedding-2 |
| Vector Store | FAISS |
| Similarity Method | Cosine Similarity |
| Total Indexed Chunks | 8 |
| Total Queries | 5 |
| Relevant Queries | 4 |
| Unrelated Queries | 1 |
| Top-K | 3 |
| Thresholds | None, 0.50, 0.60, 0.70 |

The experiment uses the same manually prepared ground-truth dataset as the previous chunk-level evaluation.

Each query embedding is generated once. Similarity threshold filtering is then applied locally to the retrieved results.

## 3. Evaluation Metrics

- Precision@3: Proportion of relevant chunks among the top three retrieved positions.
- Recall@3: Proportion of manually identified relevant chunks retrieved.
- Mean Reciprocal Rank (MRR): Average reciprocal rank of the first relevant chunk across relevant queries.

## 4. Experimental Results

| Threshold | Average Precision@3 | Average Recall@3 | MRR |
|---|---:|---:|---:|
| None | 0.4167 | 1.0000 | 0.8750 |
| 0.50 | 0.4167 | 1.0000 | 0.8750 |
| 0.60 | 0.4167 | 1.0000 | 0.8750 |
| 0.70 | 0.3333 | 0.8750 | 0.8750 |

## 5. Unrelated Query Analysis

The photosynthesis query was used to evaluate the system's behavior when the question was unrelated to the indexed DBMS documents.

| Threshold | Retrieved Chunks |
|---|---:|
| None | 3 |
| 0.50 | 3 |
| 0.60 | 0 |
| 0.70 | 0 |

Thresholds 0.60 and 0.70 filtered all retrieved chunks for the unrelated query.

## 6. Observations

1. Thresholds None, 0.50, and 0.60 produced identical aggregate metrics for relevant queries.
2. At threshold 0.60, all manually identified relevant chunks remained within the top three results.
3. Threshold 0.70 reduced average Precision@3 and Recall@3.
4. The duplicate data reduction query lost one expected relevant chunk at threshold 0.70.
5. The unrelated photosynthesis query returned no chunks at thresholds 0.60 and 0.70.
6. Increasing the similarity threshold can reduce irrelevant retrieval but may also remove relevant evidence.

## 7. Preliminary Findings

Threshold 0.60 appears promising for the evaluated dataset because it filtered the unrelated query while preserving all manually identified relevant chunks.

However, this finding is specific to the current experimental dataset and does not establish 0.60 as a universally optimal threshold.

## 8. Limitations

- The dataset contains only eight chunks.
- Only five queries were evaluated.
- Relevance labels were manually prepared.
- Only two synthetic DBMS PDF documents were used.
- The experiment does not establish performance on large-scale or diverse datasets.
- Threshold selection requires further validation on additional documents and queries.

## 9. Conclusion

The preliminary experiment demonstrates that similarity threshold filtering can influence chunk-level retrieval behavior.

A threshold of 0.60 successfully filtered the unrelated photosynthesis query while maintaining a Recall@3 of 1.0 across the four relevant queries.

Further experiments with larger datasets are necessary before selecting a general-purpose similarity threshold for EduRAG-X.