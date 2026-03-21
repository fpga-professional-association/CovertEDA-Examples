// =============================================================================
// RGB LED PWM Controller with AXI-Lite Slave
// Device: Xilinx Zynq XC7Z020-1CLG400C
// Clock: 50 MHz (from PS)
// =============================================================================

module pwm_top (
    // Clock and Reset
    input  wire         clk,            // 50 MHz from Processing System
    input  wire         rst_n,          // Active-low reset

    // AXI-Lite Slave Interface
    input  wire [31:0]  axi_awaddr,
    input  wire         axi_awvalid,
    output wire         axi_awready,
    input  wire [31:0]  axi_wdata,
    input  wire [3:0]   axi_wstrb,
    input  wire         axi_wvalid,
    output wire         axi_wready,
    output wire [1:0]   axi_bresp,
    output wire         axi_bvalid,
    input  wire         axi_bready,

    input  wire [31:0]  axi_araddr,
    input  wire         axi_arvalid,
    output wire         axi_arready,
    output wire [31:0]  axi_rdata,
    output wire [1:0]   axi_rresp,
    output wire         axi_rvalid,
    input  wire         axi_rready,

    // RGB LED Outputs
    output wire         pwm_red,
    output wire         pwm_green,
    output wire         pwm_blue
);

    // ---- Registers ----
    reg [7:0] red_duty;
    reg [7:0] green_duty;
    reg [7:0] blue_duty;

    // ---- PWM Control ----
    wire [7:0] pwm_counter;
    reg [7:0] pwm_counter_r;

    // Counter increments every clock
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            pwm_counter_r <= 8'h00;
        end else begin
            pwm_counter_r <= pwm_counter_r + 1'b1;
        end
    end

    assign pwm_counter = pwm_counter_r;

    // PWM comparison logic
    assign pwm_red   = (pwm_counter < red_duty);
    assign pwm_green = (pwm_counter < green_duty);
    assign pwm_blue  = (pwm_counter < blue_duty);

    // ---- AXI-Lite Slave Implementation ----
    reg aw_en;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            aw_en <= 1'b1;
            red_duty <= 8'h00;
            green_duty <= 8'h00;
            blue_duty <= 8'h00;
        end else begin
            // Write Address Phase
            if (axi_awvalid && axi_awready) begin
                aw_en <= 1'b0;
            end
            if (axi_bvalid && axi_bready) begin
                aw_en <= 1'b1;
            end

            // Write Data Phase
            if (axi_wvalid && axi_wready) begin
                case (axi_awaddr[3:2])
                    2'b00: begin
                        if (axi_wstrb[0]) red_duty <= axi_wdata[7:0];
                        if (axi_wstrb[1]) green_duty <= axi_wdata[15:8];
                        if (axi_wstrb[2]) blue_duty <= axi_wdata[23:16];
                    end
                    default: ;
                endcase
            end
        end
    end

    // AXI Control Signals
    assign axi_awready = axi_awvalid && aw_en;
    assign axi_wready = axi_wvalid;
    assign axi_bresp = 2'b00;  // OKAY response
    assign axi_bvalid = axi_wvalid && axi_wready;

    assign axi_arready = axi_arvalid;
    assign axi_rdata = {8'h00, blue_duty, green_duty, red_duty};
    assign axi_rresp = 2'b00;
    assign axi_rvalid = axi_arvalid && axi_arready;

endmodule
