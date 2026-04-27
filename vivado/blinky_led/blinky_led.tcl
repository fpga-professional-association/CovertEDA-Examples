# CovertEDA-managed Vivado project script for blinky_led
# Recreate the project on demand:  vivado -mode batch -source blinky_led.tcl
create_project -force blinky_led ./vivado_proj -part xc7a35tcpg236-1
add_files -norecurse { src/blinky_top.v }
add_files -fileset constrs_1 -norecurse { constraints/blinky.xdc }
set_property top blinky_top [current_fileset]
update_compile_order -fileset sources_1
