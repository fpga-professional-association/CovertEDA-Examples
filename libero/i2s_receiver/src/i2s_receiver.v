// I2S Audio Receiver - 16/24-bit samples
// Target: MPF100T (PolarFire)

module i2s_receiver (
    input        clk,
    input        reset_n,
    input        sclk_in,      // serial clock (bit clock)
    input        lrclk_in,     // left/right clock
    input        sdata_in,     // serial data
    input        bit_width_24, // 0=16-bit, 1=24-bit
    output reg [23:0] left_data,
    output reg [23:0] right_data,
    output reg        sample_valid
);

    reg        sclk_d1, sclk_d2;
    reg        lrclk_d1;
    reg [23:0] shift_reg;
    reg [4:0]  bit_cnt;
    reg        channel;        // 0=left, 1=right
    reg [4:0]  bits_per_ch;

    wire sclk_rise = ~sclk_d2 & sclk_d1;

    // Synchronize sclk
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            sclk_d1  <= 1'b0;
            sclk_d2  <= 1'b0;
            lrclk_d1 <= 1'b0;
        end else begin
            sclk_d1  <= sclk_in;
            sclk_d2  <= sclk_d1;
            lrclk_d1 <= lrclk_in;
        end
    end

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            shift_reg    <= 24'd0;
            bit_cnt      <= 5'd0;
            channel      <= 1'b0;
            left_data    <= 24'd0;
            right_data   <= 24'd0;
            sample_valid <= 1'b0;
            bits_per_ch  <= 5'd16;
        end else begin
            sample_valid <= 1'b0;
            bits_per_ch  <= bit_width_24 ? 5'd24 : 5'd16;

            if (sclk_rise) begin
                // Shift in data MSB-first
                shift_reg <= {shift_reg[22:0], sdata_in};
                bit_cnt   <= bit_cnt + 1;

                // Detect channel change via lrclk transition
                if (lrclk_in != lrclk_d1) begin
                    bit_cnt <= 0;
                    if (lrclk_in == 1'b1) begin
                        // Transition to right channel - save left
                        if (bit_width_24)
                            left_data <= shift_reg;
                        else
                            left_data <= {shift_reg[15:0], 8'd0};
                        channel <= 1'b1;
                    end else begin
                        // Transition to left channel - save right
                        if (bit_width_24)
                            right_data <= shift_reg;
                        else
                            right_data <= {shift_reg[15:0], 8'd0};
                        channel      <= 1'b0;
                        sample_valid <= 1'b1;
                    end
                end
            end
        end
    end

endmodule
