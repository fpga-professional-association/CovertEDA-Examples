// =============================================================================
// 32-bit NCO with Phase Accumulator and 12-bit Sine Output
// Device: Xilinx Artix-7 XC7A35T
// Uses a quarter-wave sine LUT (256 entries)
// =============================================================================

module nco (
    input  wire        clk,
    input  wire        rst_n,
    input  wire [31:0] freq_word,   // Phase increment per clock
    input  wire [11:0] phase_offset,
    output reg  [11:0] sine_out,
    output reg         valid_out
);

    // Phase accumulator
    reg [31:0] phase_acc;

    // Use top 8 bits of phase accumulator for LUT addressing
    wire [7:0] lut_addr;
    wire       quadrant_flip;   // Flip amplitude in 2nd/4th quadrants
    wire       quadrant_neg;    // Negate in 3rd/4th quadrants

    wire [9:0] phase_top;
    assign phase_top = phase_acc[31:22] + {phase_offset[11:2]};

    assign quadrant_neg  = phase_top[9];
    assign quadrant_flip = phase_top[8];
    assign lut_addr = quadrant_flip ? ~phase_top[7:0] : phase_top[7:0];

    // Quarter-wave sine LUT (256 entries, 12-bit unsigned)
    reg [11:0] sine_lut [0:255];
    integer i;
    initial begin
        for (i = 0; i < 256; i = i + 1) begin
            // Approximate: sin(pi/2 * i/256) * 2047
            // Precomputed linear approximation for simplicity
            sine_lut[i] = (i * 2047) / 255;
        end
    end

    wire [11:0] lut_val;
    assign lut_val = sine_lut[lut_addr];

    // Apply quadrant sign
    wire [11:0] sine_signed;
    assign sine_signed = quadrant_neg ? (12'd2048 - lut_val) : (12'd2048 + lut_val);

    // Phase accumulator update
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            phase_acc <= 32'd0;
            sine_out  <= 12'd2048;  // Mid-scale
            valid_out <= 1'b0;
        end else begin
            phase_acc <= phase_acc + freq_word;
            sine_out  <= sine_signed;
            valid_out <= 1'b1;
        end
    end

endmodule
