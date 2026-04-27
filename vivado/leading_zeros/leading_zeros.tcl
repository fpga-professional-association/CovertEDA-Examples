# CovertEDA-managed Vivado project script for leading_zeros
# Recreate the project on demand:  vivado -mode batch -source leading_zeros.tcl
create_project -force leading_zeros ./vivado_proj -part xc7a35tcpg236-1
add_files -norecurse { src/leading_zeros.v }
add_files -fileset constrs_1 -norecurse { constraints/leading_zeros.xdc }
set_property top leading_zeros [current_fileset]
update_compile_order -fileset sources_1
