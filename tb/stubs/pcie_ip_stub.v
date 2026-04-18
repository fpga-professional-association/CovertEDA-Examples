// Stub for Altera PCIe IP — passthrough for simulation with Icarus Verilog
module pcie_ip (
    input  [3:0] pcie_rxn,
    output [3:0] pcie_txn,
    input        pcie_rx_in0,
    input        pcie_rx_in1,
    input        pcie_rx_in2,
    input        pcie_rx_in3,
    output       pcie_tx_out0,
    output       pcie_tx_out1,
    output       pcie_tx_out2,
    output       pcie_tx_out3,
    input        clk_in,
    input        rst_n,
    output       clk250_out,
    output       pcie_core_clk,
    input  [7:0] test_in,
    input        sim_only_analysis_p
);
    // Pass clock through
    assign clk250_out   = clk_in;
    assign pcie_core_clk = clk_in;

    // Loopback TX from RX
    assign pcie_txn     = pcie_rxn;
    assign pcie_tx_out0 = pcie_rx_in0;
    assign pcie_tx_out1 = pcie_rx_in1;
    assign pcie_tx_out2 = pcie_rx_in2;
    assign pcie_tx_out3 = pcie_rx_in3;
endmodule
