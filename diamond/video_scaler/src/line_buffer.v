// Line Buffer - Stores one complete video line (1280 pixels x 24-bit color)
// Dual-port RAM for simultaneous read/write

module line_buffer (
    input clk,
    input reset_n,

    // Write port (input line)
    input wr_en,
    input [23:0] wr_data,
    input [9:0] wr_addr,

    // Read port (output line)
    input rd_en,
    output reg [23:0] rd_data,
    input [9:0] rd_addr
);

    // Dual-port RAM: 1280 x 24-bit = 30,720 bits
    // Uses 2 EBR blocks (each 18K bits)
    reg [23:0] line_mem [0:1279];

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            rd_data <= 24'h000000;
        end else begin
            // Read path (synchronous)
            if (rd_en) begin
                rd_data <= line_mem[rd_addr];
            end

            // Write path (synchronous)
            if (wr_en) begin
                line_mem[wr_addr] <= wr_data;
            end
        end
    end

endmodule
