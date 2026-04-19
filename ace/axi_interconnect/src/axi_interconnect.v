// AXI 2x2 Crossbar Interconnect
// Device: Achronix Speedster7t AC7t1500
// Simple 2-master, 2-slave AXI-Lite crossbar switch

module axi_interconnect #(
    parameter DATA_W = 32,
    parameter ADDR_W = 16
)(
    input  clk,
    input  rst_n,

    // Master 0 interface
    input  [ADDR_W-1:0] m0_addr,
    input  [DATA_W-1:0] m0_wdata,
    input                m0_wen,
    input                m0_ren,
    output [DATA_W-1:0]  m0_rdata,
    output               m0_ready,

    // Master 1 interface
    input  [ADDR_W-1:0] m1_addr,
    input  [DATA_W-1:0] m1_wdata,
    input                m1_wen,
    input                m1_ren,
    output [DATA_W-1:0]  m1_rdata,
    output               m1_ready,

    // Slave 0 interface (address < 0x8000)
    output [ADDR_W-1:0]  s0_addr,
    output [DATA_W-1:0]  s0_wdata,
    output                s0_wen,
    output                s0_ren,
    input  [DATA_W-1:0]  s0_rdata,

    // Slave 1 interface (address >= 0x8000)
    output [ADDR_W-1:0]  s1_addr,
    output [DATA_W-1:0]  s1_wdata,
    output                s1_wen,
    output                s1_ren,
    input  [DATA_W-1:0]  s1_rdata
);

    // Address decode: bit[15] selects slave
    wire m0_sel = m0_addr[ADDR_W-1];
    wire m1_sel = m1_addr[ADDR_W-1];

    // Arbitration: master 0 has priority when both target same slave
    wire m0_active = m0_wen | m0_ren;
    wire m1_active = m1_wen | m1_ren;

    // Conflict: both masters target same slave
    wire conflict_s0 = m0_active & m1_active & ~m0_sel & ~m1_sel;
    wire conflict_s1 = m0_active & m1_active &  m0_sel &  m1_sel;

    // Grant signals (m0 wins conflicts)
    wire m0_grant = m0_active;
    wire m1_grant = m1_active & ~(conflict_s0 | conflict_s1);

    // Slave 0 mux
    wire m0_to_s0 = m0_grant & ~m0_sel;
    wire m1_to_s0 = m1_grant & ~m1_sel;

    assign s0_addr  = m0_to_s0 ? m0_addr  : (m1_to_s0 ? m1_addr  : {ADDR_W{1'b0}});
    assign s0_wdata = m0_to_s0 ? m0_wdata : (m1_to_s0 ? m1_wdata : {DATA_W{1'b0}});
    assign s0_wen   = m0_to_s0 ? m0_wen   : (m1_to_s0 ? m1_wen   : 1'b0);
    assign s0_ren   = m0_to_s0 ? m0_ren   : (m1_to_s0 ? m1_ren   : 1'b0);

    // Slave 1 mux
    wire m0_to_s1 = m0_grant &  m0_sel;
    wire m1_to_s1 = m1_grant &  m1_sel;

    assign s1_addr  = m0_to_s1 ? m0_addr  : (m1_to_s1 ? m1_addr  : {ADDR_W{1'b0}});
    assign s1_wdata = m0_to_s1 ? m0_wdata : (m1_to_s1 ? m1_wdata : {DATA_W{1'b0}});
    assign s1_wen   = m0_to_s1 ? m0_wen   : (m1_to_s1 ? m1_wen   : 1'b0);
    assign s1_ren   = m0_to_s1 ? m0_ren   : (m1_to_s1 ? m1_ren   : 1'b0);

    // Read data mux back to masters
    reg [DATA_W-1:0] m0_rdata_r, m1_rdata_r;
    reg m0_ready_r, m1_ready_r;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            m0_rdata_r <= {DATA_W{1'b0}};
            m1_rdata_r <= {DATA_W{1'b0}};
            m0_ready_r <= 1'b0;
            m1_ready_r <= 1'b0;
        end else begin
            m0_ready_r <= m0_grant;
            m1_ready_r <= m1_grant;
            m0_rdata_r <= m0_sel ? s1_rdata : s0_rdata;
            m1_rdata_r <= m1_sel ? s1_rdata : s0_rdata;
        end
    end

    assign m0_rdata = m0_rdata_r;
    assign m1_rdata = m1_rdata_r;
    assign m0_ready = m0_ready_r;
    assign m1_ready = m1_ready_r;

endmodule
