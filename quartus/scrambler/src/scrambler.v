// Scrambler - 8-bit data scrambler/descrambler with XOR key
// Quartus / Cyclone IV E (EP4CE6)

module scrambler (
    input        clk,
    input        rst_n,
    input        valid_in,
    input  [7:0] din,
    input  [7:0] key,
    input        descramble,  // 0=scramble, 1=descramble
    output [7:0] dout,
    output       valid_out
);

    reg [7:0]  lfsr;
    reg [7:0]  dout_reg;
    reg        valid_out_reg;

    assign dout      = dout_reg;
    assign valid_out = valid_out_reg;

    // LFSR feedback polynomial: x^8 + x^6 + x^5 + x^4 + 1
    wire lfsr_feedback = lfsr[7] ^ lfsr[5] ^ lfsr[4] ^ lfsr[3];

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            lfsr          <= 8'hFF;  // non-zero init
            dout_reg      <= 8'd0;
            valid_out_reg <= 1'b0;
        end else begin
            valid_out_reg <= 1'b0;

            if (valid_in) begin
                // Advance LFSR
                lfsr <= {lfsr[6:0], lfsr_feedback};

                if (!descramble) begin
                    // Scramble: XOR data with key and LFSR
                    dout_reg <= din ^ key ^ lfsr;
                end else begin
                    // Descramble: same operation (XOR is self-inverse)
                    dout_reg <= din ^ key ^ lfsr;
                end

                valid_out_reg <= 1'b1;
            end
        end
    end

endmodule
