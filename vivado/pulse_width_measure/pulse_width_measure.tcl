# CovertEDA-managed Vivado project script for pulse_width_measure
# Recreate the project on demand:  vivado -mode batch -source pulse_width_measure.tcl
create_project -force pulse_width_measure ./vivado_proj -part xc7a35tcpg236-1
add_files -norecurse { src/pulse_width_measure.v }
add_files -fileset constrs_1 -norecurse { constraints/pulse_width_measure.xdc }
set_property top pulse_width_measure [current_fileset]
update_compile_order -fileset sources_1
