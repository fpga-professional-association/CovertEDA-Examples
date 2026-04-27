# CovertEDA-managed Vivado project script for pwm_rgb
# Recreate the project on demand:  vivado -mode batch -source pwm_rgb.tcl
create_project -force pwm_rgb ./vivado_proj -part xc7a35tcpg236-1
add_files -norecurse { src/axi_lite_slave.sv src/pwm_channel.sv src/pwm_top.sv }
add_files -fileset constrs_1 -norecurse { constraints/pwm.xdc }
set_property top pwm_top [current_fileset]
update_compile_order -fileset sources_1
