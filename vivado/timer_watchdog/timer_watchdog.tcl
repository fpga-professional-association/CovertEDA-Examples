# CovertEDA-managed Vivado project script for timer_watchdog
# Recreate the project on demand:  vivado -mode batch -source timer_watchdog.tcl
create_project -force timer_watchdog ./vivado_proj -part xc7a35tcpg236-1
add_files -norecurse { src/timer_watchdog.v }
add_files -fileset constrs_1 -norecurse { constraints/timer_watchdog.xdc }
set_property top timer_watchdog [current_fileset]
update_compile_order -fileset sources_1
