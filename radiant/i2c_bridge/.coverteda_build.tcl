# CovertEDA — Radiant Build Script
# Device: LFD2NX-40-7MG672
# Top: i2c_top

prj_create -name "i2c_top" -impl "impl1" -dev LIFCL-40-7BG400I -performance "7_High-Performance_1.0V" -synthesis "lse" -dir "C:/Users/tcove/OneDrive/Desktop/Projects/CovertEDA-Examples/radiant/i2c_bridge"
prj_add_source "C:/Users/tcove/OneDrive/Desktop/Projects/CovertEDA-Examples/radiant/i2c_bridge/src/i2c_top.v"
prj_add_source "C:/Users/tcove/OneDrive/Desktop/Projects/CovertEDA-Examples/radiant/i2c_bridge/src/i2c_slave.v"
prj_add_source "C:/Users/tcove/OneDrive/Desktop/Projects/CovertEDA-Examples/radiant/i2c_bridge/src/wb_master.v"
prj_add_source "C:/Users/tcove/OneDrive/Desktop/Projects/CovertEDA-Examples/radiant/i2c_bridge/constraints/i2c.sdc"
prj_set_impl_opt -impl "impl1" "top" "i2c_top"
prj_save
prj_run_synthesis
prj_run_map
prj_run_par
prj_run_bitstream
prj_close
