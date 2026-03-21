// UART Transmitter Top Module
// Device: iCE40UP5K

module uart_top (
    input  clk,
    input  rst_n,
    input  [7:0] data_in,
    input  valid,
    output ready,
    output uart_tx
);

    wire baud_clk;
    wire [7:0] tx_data;
    wire tx_valid;
    wire tx_ready;

    baud_gen baud_inst (
        .clk(clk),
        .rst_n(rst_n),
        .baud_clk(baud_clk)
    );

    uart_tx uart_tx_inst (
        .clk(clk),
        .rst_n(rst_n),
        .baud_clk(baud_clk),
        .data(data_in),
        .valid(valid),
        .ready(ready),
        .uart_tx(uart_tx)
    );

endmodule
