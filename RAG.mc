Challenges in RAG Systems (Primarily Quality-Related) Building RAG systems presents multifaceted roadblocks, primarily around quality, cost, safety, and knowledge. Quality is reported as the biggest challenge by over 41% of professionals. Quality issues stem from multiple data-related challenges.
1. Data Curation
    ◦ Format Diversity: Source data exists in many different formats (PDFs, HTML, Word, spreadsheets, emails, internal tools), each with unique quirks, making it beyond trivial to extract clean and consistent data.
    ◦ Noise and Redundancy: Documents often contain headers, footers, disclaimers, and irrelevant sections. If not filtered out, these pollute vector indexes and lead to subpar results.
    ◦ Content Structuring: How data is chunked is crucial. Larger chunks can be semantically imprecise due to too much information, while smaller chunks can lose important context.
    ◦ Freshness and Updates: Data is never static (e.g., product documentation, privacy policies). Maintaining freshness in data indexes automatically is a complex problem vital for system quality.
    ◦ Solution: The speaker indicates that solutions for data curation were not discussed due to time constraints.
2. Precision vs. Recall
    ◦ Concept: This is a common issue where optimizing one comes at the cost of the other.
        ▪ Precision: Fetching the most relevant documents. While good for getting the right context, overdoing precision can lead to missing peripheral parts of the answer.
        ▪ Recall: Extracting loosely related or peripheral information. This aids in completeness, but overdoing it can supply too much irrelevant context to LLMs.
    ◦ Solution: The speaker indicates that solutions for precision vs. recall were not discussed due to time constraints.
3. Semantic Gap
    ◦ Concept: Users often phrase queries vaguely, which differs significantly from how information is stored in knowledge bases. This makes it tricky for systems to pull out accurate answers. For example, a query like "why are certain deals missing in the pipeline" might semantically match keywords but miss the actual reasons like archived pipelines, missing fields, or user permissions.
    ◦ Solutions:
        ▪ Query Transformation:
            • How it works: An LLM rephrases the user's query into semantically richer and more aligned variants, understanding the context (e.g., a CRM system). It generates multiple relevant query variants (e.g., including "archived," "closed," "permissions") that are then used together to find the right answers.
            • Impact: Microsoft benchmarked this technique with search reranking, finding a 26% uptick on the NDCG scale (a measure of correctness).
        ▪ HyDE (Hypothetical Document Embeddings):
            • How it works: Instead of directly embedding the user's vague query, the LLM is asked to generate a hypothetical answer to that query. This hypothetical answer, which implicitly understands the context and contains domain-relevant concepts, is then embedded and used to search for relevant documents.
            • Impact: This approach increases the probability of finding relevant documents multifold. A study in June 2024 found an average 10% uptick in precision in systems using HyDE compared to naive RAG.
4. Irrelevant Retrievals
    ◦ Concept: Retrieving documents that are not relevant to the user's actual question. This can happen because documents are noisy, the knowledge base's sheer size dilutes quality, or individual chunks lack sufficient context. An example given is searching for "how to file a provisional patent" and getting results like "top 10 lawyers near you" or "why startups fail" because "provisional patent" might appear with higher frequency in irrelevant documents. Another example shows a relevant chunk discussing "climate change impact" failing to be retrieved for a "Nike climate change report" query because "Nike" wasn't in the chunk text.
    ◦ Solutions:
        ▪ Metadata Filtering:
            • How it works: When documents are embedded into a data store like OpenSearch, relevant metadata (e.g., fiscal year, department) is added alongside the content. When a query is fired, the system first filters the documents from the entire knowledge base based on this metadata, then runs an embedding-based retrieval only on the narrowed set of filtered documents.
            • Impact: This method yields significantly better results than blindly searching the entire database.
        ▪ CCH (Contextual Chunk Headers):
            • How it works: To provide more context to individual chunks, the chunk text is combined with a "chunk header" (e.g., the title of the document from which the chunk originated) before embedding them together.
            • Impact: This drastically improves similarity scores. In an example, adding a chunk header boosted a similarity score from 0.1 to 0.9. Benchmarking across various datasets (AI papers, financial data, company policies, US Supreme Court opinions) showed that CCH alone improved precision by 26%.
Further Advanced Techniques
• Other Sophisticated Approaches: The presentation also mentions rank rag, raptor, and graph rag as sophisticated approaches for building RAG systems.
• Caution: These techniques have received mixed feedback from users, with success varying. Significant experimentation and tuning are required to get them right for specific use cases.
Building RAG systems can be complex due to noisy data, unpredictable LLMs, and painful integrations, but getting them right leads to intelligent systems grounded in reality and provides a competitive edge.