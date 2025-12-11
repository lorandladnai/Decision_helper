#!/bin/bash
set -e

echo "=========================================="
echo "FULL PIPELINE: Ingest → Features → Models"
echo "=========================================="

echo ""
./scripts/run_all_ingest.sh

echo ""
./scripts/feature_build.sh

echo ""
./scripts/modeltrain.sh

echo ""
echo "=========================================="
echo "✓ PIPELINE COMPLETE!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. View outputs: ls -la data/processed/"
echo "  2. Run dashboard: streamlit run src/app/dashboard.py"
echo "  3. Run API: python -m src.api.main_api"
echo ""
