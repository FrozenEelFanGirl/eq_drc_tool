# TODO

Test suite coverage gaps vs. the test platform specification (`doc/test_platform.md`).

## Missing test files

- **`test_designer.py`** — Designer tests live in `test_quantizer.py` (`TestRbjAgainstGolden`).
  Only covers 42 entries (21 peak + 21 bypass). Missing: notch, lowshelf, highshelf golden
  validation. Needs known Q/gain_db parameters for the remaining filter types.
- **`test_script_composer.py`** — Composer logic only tested indirectly through integration
  tests. No dedicated validation of byte ordering, address sequence, or DRC-after-EQ ordering.
- **`test_bat_formatter.py`** — No byte-identical comparison against the golden `.bat` files
  in `doc/ref/example_bat/`. Integration tests only check structural properties (address
  presence, write count). Should match: `eq_48k_all_bypass.bat`, `drc_reference_config.bat`,
  `eq_enter_manual_mode0.bat`, `eq_read_example.bat`.

## Coverage gaps

| Layer | Gap |
|-------|-----|
| 1 — Designer | Add golden tests for notch (Q known: same list as peak), lowshelf, highshelf once Q/gain_db are confirmed. |
| 4 — Composer | Dedicated tests for init sequence, coefficient group ordering, byte splitting (REG10–REG13), DRC section placement. |
| 5 — Formatter | Byte-identical `.bat` output comparison against example files. |
| 7 — Integration | Mixed-config test (not all bypass), DRC reference golden comparison, per-band bypass verification. |

## Cleanup

- `test/golden/` — deleted; golden data is now inline in `test_quantizer.py`.
- `mock_sdw_tool.py` — exists but unused by any test. Wire into formatter or integration tests.
- `doc/test_platform.md` — stale references to `coe_array.txt` and `InterpolatingDesigner`;
  update once gaps are filled.
