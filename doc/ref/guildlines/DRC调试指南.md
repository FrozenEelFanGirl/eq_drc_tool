# DRC 调试指南

## 默认配置

### 架构概览

DRC 模块为 **3 频段多段动态范围压缩器**，位于 Pre-EQ 之后、Post-EQ 之前。

```
Input → LR4 Crossover ─┬─ Low  → Compressor ─┬─→ Sum → Post-Gain → Output
                       ├─ Mid  → Compressor ─┤
                       └─ High → Compressor ─┘
```

全频信号先经 LR4 分频器拆分为 3 个频段，每个频段独立压缩，最后合并并施加全局输出增益。

### Crossover 分频点

| 参数 | 默认值 | 说明 |
|------|-------|------|
| Split 1（低/中频分界） | 250 Hz | 低音与中频的分割点 |
| Split 2（中/高频分界） | 2.5 kHz | 中频与高频的分割点 |
| 滤波器类型 | LR4 (24 dB/oct) | 2 级 Q=0.7071 Butterworth 级联，LP+HP 幅度和恒为 1 |

### 低频段压缩器（< 250 Hz）

| 参数 | 默认值 | 范围 | 说明 |
|------|-------|------|------|
| Threshold | –24 dBFS | 0 ～ –96 dBFS | 门限以上开始压缩 |
| Ratio | 2:1 | 1:1 ～ ∞:1 | 压缩比；∞:1 = 砖墙限制 |
| Attack | 10 ms | 0.1 ～ 500 ms | 压缩响应速度 |
| Release | 100 ms | 5 ～ 5000 ms | 压缩恢复速度 |
| Knee Width | 4 dB | 0 ～ 24 dB | 0 = 硬拐点；>0 = 软拐点过渡区宽度 |
| Knee Type | Soft | Hard / Soft | 拐点曲线类型 |
| Envelope Mode | Hybrid | Peak / RMS / Hybrid | 包络检测器模式 |
| Makeup Gain | 0 dB | –24 ～ +24 dB | 压缩后补偿增益 |
| Bypass | 关闭 | — | 单频段旁通 |

### 中频段压缩器（250 Hz ～ 2.5 kHz）

| 参数 | 默认值 | 同低频段 |
|------|-------|---------|
| Threshold | –24 dBFS | 同上 |
| Ratio | 2:1 | 同上 |
| Attack | 10 ms | 同上 |
| Release | 100 ms | 同上 |
| Knee Width | 4 dB | 同上 |
| Knee Type | Soft | 同上 |
| Envelope Mode | Hybrid | 同上 |
| Makeup Gain | 0 dB | 同上 |

### 高频段压缩器（> 2.5 kHz）

| 参数 | 默认值 | 同低频段 |
|------|-------|---------|
| Threshold | –24 dBFS | 同上 |
| Ratio | 2:1 | 同上 |
| Attack | 10 ms | 同上 |
| Release | 100 ms | 同上 |
| Knee Width | 4 dB | 同上 |
| Knee Type | Soft | 同上 |
| Envelope Mode | Hybrid | 同上 |
| Makeup Gain | 0 dB | 同上 |

### 全局参数

| 参数 | 默认值 | 范围 | 说明 |
|------|-------|------|------|
| Post Gain | 0 dB | 0 ～ –96 dB | 全局衰减（防止频段合并后削波） |

---

## 参数调试指南

### Threshold（门限）

| 场景 | 建议范围 | 说明 |
|------|---------|------|
| 轻度动态控制 | –10 ～ –20 dBFS | 仅压缩信号峰值，保留大部分动态 |
| 中等压缩 | –20 ～ –40 dBFS | 明显降低动态范围，适合流行/摇滚 |
| 重度压缩 | –40 ～ –60 dBFS | 广播/播客风格，动态极小 |
| 砖墙限制 | –0.5 ～ –3 dBFS | 配合高 Ratio 防止削波 |

**调试原则：**
- 门限越低 = 压缩起效越早 = 平均响度越高，但动态越小
- 先设置门限使 Gain Reduction 表在峰值时显示 3–6 dB 的衰减，再根据需要调整
- 低频段可设置略低的门限，防止低音能量波动引发整体抽吸（pumping）

### Ratio（压缩比）

| Ratio | 听感 | 适用场景 |
|-------|------|---------|
| 1.5:1 ～ 2:1 | 轻微、透明 | 母带压缩、古典音乐 |
| 3:1 ～ 4:1 | 明显但不激进 | 人声、乐器、流行音乐 |
| 6:1 ～ 10:1 | 强压缩 | 广播人声、高动态录音 |
| ∞:1 | 砖墙限制 | 峰值保护、输出限幅 |

**调试原则：**
- 低频段用较低 Ratio（2:1），避免低音"失力"
- 高频段可略高 Ratio（3:1 ～ 4:1），控制齿音和刺耳瞬态
- Ratio 和 Threshold 联动：低 Ratio + 低 Threshold ≈ 高 Ratio + 高 Threshold，但前者听感更自然

### Attack（启动时间）

| 时间 | 听感 | 适用场景 |
|------|------|---------|
| 0.1 ～ 1 ms | 极快，压制瞬态 | 峰值限制、防削波 |
| 1 ～ 10 ms | 快，保留部分冲击力 | 流行人声、鼓组 |
| 10 ～ 50 ms | 中等，保留冲击感 | 混音总线、乐器编组 |
| 50 ～ 500 ms | 慢，保留完整瞬态 | 母带压缩、追求透明感 |

**调试原则：**
- Attack 越快 = 越压制瞬态 = 声音越"柔和"但可能失去冲击力
- Attack 越慢 = 瞬态穿过 = 保留冲击力但可能无法控制峰值
- 多频段 DRC 中，低频段可用较快 Attack（防止低音"拖尾"），高频段可用中等 Attack（保留空气感）

### Release（释放时间）

| 时间 | 听感 | 适用场景 |
|------|------|---------|
| 5 ～ 50 ms | 快速恢复 | 打击乐、密集瞬态信号 |
| 50 ～ 200 ms | 中等，自然 | 通用人声、乐器 |
| 200 ～ 1000 ms | 慢速，平滑 | 母带压缩、慢速音乐 |
| 1000 ～ 5000 ms | 极慢，几乎不恢复 | 广播自动增益控制 |

**调试原则：**
- Release 太快 → 增益快速回弹 → 可闻的"呼吸"或失真（增益调制频率进入音频范围）
- Release 太慢 → 增益恢复不及时 → 小声段落也被压缩 → 声音"闷"
- 经验法则：Release 应大于被压缩频率的最低周期（100 Hz → 至少 10 ms Release）

### Knee Width（拐点宽度）

| 宽度 | 听感 | 适用场景 |
|------|------|---------|
| 0 dB（Hard） | 精确、技术感 | 精确动态控制、峰值限制 |
| 3 ～ 6 dB | 自然过渡 | 通用音乐压缩 |
| 6 ～ 12 dB | 非常平滑 | 母带、需要透明压缩的场景 |
| 12 ～ 24 dB | 几乎感觉不到压缩起始点 | 极度透明、慢速母线压缩 |

**调试原则：**
- Soft Knee 是默认推荐 — 压缩起始更自然，无明显"开关感"
- Hard Knee 适合峰值限制和精确控制，尤其在高频段控制齿音
- Knee Width 越大，压缩在门限以下就开始渐进生效

### Envelope Mode（包络检测模式）

| 模式 | 行为 | 适用场景 |
|------|------|---------|
| Peak | 瞬间响应瞬态幅度 | 峰值限制、保护性压缩 |
| RMS | 平滑跟踪感知响度 | 音乐母线压缩、追求听感自然 |
| Hybrid | 瞬态用 Peak 捕获，释放用 RMS 加权 | **默认推荐** — 兼顾响应速度和平滑度 |

**调试原则：**
- Peak 模式对瞬态反应最快，但在低频（100 Hz 以下）可能随波形抖动
- RMS 模式更接近人耳感知，但可能漏过快速瞬态
- Hybrid 是大多数场景的最佳折中：攻击快速捕获瞬态，释放平滑避免失真

### Makeup Gain（补偿增益）

| 场景 | 建议 | 说明 |
|------|------|------|
| 轻度压缩 | GR × 0.5 | 压缩量较小时可少补 |
| 中等压缩 | GR × 1.0 | 补偿被压缩削去的平均电平 |
| 重度压缩 | GR × 1.0（注意 A/B 对比）| 用于响度提升，但需注意后续 DRC 过载 |

**调试原则：**
- Makeup Gain 应在手动 A/B 对比下调整，以感知响度相等为参考
- 补偿过多会削弱压缩的动态控制效果
- Pre-EQ 增益 + DRC Makeup Gain 叠加需注意后续 Post-EQ 和 Limiter 的余量

### Post Gain（全局输出衰减）

| 场景 | 建议 | 说明 |
|------|------|------|
| 三频段合并后无削波 | 0 dB | 保持原始输出电平 |
| 三频段在高电平叠加 | –3 ～ –6 dB | 为防止合并削波留余量 |
| 激进的 Makeup Gain | –6 ～ –12 dB | 补偿过多增益后的整体回退 |

---

## 调试工作流

### 步骤 1：明确目标

- **动态控制**：减小信号的峰均比（crest factor），让声音更"饱满"？
- **保护性限制**：防止后续 EQ / Volume 过载削波？
- **音色重塑**：通过多频段独立压缩改变频谱平衡？

不同目标对应不同参数策略。保护性限制用高 Ratio、快 Attack；音色塑造用低 Ratio、慢 Attack。

### 步骤 2：分频段单独监听

- 将三个频段分别旁通（Per-band Bypass），只保留一个频段
- 对单频段调整 Threshold 和 Ratio，观察 Gain Reduction 量
- 确认该频段的 Attack/Release 时值不会导致失真或抽吸

### 步骤 3：逐个频段调参

1. 将 Threshold 从 0 dB 缓慢降低，直到该频段峰值时出现约 3–6 dB 的增益衰减
2. 调整 Ratio，听该频段的动态是否满足需求
3. 调整 Attack — 快则压制瞬态，慢则保留
4. 调整 Release — 听增益恢复期间是否有"呼吸感"或"闷感"
5. 重复以上步骤调整其余频段

### 步骤 4：全频段联调

- 打开所有频段，以典型节目素材试听
- 注意低频瞬态是否引发了中频/高频的"抽吸"（多频段 DRC 的主要优势就是避免此问题）
- 检查三频段合并后是否有削波 — 用 Post Gain 做全局回退

### 步骤 5：A/B 验证

- 全局 Bypass DRC 模块，对比压缩前后的听感
- 用粉红噪声或正弦扫频信号验证频响未因压缩而产生意外的频谱倾斜
- 确认 Makeup Gain 未导致输出超过 Limiter 的门限

---

## 常见问题

| 症状 | 可能原因 | 解决方法 |
|------|---------|---------|
| 整体声音"扁"、无动态 | Threshold 过低 / Ratio 过高 | 提高 Threshold 或降低 Ratio；确认只需在峰值时触发 3–6 dB 压缩 |
| 低音抽吸 / 整体音量随底鼓波动 | 单频段压缩（非多频段）或低频段 Ratio 过高 | 确认多频段分频正常；降低低频段 Ratio 或提高其 Threshold |
| 人声被压缩后变"远" | Attack 过快压住了瞬态 | 增加 Attack 到 10–30 ms |
| 压缩后有可闻失真 / "颗粒感" | Release 过短导致增益调制进入音频范围 | 延长 Release（低频段建议 ≥ 50 ms） |
| 齿音过重、高频刺耳 | 高频段压缩不足或 Attack 过慢 | 单独降低高频段 Threshold、加快 Attack |
| 声音"闷" / 压缩后缺乏高频 | 高频段 Release 过慢导致持续压缩 | 缩短高频段 Release（建议 50–100 ms） |
| 压缩启动和释放有明显"开关感" | 使用 Hard Knee | 改用 Soft Knee，Knee Width 3–6 dB |
| 合并后输出削波 | 三频段叠加 + Makeup Gain 超 0 dBFS | 降低 Post Gain (–3 ～ –6 dB) |
| 瞬态削波但压缩未反应 | Attack 太慢、或 Peak 模式未被选用 | 缩短 Attack 或切换到 Peak/Hybrid 模式 |
| 低频段波形仍有抖动 | 使用 Peak 模式并处理低频信号 | 切换到 RMS 或 Hybrid 模式，避免逐采样跟踪 |

---

## 信号流参考

DRC 在整个信号链中的位置：

```
Input → Pre-EQ → DRC → Post-EQ → Volume + Loudness → Output EQ → Limiter → Output
```

**设计要点：**
- Pre-EQ 位于 DRC 之前 — 切除次声波和修正性均衡后送入 DRC，避免极低频能量误触发压缩
- DRC 控制动态后送入 Post-EQ 进行音色塑造 — 音色调整不会影响压缩行为
- DRC 的 Post Gain 仅控制 DRC 内部输出，不替代 Volume 或 Limiter 的全局控制

---

## 参考文献

### 多频段 DRC 架构

- [drc.md](drc.md) — 本项目的 DRC 参考文献索引。涵盖多频段 DRC 架构、包络检测（Peak/RMS/Hybrid）、硬/软拐点压缩曲线、Attack/Release 时间常数和增益计算机设计。

### 压缩器理论

- Giannoulis, Massberg & Reiss (2012), *"Digital Dynamic Range Compressor Design — A Tutorial and Analysis"*, JAES Vol. 60, Issue 6。数字 DRC 设计的权威参考论文。前馈式压缩器架构推荐、对数域包络检测器放置、可变 Knee 宽度设计。
- [ref_stanford_drc_deo.pdf](ref_stanford_drc_deo.pdf) — Stanford CCRMA, *"Dynamic Range Compressor Design"*。DRC 基础教程：前馈/反馈拓扑、Peak/RMS 包络检测、Attack/Release 平滑滤波器、Look-ahead 瞬态处理。

### 多频段实现参考

- [ref_multiband_drc_implementation.html](ref_multiband_drc_implementation.html) — 跨项目综合分析（Cadenza Challenge、ChromiumOS adhd drc、oximedia-audio、TI TAS3251、MPEG DRC）。LR4 分频 + 每频段压缩器参数表、多频段预设（母带 4 段、广播 3 段）、立体声联动处理。

### 定点包络检测

- [ref_fxp_envelope_detector.html](ref_fxp_envelope_detector.html) — 定点包络检测器实现参考。Peak/RMS/MS/Rectify 检测器类型、平方域 RMS（跳过 sqrt）、整数 log2 检测、dB 转换近似。

### 硬件参考架构

- [ALC1320 Datasheet_V0.18.pdf](../eq/ALC1320 Datasheet_V0.18.pdf) — Realtek ALC1320 智能功放数据手册。本项目的 DRC + EQ 三阶段架构参考了 ALC1320 的 µDSP 音频引擎。

### DSP 实现

- [NatureDSP_Signal_Library_Reference_HiFi3_3z.pdf](../eq/NatureDSP_Signal_Library_Reference_HiFi3_3z.pdf) — Cadence NatureDSP Signal Library for HiFi 3/HiFi 3z, Release 5.0.0。HiFi3z 定点移植中使用的数学函数。

### 项目规格

- [spec_drc.md](../../planning/spec_drc.md) — 本项目的 DRC 模块规格文档。完整算法定义、参数范围、拓扑结构。
