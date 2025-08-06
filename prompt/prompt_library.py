from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_template("""
    You are highly capable of assistant trained to analyze and summarize documents.
    Return only valid JSON matching the exact schema provided below.

    {format_instructions}

    Analyze this document:
    {document_text}
    """)