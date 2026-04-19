# Timing constraints for i2c_master design
# SDC file for TimeQuest Timing Analyzer

create_clock -name {clk} -period 20.000 -waveform { 0.000 10.000 } [get_ports {clk}]

set_false_path -from [get_ports {rst_n}]
set_false_path -from [get_ports {sda_in}]

set_input_delay -clock {clk} -max 5.000 [get_ports {slave_addr[*]}]
set_input_delay -clock {clk} -max 5.000 [get_ports {data_in[*]}]
set_input_delay -clock {clk} -max 5.000 [get_ports {start}]
set_input_delay -clock {clk} -max 5.000 [get_ports {rw}]

set_output_delay -clock {clk} -max 5.500 [get_ports {data_out[*]}]
set_output_delay -clock {clk} -max 5.500 [get_ports {busy}]
set_output_delay -clock {clk} -max 5.500 [get_ports {done}]
set_output_delay -clock {clk} -max 5.500 [get_ports {ack_err}]
set_output_delay -clock {clk} -max 5.500 [get_ports {scl_out}]
set_output_delay -clock {clk} -max 5.500 [get_ports {sda_out}]

set_clock_uncertainty -setup 0.100 [get_clocks {clk}]
set_clock_uncertainty -hold 0.050 [get_clocks {clk}]
