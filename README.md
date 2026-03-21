# CovertEDA Examples

Real-world FPGA design examples for all 7 vendor backends supported by [CovertEDA](https://github.com/fpga-professional-association/CovertEDA). Each example includes synthesizable RTL, vendor-specific constraint files, and authentic tool report outputs.

These examples serve as both reference designs and test fixtures for CovertEDA's report parsers and backend modules.

## Structure

```
radiant/          # Lattice Radiant (LIFCL, LFD2NX)
  blinky_led/       LED blinker - LIFCL-40
  uart_controller/  UART TX/RX 115200 baud
  spi_flash/        QSPI flash controller
  i2c_bridge/       I2C-to-Wishbone bridge
  dsp_fir_filter/   8-tap FIR filter with DSP blocks

vivado/           # AMD Vivado (Artix-7, Zynq, Kintex-7)
  blinky_led/       LED blinker - XC7A35T
  uart_echo/        UART echo with FIFO
  pwm_rgb/          AXI-Lite RGB PWM - XC7Z020
  ddr3_test/        DDR3 memory tester - XC7A200T
  axi_dma_engine/   AXI DMA scatter-gather - XC7K325T

quartus/          # Intel Quartus (Cyclone IV/V, Arria II/10)
  blinky_led/       LED blinker - EP4CE6
  nios_hello/       Nios II system - EP4CE115
  ethernet_mac/     10/100 Ethernet MAC - Cyclone V GX
  pcie_endpoint/    PCIe Gen2 x4 - Arria 10
  signal_proc/      Digital downconverter - Arria II GX

diamond/          # Lattice Diamond (ECP5)
  blinky_led/       LED blinker - LFE5U-25F
  uart_bridge/      USB-UART bridge - LFE5U-45F
  serdes_loopback/  SERDES loopback - LFE5UM5G-85F
  wishbone_soc/     Wishbone SoC - LFE5U-85F
  video_scaler/     720p-to-1080p scaler - LFE5U-85F

libero/           # Microchip Libero SoC (PolarFire)
  blinky_led/       LED blinker - MPF300T
  risc_v_core/      RV32I processor - MPFS250T
  adc_interface/    ADC SPI controller - MPF100T
  can_controller/   CAN 2.0B bus - MPF300T
  motor_pwm/        3-phase motor PWM - MPF200T

ace/              # Achronix ACE (Speedster7t)
  blinky_led/       LED blinker - AC7t1500
  noc_endpoint/     NoC endpoint - AC7t1500
  gddr6_test/       GDDR6 memory test - AC7t1500
  ethernet_400g/    400G Ethernet MAC - AC7t1500
  ml_accelerator/   ML inference engine - AC7t1500

oss/              # OSS CAD Suite (yosys + nextpnr)
  blinky_led/       LED blinker - iCE40UP5K
  uart_tx/          UART transmitter - iCE40UP5K
  spi_slave/        SPI slave - ECP5 LFE5U-25F
  pwm_audio/        PWM audio DAC - iCE40UP5K
  ws2812_driver/    WS2812B LED driver - iCE40HX8K
```

## Per-Project Layout

Each project follows a consistent directory structure:

```
<project>/
  src/              Synthesizable Verilog/SystemVerilog RTL
  constraints/      Vendor-specific constraint files (.xdc, .sdc, .pdc, .lpf, .qsf, .pcf)
  reports/          Authentic vendor tool report outputs
```

## Usage with CovertEDA

This repository is included as a git submodule in the main CovertEDA repository under `examples/`. CovertEDA's test suite uses the report files as real-world fixtures for parser validation.

## License

Open Source. These example designs are provided for educational and testing purposes.
