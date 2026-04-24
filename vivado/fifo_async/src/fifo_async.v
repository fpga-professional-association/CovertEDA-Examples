// =============================================================================
// 16-deep x 8-bit Asynchronous FIFO with Dual Clocks
// Device: Xilinx Kintex-7 XC7K325T
// Uses Gray-code pointers for safe CDC
// =============================================================================

module fifo_async (
    // Write domain
    input  wire       wr_clk,
    input  wire       wr_rst_n,
    input  wire [7:0] wr_data,
    input  wire       wr_en,
    output wire       full,

    // Read domain
    input  wire       rd_clk,
    input  wire       rd_rst_n,
    output wire [7:0] rd_data,
    input  wire       rd_en,
    output wire       empty
);

    parameter DEPTH = 16;
    parameter ADDR_W = 4;

    // Memory
    reg [7:0] mem [0:DEPTH-1];

    // Write pointer (binary and gray)
    reg [ADDR_W:0] wr_ptr_bin;
    wire [ADDR_W:0] wr_ptr_gray;

    // Read pointer (binary and gray)
    reg [ADDR_W:0] rd_ptr_bin;
    wire [ADDR_W:0] rd_ptr_gray;

    // Synchronized pointers
    reg [ADDR_W:0] wr_ptr_gray_sync1, wr_ptr_gray_sync2;
    reg [ADDR_W:0] rd_ptr_gray_sync1, rd_ptr_gray_sync2;

    // Binary to Gray conversion
    assign wr_ptr_gray = wr_ptr_bin ^ (wr_ptr_bin >> 1);
    assign rd_ptr_gray = rd_ptr_bin ^ (rd_ptr_bin >> 1);

    // Write logic
    always @(posedge wr_clk or negedge wr_rst_n) begin
        if (!wr_rst_n) begin
            wr_ptr_bin <= 0;
        end else if (wr_en && !full) begin
            mem[wr_ptr_bin[ADDR_W-1:0]] <= wr_data;
            wr_ptr_bin <= wr_ptr_bin + 1;
        end
    end

    // Read logic
    always @(posedge rd_clk or negedge rd_rst_n) begin
        if (!rd_rst_n) begin
            rd_ptr_bin <= 0;
        end else if (rd_en && !empty) begin
            rd_ptr_bin <= rd_ptr_bin + 1;
        end
    end

    assign rd_data = mem[rd_ptr_bin[ADDR_W-1:0]];

    // Synchronize read pointer into write domain
    always @(posedge wr_clk or negedge wr_rst_n) begin
        if (!wr_rst_n) begin
            rd_ptr_gray_sync1 <= 0;
            rd_ptr_gray_sync2 <= 0;
        end else begin
            rd_ptr_gray_sync1 <= rd_ptr_gray;
            rd_ptr_gray_sync2 <= rd_ptr_gray_sync1;
        end
    end

    // Synchronize write pointer into read domain
    always @(posedge rd_clk or negedge rd_rst_n) begin
        if (!rd_rst_n) begin
            wr_ptr_gray_sync1 <= 0;
            wr_ptr_gray_sync2 <= 0;
        end else begin
            wr_ptr_gray_sync1 <= wr_ptr_gray;
            wr_ptr_gray_sync2 <= wr_ptr_gray_sync1;
        end
    end

    // Full: write pointer gray == inverted MSBs of synced read pointer gray
    assign full = (wr_ptr_gray == {~rd_ptr_gray_sync2[ADDR_W:ADDR_W-1],
                                     rd_ptr_gray_sync2[ADDR_W-2:0]});

    // Empty: read pointer gray == synced write pointer gray
    assign empty = (rd_ptr_gray == wr_ptr_gray_sync2);

endmodule
