// =============================================================================
// AXI DMA Engine with Scatter-Gather Support
// Device: Xilinx Kintex-7 XC7K325T-2FFG900C
// Clock: 250 MHz
// =============================================================================

module dma_top (
    input  wire         clk,
    input  wire         rst_n,

    // AXI Master (Read Channel)
    output wire [31:0]  m_axi_araddr,
    output wire [7:0]   m_axi_arlen,
    output wire [2:0]   m_axi_arsize,
    output wire [1:0]   m_axi_arburst,
    output wire         m_axi_arvalid,
    input  wire         m_axi_arready,

    input  wire [63:0]  m_axi_rdata,
    input  wire [1:0]   m_axi_rresp,
    input  wire         m_axi_rlast,
    input  wire         m_axi_rvalid,
    output wire         m_axi_rready,

    // AXI Master (Write Channel)
    output wire [31:0]  m_axi_awaddr,
    output wire [7:0]   m_axi_awlen,
    output wire [2:0]   m_axi_awsize,
    output wire [1:0]   m_axi_awburst,
    output wire         m_axi_awvalid,
    input  wire         m_axi_awready,

    output wire [63:0]  m_axi_wdata,
    output wire [7:0]   m_axi_wstrb,
    output wire         m_axi_wlast,
    output wire         m_axi_wvalid,
    input  wire         m_axi_wready,

    input  wire [1:0]   m_axi_bresp,
    input  wire         m_axi_bvalid,
    output wire         m_axi_bready,

    // AXI Slave (Control)
    input  wire [31:0]  s_axi_awaddr,
    input  wire         s_axi_awvalid,
    output wire         s_axi_awready,

    input  wire [31:0]  s_axi_wdata,
    input  wire [3:0]   s_axi_wstrb,
    input  wire         s_axi_wvalid,
    output wire         s_axi_wready,

    output wire [1:0]   s_axi_bresp,
    output wire         s_axi_bvalid,
    input  wire         s_axi_bready,

    input  wire [31:0]  s_axi_araddr,
    input  wire         s_axi_arvalid,
    output wire         s_axi_arready,

    output wire [31:0]  s_axi_rdata,
    output wire [1:0]   s_axi_rresp,
    output wire         s_axi_rvalid,
    input  wire         s_axi_rready,

    // Interrupt
    output wire         dma_interrupt
);

    // ---- Register File ----
    reg [31:0] src_addr;
    reg [31:0] dst_addr;
    reg [31:0] xfer_len;
    reg [7:0]  xfer_control;  // [0]=start, [1]=done, [2]=error
    reg [31:0] sg_ptr;
    reg sg_enable;

    // ---- Status Signals ----
    reg dma_busy;
    reg transfer_done;
    reg transfer_error;

    // ---- Scatter-Gather Engine ----
    wire sg_valid;
    wire [31:0] sg_src_addr;
    wire [31:0] sg_dst_addr;
    wire [31:0] sg_length;

    sg_engine sg_inst (
        .clk(clk),
        .rst_n(rst_n),
        .enable(sg_enable),
        .sg_ptr(sg_ptr),
        .sg_valid(sg_valid),
        .src_addr(sg_src_addr),
        .dst_addr(sg_dst_addr),
        .length(sg_length)
    );

    // ---- AXI Master (read path) ----
    wire read_en;
    wire [31:0] read_addr;
    wire [15:0] read_burst_len;

    axi_master #(.ADDR_WIDTH(32), .DATA_WIDTH(64)) axi_read (
        .clk(clk),
        .rst_n(rst_n),
        .start(read_en),
        .addr(read_addr),
        .burst_len(read_burst_len),
        .m_axi_araddr(m_axi_araddr),
        .m_axi_arlen(m_axi_arlen),
        .m_axi_arsize(m_axi_arsize),
        .m_axi_arburst(m_axi_arburst),
        .m_axi_arvalid(m_axi_arvalid),
        .m_axi_arready(m_axi_arready),
        .m_axi_rdata(m_axi_rdata),
        .m_axi_rresp(m_axi_rresp),
        .m_axi_rlast(m_axi_rlast),
        .m_axi_rvalid(m_axi_rvalid),
        .m_axi_rready(m_axi_rready)
    );

    // ---- AXI Master (write path) ----
    wire write_en;
    wire [31:0] write_addr;
    wire [15:0] write_burst_len;

    axi_master #(.ADDR_WIDTH(32), .DATA_WIDTH(64)) axi_write (
        .clk(clk),
        .rst_n(rst_n),
        .start(write_en),
        .addr(write_addr),
        .burst_len(write_burst_len),
        .m_axi_awaddr(m_axi_awaddr),
        .m_axi_awlen(m_axi_awlen),
        .m_axi_awsize(m_axi_awsize),
        .m_axi_awburst(m_axi_awburst),
        .m_axi_awvalid(m_axi_awvalid),
        .m_axi_awready(m_axi_awready),
        .m_axi_wdata(m_axi_wdata),
        .m_axi_wstrb(m_axi_wstrb),
        .m_axi_wlast(m_axi_wlast),
        .m_axi_wvalid(m_axi_wvalid),
        .m_axi_wready(m_axi_wready)
    );

    // ---- DMA Control FSM ----
    reg [2:0] state;
    localparam IDLE = 3'b000, SG_FETCH = 3'b001, READ = 3'b010, WRITE = 3'b011, DONE = 3'b100;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            dma_busy <= 1'b0;
            transfer_done <= 1'b0;
            transfer_error <= 1'b0;
        end else begin
            case (state)
                IDLE: begin
                    if (xfer_control[0]) begin  // Start bit
                        if (sg_enable) begin
                            state <= SG_FETCH;
                        end else begin
                            state <= READ;
                        end
                        dma_busy <= 1'b1;
                    end
                end

                SG_FETCH: begin
                    if (sg_valid) begin
                        state <= READ;
                    end
                end

                READ: begin
                    if (m_axi_rvalid && m_axi_rlast) begin
                        state <= WRITE;
                    end
                end

                WRITE: begin
                    if (m_axi_bvalid) begin
                        state <= DONE;
                    end
                end

                DONE: begin
                    dma_busy <= 1'b0;
                    transfer_done <= 1'b1;
                    state <= IDLE;
                end
            endcase
        end
    end

    // ---- AXI Slave Interface (Control) ----
    reg aw_en;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            aw_en <= 1'b1;
            src_addr <= 32'h0;
            dst_addr <= 32'h0;
            xfer_len <= 32'h0;
            sg_ptr <= 32'h0;
            sg_enable <= 1'b0;
        end else begin
            // Write
            if (s_axi_awvalid && s_axi_awready) begin
                aw_en <= 1'b0;
            end
            if (s_axi_bvalid && s_axi_bready) begin
                aw_en <= 1'b1;
            end

            if (s_axi_wvalid && s_axi_wready) begin
                case (s_axi_awaddr[5:2])
                    4'h0: src_addr <= s_axi_wdata;
                    4'h1: dst_addr <= s_axi_wdata;
                    4'h2: xfer_len <= s_axi_wdata;
                    4'h3: xfer_control <= s_axi_wdata[7:0];
                    4'h4: sg_ptr <= s_axi_wdata;
                    4'h5: sg_enable <= s_axi_wdata[0];
                    default: ;
                endcase
            end
        end
    end

    assign s_axi_awready = s_axi_awvalid && aw_en;
    assign s_axi_wready = s_axi_wvalid;
    assign s_axi_bresp = 2'b00;
    assign s_axi_bvalid = s_axi_wvalid && s_axi_wready;

    // Read
    reg [31:0] rdata;
    always @(*) begin
        case (s_axi_araddr[5:2])
            4'h0: rdata = src_addr;
            4'h1: rdata = dst_addr;
            4'h2: rdata = xfer_len;
            4'h3: rdata = {24'h0, xfer_control};
            4'h4: rdata = sg_ptr;
            4'h5: rdata = {31'h0, sg_enable};
            4'h6: rdata = {30'h0, transfer_done, transfer_error};  // Status
            default: rdata = 32'h0;
        endcase
    end

    assign s_axi_arready = s_axi_arvalid;
    assign s_axi_rdata = rdata;
    assign s_axi_rresp = 2'b00;
    assign s_axi_rvalid = s_axi_arvalid;

    // Interrupt
    assign dma_interrupt = transfer_done | transfer_error;

endmodule
