# CovertEDA — Radiant Build Script
# Device: LIFCL-40-7BG400I
# Top: uart_top

prj_create -name "uart_top" -impl "impl1" -dev LIFCL-40-7BG400I -performance "7_High-Performance_1.0V" -synthesis "lse" -dir "C:/Users/tcove/OneDrive/Desktop/Projects/CovertEDA-Examples/radiant/uart_controller"
prj_add_source "C:/Users/tcove/OneDrive/Desktop/Projects/CovertEDA-Examples/radiant/uart_controller/src/uart_top.v"
prj_add_source "C:/Users/tcove/OneDrive/Desktop/Projects/CovertEDA-Examples/radiant/uart_controller/src/uart_tx.v"
prj_add_source "C:/Users/tcove/OneDrive/Desktop/Projects/CovertEDA-Examples/radiant/uart_controller/src/uart_rx.v"
prj_add_source "C:/Users/tcove/OneDrive/Desktop/Projects/CovertEDA-Examples/radiant/uart_controller/src/baud_gen.v"
prj_add_source "C:/Users/tcove/OneDrive/Desktop/Projects/CovertEDA-Examples/radiant/uart_controller/constraints/uart.sdc"
prj_set_impl_opt -impl "impl1" "top" "uart_top"
prj_save
prj_run_synthesis
prj_run_map
prj_run_par
prj_run_bitstream
prj_close
