# TimeQuest SDC for Ethernet MAC
# 10/100 Mbps Ethernet with MII Interface

# Create clock for 125MHz input
create_clock -name {clk_125m} -period 8.000 -waveform { 0.000 4.000 } [get_ports {clk_125m}]

# Create MII TX clock (25MHz from 125MHz)
create_generated_clock -name {mii_tx_clk} -source [get_ports {clk_125m}] -divide_by 5 [get_ports {mii_tx_clk}]

# Create MII RX clock (25MHz from 125MHz)
create_generated_clock -name {mii_rx_clk} -source [get_ports {clk_125m}] -divide_by 5 [get_ports {mii_rx_clk}]

# Clock uncertainties
set_clock_uncertainty -setup 0.150 [get_clocks {clk_125m}]
set_clock_uncertainty -hold 0.100 [get_clocks {clk_125m}]

set_clock_uncertainty -setup 0.200 [get_clocks {mii_tx_clk}]
set_clock_uncertainty -hold 0.150 [get_clocks {mii_tx_clk}]

set_clock_uncertainty -setup 0.200 [get_clocks {mii_rx_clk}]
set_clock_uncertainty -hold 0.150 [get_clocks {mii_rx_clk}]

# MII Interface Timing Constraints (IEEE 802.3)
# TX timing: data valid on rising edge, hold time 0ns
set_output_delay -clock {mii_tx_clk} -min -2.0 [get_ports {mii_txd[*]}]
set_output_delay -clock {mii_tx_clk} -max 5.5 [get_ports {mii_txd[*]}]
set_output_delay -clock {mii_tx_clk} -min -2.0 [get_ports {mii_tx_en}]
set_output_delay -clock {mii_tx_clk} -max 5.5 [get_ports {mii_tx_en}]

# RX timing: data sampled on falling edge
set_input_delay -clock {mii_rx_clk} -min 1.5 [get_ports {mii_rxd[*]}]
set_input_delay -clock {mii_rx_clk} -max 4.5 [get_ports {mii_rxd[*]}]
set_input_delay -clock {mii_rx_clk} -min 1.5 [get_ports {mii_rx_dv}]
set_input_delay -clock {mii_rx_clk} -max 4.5 [get_ports {mii_rx_dv}]

# Control and data interface timing
set_input_delay -clock {clk_125m} -min 1.2 [get_ports {mac_addr[*]}]
set_input_delay -clock {clk_125m} -max 4.8 [get_ports {mac_addr[*]}]
set_input_delay -clock {clk_125m} -min 1.2 [get_ports {eth_type[*]}]
set_input_delay -clock {clk_125m} -max 4.8 [get_ports {eth_type[*]}]

set_input_delay -clock {clk_125m} -min 1.2 [get_ports {tx_data[*]}]
set_input_delay -clock {clk_125m} -max 4.8 [get_ports {tx_data[*]}]
set_input_delay -clock {clk_125m} -min 1.2 [get_ports {tx_valid}]
set_input_delay -clock {clk_125m} -max 4.8 [get_ports {tx_valid}]

set_output_delay -clock {clk_125m} -min -1.5 [get_ports {tx_ready}]
set_output_delay -clock {clk_125m} -max 5.5 [get_ports {tx_ready}]

set_output_delay -clock {clk_125m} -min -1.5 [get_ports {rx_data[*]}]
set_output_delay -clock {clk_125m} -max 5.5 [get_ports {rx_data[*]}]
set_output_delay -clock {clk_125m} -min -1.5 [get_ports {rx_valid}]
set_output_delay -clock {clk_125m} -max 5.5 [get_ports {rx_valid}]
set_output_delay -clock {clk_125m} -min -1.5 [get_ports {rx_last}]
set_output_delay -clock {clk_125m} -max 5.5 [get_ports {rx_last}]

# Clock domain crossings
set_false_path -from [get_clocks {mii_tx_clk}] -to [get_clocks {clk_125m}]
set_false_path -from [get_clocks {mii_rx_clk}] -to [get_clocks {clk_125m}]

# Asynchronous reset
set_false_path -from [get_ports {rst_n}]

# Maximum delay constraints
set_max_delay 8.000 -from [all_inputs] -to [all_outputs]
