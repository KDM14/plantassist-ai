#!/usr/bin/env python3
"""
PlantAssist AI - Document Ingestion CLI
Run this to index PDFs into ChromaDB before starting the server.

Usage:
    python ingest.py
    python ingest.py --force          # re-ingest all even if unchanged
    python ingest.py --docs-dir /path/to/pdfs
"""
import sys
import logging
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.database import init_db
from app.services.ingestion import ingest_documents

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="PlantAssist AI - Document Ingestion")
    parser.add_argument("--docs-dir", type=str, default=None,
                        help="Directory containing PDFs (default: data/docs/)")
    parser.add_argument("--force", action="store_true",
                        help="Force re-ingestion of all documents even if unchanged")
    args = parser.parse_args()

    logger.info("=" * 50)
    logger.info("PlantAssist AI - Document Ingestion")
    logger.info("=" * 50)

    init_db()

    stats = ingest_documents(docs_dir=args.docs_dir, force=args.force)

    if "error" in stats:
        logger.error(f"Ingestion error: {stats['error']}")
        sys.exit(1)

    logger.info("=" * 50)
    logger.info(f"Processed  : {stats['processed']}")
    logger.info(f"Skipped    : {stats['skipped']} (unchanged)")
    logger.info(f"Failed     : {stats['failed']}")
    logger.info(f"Chunks add : {stats['chunks_added']}")
    logger.info("=" * 50)

    for doc in stats.get("documents", []):
        if doc["status"] == "processed":
            logger.info(f"  ✓ {doc['filename']}: {doc['pages']} pages, {doc['chunks']} chunks")
        else:
            logger.error(f"  ✗ {doc['filename']}: {doc.get('error', 'unknown error')}")

    if stats["processed"] == 0 and stats["skipped"] == 0:
        logger.warning("No documents were processed. Check the docs directory.")
        sys.exit(1)

    logger.info("Ingestion complete.")


if __name__ == "__main__":
    main()
