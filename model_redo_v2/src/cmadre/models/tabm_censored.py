"""A TabM-inspired MiniEnsemble with an interval-censored Gaussian log-target loss.

This is an independent, compact implementation of the paper's parameter-efficient
MiniEnsemble idea: member-specific input adapters followed by shared MLP weights.
It is not a vendored copy of the official TabM repository.
"""

from __future__ import annotations

import copy
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import ndtri

from ..labels import LabelIntervals
from .base import CensoredRegressor, DistributionPrediction
from .preprocessing import RobustNumericPreprocessor

try:
    import torch
    from torch import nn
except ImportError:  # keep the rest of the package importable without the optional heavy dependency
    torch = None
    nn = None


if nn is not None:

    class _TabMMiniNet(nn.Module):
        def __init__(
            self,
            input_dim: int,
            hidden_dims: list[int],
            ensemble_size: int,
            dropout: float,
            min_scale: float = 1e-3,
            max_scale: float | None = None,
        ):
            super().__init__()
            if min_scale <= 0:
                raise ValueError("min_scale must be positive")
            if max_scale is not None and max_scale <= min_scale:
                raise ValueError("max_scale must be greater than min_scale")
            self.ensemble_size = ensemble_size
            self.min_scale = float(min_scale)
            self.max_scale = None if max_scale is None else float(max_scale)
            self.input_scale = nn.Parameter(torch.ones(ensemble_size, input_dim))
            self.input_bias = nn.Parameter(torch.zeros(ensemble_size, input_dim))
            layers: list[nn.Module] = []
            current = input_dim
            for hidden in hidden_dims:
                layers.extend([nn.Linear(current, hidden), nn.SiLU(), nn.Dropout(dropout)])
                current = hidden
            self.backbone = nn.Sequential(*layers)
            self.location_head = nn.Linear(current, 1)
            self.scale_head = nn.Linear(current, 1)
            self.member_location_bias = nn.Parameter(torch.zeros(ensemble_size))
            self.member_scale_bias = nn.Parameter(torch.zeros(ensemble_size))
            nn.init.normal_(self.input_scale, mean=1.0, std=0.01)

        def forward(self, x):
            # x: [batch, features] -> [batch, members, features]
            adapted = x[:, None, :] * self.input_scale[None, :, :] + self.input_bias[None, :, :]
            hidden = self.backbone(adapted)
            location = self.location_head(hidden).squeeze(-1) + self.member_location_bias[None, :]
            raw_scale = self.scale_head(hidden).squeeze(-1) + self.member_scale_bias[None, :]
            if self.max_scale is None:
                # Backward-compatible path for v2 artifacts whose configuration did
                # not contain max_scale. New v3 runs use a bounded latent scale.
                scale = torch.nn.functional.softplus(raw_scale) + self.min_scale
            else:
                scale = self.min_scale + (self.max_scale - self.min_scale) * torch.sigmoid(raw_scale)
            return location, scale


def _require_torch():
    if torch is None or nn is None:
        raise ImportError("torch is required for model 'tabm_censored'; install project dependencies")


def censored_gaussian_log_target_nll(location, scale, lower, upper, exact, sample_weight=None):
    """NLL on Z=log1p(Y); left-censored [0,U] contributes log Phi(z_U)."""
    _require_torch()
    lower = lower[:, None]
    upper = upper[:, None]
    exact = exact[:, None]
    z_exact = torch.log1p(torch.clamp(lower, min=0.0))
    standardized_exact = (z_exact - location) / scale
    exact_nll = 0.5 * standardized_exact.square() + torch.log(scale) + 0.5 * np.log(2.0 * np.pi)

    z_upper = torch.log1p(torch.clamp(upper, min=0.0))
    standardized_upper = (z_upper - location) / scale
    log_cdf_upper = torch.special.log_ndtr(standardized_upper)

    positive_lower = lower > 0
    z_lower = torch.log1p(torch.clamp(lower, min=0.0))
    standardized_lower = (z_lower - location) / scale
    log_cdf_lower = torch.special.log_ndtr(standardized_lower)
    ratio = torch.exp(torch.clamp(log_cdf_lower - log_cdf_upper, max=-1e-7))
    log_interval = log_cdf_upper + torch.log1p(-ratio)
    censored_nll = torch.where(positive_lower, -log_interval, -log_cdf_upper)

    per_member = torch.where(exact, exact_nll, censored_nll)
    per_sample = per_member.mean(dim=1)
    if sample_weight is not None:
        weights = sample_weight / torch.clamp(sample_weight.mean(), min=1e-8)
        per_sample = per_sample * weights
    return per_sample.mean()


class TabMCensoredRegressor(CensoredRegressor):
    name = "tabm_censored"

    def __init__(self, params: dict, seed: int = 42):
        self.params = dict(params)
        self.seed = int(seed)
        self.preprocessor = RobustNumericPreprocessor(add_missing_indicators=True)
        self.network = None
        self.feature_names: list[str] | None = None
        self.input_dim_: int | None = None
        self.best_epoch_: int | None = None
        self.device_: str | None = None
        self.amp_enabled_: bool = False

    def _device(self) -> str:
        requested = self.params.get("device", "auto")
        if requested == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        if str(requested).startswith("cuda") and not torch.cuda.is_available():
            raise RuntimeError("CUDA was requested but is unavailable")
        return str(requested)

    def _set_determinism(self) -> None:
        torch.manual_seed(self.seed)
        np.random.seed(self.seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(self.seed)
        torch.use_deterministic_algorithms(True, warn_only=True)
        if hasattr(torch.backends, "cudnn"):
            torch.backends.cudnn.benchmark = False
            torch.backends.cudnn.deterministic = True

    def _make_loader(self, features, labels: LabelIntervals, weights, shuffle: bool):
        tensor_dataset = torch.utils.data.TensorDataset(
            torch.as_tensor(features, dtype=torch.float32),
            torch.as_tensor(labels.lower, dtype=torch.float32),
            torch.as_tensor(labels.upper, dtype=torch.float32),
            torch.as_tensor(labels.exact, dtype=torch.bool),
            torch.as_tensor(weights, dtype=torch.float32),
        )
        generator = torch.Generator()
        generator.manual_seed(self.seed)
        return torch.utils.data.DataLoader(
            tensor_dataset,
            batch_size=int(self.params.get("batch_size", 512)),
            shuffle=shuffle,
            num_workers=0,
            generator=generator,
            pin_memory=self.device_ != "cpu",
        )

    def _evaluate_loader(self, loader) -> float:
        self.network.eval()
        losses = []
        with torch.no_grad():
            for features, lower, upper, exact, weights in loader:
                features = features.to(self.device_)
                lower = lower.to(self.device_)
                upper = upper.to(self.device_)
                exact = exact.to(self.device_)
                weights = weights.to(self.device_)
                with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=self.amp_enabled_):
                    location, scale = self.network(features)
                # CDF differences can underflow in FP16; preserve the statistical
                # loss in FP32 while still accelerating the network matmuls.
                location = location.float()
                scale = scale.float()
                loss = censored_gaussian_log_target_nll(location, scale, lower, upper, exact, weights)
                losses.append(float(loss.detach().cpu()))
        return float(np.mean(losses))

    def fit(
        self,
        X: pd.DataFrame,
        labels: LabelIntervals,
        X_validation: pd.DataFrame | None = None,
        validation_labels: LabelIntervals | None = None,
        sample_weight: np.ndarray | None = None,
    ) -> TabMCensoredRegressor:
        _require_torch()
        self._set_determinism()
        self.feature_names = list(X.columns)
        train_features = self.preprocessor.fit_transform(X)
        self.input_dim_ = int(train_features.shape[1])
        validation_features = None
        if X_validation is not None and validation_labels is not None and len(X_validation):
            validation_features = self.preprocessor.transform(X_validation)
        train_weights = (
            np.ones(len(X), dtype=np.float32)
            if sample_weight is None
            else np.asarray(sample_weight, dtype=np.float32)
        )
        validation_weights = (
            np.ones(len(X_validation), dtype=np.float32)
            if validation_features is not None
            else np.empty(0, dtype=np.float32)
        )

        self.device_ = self._device()
        self.amp_enabled_ = bool(self.params.get("amp", True)) and self.device_.startswith("cuda")
        self.network = _TabMMiniNet(
            input_dim=self.input_dim_,
            hidden_dims=[int(value) for value in self.params.get("hidden_dims", [256, 256, 128])],
            ensemble_size=int(self.params.get("ensemble_size", 16)),
            dropout=float(self.params.get("dropout", 0.15)),
            min_scale=float(self.params.get("min_scale", 1e-3)),
            max_scale=(
                None if self.params.get("max_scale") is None else float(self.params["max_scale"])
            ),
        ).to(self.device_)
        optimizer = torch.optim.AdamW(
            self.network.parameters(),
            lr=float(self.params.get("learning_rate", 1e-3)),
            weight_decay=float(self.params.get("weight_decay", 1e-4)),
        )
        scaler = torch.amp.GradScaler("cuda", enabled=self.amp_enabled_)
        train_loader = self._make_loader(train_features, labels, train_weights, shuffle=True)
        validation_loader = None
        if validation_features is not None:
            validation_loader = self._make_loader(
                validation_features, validation_labels, validation_weights, shuffle=False
            )

        best_loss = np.inf
        best_state = None
        patience = int(self.params.get("patience", 30))
        stale_epochs = 0
        max_epochs = int(self.params.get("max_epochs", 300))
        for epoch in range(max_epochs):
            self.network.train()
            for features, lower, upper, exact, weights in train_loader:
                features = features.to(self.device_)
                lower = lower.to(self.device_)
                upper = upper.to(self.device_)
                exact = exact.to(self.device_)
                weights = weights.to(self.device_)
                optimizer.zero_grad(set_to_none=True)
                with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=self.amp_enabled_):
                    location, scale = self.network(features)
                location = location.float()
                scale = scale.float()
                loss = censored_gaussian_log_target_nll(location, scale, lower, upper, exact, weights)
                if not torch.isfinite(loss):
                    raise FloatingPointError("non-finite TabM censored loss")
                scaler.scale(loss).backward()
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(
                    self.network.parameters(), float(self.params.get("gradient_clip", 1.0))
                )
                scaler.step(optimizer)
                scaler.update()
            monitored = self._evaluate_loader(validation_loader or train_loader)
            if monitored < best_loss - 1e-6:
                best_loss = monitored
                best_state = copy.deepcopy(
                    {key: value.detach().cpu() for key, value in self.network.state_dict().items()}
                )
                self.best_epoch_ = epoch + 1
                stale_epochs = 0
            else:
                stale_epochs += 1
                if validation_loader is not None and stale_epochs >= patience:
                    break
        if best_state is None:
            raise RuntimeError("TabM training did not produce a finite model")
        self.network.load_state_dict(best_state)
        self.network.to(self.device_)
        return self

    def _component_parameters(self, X: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
        if self.network is None or self.feature_names is None:
            raise RuntimeError("model is not fitted")
        if list(X.columns) != self.feature_names:
            raise ValueError("feature columns/order differ from fitted TabM model")
        features = self.preprocessor.transform(X)
        locations = []
        scales = []
        self.network.eval()
        batch_size = int(self.params.get("batch_size", 512))
        with torch.no_grad():
            for start in range(0, len(features), batch_size):
                batch = torch.as_tensor(
                    features[start : start + batch_size], dtype=torch.float32, device=self.device_
                )
                with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=self.amp_enabled_):
                    location, scale = self.network(batch)
                locations.append(location.cpu().numpy())
                scales.append(scale.cpu().numpy())
        return np.concatenate(locations), np.concatenate(scales)

    def predict_distribution(self, X: pd.DataFrame) -> DistributionPrediction:
        location, scale = self._component_parameters(X)
        quantile_predictions = []
        for probability in (0.1, 0.5, 0.9):
            component = np.maximum(np.expm1(location + scale * ndtri(probability)), 0)
            # Mean of component quantiles is a deterministic ensemble summary. The
            # full member parameters are retained in `extra` for mixture diagnostics.
            quantile_predictions.append(component.mean(axis=1))
        return DistributionPrediction(
            q10=quantile_predictions[0],
            q50=quantile_predictions[1],
            q90=quantile_predictions[2],
            extra={"best_epoch": self.best_epoch_, "ensemble_size": int(location.shape[1])},
        )

    def save(self, path: str | Path) -> None:
        _require_torch()
        if self.network is None:
            raise RuntimeError("model is not fitted")
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "params": self.params,
            "seed": self.seed,
            "feature_names": self.feature_names,
            "input_dim": self.input_dim_,
            "best_epoch": self.best_epoch_,
            "preprocessor": pickle.dumps(self.preprocessor, protocol=pickle.HIGHEST_PROTOCOL),
            "state_dict": {key: value.detach().cpu() for key, value in self.network.state_dict().items()},
        }
        torch.save(payload, path)

    @classmethod
    def load(cls, path: str | Path) -> TabMCensoredRegressor:
        _require_torch()
        payload = torch.load(Path(path), map_location="cpu", weights_only=False)
        result = cls(payload["params"], payload["seed"])
        result.feature_names = payload["feature_names"]
        result.input_dim_ = int(payload["input_dim"])
        result.best_epoch_ = payload["best_epoch"]
        result.preprocessor = pickle.loads(payload["preprocessor"])
        result.device_ = result._device()
        result.amp_enabled_ = bool(result.params.get("amp", True)) and result.device_.startswith("cuda")
        result.network = _TabMMiniNet(
            input_dim=result.input_dim_,
            hidden_dims=[int(value) for value in result.params.get("hidden_dims", [256, 256, 128])],
            ensemble_size=int(result.params.get("ensemble_size", 16)),
            dropout=float(result.params.get("dropout", 0.15)),
            min_scale=float(result.params.get("min_scale", 1e-3)),
            max_scale=(
                None
                if result.params.get("max_scale") is None
                else float(result.params["max_scale"])
            ),
        )
        result.network.load_state_dict(payload["state_dict"])
        result.network.to(result.device_)
        return result
