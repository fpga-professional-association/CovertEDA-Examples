# CovertEDA-managed Vivado project script for ddr3_test
# Recreate the project on demand:  vivado -mode batch -source ddr3_test.tcl
create_project -force ddr3_test ./vivado_proj -part xc7a35tcpg236-1
add_files -norecurse { src/mem_top.v src/pattern_checker.v src/traffic_gen.v }
add_files -fileset constrs_1 -norecurse { constraints/ddr3.xdc }
set_property top mem_top [current_fileset]
update_compile_order -fileset sources_1
