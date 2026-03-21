// Pseudo-Random Binary Sequence (PRBS) Generator
// Implements PRBS7 (2^7-1 = 127-bit polynomial)
// Configurable width for parallel output

module prbs_gen #(
    parameter WIDTH = 32
) (
    input clk,
    input reset_n,
    input enable,
    output reg [WIDTH-1:0] prbs_out
);

    // PRBS7 state register
    reg [6:0] lfsr;
    wire [6:0] feedback;

    // PRBS7 feedback: taps at positions 7 and 6
    assign feedback = {
        lfsr[5] ^ lfsr[6],     // tap[7]
        lfsr[4] ^ lfsr[6],     // tap[6]
        lfsr[5],
        lfsr[4],
        lfsr[3],
        lfsr[2],
        lfsr[1] ^ lfsr[6]      // tap[1]
    };

    // Generate parallel PRBS output
    always @(*) begin
        case(WIDTH)
            8: prbs_out = {lfsr, feedback[0]};
            16: prbs_out = {feedback, lfsr};
            32: prbs_out = {feedback[5:0], lfsr, feedback[4:0], lfsr[4:0], feedback};
            default: prbs_out = {WIDTH{lfsr[0]}};
        endcase
    end

    // LFSR shift
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            lfsr <= 7'b0000001;  // Non-zero initial state
        end else if (enable) begin
            lfsr <= feedback;
        end
    end

endmodule
