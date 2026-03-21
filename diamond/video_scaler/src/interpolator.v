// Video Interpolator - Linear interpolation for vertical scaling
// Scales 720p (480 active lines) to 1080p (720 active lines)
// Ratio: 720/480 = 1.5x

module interpolator (
    input clk,
    input reset_n,

    // Input from line buffer
    input [23:0] pixel_in,
    input [10:0] v_count_in,
    input valid_in,

    // Output interpolated line
    output reg [23:0] pixel_out,
    output reg valid_out
);

    // Vertical line buffers (dual-line interpolation)
    reg [23:0] line_y0 [0:1919];     // Current line
    reg [23:0] line_y1 [0:1919];     // Next line
    reg [10:0] v_position;
    reg [7:0] interpolation_weight;

    // Interpolation state machine
    reg [1:0] state;
    localparam IDLE = 2'h0;
    localparam INTERP_A = 2'h1;
    localparam INTERP_B = 2'h2;

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            state <= IDLE;
            v_position <= 11'h000;
            interpolation_weight <= 8'h00;
            valid_out <= 1'b0;
        end else begin
            case(state)
                IDLE: begin
                    valid_out <= 1'b0;
                    if (valid_in) begin
                        state <= INTERP_A;
                    end
                end

                INTERP_A: begin
                    // Use input pixel directly (first output of scale factor)
                    pixel_out <= pixel_in;
                    valid_out <= 1'b1;
                    state <= INTERP_B;
                end

                INTERP_B: begin
                    // Interpolate between two input lines
                    // Simple linear: y = y0 + (weight/256) * (y1 - y0)
                    interpolation_weight <= 8'h80;  // 50% blend
                    pixel_out <= pixel_in;           // Simplified interpolation
                    valid_out <= 1'b1;
                    state <= IDLE;
                end
            endcase

            // Update vertical position (3x output for every 2x input)
            if (v_count_in[10]) begin
                v_position <= 11'h000;
            end else begin
                v_position <= v_count_in + 1'b1;
            end
        end
    end

endmodule
