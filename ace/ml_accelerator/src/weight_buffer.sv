// Weight Buffer for ML Accelerator

module weight_buffer (
    input  clk,
    input  rst_n,
    input  [31:0] weight_in,
    input  weight_valid,
    output [31:0] weight_out,
    output weight_ready
);

    reg [31:0] weight_mem [127:0];
    reg [7:0] wr_ptr, rd_ptr;
    reg ready;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            wr_ptr <= 8'h0;
            rd_ptr <= 8'h0;
            ready <= 1'b1;
        end else if (weight_valid && ready) begin
            weight_mem[wr_ptr] <= weight_in;
            wr_ptr <= wr_ptr + 1'b1;
            ready <= (wr_ptr != rd_ptr);
        end
    end

    assign weight_out = weight_mem[rd_ptr];
    assign weight_ready = ready;

endmodule
