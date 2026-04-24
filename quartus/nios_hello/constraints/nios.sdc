# TimeQuest SDC file for NIOS II System
# Constraint file for design timing verification

# Create clock for 100MHz input
create_clock -name {clk_100m} -period 10.000 -waveform { 0.000 5.000 } [get_ports {clk_100m}]

# Create derived clock for PLL output (100MHz)
create_generated_clock -name {clk_sys} -source [get_ports {clk_100m}] -divide_by 1 [get_pins {pll_inst|altpll_component|clk[0]}]

# Set clock uncertainties
set_clock_uncertainty -setup -to [get_clocks {clk_sys}] 0.120
set_clock_uncertainty -hold -to [get_clocks {clk_sys}] 0.080

# Input timing constraints (asynchronous reset and switches)
set_false_path -from [get_ports {rst_n}]
set_input_delay -clock {clk_sys} -min 1.200 [get_ports {sw_input[*]}]
set_input_delay -clock {clk_sys} -max 4.500 [get_ports {sw_input[*]}]

# Output timing constraints
set_output_delay -clock {clk_sys} -min -1.500 [get_ports {led_output[*]}]
set_output_delay -clock {clk_sys} -max 5.500 [get_ports {led_output[*]}]
set_output_delay -clock {clk_sys} -min -1.500 [get_ports {seg_output[*]}]
set_output_delay -clock {clk_sys} -max 5.500 [get_ports {seg_output[*]}]

# GPIO bidirectional pin constraints
set_input_delay -clock {clk_sys} -min 1.100 [get_ports {gpio_bidir[*]}]
set_input_delay -clock {clk_sys} -max 4.400 [get_ports {gpio_bidir[*]}]
set_output_delay -clock {clk_sys} -min -1.200 [get_ports {gpio_bidir[*]}]
set_output_delay -clock {clk_sys} -max 5.200 [get_ports {gpio_bidir[*]}]

# Multicycle constraints (longer paths)
set_multicycle_path -from [get_registers {*gpio_out*}] -to [get_ports {gpio_bidir[*]}] -setup 2

# Maximum delay constraints
set_max_delay 10.000 -from [all_inputs] -to [all_outputs]
