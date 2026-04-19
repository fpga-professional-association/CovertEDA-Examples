// =============================================================================
// 256x32 True Dual-Port RAM
// Device: Xilinx Artix-7 XC7A200T
// =============================================================================

module dpram (
    // Port A
    input  wire        clk_a,
    input  wire        en_a,
    input  wire        we_a,
    input  wire [7:0]  addr_a,
    input  wire [31:0] din_a,
    output reg  [31:0] dout_a,

    // Port B
    input  wire        clk_b,
    input  wire        en_b,
    input  wire        we_b,
    input  wire [7:0]  addr_b,
    input  wire [31:0] din_b,
    output reg  [31:0] dout_b
);

    // Memory array
    reg [31:0] mem [0:255];

    // Port A logic
    always @(posedge clk_a) begin
        if (en_a) begin
            if (we_a) begin
                mem[addr_a] <= din_a;
            end
            dout_a <= mem[addr_a];
        end
    end

    // Port B logic
    always @(posedge clk_b) begin
        if (en_b) begin
            if (we_b) begin
                mem[addr_b] <= din_b;
            end
            dout_b <= mem[addr_b];
        end
    end

endmodule
