# CovertEDA-managed Vivado project script for nco
# Recreate the project on demand:  vivado -mode batch -source nco.tcl
create_project -force nco ./vivado_proj -part xc7a35tcpg236-1
add_files -norecurse { src/nco.v }
add_files -fileset constrs_1 -norecurse { constraints/nco.xdc }
set_property top nco [current_fileset]
update_compile_order -fileset sources_1
