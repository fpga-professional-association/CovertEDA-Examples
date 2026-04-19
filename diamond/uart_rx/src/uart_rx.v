// UART Receiver with Error Detection
// Target: LFE5U-25F (ECP5)
// 8N1 format, configurable baud via CLKS_PER_BIT parameter

module uart_rx #(
    parameter CLKS_PER_BIT = 4  // Small value for simulation
)(
    input        clk,
    input        reset_n,
    input        rx_serial,
    output reg [7:0] rx_data,
    output reg       rx_valid,
    output reg       rx_error    // framing error (bad stop bit)
);

    localparam IDLE  = 3'd0;
    localparam START = 3'd1;
    localparam DATA  = 3'd2;
    localparam STOP  = 3'd3;

    reg [2:0]  state;
    reg [15:0] clk_cnt;
    reg [2:0]  bit_idx;
    reg [7:0]  rx_shift;

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            state    <= IDLE;
            clk_cnt  <= 0;
            bit_idx  <= 0;
            rx_shift <= 0;
            rx_data  <= 0;
            rx_valid <= 0;
            rx_error <= 0;
        end else begin
            rx_valid <= 1'b0;
            rx_error <= 1'b0;

            case (state)
                IDLE: begin
                    clk_cnt <= 0;
                    bit_idx <= 0;
                    if (rx_serial == 1'b0) begin
                        state <= START;
                    end
                end

                START: begin
                    // Wait for middle of start bit
                    if (clk_cnt == (CLKS_PER_BIT - 1) / 2) begin
                        if (rx_serial == 1'b0) begin
                            clk_cnt <= 0;
                            state   <= DATA;
                        end else begin
                            state <= IDLE;  // False start
                        end
                    end else begin
                        clk_cnt <= clk_cnt + 1;
                    end
                end

                DATA: begin
                    if (clk_cnt == CLKS_PER_BIT - 1) begin
                        clk_cnt <= 0;
                        rx_shift[bit_idx] <= rx_serial;
                        if (bit_idx == 7) begin
                            state <= STOP;
                        end else begin
                            bit_idx <= bit_idx + 1;
                        end
                    end else begin
                        clk_cnt <= clk_cnt + 1;
                    end
                end

                STOP: begin
                    if (clk_cnt == CLKS_PER_BIT - 1) begin
                        clk_cnt <= 0;
                        if (rx_serial == 1'b1) begin
                            rx_data  <= rx_shift;
                            rx_valid <= 1'b1;
                        end else begin
                            rx_error <= 1'b1;  // Framing error
                        end
                        state <= IDLE;
                    end else begin
                        clk_cnt <= clk_cnt + 1;
                    end
                end

                default: state <= IDLE;
            endcase
        end
    end

endmodule
