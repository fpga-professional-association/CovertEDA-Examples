# Timing constraints for clock_divider design
# SDC file for TimeQuest Timing Analyzer

create_clock -name {clk} -period 20.000 -waveform { 0.000 10.000 } [get_ports {clk}]

set_false_path -from [get_ports {rst_n}]

set_input_delay -clock {clk} -max 5.000 [get_ports {divisor[*]}]
set_input_delay -clock {clk} -max 5.000 [get_ports {load}]

set_output_delay -clock {clk} -max 5.500 [get_ports {clk_out}]
set_output_delay -clock {clk} -max 5.500 [get_ports {tick}]

set_clock_uncertainty -setup -to [get_clocks {clk}] 0.100
set_clock_uncertainty -hold -to [get_clocks {clk}] 0.050
