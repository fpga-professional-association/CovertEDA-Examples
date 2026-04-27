# CovertEDA-managed Vivado project script for hamming_encoder
# Recreate the project on demand:  vivado -mode batch -source hamming_encoder.tcl
create_project -force hamming_encoder ./vivado_proj -part xc7a35tcpg236-1
add_files -norecurse { src/hamming_encoder.v }
add_files -fileset constrs_1 -norecurse { constraints/hamming_encoder.xdc }
set_property top hamming_encoder [current_fileset]
update_compile_order -fileset sources_1
