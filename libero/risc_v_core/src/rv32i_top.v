// RV32I Simple RISC-V Core Top Module
// Device: MPFS250T-FCVG484I (PolarFire SoC)
// Instruction Set: RV32I Base Integer

module rv32i_top (
    input  clk,
    input  rst_n,

    // Instruction Memory Interface
    output [31:0] imem_addr,
    input  [31:0] imem_data,

    // Data Memory Interface
    output [31:0] dmem_addr,
    output [31:0] dmem_data_out,
    input  [31:0] dmem_data_in,
    output        dmem_we,

    // Debug signals
    output [31:0] pc_debug,
    output [31:0] reg_x1_debug
);

    // Internal signals
    wire [31:0] pc;
    wire [31:0] pc_next;
    wire [31:0] instruction;
    wire [31:0] alu_result;
    wire [31:0] reg_rs1;
    wire [31:0] reg_rs2;
    wire [31:0] immediate;

    // Control signals
    wire [3:0] alu_op;
    wire reg_write;
    wire mem_write;
    wire mem_read;
    wire [1:0] alu_src_a;
    wire [1:0] alu_src_b;
    wire pc_src;

    // Instruction fields
    wire [6:0] opcode;
    wire [4:0] rd, rs1, rs2;
    wire [2:0] func3;
    wire [6:0] func7;

    // PC Unit
    pc_unit pc_inst (
        .clk(clk),
        .rst_n(rst_n),
        .pc_next(pc_next),
        .pc(pc)
    );

    // Instruction decoder
    decoder decoder_inst (
        .instruction(instruction),
        .opcode(opcode),
        .rd(rd),
        .rs1(rs1),
        .rs2(rs2),
        .func3(func3),
        .func7(func7),
        .immediate(immediate)
    );

    // Register file
    regfile regfile_inst (
        .clk(clk),
        .rst_n(rst_n),
        .rs1(rs1),
        .rs2(rs2),
        .rd(rd),
        .write_data(alu_result),
        .reg_write(reg_write),
        .reg_rs1(reg_rs1),
        .reg_rs2(reg_rs2),
        .x1_debug(reg_x1_debug)
    );

    // ALU
    alu alu_inst (
        .a(reg_rs1),
        .b(reg_rs2),
        .imm(immediate),
        .alu_op(alu_op),
        .alu_src_b(alu_src_b),
        .result(alu_result)
    );

    // Simple control logic
    always @* begin
        case (opcode)
            7'b0110011: begin  // R-type
                alu_op = {func7[5], func3};
                reg_write = 1'b1;
                mem_write = 1'b0;
                alu_src_a = 2'b00;
                alu_src_b = 2'b00;
                pc_src = 1'b0;
            end
            7'b0010011: begin  // I-type
                alu_op = {1'b0, func3};
                reg_write = 1'b1;
                mem_write = 1'b0;
                alu_src_a = 2'b00;
                alu_src_b = 2'b01;
                pc_src = 1'b0;
            end
            7'b0000011: begin  // Load
                alu_op = 4'b0000;
                reg_write = 1'b1;
                mem_write = 1'b0;
                alu_src_a = 2'b00;
                alu_src_b = 2'b01;
                pc_src = 1'b0;
            end
            7'b0100011: begin  // Store
                alu_op = 4'b0000;
                reg_write = 1'b0;
                mem_write = 1'b1;
                alu_src_a = 2'b00;
                alu_src_b = 2'b01;
                pc_src = 1'b0;
            end
            7'b1100011: begin  // Branch
                alu_op = {1'b1, func3};
                reg_write = 1'b0;
                mem_write = 1'b0;
                alu_src_a = 2'b00;
                alu_src_b = 2'b00;
                pc_src = (alu_result[0]);
            end
            default: begin
                alu_op = 4'b0000;
                reg_write = 1'b0;
                mem_write = 1'b0;
                alu_src_a = 2'b00;
                alu_src_b = 2'b00;
                pc_src = 1'b0;
            end
        endcase
    end

    // Next PC calculation
    assign pc_next = pc_src ? (pc + immediate) : (pc + 4);

    // Memory assignments
    assign imem_addr = pc;
    assign instruction = imem_data;
    assign dmem_addr = alu_result;
    assign dmem_data_out = reg_rs2;
    assign dmem_we = mem_write;

    // Debug outputs
    assign pc_debug = pc;

endmodule
