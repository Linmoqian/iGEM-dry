from __future__ import annotations

import numpy as np
import pytest

torch = pytest.importorskip("torch")

from cmadre.models.tabm_censored import censored_gaussian_log_target_nll


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
