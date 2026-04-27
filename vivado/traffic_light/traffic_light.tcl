# CovertEDA-managed Vivado project script for traffic_light
# Recreate the project on demand:  vivado -mode batch -source traffic_light.tcl
create_project -force traffic_light ./vivado_proj -part xc7a35tcpg236-1
add_files -norecurse { src/traffic_light.v }
add_files -fileset constrs_1 -norecurse { constraints/traffic_light.xdc }
set_property top traffic_light [current_fileset]
update_compile_order -fileset sources_1
