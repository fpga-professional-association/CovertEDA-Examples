# CovertEDA-managed Vivado project script for axi_fifo
# Recreate the project on demand:  vivado -mode batch -source axi_fifo.tcl
create_project -force axi_fifo ./vivado_proj -part xc7a35tcpg236-1
add_files -norecurse { src/axi_fifo.v }
add_files -fileset constrs_1 -norecurse { constraints/axi_fifo.xdc }
set_property top axi_fifo [current_fileset]
update_compile_order -fileset sources_1
