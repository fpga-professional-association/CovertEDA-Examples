# CovertEDA-managed Vivado project script for fifo_async
# Recreate the project on demand:  vivado -mode batch -source fifo_async.tcl
create_project -force fifo_async ./vivado_proj -part xc7a35tcpg236-1
add_files -norecurse { src/fifo_async.v }
add_files -fileset constrs_1 -norecurse { constraints/fifo_async.xdc }
set_property top fifo_async [current_fileset]
update_compile_order -fileset sources_1
