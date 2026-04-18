# CovertEDA — Radiant Build Script
# Device: LIFCL-40-7BG400I
# Top: blinky_top

prj_create -name "blinky_top" -impl "impl1" -dev LIFCL-40-7BG400I -performance "7_High-Performance_1.0V" -synthesis "lse" -dir "C:/Users/tcove/OneDrive/Desktop/Projects/CovertEDA-Examples/radiant/blinky_led"
prj_add_source "C:/Users/tcove/OneDrive/Desktop/Projects/CovertEDA-Examples/radiant/blinky_led/src/blinky_top.v"
prj_add_source "C:/Users/tcove/OneDrive/Desktop/Projects/CovertEDA-Examples/radiant/blinky_led/constraints/blinky.sdc"
prj_set_impl_opt -impl "impl1" "top" "blinky_top"
prj_save
prj_run_synthesis
prj_run_map
prj_run_par
prj_run_bitstream
prj_close
