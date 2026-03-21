// WS2812B LED Strip Driver Top Module
// Device: iCE40HX8K-CT256

module ws2812_top (
    input  clk,
    input  rst_n,
    output ws2812_out
);

    wire [23:0] color;
    wire color_valid;

    ws2812_tx tx_inst (
        .clk(clk),
        .rst_n(rst_n),
        .color(color),
        .color_valid(color_valid),
        .ws2812_out(ws2812_out)
    );

    color_rom rom_inst (
        .clk(clk),
        .addr(addr),
        .color(color),
        .valid(color_valid)
    );

endmodule
