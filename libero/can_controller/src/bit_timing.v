// CAN Bit Timing Module

module bit_timing (
    input  clk,
    input  rst_n,
    output reg bit_clk,
    output reg bit_strobe
);

    // 80 MHz / 8 = 10 MHz bit clock = 100ns per bit
    // For 500 kbit/s: 10 MHz / 20 = 500 kHz clock divider

    reg [4:0] div_count;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            div_count <= 5'h0;
            bit_clk <= 1'b0;
            bit_strobe <= 1'b0;
        end else begin
            div_count <= div_count + 1'b1;

            if (div_count == 5'd19) begin
                bit_clk <= !bit_clk;
                bit_strobe <= 1'b1;
                div_count <= 5'h0;
            end else begin
                bit_strobe <= 1'b0;
            end
        end
    end

endmodule
