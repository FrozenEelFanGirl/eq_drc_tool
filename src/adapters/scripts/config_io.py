import json
from pathlib import Path

from ...application.drc_session import DRCSession
from ...application.eq_session import EQSession
from ...domain.eq.params import FilterParams, FilterType


def export_config(path: str | Path, eq: EQSession, drc: DRCSession) -> None:
    """Save EQ+DRC configuration to JSON file."""
    data = {
        "version": 1,
        "sample_rate": eq.sample_rate,
        "bands": [],
        "drc": {
            "enabled": drc.enabled,
            "params": {
                "threshold_db": drc.params.threshold_db,
                "ratio_idx": drc.params.ratio_idx,
                "attack_val": drc.params.attack_val,
                "release_val": drc.params.release_val,
                "makeup_gain_db": drc.params.makeup_gain_db,
                "update_window": drc.params.update_window,
                "gain_compute": drc.params.gain_compute,
                "noise_gate_db": drc.params.noise_gate_db,
                "gain_balance": drc.params.gain_balance,
                "max_output_db": drc.params.max_output_db,
                "extended_window": drc.params.extended_window,
            },
        },
    }
    for i in range(7):
        if eq.bands[i] is not None:
            p = eq.bands[i]
            data["bands"].append({
                "freq": p.freq,
                "filter_type": p.filter_type.value,
                "gain_db": p.gain_db,
                "Q": p.Q,
                "bypass": eq.bypass_flags[i],
            })
        else:
            data["bands"].append({
                "bypass": True,
            })
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def import_config(path: str | Path, eq: EQSession, drc: DRCSession) -> None:
    """Load EQ+DRC configuration from JSON file."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))

    if "sample_rate" in data:
        eq.set_sample_rate(data["sample_rate"])

    if "bands" in data:
        for i, b in enumerate(data["bands"]):
            if i >= 7:
                break
            bypass = b.get("bypass", True)
            if not bypass and "filter_type" in b:
                eq.update_band(i, FilterParams(
                    freq=b["freq"],
                    filter_type=FilterType(b["filter_type"]),
                    gain_db=b.get("gain_db", 0),
                    Q=b.get("Q", 1.0),
                ))
            else:
                eq.bypass_flags[i] = True

    if "drc" in data:
        drc_data = data["drc"]
        if "params" in drc_data:
            from ...domain.drc.params import DRCParams
            p = drc_data["params"]
            drc.update(DRCParams(
                threshold_db=p.get("threshold_db", -10),
                ratio_idx=p.get("ratio_idx", 4),
                attack_val=p.get("attack_val", 0),
                release_val=p.get("release_val", 0),
                makeup_gain_db=p.get("makeup_gain_db", 0),
                update_window=p.get("update_window", 128),
                gain_compute=p.get("gain_compute", 0x42),
                noise_gate_db=p.get("noise_gate_db", -88.98),
                gain_balance=p.get("gain_balance", 0),
                max_output_db=p.get("max_output_db", 0),
                extended_window=p.get("extended_window", True),
            ))
        if drc_data.get("enabled", False) != drc.enabled:
            drc.toggle()
