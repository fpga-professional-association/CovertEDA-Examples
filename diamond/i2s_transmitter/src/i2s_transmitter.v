// I2S Audio Transmitter - 16/24-bit samples
// Target: LFE5U-25F (ECP5)

module i2s_transmitter (
    input        clk,
    input        reset_n,
    input [23:0] left_data,
    input [23:0] right_data,
    input        sample_valid,
    input        bit_width_24,   // 0=16-bit, 1=24-bit
    output reg   sclk,           // serial clock (bit clock)
    output reg   lrclk,          // left/right clock (word select)
    output reg   sdata,          // serial data
    output reg   ready           // ready for new sample
);

    localparam DIV_RATIO = 4;  // clk/sclk divider

    reg [3:0]  clk_div;
    reg [5:0]  bit_cnt;
    reg [23:0] shift_reg;
    reg [4:0]  bits_per_ch;
    reg        channel;   // 0=left, 1=right
    reg [23:0] left_buf, right_buf;
    reg        active;

    wire sclk_edge = (clk_div == DIV_RATIO - 1);

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            clk_div   <= 0;
            bit_cnt   <= 0;
            shift_reg <= 0;
            sclk      <= 0;
            lrclk     <= 0;
            sdata     <= 0;
            ready     <= 1;
            channel   <= 0;
            left_buf  <= 0;
            right_buf <= 0;
            active    <= 0;
            bits_per_ch <= 16;
        end else begin
            bits_per_ch <= bit_width_24 ? 5'd24 : 5'd16;

            // Latch new samples
            if (sample_valid && ready) begin
                left_buf  <= left_data;
                right_buf <= right_data;
                ready     <= 1'b0;
                active    <= 1'b1;
                channel   <= 1'b0;
                bit_cnt   <= 0;
                // Load left channel MSB-first
                if (bit_width_24)
                    shift_reg <= left_data;
                else
                    shift_reg <= {left_data[15:0], 8'd0};
            end

            // Clock divider
            if (active) begin
                clk_div <= clk_div + 1;
                if (sclk_edge) begin
                    clk_div <= 0;
                    sclk <= ~sclk;

                    if (sclk) begin  // falling edge of sclk
                        sdata <= shift_reg[23];
                        shift_reg <= {shift_reg[22:0], 1'b0};
                        bit_cnt <= bit_cnt + 1;

                        if (bit_cnt == {1'b0, bits_per_ch} - 1) begin
                            bit_cnt <= 0;
                            if (channel == 0) begin
                                // Switch to right channel
                                channel <= 1;
                                lrclk   <= 1;
                                if (bit_width_24)
                                    shift_reg <= right_buf;
                                else
                                    shift_reg <= {right_buf[15:0], 8'd0};
                            end else begin
                                // Done with both channels
                                active <= 0;
                                lrclk  <= 0;
                                ready  <= 1;
                            end
                        end
                    end
                end
            end
        end
    end

endmodule
