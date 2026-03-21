// =============================================================================
// Design      : UART Controller
// Module      : uart_top
// Description : Full UART TX/RX interface with 115200 baud rate
// Device      : LIFCL-40-7BG400I
// Frequency   : 50 MHz
// Baud Rate   : 115200 bps
// =============================================================================

module uart_top (
    input   wire        clk,        // 50 MHz system clock
    input   wire        rst_n,      // Active-low reset

    // UART RX interface
    input   wire        rx,         // Serial receive data
    output  wire        rx_valid,   // RX data valid flag
    output  wire [7:0]  rx_data,    // RX data byte

    // UART TX interface
    input   wire        tx_valid,   // TX data valid flag
    input   wire [7:0]  tx_data,    // TX data byte
    output  wire        tx_ready,   // TX ready flag
    output  wire        tx          // Serial transmit data
);

    // Baud rate generator instantiation
    wire baud_clk;
    baud_gen baudgen (
        .clk(clk),
        .rst_n(rst_n),
        .baud_clk(baud_clk)
    );

    // UART RX instantiation
    uart_rx receiver (
        .clk(clk),
        .baud_clk(baud_clk),
        .rst_n(rst_n),
        .rx(rx),
        .data_out(rx_data),
        .data_valid(rx_valid)
    );

    // UART TX instantiation
    uart_tx transmitter (
        .clk(clk),
        .baud_clk(baud_clk),
        .rst_n(rst_n),
        .data_in(tx_data),
        .data_valid(tx_valid),
        .tx_ready(tx_ready),
        .tx(tx)
    );

endmodule
