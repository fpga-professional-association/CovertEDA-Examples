// UART Bridge Top-Level Module
// USB to UART conversion interface
// Target: LFE5U-45F-8BG381C
// Oscillator: 48 MHz

module uart_top (
    input clk_48m,          // 48 MHz system clock
    input reset_n,          // Active low reset

    // USB side
    input usb_rx_data,      // USB RX data valid
    input [7:0] usb_data_in,// USB data input
    output usb_tx_ready,    // USB ready for TX
    output [7:0] usb_data_out,// USB data output
    output usb_tx_valid,    // USB TX data valid

    // UART side
    output uart_tx,         // UART transmit
    input uart_rx,          // UART receive

    // Status LEDs
    output [2:0] status_led
);

    // Internal signals
    wire uart_rx_valid;
    wire [7:0] uart_rx_data;
    wire uart_tx_ready;
    wire [7:0] fifo_rx_dout;
    wire fifo_rx_valid;
    wire fifo_rx_empty;
    wire fifo_tx_valid;
    wire [7:0] fifo_tx_din;

    // Status signals
    reg [23:0] activity_counter;
    reg [2:0] status_reg;

    // Instantiate UART Core
    uart_core uart_inst (
        .clk(clk_48m),
        .reset_n(reset_n),
        .baud_rate(4'd4),       // 115200 baud @ 48MHz
        .tx(uart_tx),
        .rx(uart_rx),
        .tx_data(fifo_tx_din),
        .tx_valid(fifo_tx_valid),
        .tx_ready(uart_tx_ready),
        .rx_data(uart_rx_data),
        .rx_valid(uart_rx_valid)
    );

    // Instantiate RX FIFO (USB -> UART)
    fifo_sync #(.WIDTH(8), .DEPTH(512)) fifo_rx_inst (
        .clk(clk_48m),
        .reset_n(reset_n),
        .wr_en(usb_rx_data),
        .wr_data(usb_data_in),
        .rd_en(uart_tx_ready && !fifo_rx_empty),
        .rd_data(fifo_rx_dout),
        .empty(fifo_rx_empty),
        .full(),
        .count()
    );

    // Instantiate TX FIFO (UART -> USB)
    fifo_sync #(.WIDTH(8), .DEPTH(512)) fifo_tx_inst (
        .clk(clk_48m),
        .reset_n(reset_n),
        .wr_en(uart_rx_valid),
        .wr_data(uart_rx_data),
        .rd_en(usb_tx_ready),
        .rd_data(usb_data_out),
        .empty(),
        .full(),
        .count()
    );

    // Activity monitor
    always @(posedge clk_48m or negedge reset_n) begin
        if (!reset_n) begin
            activity_counter <= 24'h000000;
            status_reg <= 3'b100;  // Power on LED
        end else begin
            if (uart_rx_valid || usb_rx_data) begin
                activity_counter <= 24'hFFFFFF;
                status_reg[0] <= 1'b1;
            end

            if (uart_tx_ready && fifo_rx_valid) begin
                status_reg[1] <= 1'b1;
            end

            if (activity_counter > 0) begin
                activity_counter <= activity_counter - 1;
            end else begin
                status_reg[0] <= 1'b0;
                status_reg[1] <= 1'b0;
            end
        end
    end

    assign usb_tx_valid = uart_rx_valid;
    assign usb_tx_ready = 1'b1;
    assign fifo_tx_valid = uart_rx_valid;
    assign fifo_tx_din = uart_rx_data;
    assign status_led = status_reg;

endmodule
