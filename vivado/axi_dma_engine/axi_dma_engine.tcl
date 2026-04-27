# CovertEDA-managed Vivado project script for axi_dma_engine
# Recreate the project on demand:  vivado -mode batch -source axi_dma_engine.tcl
create_project -force axi_dma_engine ./vivado_proj -part xc7a35tcpg236-1
add_files -norecurse { src/axi_master.sv src/descriptor_cache.sv src/dma_top.sv src/sg_engine.sv }
add_files -fileset constrs_1 -norecurse { constraints/dma.xdc }
set_property top dma_top [current_fileset]
update_compile_order -fileset sources_1
