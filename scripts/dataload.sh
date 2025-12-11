#!/bin/bash
set -e

echo "=========================================="
echo "Running Data Ingestion Pipeline"
echo "=========================================="

echo "1. Loading MNB data..."
python -m src.data_load.dataload

echo ""
echo "2. Building features..."
python -m src.features.features

echo ""
echo "✓ Data ingestion complete!"
