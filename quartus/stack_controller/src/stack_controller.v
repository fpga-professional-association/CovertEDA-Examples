// Stack Controller - 16-deep x 32-bit hardware stack
// Quartus / Cyclone IV E (EP4CE6)

module stack_controller (
    input         clk,
    input         rst_n,
    input         push,
    input         pop,
    input  [31:0] din,
    output [31:0] dout,
    output        full,
    output        empty,
    output [4:0]  depth
);

    reg [31:0] stack_mem [0:15];
    reg [4:0]  sp;  // stack pointer (0 = empty, 16 = full)

    reg [31:0] dout_reg;

    assign dout  = dout_reg;
    assign full  = (sp == 5'd16);
    assign empty = (sp == 5'd0);
    assign depth = sp;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sp       <= 5'd0;
            dout_reg <= 32'd0;
        end else begin
            if (push && !full && !(pop && !empty)) begin
                // Push only
                stack_mem[sp[3:0]] <= din;
                sp <= sp + 5'd1;
            end else if (pop && !empty && !(push && !full)) begin
                // Pop only
                sp <= sp - 5'd1;
                dout_reg <= stack_mem[sp - 5'd1];
            end else if (push && !full && pop && !empty) begin
                // Simultaneous push and pop: replace top
                stack_mem[sp - 5'd1] <= din;
                dout_reg <= stack_mem[sp - 5'd1];
            end
        end
    end

endmodule
