# =============================================================================
# XDC Constraints for AXI DMA Engine
# Device: Xilinx Kintex-7 XC7K325T-2FFG900C
# =============================================================================

# ---- System Clock (250 MHz) ----
create_clock -add -name clk_250 -period 4.000 -waveform {0 2} [get_ports clk]

# ---- Reset ----
set_property -dict { PACKAGE_PIN AB7 IOSTANDARD LVCMOS18 PULLUP TRUE } [get_ports {rst_n}];

# ---- Interrupt Output ----
set_property -dict { PACKAGE_PIN AA7 IOSTANDARD LVCMOS18 DRIVE 12 } [get_ports {dma_interrupt}];

# ---- Timing Constraints ----

# AXI master paths (high-speed, use conservative timing)
set_input_delay -clock clk_250 -min 0.0 [get_ports {m_axi_arready m_axi_rvalid m_axi_rlast m_axi_rdata}]
set_input_delay -clock clk_250 -max 2.0 [get_ports {m_axi_arready m_axi_rvalid m_axi_rlast m_axi_rdata}]

set_output_delay -clock clk_250 -min -0.5 [get_ports {m_axi_araddr m_axi_arlen m_axi_arsize m_axi_arburst m_axi_arvalid}]
set_output_delay -clock clk_250 -max 1.5 [get_ports {m_axi_araddr m_axi_arlen m_axi_arsize m_axi_arburst m_axi_arvalid}]

# AXI slave control (lower speed)
set_input_delay -clock clk_250 -min 0.0 [get_ports {s_axi_awaddr s_axi_awvalid s_axi_wdata s_axi_wstrb s_axi_wvalid}]
set_input_delay -clock clk_250 -max 3.0 [get_ports {s_axi_awaddr s_axi_awvalid s_axi_wdata s_axi_wstrb s_axi_wvalid}]

set_output_delay -clock clk_250 -min -1.0 [get_ports {s_axi_awready s_axi_wready s_axi_bresp s_axi_bvalid}]
set_output_delay -clock clk_250 -max 2.0 [get_ports {s_axi_awready s_axi_wready s_axi_bresp s_axi_bvalid}]

# ---- False Paths ----
# Reset is asynchronous
set_false_path -from [get_ports rst_n]

# ---- Placement Constraints ----
# Locate DSP blocks near arithmetic units
set_property LOC SLICE_X45Y100 [get_cells dma_top/axi_read/addr_r]

# ---- Design Constraints ----
set_property ALLOW_COMBINATORIAL_LOOPS TRUE [current_design]

# ---- Optimization Settings ----
# Maximize performance for this high-speed design
set_property SEVERITY WARNING [get_drc_checks PLCK-12]
