// Sample ROM

module sample_rom (
    input  clk,
    input  [9:0] addr,
    output [7:0] data,
    output valid
);

    reg [7:0] rom [1023:0];
    reg [7:0] data_reg;

    initial begin
        $readmemh("samples.hex", rom);
    end

    always @(posedge clk) begin
        data_reg <= rom[addr];
    end

    assign data = data_reg;
    assign valid = 1'b1;

endmodule
