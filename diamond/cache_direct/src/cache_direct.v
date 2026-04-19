// Direct-Mapped Cache - 4-way, 256 lines x 32-bit
// Target: LFE5U-85F (ECP5)
// Simplified: single-way direct-mapped for simulation

module cache_direct (
    input         clk,
    input         reset_n,
    input  [31:0] addr,
    input  [31:0] wr_data,
    input         rd_en,
    input         wr_en,
    output reg [31:0] rd_data,
    output reg        hit,
    output reg        miss
);

    // Cache parameters: 256 lines, direct-mapped
    // Address: [31:16] tag | [15:8] index | [7:0] ignored (word-aligned)
    localparam LINES     = 256;
    localparam TAG_W     = 16;
    localparam INDEX_W   = 8;

    reg [31:0] data_mem  [0:LINES-1];
    reg [TAG_W-1:0] tag_mem [0:LINES-1];
    reg        valid_mem [0:LINES-1];

    wire [INDEX_W-1:0] index = addr[15:8];
    wire [TAG_W-1:0]   tag   = addr[31:16];

    integer i;

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            rd_data <= 32'd0;
            hit     <= 1'b0;
            miss    <= 1'b0;
            for (i = 0; i < LINES; i = i + 1) begin
                valid_mem[i] <= 1'b0;
                tag_mem[i]   <= {TAG_W{1'b0}};
                data_mem[i]  <= 32'd0;
            end
        end else begin
            hit  <= 1'b0;
            miss <= 1'b0;

            if (wr_en) begin
                data_mem[index]  <= wr_data;
                tag_mem[index]   <= tag;
                valid_mem[index] <= 1'b1;
                hit <= 1'b1;
            end else if (rd_en) begin
                if (valid_mem[index] && tag_mem[index] == tag) begin
                    rd_data <= data_mem[index];
                    hit     <= 1'b1;
                end else begin
                    rd_data <= 32'd0;
                    miss    <= 1'b1;
                end
            end
        end
    end

endmodule
