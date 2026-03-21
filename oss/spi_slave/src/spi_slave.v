// SPI Slave

module spi_slave (
    input  clk,
    input  rst_n,
    input  spi_clk,
    input  spi_cs_n,
    input  spi_mosi,
    output spi_miso,
    output [31:0] data_out,
    output valid
);

    reg [31:0] shift_in, shift_out;
    reg [5:0] bit_count;
    reg valid_reg;

    always @(posedge spi_clk or negedge spi_cs_n) begin
        if (!spi_cs_n) begin
            bit_count <= 6'h0;
        end else begin
            shift_in <= {shift_in[30:0], spi_mosi};
            bit_count <= bit_count + 1'b1;
            if (bit_count == 6'd31) begin
                valid_reg <= 1'b1;
            end
        end
    end

    always @(negedge spi_clk) begin
        if (!spi_cs_n) begin
            spi_miso <= shift_out[31];
            shift_out <= {shift_out[30:0], 1'b0};
        end
    end

    assign data_out = shift_in;
    assign valid = valid_reg;

endmodule
