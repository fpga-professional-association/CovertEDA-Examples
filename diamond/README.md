# Lattice Diamond FPGA Example Projects

Five complete, production-ready Lattice Diamond FPGA projects demonstrating various design patterns and complexity levels.

## Project Overview

### 1. blinky_led - Simple LED Blinker
**Target Device:** LFE5U-25F-6BG256C (ECP5)  
**Complexity:** Beginner  
**Key Features:**
- 25 MHz system clock
- 4-LED blinker with rotating pattern
- Simple prescaler-based timing
- Power: 22.3 mW, Fmax: 287.5 MHz

**Files:**
- `blinky_led/src/blinky_top.v` - LED blinker module with prescaler
- `blinky_led/constraints/blinky.lpf` - Pin assignments (LVCMOS33)
- `blinky_led/reports/timing.twr` - Timing closure: 36.5ns slack
- `blinky_led/reports/utilization.mrp` - 34 LUTs, 24 FFs, 0.7% device
- `blinky_led/reports/power.rpt` - Static 4.2mW, Dynamic 18.1mW
- `blinky_led/reports/drc.rpt` - Design rule check (PASSED)
- `blinky_led/reports/pad.rpt` - Pin verification

---

### 2. uart_bridge - USB-UART Bridge
**Target Device:** LFE5U-45F-8BG381C  
**Complexity:** Intermediate  
**Key Features:**
- 48 MHz system clock
- UART core with configurable baud rates (9600-115200)
- Dual 512-byte FIFOs (4 EBR blocks)
- USB interface simulation
- Activity-based LED indicators
- Power: 35.6 mW, Fmax: 156.0 MHz

**Files:**
- `uart_bridge/src/uart_top.v` - USB-UART bridge with FIFOs
- `uart_bridge/src/uart_core.v` - 8N1 UART transmitter/receiver
- `uart_bridge/src/fifo_sync.v` - Synchronous FIFO with configurable depth
- `uart_bridge/constraints/uart.lpf` - Pin assignments (31 I/O)
- `uart_bridge/reports/` - Timing (7.5ns slack), Util (412 LUTs/298 FFs/4 EBR)

---

### 3. serdes_loopback - High-Speed Serial Loopback
**Target Device:** LFE5UM5G-85F-8BG756C  
**Complexity:** Advanced  
**Key Features:**
- 312.5 MHz reference clock (2.5 Gbps SERDES)
- PLL for clock multiplication
- PRBS7 generator and checker
- LVDS differential pairs
- 8 status LEDs for debugging
- Power: 156.7 mW, Fmax: 312.5 MHz

**Files:**
- `serdes_loopback/src/serdes_top.v` - High-speed loopback controller
- `serdes_loopback/src/serdes_wrapper.v` - SERDES serializer/deserializer
- `serdes_loopback/src/prbs_gen.v` - PRBS7 test pattern generator
- `serdes_loopback/src/prbs_check.v` - PRBS pattern checker with lock detection
- `serdes_loopback/constraints/serdes.lpf` - LVDS differential pairs
- `serdes_loopback/reports/` - Timing (1.044ns slack - marginal), Util (1245 LUTs/890 FFs/2 SERDES)

---

### 4. wishbone_soc - Simple Wishbone Bus SoC
**Target Device:** LFE5U-85F-6BG554I  
**Complexity:** Intermediate-Advanced  
**Key Features:**
- 50 MHz Wishbone bus master (CPU simulator)
- 4 KB SRAM (1 KB per EBR block)
- GPIO slave with interrupt support
- 32-bit timer with prescaler
- Bus interconnect with address decoding
- Power: 78.9 mW, Fmax: 125.0 MHz

**Files:**
- `wishbone_soc/src/soc_top.v` - SoC top-level with bus master
- `wishbone_soc/src/wb_intercon.v` - Wishbone interconnect/arbiter
- `wishbone_soc/src/wb_sram.v` - 4KB dual-port SRAM slave
- `wishbone_soc/src/wb_gpio.v` - GPIO slave with input change detection
- `wishbone_soc/src/wb_timer.v` - 32-bit timer with interrupt
- `wishbone_soc/constraints/soc.lpf` - 16 I/O pins
- `wishbone_soc/reports/` - Timing (12ns slack), Util (3456 LUTs/2134 FFs/16 EBR)

---

### 5. video_scaler - 720p→1080p Vertical Scaler
**Target Device:** LFE5U-85F-8BG756C  
**Complexity:** Advanced  
**Key Features:**
- 148.5 MHz pixel clock (1080p@60Hz)
- 1280x720 input → 1920x1080 output scaling
- Line buffers (2 EBR blocks for 1280px/line)
- Linear interpolation with DSP blocks (8 multipliers)
- LVDS differential I/O for video signals
- Power: 234.5 mW, Fmax: 165.3 MHz

**Files:**
- `video_scaler/src/scaler_top.v` - Video scaler pipeline controller
- `video_scaler/src/line_buffer.v` - Dual-port line buffer (1280x24-bit)
- `video_scaler/src/interpolator.v` - Vertical interpolation engine
- `video_scaler/src/pixel_counter.v` - Pixel timing generator (1920x1080)
- `video_scaler/constraints/scaler.lpf` - LVDS pairs for 24-bit pixel bus
- `video_scaler/reports/` - Timing (0.687ns slack - tight), Util (5678 LUTs/4123 FFs/32 EBR/8 DSP)

---

## Report Format Details

All projects include realistic Lattice Diamond reports:

### timing.twr (Timing Report)
- Fmax calculation with margin analysis
- Setup/hold slack per path group
- Critical path identification
- Constraint verification (FREQUENCY, custom constraints)
- Pin-level timing analysis

### utilization.mrp (Map Report)
- Resource utilization (LUTs, FFs, EBR, DSP, PLL)
- Logic density and routing congestion
- Memory block allocation
- I/O bank configuration
- Compile statistics

### power.rpt (Power Calculator Report)
- Static vs dynamic power breakdown
- Per-rail power analysis (VCORE, VCCIO, VCCAUX, etc.)
- Functional block power attribution
- Thermal analysis with junction temperature
- Switching activity estimation

### drc.rpt (Design Rule Check) - blinky_led only
- I/O configuration verification
- Voltage compatibility checks
- Timing constraint validation
- Net connection verification
- Pin assignment conflicts

### pad.rpt (Pad Report) - blinky_led only
- Pin-to-location mapping
- Bank voltage configuration
- Drive strength specifications
- Input/output impedance
- PCB-level recommendations

---

## Device Specifications Summary

| Project | Device | Clock | Power | Fmax | LUT | FF | EBR | DSP |
|---------|--------|-------|-------|------|-----|----|----|-----|
| blinky_led | LFE5U-25F | 25 MHz | 22.3mW | 287.5 MHz | 34 | 24 | 0 | 0 |
| uart_bridge | LFE5U-45F | 48 MHz | 35.6mW | 156.0 MHz | 412 | 298 | 4 | 0 |
| serdes_loopback | LFE5UM5G-85F | 312.5MHz | 156.7mW | 312.5 MHz | 1245 | 890 | 0 | 2 SERDES |
| wishbone_soc | LFE5U-85F | 50 MHz | 78.9mW | 125.0 MHz | 3456 | 2134 | 16 | 0 |
| video_scaler | LFE5U-85F | 148.5MHz | 234.5mW | 165.3 MHz | 5678 | 4123 | 32 | 8 |

---

## Design Patterns Demonstrated

1. **Simple Logic** - blinky_led: Prescaler, shift register, counters
2. **Serial Communication** - uart_bridge: UART, FIFO, handshaking
3. **High-Speed I/O** - serdes_loopback: SERDES, LVDS, PRBS testing
4. **Bus Architecture** - wishbone_soc: Interconnect, address decoding, slaves
5. **Video Processing** - video_scaler: Buffering, interpolation, DSP blocks

---

## Report Realism Features

All reports include:
- Realistic timing slack distributions
- Device-specific resource counts
- Authentic power estimates per rail
- Temperature analysis with thermal resistance
- Practical decoupling recommendations
- PCB-level considerations
- Manufacturing notes

Reports are formatted exactly like real Lattice Diamond output and can serve as templates for actual projects.

---

Created: 2026-03-21  
Total Files: 38 (Verilog + LPF + Reports)
