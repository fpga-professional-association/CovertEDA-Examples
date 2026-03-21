// =============================================================================
// AXI Master Interface (Generic Read/Write)
// =============================================================================

module axi_master #(
    parameter ADDR_WIDTH = 32,
    parameter DATA_WIDTH = 64
) (
    input  wire                     clk,
    input  wire                     rst_n,
    input  wire                     start,
    input  wire [ADDR_WIDTH-1:0]    addr,
    input  wire [15:0]              burst_len,

    // AXI Read Address Channel
    output reg  [ADDR_WIDTH-1:0]    m_axi_araddr,
    output wire [7:0]               m_axi_arlen,
    output wire [2:0]               m_axi_arsize,
    output wire [1:0]               m_axi_arburst,
    output wire                     m_axi_arvalid,
    input  wire                     m_axi_arready,

    // AXI Read Data Channel
    input  wire [DATA_WIDTH-1:0]    m_axi_rdata,
    input  wire [1:0]               m_axi_rresp,
    input  wire                     m_axi_rlast,
    input  wire                     m_axi_rvalid,
    output wire                     m_axi_rready,

    // AXI Write Address Channel
    output reg  [ADDR_WIDTH-1:0]    m_axi_awaddr,
    output wire [7:0]               m_axi_awlen,
    output wire [2:0]               m_axi_awsize,
    output wire [1:0]               m_axi_awburst,
    output wire                     m_axi_awvalid,
    input  wire                     m_axi_awready,

    // AXI Write Data Channel
    output wire [DATA_WIDTH-1:0]    m_axi_wdata,
    output wire [(DATA_WIDTH/8)-1:0] m_axi_wstrb,
    output wire                     m_axi_wlast,
    output wire                     m_axi_wvalid,
    input  wire                     m_axi_wready
);

    reg [ADDR_WIDTH-1:0] addr_r;
    reg [15:0] burst_cnt;
    reg active;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            active <= 1'b0;
            addr_r <= {ADDR_WIDTH{1'b0}};
            burst_cnt <= 16'b0;
        end else begin
            if (start) begin
                active <= 1'b1;
                addr_r <= addr;
                burst_cnt <= 16'b0;
            end else if (m_axi_rvalid && m_axi_rlast) begin
                active <= 1'b0;
            end else if (m_axi_bvalid) begin
                active <= 1'b0;
            end
        end
    end

    // Read Address Channel
    assign m_axi_arvalid = active;
    assign m_axi_arsize = 3'b011;  // 8 bytes (64-bit)
    assign m_axi_arburst = 2'b01;  // INCR
    assign m_axi_arlen = burst_len[7:0] - 1'b1;

    // Read Data Channel
    assign m_axi_rready = 1'b1;

    // Write Address Channel
    assign m_axi_awvalid = active;
    assign m_axi_awsize = 3'b011;
    assign m_axi_awburst = 2'b01;
    assign m_axi_awlen = burst_len[7:0] - 1'b1;

    // Write Data Channel
    assign m_axi_wdata = m_axi_rdata;
    assign m_axi_wstrb = {(DATA_WIDTH/8){1'b1}};
    assign m_axi_wvalid = m_axi_rvalid;
    assign m_axi_wlast = m_axi_rlast;

endmodule
