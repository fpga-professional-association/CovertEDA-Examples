// FSM-Based Pattern Sequence Detector
// Device: iCE40UP5K
// Detects the bit pattern 1011 in a serial stream

module sequence_detector (
    input      clk,
    input      rst_n,
    input      bit_in,
    input      bit_valid,
    output     detected,
    output [2:0] state_out
);

    reg [2:0] state;
    reg       detected_r;

    localparam S0 = 3'd0;  // Initial / no match
    localparam S1 = 3'd1;  // Matched '1'
    localparam S2 = 3'd2;  // Matched '10'
    localparam S3 = 3'd3;  // Matched '101'
    localparam S4 = 3'd4;  // Matched '1011' -- detected!

    assign detected  = detected_r;
    assign state_out = state;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state      <= S0;
            detected_r <= 1'b0;
        end else begin
            detected_r <= 1'b0;
            if (bit_valid) begin
                case (state)
                    S0: state <= bit_in ? S1 : S0;
                    S1: state <= bit_in ? S1 : S2;
                    S2: state <= bit_in ? S3 : S0;
                    S3: begin
                        if (bit_in) begin
                            state      <= S1; // overlap: last '1' could start new sequence
                            detected_r <= 1'b1;
                        end else
                            state <= S2;
                    end
                    default: state <= S0;
                endcase
            end
        end
    end

endmodule
