// =============================================================================
// AXI-Lite Slave Register Interface (Generic)
// =============================================================================

module axi_lite_slave #(
    parameter C_S_AXI_DATA_WIDTH = 32,
    parameter C_S_AXI_ADDR_WIDTH = 12
) (
    input  wire                              clk,
    input  wire                              rst_n,

    // AXI-Lite Write Address
    input  wire [C_S_AXI_ADDR_WIDTH-1:0]     axi_awaddr,
    input  wire [2:0]                        axi_awprot,
    input  wire                              axi_awvalid,
    output wire                              axi_awready,

    // AXI-Lite Write Data
    input  wire [C_S_AXI_DATA_WIDTH-1:0]     axi_wdata,
    input  wire [(C_S_AXI_DATA_WIDTH/8)-1:0] axi_wstrb,
    input  wire                              axi_wvalid,
    output wire                              axi_wready,

    // AXI-Lite Write Response
    output wire [1:0]                        axi_bresp,
    output wire                              axi_bvalid,
    input  wire                              axi_bready,

    // AXI-Lite Read Address
    input  wire [C_S_AXI_ADDR_WIDTH-1:0]     axi_araddr,
    input  wire [2:0]                        axi_arprot,
    input  wire                              axi_arvalid,
    output wire                              axi_arready,

    // AXI-Lite Read Data
    output wire [C_S_AXI_DATA_WIDTH-1:0]     axi_rdata,
    output wire [1:0]                        axi_rresp,
    output wire                              axi_rvalid,
    input  wire                              axi_rready,

    // Internal Register Outputs (4x 32-bit registers)
    output reg  [C_S_AXI_DATA_WIDTH-1:0]     reg0,
    output reg  [C_S_AXI_DATA_WIDTH-1:0]     reg1,
    output reg  [C_S_AXI_DATA_WIDTH-1:0]     reg2,
    output reg  [C_S_AXI_DATA_WIDTH-1:0]     reg3,
    output reg  [C_S_AXI_DATA_WIDTH-1:0]     reg_status
);

    reg aw_en;
    reg [C_S_AXI_ADDR_WIDTH-1:0] axi_awaddr_r;
    reg [C_S_AXI_ADDR_WIDTH-1:0] axi_araddr_r;

    // ---- Write Address Phase ----
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            aw_en <= 1'b1;
            axi_awaddr_r <= {C_S_AXI_ADDR_WIDTH{1'b0}};
        end else begin
            if (axi_awvalid && axi_awready) begin
                axi_awaddr_r <= axi_awaddr;
                aw_en <= 1'b0;
            end
            if (axi_bvalid && axi_bready) begin
                aw_en <= 1'b1;
            end
        end
    end

    assign axi_awready = axi_awvalid && aw_en;

    // ---- Write Data Phase ----
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            reg0 <= {C_S_AXI_DATA_WIDTH{1'b0}};
            reg1 <= {C_S_AXI_DATA_WIDTH{1'b0}};
            reg2 <= {C_S_AXI_DATA_WIDTH{1'b0}};
            reg3 <= {C_S_AXI_DATA_WIDTH{1'b0}};
        end else if (axi_wvalid && axi_wready) begin
            case (axi_awaddr_r[3:2])
                2'b00: begin
                    if (axi_wstrb[0]) reg0[7:0]   <= axi_wdata[7:0];
                    if (axi_wstrb[1]) reg0[15:8]  <= axi_wdata[15:8];
                    if (axi_wstrb[2]) reg0[23:16] <= axi_wdata[23:16];
                    if (axi_wstrb[3]) reg0[31:24] <= axi_wdata[31:24];
                end
                2'b01: begin
                    if (axi_wstrb[0]) reg1[7:0]   <= axi_wdata[7:0];
                    if (axi_wstrb[1]) reg1[15:8]  <= axi_wdata[15:8];
                    if (axi_wstrb[2]) reg1[23:16] <= axi_wdata[23:16];
                    if (axi_wstrb[3]) reg1[31:24] <= axi_wdata[31:24];
                end
                2'b10: begin
                    if (axi_wstrb[0]) reg2[7:0]   <= axi_wdata[7:0];
                    if (axi_wstrb[1]) reg2[15:8]  <= axi_wdata[15:8];
                    if (axi_wstrb[2]) reg2[23:16] <= axi_wdata[23:16];
                    if (axi_wstrb[3]) reg2[31:24] <= axi_wdata[31:24];
                end
                2'b11: begin
                    if (axi_wstrb[0]) reg3[7:0]   <= axi_wdata[7:0];
                    if (axi_wstrb[1]) reg3[15:8]  <= axi_wdata[15:8];
                    if (axi_wstrb[2]) reg3[23:16] <= axi_wdata[23:16];
                    if (axi_wstrb[3]) reg3[31:24] <= axi_wdata[31:24];
                end
            endcase
        end
    end

    assign axi_wready = axi_wvalid;
    assign axi_bresp = 2'b00;  // OKAY response
    assign axi_bvalid = axi_wvalid && axi_wready;

    // ---- Read Address Phase ----
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            axi_araddr_r <= {C_S_AXI_ADDR_WIDTH{1'b0}};
        end else if (axi_arvalid && axi_arready) begin
            axi_araddr_r <= axi_araddr;
        end
    end

    assign axi_arready = axi_arvalid;

    // ---- Read Data Phase ----
    reg [C_S_AXI_DATA_WIDTH-1:0] rdata;

    always @(*) begin
        case (axi_araddr_r[3:2])
            2'b00:   rdata = reg0;
            2'b01:   rdata = reg1;
            2'b10:   rdata = reg2;
            2'b11:   rdata = reg3;
            default: rdata = {C_S_AXI_DATA_WIDTH{1'b0}};
        endcase
    end

    assign axi_rdata = rdata;
    assign axi_rresp = 2'b00;  // OKAY response
    assign axi_rvalid = axi_arvalid;

endmodule
