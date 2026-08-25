#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

export CUDA_VISIBLE_DEVICES=0
export CUBLAS_WORKSPACE_CONFIG="${CUBLAS_WORKSPACE_CONFIG:-:4096:8}"
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-16}"
export MKL_NUM_THREADS="${MKL_NUM_THREADS:-16}"

CONDA_BIN="${CONDA_BIN:-$HOME/anaconda3/bin/conda}"
if [[ ! -x "$CONDA_BIN" ]]; then
  echo "Conda executable not found at $CONDA_BIN" >&2
  exit 1
fi

"$CONDA_BIN" run --no-capture-output -n igem-cmadre python run_train.py \
  --config configs/server_gpu.json \
  --target total_microcystins \
  --panel core_field \
  --split-protocol source_ood \
  --models xgb_aft,catboost_quantile,tabm_censored \
  --run-name total_mc_source_ood
