// 400G Ethernet MAC Top Module
// Device: AC7t1500ES0
// Ref Clock: 322.265625 MHz

module eth400g_top (
    input  clk_ref,
    input  rst_n,
    input  [255:0] tx_data,
    input  tx_valid,
    output tx_ready,
    output [255:0] rx_data,
    output rx_valid,
    input  rx_ready
);

    wire mac_clk;
    wire [255:0] pcs_data;

    mac_engine mac_inst (
        .clk_ref(clk_ref),
        .rst_n(rst_n),
        .tx_data(tx_data),
        .tx_valid(tx_valid),
        .tx_ready(tx_ready),
        .mac_data(pcs_data),
        .mac_valid()
    );

    pcs_layer pcs_inst (
        .clk_ref(clk_ref),
        .rst_n(rst_n),
        .in_data(pcs_data),
        .out_data(rx_data),
        .out_valid(rx_valid)
    );

endmodule
