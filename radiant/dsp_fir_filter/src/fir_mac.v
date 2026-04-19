// =============================================================================
// Module: fir_mac
// Description: MAC cell for FIR filter coefficient
// Implements: output = (sample * coeff) + input_accumulator
// =============================================================================

module fir_mac (
    input   wire        clk,        // System clock
    input   wire        rst_n,      // Active-low reset
    input   wire [15:0] sample,     // Input sample
    input   wire [15:0] coeff,      // FIR coefficient
    input   wire [31:0] mac_in,     // Accumulator input
    output  reg  [31:0] mac_out     // Accumulator output
);

    // Internal pipeline registers
    wire [31:0] product;

    // Multiply
    assign product = sample * coeff;

    // Register the accumulate result
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            mac_out <= 32'h0;
        else
            mac_out <= mac_in + product;
    end

endmodule
