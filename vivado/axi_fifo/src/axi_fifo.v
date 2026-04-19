// =============================================================================
// AXI4-Stream FIFO, 32-bit Width, 16-deep
// Device: Xilinx Zynq-7000 XC7Z020
// =============================================================================

module axi_fifo (
    input  wire        clk,
    input  wire        rst_n,

    // AXI4-Stream Slave (input)
    input  wire [31:0] s_axis_tdata,
    input  wire        s_axis_tvalid,
    output wire        s_axis_tready,
    input  wire        s_axis_tlast,

    // AXI4-Stream Master (output)
    output wire [31:0] m_axis_tdata,
    output wire        m_axis_tvalid,
    input  wire        m_axis_tready,
    output wire        m_axis_tlast,

    // Status
    output wire [4:0]  fill_level
);

    parameter DEPTH = 16;
    parameter ADDR_W = 4;

    reg [32:0] mem [0:DEPTH-1];  // 32 data + 1 tlast
    reg [ADDR_W:0] wr_ptr;
    reg [ADDR_W:0] rd_ptr;

    wire [ADDR_W:0] count;
    assign count = wr_ptr - rd_ptr;
    assign fill_level = count[4:0];

    wire full  = (count == DEPTH);
    wire empty = (count == 0);

    // Slave interface
    assign s_axis_tready = !full;

    // Master interface
    assign m_axis_tvalid = !empty;
    assign m_axis_tdata  = mem[rd_ptr[ADDR_W-1:0]][31:0];
    assign m_axis_tlast  = mem[rd_ptr[ADDR_W-1:0]][32];

    // Write logic
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            wr_ptr <= 0;
        end else if (s_axis_tvalid && s_axis_tready) begin
            mem[wr_ptr[ADDR_W-1:0]] <= {s_axis_tlast, s_axis_tdata};
            wr_ptr <= wr_ptr + 1;
        end
    end

    // Read logic
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            rd_ptr <= 0;
        end else if (m_axis_tvalid && m_axis_tready) begin
            rd_ptr <= rd_ptr + 1;
        end
    end

endmodule
