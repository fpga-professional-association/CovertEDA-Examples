// Instruction Decoder for RV32I

module decoder (
    input  [31:0] instruction,
    output [6:0]  opcode,
    output [4:0]  rd,
    output [4:0]  rs1,
    output [4:0]  rs2,
    output [2:0]  func3,
    output [6:0]  func7,
    output [31:0] immediate
);

    // Instruction field extraction
    assign opcode = instruction[6:0];
    assign rd = instruction[11:7];
    assign func3 = instruction[14:12];
    assign rs1 = instruction[19:15];
    assign rs2 = instruction[24:20];
    assign func7 = instruction[31:25];

    // Immediate generation based on instruction type
    wire is_r_type = (opcode == 7'b0110011);
    wire is_i_type = (opcode == 7'b0010011) || (opcode == 7'b0000011);
    wire is_s_type = (opcode == 7'b0100011);
    wire is_b_type = (opcode == 7'b1100011);
    wire is_u_type = (opcode == 7'b0110111);
    wire is_j_type = (opcode == 7'b1101111);

    reg [31:0] imm;

    always @* begin
        if (is_i_type || is_r_type) begin
            // I-type: sign-extend 12-bit immediate
            imm = {{20{instruction[31]}}, instruction[31:20]};
        end else if (is_s_type) begin
            // S-type: sign-extend from [31:25][11:7]
            imm = {{20{instruction[31]}}, instruction[31:25], instruction[11:7]};
        end else if (is_b_type) begin
            // B-type: sign-extend from [31], [7], [30:25], [11:8]
            imm = {{20{instruction[31]}}, instruction[7], instruction[30:25], instruction[11:8], 1'b0};
        end else if (is_u_type) begin
            // U-type: immediate in [31:12]
            imm = {instruction[31:12], 12'h0};
        end else if (is_j_type) begin
            // J-type: sign-extend from [31], [19:12], [20], [30:21]
            imm = {{12{instruction[31]}}, instruction[19:12], instruction[20], instruction[30:21], 1'b0};
        end else begin
            imm = 32'h0;
        end
    end

    assign immediate = imm;

endmodule
