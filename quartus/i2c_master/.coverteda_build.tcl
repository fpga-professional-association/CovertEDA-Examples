# CovertEDA — Quartus Prime Build Script
# Device: 10CL025YF256C8G
# Top: i2c_master

# Open existing project or create new
project_open C:/Users/tcove/OneDrive/Desktop/Projects/CovertEDA-Examples/quartus/i2c_master/i2c_master

# Set device and top-level
set_global_assignment -name DEVICE 10CL025YF256C8G
set_global_assignment -name TOP_LEVEL_ENTITY i2c_master

# Source files
set_global_assignment -name VERILOG_FILE "C:/Users/tcove/OneDrive/Desktop/Projects/CovertEDA-Examples/quartus/i2c_master/src/i2c_master.v"

# Constraint files
set_global_assignment -name SDC_FILE "C:/Users/tcove/OneDrive/Desktop/Projects/CovertEDA-Examples/quartus/i2c_master/constraints/i2c_master.sdc"

if {[catch {execute_module -tool syn} err]} {
    puts "ERROR: Stage 'synth' failed: $err"
    # Print report file contents for diagnostics
    foreach rpt [glob -nocomplain *.syn.rpt *_syn.rpt] {
        puts "--- Report: $rpt ---"
        if {[catch {set f [open $rpt r]; puts [read $f]; close $f}]} {}
    }
    project_close
    exit 1
}
if {[catch {execute_module -tool fit} err]} {
    puts "ERROR: Stage 'fit' failed: $err"
    # Print report file contents for diagnostics
    foreach rpt [glob -nocomplain *.fit.rpt *_fit.rpt] {
        puts "--- Report: $rpt ---"
        if {[catch {set f [open $rpt r]; puts [read $f]; close $f}]} {}
    }
    project_close
    exit 1
}
if {[catch {execute_module -tool sta} err]} {
    puts "ERROR: Stage 'sta' failed: $err"
    # Print report file contents for diagnostics
    foreach rpt [glob -nocomplain *.sta.rpt *_sta.rpt] {
        puts "--- Report: $rpt ---"
        if {[catch {set f [open $rpt r]; puts [read $f]; close $f}]} {}
    }
    project_close
    exit 1
}
if {[catch {execute_module -tool asm} err]} {
    puts "ERROR: Stage 'asm' failed: $err"
    # Print report file contents for diagnostics
    foreach rpt [glob -nocomplain *.asm.rpt *_asm.rpt] {
        puts "--- Report: $rpt ---"
        if {[catch {set f [open $rpt r]; puts [read $f]; close $f}]} {}
    }
    project_close
    exit 1
}

project_close
