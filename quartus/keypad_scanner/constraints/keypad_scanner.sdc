# Timing constraints for keypad_scanner design
# SDC file for TimeQuest Timing Analyzer

create_clock -name {clk} -period 20.000 -waveform { 0.000 10.000 } [get_ports {clk}]

set_false_path -from [get_ports {rst_n}]
set_false_path -from [get_ports {col_in[*]}]

set_output_delay -clock {clk} -max 5.500 [get_ports {row_out[*]}]
set_output_delay -clock {clk} -max 5.500 [get_ports {key_code[*]}]
set_output_delay -clock {clk} -max 5.500 [get_ports {key_valid}]
set_output_delay -clock {clk} -max 5.500 [get_ports {key_pressed}]

set_clock_uncertainty -setup -to [get_clocks {clk}] 0.100
set_clock_uncertainty -hold -to [get_clocks {clk}] 0.050
