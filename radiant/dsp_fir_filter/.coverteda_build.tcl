# CovertEDA — Radiant Build Script
# Device: LIFCL-40-7BG400I
# Top: fir_top

prj_create -name "fir_top" -impl "impl1" -dev LIFCL-40-7BG400I -performance "7_High-Performance_1.0V" -synthesis "lse" -dir "C:/Users/tcove/OneDrive/Desktop/Projects/CovertEDA-Examples/radiant/dsp_fir_filter"
prj_add_source "C:/Users/tcove/OneDrive/Desktop/Projects/CovertEDA-Examples/radiant/dsp_fir_filter/src/fir_top.v"
prj_add_source "C:/Users/tcove/OneDrive/Desktop/Projects/CovertEDA-Examples/radiant/dsp_fir_filter/src/fir_mac.v"
prj_add_source "C:/Users/tcove/OneDrive/Desktop/Projects/CovertEDA-Examples/radiant/dsp_fir_filter/src/coeff_rom.v"
prj_add_source "C:/Users/tcove/OneDrive/Desktop/Projects/CovertEDA-Examples/radiant/dsp_fir_filter/constraints/fir.sdc"
prj_set_impl_opt -impl "impl1" "top" "fir_top"
prj_save
prj_run_synthesis
prj_run_map
prj_run_par
prj_run_bitstream
prj_close
