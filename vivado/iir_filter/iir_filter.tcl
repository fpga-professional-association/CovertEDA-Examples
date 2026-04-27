# CovertEDA-managed Vivado project script for iir_filter
# Recreate the project on demand:  vivado -mode batch -source iir_filter.tcl
create_project -force iir_filter ./vivado_proj -part xc7a35tcpg236-1
add_files -norecurse { src/iir_filter.v }
add_files -fileset constrs_1 -norecurse { constraints/iir_filter.xdc }
set_property top iir_filter [current_fileset]
update_compile_order -fileset sources_1
