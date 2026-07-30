# CLAUDE.md

## Project

GUI application for configuring SoundWire DAC EQ (7-band biquad equalizer) and DRC
(dynamic range compression) parameters, with real-time frequency response visualization
and register-write script generation.

## Coding Strategy

The goal is not a perfect system. It's a collection of **clearly bounded,
single-responsibility modules** — small, replaceable parts with high cohesion
and low coupling. When change comes, you only pay for the part you actually
need to modify.

Four structural layers achieve this, mapped directly to this project.

### 1. Dependency Inversion

**High-level policy never depends on low-level details. Both depend on abstractions.**

| Principle | In this project |
|-----------|----------------|
| Core logic owns the interface | `FilterDesigner` is a Protocol defined in `domain/eq/designer.py`. It declares "given params, return coefficients." The domain owns this contract. |
| Adapters implement the interface | `RBJDesigner` satisfies `FilterDesigner`. The core calls the port — it never knows which implementation is wired in. |
| Swap without touching core | A new designer implementation requires changing one line in the composition root (`main.py`). `eq_session.py`, `frequency_response.py`, the GUI — zero changes. |

```python
# domain/eq/designer.py — the port (owned by core)
class FilterDesigner(Protocol):
    def design(self, params: FilterParams, sample_rate: int) -> DesignedCoefficients: ...

# application/eq_session.py — depends only on the port
class EQSession:
    def __init__(self, designer: FilterDesigner): ...

# adapters/designers/rbj.py — an implementation, drop-in replaceable
class RBJDesigner:
    def design(self, params: FilterParams, sample_rate: int) -> DesignedCoefficients: ...
```

Same pattern applies to `DRCDesigner` and `ScriptFormatter` — every
external-facing concern is behind a port.

### 2. Strategy Pattern

**Encapsulate variable behavior behind an interface. Don't branch with `if-else`.**

| Principle | In this project |
|-----------|----------------|
| Pluggable algorithms | `ScriptFormatter` port: `BatScriptFormatter` generates `.bat` files today. `ExeExporter` (future) generates `.exe` downloads. Same port, drop-in swap. |
| Open for extension, closed for modification | Adding a JSON script formatter means one new file in `adapters/scripts/`. No existing code changes. |

```python
# application/ports.py
class ScriptFormatter(Protocol):
    def format(self, writes: list[RegisterWrite]) -> str: ...

# adapters/scripts/bat_formatter.py
class BatScriptFormatter:
    def format(self, writes: list[RegisterWrite]) -> str: ...

# adapters/scripts/exe_exporter.py (future)
class ExeExporter:
    def format(self, writes: list[RegisterWrite]) -> str: ...
```

### 3. Ports & Adapters (Hexagonal Architecture)

**The core knows nothing about the outside world. Dependencies point inward.**

| Layer | What lives here | Examples from this project |
|-------|----------------|---------------------------|
| **Domain** (innermost) | Pure business logic, value objects, ports | `FilterParams`, `BiquadCoefficients`, `DesignedCoefficients`, `QuantizedCoefficients`, `FilterDesigner` (port), `FrequencyResponse`, `RegisterWrite` |
| **Application** | Orchestration, session state, commands | `EQSession`, `DRCSession`, `ScriptComposer` |
| **Adapters** (outermost) | GUI, file I/O, script formatting, concrete designers | `MainWindow`, `BatScriptFormatter`, `RBJDesigner`, `pyqtgraph PlotWidget` |

```
     ┌──────────────────────────┐
     │   Adapters (outside)     │  ← PySide6, .bat files, pyqtgraph
     │  ┌────────────────────┐  │
     │  │  Application       │  │  ← EQSession, ScriptComposer
     │  │  ┌──────────────┐  │  │
     │  │  │   Domain     │  │  │  ← FilterParams, Quantizer, ports
     │  │  └──────────────┘  │  │
     │  └────────────────────┘  │
     └──────────────────────────┘
```

- **Driving adapter**: The PySide6 GUI calls `EQSession.update_band()`.
- **Driven adapter**: `ScriptComposer` calls `ScriptFormatter.format()` —
  the core doesn't know or care whether it's generating a `.bat` file or a `.exe`.

### 4. Feature Switches

**Wrap uncertain or toggleable features behind a switch. Control *when*, not *what*.**

| Switch | How it works |
|--------|-------------|
| Per-band EQ bypass | `EQSession.toggle_band(n)` — bypassed bands write passthrough coefficients and are excluded from the frequency response cascade. No band deletion, no special-case code. |
| DRC on/off | `DRCSession.bypass()` — when off, DRC register writes are omitted from the generated script. The transfer curve is hidden from the plot. |
| EQ reset level | Soft (`0x87`, data path only) vs. full (`0x8F`, data + coefficients). The `ScriptComposer` selects the reset command based on a single flag. |

### Summary

- **Clearly bounded modules** — `eq/`, `drc/`, `script/` in domain; one panel per adapter.
- **Pure core, oblivious to technology** — domain code imports nothing from PySide6, pyqtgraph, or the filesystem.
- **Communication through ports** — `FilterDesigner`, `DRCDesigner`, `ScriptFormatter`, `Observer`.
- **Pluggable strategies** — designers and formatters swap with one line.
- **Feature switches** — per-band bypass, DRC toggle, reset levels.

Don't build a perfect system on day one. Build a collection of independently
replaceable parts. When change comes, you pay only for the part you modify.

## Directory Structure

```
eq_script/
├── src/
│   ├── domain/
│   │   ├── eq/          (params, coefficients, designer port, frequency_response, quantizer, validity)
│   │   ├── drc/         (params, transfer_curve, designer)
│   │   └── script/      (register_map, commands)
│   ├── application/
│   │   ├── ports.py     (ScriptFormatter, Observer protocols)
│   │   ├── eq_session.py
│   │   ├── drc_session.py
│   │   └── script_composer.py
│   ├── adapters/
│   │   ├── designers/   (rbj.py, drc_hardware.py)
│   │   ├── scripts/     (bat_formatter.py, config_io.py)
│   │   └── gui/         (main_window, eq_panel, drc_panel, plot_canvas, widgets, i18n, help_dialog, copyright_dialog, coefficient_view)
│   └── main.py          (composition root)
├── scripts/
│   ├── run.py            (PyInstaller entry point)
│   └── eq_drc_tool.spec  (PyInstaller build config)
├── test/
│   ├── conftest.py       (--real-hardware option)
│   ├── test_quantizer.py (quantizer + inline golden RBJ test)
│   ├── test_integration.py
│   ├── test_protocol.py  (FSM rules)
│   └── test_register_map.py
├── doc/
│   ├── ref/
│   │   ├── DAC.docx              (CT_DAC register specification, REG1–REG27)
│   │   ├── rbj_cookbook.html     (RBJ biquad coefficient formulas)
│   │   ├── guildlines/           (EQ/DRC tuning guides — bundled in .exe)
│   │   └── example_bat/          (working .bat examples)
│   └── old_backup/               (legacy CLI tools, preserved for reference)
├── pyproject.toml
├── requirements.txt
├── CLAUDE.md
└── README.md
```

### Layer Architecture

**Layer 1 — Domain (pure business logic, no dependencies)**

| Module | Responsibility |
|--------|---------------|
| `eq/params.py` | `FilterParams` value object: freq, type, gain_db, Q |
| `eq/coefficients.py` | `BiquadCoefficients` value object: b0, b1, b2, a1, a2 (float64) |
| `eq/designer.py` | `FilterDesigner` port (Protocol) + `DesignedCoefficients` (float + Q2.14 quantized pair) |
| `eq/frequency_response.py` | Evaluate H(z) → magnitude/phase from 20 Hz–20 kHz |
| `eq/quantizer.py` | Float ↔ Q2.14: `quantize`, `dequantize`, `unpack_to_coeffs` |
| `eq/validity.py` | Check whether biquad coefficients are within Q2.14 range |
| `drc/params.py` | `DRCParams` value object: threshold_db, ratio, attack_ms, release_ms, makeup_gain_db, knee_db |
| `drc/transfer_curve.py` | Static DRC input→output level mapping |
| `drc/designer.py` | `DRCDesigner` port: DRCParams → DRC register values |
| `script/register_map.py` | Bank/address layout (48k: 0x30, 96k: 0x45, 192k: 0x5A) |
| `script/commands.py` | `RegisterWrite` value object: address + value |

**Layer 2 — Application (orchestration, depends on ports not implementations)**

| Module | Responsibility |
|--------|---------------|
| `ports.py` | Application-layer ports: `ScriptFormatter`, `Observer` (`FilterDesigner` and `DRCDesigner` are domain ports) |
| `eq_session.py` | Observable state of 7 EQ bands, per-band bypass toggle |
| `drc_session.py` | Observable DRC state, bypass toggle |
| `script_composer.py` | EQSession + DRCSession → list of RegisterWrite commands |

**Layer 3 — Adapters (implement ports, contain all tech details)**

| Adapter | Implements |
|---------|------------|
| `designers/rbj.py` | `RBJDesigner` — RBJ Audio EQ Cookbook biquad formulas |
| `designers/drc_hardware.py` | `HardwareDrcDesigner` — converts DRCParams → DrcRegisters |
| `scripts/bat_formatter.py` | `BatScriptFormatter` — .bat file with PowerShell register writes |
| `scripts/config_io.py` | JSON import/export for EQ+DRC configuration |
| `gui/main_window.py` | PySide6 QMainWindow — top-level window, menu, file ops |
| `gui/eq_panel.py` | 7 band strips: slider, filter type selector, bypass checkbox |
| `gui/drc_panel.py` | DRC parameter controls + enable toggle + extend window |
| `gui/plot_canvas.py` | pyqtgraph tabs: magnitude, phase, DRC transfer curve |
| `gui/i18n.py` | EN/ZH translation tables, OS language detection |
| `gui/widgets.py` | `HelpButton` ("?" tooltip) and `LabelWithHelp` |
| `gui/help_dialog.py` | EQ/DRC tuning guide viewer in English and Chinese |
| `gui/copyright_dialog.py` | About / copyright dialog |
| `gui/coefficient_view.py` | Table showing quantized hex values (unused, reserved) |

## Q-Format

- **Q2.14** (16-bit per coefficient, 2 per 32-bit register): 1 sign + 1 integer + 14 fractional bits
- Range [-2.0, 2.0), scale = 2^14 = 16384
- `0x4000` = 1.0; `0xC000` = -1.0
- Register packing: B=0 (b0/b2), B=1 (b1/a2), B=2 (a1/placeholder)
- Upper 16 bits = first coefficient, lower 16 bits = second coefficient
- a1, a2 use **negated feedback** convention: na1 = -a1, na2 = -a2
- B=2 lower 16 bits (the "gain" placeholder) are unused
- This project is independent of the DSP project's Q1_30 format

## EQ Register Map

**REG10–REG15**

| Register | Address | Role |
|----------|---------|------|
| REG10 | 0x00002060 | EQ coefficient 1 MSB (8 bits) |
| REG11 | 0x00002061 | EQ coefficient 1 LSB (8 bits) |
| REG12 | 0x00002062 | EQ coefficient 2 MSB (8 bits) |
| REG13 | 0x00002063 | EQ coefficient 2 LSB (8 bits) |
| REG14 | 0x00002064 | `dacs_eq_bank_command` — 7-bit address in bits 6:0 |
| REG15 | 0x00002065 | `dacs_eq_control_command` — 8 control bits |

EQ address map: decimal 48–68 (Bank 0 / 48k), 69–89 (Bank 1 / 96k), 90–110 (Bank 2 / 192k).
Each stage uses 3 consecutive addresses. Address 111 = completion trigger (write here to exit CONFIG → WAIT).

### EQ FSM

```
Power-on → IDLE → WAIT ⇄ CONFIG
                          ↓ (write to addr 111)
                         WAIT → RUNNING (auto, data valid)
                
Reset (any state) → IDLE → WAIT
```

- **Enter CONFIG**: `manual_mode=1 & config_mode=1` (0x93), WAIT→CONFIG. Set twice for timing margin.
- **Exit CONFIG**: Only two ways: (1) write to address 111, or (2) reset. `config_mode=0` does NOT exit.
- **RUNNING**: Hardware auto-transitions from WAIT when input data is valid.

**REG15 Bit Map**

| Bit | Name | Description |
|-----|------|-------------|
| 7 | disable_ae_interruption | 1 = disable MFPU AE interrupt |
| 6 | manual_read_en | Rising edge triggers coefficient read |
| 5 | manual_write_en | Rising edge triggers coefficient write |
| 4 | manual_configuration_mode | 1 = enter CONFIG state |
| 3 | reset_mode | 0 = reset data path only; 1 = reset data path + coefficients |
| 2 | manual_reset | 1 = trigger reset → IDLE |
| 1 | manual_en | 1 = enable EQ in manual mode |
| 0 | manual_mode | 1 = CT register control (not MFPU) |

**REG15 Commands**

| Command | Value | Bits active |
|---------|-------|-------------|
| Enter CONFIG | 0x93 | config_mode + manual_en + manual_mode |
| Write pulse | 0xA3 | write_en + manual_en + manual_mode (config_mode=0, stays in CONFIG) |
| Read pulse | 0xC3 | read_en + manual_en + manual_mode (config_mode=0, stays in CONFIG) |
| Reset data path only | 0x87 | manual_reset + manual_en + manual_mode (config_mode=0, exits to IDLE) |
| Reset data + coefficients | 0x8F | reset_mode + manual_reset + manual_en + manual_mode (config_mode=0, exits to IDLE) |

Bit 7 is always set to 1 (disable AE) in all commands.

### Clock Requirement

Hardware configuration requires the DAC2 clock to be active. Two options:

1. **Check**: Read `0x41080180` — if 0, clock is ready.
2. **Force**: Set REG16 bit4 (`ct_dacs_eq_drc_force_clk_en`) = 1 to force clock on.

The app uses method 2: force clock before config, release after.

**EQ Init + Write (full protocol):**
```
REG16 = 0x10               # Force clock (bit4=1), DRC unchanged
REG15 = 0x87 (or 0x8F)    # Reset → IDLE → WAIT
REG15 = 0x93 (×2)          # Enter CONFIG
REG10–REG13 = 0x00         # Clear coeff registers
REG14 = 0x00               # Clear address register

For each coeff group (21 groups total):
  REG10–REG13 = 4 bytes    # coe1 MSB, coe1 LSB, coe2 MSB, coe2 LSB
  REG14 = addr             # 0x30–0x6E
  REG15 = 0xA3             # Write pulse, stays in CONFIG

REG14 = 0x6F               # Completion address (111)
REG15 = 0xA3               # Write → exits CONFIG → WAIT → RUNNING
REG16 = 0x00               # Release clock force
```

**EQ Read-back Protocol:**
```
REG16 = 0x10               # Force clock
REG15 = 0x93 (×2)          # Enter CONFIG
REG14 = target addr        # 0x30–0x6E
REG15 = 0xC3               # Read pulse, stays in CONFIG
Read REG10–REG13           # Get coefficient data
REG14 = 0x6F               # Completion
REG15 = 0xA3               # Exit CONFIG → WAIT → RUNNING
REG16 = 0x00               # Release clock force
```

## DRC Register Map

**REG16–REG27**

| Register | Address | Content | Format |
|----------|---------|---------|--------|
| REG16 | 0x00002066 | `dacs_drc_control_command` | Bit flags |
| REG17 | 0x00002067 | `drc_threshold[15:8]` (MSB) | 1.7.8 signed dB |
| REG18 | 0x00002068 | `drc_threshold[7:0]` (LSB) | 1.7.8 signed dB |
| REG19 | 0x00002069 | `drc_update_window_length` | Sample count (≥ 96) |
| REG20 | 0x0000206A | `drc_attack_coe[9:2]` (MSB 8) | Q1.15 exp decay |
| REG21 | 0x0000206B | `drc_release_coe[9:2]` (MSB 8) | Q1.15 exp decay |
| REG22 | 0x0000206C | Ratio + attack[1:0] + release[1:0] | Mixed bits |
| REG23 | 0x0000206D | `drc_gain_compute_floating` | Threshold smoothing (≥ 0x40) |
| REG24 | 0x0000206E | `drc_noise_gate` | Scaled (exact = {3'd0, val, 5'd0}) |
| REG25 | 0x0000206F | Timeout + gain balance mode | Mixed bits |
| REG26 | 0x0000205E | `drc_makeup_gain` | Scaled (exact = {3'd0, val, 5'd0}) |
| REG27 | 0x0000205F | `drc_max_drc_db_out` | Default: 0x6000 (exact = {val, 8'd0}) |

**REG16 Bit Map**

| Bit | Name | Description |
|-----|------|-------------|
| 7 | disable_ae_interruption | 1 = disable DRC MFPU AE interrupt |
| 6 | disable UMP check | 1 = disable MFPU UMP check content |
| 5 | disable UMP timeout | 1 = disable MFPU UMP timeout |
| 4 | force clock enable | 1 = force DAC2 clock for config |
| 3 | ramp down tail | 0 = UAJ length, 1 = 4× UAJ length |
| 1 | manual_en | 0 = bypass DRC, 1 = enable DRC |
| 0 | manual_mode | 0 = MFPU control, 1 = CT register control |

DRC enable: REG16 = 0xC3 (disable AE + disable UMP check + manual_en + manual_mode).
DRC disable + clock force: REG16 = 0x50 (disable UMP check + disable UMP timeout + force clock).
DRC disable: REG16 = 0x00.

**DRC Threshold format:** 1 sign + 7 integer + 8 fractional bits. 0 dB = 0x58FA.
To set -N dB: `0x58FA - N * 256`. Reference config: 0x40FA = -24 dB.

**DRC Attack/Release computation:**
`coeff = exp(-ln(9) / (Fs * attack_time_s))` quantized to Q1.15.
Hardware prepends bits [15:10] = `011111` (value ≈ 0.969).
Store bits [9:2] → REG20/REG21, bits [1:0] → REG22[3:2]/REG22[1:0].

**DRC Config Sequence:**
1. REG16 = 0x50 (force clock + disable DRC — bit6+5+4 = 1)
2. Write REG17–REG27 parameter values
3. REG16 = 0xC3 (release clock force + enable DRC manual mode)

REG22 compress ratio table:
| Bits | Ratio |
|------|-------|
| 000 | ∞ (infinity) |
| 001 | 0.125 |
| 010 | 0.25 |
| 011 | 0.375 |
| 100 | 0.5 |
| 101 | 0.625 |
| 110 | 0.75 |
| 111 | 0.875 |

## pyqtgraph 0.14 Compatibility

The app targets pyqtgraph 0.14, which removed `PlotItem.ctrl` as a publicly
accessible attribute via `PlotWidget.__getattr__` (it's not callable). Key patterns:

- **No `plot.ctrl` access**: use `plot.getPlotItem().ctrl` directly for the internal
  `logXCheck`, `logYCheck`, etc.
- **`setLogMode` triggers `enableAutoRange()`**: `PlotItem.setLogMode()` → `updateLogMode()`
  → `enableAutoRange()` re-enables auto-range for **both** X and Y axes. Re-apply
  `_fix_x`/`_fix_y` on the internal `logXCheck.toggled` signal.
- **Log x-axis range uses log10 values**: pyqtgraph's `setXRange` in log mode takes
  `log10(val)`. Linear mode takes the actual value.
  ```python
  def _fix_x(plot, log_x):
      vb = plot.getPlotItem().vb
      vb.disableAutoRange(axis=pg.ViewBox.XAxis)
      if log_x:
          vb.setXRange(np.log10(0.02), np.log10(20.0), padding=0)
      else:
          vb.setXRange(0.0, 20.0, padding=0)
  ```

### Plot Configuration vs. Data

Axis configuration (ranges, log/linear mode) is **separated** from data updates:

- **Config** — set once during `__init__` and re-applied on log toggle via
  `pi.ctrl.logXCheck.toggled`. Includes `_fix_x` (X: 0–20 kHz linear,
  log10 range for log) and `_fix_y` (Y: ±12 dB or ±180°).
- **Data** — updated on every `update()` call when EQ/DRC parameters change.
  Axis ranges are not touched.
- **Default**: linear X, log X available via right-click menu → Transform → Log X.
- Custom "Log X" and "Fit Y" checkboxes were **removed** — they conflicted with
  pyqtgraph's internal state machine. Use the right-click menu instead.

## Key Decisions

### GUI: PySide6 + pyqtgraph
- pyqtgraph for real-time frequency response plot (log axes, 60fps, zoom/pan)
- Native Windows look, cross-platform (Linux possible later)
- Packaged via PyInstaller `--onefile` → single portable .exe (~100–130MB)
- LGPL license, manageable compliance via dynamic linking

### Frequency Response Range
- Frequency response is computed from **20 Hz to 20 kHz** (standard audible range),
  not to Nyquist. Prevents x-axis overflow beyond the intended display range.

### `DesignedCoefficients` and `dequantize`
- `FilterDesigner.design()` returns `DesignedCoefficients` — a frozen dataclass
  containing both `float_coeffs: BiquadCoefficients` and `quantized: QuantizedCoefficients`.
  This eliminates separate `quantize()` calls in the application layer.
- `dequantize(value)` and `unpack_to_coeffs(q)` are shared in `quantizer.py` —
  the single source of truth for Q2.14 ↔ float conversion. No duplicated dequant
  logic in `frequency_response.py`.
- `DRCParams` is `frozen=True` (same as `FilterParams`) — prevents aliasing bugs
  from shared mutable defaults.

### Coefficient Source
- `RBJDesigner` — RBJ Audio EQ Cookbook formulas (ref: `doc/ref/rbj_cookbook.html`).
  Computes biquad coefficients analytically at runtime — no pre-computed lookup tables.

### Feature Switches
- Per-band EQ bypass (writes bypass coefficients, omitted from freq response)
- DRC on/off toggle (REG16 = 0xC3 / 0x00)
- Two EQ reset levels: soft (data path only, 0x87) / full (data + coefficients, 0x8F)

### Script Generation
- `.bat` file export with full EQ+DRC protocol (init reset → coefficient writes → release)
- EQ read-back support (REG15 = 0xC3) for hardware verification
- Future: direct `.exe` parameter download tool via additional `ScriptFormatter` plugin

### Deployment
- Develop in project-specific Python venv with pip-installed dependencies
- Package with PyInstaller via `scripts/eq_drc_tool.spec` → portable .exe (~64 MB), no installation
- Build tooling in `scripts/`: `run.py` (entry point), `eq_drc_tool.spec` (build config)
- Release: tag with `pyproject.toml` version → build → upload to GitHub Releases
- Target: Windows first, Linux possible later

## Testing

| Layer | What it validates |
|--------|-------------------|
| Designer | `RBJDesigner.design()` → correct Q2.14 hex. Golden data (21 peak + bypass entries at 48k/96k/192k) is inline in `test_quantizer.py`. |
| Quantizer | Float coeffs → Q2.14 32-bit packed words. Hand-computed expected values for bypass, negated feedback, range clamping. |
| Register Map | Bank/stage/group → correct REG14 address (`test_register_map.py`). |
| Protocol | Write/read/reset sequences obey FSM rules (`test_protocol.py`). Uses `StubDesigner`. |
| Integration | Full pipeline: params → designer → quantizer → .bat script (`test_integration.py`). |

Run: `python -m pytest test/ -v`

## Deployment

Build the standalone `.exe`:

```
pip install pyinstaller
pyinstaller scripts/eq_drc_tool.spec
```

Output: `dist/eq_drc_tool.exe` (~64 MB, self-contained, no Python installation needed).

The `.spec` bundles `doc/ref/guildlines/` (help guides loaded at runtime).
`pyproject.toml` version → Git tag → GitHub Release.

### SdwRegisterTool Interface

From `SdwRegisterTool.ps1` and `doc/ref/example_running/`:

```
Usage:  SdwRegisterTool.exe w reg <hex_addr> <hex_val>     # write byte
        SdwRegisterTool.exe r reg <hex_addr>                # read byte

Output: Address=<hex> Value=<hex> Status=<hex>
        Status=0x00000000 → success; any other value → failure
```

Arguments are hex without `0x` prefix (lowercase). The `.ps1` is a thin
wrapper that strips `0x`, delegates to `.exe`, and parses the key=value output.

Offline tests use a mock (`mock_sdw_tool.py`) that records writes and returns
configurable read values. Online tests (flag: `--real-hardware`) use the real
`.exe` from `doc/ref/example_running/`.
