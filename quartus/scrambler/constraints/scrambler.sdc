# Timing constraints for scrambler design
# SDC file for TimeQuest Timing Analyzer

create_clock -name {clk} -period 20.000 -waveform { 0.000 10.000 } [get_ports {clk}]

set_false_path -from [get_ports {rst_n}]

set_input_delay -clock {clk} -max 5.000 [get_ports {din[*]}]
set_input_delay -clock {clk} -max 5.000 [get_ports {key[*]}]
set_input_delay -clock {clk} -max 5.000 [get_ports {valid_in}]
set_input_delay -clock {clk} -max 5.000 [get_ports {descramble}]

set_output_delay -clock {clk} -max 5.500 [get_ports {dout[*]}]
set_output_delay -clock {clk} -max 5.500 [get_ports {valid_out}]

set_clock_uncertainty -setup -to [get_clocks {clk}] 0.100
set_clock_uncertainty -hold -to [get_clocks {clk}] 0.050
