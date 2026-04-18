// =============================================================================
// Design      : SPI Flash Controller
// Module      : spi_top
// Description : SPI master controller for flash memory access
// Device      : LIFCL-40-7BG400I
// Frequency   : 50 MHz
// =============================================================================

module spi_top (
    input   wire        clk,        // 50 MHz system clock
    input   wire        rst_n,      // Active-low reset

    // SPI interface
    output  wire        sclk,       // SPI clock
    output  wire        cs_n,       // Chip select (active-low)
    output  wire        mosi,       // Master out, slave in
    input   wire        miso,       // Master in, slave out

    // Control interface
    input   wire [15:0] addr,       // Address for flash (16-bit)
    input   wire [7:0]  data_in,    // Data to write
    output  wire [7:0]  data_out,   // Data read
    input   wire        rd_en,      // Read enable
    input   wire        wr_en,      // Write enable
    output  wire        busy        // Busy flag
);

    // SPI Master instantiation
    wire [7:0] spi_rx_data;
    wire spi_rx_valid;
    wire spi_tx_ready;

    spi_master master (
        .clk(clk),
        .rst_n(rst_n),
        .sclk(sclk),
        .cs_n(cs_n),
        .mosi(mosi),
        .miso(miso),
        .data_in(data_in),
        .data_out(spi_rx_data),
        .rx_valid(spi_rx_valid),
        .tx_ready(spi_tx_ready),
        .busy(busy)
    );

    // FIFO for command/address buffering
    wire fifo_empty, fifo_full;
    wire [15:0] fifo_data_out;

    spi_fifo fifo (
        .clk(clk),
        .rst_n(rst_n),
        .wr_en(wr_en | rd_en),
        .rd_en(spi_tx_ready),
        .data_in(addr),
        .data_out(fifo_data_out),
        .empty(fifo_empty),
        .full(fifo_full)
    );

    // Output assignment
    assign data_out = spi_rx_data;

endmodule
