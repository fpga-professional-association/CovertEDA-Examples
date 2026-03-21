// Data Checker

module data_checker (
    input  clk,
    input  rst_n,
    input  [255:0] expected,
    input  [255:0] actual,
    input  valid,
    output [31:0] result
);

    reg [31:0] error_count;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            error_count <= 32'h0;
        end else if (valid && (expected != actual)) begin
            error_count <= error_count + 1'b1;
        end
    end

    assign result = error_count;

endmodule
