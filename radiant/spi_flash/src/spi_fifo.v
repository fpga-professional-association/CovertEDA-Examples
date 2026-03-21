// =============================================================================
// Module: spi_fifo
// Description: Synchronous FIFO for SPI command/data buffering (256 entries)
// =============================================================================

module spi_fifo (
    input   wire        clk,        // System clock
    input   wire        rst_n,      // Reset
    input   wire        wr_en,      // Write enable
    input   wire        rd_en,      // Read enable
    input   wire [15:0] data_in,    // Write data
    output  wire [15:0] data_out,   // Read data
    output  wire        empty,      // Empty flag
    output  wire        full        // Full flag
);

    parameter DEPTH = 256;
    parameter ADDR_WIDTH = 8;

    reg [15:0] memory[0:DEPTH-1];
    reg [ADDR_WIDTH:0] wr_ptr;
    reg [ADDR_WIDTH:0] rd_ptr;

    assign empty = (wr_ptr == rd_ptr);
    assign full = (wr_ptr[ADDR_WIDTH-1:0] == rd_ptr[ADDR_WIDTH-1:0]) &&
                  (wr_ptr[ADDR_WIDTH] != rd_ptr[ADDR_WIDTH]);

    assign data_out = memory[rd_ptr[ADDR_WIDTH-1:0]];

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            wr_ptr <= {(ADDR_WIDTH+1){1'b0}};
            rd_ptr <= {(ADDR_WIDTH+1){1'b0}};
        end else begin
            if (wr_en && !full) begin
                memory[wr_ptr[ADDR_WIDTH-1:0]] <= data_in;
                wr_ptr <= wr_ptr + 1'b1;
            end

            if (rd_en && !empty) begin
                rd_ptr <= rd_ptr + 1'b1;
            end
        end
    end

endmodule
