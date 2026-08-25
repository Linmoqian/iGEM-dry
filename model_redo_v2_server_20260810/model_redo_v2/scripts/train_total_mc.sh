#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

export CUDA_VISIBLE_DEVICES=0
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-16}"
export MKL_NUM_THREADS="${MKL_NUM_THREADS:-16}"

conda run -n igem-cmadre python run_train.py \
  --config configs/server_gpu.json \
  --target total_microcystins \
  --panel core_field \
  --split-protocol source_ood \
  --models xgb_aft,catboost_quantile,tabm_censored \
  --run-name total_mc_source_ood
