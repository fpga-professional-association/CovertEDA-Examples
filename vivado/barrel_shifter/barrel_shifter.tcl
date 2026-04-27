# CovertEDA-managed Vivado project script for barrel_shifter
# Recreate the project on demand:  vivado -mode batch -source barrel_shifter.tcl
create_project -force barrel_shifter ./vivado_proj -part xc7a35tcpg236-1
add_files -norecurse { src/barrel_shifter.v }
add_files -fileset constrs_1 -norecurse { constraints/barrel_shifter.xdc }
set_property top barrel_shifter [current_fileset]
update_compile_order -fileset sources_1
