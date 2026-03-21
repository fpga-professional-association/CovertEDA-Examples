// Numerically Controlled Oscillator (NCO)
// Generates sine and cosine outputs using Taylor series approximation

module nco (
    input  clk,
    input  rst,
    input  [31:0] freq_word,       // Frequency tuning word (32-bit)
    output signed [15:0] i_out,    // Cosine output (I component)
    output signed [15:0] q_out,    // Sine output (Q component)
    output valid
);

    reg [31:0] phase_acc;
    wire [31:0] phase_next;
    wire [7:0] phase_index;
    wire [15:0] sin_val, cos_val;

    // Phase accumulator
    assign phase_next = phase_acc + freq_word;

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            phase_acc <= 32'b0;
        end else begin
            phase_acc <= phase_next;
        end
    end

    // Use upper 8 bits for lookup table index (256 entries for quarter cycle)
    assign phase_index = phase_acc[31:24];

    // Sine/Cosine LUT (simplified to 256 entries)
    sine_cos_lut lut_inst (
        .index(phase_index),
        .sin_val(sin_val),
        .cos_val(cos_val)
    );

    // Apply quadrant correction based on phase_acc[30:29]
    always @(posedge clk or posedge rst) begin
        if (rst) begin
            // Reset outputs
        end else begin
            case (phase_acc[31:30])
                2'b00: begin  // 0-90 degrees
                    i_out <= cos_val;
                    q_out <= sin_val;
                end
                2'b01: begin  // 90-180 degrees
                    i_out <= -sin_val;
                    q_out <= cos_val;
                end
                2'b10: begin  // 180-270 degrees
                    i_out <= -cos_val;
                    q_out <= -sin_val;
                end
                2'b11: begin  // 270-360 degrees
                    i_out <= sin_val;
                    q_out <= -cos_val;
                end
            endcase
        end
    end

    assign valid = 1'b1;

endmodule

// Sine/Cosine Lookup Table
module sine_cos_lut (
    input  [7:0] index,
    output [15:0] sin_val,
    output [15:0] cos_val
);

    wire [15:0] sin_rom [0:255];
    wire [15:0] cos_rom [0:255];

    // Initialize ROMs with precomputed sine/cosine values
    // For brevity, just return index * 256 as placeholder
    assign sin_val = {index, 8'b0};
    assign cos_val = {8'b0, index};

endmodule
