// =============================================================================
// Design      : SPI Flash Controller
// Module      : spi_top
// Description : SPI master with QSPI support for flash memory
// Device      : LIFCL-40-9BG400C
// Frequency   : 100 MHz
// =============================================================================

module spi_top (
    input   wire        clk,        // 100 MHz system clock
    input   wire        rst_n,      // Active-low reset

    // SPI interface
    output  wire        sclk,       // SPI clock
    output  wire        cs_n,       // Chip select (active-low)
    output  wire        mosi,       // Master out, slave in
    input   wire        miso,       // Master in, slave out

    // QSPI interface
    inout   wire [3:0]  qspi_io,    // Quad SPI I/O [3:0]

    // Control interface
    input   wire        spi_mode,   // 0=SPI, 1=QSPI
    input   wire [31:0] addr,       // Address for flash
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
        .data_in({addr[15:8], addr[7:0]}),
        .data_out(fifo_data_out),
        .empty(fifo_empty),
        .full(fifo_full)
    );

    // Output assignment
    assign data_out = spi_rx_data;

endmodule
