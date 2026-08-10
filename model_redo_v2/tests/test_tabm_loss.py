from __future__ import annotations

import numpy as np
import pytest

torch = pytest.importorskip("torch")

from cmadre.models.tabm_censored import _TabMMiniNet, censored_gaussian_log_target_nll


def test_censored_tabm_loss_is_finite_and_differentiable() -> None:
    location = torch.tensor([[0.0, 0.1], [0.5, 0.6]], requires_grad=True)
    scale = torch.ones_like(location)
    lower = torch.tensor([1.0, 0.0])
    upper = torch.tensor([1.0, 0.5])
    exact = torch.tensor([True, False])
    loss = censored_gaussian_log_target_nll(location, scale, lower, upper, exact)
    assert torch.isfinite(loss)
    loss.backward()
    assert location.grad is not None
    assert np.isfinite(location.grad.detach().numpy()).all()


def test_tabm_bounded_scale_prevents_pathological_intervals() -> None:
    network = _TabMMiniNet(
        input_dim=3,
        hidden_dims=[8],
        ensemble_size=4,
        dropout=0.0,
        min_scale=0.03,
        max_scale=3.0,
    )
    with torch.no_grad():
        network.member_scale_bias.fill_(100.0)
        _, scale = network(torch.zeros((5, 3)))
    assert torch.isfinite(scale).all()
    assert float(scale.min()) >= 0.03
    assert float(scale.max()) <= 3.0
