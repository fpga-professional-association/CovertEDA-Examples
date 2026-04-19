// =============================================================================
// Design      : Synchronous FIFO
// Module      : fifo_sync
// Description : 8-deep x 8-bit synchronous FIFO with full/empty flags
// Device      : LIFCL-40-7BG400I
// Frequency   : 25 MHz
// =============================================================================

module fifo_sync #(
    parameter DATA_WIDTH = 8,
    parameter ADDR_WIDTH = 3           // 2^3 = 8 deep
)(
    input   wire                    clk,
    input   wire                    rst_n,
    input   wire                    wr_en,
    input   wire                    rd_en,
    input   wire [DATA_WIDTH-1:0]   wr_data,
    output  reg  [DATA_WIDTH-1:0]   rd_data,
    output  wire                    full,
    output  wire                    empty,
    output  wire [ADDR_WIDTH:0]     count       // Number of entries
);

    localparam DEPTH = 1 << ADDR_WIDTH;

    reg [DATA_WIDTH-1:0] mem [0:DEPTH-1];
    reg [ADDR_WIDTH:0]   wr_ptr;
    reg [ADDR_WIDTH:0]   rd_ptr;

    wire [ADDR_WIDTH:0] next_count;

    assign count = wr_ptr - rd_ptr;
    assign full  = (count == DEPTH);
    assign empty = (count == 0);

    // Write logic
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            wr_ptr <= 0;
        end else if (wr_en && !full) begin
            mem[wr_ptr[ADDR_WIDTH-1:0]] <= wr_data;
            wr_ptr <= wr_ptr + 1;
        end
    end

    // Read logic
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            rd_ptr  <= 0;
            rd_data <= {DATA_WIDTH{1'b0}};
        end else if (rd_en && !empty) begin
            rd_data <= mem[rd_ptr[ADDR_WIDTH-1:0]];
            rd_ptr  <= rd_ptr + 1;
        end
    end

endmodule
