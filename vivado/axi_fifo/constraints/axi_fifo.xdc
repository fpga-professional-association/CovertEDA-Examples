# =============================================================================
# XDC Constraints File for axi_fifo
# Device: Xilinx Zynq-7000 XC7Z020-CLG484-1
# =============================================================================

create_clock -add -name sys_clk -period 10.000 -waveform {0 5} [get_ports clk]

set_input_delay -clock sys_clk -min 0.0 [get_ports {s_axis_tdata[*] s_axis_tvalid s_axis_tlast m_axis_tready rst_n}]
set_input_delay -clock sys_clk -max 3.0 [get_ports {s_axis_tdata[*] s_axis_tvalid s_axis_tlast m_axis_tready rst_n}]
set_output_delay -clock sys_clk -min -1.0 [get_ports {m_axis_tdata[*] m_axis_tvalid m_axis_tlast s_axis_tready fill_level[*]}]
set_output_delay -clock sys_clk -max 2.0 [get_ports {m_axis_tdata[*] m_axis_tvalid m_axis_tlast s_axis_tready fill_level[*]}]

set_property -dict { PACKAGE_PIN E3 IOSTANDARD LVCMOS33 } [get_ports {clk}]
set_property -dict { PACKAGE_PIN D9 IOSTANDARD LVCMOS33 PULLUP TRUE } [get_ports {rst_n}]

set_false_path -from [get_ports rst_n]
