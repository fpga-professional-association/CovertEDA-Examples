// MAC Array for ML Accelerator

module mac_array (
    input  clk,
    input  rst_n,
    input  [31:0] in_data,
    input  in_valid,
    output [31:0] result,
    output result_valid
);

    reg [31:0] accum;
    reg valid;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            accum <= 32'h0;
            valid <= 1'b0;
        end else if (in_valid) begin
            accum <= accum + in_data;
            valid <= 1'b1;
        end else begin
            valid <= 1'b0;
        end
    end

    assign result = accum;
    assign result_valid = valid;

endmodule
