import streamlit as st
from pathlib import Path

from src.edurag_x.ingestion.document_pipeline import (
    DocumentIngestionPipeline
)

from src.edurag_x.rag.retriever import Retriever
from src.edurag_x.rag.keyword_retriever import KeywordRetriever
from src.edurag_x.rag.hybrid_retriever import HybridRetriever
from src.edurag_x.rag.evidence_relevance_filter import EvidenceRelevanceFilter

from src.edurag_x.rag.rag_pipeline import RAGPipeline
from src.edurag_x.ingestion.processing_history import ProcessingHistory


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="EduRAG-X | AI Teaching Assistant",
    page_icon="",
    layout="wide"
)


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>
.main-title {
    font-size: 38px;
    font-weight: 700;
    color: #2563EB;
}

.subtitle {
    font-size: 17px;
    color: #64748B;
}

.section-title {
    font-size: 22px;
    font-weight: 600;
}

.answer-box {
    padding: 18px;
    border-radius: 10px;
    background-color: #F0F7FF;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# SESSION STATE INITIALIZATION
# --------------------------------------------------

if "ingestion_pipeline" not in st.session_state:
    st.session_state.ingestion_pipeline = None

if "rag_pipeline" not in st.session_state:
    st.session_state.rag_pipeline = None

if "processed_documents" not in st.session_state:
    st.session_state.processed_documents = set()

if "answer_result" not in st.session_state:
    st.session_state.answer_result = None


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(
    '<div class="main-title"> EduRAG-X</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'An Intelligent, Evidence-Aware Hybrid RAG System '
    'for Adaptive Teaching and Research Assistance'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.header(" System Information")

    st.success("Application Interface Active")

    st.info("AI Engine: Gemini")

    st.info("Vector Database: FAISS")

    st.info("Retrieval: Hybrid RAG Architecture")

    st.divider()

    st.markdown("### About EduRAG-X")

    st.write(
        "EduRAG-X is an AI-powered teaching assistant "
        "that provides evidence-aware answers using "
        "uploaded educational documents."
    )


# --------------------------------------------------
# INITIALIZE BACKEND
# --------------------------------------------------

try:

    if st.session_state.ingestion_pipeline is None:

        st.session_state.ingestion_pipeline = (
            DocumentIngestionPipeline()
        )

    ingestion_pipeline = (
        st.session_state.ingestion_pipeline
    )

    if "processing_history" not in st.session_state:
        st.session_state.processing_history = ProcessingHistory()

    processing_history = st.session_state.processing_history

except Exception as error:

    st.error(f"Backend initialization failed: {error}")

    st.stop()


# --------------------------------------------------
# MAIN LAYOUT
# --------------------------------------------------

left_column, right_column = st.columns([1, 1])


# --------------------------------------------------
# PDF UPLOAD SECTION
# --------------------------------------------------

with left_column:

    st.markdown(
        '<div class="section-title"> Upload Documents</div>',
        unsafe_allow_html=True
    )
    uploaded_files = st.file_uploader(
        "Upload your PDF documents",
        type=["pdf"],
        accept_multiple_files=True,
        max_upload_size=20
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:

            if uploaded_file.size == 0:
                st.error(
                    f"{uploaded_file.name} is empty."
                )

            elif uploaded_file.size > 20 * 1024 * 1024:
                st.error(
                    f"{uploaded_file.name} exceeds the 20 MB limit."
                )

    if uploaded_files:

        st.write("### Selected Documents")

        for file in uploaded_files:

            st.write(f" {file.name}")

        process_button = st.button(
            " Process Documents",
            use_container_width=True
        )

       
        if process_button:

            upload_directory = Path("data/uploads")
            upload_directory.mkdir(parents=True, exist_ok=True)

            successful_documents = []
            failed_documents = []
            skipped_documents = []

            progress_bar = st.progress(0)
            status_text = st.empty()

            total_files = len(uploaded_files)

            for index, uploaded_file in enumerate(uploaded_files):

                original_name = Path(uploaded_file.name).name

                if uploaded_file.size == 0:
                    error_message = "PDF file is empty."
                    failed_documents.append((original_name, error_message))
                    processing_history.add_record(
                        filename=original_name, status="FAILED", error=error_message
                    )
                    continue

                if uploaded_file.size > 20 * 1024 * 1024:
                    error_message = "PDF exceeds the 20 MB limit."
                    failed_documents.append((original_name, error_message))
                    processing_history.add_record(
                        filename=original_name, status="FAILED", error=error_message
                    )
                    continue

                file_header = uploaded_file.getvalue()[:5]

                if file_header != b"%PDF-":
                    error_message = "Invalid PDF file format."
                    failed_documents.append((original_name, error_message))
                    processing_history.add_record(
                        filename=original_name, status="FAILED", error=error_message
                    )
                    continue

                status_text.info(
                    f"Processing {index + 1}/{total_files}: {original_name}"
                )

                try:

                    if original_name in st.session_state.processed_documents:
                        skipped_documents.append(original_name)
                        processing_history.add_record(
                            filename=original_name,
                            status="SKIPPED",
                            error="Document already processed in this session."
                        )
                        continue

                    existing_sources = {
                        document["source"]
                        for document in ingestion_pipeline.vector_store.documents
                    }

                    if original_name in existing_sources:
                        skipped_documents.append(original_name)
                        st.session_state.processed_documents.add(original_name)
                        processing_history.add_record(
                            filename=original_name,
                            status="SKIPPED",
                            error="Document is already present in the knowledge base."
                        )
                        continue

                    pdf_path = upload_directory / original_name

                    with open(pdf_path, "wb") as file:
                        file.write(uploaded_file.getvalue())

                    result = ingestion_pipeline.ingest_pdf(pdf_path)

                    if result["chunks"] == 0:
                        error_message = "No extractable text found."
                        failed_documents.append((original_name, error_message))
                        processing_history.add_record(
                            filename=original_name,
                            status="FAILED",
                            pages=result.get("pages", 0),
                            error=error_message
                        )
                        continue

                    successful_documents.append({
                        "name": original_name,
                        "pages": result["pages"],
                        "chunks": result["chunks"],
                        "vectors": result["vectors_stored"]
                    })

                    processing_history.add_record(
                        filename=original_name,
                        status="SUCCESS",
                        pages=result["pages"],
                        chunks=result["chunks"],
                        vectors=result["vectors_stored"]
                    )

                    st.session_state.processed_documents.add(original_name)

                except Exception as error:

                    error_message = str(error)
                    failed_documents.append((original_name, error_message))
                    processing_history.add_record(
                        filename=original_name,
                        status="FAILED",
                        error=error_message
                    )

                finally:

                    progress_bar.progress(
                        (index + 1) / total_files
                    )

            status_text.empty()

            if successful_documents:
                st.session_state.rag_pipeline = None
                st.session_state.answer_result = None

            st.divider()
            st.subheader(" Processing Summary")

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Successful",
                len(successful_documents)
            )

            col2.metric(
                "Failed",
                len(failed_documents)
            )

            col3.metric(
                "Skipped",
                len(skipped_documents)
            )

            for document in successful_documents:

                st.success(
                    f"{document['name']} | "
                    f"Pages: {document['pages']} | "
                    f"Chunks: {document['chunks']} | "
                    f"Vectors: {document['vectors']}"
                )

            for name, error in failed_documents:

                st.error(f"{name}: {error}")

            for name in skipped_documents:

                st.warning(f"{name}: Already indexed or processed.")

            progress_bar.empty()


    # --------------------------------------------------
    # VECTOR DATABASE INFORMATION
    # --------------------------------------------------

       # --------------------------------------------------
    # KNOWLEDGE BASE MANAGEMENT
    # --------------------------------------------------

    st.divider()

    st.markdown("###  Knowledge Base Management")

    documents = ingestion_pipeline.vector_store.documents

    total_vectors = len(documents)

    unique_sources = sorted({
        document["source"]
        for document in documents
    })

    total_documents = len(unique_sources)

    col1, col2 = st.columns(2)

    col1.metric(
        "Indexed Documents",
        total_documents
    )

    col2.metric(
        "Total Stored Chunks",
        total_vectors
    )

    if documents:

        st.markdown("####  Indexed Document Details")

        for source in unique_sources:

            source_chunks = [
                document
                for document in documents
                if document["source"] == source
            ]

            unique_pages = {
                document["page_number"]
                for document in source_chunks
            }

            with st.expander(f" {source}"):

                detail_col1, detail_col2 = st.columns(2)

                detail_col1.metric(
                    "Pages Indexed",
                    len(unique_pages)
                )

                detail_col2.metric(
                    "Chunks Stored",
                    len(source_chunks)
                )

                st.write("**Indexed Pages:**")

                st.write(
                    ", ".join(
                        str(page)
                        for page in sorted(unique_pages)
                    )
                )

    else:

        st.info("No documents indexed yet.")

# --------------------------------------------------
# QUESTION ANSWERING SECTION
# --------------------------------------------------

with right_column:

    st.markdown(
        '<div class="section-title"> Ask a Question</div>',
        unsafe_allow_html=True
    )

    question = st.text_area(
        "Enter your question",
        placeholder="Example: Explain ACID properties in DBMS...",
        height=150
    )

    use_similarity_threshold = st.checkbox(
        "Enable similarity threshold"
    )

    min_similarity = None

    if use_similarity_threshold:
        min_similarity = st.slider(
            "Minimum similarity score",
            min_value=0.0,
            max_value=1.0,
            value=0.60,
            step=0.05,
            help="Only retrieve chunks meeting this similarity score."
        )

    ask_button = st.button(
        " Generate Answer",
        use_container_width=True
    )

    if ask_button:

        if not question.strip():

            st.warning("Please enter a question.")

        elif ingestion_pipeline.vector_store.total_vectors() == 0:

            st.warning(
                "Please upload and process PDF documents first."
            )

        else:

            try:

                if st.session_state.rag_pipeline is None:

                    vector_store = ingestion_pipeline.vector_store

                    semantic_retriever = Retriever(
                        vector_store=vector_store
                    )

                    keyword_retriever = KeywordRetriever(
                        vector_store=vector_store
                    )

                    hybrid_retriever = HybridRetriever(
                        semantic_retriever=semantic_retriever,
                        keyword_retriever=keyword_retriever,
                        rrf_k=60
                    )

                    evidence_relevance_filter = EvidenceRelevanceFilter(
                        vector_store=vector_store,
                        min_relevance=0.60
                    )

                    st.session_state.rag_pipeline = RAGPipeline(
                        retriever=hybrid_retriever,
                        evidence_relevance_filter=evidence_relevance_filter
                    )

                with st.spinner(
                    "Searching documents and generating answer..."
                ):

                    result = (
                        st.session_state.rag_pipeline.answer_question(
                            question,
                            top_k=5,
                            min_similarity=min_similarity
                        )
                    )

                st.session_state.answer_result = result

            except Exception as error:

                st.error(
                    f"Unable to generate answer: {error}"
                )


# --------------------------------------------------
# DOCUMENT PROCESSING HISTORY (FULL WIDTH)
# --------------------------------------------------

st.divider()
st.markdown("###  Document Processing History")

history_records = processing_history.get_history()

if history_records:
    import pandas as pd

    history_df = pd.DataFrame(history_records[::-1])

    # Keep a predictable column order and show all available fields.
    display_columns = [
        "filename", "status", "pages", "chunks",
        "vectors", "error", "timestamp"
    ]
    history_df = history_df.reindex(columns=display_columns)

    st.caption(f"Total history records: {len(history_records)}")

    def style_history_status(value):
        status_styles = {
            "SUCCESS": "background-color: #DCFCE7; color: #166534; font-weight: 700;",
            "FAILED": "background-color: #FEE2E2; color: #991B1B; font-weight: 700;",
            "SKIPPED": "background-color: #FEF3C7; color: #92400E; font-weight: 700;",
        }
        return status_styles.get(value, "")

    styled_history = history_df.style.map(
        style_history_status,
        subset=["status"]
    )

    st.dataframe(
        styled_history,
        width="stretch",
        hide_index=True,
        height=min(500, 38 * (len(history_df) + 1) + 10),
        column_config={
            "filename": st.column_config.TextColumn(
                "Filename", width="medium"
            ),
            "status": st.column_config.TextColumn(
                "Status", width="small"
            ),
            "pages": st.column_config.NumberColumn(
                "Pages", width="small"
            ),
            "chunks": st.column_config.NumberColumn(
                "Chunks", width="small"
            ),
            "vectors": st.column_config.NumberColumn(
                "Vectors", width="small"
            ),
            "error": st.column_config.TextColumn(
                "Error details", width="large"
            ),
            "timestamp": st.column_config.TextColumn(
                "Timestamp (UTC)", width="large"
            ),
        }
    )
else:
    st.info("No document processing history available yet.")


# --------------------------------------------------
# DISPLAY ANSWER
# --------------------------------------------------

result = st.session_state.answer_result

if result:

    st.divider()

    st.header(" Generated Answer")

    if result["status"] == "COMPLETED":

        st.markdown(
            '<div class="answer-box">',
            unsafe_allow_html=True
        )

        st.markdown(result["answer"])

        st.markdown("</div>", unsafe_allow_html=True)

        # ------------------------------------------
        # CITATION VALIDATION
        # ------------------------------------------

        st.subheader(" Citation Validation")

        citation_result = result["citation_validation"]

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total Citations",
            citation_result["total_citations"]
        )

        col2.metric(
            "Valid Citations",
            citation_result["valid_citations"]
        )

        col3.metric(
            "Invalid Citations",
            citation_result["invalid_citations"]
        )

        if citation_result["all_valid"]:

            st.success("All detected citations are valid.")

        elif citation_result["missing_citations"]:

            st.warning("No citations were detected.")

        else:

            st.warning(
                "Some citations are invalid. "
                "Please review the source references."
            )

        # ------------------------------------------
        # EVIDENCE VERIFICATION
        # ------------------------------------------

        st.subheader("Evidence Verification")

        verification = result["evidence_verification"]

        verification_status = verification["verification_status"]

        if verification_status == "COMPLETED":

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Supported Claims",
                verification.get("supported_claims", 0)
            )

            col2.metric(
                "Unsupported Claims",
                verification.get("unsupported_claims", 0)
            )

            col3.metric(
                "Uncertain Claims",
                verification.get("uncertain_claims", 0)
            )

            for index, claim in enumerate(
                verification["claims"],
                start=1
            ):

                with st.expander(
                    f"Claim {index}: {claim['status']}"
                ):

                    st.write(claim["claim"])

                    st.write(
                        "**Reason:**",
                        claim.get("reason", "Not provided.")
                    )

                    st.write(
                        "**Evidence:**",
                        claim.get("evidence", [])
                    )

                    st.write(
                        "**Evidence References Valid:**",
                        claim.get("evidence_references_valid", False)
                    )

        elif verification_status == "INSUFFICIENT_EVIDENCE":

            st.info(
                "Evidence verification was not required "
                "because no relevant document chunks were retrieved."
            )

        else:

            st.warning(
                "Evidence verification could not be completed."
            )

            st.write(
                verification.get("error", "Unknown error.")
            )

        # ------------------------------------------
        # HYBRID RETRIEVAL ANALYSIS
        # ------------------------------------------

        st.subheader("Hybrid Retrieval Analysis")

        retrieved_chunks = result.get("retrieved_chunks", [])

        if retrieved_chunks:
            hybrid_analysis_rows = []

            for rank, chunk in enumerate(retrieved_chunks, start=1):
                retrieval_sources = chunk.get("retrieval_sources") or []
                if isinstance(retrieval_sources, str):
                    retrieval_sources_display = retrieval_sources
                elif retrieval_sources:
                    retrieval_sources_display = ", ".join(
                        str(source).title() for source in retrieval_sources
                    )
                else:
                    retrieval_sources_display = "Not available"

                similarity_score = chunk.get("similarity_score")
                keyword_score = chunk.get("keyword_score")
                rrf_score = chunk.get("rrf_score")

                hybrid_analysis_rows.append({
                    "Final Rank": rank,
                    "Source": chunk.get("source", "Unknown"),
                    "Page": chunk.get("page_number", "N/A"),
                    "Semantic Rank": chunk.get("semantic_rank") if chunk.get("semantic_rank") is not None else "N/A",
                    "Keyword Rank": chunk.get("keyword_rank") if chunk.get("keyword_rank") is not None else "N/A",
                    "Similarity Score": round(similarity_score, 4) if isinstance(similarity_score, (int, float)) else "N/A",
                    "Keyword Score": round(keyword_score, 4) if isinstance(keyword_score, (int, float)) else "N/A",
                    "RRF Score": round(rrf_score, 6) if isinstance(rrf_score, (int, float)) else "N/A",
                    "Retrieval Source": retrieval_sources_display,
                })

            st.caption(
                "The table shows the ranking metadata returned by the HybridRetriever. "
                "Semantic and keyword scores are different measures and should not be "
                "compared directly. RRF Score is used to combine the two ranked lists."
            )

            st.dataframe(
                hybrid_analysis_rows,
                width="stretch",
                hide_index=True
            )
        else:
            st.info("No retrieved chunks are available for hybrid retrieval analysis.")

        # ------------------------------------------
        # RETRIEVED SOURCES
        # ------------------------------------------

        st.subheader(" Retrieved Sources")

        for index, chunk in enumerate(
            result["retrieved_chunks"],
            start=1
        ):

            with st.expander(
                f"Source {index}: {chunk['source']} "
                f"| Page {chunk['page_number']}"
            ):

                st.write(chunk["text"])

                similarity_score = chunk.get("similarity_score")
                keyword_score = chunk.get("keyword_score")
                rrf_score = chunk.get("rrf_score")

                st.write(
                    "Similarity Score:",
                    round(similarity_score, 4)
                    if isinstance(similarity_score, (int, float))
                    else "N/A"
                )
                st.write(
                    "Keyword Score:",
                    round(keyword_score, 4)
                    if isinstance(keyword_score, (int, float))
                    else "N/A"
                )
                st.write(
                    "RRF Score:",
                    round(rrf_score, 6)
                    if isinstance(rrf_score, (int, float))
                    else "N/A"
                )
                st.write(
                    "Semantic Rank:",
                    chunk.get("semantic_rank")
                    if chunk.get("semantic_rank") is not None
                    else "N/A"
                )
                st.write(
                    "Keyword Rank:",
                    chunk.get("keyword_rank")
                    if chunk.get("keyword_rank") is not None
                    else "N/A"
                )
                st.write(
                    "Retrieval Sources:",
                    ", ".join(chunk.get("retrieval_sources") or [])
                    or "Not available"
                )

    elif result["status"] == "INSUFFICIENT_EVIDENCE":

        st.warning("Insufficient Evidence")

        st.info(result["answer"])

        retrieved_count = len(
            result.get("retrieved_chunks", [])
        )

        filtered_count = len(
            result.get("filtered_chunks", [])
        )

        col1, col2 = st.columns(2)

        col1.metric(
            "Retrieved Chunks",
            retrieved_count
        )

        col2.metric(
            "Relevant Chunks After Filtering",
            filtered_count
        )

        st.success(
            "The system abstained because no sufficiently "
                "relevant evidence was found."
            )

    elif result["status"] == "ANSWER_GENERATION_FAILED":

        st.error("Answer generation failed.")

        st.write(
            result.get("error", "Unknown error.")
        )

    else:

        st.error(
            f"Unexpected result status: {result['status']}"
        )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "EduRAG-X | Final Year Project | "
    "Evidence-Aware AI Teaching Assistant"
)
