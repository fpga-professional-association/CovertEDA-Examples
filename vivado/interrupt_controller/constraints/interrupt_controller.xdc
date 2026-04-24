# =============================================================================
# XDC Constraints File for interrupt_controller
# Device: Xilinx Artix-7 XC7A35T-1CPG236C
# =============================================================================

create_clock -add -name sys_clk -period 10.000 -waveform {0 5} [get_ports clk]

set_input_delay -clock sys_clk -min 0.0 [get_ports {irq_in[*] irq_mask[*] irq_ack rst_n}]
set_input_delay -clock sys_clk -max 3.0 [get_ports {irq_in[*] irq_mask[*] irq_ack rst_n}]
set_output_delay -clock sys_clk -min -1.0 [get_ports {irq_id[*] irq_valid irq_pending[*]}]
set_output_delay -clock sys_clk -max 2.0 [get_ports {irq_id[*] irq_valid irq_pending[*]}]

set_property -dict { PACKAGE_PIN E3 IOSTANDARD LVCMOS33 } [get_ports {clk}]
set_property -dict { PACKAGE_PIN D9 IOSTANDARD LVCMOS33 PULLUP TRUE } [get_ports {rst_n}]

set_false_path -from [get_ports rst_n]
