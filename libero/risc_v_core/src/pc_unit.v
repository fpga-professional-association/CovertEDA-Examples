// Program Counter Unit

module pc_unit (
    input  clk,
    input  rst_n,
    input  [31:0] pc_next,
    output [31:0] pc
);

    reg [31:0] pc_reg;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            pc_reg <= 32'h0;
        end else begin
            pc_reg <= pc_next;
        end
    end

    assign pc = pc_reg;

endmodule
