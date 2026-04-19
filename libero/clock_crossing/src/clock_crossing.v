// CDC Synchronizer with Gray-code FIFO
// Target: MPF100T (PolarFire)
// Async FIFO using gray-code pointers for clock domain crossing

module clock_crossing #(
    parameter WIDTH = 8,
    parameter DEPTH = 8   // must be power of 2
)(
    // Write domain
    input              wr_clk,
    input              wr_reset_n,
    input  [WIDTH-1:0] wr_data,
    input              wr_en,
    output reg         wr_full,
    // Read domain
    input              rd_clk,
    input              rd_reset_n,
    output reg [WIDTH-1:0] rd_data,
    input              rd_en,
    output reg         rd_empty
);

    localparam ADDR_W = $clog2(DEPTH);

    reg [WIDTH-1:0] mem [0:DEPTH-1];

    // Write domain
    reg [ADDR_W:0] wr_ptr_bin, wr_ptr_gray;
    reg [ADDR_W:0] rd_ptr_gray_sync1, rd_ptr_gray_sync2;

    // Read domain
    reg [ADDR_W:0] rd_ptr_bin, rd_ptr_gray;
    reg [ADDR_W:0] wr_ptr_gray_sync1, wr_ptr_gray_sync2;

    // Binary to gray conversion
    function [ADDR_W:0] bin2gray;
        input [ADDR_W:0] bin;
        begin
            bin2gray = bin ^ (bin >> 1);
        end
    endfunction

    // Write logic
    always @(posedge wr_clk or negedge wr_reset_n) begin
        if (!wr_reset_n) begin
            wr_ptr_bin  <= 0;
            wr_ptr_gray <= 0;
            rd_ptr_gray_sync1 <= 0;
            rd_ptr_gray_sync2 <= 0;
            wr_full <= 0;
        end else begin
            // Synchronize rd_ptr to wr domain
            rd_ptr_gray_sync1 <= rd_ptr_gray;
            rd_ptr_gray_sync2 <= rd_ptr_gray_sync1;

            if (wr_en && !wr_full) begin
                mem[wr_ptr_bin[ADDR_W-1:0]] <= wr_data;
                wr_ptr_bin  <= wr_ptr_bin + 1;
                wr_ptr_gray <= bin2gray(wr_ptr_bin + 1);
            end

            // Full: MSBs differ, rest equal (in gray code)
            wr_full <= (bin2gray(wr_ptr_bin + (wr_en && !wr_full ? 1 : 0)) ==
                       {~rd_ptr_gray_sync2[ADDR_W:ADDR_W-1],
                        rd_ptr_gray_sync2[ADDR_W-2:0]});
        end
    end

    // Read logic
    always @(posedge rd_clk or negedge rd_reset_n) begin
        if (!rd_reset_n) begin
            rd_ptr_bin  <= 0;
            rd_ptr_gray <= 0;
            wr_ptr_gray_sync1 <= 0;
            wr_ptr_gray_sync2 <= 0;
            rd_empty <= 1;
            rd_data  <= 0;
        end else begin
            // Synchronize wr_ptr to rd domain
            wr_ptr_gray_sync1 <= wr_ptr_gray;
            wr_ptr_gray_sync2 <= wr_ptr_gray_sync1;

            if (rd_en && !rd_empty) begin
                rd_data     <= mem[rd_ptr_bin[ADDR_W-1:0]];
                rd_ptr_bin  <= rd_ptr_bin + 1;
                rd_ptr_gray <= bin2gray(rd_ptr_bin + 1);
            end

            // Empty: pointers equal in gray code
            rd_empty <= (bin2gray(rd_ptr_bin + (rd_en && !rd_empty ? 1 : 0)) ==
                        wr_ptr_gray_sync2);
        end
    end

endmodule
