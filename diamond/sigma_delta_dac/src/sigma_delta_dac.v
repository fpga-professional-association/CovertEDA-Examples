// 1-bit Sigma-Delta DAC - 16-bit input
// Target: LFE5U-25F (ECP5)
// First-order sigma-delta modulator

module sigma_delta_dac (
    input         clk,
    input         reset_n,
    input  [15:0] din,        // 16-bit unsigned input sample
    input         din_valid,
    output reg    dout,       // 1-bit output
    output reg    dout_valid
);

    reg [16:0] accumulator;
    reg [15:0] sample_reg;

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            accumulator <= 17'd0;
            sample_reg  <= 16'd0;
            dout        <= 1'b0;
            dout_valid  <= 1'b0;
        end else begin
            // Latch new sample
            if (din_valid) begin
                sample_reg <= din;
            end

            // Sigma-delta: accumulator += sample, output = carry
            accumulator <= accumulator[15:0] + sample_reg;
            dout        <= accumulator[16];
            dout_valid  <= 1'b1;
        end
    end

endmodule
