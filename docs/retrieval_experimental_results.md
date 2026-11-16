# EduRAG-X: Consolidated Retrieval Experimental Results

## 1. Introduction

This document consolidates the preliminary retrieval evaluation experiments conducted for EduRAG-X.

Three experiments were performed to investigate retrieval performance:

1. Document-Level Retrieval Evaluation
2. Chunk-Level Retrieval Evaluation
3. Chunk-Level Similarity Threshold Evaluation

The experiments use two synthetic DBMS PDF documents containing eight indexed chunks and five manually prepared test queries.

## 2. Experimental Dataset

| Document | Number of Chunks |
|---|---:|
| dbms_sample.pdf | 4 |
| dbms_transactions_sample.pdf | 4 |
| **Total** | **8** |

Query distribution:

| Query Category | Number of Queries |
|---|---:|
| Relevant | 4 |
| Unrelated | 1 |
| **Total** | **5** |

The unrelated query concerns photosynthesis, which is outside the subject matter of the indexed DBMS documents.

## 3. Experiment 1: Document-Level Retrieval Evaluation

### Objective

To evaluate whether the retrieval system identifies the correct source documents for a given query.

### Configuration

- Vector database: FAISS
- Similarity method: Cosine Similarity
- Top-K documents: 2
- Similarity thresholds: None, 0.50, 0.60, 0.70

### Results

Across the four relevant queries:

| Metric | Result |
|---|---:|
| Average Precision@2 | 0.5000 |
| Average Recall | 1.0000 |
| Average MRR | 1.0000 |

### Unrelated Query Results

| Threshold | Retrieved Documents |
|---|---:|
| None | 2 |
| 0.50 | 2 |
| 0.60 | 0 |
| 0.70 | 0 |

### Observation

All four relevant queries retrieved the expected document at rank 1.

The unrelated photosynthesis query returned two documents without filtering. At thresholds 0.60 and 0.70, no documents remained.

## 4. Experiment 2: Chunk-Level Retrieval Evaluation

### Objective

To examine whether the system retrieves the correct text segments from indexed documents.

### Configuration

- Total indexed chunks: 8
- Top-K chunks: 3
- Relevant queries: 4
- Unrelated queries: 1
- Ground truth: Manually prepared chunk identifiers

### Results

| Query | Precision@3 | Recall@3 | Reciprocal Rank |
|---|---:|---:|---:|
| Duplicate data reduction | 0.6667 | 1.0000 | 1.0000 |
| ACID properties | 0.3333 | 1.0000 | 1.0000 |
| SQL commands | 0.3333 | 1.0000 | 1.0000 |
| Database indexing | 0.3333 | 1.0000 | 0.5000 |

### Aggregate Results

| Metric | Average |
|---|---:|
| Precision@3 | 0.4167 |
| Recall@3 | 1.0000 |
| MRR | 0.8750 |

### Observation

All manually identified relevant chunks were retrieved within the top three results for the four relevant queries.

However, the unrelated photosynthesis query also returned three DBMS chunks.

This indicates that ordinary Top-K retrieval does not independently determine whether a query is related to the indexed documents.

## 5. Experiment 3: Chunk-Level Similarity Threshold Evaluation

### Objective

To investigate whether similarity threshold filtering can reduce irrelevant chunk retrieval while preserving relevant evidence.

### Configuration

- Top-K: 3
- Thresholds: None, 0.50, 0.60, 0.70
- Query embeddings: Generated once per query
- Filtering: Applied locally to retrieved results

### Aggregate Results

| Threshold | Average Precision@3 | Average Recall@3 | MRR |
|---|---:|---:|---:|
| None | 0.4167 | 1.0000 | 0.8750 |
| 0.50 | 0.4167 | 1.0000 | 0.8750 |
| 0.60 | 0.4167 | 1.0000 | 0.8750 |
| 0.70 | 0.3333 | 0.8750 | 0.8750 |

### Unrelated Query Results

| Threshold | Retrieved Chunks |
|---|---:|
| None | 3 |
| 0.50 | 3 |
| 0.60 | 0 |
| 0.70 | 0 |

### Observation

Thresholds 0.50 and 0.60 produced identical aggregate metrics for relevant queries.

At threshold 0.60, the unrelated query returned no chunks while all manually identified relevant chunks remained within the top three results.

At threshold 0.70, one expected relevant chunk was filtered out, reducing average Recall@3 to 0.8750.

## 6. Comparative Analysis

The following table compares the unfiltered document-level and chunk-level experiments.

| Metric | Document-Level | Chunk-Level |
|---|---:|---:|
| Precision | 0.5000 | 0.4167 |
| Recall | 1.0000 | 1.0000 |
| MRR | 1.0000 | 0.8750 |
| Retrieval Limit | Top 2 | Top 3 |

Note: Precision values are not directly equivalent because the two experiments use different Top-K values and different retrieval units.

### Key Differences

**Document-Level Evaluation**

- Measures source-document retrieval.
- All four relevant queries retrieved the expected document at rank 1.
- Similarity threshold filtering removed unrelated documents at 0.60 and 0.70.

**Chunk-Level Evaluation**

- Measures retrieval of individual text segments.
- Provides more detailed evidence-ranking information.
- Revealed that some retrieved chunks were not manually labelled as relevant.

**Chunk-Level Threshold Evaluation**

- Examines the effect of filtering individual chunks.
- Threshold 0.60 preserved the observed relevant retrieval results.
- The unrelated query returned no chunks at threshold 0.60.

## 7. Key Experimental Findings

1. Document-level and chunk-level evaluation provide complementary information about retrieval quality.

2. All four relevant queries achieved a recall of 1.0 in the unfiltered document-level and chunk-level experiments.

3. Document-level evaluation achieved an average MRR of 1.0.

4. Chunk-level evaluation achieved an average MRR of 0.8750, indicating a ranking difference for the database indexing query.

5. Similarity threshold filtering influenced both relevant and unrelated retrieval behavior.

6. A threshold of 0.60 appeared promising on the current experimental dataset because it filtered the unrelated query without reducing the observed relevant-query recall.

7. A threshold of 0.70 reduced relevant chunk recall, demonstrating the potential trade-off between filtering and evidence retention.

## 8. Research Limitations

The current experiments have several limitations:

- Only two synthetic DBMS PDF documents were used.
- The indexed dataset contains eight chunks.
- Only five queries were evaluated.
- Relevance labels were manually prepared.
- The dataset does not represent a large-scale academic knowledge base.
- The experiments do not establish general retrieval performance across different subjects.
- Similarity thresholds have not been calibrated using a larger validation dataset.
- The observed results should not be interpreted as statistically generalizable performance.

## 9. Future Improvements

The following improvements are proposed:

1. Evaluate retrieval using a larger and more diverse document collection.
2. Prepare a larger query and ground-truth dataset.
3. Investigate sentence-aware and semantic chunking strategies.
4. Evaluate additional similarity thresholds.
5. Investigate adaptive threshold selection.
6. Improve handling of unrelated queries.
7. Evaluate retrieval performance across multiple academic subjects.
8. Investigate whether improved chunk ranking can increase precision without sacrificing recall.

## 10. Overall Conclusion

The three preliminary experiments demonstrate the usefulness of evaluating retrieval at both document and chunk levels.

Document-level evaluation provides information about source-document ranking, while chunk-level evaluation provides a more detailed assessment of evidence retrieval.

Similarity threshold filtering also showed promising behavior in the current experimental dataset.

In particular, threshold 0.60 filtered the unrelated photosynthesis query while maintaining the observed relevant-query recall.

These findings provide an initial experimental foundation for further development and evaluation of the EduRAG-X retrieval system.

However, larger datasets and more extensive experiments are required before making broader performance claims.