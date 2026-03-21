// Color ROM

module color_rom (
    input  clk,
    input  [7:0] addr,
    output [23:0] color,
    output valid
);

    reg [23:0] rom [255:0];
    reg [23:0] color_reg;

    initial begin
        rom[0] = 24'hFF0000;  // Red
        rom[1] = 24'h00FF00;  // Green
        rom[2] = 24'h0000FF;  // Blue
        rom[3] = 24'hFFFF00;  // Yellow
        rom[4] = 24'hFF00FF;  // Magenta
        rom[5] = 24'h00FFFF;  // Cyan
    end

    always @(posedge clk) begin
        color_reg <= rom[addr];
    end

    assign color = color_reg;
    assign valid = 1'b1;

endmodule
