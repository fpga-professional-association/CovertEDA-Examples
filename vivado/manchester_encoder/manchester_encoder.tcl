# CovertEDA-managed Vivado project script for manchester_encoder
# Recreate the project on demand:  vivado -mode batch -source manchester_encoder.tcl
create_project -force manchester_encoder ./vivado_proj -part xc7a35tcpg236-1
add_files -norecurse { src/manchester_encoder.v }
add_files -fileset constrs_1 -norecurse { constraints/manchester_encoder.xdc }
set_property top manchester_encoder [current_fileset]
update_compile_order -fileset sources_1
