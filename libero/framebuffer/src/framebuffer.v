// 320x240 8-bit Framebuffer with Read Port
// Target: MPF300T (PolarFire)
// Dual-port: write port for CPU, read port for display

module framebuffer (
    input         clk,
    input         reset_n,
    // Write port (CPU side)
    input  [16:0] wr_addr,     // 320*240 = 76800 addresses (17 bits)
    input  [7:0]  wr_data,
    input         wr_en,
    // Read port (display side)
    input  [16:0] rd_addr,
    input         rd_en,
    output reg [7:0] rd_data,
    output reg       rd_valid,
    // Status
    output reg [16:0] pixel_count
);

    // Reduced memory for simulation: 1024 pixels
    localparam MEM_SIZE = 1024;
    localparam ADDR_MASK = MEM_SIZE - 1;

    reg [7:0] fb_mem [0:MEM_SIZE-1];
    integer i;

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            rd_data     <= 8'd0;
            rd_valid    <= 1'b0;
            pixel_count <= 17'd0;
            for (i = 0; i < MEM_SIZE; i = i + 1)
                fb_mem[i] <= 8'd0;
        end else begin
            rd_valid <= 1'b0;

            // Write port
            if (wr_en) begin
                fb_mem[wr_addr & ADDR_MASK] <= wr_data;
                pixel_count <= pixel_count + 1;
            end

            // Read port
            if (rd_en) begin
                rd_data  <= fb_mem[rd_addr & ADDR_MASK];
                rd_valid <= 1'b1;
            end
        end
    end

endmodule
