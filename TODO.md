# TODO

## Architecture: `Localizable` protocol

Every text-bearing UI component must implement a `Localizable` protocol
so `MainWindow._switch_lang()` can call `refresh_language(lang)` uniformly
without knowing widget internals.

**Current anti-patterns to fix:**

1. Module-level hardcoded strings (`RATIO_LABELS`, `BALANCE_MODES` in `drc_panel.py`)
2. Strings built at init time with no re-localize path (DRC `_add_row` labels,
   `_update_times` prefixes like `att@`/`rel@`/`ms`)
3. Missing i18n keys for new DRC params (update_window, gain_compute, noise_gate,
   gain_balance, max_output, window_extend) — partially fixed, need `Localizable`
   to prevent recurrence

## DRC panel: combo box + time label i18n

- `RATIO_LABELS` and `BALANCE_MODES` are module-level English lists — never
  re-localized in `refresh_language`. Move to a method that rebuilds with `tr()`.
- `_update_times()` hardcodes `att@`, `rel@`, `ms` — use `tr()` keys.

## Config import: panel state sync

- `_sync_ui_from_session()` only syncs EQ strips and DRC `_enable_cb`.
  DRC sliders/spinboxes/combos are not updated from the imported session,
  so old panel values overwrite the session on next interaction.
- Need `DRCPanel.set_params(params)` called from sync.
- Same for `EQPanel` — should have a `set_bands()` method instead of
  `_sync_ui_from_session` poking private `_BandStrip` attributes.

## General

- `_BandStrip._lbl` inner function duplicates `LabelWithHelp` pattern — unify.
- `_HelpButton` duplicated in both `eq_panel.py` and `drc_panel.py` — extract
  to shared `widgets.py`.
