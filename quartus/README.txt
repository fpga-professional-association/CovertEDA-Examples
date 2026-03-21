INTEL QUARTUS FPGA EXAMPLE PROJECTS
====================================

This directory contains 5 complete, realistic Quartus II/Pro FPGA projects
demonstrating various complexity levels and design patterns.

PROJECT STRUCTURE
=================

Each project follows the standard Quartus directory layout:
  src/          - Verilog/SystemVerilog source files
  constraints/  - QSF project files and SDC timing constraints
  reports/      - Realistic Quartus report outputs (timing, utilization, power, DRC)

PROJECTS OVERVIEW
=================

1. blinky_led (Cyclone IV E - EP4CE6E22C8)
   - Simple LED blinker with 4 independent counters
   - Demonstrates basic Quartus setup and pin assignments
   - Files: 1 Verilog module
   - Utilization: 31 LEs / 18 registers
   - Fmax: 287.36 MHz

2. nios_hello (Cyclone IV E - EP4CE115F29C7)
   - NIOS II soft processor system with GPIO controller
   - PLL-based clock generation
   - Demonstrates larger FPGA with embedded system
   - Files: 3 Verilog modules
   - Utilization: 4523 LEs / 3201 registers / 32M memory
   - Fmax: 125.4 MHz

3. ethernet_mac (Cyclone V GX - 5CGXFC7C7F23C8)
   - 10/100 Mbps Ethernet MAC controller
   - MII interface with TX/RX paths
   - CRC-32 checksum generator
   - Files: 5 Verilog modules
   - Utilization: 2891 ALMs / 1845 registers / 8 M10K blocks
   - Fmax: 156.25 MHz

4. pcie_endpoint (Arria 10 - 10AX115S2F45I1SG)
   - PCIe Gen2 x4 endpoint with TLP handler
   - BAR decoder for address mapping
   - High-speed differential signaling
   - Files: 3 SystemVerilog modules
   - Utilization: 12456 ALMs / 8901 registers / 16 DSP blocks
   - Fmax: 312.5 MHz
   - Power: 2.34 W

5. signal_proc (Arria II GX - EP2AGX125EF29C5)
   - Digital downconverter (DDC) with NCO, CIC, and FIR filters
   - DSP-heavy design for signal processing
   - Files: 4 Verilog modules
   - Utilization: 5678 ALMs / 4321 registers / 32 DSP blocks
   - Fmax: 234.5 MHz
   - Power: 1.89 W

CONSTRAINT FILES
================

Each project includes:
  *.qsf - Quartus Settings File with:
    - Device and board selection
    - Pin assignments (location_assignment)
    - I/O standards and voltage levels
    - Compilation settings
    - Design file references

  *.sdc - Synopsys Design Constraints with:
    - Clock definitions and frequencies
    - Input/output delays
    - Timing exceptions and false paths
    - Multicycle paths for DSP operations
    - Clock domain crossing constraints

REPORT FILES
============

Realistic Quartus report outputs included for each project:

  timing.sta.rpt - TimeQuest Timing Analysis
    - Fmax (maximum frequency)
    - Setup/hold slack analysis
    - Clock domain crossing analysis
    - Path timing summaries

  utilization.fit.rpt - Fitter Resource Usage
    - Logic element/ALM usage
    - Memory block utilization
    - DSP block counts
    - I/O pin usage
    - Logic depth distribution

  power.rpt - PowerPlay Power Analysis
    - Total power consumption breakdown
    - Dynamic and static power
    - Power by entity and logic type
    - Per-pin power analysis
    - Thermal estimates

  drc.rpt (blinky_led only) - Design Rule Check
    - Critical/major/minor violations
    - Design connectivity status
    - Warning and error reports

FILE ORGANIZATION
=================

All Verilog/SystemVerilog files are synthesizable RTL with:
  - Proper module interfaces
  - Realistic signal widths and naming
  - State machine implementations where appropriate
  - Parameterizable designs (where suitable)
  - Comments explaining key functionality

Constraint files use authentic Quartus syntax:
  - QSF files use Tcl assignment syntax
  - SDC files follow IEEE 1076 timing constraint format
  - Real device pin numbers for target FPGAs
  - Appropriate I/O standards for each device

USAGE
=====

These projects can be used for:
  - Learning Quartus project structure
  - Understanding constraint file formats
  - Analyzing report file structures
  - Benchmarking EDA tools
  - Reference implementations
  - Design pattern examples

DEVICE NOTES
============

All projects use real Intel/Altera device codes:
  - Cyclone IV E: Mid-range, cost-effective designs
  - Cyclone V GX: High-performance with transceivers
  - Arria II GX: High-end DSP-capable device
  - Arria 10: Advanced features, high performance

Generated: March 21, 2026
Quartus Versions: 11.0 - 17.1 (Pro)
