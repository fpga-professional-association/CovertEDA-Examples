// SPI Master - Configurable CPOL/CPHA
// Quartus / Cyclone IV E (EP4CE6)
// 8-bit SPI master with configurable clock polarity and phase

module spi_master (
    input        clk,
    input        rst_n,
    input        start,       // start transaction
    input  [7:0] data_in,     // data to transmit
    input        cpol,        // clock polarity
    input        cpha,        // clock phase
    input  [3:0] clk_div,     // SCK clock divider (0-15)
    output [7:0] data_out,    // received data
    output       busy,        // transaction in progress
    output       done,        // transaction complete pulse
    output       sck,         // SPI clock
    output       mosi,        // master out slave in
    input        miso,        // master in slave out
    output       cs_n         // chip select (active low)
);

    localparam IDLE   = 2'd0;
    localparam ACTIVE = 2'd1;
    localparam FINISH = 2'd2;

    reg [1:0]  state;
    reg [7:0]  tx_shift;
    reg [7:0]  rx_shift;
    reg [7:0]  data_out_reg;
    reg [3:0]  bit_cnt;
    reg [3:0]  div_cnt;
    reg        sck_reg;
    reg        mosi_reg;
    reg        cs_n_reg;
    reg        busy_reg;
    reg        done_reg;
    reg        sck_edge;  // toggles on each SCK edge

    assign data_out = data_out_reg;
    assign busy     = busy_reg;
    assign done     = done_reg;
    assign sck      = sck_reg;
    assign mosi     = mosi_reg;
    assign cs_n     = cs_n_reg;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state        <= IDLE;
            tx_shift     <= 8'd0;
            rx_shift     <= 8'd0;
            data_out_reg <= 8'd0;
            bit_cnt      <= 4'd0;
            div_cnt      <= 4'd0;
            sck_reg      <= 1'b0;
            mosi_reg     <= 1'b0;
            cs_n_reg     <= 1'b1;
            busy_reg     <= 1'b0;
            done_reg     <= 1'b0;
            sck_edge     <= 1'b0;
        end else begin
            done_reg <= 1'b0;

            case (state)
                IDLE: begin
                    sck_reg  <= cpol;
                    cs_n_reg <= 1'b1;
                    mosi_reg <= 1'b0;
                    if (start) begin
                        state    <= ACTIVE;
                        tx_shift <= data_in;
                        rx_shift <= 8'd0;
                        bit_cnt  <= 4'd0;
                        div_cnt  <= 4'd0;
                        cs_n_reg <= 1'b0;
                        busy_reg <= 1'b1;
                        sck_reg  <= cpol;
                        sck_edge <= 1'b0;
                        // CPHA=0: put first bit on MOSI immediately
                        if (!cpha)
                            mosi_reg <= data_in[7];
                    end
                end

                ACTIVE: begin
                    div_cnt <= div_cnt + 4'd1;
                    if (div_cnt >= clk_div) begin
                        div_cnt  <= 4'd0;
                        sck_edge <= ~sck_edge;
                        sck_reg  <= sck_edge ? cpol : ~cpol;

                        if (cpha == 1'b0) begin
                            // CPHA=0: sample on leading edge, shift on trailing
                            if (!sck_edge) begin
                                // Leading edge: sample MISO
                                rx_shift <= {rx_shift[6:0], miso};
                                bit_cnt  <= bit_cnt + 4'd1;
                            end else begin
                                // Trailing edge: shift out next bit
                                tx_shift <= {tx_shift[6:0], 1'b0};
                                mosi_reg <= tx_shift[6];
                            end
                        end else begin
                            // CPHA=1: shift on leading edge, sample on trailing
                            if (!sck_edge) begin
                                // Leading edge: shift out
                                mosi_reg <= tx_shift[7];
                                tx_shift <= {tx_shift[6:0], 1'b0};
                            end else begin
                                // Trailing edge: sample MISO
                                rx_shift <= {rx_shift[6:0], miso};
                                bit_cnt  <= bit_cnt + 4'd1;
                            end
                        end

                        if (bit_cnt >= 4'd8) begin
                            state        <= FINISH;
                            data_out_reg <= rx_shift;
                        end
                    end
                end

                FINISH: begin
                    cs_n_reg <= 1'b1;
                    sck_reg  <= cpol;
                    busy_reg <= 1'b0;
                    done_reg <= 1'b1;
                    state    <= IDLE;
                end
            endcase
        end
    end

endmodule
