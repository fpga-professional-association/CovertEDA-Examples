# =============================================================================
# XDC Constraints for DDR3 Test Design
# Device: Xilinx Artix-7 XC7A200T-2FBG676C
# =============================================================================

# ---- System Clock (200 MHz) ----
create_clock -add -name sys_clk_200 -period 5.000 -waveform {0 2.5} [get_ports clk_200_in]

# ---- System Clock for logic ----
create_clock -add -name sys_clk -period 5.000 -waveform {0 2.5} [get_ports clk_sys]

# ---- Reset Input ----
set_property -dict { PACKAGE_PIN U4 IOSTANDARD LVCMOS33 PULLUP TRUE } [get_ports {rst_n}];

# ---- Test Control Interface ----
set_property -dict { PACKAGE_PIN V4 IOSTANDARD LVCMOS33 PULLUP TRUE } [get_ports {test_en}];
set_property -dict { PACKAGE_PIN T5 IOSTANDARD LVCMOS33 } [get_ports {test_mode[0]}];
set_property -dict { PACKAGE_PIN T4 IOSTANDARD LVCMOS33 } [get_ports {test_mode[1]}];
set_property -dict { PACKAGE_PIN U5 IOSTANDARD LVCMOS33 } [get_ports {test_mode[2]}];
set_property -dict { PACKAGE_PIN U3 IOSTANDARD LVCMOS33 } [get_ports {test_mode[3]}];

# ---- Status Outputs ----
set_property -dict { PACKAGE_PIN V5 IOSTANDARD LVCMOS33 DRIVE 12 } [get_ports {test_busy}];
set_property -dict { PACKAGE_PIN V3 IOSTANDARD LVCMOS33 DRIVE 12 } [get_ports {test_passed}];
set_property -dict { PACKAGE_PIN W3 IOSTANDARD LVCMOS33 DRIVE 12 } [get_ports {test_failed}];

# ---- DDR3 Address Bus (16 bits) ----
set_property -dict { PACKAGE_PIN AB9  IOSTANDARD SSTL15 } [get_ports {ddr3_addr[0]}];
set_property -dict { PACKAGE_PIN AB8  IOSTANDARD SSTL15 } [get_ports {ddr3_addr[1]}];
set_property -dict { PACKAGE_PIN AA8  IOSTANDARD SSTL15 } [get_ports {ddr3_addr[2]}];
set_property -dict { PACKAGE_PIN AA7  IOSTANDARD SSTL15 } [get_ports {ddr3_addr[3]}];
set_property -dict { PACKAGE_PIN AB7  IOSTANDARD SSTL15 } [get_ports {ddr3_addr[4]}];
set_property -dict { PACKAGE_PIN AA6  IOSTANDARD SSTL15 } [get_ports {ddr3_addr[5]}];
set_property -dict { PACKAGE_PIN AB6  IOSTANDARD SSTL15 } [get_ports {ddr3_addr[6]}];
set_property -dict { PACKAGE_PIN AA5  IOSTANDARD SSTL15 } [get_ports {ddr3_addr[7]}];
set_property -dict { PACKAGE_PIN AB5  IOSTANDARD SSTL15 } [get_ports {ddr3_addr[8]}];
set_property -dict { PACKAGE_PIN AA4  IOSTANDARD SSTL15 } [get_ports {ddr3_addr[9]}];
set_property -dict { PACKAGE_PIN AB4  IOSTANDARD SSTL15 } [get_ports {ddr3_addr[10]}];
set_property -dict { PACKAGE_PIN AA3  IOSTANDARD SSTL15 } [get_ports {ddr3_addr[11]}];
set_property -dict { PACKAGE_PIN AB3  IOSTANDARD SSTL15 } [get_ports {ddr3_addr[12]}];

# ---- DDR3 Bank Select (3 bits) ----
set_property -dict { PACKAGE_PIN AA1  IOSTANDARD SSTL15 } [get_ports {ddr3_ba[0]}];
set_property -dict { PACKAGE_PIN AB1  IOSTANDARD SSTL15 } [get_ports {ddr3_ba[1]}];
set_property -dict { PACKAGE_PIN AA2  IOSTANDARD SSTL15 } [get_ports {ddr3_ba[2]}];

# ---- DDR3 Control Signals ----
set_property -dict { PACKAGE_PIN AB2  IOSTANDARD SSTL15 } [get_ports {ddr3_ras_n}];
set_property -dict { PACKAGE_PIN Y3   IOSTANDARD SSTL15 } [get_ports {ddr3_cas_n}];
set_property -dict { PACKAGE_PIN Y2   IOSTANDARD SSTL15 } [get_ports {ddr3_we_n}];
set_property -dict { PACKAGE_PIN Y1   IOSTANDARD SSTL15 } [get_ports {ddr3_cke}];
set_property -dict { PACKAGE_PIN W1   IOSTANDARD SSTL15 } [get_ports {ddr3_cs_n}];
set_property -dict { PACKAGE_PIN W2   IOSTANDARD SSTL15 } [get_ports {ddr3_odt}];

# ---- DDR3 Clock ----
set_property -dict { PACKAGE_PIN U9  IOSTANDARD DIFF_SSTL15 } [get_ports {ddr3_ck_p}];
set_property -dict { PACKAGE_PIN V9  IOSTANDARD DIFF_SSTL15 } [get_ports {ddr3_ck_n}];

# ---- DDR3 Data Bus (64 bits) ----
set_property -dict { PACKAGE_PIN Y11 IOSTANDARD SSTL15 } [get_ports {ddr3_dq[0]}];
set_property -dict { PACKAGE_PIN Y10 IOSTANDARD SSTL15 } [get_ports {ddr3_dq[1]}];
set_property -dict { PACKAGE_PIN W11 IOSTANDARD SSTL15 } [get_ports {ddr3_dq[2]}];
set_property -dict { PACKAGE_PIN W10 IOSTANDARD SSTL15 } [get_ports {ddr3_dq[3]}];
set_property -dict { PACKAGE_PIN V11 IOSTANDARD SSTL15 } [get_ports {ddr3_dq[4]}];
set_property -dict { PACKAGE_PIN V10 IOSTANDARD SSTL15 } [get_ports {ddr3_dq[5]}];
set_property -dict { PACKAGE_PIN U11 IOSTANDARD SSTL15 } [get_ports {ddr3_dq[6]}];
set_property -dict { PACKAGE_PIN U10 IOSTANDARD SSTL15 } [get_ports {ddr3_dq[7]}];
set_property -dict { PACKAGE_PIN T12 IOSTANDARD SSTL15 } [get_ports {ddr3_dq[8]}];
set_property -dict { PACKAGE_PIN T11 IOSTANDARD SSTL15 } [get_ports {ddr3_dq[9]}];
set_property -dict { PACKAGE_PIN R12 IOSTANDARD SSTL15 } [get_ports {ddr3_dq[10]}];
set_property -dict { PACKAGE_PIN R11 IOSTANDARD SSTL15 } [get_ports {ddr3_dq[11]}];
set_property -dict { PACKAGE_PIN P12 IOSTANDARD SSTL15 } [get_ports {ddr3_dq[12]}];
set_property -dict { PACKAGE_PIN P11 IOSTANDARD SSTL15 } [get_ports {ddr3_dq[13]}];
set_property -dict { PACKAGE_PIN N12 IOSTANDARD SSTL15 } [get_ports {ddr3_dq[14]}];
set_property -dict { PACKAGE_PIN N11 IOSTANDARD SSTL15 } [get_ports {ddr3_dq[15]}];
set_property -dict { PACKAGE_PIN M12 IOSTANDARD SSTL15 } [get_ports {ddr3_dq[16]}];
set_property -dict { PACKAGE_PIN M11 IOSTANDARD SSTL15 } [get_ports {ddr3_dq[17]}];
set_property -dict { PACKAGE_PIN L12 IOSTANDARD SSTL15 } [get_ports {ddr3_dq[18]}];
set_property -dict { PACKAGE_PIN L11 IOSTANDARD SSTL15 } [get_ports {ddr3_dq[19]}];
set_property -dict { PACKAGE_PIN K12 IOSTANDARD SSTL15 } [get_ports {ddr3_dq[20]}];
set_property -dict { PACKAGE_PIN K11 IOSTANDARD SSTL15 } [get_ports {ddr3_dq[21]}];
set_property -dict { PACKAGE_PIN J12 IOSTANDARD SSTL15 } [get_ports {ddr3_dq[22]}];
set_property -dict { PACKAGE_PIN J11 IOSTANDARD SSTL15 } [get_ports {ddr3_dq[23]}];
set_property -dict { PACKAGE_PIN H12 IOSTANDARD SSTL15 } [get_ports {ddr3_dq[24]}];
set_property -dict { PACKAGE_PIN H11 IOSTANDARD SSTL15 } [get_ports {ddr3_dq[25]}];
set_property -dict { PACKAGE_PIN G12 IOSTANDARD SSTL15 } [get_ports {ddr3_dq[26]}];
set_property -dict { PACKAGE_PIN G11 IOSTANDARD SSTL15 } [get_ports {ddr3_dq[27]}];
set_property -dict { PACKAGE_PIN F12 IOSTANDARD SSTL15 } [get_ports {ddr3_dq[28]}];
set_property -dict { PACKAGE_PIN F11 IOSTANDARD SSTL15 } [get_ports {ddr3_dq[29]}];
set_property -dict { PACKAGE_PIN E12 IOSTANDARD SSTL15 } [get_ports {ddr3_dq[30]}];
set_property -dict { PACKAGE_PIN E11 IOSTANDARD SSTL15 } [get_ports {ddr3_dq[31]}];

# ---- DDR3 Data Strobe ----
set_property -dict { PACKAGE_PIN W12 IOSTANDARD DIFF_SSTL15 } [get_ports {ddr3_dqs_p[0]}];
set_property -dict { PACKAGE_PIN W13 IOSTANDARD DIFF_SSTL15 } [get_ports {ddr3_dqs_n[0]}];
set_property -dict { PACKAGE_PIN U12 IOSTANDARD DIFF_SSTL15 } [get_ports {ddr3_dqs_p[1]}];
set_property -dict { PACKAGE_PIN U13 IOSTANDARD DIFF_SSTL15 } [get_ports {ddr3_dqs_n[1]}];
set_property -dict { PACKAGE_PIN P13 IOSTANDARD DIFF_SSTL15 } [get_ports {ddr3_dqs_p[2]}];
set_property -dict { PACKAGE_PIN P14 IOSTANDARD DIFF_SSTL15 } [get_ports {ddr3_dqs_n[2]}];
set_property -dict { PACKAGE_PIN L13 IOSTANDARD DIFF_SSTL15 } [get_ports {ddr3_dqs_p[3]}];
set_property -dict { PACKAGE_PIN L14 IOSTANDARD DIFF_SSTL15 } [get_ports {ddr3_dqs_n[3]}];
set_property -dict { PACKAGE_PIN J14 IOSTANDARD DIFF_SSTL15 } [get_ports {ddr3_dqs_p[4]}];
set_property -dict { PACKAGE_PIN J15 IOSTANDARD DIFF_SSTL15 } [get_ports {ddr3_dqs_n[4]}];
set_property -dict { PACKAGE_PIN G14 IOSTANDARD DIFF_SSTL15 } [get_ports {ddr3_dqs_p[5]}];
set_property -dict { PACKAGE_PIN G15 IOSTANDARD DIFF_SSTL15 } [get_ports {ddr3_dqs_n[5]}];
set_property -dict { PACKAGE_PIN D14 IOSTANDARD DIFF_SSTL15 } [get_ports {ddr3_dqs_p[6]}];
set_property -dict { PACKAGE_PIN D15 IOSTANDARD DIFF_SSTL15 } [get_ports {ddr3_dqs_n[6]}];
set_property -dict { PACKAGE_PIN B14 IOSTANDARD DIFF_SSTL15 } [get_ports {ddr3_dqs_p[7]}];
set_property -dict { PACKAGE_PIN B15 IOSTANDARD DIFF_SSTL15 } [get_ports {ddr3_dqs_n[7]}];

# ---- Timing Constraints ----
set_input_delay -clock sys_clk_200 -min 0.0 [get_ports {test_en test_mode}]
set_input_delay -clock sys_clk_200 -max 3.0 [get_ports {test_en test_mode}]

set_output_delay -clock sys_clk_200 -min -1.0 [get_ports {test_busy test_passed test_failed error_count status}]
set_output_delay -clock sys_clk_200 -max 2.0 [get_ports {test_busy test_passed test_failed error_count status}]

# ---- DDR3 Timing Constraints (High-Speed) ----
set_false_path -from [get_ports test_en]
set_false_path -to [get_ports test_busy]
set_false_path -to [get_ports test_passed]
set_false_path -to [get_ports test_failed]

# ========== Virtual-port assignments ==========
# Suppresses IOB inference — matches VIRTUAL_PIN semantics in Quartus.
set_property IO_BUFFER_TYPE NONE [get_ports {clk_sys}]
set_property IO_BUFFER_TYPE NONE [get_ports {clk_200_in}]
set_property IO_BUFFER_TYPE NONE [get_ports {rst_n}]
set_property IO_BUFFER_TYPE NONE [get_ports {ddr3_addr}]
set_property IO_BUFFER_TYPE NONE [get_ports {ddr3_ba}]
set_property IO_BUFFER_TYPE NONE [get_ports {ddr3_ras_n}]
set_property IO_BUFFER_TYPE NONE [get_ports {ddr3_cas_n}]
set_property IO_BUFFER_TYPE NONE [get_ports {ddr3_we_n}]
set_property IO_BUFFER_TYPE NONE [get_ports {ddr3_dq}]
set_property IO_BUFFER_TYPE NONE [get_ports {ddr3_dqs_n}]
set_property IO_BUFFER_TYPE NONE [get_ports {ddr3_dqs_p}]
set_property IO_BUFFER_TYPE NONE [get_ports {ddr3_ck_p}]
set_property IO_BUFFER_TYPE NONE [get_ports {ddr3_ck_n}]
set_property IO_BUFFER_TYPE NONE [get_ports {ddr3_cke}]
set_property IO_BUFFER_TYPE NONE [get_ports {ddr3_cs_n}]
set_property IO_BUFFER_TYPE NONE [get_ports {ddr3_odt}]
set_property IO_BUFFER_TYPE NONE [get_ports {test_en}]
set_property IO_BUFFER_TYPE NONE [get_ports {test_mode}]
set_property IO_BUFFER_TYPE NONE [get_ports {test_busy}]
set_property IO_BUFFER_TYPE NONE [get_ports {test_passed}]
set_property IO_BUFFER_TYPE NONE [get_ports {test_failed}]
set_property IO_BUFFER_TYPE NONE [get_ports {error_count}]
set_property IO_BUFFER_TYPE NONE [get_ports {status}]
