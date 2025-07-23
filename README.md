Document Portal project is AI based LLM document analyzer which does the following:
1. Analyze the document
2. Compare the document with one another
3. Chat(Q&A) with the document
4. Chat(Q&A) with multiple documents

Requirements for the project:

1. LLM Model ## GROQ(free), OPENAI(paid), Gemini(15 days free access), Claude(paid), HuggingFace(free), Ollama (not recommended as it runs locally and requires better local infrastructure i.e., at least 16GB+ RAM)

2. Word Embedding Model ## OpenAI, hf, gemini

3. Vector Databases ## Inmemory  ##OnDisk ##CloudBased


Agenda:
1. Implementation of RAG and its key components
2. Configure logging, monitoring and exception handling
3. Cloud implementation and CI/CD pipeline

Four Services of the Document Portal application:
1. Document Analysis - Complete analysis of the PDF and extract the data. This data will be provided to LLM as context
2. Document Compare - Any two documents(be it PDF, Word, PPT, web content) will be compared. Ex. there is a document(Doc1) and some updates are made to the document and a new document(Doc2) is created. Compare Doc1 with Doc2.
3. Chat with Single Document - The document is analyzed and stored in a VDB. The queries are posted and retrieve information by combining the document (context) with LLM.
4. Chat with Multiple Document - Multiple documents are analyzed and stored in VDB. The queries are posted and retrieve information by combining the document (context) with LLM.

Business UseCase:
A Chip manufacturing company procures spare parts from 3rd party vendors. The chip company recieves invoices and reports in email. The company needs document portal for the following reasons:
1. Extract info from invoices and reports
2. Compare the invoices and reports
3. Q&A with reports
4. Analyze the reports and invoices
