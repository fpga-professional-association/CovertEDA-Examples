# Timing constraints for rotary_encoder design
# SDC file for TimeQuest Timing Analyzer

create_clock -name {clk} -period 20.000 -waveform { 0.000 10.000 } [get_ports {clk}]

set_false_path -from [get_ports {rst_n}]
set_false_path -from [get_ports {enc_a}]
set_false_path -from [get_ports {enc_b}]
set_false_path -from [get_ports {clear}]

set_output_delay -clock {clk} -max 5.500 [get_ports {position[*]}]
set_output_delay -clock {clk} -max 5.500 [get_ports {dir}]
set_output_delay -clock {clk} -max 5.500 [get_ports {step_event}]

set_clock_uncertainty -setup -to [get_clocks {clk}] 0.100
set_clock_uncertainty -hold -to [get_clocks {clk}] 0.050
