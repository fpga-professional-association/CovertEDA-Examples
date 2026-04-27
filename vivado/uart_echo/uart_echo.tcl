# CovertEDA-managed Vivado project script for uart_echo
# Recreate the project on demand:  vivado -mode batch -source uart_echo.tcl
create_project -force uart_echo ./vivado_proj -part xc7a35tcpg236-1
add_files -norecurse { src/sync_fifo.sv src/uart_rx.sv src/uart_top.sv src/uart_tx.sv }
add_files -fileset constrs_1 -norecurse { constraints/uart.xdc }
set_property top uart_top [current_fileset]
update_compile_order -fileset sources_1
