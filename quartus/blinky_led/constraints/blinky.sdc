# Timing constraints for blinky_led design
# SDC file for TimeQuest Timing Analyzer

# Create clock for 50MHz oscillator input
create_clock -name {clk_50m} -period 20.000 -waveform { 0.000 10.000 } [get_ports {clk_50m}]

# Input delay constraints (asynchronous reset, no timing requirement)
set_false_path -from [get_ports {rst_n}]

# Output delay constraints
set_output_delay -clock {clk_50m} -min -1.500 [get_ports {led[*]}]
set_output_delay -clock {clk_50m} -max 5.500 [get_ports {led[*]}]

# Set minimum/maximum delay across clock domains
set_clock_uncertainty -setup 0.100 [get_clocks {clk_50m}]
set_clock_uncertainty -hold 0.050 [get_clocks {clk_50m}]

# Maximum frequency constraint
set_max_delay 20.000 -from [all_inputs] -to [all_outputs]
