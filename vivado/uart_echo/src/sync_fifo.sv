// =============================================================================
// Synchronous FIFO Module (Single-Clock Domain)
// =============================================================================

module sync_fifo #(
    parameter WIDTH = 8,
    parameter DEPTH = 512,
    parameter ADDR_WIDTH = $clog2(DEPTH)
) (
    input  wire                 clk,
    input  wire                 rst_n,
    input  wire [WIDTH-1:0]     din,
    input  wire                 wr_en,
    output wire [WIDTH-1:0]     dout,
    input  wire                 rd_en,
    output wire                 empty,
    output wire                 full,
    output wire                 almost_full,
    output wire [ADDR_WIDTH:0]  count
);

    // Memory array
    reg [WIDTH-1:0] mem [0:DEPTH-1];

    // Pointers (with extra bit for distinguishing full vs. empty)
    reg [ADDR_WIDTH:0] wr_ptr;
    reg [ADDR_WIDTH:0] rd_ptr;
    wire [ADDR_WIDTH:0] wr_ptr_next;
    wire [ADDR_WIDTH:0] rd_ptr_next;

    // Control signals
    wire wr_valid = wr_en & ~full;
    wire rd_valid = rd_en & ~empty;

    assign wr_ptr_next = wr_ptr + (wr_valid ? 1'b1 : 1'b0);
    assign rd_ptr_next = rd_ptr + (rd_valid ? 1'b1 : 1'b0);

    // Empty and full generation
    assign empty = (wr_ptr == rd_ptr);
    assign full = (wr_ptr_next[ADDR_WIDTH] != rd_ptr[ADDR_WIDTH]) &&
                  (wr_ptr_next[ADDR_WIDTH-1:0] == rd_ptr[ADDR_WIDTH-1:0]);

    // Almost full (< 2 words remaining)
    wire [ADDR_WIDTH:0] count_next = (wr_ptr >= rd_ptr) ?
                                       (wr_ptr - rd_ptr) :
                                       (DEPTH - (rd_ptr - wr_ptr));
    assign almost_full = (count_next >= (DEPTH - 2));

    // Current count
    assign count = (wr_ptr >= rd_ptr) ? (wr_ptr - rd_ptr) :
                   ({1'b1, {ADDR_WIDTH{1'b0}}} - (rd_ptr - wr_ptr));

    // Data output
    assign dout = mem[rd_ptr[ADDR_WIDTH-1:0]];

    // Write and read operations
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            wr_ptr <= {(ADDR_WIDTH+1){1'b0}};
            rd_ptr <= {(ADDR_WIDTH+1){1'b0}};
        end else begin
            // Write operation
            if (wr_valid) begin
                mem[wr_ptr[ADDR_WIDTH-1:0]] <= din;
                wr_ptr <= wr_ptr_next;
            end

            // Read operation
            if (rd_valid) begin
                rd_ptr <= rd_ptr_next;
            end
        end
    end

endmodule
