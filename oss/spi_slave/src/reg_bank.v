// Register Bank

module reg_bank (
    input  clk,
    input  rst_n,
    input  [1:0] addr,
    input  write_en,
    input  [31:0] write_data,
    output [31:0] read_data
);

    reg [31:0] regs [3:0];

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            regs[0] <= 32'h0;
            regs[1] <= 32'h0;
            regs[2] <= 32'h0;
            regs[3] <= 32'h0;
        end else if (write_en) begin
            regs[addr] <= write_data;
        end
    end

    assign read_data = regs[addr];

endmodule
