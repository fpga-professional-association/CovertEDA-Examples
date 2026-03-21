// =============================================================================
// UART Echo with FIFO Top Module
// Device: Xilinx Artix-7 XC7A100T-1CSG324C
// Clock: 100 MHz
// Baud Rate: 115200
// =============================================================================

module uart_top (
    input  wire         clk,          // 100 MHz system clock
    input  wire         rst_n,        // Active-low reset
    input  wire         uart_rx,      // UART receive
    output wire         uart_tx,      // UART transmit
    output wire [3:0]   status_led    // Status LEDs (RX, TX, FIFO_FULL, FIFO_EMPTY)
);

    // ---- Clock and Reset ----
    wire clk_16x;                    // 16x baud clock (1.8432 MHz for 115200)
    wire rst_sync;

    // ---- UART Interface ----
    wire [7:0]  rx_data;
    wire        rx_valid;
    wire        rx_ready;

    wire [7:0]  tx_data;
    wire        tx_valid;
    wire        tx_ready;

    // ---- FIFO Signals ----
    wire [7:0]  fifo_dout;
    wire        fifo_rd;
    wire        fifo_empty;
    wire        fifo_full;
    wire        fifo_almost_full;
    wire [9:0]  fifo_count;

    // ---- CDC and Synchronization ----
    wire rx_valid_sync;
    wire tx_ready_sync;

    // Status register
    reg [3:0] status;

    // ---- Baud Rate Clock Generation (16x oversampling) ----
    // For 115200 baud at 100 MHz: clock divisor = 100M / (115200 * 16) = 54.25 ~= 54
    baud_gen #(.DIVISOR(54)) baud_inst (
        .clk(clk),
        .rst_n(rst_n),
        .clk_16x(clk_16x)
    );

    // ---- Synchronize reset to sys clock ----
    reset_sync reset_sync_inst (
        .clk(clk),
        .rst_n(rst_n),
        .rst_sync_n(rst_sync)
    );

    // ---- UART Receiver ----
    uart_rx uart_rx_inst (
        .clk(clk_16x),
        .rst_n(rst_sync),
        .uart_rx(uart_rx),
        .data_out(rx_data),
        .data_valid(rx_valid),
        .data_ready(rx_ready)
    );

    // ---- Synchronize RX valid to system clock ----
    cdc_sync #(.WIDTH(8)) cdc_rx (
        .src_clk(clk_16x),
        .dst_clk(clk),
        .src_data(rx_data),
        .src_valid(rx_valid),
        .dst_data(fifo_din),
        .dst_valid(fifo_wr),
        .dst_ready(~fifo_full)
    );

    // ---- Synchronous FIFO (RX to TX path) ----
    sync_fifo #(.WIDTH(8), .DEPTH(512)) fifo_inst (
        .clk(clk),
        .rst_n(rst_sync),
        .din(rx_data),
        .wr_en(rx_valid & ~fifo_full),
        .dout(fifo_dout),
        .rd_en(fifo_rd),
        .empty(fifo_empty),
        .full(fifo_full),
        .almost_full(fifo_almost_full),
        .count(fifo_count)
    );

    // ---- UART Transmitter ----
    uart_tx uart_tx_inst (
        .clk(clk_16x),
        .rst_n(rst_sync),
        .data_in(fifo_dout),
        .data_valid(~fifo_empty),
        .data_ready(tx_ready),
        .uart_tx(uart_tx)
    );

    assign fifo_rd = ~fifo_empty & tx_ready;

    // ---- Status Indicator LEDs ----
    always @(posedge clk or negedge rst_sync) begin
        if (!rst_sync) begin
            status <= 4'b0000;
        end else begin
            status[0] <= rx_valid;          // RX activity
            status[1] <= fifo_rd;           // TX activity
            status[2] <= fifo_full;         // FIFO full flag
            status[3] <= fifo_empty;        // FIFO empty flag
        end
    end

    assign status_led = status;

endmodule

// =============================================================================
// Baud Rate Generator (Divisor-based)
// =============================================================================

module baud_gen #(parameter DIVISOR = 54) (
    input  wire clk,
    input  wire rst_n,
    output reg  clk_16x
);

    reg [7:0] cnt;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            cnt <= 8'b0;
            clk_16x <= 1'b0;
        end else begin
            if (cnt >= DIVISOR - 1) begin
                cnt <= 8'b0;
                clk_16x <= ~clk_16x;
            end else begin
                cnt <= cnt + 1'b1;
            end
        end
    end

endmodule

// =============================================================================
// Reset Synchronizer
// =============================================================================

module reset_sync (
    input  wire clk,
    input  wire rst_n,
    output reg  rst_sync_n
);

    reg rst_r;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            rst_r <= 1'b0;
            rst_sync_n <= 1'b0;
        end else begin
            rst_r <= 1'b1;
            rst_sync_n <= rst_r;
        end
    end

endmodule

// =============================================================================
// Clock Domain Crossing Synchronizer
// =============================================================================

module cdc_sync #(parameter WIDTH = 8) (
    input  wire             src_clk,
    input  wire             dst_clk,
    input  wire [WIDTH-1:0] src_data,
    input  wire             src_valid,
    output reg  [WIDTH-1:0] dst_data,
    output reg              dst_valid,
    input  wire             dst_ready
);

    reg [WIDTH-1:0] sync_ff;
    reg valid_ff;

    always @(posedge dst_clk) begin
        sync_ff <= src_data;
        dst_data <= sync_ff;
        valid_ff <= src_valid;
        dst_valid <= valid_ff;
    end

endmodule
