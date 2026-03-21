// =============================================================================
// Design      : I2C to Wishbone Bridge
// Module      : i2c_top
// Description : I2C slave with Wishbone master interface
// Device      : LFD2NX-40-7MG672
// Frequency   : 50 MHz
// =============================================================================

module i2c_top (
    input   wire        clk,        // 50 MHz system clock
    input   wire        rst_n,      // Active-low reset

    // I2C interface (open-drain)
    inout   wire        sda,        // I2C data line
    inout   wire        scl,        // I2C clock line

    // Wishbone master interface
    output  wire        wb_clk,     // Wishbone clock
    output  wire        wb_rst,     // Wishbone reset
    output  wire [31:0] wb_addr,    // Address bus
    output  wire [31:0] wb_data_o,  // Write data bus
    input   wire [31:0] wb_data_i,  // Read data bus
    output  wire        wb_we,      // Write enable
    output  wire [3:0]  wb_sel,     // Byte select
    output  wire        wb_cyc,     // Bus cycle
    output  wire        wb_stb,     // Strobe
    input   wire        wb_ack      // Acknowledge
);

    // I2C slave instantiation
    wire i2c_busy;
    wire [7:0] i2c_addr;
    wire [31:0] i2c_data_o;
    wire [31:0] i2c_data_i;
    wire i2c_we;

    i2c_slave i2c_slave_inst (
        .clk(clk),
        .rst_n(rst_n),
        .sda(sda),
        .scl(scl),
        .addr_out(i2c_addr),
        .data_out(i2c_data_o),
        .data_in(i2c_data_i),
        .write_en(i2c_we),
        .busy(i2c_busy)
    );

    // Wishbone master instantiation
    wb_master wb_master_inst (
        .clk(clk),
        .rst_n(rst_n),
        .i2c_addr(i2c_addr),
        .i2c_data_o(i2c_data_o),
        .i2c_data_i(i2c_data_i),
        .i2c_we(i2c_we),
        .i2c_busy(i2c_busy),
        .wb_addr(wb_addr),
        .wb_data_o(wb_data_o),
        .wb_data_i(wb_data_i),
        .wb_we(wb_we),
        .wb_sel(wb_sel),
        .wb_cyc(wb_cyc),
        .wb_stb(wb_stb),
        .wb_ack(wb_ack)
    );

    assign wb_clk = clk;
    assign wb_rst = !rst_n;

endmodule
