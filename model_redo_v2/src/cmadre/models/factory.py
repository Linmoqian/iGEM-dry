"""Centralized model factory so experiments cannot silently change implementations."""

from __future__ import annotations

from .base import CensoredRegressor
from .hurdle import CatBoostHurdleRegressor
from .quantile_trees import CatBoostQuantileRegressor, LightGBMQuantileRegressor
from .tabicl_challenger import TabICLChallenger
from .tabm_censored import TabMCensoredRegressor
from .xgb_aft import XGBoostAFTRegressor
from .xgb_quantile import XGBoostQuantileRegressor

SUPPORTED_MODELS = {
    "xgb_aft",
    "xgb_quantile",
    "xgb_quantile_tail",
    "catboost_quantile",
    "lightgbm_quantile",
    "catboost_hurdle",
    "tabm_censored",
    "tabicl",
}


def create_model(name: str, config: dict, seed_offset: int = 0) -> CensoredRegressor:
    seed = int(config["seed"]) + int(seed_offset)
    if name == "xgb_aft":
        return XGBoostAFTRegressor(config["xgb_aft"], seed)
    if name == "xgb_quantile":
        return XGBoostQuantileRegressor(config["xgb_quantile"], seed, name=name)
    if name == "xgb_quantile_tail":
        return XGBoostQuantileRegressor(config["xgb_quantile_tail"], seed, name=name)
    if name == "catboost_quantile":
        return CatBoostQuantileRegressor(config["catboost_quantile"], seed)
    if name == "lightgbm_quantile":
        return LightGBMQuantileRegressor(config["lightgbm_quantile"], seed)
    if name == "catboost_hurdle":
        return CatBoostHurdleRegressor(config.get("catboost_hurdle", config["catboost_quantile"]), seed)
    if name == "tabm_censored":
        return TabMCensoredRegressor(config["tabm_censored"], seed)
    if name == "tabicl":
        return TabICLChallenger(config["tabicl"], seed)
    raise ValueError(f"unsupported model {name!r}; available: {sorted(SUPPORTED_MODELS)}")
