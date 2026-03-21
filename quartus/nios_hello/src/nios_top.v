// NIOS II System Top Level
// Cyclone IV E - EP4CE115F29C7

module nios_top (
    input  clk_100m,
    input  rst_n,
    input  [7:0] sw_input,
    output [7:0] led_output,
    output [7:0] seg_output,
    inout  [7:0] gpio_bidir
);

    // Internal clock and reset signals
    wire clk_sys;
    wire rst_sys;
    wire pll_locked;

    // NIOS II Bus Signals
    wire [31:0] nios_address;
    wire [31:0] nios_writedata;
    wire [31:0] nios_readdata;
    wire [3:0] nios_byteenable;
    wire nios_write;
    wire nios_read;
    wire nios_waitrequest;

    // Peripheral Control Signals
    reg [7:0] led_ctrl;
    reg [7:0] seg_ctrl;
    reg [7:0] gpio_oe;
    reg [7:0] gpio_out;
    wire [7:0] gpio_in;

    // PLL instance
    system_pll pll_inst (
        .areset(~rst_n),
        .inclk0(clk_100m),
        .c0(clk_sys),
        .locked(pll_locked)
    );

    // System reset logic
    assign rst_sys = ~rst_n | ~pll_locked;

    // GPIO controller
    gpio_ctrl gpio_controller (
        .clk(clk_sys),
        .rst(rst_sys),
        .oe(gpio_oe),
        .data_out(gpio_out),
        .data_in(gpio_in),
        .bidir(gpio_bidir)
    );

    // Bus slave interface (simplified for illustration)
    always @(posedge clk_sys or posedge rst_sys) begin
        if (rst_sys) begin
            led_ctrl <= 8'b0;
            seg_ctrl <= 8'b0;
            gpio_oe <= 8'b0;
            gpio_out <= 8'b0;
        end else begin
            // Write transactions
            if (nios_write && !nios_waitrequest) begin
                case (nios_address[15:0])
                    16'h0000: led_ctrl <= nios_writedata[7:0];
                    16'h0004: seg_ctrl <= nios_writedata[7:0];
                    16'h0008: gpio_oe <= nios_writedata[7:0];
                    16'h000C: gpio_out <= nios_writedata[7:0];
                    default: ;
                endcase
            end
        end
    end

    // Read multiplexer
    assign nios_readdata = (nios_read) ? (
        (nios_address[15:0] == 16'h0000) ? {24'b0, led_ctrl} :
        (nios_address[15:0] == 16'h0004) ? {24'b0, seg_ctrl} :
        (nios_address[15:0] == 16'h0008) ? {24'b0, gpio_oe} :
        (nios_address[15:0] == 16'h000C) ? {24'b0, gpio_out} :
        (nios_address[15:0] == 16'h0010) ? {24'b0, gpio_in} :
        (nios_address[15:0] == 16'h0014) ? {24'b0, sw_input} :
        32'h0
    ) : 32'h0;

    // Output assignments
    assign led_output = led_ctrl;
    assign seg_output = seg_ctrl;

    // No wait states in this simplified design
    assign nios_waitrequest = 1'b0;

endmodule
