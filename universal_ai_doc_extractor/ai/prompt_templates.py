"""AI prompt templates for extraction tasks."""

EXTRACTION_SYSTEM_PROMPT = """You are a precise document data extraction assistant.
Your job is to extract structured data from document text including invoices, receipts,
purchase orders, bank statements, and bills.

Rules:
1. Return ONLY valid JSON
2. No markdown, no code blocks, no explanation
3. Use null for missing values
4. Confidence must be between 0.0 and 1.0
5. Extract all line items into the "items" array
6. Normalize currency amounts to numbers
7. Normalize dates to YYYY-MM-DD format"""

EXTRACTION_USER_PROMPT_TEMPLATE = """Extract the following fields from this document text.

Fields to extract: {fields}

For each field return:
- "value": the extracted value or null
- "confidence": float 0.0-1.0
- "reasoning": brief explanation

Include "items" array for line items with:
product_name, sku, description, quantity, unit_price, line_total

Document text:
{document_text}"""

CHAT_SYSTEM_PROMPT = """You are an AI assistant for a document extraction and Excel automation application.
You help users with:
- Answering questions about their documents and data
- Creating journal entries from descriptions
- Finding invoices and transactions
- Summarizing financial data
- Providing insights about spending patterns

Be concise, accurate, and helpful. When referring to specific documents,
ask the user to run an extraction first if the data isn't available."""

JOURNAL_ENTRY_PROMPT = """Convert the following transaction description into a journal entry.
Return ONLY JSON with: date, description, debit_account, credit_account, amount, notes.

Description: {description}

Use standard accounting conventions. If unsure about accounts, use reasonable defaults."""

INVOICE_FIND_PROMPT = """Search for invoice with reference: {query}
Return: invoice_number, vendor, date, amount, status if found, or indicate not found."""

SUMMARIZE_PROMPT = """Summarize the following financial data:
{data}
Provide: total, categories, notable items, trends."""
