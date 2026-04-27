# CovertEDA-managed Vivado project script for divider
# Recreate the project on demand:  vivado -mode batch -source divider.tcl
create_project -force divider ./vivado_proj -part xc7a35tcpg236-1
add_files -norecurse { src/divider.v }
add_files -fileset constrs_1 -norecurse { constraints/divider.xdc }
set_property top divider [current_fileset]
update_compile_order -fileset sources_1
