extra_tests33='''


def test_schedule_switches_at_explicit_fold_boundaries_with_two_sided_turnover():
    axis = axis_of(3)
    series, _ = vectors.schedule_series(
        axis, {"A": [100]*3, "B": [100]*3}, ["A", "B"], evaluation=axis[1:],
        rebalance_days=7, decision_days=axis[1:], cost_rate=0.01,
        weights_for=lambda last: {"A" if last == 0 else "B": 1},
    )
    assert series == pytest.approx([1/1.01 - 1, -0.02/1.01])


def test_risk_static_control_uses_only_pre_evaluation_data_and_does_not_promote():
    axis = axis_of(100)
    closes = {"A": [100.0], "B": [100.0]}
    for i in range(1, 100):
        for symbol, scale in [("A", 0.01), ("B", 0.02)]:
            closes[symbol].append(closes[symbol][-1] * (1 + scale * (1 if i % 2 else -1)))
    assets = list(closes)
    panel = {"axis": axis, "closes": closes, "asset_returns": vectors.panel_returns(axis, closes, assets)}
    config = {
        "evaluation_days": axis[30:], "decision_indices": list(range(29, 99, 7)),
        "rebalance_days": 7, "cost_rate": 0.0025, "vol_lookback_days": 21, "vol_forward_days": 21,
        "static_control": {"id": "test", "lookback_days": 21, "minimum_volatility_reduction": 0.05,
                           "decision": "test control; never a candidate"},
    }
    basket, _ = vectors.scheduled(panel, assets, config, vectors.constant_weights({"A": 0.5, "B": 0.5}))
    result = vectors.risk_vector(panel, basket, assets=assets, config=config, deposit=100,
                                bootstrap={"block_mean_days": 5, "resamples": 100, "seed": 23},
                                power={"alpha": 0.05, "power": 0.8})
    control = result["static_control"]
    assert control["freeze_day"] == axis[29].isoformat()
    assert control["weights"] == pytest.approx({"A": 2/3, "B": 1/3})
    assert control["volatility_ratio"]["estimate"] == pytest.approx(1)
    assert control["decision"] == "NO_INCREMENTAL_EVIDENCE"
    # Future volatility changes cannot alter the weights frozen before evaluation.
    for i in range(30, 100):
        panel["asset_returns"]["A"][i] *= 10
    again = vectors.risk_vector(panel, basket, assets=assets, config=config, deposit=100,
                               bootstrap={"block_mean_days": 5, "resamples": 100, "seed": 23},
                               power={"alpha": 0.05, "power": 0.8})
    assert again["static_control"]["weights"] == control["weights"]


def test_alpha_bootstrap_reports_no_information_for_degenerate_regressions():
    assert vectors.bootstrap_alpha_p([0.01]*30, [0.0]*30, block_mean=5, resamples=100, seed=1) is None
'''
print(patch(project_root_path/'tests/test_vectors.py',[{'from':'302:dc5','replace':'    assert stationary_mean_p([1.0] * 30, block_mean=5, resamples=100, seed=23) == pytest.approx(2 / 101)'+extra_tests33}]))
print(patch(project_root_path/'src/cryptosyf/vectors.py',[{'from':'83:868','replace':'                           for symbol in sorted(set(target) | set(positions)))'}]))
print(patch(project_root_path/'src/cryptosyf/comparison.py',[
 {'from':'770:58b','replace':'    return {\n        "experiment": select.get("experiment"),'},
 {'from':'881:58b','replace':'    return {\n        "experiment": study.get("experiment"),\n        "static_control": risk.get("static_control") or {},'},
 {'from':'1255:562','replace':'        "## 9. Autoselekcja par — " + ((comparison.get("select") or {}).get("experiment") or REGISTERED_NOT_RUN),'},
 {'from':'1334:52b','replace':'        "## 10. Rozkład wektorowy — " + (vectors.get("experiment") or REGISTERED_NOT_RUN),'},
 {'from':'1346:69f','replace':'        "względem benchmarku (top-k minus koszyk, nie beta-neutralny) z IC rang, V3 ryzyko (trwałość zmienności,",