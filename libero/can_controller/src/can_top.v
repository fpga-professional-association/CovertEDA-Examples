// CAN 2.0B Controller Top Module
// Device: MPF300T-1FCG1152I

module can_top (
    input  clk,
    input  rst_n,
    input  can_rx,
    output can_tx,
    input  [31:0] tx_id,
    input  [63:0] tx_data,
    input  [3:0]  tx_dlc,
    input  tx_valid,
    output tx_ready,
    output [31:0] rx_id,
    output [63:0] rx_data,
    output [3:0]  rx_dlc,
    output rx_valid
);

    wire bit_clk;
    wire bit_strobe;

    // Bit timing module
    bit_timing bit_timer (
        .clk(clk),
        .rst_n(rst_n),
        .bit_clk(bit_clk),
        .bit_strobe(bit_strobe)
    );

    // CAN core
    can_core can_core_inst (
        .clk(clk),
        .rst_n(rst_n),
        .bit_clk(bit_clk),
        .bit_strobe(bit_strobe),
        .can_rx(can_rx),
        .can_tx(can_tx),
        .tx_id(tx_id),
        .tx_data(tx_data),
        .tx_dlc(tx_dlc),
        .tx_valid(tx_valid),
        .tx_ready(tx_ready),
        .rx_id(rx_id),
        .rx_data(rx_data),
        .rx_dlc(rx_dlc),
        .rx_valid(rx_valid)
    );

endmodule
