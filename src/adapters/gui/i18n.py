import locale
import os
import sys
from enum import Enum


class Lang(Enum):
    EN = "en"
    ZH = "zh"


def detect_os_language() -> Lang:
    """Detect OS language. Returns Lang.EN or Lang.ZH."""
    if sys.platform == "win32":
        import ctypes
        try:
            lcid = ctypes.windll.kernel32.GetUserDefaultUILanguage()
            if lcid in (0x0804, 0x0404, 0x0C04, 0x1004):  # zh-CN, zh-TW, zh-HK, zh-SG
                return Lang.ZH
        except Exception:
            pass
    for loc in (os.environ.get("LANG", ""), os.environ.get("LC_ALL", ""),
                os.environ.get("LC_MESSAGES", "")):
        if loc.startswith("zh"):
            return Lang.ZH
    return Lang.EN


# --- Translation tables ---
_EN = {
    # Window
    "app.title": "EQ+DRC Configuration Tool",
    # Menu
    "menu.file": "&File",
    "menu.file.import": "&Import Config...",
    "menu.file.export": "&Export Config...",
    "menu.file.export_bat": "Export .bat Script...",
    "menu.file.exit": "E&xit",
    "menu.language": "&Language",
    "menu.lang.en": "English",
    "menu.lang.zh": "中文",
    "menu.help": "&Help",
    "menu.help.eq_guide": "EQ Tuning Guide",
    "menu.help.drc_guide": "DRC Tuning Guide",
    "menu.help.about": "&About / Copyright",
    # EQ panel
    "eq.title": "EQ Bands",
    "eq.stage": "Stage {}",
    "eq.type": "Type",
    "eq.freq": "Freq",
    "eq.gain": "Gain",
    "eq.q": "Q",
    "eq.bypass": "Bypass",
    "eq.q_warn": "Q2.14 quantization FAILED for Stage {}: {}",
    # DRC panel
    "drc.title": "DRC",
    "drc.enable": "Enable DRC",
    "drc.threshold": "Threshold",
    "drc.ratio": "Ratio",
    "drc.attack": "Attack",
    "drc.release": "Release",
    "drc.makeup_gain": "Makeup Gain",
    "drc.update_window": "Update Window",
    "drc.gain_compute": "Gain Compute",
    "drc.noise_gate": "Noise Gate",
    "drc.gain_balance": "Gain Balance",
    "drc.max_output": "Max Output",
    "drc.window_extend": "Extend Range",
    # Plot
    "plot.magnitude": "Magnitude",
    "plot.phase": "Phase",
    "plot.frequency_khz": "Frequency (kHz)",
    "plot.magnitude_db": "Magnitude (dB)",
    "plot.phase_deg": "Phase (°)",
    "plot.input_db": "Input (dB)",
    "plot.output_db": "Output (dB)",
    "plot.log_x": "Log X",
    "plot.lin_x": "Lin X",
    "plot.fit_x": "Fit X",
    "plot.fit_y": "Fit Y",
    "plot.legend": "Legend",
    "plot.show_band": "Stage {}",
    "plot.drc": "DRC Transfer Curve",
    "plot.show_drc": "DRC Curve",
    "plot.show_float_vs_q": "Float vs Q2.14 Diff",
    # Filter types
    "ftype.0": "Bypass",
    "ftype.1": "Peak",
    "ftype.2": "Notch",
    "ftype.3": "Lowshelf",
    "ftype.4": "Highshelf",
    "ftype.5": "HPF",
    "ftype.6": "LPF",
    # Dialogs
    "dialog.export_ok": "Export Complete",
    "dialog.export_ok_msg": "Script saved to:\n{}",
    "dialog.import_ok": "Import Complete",
    "dialog.import_ok_msg": "Configuration loaded from:\n{}",
    "dialog.about_title": "About / Copyright",
    "dialog.help_export": "Export .md",
    # Config
    "config.filter": "BAT Files (*.bat);;All Files (*)",
    "config.json_filter": "JSON Files (*.json);;All Files (*)",
    "config.md_filter": "Markdown Files (*.md);;All Files (*)",
    "config.import_error": "Import Failed",
    "config.import_error_msg": "Could not load config:\n{}",
    # Help tooltips — EQ
    "help.eq.type": "Filter Type. Bypass=passthrough, Peak=boost/cut, Notch=RBJ notch (infinite null, Q controls width), Lowshelf/Highshelf=tilting EQ, HPF/LPF=edges.",
    "help.eq.freq": "Center Frequency (Hz). Adjustable 20–20000 Hz.",
    "help.eq.gain": "Gain (dB). Boost/cut level. Not used by HPF/LPF/Notch.",
    "help.eq.q": "Quality Factor (Q). Controls filter bandwidth. Lower Q = wider band, higher Q = narrower.",
    "help.eq.bypass": "Bypass this stage. Bypassed stages write passthrough coefficients and are excluded from frequency response.",
    "help.ftype.0": "Bypass: signal passes through unchanged.",
    "help.ftype.1": "Peaking: boost or cut at center frequency using RBJ peaking formula.",
    "help.ftype.2": "Notch: RBJ notch filter. Creates deep null at center frequency. Q controls width. Gain not used.",
    "help.ftype.3": "Lowshelf: tilts low frequencies up/down below center frequency.",
    "help.ftype.4": "Highshelf: tilts high frequencies up/down above center frequency.",
    "help.ftype.5": "HPF: high-pass filter. Only freq and Q used. Gain not used.",
    "help.ftype.6": "LPF: low-pass filter. Only freq and Q used. Gain not used.",
    # Help tooltips — DRC
    "help.drc.enable": "Enable DRC block. When enabled, DRC parameters are written to the register script.",
    "help.drc.threshold": "ct_dacs_drc_threshold[15:0]. 1.7.8 signed dB. 0 dB = 0x58FA. Range [-80, 0] dB. Signals above threshold are compressed.",
    "help.drc.update_window": "ct_dacs_drc_update_window_length. Samples per DRC update window. < 96 risks THD-N from per-sample gain updates.",
    "drc.window_extend_warn": "WARNING: Values < 96 may cause THD-N degradation.",
    "help.drc.window_extend": "Extend update window range to [0, 255]. Values below 96 may cause THD-N issues.",
    "help.drc.attack": "ct_dacs_drc_attack_coe[9:2]+[1:0]. 10-bit register value. HW prepends 6-bit 011111 prefix. Time computed at 48k/96k/192k.",
    "help.drc.release": "ct_dacs_drc_release_coe[9:2]+[1:0]. 10-bit register value. HW prepends 6-bit 011111 prefix. Time computed at 48k/96k/192k.",
    "help.drc.ratio": "ct_dacs_drc_compress_ratio[2:0]. Compression slope. 000=∞:1 (brickwall), 001=8:1, 010=4:1, 011=2.67:1, 100=2:1, 101=1.6:1, 110=1.33:1, 111=1.14:1.",
    "help.drc.gain_compute": "ct_dacs_drc_gain_compute_floating. Hysteresis margin to prevent DRC oscillation around threshold. Minimum 0x40. Range [0x40, 0xFF].",
    "help.drc.noise_gate": "ct_dacs_drc_noise_gate[7:0]. 1.7.8 signed dB. Signals below this level are forced to zero. Prevents IIR filter tail. exact = {3'd0, val, 5'd0} → dB = -(0x58FA - exact)/256.",
    "help.drc.gain_balance": "ct_dacs_drc_gain_balance_mode[1:0]. 00=independent L/R, 01=use left, 10=use right, 11=use max.",
    "help.drc.makeup_gain": "ct_dacs_drc_makeup_gain[7:0]. Absolute dB gain added after compression. Q8.8 unsigned. exact = {3'd0, val, 5'd0} → dB = val/8. Range [0, 31.875].",
    "help.drc.max_output": "ct_dacs_drc_max_drc_db_out[7:0]. Clamps output after compression. exact = {val, 8'd0} → dB = val - 88.98. Constraint: exact_makeup + exact_max_output ≤ 0x58FA.",
}

_ZH = {
    "app.title": "EQ+DRC 配置工具",
    "menu.file": "文件(&F)",
    "menu.file.import": "导入配置(&I)...",
    "menu.file.export": "导出配置(&E)...",
    "menu.file.export_bat": "导出 .bat 脚本...",
    "menu.file.exit": "退出(&X)",
    "menu.language": "语言(&L)",
    "menu.lang.en": "English",
    "menu.lang.zh": "中文",
    "menu.help": "帮助(&H)",
    "menu.help.eq_guide": "EQ 调试指南",
    "menu.help.drc_guide": "DRC 调试指南",
    "menu.help.about": "关于 / 版权(&A)",
    "eq.title": "EQ 频段",
    "eq.stage": "频段 {}",
    "eq.type": "类型",
    "eq.freq": "频率",
    "eq.gain": "增益",
    "eq.q": "质量因子(Q)",
    "eq.bypass": "旁通",
    "eq.q_warn": "Q2.14 量化失败 频段 {}: {}",
    "drc.title": "DRC",
    "drc.enable": "启用 DRC",
    "drc.threshold": "门限",
    "drc.ratio": "压缩比",
    "drc.attack": "启动时间",
    "drc.release": "释放时间",
    "drc.makeup_gain": "补偿增益(Makeup Gain)",
    "drc.update_window": "更新窗口(Update Window)",
    "drc.gain_compute": "增益计算(Gain Compute)",
    "drc.noise_gate": "噪声门限(Noise Gate)",
    "drc.gain_balance": "增益平衡(Gain Balance)",
    "drc.max_output": "最大输出(Max Output)",
    "drc.window_extend": "扩展范围(Extend Range)",
    "plot.magnitude": "幅度响应",
    "plot.phase": "相位响应",
    "plot.frequency_khz": "频率 (kHz)",
    "plot.magnitude_db": "幅度 (dB)",
    "plot.phase_deg": "相位 (°)",
    "plot.input_db": "输入 (dB)",
    "plot.output_db": "输出 (dB)",
    "plot.log_x": "对数 X",
    "plot.lin_x": "线性 X",
    "plot.fit_x": "自适应 X",
    "plot.fit_y": "自适应 Y",
    "plot.legend": "图例",
    "plot.show_band": "频段 {}",
    "plot.drc": "DRC 压缩曲线",
    "plot.show_drc": "DRC 曲线",
    "plot.show_float_vs_q": "浮点 vs Q2.14 量化误差",
    "ftype.0": "旁通(Bypass)",
    "ftype.1": "峰形(Peak)",
    "ftype.2": "陷波(Notch)",
    "ftype.3": "低搁架(Lowshelf)",
    "ftype.4": "高搁架(Highshelf)",
    "ftype.5": "高通(HPF)",
    "ftype.6": "低通(LPF)",
    "dialog.export_ok": "导出完成",
    "dialog.export_ok_msg": "脚本已保存至:\n{}",
    "dialog.import_ok": "导入完成",
    "dialog.import_ok_msg": "配置已从以下文件加载:\n{}",
    "dialog.about_title": "关于 / 版权",
    "dialog.help_export": "导出 .md",
    "config.filter": "BAT 文件 (*.bat);;所有文件 (*)",
    "config.json_filter": "JSON 文件 (*.json);;所有文件 (*)",
    "config.md_filter": "Markdown 文件 (*.md);;所有文件 (*)",
    "config.import_error": "导入失败",
    "config.import_error_msg": "无法加载配置:\n{}",
    # 帮助提示 — EQ
    "help.eq.type": "滤波器类型(Type). 直通=旁路, 峰值=增益/衰减, 陷波=RBJ陷波(无限深, Q控制宽度), 低架/高架=倾斜EQ, HPF/LPF=边缘滤波.",
    "help.eq.freq": "中心频率(Freq) (Hz). 可调范围 20–20000 Hz.",
    "help.eq.gain": "增益(Gain) (dB). 提升/衰减量. HPF/LPF/陷波不使用此参数.",
    "help.eq.q": "质量因子(Q). 控制滤波器带宽. Q越低=带宽越宽, Q越高=带宽越窄.",
    "help.eq.bypass": "旁路此频段. 旁路的频段写入直通系数, 不参与频率响应计算.",
    "help.ftype.0": "直通(Bypass): 信号无变化通过.",
    "help.ftype.1": "峰值(Peak): 在中心频率处提升或衰减.",
    "help.ftype.2": "陷波(Notch): RBJ陷波滤波器. 在中心频率处产生深零点. Q控制宽度. 不使用增益参数.",
    "help.ftype.3": "低架(Lowshelf): 在中心频率以下倾斜低频频谱.",
    "help.ftype.4": "高架(Highshelf): 在中心频率以上倾斜高频频谱.",
    "help.ftype.5": "高通(HPF): 高通滤波器. 仅使用频率和Q参数. 不使用增益参数.",
    "help.ftype.6": "低通(LPF): 低通滤波器. 仅使用频率和Q参数. 不使用增益参数.",
    # 帮助提示 — DRC
    "help.drc.enable": "启用DRC模块. 启用后DRC参数将写入寄存器脚本.",
    "help.drc.threshold": "ct_dacs_drc_threshold[15:0]. 1.7.8 有符号dB. 0 dB = 0x58FA. 范围 [-80, 0] dB. 超过阈值的信号被压缩.",
    "help.drc.update_window": "ct_dacs_drc_update_window_length. 每窗口采样数. < 96 可能因逐点更新增益导致THD-N.",
    "drc.window_extend_warn": "警告: 数值 < 96 可能导致THD-N性能下降.",
    "help.drc.window_extend": "扩展更新窗口范围至 [0, 255]. 低于96可能导致THD-N问题.",
    "help.drc.attack": "ct_dacs_drc_attack_coe[9:2]+[1:0]. 10位寄存器值. 硬件前置6位011111前缀. 显示48k/96k/192k下的计算时间.",
    "help.drc.release": "ct_dacs_drc_release_coe[9:2]+[1:0]. 10位寄存器值. 硬件前置6位011111前缀. 显示48k/96k/192k下的计算时间.",
    "help.drc.ratio": "ct_dacs_drc_compress_ratio[2:0]. 压缩斜率. 000=∞:1 (限制器), 001=8:1, 010=4:1, 011=2.67:1, 100=2:1, 101=1.6:1, 110=1.33:1, 111=1.14:1.",
    "help.drc.gain_compute": "ct_dacs_drc_gain_compute_floating. 迟滞裕量, 防止DRC在阈值附近振荡. 最小值 0x40. 范围 [0x40, 0xFF].",
    "help.drc.noise_gate": "ct_dacs_drc_noise_gate[7:0]. 1.7.8 有符号dB. 低于此电平的信号被强制归零. 防止IIR滤波器拖尾. exact = {3'd0, val, 5'd0} → dB = -(0x58FA - exact)/256.",
    "help.drc.gain_balance": "ct_dacs_drc_gain_balance_mode[1:0]. 00=独立L/R, 01=使用左声道, 10=使用右声道, 11=使用最大值.",
    "help.drc.makeup_gain": "ct_dacs_drc_makeup_gain[7:0]. 压缩后添加的绝对dB增益. Q8.8无符号. exact = {3'd0, val, 5'd0} → dB = val/8. 范围 [0, 31.875].",
    "help.drc.max_output": "ct_dacs_drc_max_drc_db_out[7:0]. 压缩后输出上限钳位. exact = {val, 8'd0} → dB = val - 88.98. 约束: exact_makeup + exact_max_output ≤ 0x58FA.",
}

_TABLES = {Lang.EN: _EN, Lang.ZH: _ZH}


def tr(key: str, lang: Lang) -> str:
    """Return translated string for the given key."""
    return _TABLES.get(lang, _EN).get(key, _EN.get(key, key))


_current_lang: Lang = Lang.EN


def set_language(lang: Lang) -> None:
    global _current_lang
    _current_lang = lang


def get_language() -> Lang:
    return _current_lang


def _(key: str) -> str:
    """Shortcut for tr() using current global language."""
    return tr(key, _current_lang)
