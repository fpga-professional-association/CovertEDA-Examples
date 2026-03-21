create_clock -name sys_clk -period 10.0 -waveform {0 5} [get_ports clk]

set_input_delay -clock sys_clk -max 2.0 [get_ports {rst_n speed_cmd encoder_a encoder_b}]
set_output_delay -clock sys_clk -max 2.0 [get_ports {pwm_u pwm_v pwm_w pwm_u_n pwm_v_n pwm_w_n encoder_count speed_measured}]

set_false_path -from [get_ports rst_n]
set_multicycle_path -setup 2 -from [get_ports encoder_a]
set_multicycle_path -hold 1 -from [get_ports encoder_a]
