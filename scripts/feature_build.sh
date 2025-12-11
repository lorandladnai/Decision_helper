#!/bin/bash
set -e

echo "=========================================="
echo "Building Features"
echo "=========================================="

python -m src.features.features

echo "✓ Features built!"
