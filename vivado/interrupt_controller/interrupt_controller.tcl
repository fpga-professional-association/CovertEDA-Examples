# CovertEDA-managed Vivado project script for interrupt_controller
# Recreate the project on demand:  vivado -mode batch -source interrupt_controller.tcl
create_project -force interrupt_controller ./vivado_proj -part xc7a35tcpg236-1
add_files -norecurse { src/interrupt_controller.v }
add_files -fileset constrs_1 -norecurse { constraints/interrupt_controller.xdc }
set_property top interrupt_controller [current_fileset]
update_compile_order -fileset sources_1
