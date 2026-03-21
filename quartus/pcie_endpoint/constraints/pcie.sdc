# TimeQuest SDC for PCIe Gen2 x4 Endpoint
# Timing constraints for Arria 10 PCIe design

# Create clock for 250MHz reference input
create_clock -name {clk_250m} -period 4.000 -waveform { 0.000 2.000 } [get_ports {clk_250m}]

# PCIe core clock (generated internally from reference)
create_generated_clock -name {pcie_clk} -source [get_ports {clk_250m}] -divide_by 1 [get_pins {pcie_core_inst|clk250_out}]

# Clock uncertainties
set_clock_uncertainty -setup 0.200 [get_clocks {clk_250m}]
set_clock_uncertainty -hold 0.150 [get_clocks {clk_250m}]

set_clock_uncertainty -setup 0.200 [get_clocks {pcie_clk}]
set_clock_uncertainty -hold 0.150 [get_clocks {pcie_clk}]

# PCIe differential signaling constraints
set_output_delay -clock {pcie_clk} -min -2.0 [get_ports {pcie_tx[*]}]
set_output_delay -clock {pcie_clk} -max 2.0 [get_ports {pcie_tx[*]}]
set_input_delay -clock {pcie_clk} -min -1.0 [get_ports {pcie_rx[*]}]
set_input_delay -clock {pcie_clk} -max 1.0 [get_ports {pcie_rx[*]}]

# Application interface timing
set_input_delay -clock {pcie_clk} -min 1.5 [get_ports {app_data_in[*]}]
set_input_delay -clock {pcie_clk} -max 5.5 [get_ports {app_data_in[*]}]
set_input_delay -clock {pcie_clk} -min 1.5 [get_ports {app_byte_en[*]}]
set_input_delay -clock {pcie_clk} -max 5.5 [get_ports {app_byte_en[*]}]
set_input_delay -clock {pcie_clk} -min 1.5 [get_ports {app_valid}]
set_input_delay -clock {pcie_clk} -max 5.5 [get_ports {app_valid}]

set_output_delay -clock {pcie_clk} -min -2.0 [get_ports {app_data_out[*]}]
set_output_delay -clock {pcie_clk} -max 6.0 [get_ports {app_data_out[*]}]
set_output_delay -clock {pcie_clk} -min -2.0 [get_ports {app_ready}]
set_output_delay -clock {pcie_clk} -max 6.0 [get_ports {app_ready}]

# Control signal timing
set_input_delay -clock {pcie_clk} -min 1.5 [get_ports {device_id[*]}]
set_input_delay -clock {pcie_clk} -max 5.5 [get_ports {device_id[*]}]
set_input_delay -clock {pcie_clk} -min 1.5 [get_ports {bar0_config[*]}]
set_input_delay -clock {pcie_clk} -max 5.5 [get_ports {bar0_config[*]}]

set_output_delay -clock {pcie_clk} -min -2.0 [get_ports {pcie_link_up}]
set_output_delay -clock {pcie_clk} -max 6.0 [get_ports {pcie_link_up}]
set_output_delay -clock {pcie_clk} -min -2.0 [get_ports {link_speed[*]}]
set_output_delay -clock {pcie_clk} -max 6.0 [get_ports {link_speed[*]}]

# Asynchronous reset
set_false_path -from [get_ports {rst_n}]

# Maximum delay constraints
set_max_delay 4.000 -from [all_inputs] -to [all_outputs]

# PCIe Gen2 x4 requires high-speed differential pairs
# Constraint for skew matching
set_max_skew -from [get_ports {pcie_tx[*]}] 0.100
set_max_skew -from [get_ports {pcie_rx[*]}] 0.100
