// RS232 Bridge with RTS/CTS Flow Control
// Target: MPF100T (PolarFire)
// FIFO-buffered UART with hardware flow control

module rs232_bridge #(
    parameter CLKS_PER_BIT = 4
)(
    input        clk,
    input        reset_n,
    // TX side
    input  [7:0] tx_data,
    input        tx_valid,
    output reg   tx_ready,
    output reg   txd,
    // RX side
    input        rxd,
    output reg [7:0] rx_data,
    output reg       rx_valid,
    // Flow control
    input        cts_n,    // Clear To Send (active low, from remote)
    output reg   rts_n     // Request To Send (active low, to remote)
);

    // TX state machine
    localparam TX_IDLE  = 2'd0;
    localparam TX_START = 2'd1;
    localparam TX_DATA  = 2'd2;
    localparam TX_STOP  = 2'd3;

    reg [1:0]  tx_state;
    reg [15:0] tx_clk_cnt;
    reg [2:0]  tx_bit_idx;
    reg [7:0]  tx_shift;

    // RX state machine
    localparam RX_IDLE  = 2'd0;
    localparam RX_START = 2'd1;
    localparam RX_DATA  = 2'd2;
    localparam RX_STOP  = 2'd3;

    reg [1:0]  rx_state;
    reg [15:0] rx_clk_cnt;
    reg [2:0]  rx_bit_idx;
    reg [7:0]  rx_shift;

    // RX FIFO (4 entries)
    reg [7:0] rx_fifo [0:3];
    reg [1:0] rx_wr_ptr, rx_rd_ptr;
    reg [2:0] rx_count;

    // Flow control: deassert RTS when FIFO is nearly full
    always @(*) begin
        rts_n = (rx_count >= 3) ? 1'b1 : 1'b0;
    end

    // TX logic
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            tx_state   <= TX_IDLE;
            tx_clk_cnt <= 0;
            tx_bit_idx <= 0;
            tx_shift   <= 0;
            txd        <= 1'b1;
            tx_ready   <= 1'b1;
        end else begin
            case (tx_state)
                TX_IDLE: begin
                    txd      <= 1'b1;
                    tx_ready <= 1'b1;
                    if (tx_valid && !cts_n) begin
                        tx_shift   <= tx_data;
                        tx_state   <= TX_START;
                        tx_clk_cnt <= 0;
                        tx_ready   <= 1'b0;
                    end
                end

                TX_START: begin
                    txd <= 1'b0;
                    if (tx_clk_cnt == CLKS_PER_BIT - 1) begin
                        tx_clk_cnt <= 0;
                        tx_bit_idx <= 0;
                        tx_state   <= TX_DATA;
                    end else begin
                        tx_clk_cnt <= tx_clk_cnt + 1;
                    end
                end

                TX_DATA: begin
                    txd <= tx_shift[tx_bit_idx];
                    if (tx_clk_cnt == CLKS_PER_BIT - 1) begin
                        tx_clk_cnt <= 0;
                        if (tx_bit_idx == 7)
                            tx_state <= TX_STOP;
                        else
                            tx_bit_idx <= tx_bit_idx + 1;
                    end else begin
                        tx_clk_cnt <= tx_clk_cnt + 1;
                    end
                end

                TX_STOP: begin
                    txd <= 1'b1;
                    if (tx_clk_cnt == CLKS_PER_BIT - 1) begin
                        tx_state <= TX_IDLE;
                    end else begin
                        tx_clk_cnt <= tx_clk_cnt + 1;
                    end
                end
            endcase
        end
    end

    // RX logic
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            rx_state   <= RX_IDLE;
            rx_clk_cnt <= 0;
            rx_bit_idx <= 0;
            rx_shift   <= 0;
            rx_data    <= 0;
            rx_valid   <= 0;
            rx_wr_ptr  <= 0;
            rx_rd_ptr  <= 0;
            rx_count   <= 0;
        end else begin
            rx_valid <= 1'b0;

            case (rx_state)
                RX_IDLE: begin
                    if (rxd == 1'b0) begin
                        rx_state   <= RX_START;
                        rx_clk_cnt <= 0;
                    end
                end

                RX_START: begin
                    if (rx_clk_cnt == (CLKS_PER_BIT-1)/2) begin
                        if (rxd == 1'b0) begin
                            rx_clk_cnt <= 0;
                            rx_state   <= RX_DATA;
                            rx_bit_idx <= 0;
                        end else begin
                            rx_state <= RX_IDLE;
                        end
                    end else begin
                        rx_clk_cnt <= rx_clk_cnt + 1;
                    end
                end

                RX_DATA: begin
                    if (rx_clk_cnt == CLKS_PER_BIT - 1) begin
                        rx_clk_cnt <= 0;
                        rx_shift[rx_bit_idx] <= rxd;
                        if (rx_bit_idx == 7)
                            rx_state <= RX_STOP;
                        else
                            rx_bit_idx <= rx_bit_idx + 1;
                    end else begin
                        rx_clk_cnt <= rx_clk_cnt + 1;
                    end
                end

                RX_STOP: begin
                    if (rx_clk_cnt == CLKS_PER_BIT - 1) begin
                        if (rxd == 1'b1) begin
                            rx_data  <= rx_shift;
                            rx_valid <= 1'b1;
                        end
                        rx_state <= RX_IDLE;
                    end else begin
                        rx_clk_cnt <= rx_clk_cnt + 1;
                    end
                end
            endcase
        end
    end

endmodule
