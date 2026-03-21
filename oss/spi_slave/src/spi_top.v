// SPI Slave Top Module
// Device: LFE5U-25F

module spi_top (
    input  clk,
    input  rst_n,
    input  spi_clk,
    input  spi_cs_n,
    input  spi_mosi,
    output spi_miso,
    output [31:0] rx_data,
    output rx_valid
);

    wire [31:0] reg_data;
    wire reg_write;

    spi_slave spi_inst (
        .clk(clk),
        .rst_n(rst_n),
        .spi_clk(spi_clk),
        .spi_cs_n(spi_cs_n),
        .spi_mosi(spi_mosi),
        .spi_miso(spi_miso),
        .data_out(rx_data),
        .valid(rx_valid)
    );

    reg_bank regfile (
        .clk(clk),
        .rst_n(rst_n),
        .addr(rx_data[9:8]),
        .write_en(reg_write),
        .write_data(rx_data),
        .read_data(reg_data)
    );

endmodule
