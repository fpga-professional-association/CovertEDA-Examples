// PCIe Gen2 x4 Endpoint Top Level
// Arria 10 - 10AX115S2F45I1SG

module pcie_top (
    input  clk_250m,
    input  rst_n,

    // PCIe Lanes
    input  [3:0] pcie_rx,
    output [3:0] pcie_tx,

    // Application Interface
    input  [63:0] app_data_in,
    input  [7:0] app_byte_en,
    input  app_valid,
    output app_ready,

    output [63:0] app_data_out,
    output [7:0] app_byte_en_out,
    output app_valid_out,
    input  app_ready_out,

    // Control
    input  [15:0] device_id,
    input  [7:0] bar0_config,
    output pcie_link_up,
    output [7:0] link_speed
);

    // Internal signals
    wire pcie_clk;
    wire pcie_rst;
    wire [63:0] tlp_data;
    wire [7:0] tlp_be;
    wire tlp_valid;
    wire tlp_ready;
    wire [63:0] bar_data;
    wire bar_valid;
    wire [15:0] bar_address;

    // PCIe Core Instance (Altera IP stub for synthesis)
    pcie_ip pcie_core_inst (
        .pcie_rxn(pcie_rx),
        .pcie_txn(pcie_tx),
        .pcie_rx_in0(pcie_rx[0]),
        .pcie_rx_in1(pcie_rx[1]),
        .pcie_rx_in2(pcie_rx[2]),
        .pcie_rx_in3(pcie_rx[3]),
        .pcie_tx_out0(pcie_tx[0]),
        .pcie_tx_out1(pcie_tx[1]),
        .pcie_tx_out2(pcie_tx[2]),
        .pcie_tx_out3(pcie_tx[3]),
        .clk_in(clk_250m),
        .rst_n(rst_n),
        .clk250_out(pcie_clk),
        .pcie_core_clk(pcie_clk),
        .test_in(8'h0),
        .sim_only_analysis_p(1'b0)
    );

    // Reset synchronizer
    assign pcie_rst = ~rst_n;

    // TLP Handler
    tlp_handler tlp_inst (
        .clk(pcie_clk),
        .rst(pcie_rst),
        .tlp_data_in(tlp_data),
        .tlp_be_in(tlp_be),
        .tlp_valid_in(tlp_valid),
        .tlp_ready_out(tlp_ready),
        .app_data_out(app_data_out),
        .app_be_out(app_byte_en_out),
        .app_valid_out(app_valid_out),
        .app_ready_in(app_ready_out)
    );

    // BAR Decoder
    bar_decoder bar_inst (
        .clk(pcie_clk),
        .rst(pcie_rst),
        .tlp_address(bar_address),
        .bar0_config(bar0_config),
        .bar_data_in(app_data_in),
        .bar_be_in(app_byte_en),
        .bar_valid_in(app_valid),
        .bar_ready_out(app_ready),
        .bar_data_out(bar_data),
        .bar_valid_out(bar_valid)
    );

    // Link status signals
    assign pcie_link_up = 1'b1;  // Placeholder
    assign link_speed = 8'd2;    // Gen2

endmodule
