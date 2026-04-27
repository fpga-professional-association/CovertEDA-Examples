# CovertEDA-managed Vivado project script for vga_controller
# Recreate the project on demand:  vivado -mode batch -source vga_controller.tcl
create_project -force vga_controller ./vivado_proj -part xc7a35tcpg236-1
add_files -norecurse { src/vga_controller.v }
add_files -fileset constrs_1 -norecurse { constraints/vga_controller.xdc }
set_property top vga_controller [current_fileset]
update_compile_order -fileset sources_1
