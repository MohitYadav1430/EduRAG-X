# EduRAG-X: Retrieval Quality Evaluation

## 1. Objective

The objective of this evaluation is to assess the document retrieval quality of the EduRAG-X RAG system.

The evaluation focuses on:
- Retrieval of relevant documents.
- Retrieval across multiple PDF documents.
- Handling of unrelated queries.
- Effect of minimum similarity thresholds.
- Ranking of relevant documents.

## 2. Evaluation Dataset

The evaluation uses two controlled sample PDF documents:

1. dbms_sample.pdf
2. dbms_transactions_sample.pdf

Both documents contain DBMS concepts, normalization, database transactions, ACID properties, SQL commands, and database indexing.

Dataset statistics:
- Total PDF documents: 2
- Total extracted chunks: 8
- Total indexed vectors: 8

## 3. Evaluation Test Cases

| Test ID | Query | Expected Relevant Document |
|---|---|---|
| RQ-01 | How can duplicate data in a database be reduced? | dbms_sample.pdf |
| RQ-02 | Explain ACID properties in DBMS. | dbms_transactions_sample.pdf |
| RQ-03 | What are the different SQL commands? | dbms_transactions_sample.pdf |
| RQ-04 | What is database indexing? | dbms_transactions_sample.pdf |
| RQ-05 | Explain the process of photosynthesis. | No relevant document |

Four queries are relevant to the indexed documents. One query is unrelated to the available dataset.

## 4. Evaluation Metrics

The following metrics are used:

- Precision@2: Proportion of relevant documents among the top two document positions.
- Recall: Proportion of expected relevant documents successfully retrieved.
- Mean Reciprocal Rank (MRR): Average reciprocal rank of the first relevant document.
- Unrelated Query Handling: Whether the system retrieves documents for a query with no expected relevant document.

This experiment performs document-level evaluation by retaining the highest-ranked chunk for each source document.

## 5. Experimental Configuration

The evaluation uses the following minimum similarity threshold settings:

- No threshold (baseline)
- 0.50
- 0.60
- 0.70

The retriever initially ranks all indexed chunks. Duplicate results from the same PDF are then removed, retaining the highest-ranked chunk for each source document.

The evaluation uses a document-level cutoff of K = 2.

## 6. Experimental Results

### 6.1 Relevant Query Results

Four relevant queries were evaluated.

| Threshold | Mean Precision@2 | Mean Recall | MRR |
|---|---:|---:|---:|
| None | 0.50 | 1.00 | 1.00 |
| 0.50 | 0.50 | 1.00 | 1.00 |
| 0.60 | 0.50 | 1.00 | 1.00 |
| 0.70 | 0.50 | 1.00 | 1.00 |

### 6.2 Document Ranking Observations

The expected relevant document appeared at rank 1 for all four relevant queries.

| Query | First Retrieved Document | Expected Document | Result |
|---|---|---|---|
| Duplicate data reduction | dbms_sample.pdf | dbms_sample.pdf | Correct |
| ACID properties | dbms_transactions_sample.pdf | dbms_transactions_sample.pdf | Correct |
| SQL commands | dbms_transactions_sample.pdf | dbms_transactions_sample.pdf | Correct |
| Database indexing | dbms_transactions_sample.pdf | dbms_transactions_sample.pdf | Correct |

### 6.3 Similarity Threshold and Unrelated Query

The photosynthesis query was used to evaluate retrieval behavior when no relevant document was available.

| Threshold | Retrieved Documents | Unrelated Query Handling |
|---|---:|---|
| None | 2 | Irrelevant documents retrieved |
| 0.50 | 2 | Irrelevant documents retrieved |
| 0.60 | 0 | No documents retrieved |
| 0.70 | 0 | No documents retrieved |

The results indicate that the similarity threshold affects the retrieval of unrelated documents.

At thresholds of 0.60 and 0.70, no documents were retrieved for the photosynthesis query.

However, this observation is based on only one unrelated query and does not establish general rejection reliability.

## 7. Discussion

The experiment produced the following observations:

1. The expected relevant document was ranked first for all four relevant queries.
2. Mean Recall was 1.00 across all tested threshold settings.
3. MRR was 1.00, indicating that the first relevant document appeared at rank 1 for every relevant query.
4. Precision@2 was 0.50 because only one of the two indexed documents was expected to be relevant for each relevant query.
5. The 0.60 and 0.70 thresholds prevented document retrieval for the tested unrelated query.
6. A threshold of 0.70 reduced the number of retrieved documents for relevant queries from two to one without removing the expected relevant document.

These findings are preliminary and apply only to the current controlled dataset.

## 8. Limitations

- The evaluation dataset contains only two controlled sample PDFs.
- Only five queries were evaluated.
- Only one unrelated query was included.
- Relevance judgments were manually defined.
- This is a document-level evaluation, not a comprehensive chunk-level benchmark.
- Similarity scores are not calibrated confidence scores.
- The experiment does not establish general retrieval accuracy or performance on large-scale datasets.
- Additional documents, queries, and independent relevance judgments are required for stronger conclusions.

## 9. Conclusion

The preliminary evaluation shows that EduRAG-X retrieved the expected relevant document at rank 1 for all four relevant test queries.

The experiment also indicates that minimum similarity thresholds influence the retrieval of unrelated documents.

These results provide an initial assessment of the retrieval component. Further evaluation on a larger and more diverse dataset is necessary before making broader performance claims.


