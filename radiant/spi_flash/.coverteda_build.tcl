# CovertEDA — Radiant Build Script
# Device: LIFCL-40-9BG400C
# Top: spi_top

prj_create -name "spi_top" -impl "impl1" -dev LIFCL-40-7BG400I -performance "7_High-Performance_1.0V" -synthesis "lse" -dir "C:/Users/tcove/OneDrive/Desktop/Projects/CovertEDA-Examples/radiant/spi_flash"
prj_add_source "C:/Users/tcove/OneDrive/Desktop/Projects/CovertEDA-Examples/radiant/spi_flash/src/spi_top.v"
prj_add_source "C:/Users/tcove/OneDrive/Desktop/Projects/CovertEDA-Examples/radiant/spi_flash/src/spi_master.v"
prj_add_source "C:/Users/tcove/OneDrive/Desktop/Projects/CovertEDA-Examples/radiant/spi_flash/src/spi_fifo.v"
prj_add_source "C:/Users/tcove/OneDrive/Desktop/Projects/CovertEDA-Examples/radiant/spi_flash/constraints/spi.sdc"
prj_set_impl_opt -impl "impl1" "top" "spi_top"
prj_save
prj_run_synthesis
prj_run_map
prj_run_par
prj_run_bitstream
prj_close
