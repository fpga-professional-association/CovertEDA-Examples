// PRNG - 32-bit Xorshift Pseudo-Random Number Generator
// Quartus / Cyclone IV E (EP4CE6)
// Algorithm: xorshift32 (Marsaglia)

module prng (
    input         clk,
    input         rst_n,
    input         enable,
    input         seed_wr,
    input  [31:0] seed_val,
    output [31:0] rng_out,
    output        valid
);

    reg [31:0] state;
    reg        valid_reg;

    assign rng_out = state;
    assign valid   = valid_reg;

    reg [31:0] xor1, xor2, xor3;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state     <= 32'h12345678;  // default seed (non-zero)
            valid_reg <= 1'b0;
        end else if (seed_wr) begin
            // Load user seed; ensure non-zero
            state     <= (seed_val == 32'd0) ? 32'h12345678 : seed_val;
            valid_reg <= 1'b0;
        end else if (enable) begin
            // Xorshift32 algorithm
            xor1 = state ^ (state << 13);
            xor2 = xor1  ^ (xor1  >> 17);
            xor3 = xor2  ^ (xor2  << 5);
            state     <= xor3;
            valid_reg <= 1'b1;
        end else begin
            valid_reg <= 1'b0;
        end
    end

endmodule
