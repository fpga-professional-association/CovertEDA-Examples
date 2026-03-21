// ADC SPI Interface Top Module
// Device: MPF100T-1FCG484I

module adc_top (
    input  clk,
    input  rst_n,
    input  adc_miso,
    output adc_sclk,
    output adc_cs_n,
    output adc_mosi,
    output [11:0] adc_data,
    output data_valid
);

    // SPI master controller
    wire spi_clk;
    wire [7:0] spi_tx_data;
    wire [7:0] spi_rx_data;
    wire spi_busy;

    spi_master spi_inst (
        .clk(clk),
        .rst_n(rst_n),
        .cs_n(adc_cs_n),
        .sclk(adc_sclk),
        .mosi(adc_mosi),
        .miso(adc_miso),
        .tx_data(spi_tx_data),
        .rx_data(spi_rx_data),
        .busy(spi_busy)
    );

    // Sample buffer
    wire [11:0] buf_data;
    wire buf_valid;

    sample_buffer buf_inst (
        .clk(clk),
        .rst_n(rst_n),
        .spi_data(spi_rx_data),
        .spi_valid(!spi_busy),
        .adc_data(buf_data),
        .adc_valid(buf_valid)
    );

    assign adc_data = buf_data;
    assign data_valid = buf_valid;
    assign spi_tx_data = 8'h00;  // Read command

endmodule
