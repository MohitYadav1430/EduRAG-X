# Document-Level and Chunk-Level Retrieval Evaluation Comparison

## 1. Introduction

EduRAG-X uses two complementary evaluation approaches to examine the performance of its retrieval system:

1. Document-Level Retrieval Evaluation
2. Chunk-Level Retrieval Evaluation

Document-level evaluation measures whether the correct source document is retrieved, whereas chunk-level evaluation measures whether the correct text segments are retrieved and ranked effectively.

Both evaluations use the same two sample DBMS PDF documents and four relevant queries.

## 2. Comparative Results

The following table presents the average metrics across the four relevant queries.

| Metric | Document-Level | Chunk-Level |
|---|---:|---:|
| Average Precision | 0.5000 | 0.4167 |
| Average Recall | 1.0000 | 1.0000 |
| Average MRR | 1.0000 | 0.8750 |

Note: Document-level evaluation uses Top-2 document retrieval, while chunk-level evaluation uses Top-3 chunk retrieval. Therefore, precision values are not directly equivalent.

## 3. Comparative Analysis

### 3.1 Precision

Document-level evaluation achieved an average Precision@2 of 0.50.

Chunk-level evaluation achieved an average Precision@3 of approximately 0.4167.

This indicates that the retrieved chunk lists contain some non-relevant chunks, even when the correct information is retrieved.

### 3.2 Recall

Both evaluation approaches achieved an average recall of 1.0 across the four relevant queries.

This indicates that all manually identified relevant documents and chunks were retrieved within their respective retrieval limits.

### 3.3 Mean Reciprocal Rank

Document-level evaluation achieved an average MRR of 1.0.

Chunk-level evaluation achieved an average MRR of 0.875.

The difference is primarily due to the database indexing query, where the expected relevant chunk appeared at rank 2 instead of rank 1.

## 4. Unrelated Query Analysis

The photosynthesis query was used to examine retrieval behavior for a topic unrelated to the indexed DBMS documents.

Document-level evaluation:

| Similarity Threshold | Retrieved Documents |
|---|---:|
| None | 2 |
| 0.50 | 2 |
| 0.60 | 0 |
| 0.70 | 0 |

Chunk-level evaluation without similarity filtering returned three DBMS chunks for the same unrelated query.

This demonstrates that retrieval without an appropriate relevance filter can return unrelated results.

The document-level experiment suggests that similarity thresholding may help reduce irrelevant retrieval results in this small dataset.

However, these findings require validation on a larger dataset.

## 5. Key Findings

1. Both retrieval approaches successfully retrieved all manually identified relevant items for the four relevant queries.
2. Document-level evaluation achieved higher average precision and MRR in this experiment.
3. Chunk-level evaluation exposed ranking differences that were not visible at the document level.
4. The unrelated query demonstrated the limitations of unfiltered Top-K retrieval.
5. Similarity thresholding reduced unrelated document retrieval in the document-level experiment.

## 6. Limitations

- Only two synthetic DBMS PDF documents were evaluated.
- The dataset contains eight chunks and five queries.
- Ground-truth labels were manually prepared.
- The evaluation results are preliminary.
- Different Top-K values were used in the two evaluation approaches.
- Similarity thresholds were evaluated at document level but not at chunk level.
- The results do not establish general retrieval performance across large or diverse datasets.

## 7. Conclusion

The comparative evaluation demonstrates the usefulness of combining document-level and chunk-level retrieval analysis in EduRAG-X.

Document-level evaluation provides information about source-document ranking, while chunk-level evaluation provides a more detailed view of evidence retrieval.

Both approaches achieved perfect recall on the four relevant test queries in this preliminary experiment.

Further work should investigate chunk-level similarity thresholding, improved relevance filtering, and evaluation on a larger and more diverse dataset.