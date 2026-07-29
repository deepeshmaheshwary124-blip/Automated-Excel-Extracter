"""Pytest configuration and fixtures."""

import os
import sys
import tempfile
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment with temp directories and database."""
    from database.connection import DatabaseConnection
    from database.migrations import run_migrations
    from config.constants import ensure_dirs

    ensure_dirs()

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)

    db = DatabaseConnection()
    db.initialize(db_path)
    run_migrations()

    old_cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir)
        os.chdir(str(test_dir))
        yield

    os.chdir(old_cwd)
    db.close()
    db_path.unlink(missing_ok=True)


@pytest.fixture
def temp_db_path():
    """Create a temporary database path."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    yield db_path
    db_path.unlink(missing_ok=True)


@pytest.fixture
def sample_text():
    return """INVOICE
Invoice #: INV-2024-001
Date: 2024-01-15
Due Date: 2024-02-14

Vendor: Acme Corporation
Address: 123 Business Ave, Suite 100, New York, NY 10001
Phone: (212) 555-0198
Email: billing@acmecorp.com

Bill To:
Customer: TechStart Inc.
123 Innovation Drive
San Francisco, CA 94105

Items:
1. Web Development Services - 40 hours @ $150/hr = $6,000.00
2. Cloud Infrastructure - 1 month @ $500/mo = $500.00
3. SSL Certificate - 1 year @ $299/yr = $299.00

Subtotal: $6,799.00
Tax (8.875%): $603.41
Shipping: $50.00
Discount: -$100.00
Grand Total: $7,352.41

Payment Method: Wire Transfer
Reference: PO-2024-089
"""
