# Synopsys Design Constraints (SDC) for Blinky LED
# SmartTime timing constraints for PolarFire MPF300T

# System clock
create_clock -name sys_clk -period 20.0 -waveform {0 10} [get_ports clk]

# Clock groups
set_clock_groups -asynchronous -group {sys_clk}

# Input delays (from input pads)
set_input_delay -clock sys_clk -max 2.0 [get_ports rst_n]
set_input_delay -clock sys_clk -min 0.5 [get_ports rst_n]

# Output delays (to output pads)
set_output_delay -clock sys_clk -max 3.0 [get_ports led]
set_output_delay -clock sys_clk -min 1.0 [get_ports led]

# Timing exceptions
set_false_path -from [get_ports rst_n]

# False path for asynchronous reset
set_false_path -through [get_pins -filter "NAME =~ *rst*"]

# Drive constraints
set_driving_cell -lib_cell CLKINT -pin CLK [get_ports clk]

# Fanout constraints
set_max_fanout 256 [get_designs *]
