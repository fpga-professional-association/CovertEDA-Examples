// =============================================================================
// Design      : LFSR
// Module      : lfsr
// Description : 16-bit LFSR pseudo-random generator with configurable taps
// Device      : LIFCL-40-7BG400I
// Frequency   : 25 MHz
// =============================================================================

module lfsr #(
    parameter SEED = 16'hACE1
)(
    input   wire        clk,
    input   wire        rst_n,
    input   wire        enable,
    input   wire        load,           // Load seed value
    input   wire [15:0] seed_in,        // External seed
    output  reg  [15:0] lfsr_out,       // LFSR output
    output  wire        bit_out         // Single-bit random output
);

    // Taps for maximal length 16-bit LFSR: x^16 + x^14 + x^13 + x^11 + 1
    wire feedback;
    assign feedback = lfsr_out[15] ^ lfsr_out[13] ^ lfsr_out[12] ^ lfsr_out[10];
    assign bit_out  = lfsr_out[0];

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            lfsr_out <= SEED;
        end else if (load) begin
            lfsr_out <= (seed_in == 16'd0) ? SEED : seed_in;  // Prevent all-zero lockup
        end else if (enable) begin
            lfsr_out <= {lfsr_out[14:0], feedback};
        end
    end

endmodule
