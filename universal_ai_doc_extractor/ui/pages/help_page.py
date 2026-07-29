"""Help page with user guide and documentation."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QTextBrowser, QTreeWidget, QTreeWidgetItem,
    QSplitter,
)


HELP_CONTENT = {
    "Getting Started": """
<h2>Getting Started</h2>
<h3>Welcome to Universal AI Document Extractor</h3>
<p>This application helps you extract data from documents (PDFs, images, invoices, receipts) using AI and OCR, then write the extracted data to Excel workbooks.</p>

<h3>Quick Start</h3>
<ol>
<li>Go to <b>Document Extractor</b> to upload files</li>
<li>Configure your <b>AI Provider</b> in Settings (API key required)</li>
<li>Click <b>Process All</b> to extract data</li>
<li>Review extractions in <b>Review Center</b></li>
<li>Data is automatically saved to your workbook</li>
</ol>
""",
    "Document Extraction": """
<h2>Document Extraction</h2>
<h3>Supported Formats</h3>
<ul>
<li>PDF (native and scanned)</li>
<li>PNG, JPG, JPEG, TIFF, BMP</li>
<li>DOCX, CSV, TXT</li>
<li>Excel (.xlsx, .xlsm)</li>
</ul>

<h3>Extraction Fields</h3>
<p>The AI extracts: Invoice Number, Vendor, Customer, Address, Phone, Email, Date, Due Date, Currency, Subtotal, Tax, Discount, Shipping, Grand Total, Payment Method, Reference Number, Purchase Order, and Line Items.</p>

<h3>OCR Engines</h3>
<p>Choose between Tesseract OCR, EasyOCR, or OCRmyPDF in Settings.</p>
""",
    "AI Assistant": """
<h2>AI Assistant</h2>
<p>The built-in AI assistant helps you with natural language queries.</p>

<h3>Examples</h3>
<ul>
<li>"I paid electricity today $230" - Creates a journal entry</li>
<li>"Create journal entry" - Generates accounting entries</li>
<li>"Find invoice INV-1023" - Searches for invoices</li>
<li>"Show unpaid invoices" - Lists unpaid invoices</li>
<li>"Summarize July expenses" - Provides expense summary</li>
</ul>
""",
    "Excel Integration": """
<h2>Excel Integration</h2>
<h3>Workbook Manager</h3>
<p>Create, open, duplicate, and manage Excel workbooks. All extractions are appended intelligently without overwriting existing data.</p>

<h3>Data Writing</h3>
<p>The application:</p>
<ul>
<li>Detects the correct sheet automatically</li>
<li>Finds the next available row</li>
<li>Preserves formatting, formulas, and merged cells</li>
<li>Never corrupts existing data</li>
<li>Creates automatic backups</li>
</ul>
""",
    "Review Center": """
<h2>Review Center</h2>
<p>Every extracted field is displayed for review. You can:</p>
<ul>
<li>View confidence scores for each field</li>
<li>Edit any extracted value</li>
<li>Approve all fields at once</li>
<li>Reject incorrect extractions</li>
<li>Save drafts for later review</li>
</ul>
<p>Fields with low confidence are highlighted for your attention.</p>
""",
    "Settings": """
<h2>Settings</h2>
<h3>AI Provider</h3>
<p>Supports OpenAI, Claude (Anthropic), Gemini (Google), OpenRouter, and local Ollama models. API keys are encrypted (AES-256) and stored locally.</p>

<h3>Themes</h3>
<p>Choose between Dark, Light, or System themes.</p>

<h3>Backup</h3>
<p>Configure automatic backup frequency and retention.</p>
""",
    "Keyboard Shortcuts": """
<h2>Keyboard Shortcuts</h2>
<table>
<tr><td><b>Ctrl+O</b></td><td>Open workbook</td></tr>
<tr><td><b>Ctrl+N</b></td><td>New workbook</td></tr>
<tr><td><b>Ctrl+Q</b></td><td>Exit application</td></tr>
<tr><td><b>F5</b></td><td>Refresh</td></tr>
</table>
""",
    "FAQ": """
<h2>Frequently Asked Questions</h2>

<h3>How do I get an API key?</h3>
<p>Visit the AI provider's website (OpenAI, Anthropic, Google) to generate an API key, then enter it in Settings.</p>

<h3>Are my documents uploaded anywhere?</h3>
<p>No. Text is sent to the AI provider for extraction, but files stay on your computer. API keys are encrypted locally.</p>

<h3>How accurate is the extraction?</h3>
<p>Accuracy depends on document quality. Clean digital PDFs achieve 95%+ accuracy. Scanned documents vary. Always review in Review Center.</p>

<h3>Can I use it offline?</h3>
<p>Local OCR (Tesseract/EasyOCR) works offline. AI extraction requires internet for cloud providers. Ollama works locally.</p>
""",
}


class HelpPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("Help")
        title.setObjectName("titleLabel")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        splitter = QSplitter(Qt.Horizontal)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Topics")
        self.tree.setMinimumWidth(200)
        for topic in HELP_CONTENT:
            item = QTreeWidgetItem([topic])
            self.tree.addTopLevelItem(item)
        self.tree.currentItemChanged.connect(self._show_topic)

        splitter.addWidget(self.tree)

        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        self.browser.setStyleSheet("background: #252640; border: none; padding: 16px; color: #e8e9f0; font-size: 14px;")
        splitter.addWidget(self.browser)
        splitter.setSizes([200, 600])

        layout.addWidget(splitter, 1)

        if self.tree.topLevelItemCount() > 0:
            self.tree.setCurrentItem(self.tree.topLevelItem(0))

    def _show_topic(self, current, previous):
        if current:
            topic = current.text(0)
            content = HELP_CONTENT.get(topic, "<p>Topic not found.</p>")
            self.browser.setHtml(content)
