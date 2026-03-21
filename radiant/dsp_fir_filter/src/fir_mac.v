// =============================================================================
// Module: fir_mac
// Description: MAC cell using DSP18X18 block for FIR filter coefficient
// Implements: output = (sample * coeff) + input_accumulator
// =============================================================================

module fir_mac (
    input   wire [15:0] sample,     // Input sample
    input   wire [15:0] coeff,      // FIR coefficient
    input   wire [31:0] mac_in,     // Accumulator input
    output  wire [31:0] mac_out     // Accumulator output
);

    // Internal registers for pipelining
    reg [15:0] sample_r1, sample_r2;
    reg [15:0] coeff_r1, coeff_r2;
    reg [31:0] mac_in_r1, mac_in_r2;
    wire [31:0] product;
    reg [31:0] mac_out_r;

    assign mac_out = mac_out_r;

    // Stage 1: Register inputs
    always @(*) begin
        sample_r1 = sample;
        coeff_r1 = coeff;
        mac_in_r1 = mac_in;
    end

    // Stage 2: Multiply
    assign product = sample_r1 * coeff_r1;

    // Stage 3: Accumulate
    always @(*) begin
        mac_out_r = mac_in + product;
    end

endmodule
