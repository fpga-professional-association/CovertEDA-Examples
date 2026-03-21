// Gamma LUT for WS2812B

module gamma_lut (
    input  clk,
    input  [7:0] brightness,
    input  [23:0] color_in,
    output [23:0] color_out
);

    reg [7:0] gamma_lut [255:0];
    reg [23:0] color_gamma;

    initial begin
        $readmemh("gamma_table.hex", gamma_lut);
    end

    wire [7:0] gamma_r = gamma_lut[color_in[23:16]];
    wire [7:0] gamma_g = gamma_lut[color_in[15:8]];
    wire [7:0] gamma_b = gamma_lut[color_in[7:0]];

    assign color_out = {gamma_r, gamma_g, gamma_b};

endmodule
