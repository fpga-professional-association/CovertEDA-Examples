// =============================================================================
// Module: coeff_rom
// Description: Coefficient storage for FIR filter (can be replaced with EBR)
// 8 coefficients × 16 bits
// =============================================================================

module coeff_rom (
    input   wire [2:0]  addr,       // Coefficient address
    output  wire [15:0] coeff       // Coefficient value
);

    // Coefficient values for 8-tap lowpass FIR filter
    // These are Q1.15 fixed-point coefficients
    reg [15:0] coeffs[0:7];

    initial begin
        coeffs[0] = 16'h0C3B;  // 0.0766 * 2^15
        coeffs[1] = 16'h1F4A;  // 0.1234 * 2^15
        coeffs[2] = 16'h2B5C;  // 0.1707 * 2^15
        coeffs[3] = 16'h2F6D;  // 0.1855 * 2^15
        coeffs[4] = 16'h2F6D;  // 0.1855 * 2^15 (symmetrical)
        coeffs[5] = 16'h2B5C;  // 0.1707 * 2^15
        coeffs[6] = 16'h1F4A;  // 0.1234 * 2^15
        coeffs[7] = 16'h0C3B;  // 0.0766 * 2^15
    end

    assign coeff = coeffs[addr];

endmodule
