// N-bit Reversal Circuit
// Target: LFE5U-25F (ECP5)
// Reverses bit order of input data with configurable width

module bit_reversal #(
    parameter WIDTH = 32
)(
    input                clk,
    input                reset_n,
    input  [WIDTH-1:0]   data_in,
    input                valid_in,
    output reg [WIDTH-1:0] data_out,
    output reg             valid_out
);

    integer i;

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            data_out  <= {WIDTH{1'b0}};
            valid_out <= 1'b0;
        end else begin
            valid_out <= valid_in;
            if (valid_in) begin
                for (i = 0; i < WIDTH; i = i + 1) begin
                    data_out[i] <= data_in[WIDTH - 1 - i];
                end
            end
        end
    end

endmodule
