#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

if conda env list | awk '{print $1}' | grep -qx 'igem-cmadre'; then
  conda env update -n igem-cmadre -f environment.yml --prune
else
  conda env create -f environment.yml
fi

conda run -n igem-cmadre python -m pip install -e .
conda run -n igem-cmadre python run_validate.py
conda run -n igem-cmadre pytest -q

echo "Environment and data contract are ready."

