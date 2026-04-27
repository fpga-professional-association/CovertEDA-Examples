# CovertEDA-managed Vivado project script for dpram
# Recreate the project on demand:  vivado -mode batch -source dpram.tcl
create_project -force dpram ./vivado_proj -part xc7a35tcpg236-1
add_files -norecurse { src/dpram.v }
add_files -fileset constrs_1 -norecurse { constraints/dpram.xdc }
set_property top dpram [current_fileset]
update_compile_order -fileset sources_1
