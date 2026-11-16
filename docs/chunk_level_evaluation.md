# Chunk-Level Retrieval Evaluation

## 1. Overview

Chunk-Level Retrieval Evaluation is performed to measure how effectively the EduRAG-X retrieval system identifies relevant document chunks for a given query.

Unlike document-level evaluation, which checks whether the correct document is retrieved, chunk-level evaluation examines whether the correct text segments are retrieved and ranked near the top.

The evaluation uses manually prepared ground-truth labels and Gemini-generated embeddings.

## 2. Dataset

The evaluation uses two sample PDF documents:

| Document | Number of Chunks |
|---|---:|
| dbms_sample.pdf | 4 |
| dbms_transactions_sample.pdf | 4 |
| **Total** | **8** |

Five test queries were prepared:

- Four relevant queries related to the indexed DBMS documents.
- One unrelated query about photosynthesis.

Expected relevant chunks were manually identified and stored in:

`docs/chunk_level_ground_truth.csv`

Each chunk is identified using the format:

`source:chunk_id`

## 3. Evaluation Configuration

| Parameter | Value |
|---|---|
| Embedding Model | gemini-embedding-2 |
| Vector Store | FAISS |
| Similarity Method | Cosine Similarity |
| Top-K | 3 |
| Indexed Chunks | 8 |
| Total Queries | 5 |
| Relevant Queries | 4 |
| Unrelated Queries | 1 |

## 4. Evaluation Metrics

### 4.1 Precision@3

Measures the proportion of the top three retrieved chunks that are relevant.

Precision@3 = Relevant Retrieved Chunks / 3

### 4.2 Recall@3

Measures how many of the manually identified relevant chunks were retrieved within the top three results.

Recall@3 = Relevant Retrieved Chunks / Total Expected Relevant Chunks

### 4.3 Mean Reciprocal Rank (MRR)

Measures the ranking position of the first relevant chunk.

Reciprocal Rank = 1 / Rank of First Relevant Chunk

MRR is calculated as the average reciprocal rank across relevant queries.

## 5. Experimental Results

The actual evaluation produced the following results:

| Query | Precision@3 | Recall@3 | Reciprocal Rank |
|---|---:|---:|---:|
| Duplicate data reduction | 0.6667 | 1.0000 | 1.0000 |
| ACID properties | 0.3333 | 1.0000 | 1.0000 |
| SQL commands | 0.3333 | 1.0000 | 1.0000 |
| Database indexing | 0.3333 | 1.0000 | 0.5000 |
| Photosynthesis | N/A | N/A | N/A |

### 5.1 Average Metrics for Relevant Queries

The macro averages across the four relevant queries are:

| Metric | Average |
|---|---:|
| Precision@3 | 0.4167 |
| Recall@3 | 1.0000 |
| MRR | 0.8750 |

The unrelated photosynthesis query is excluded from these averages.

## 6. Observations

1. The duplicate data reduction query retrieved both expected relevant chunks within the top three results.

2. The ACID properties query retrieved its expected relevant chunk at rank 1.

3. The SQL commands query also retrieved its expected relevant chunk at rank 1.

4. The database indexing query retrieved its expected relevant chunk at rank 2, resulting in a reciprocal rank of 0.5.

5. All four relevant queries achieved Recall@3 of 1.0, meaning all manually identified relevant chunks were retrieved within the top three results.

6. The unrelated photosynthesis query also returned three DBMS chunks. This indicates that the current retriever does not independently abstain from returning results for unrelated queries.

## 7. Limitations

- The evaluation dataset contains only eight chunks and five queries.
- Ground-truth relevance labels were manually prepared.
- Only two synthetic sample PDF documents were used.
- The evaluation does not establish performance on large or diverse real-world datasets.
- Precision and recall depend on the manually defined relevant chunks.
- The unrelated query demonstrates that returning the top-k results does not guarantee their relevance.
- Similarity scores are not calibrated confidence scores.

## 8. Conclusion

The preliminary chunk-level evaluation shows that the EduRAG-X retrieval system successfully retrieves the manually identified relevant chunks for all four relevant test queries within the top three results.

The average Recall@3 is 1.0, while the average Precision@3 is approximately 0.4167 and MRR is 0.8750.

However, the unrelated photosynthesis query also retrieves DBMS chunks. This highlights the need for further investigation into retrieval filtering and relevance-based abstention.

These findings are preliminary and should not be generalized beyond the small experimental dataset.