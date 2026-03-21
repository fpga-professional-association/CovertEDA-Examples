// Activation Function for ML Accelerator

module activation (
    input  clk,
    input  rst_n,
    input  [31:0] in_data,
    input  in_valid,
    output [31:0] out_data,
    output out_valid
);

    reg [31:0] activated;
    reg valid;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            activated <= 32'h0;
            valid <= 1'b0;
        end else if (in_valid) begin
            activated <= (in_data[31]) ? 32'h0 : in_data;
            valid <= 1'b1;
        end else begin
            valid <= 1'b0;
        end
    end

    assign out_data = activated;
    assign out_valid = valid;

endmodule
