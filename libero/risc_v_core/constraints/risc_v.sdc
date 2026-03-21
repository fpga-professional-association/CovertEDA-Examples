# SDC for RV32I Core

create_clock -name sys_clk -period 10.0 -waveform {0 5} [get_ports clk]

set_input_delay -clock sys_clk -max 2.0 [get_ports rst_n]
set_input_delay -clock sys_clk -min 0.5 [get_ports rst_n]

set_output_delay -clock sys_clk -max 3.0 [get_ports {imem_addr dmem_addr pc_debug}]
set_output_delay -clock sys_clk -min 1.0 [get_ports {imem_addr dmem_addr pc_debug}]

set_false_path -from [get_ports rst_n]
set_max_fanout 256 [get_designs *]
