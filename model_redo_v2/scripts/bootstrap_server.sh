#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

if command -v conda >/dev/null 2>&1; then
  CONDA_BIN="$(command -v conda)"
elif [[ -x "$HOME/anaconda3/bin/conda" ]]; then
  CONDA_BIN="$HOME/anaconda3/bin/conda"
elif [[ -x "$HOME/miniconda3/bin/conda" ]]; then
  CONDA_BIN="$HOME/miniconda3/bin/conda"
else
  echo "Conda executable not found." >&2
  exit 1
fi

if "$CONDA_BIN" env list | awk '{print $1}' | grep -qx 'igem-cmadre'; then
  "$CONDA_BIN" env update -n igem-cmadre -f environment.yml --prune
else
  "$CONDA_BIN" env create -f environment.yml
fi

"$CONDA_BIN" run --no-capture-output -n igem-cmadre python -m pip install -e .
"$CONDA_BIN" run --no-capture-output -n igem-cmadre python run_validate.py
"$CONDA_BIN" run --no-capture-output -n igem-cmadre pytest -q

echo "Environment and data contract are ready."
