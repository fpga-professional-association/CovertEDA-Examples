# TimeQuest SDC for Digital Downconverter (DDC)
# High-speed DSP processing constraints

# Create clock for 200MHz input
create_clock -name {clk_200m} -period 5.000 -waveform { 0.000 2.500 } [get_ports {clk_200m}]

# Clock uncertainties
set_clock_uncertainty -setup -to [get_clocks {clk_200m}] 0.150
set_clock_uncertainty -hold -to [get_clocks {clk_200m}] 0.100

# ADC Input timing constraints
set_input_delay -clock {clk_200m} -min 0.800 [get_ports {adc_data[*]}]
set_input_delay -clock {clk_200m} -max 3.200 [get_ports {adc_data[*]}]
set_input_delay -clock {clk_200m} -min 0.800 [get_ports {adc_valid}]
set_input_delay -clock {clk_200m} -max 3.200 [get_ports {adc_valid}]

# Frequency and decimation control inputs
set_input_delay -clock {clk_200m} -min 1.0 [get_ports {nco_freq[*]}]
set_input_delay -clock {clk_200m} -max 4.0 [get_ports {nco_freq[*]}]
set_input_delay -clock {clk_200m} -min 1.0 [get_ports {decim_rate[*]}]
set_input_delay -clock {clk_200m} -max 4.0 [get_ports {decim_rate[*]}]

# Output timing constraints
set_output_delay -clock {clk_200m} -min -1.5 [get_ports {i_data[*]}]
set_output_delay -clock {clk_200m} -max 5.5 [get_ports {i_data[*]}]
set_output_delay -clock {clk_200m} -min -1.5 [get_ports {q_data[*]}]
set_output_delay -clock {clk_200m} -max 5.5 [get_ports {q_data[*]}]
set_output_delay -clock {clk_200m} -min -1.5 [get_ports {output_valid}]
set_output_delay -clock {clk_200m} -max 5.5 [get_ports {output_valid}]

# Multicycle paths for complex math operations
set_multicycle_path -from [get_registers {*nco_inst*}] -to [get_registers {*mix*}] -setup 3
set_multicycle_path -from [get_registers {*mix*}] -to [get_registers {*cic_inst*}] -setup 2
set_multicycle_path -from [get_registers {*cic_inst*}] -to [get_registers {*fir_inst*}] -setup 2

# Asynchronous reset
set_false_path -from [get_ports {rst_n}]

# Maximum delay constraints (tight for DSP pipeline)
set_max_delay 5.000 -from [all_inputs] -to [all_outputs]

# False paths for control signals (not time-critical)
set_false_path -from [get_ports {nco_freq[*]}] -to [all_outputs]
set_false_path -from [get_ports {decim_rate[*]}] -to [all_outputs]
