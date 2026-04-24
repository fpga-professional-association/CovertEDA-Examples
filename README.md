# CovertEDA Examples

Real-world FPGA design examples for all 7 vendor backends supported by
[CovertEDA](https://github.com/fpga-professional-association/CovertEDA).
Each example ships synthesizable RTL, vendor-specific constraints, and
authentic tool report output.

These examples serve as both reference designs and test fixtures for
CovertEDA's report parsers and backend modules.

## At a Glance

| Category        | Count |
|-----------------|-------|
| FPGA projects   | 135   |
| Vendor backends | 7     |
| Cocotb tests    | 1,037 |
| Vendor report fixtures (real tool output) | Vivado: 20/20 • Quartus: 19/19 • OSS: 17/19 PnR + 19/19 synth |

## Structure

```
radiant/          # Lattice Radiant (LIFCL, LFD2NX)
  blinky_led/         LED blinker - LIFCL-40
  uart_controller/    UART TX/RX 115200 baud
  spi_flash/          QSPI flash controller
  i2c_bridge/         I2C-to-Wishbone bridge
  dsp_fir_filter/     8-tap FIR filter with DSP blocks
  ... + 15 more

vivado/           # AMD Vivado (Artix-7, Kintex-7, Zynq)
  blinky_led/         LED blinker - XC7A35T
  uart_echo/          UART echo with FIFO
  pwm_rgb/            AXI-Lite RGB PWM - XC7Z020
  ddr3_test/          DDR3 memory tester - XC7A200T
  axi_dma_engine/     AXI DMA scatter-gather - XC7K325T
  ... + 15 more (20 projects total)

quartus/          # Intel / Altera Quartus Prime Pro 25.3 (Cyclone 10 GX)
  blinky_led/         LED blinker
  nios_hello/         Nios II system (stub PLL)
  ethernet_mac/       10/100 Ethernet MAC
  pcie_endpoint/      PCIe endpoint (stub)
  signal_proc/        Digital downconverter
  ... + 13 more (18 projects total, Cyclone 10 GX target)

diamond/          # Lattice Diamond (ECP5)
  blinky_led/  uart_bridge/  serdes_loopback/  wishbone_soc/  video_scaler/

libero/           # Microchip Libero SoC (PolarFire)
  blinky_led/  risc_v_core/  adc_interface/  can_controller/  motor_pwm/

ace/              # Achronix ACE (Speedster7t)
  blinky_led/  noc_endpoint/  gddr6_test/  ethernet_400g/  ml_accelerator/

oss/              # OSS CAD Suite (yosys + nextpnr)
  blinky_led/         iCE40UP5K SG48
  uart_tx/            iCE40UP5K
  spi_slave/          ECP5 LFE5U-25F
  pwm_audio/          iCE40UP5K (with PCM sample ROM)
  ws2812_driver/      iCE40HX8K (with gamma LUT)
  ... + 14 more (19 projects total)

tb/               # Cocotb 2.0.1 testbenches (1,037 test cases)
  common/             Shared clock/reset/bus helpers
  stubs/              Vendor primitive stubs
  <vendor>/<project>/ Per-project Makefile + test_*.py
```

## Per-Project Layout

Each project follows the same directory structure:

```
<project>/
  .coverteda        JSON project config (device, top module, source patterns)
  src/              Synthesizable Verilog / SystemVerilog RTL
  constraints/      Vendor-specific constraint files (.xdc/.sdc/.pdc/.lpf/.qsf/.pcf)
  reports/          Tool report output (real, per-vendor - see next section)
```

## Vendor Report Fixtures

Every project's `reports/` directory ships **real tool output** — not
synthesized placeholders. These files are what CovertEDA's regex-based
parsers are tested against.

| Vendor  | Tool          | Flow stage             | Files in reports/                                                                       |
|---------|---------------|------------------------|-----------------------------------------------------------------------------------------|
| Vivado  | Vivado 2025.2 | Synthesis              | `timing_summary.rpt`, `utilization.rpt`                                                 |
| Quartus | Prime Pro 25.3| Synthesis              | `synthesis.rpt`, `synthesis.summary`, `synthesis.analysis_elab.rpt`, `flow.rpt`, `build.log` |
| OSS     | yosys + nextpnr | Synth + PnR + timing | `yosys.log`, `yosys_stat.rpt`, `nextpnr.log`, `timing.json`, `build_summary.txt`        |

The Vivado and Quartus flows stop after synthesis because the example
constraint files intentionally do not pin-assign for a specific board —
they're device-agnostic so each project is useful as a parser fixture
without requiring a specific evaluation board. The OSS flow runs end-to-end
(yosys synthesis + nextpnr placement, routing, and timing) because
iCE40/ECP5 nextpnr accepts auto-placement. Two OSS projects
(`spi_flash_reader`, `temp_sensor_spi`) synthesize cleanly in yosys but
exceed the iCE40UP5K-SG48 I/O budget at nextpnr time — their `yosys.log`
and `yosys_stat.rpt` are still real output.

## Quick Start

### Run cocotb simulation tests

All 1,037 test cases, in parallel:

```bash
pip install -r requirements-sim.txt    # cocotb 2.0.1 + deps
python run_all_tests.py --parallel 4
```

Run a single project's tests:

```bash
cd tb/vivado/uart_echo
make        # SIM=icarus by default
```

### Regenerate vendor reports

Requires the corresponding toolchain installed locally. From the repo root:

```bash
# Rebuild all Quartus projects (Quartus Prime Pro 25.3)
python scripts/batch_build.py quartus

# Rebuild all OSS projects (needs C:\oss-cad-suite\oss-cad-suite)
python scripts/batch_build.py oss

# Rebuild a single project
python scripts/run_quartus_project.py blinky_led
python scripts/run_oss_project.py     blinky_led

# Distribute Vivado reports from vivado_reports/ into per-project reports/
python scripts/distribute_vivado_reports.py
```

Each per-vendor batch writes a summary at `<vendor>_reports_summary.txt`
in the repo root.

## Usage with CovertEDA

This repository is included as a git submodule in the main CovertEDA
repository under `examples/`. CovertEDA's Rust backend test suite uses
the report files as real-world fixtures for parser validation — every
regex in `src-tauri/src/parser/` is tested against output this repo
produced.

```bash
# From the CovertEDA root:
git clone --recursive https://github.com/fpga-professional-association/CovertEDA.git
cd CovertEDA
cargo test --manifest-path src-tauri/Cargo.toml
```

## Releases

- **v0.1.0** — first tagged release. 135 projects, 7 vendor backends,
  1,037 cocotb tests, authentic Vivado/Quartus/OSS reports.

## License

Open Source. These example designs are provided for educational and
testing purposes.
