# Timing constraints for stepper_driver design
# SDC file for TimeQuest Timing Analyzer

create_clock -name {clk} -period 20.000 -waveform { 0.000 10.000 } [get_ports {clk}]

set_false_path -from [get_ports {rst_n}]

set_input_delay -clock {clk} -max 5.000 [get_ports {enable}]
set_input_delay -clock {clk} -max 5.000 [get_ports {direction}]
set_input_delay -clock {clk} -max 5.000 [get_ports {half_step}]
set_input_delay -clock {clk} -max 5.000 [get_ports {step_pulse}]

set_output_delay -clock {clk} -max 5.500 [get_ports {phase_out[*]}]

set_clock_uncertainty -setup -to [get_clocks {clk}] 0.100
set_clock_uncertainty -hold -to [get_clocks {clk}] 0.050
