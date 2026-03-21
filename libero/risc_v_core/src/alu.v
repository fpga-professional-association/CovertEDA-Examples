// ALU for RV32I Core

module alu (
    input  [31:0] a,
    input  [31:0] b,
    input  [31:0] imm,
    input  [3:0]  alu_op,
    input  [1:0]  alu_src_b,
    output [31:0] result
);

    reg [31:0] operand_b;
    reg [31:0] alu_result;

    always @* begin
        case (alu_src_b)
            2'b00: operand_b = b;
            2'b01: operand_b = imm;
            default: operand_b = 32'h0;
        endcase
    end

    always @* begin
        case (alu_op)
            4'b0000: alu_result = a + operand_b;          // ADD/ADDI
            4'b0001: alu_result = a - operand_b;          // SUB
            4'b0010: alu_result = a & operand_b;          // AND
            4'b0011: alu_result = a | operand_b;          // OR
            4'b0100: alu_result = a ^ operand_b;          // XOR
            4'b0101: alu_result = a << operand_b[4:0];    // SLL
            4'b0110: alu_result = a >> operand_b[4:0];    // SRL
            4'b0111: alu_result = $signed(a) >>> operand_b[4:0]; // SRA
            4'b1000: alu_result = (a < operand_b) ? 32'h1 : 32'h0; // SLT
            4'b1001: alu_result = (a == operand_b) ? 32'h1 : 32'h0; // BEQ
            4'b1010: alu_result = (a != operand_b) ? 32'h1 : 32'h0; // BNE
            4'b1011: alu_result = (a >= operand_b) ? 32'h1 : 32'h0; // BGE
            default: alu_result = 32'h0;
        endcase
    end

    assign result = alu_result;

endmodule
