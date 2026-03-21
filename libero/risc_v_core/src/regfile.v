// Register File for RV32I Core

module regfile (
    input  clk,
    input  rst_n,
    input  [4:0]  rs1,
    input  [4:0]  rs2,
    input  [4:0]  rd,
    input  [31:0] write_data,
    input         reg_write,
    output [31:0] reg_rs1,
    output [31:0] reg_rs2,
    output [31:0] x1_debug
);

    reg [31:0] registers [31:0];
    integer i;

    // Initialize registers
    initial begin
        for (i = 0; i < 32; i = i + 1)
            registers[i] = 32'h0;
    end

    // Read operations (combinational)
    assign reg_rs1 = (rs1 == 5'h0) ? 32'h0 : registers[rs1];
    assign reg_rs2 = (rs2 == 5'h0) ? 32'h0 : registers[rs2];
    assign x1_debug = registers[1];

    // Write operation (sequential)
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (i = 0; i < 32; i = i + 1)
                registers[i] <= 32'h0;
        end else if (reg_write && (rd != 5'h0)) begin
            registers[rd] <= write_data;
        end
    end

endmodule
