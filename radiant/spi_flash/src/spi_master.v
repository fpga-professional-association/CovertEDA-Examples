// =============================================================================
// Module: spi_master
// Description: SPI master controller with programmable clock divider
// =============================================================================

module spi_master (
    input   wire        clk,        // System clock
    input   wire        rst_n,      // Reset
    output  reg         sclk,       // SPI clock
    output  wire        cs_n,       // Chip select
    output  reg         mosi,       // Master out
    input   wire        miso,       // Master in
    input   wire [7:0]  data_in,    // TX data
    output  reg [7:0]   data_out,   // RX data
    output  wire        rx_valid,   // RX valid
    output  wire        tx_ready,   // TX ready
    output  reg         busy        // Busy flag
);

    parameter CLK_DIV = 4;  // Clock divider for 100MHz -> 25MHz SPI

    reg [3:0] clk_count;
    reg [3:0] bit_count;
    reg [7:0] shift_reg_rx;
    reg [7:0] shift_reg_tx;
    wire sclk_enable;

    reg cs_active;
    assign cs_n = !cs_active;

    // Clock divider
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            clk_count <= 4'h0;
            sclk <= 1'b0;
        end else begin
            if (busy) begin
                clk_count <= clk_count + 1'b1;
                if (clk_count == (CLK_DIV - 1)) begin
                    clk_count <= 4'h0;
                    sclk <= ~sclk;
                end
            end
        end
    end

    assign sclk_enable = (clk_count == (CLK_DIV - 1));
    assign tx_ready = !busy;
    assign rx_valid = (bit_count == 4'h0) & !busy;

    // Shift register logic
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            shift_reg_tx <= 8'h0;
            shift_reg_rx <= 8'h0;
            data_out <= 8'h0;
            bit_count <= 4'h0;
            busy <= 1'b0;
            cs_active <= 1'b0;
        end else begin
            if (!busy && (data_in != 8'h0)) begin
                busy <= 1'b1;
                cs_active <= 1'b1;
                shift_reg_tx <= data_in;
                bit_count <= 4'h8;
            end else if (busy && sclk_enable && sclk) begin
                mosi <= shift_reg_tx[7];
                shift_reg_rx <= {shift_reg_rx[6:0], miso};
                shift_reg_tx <= {shift_reg_tx[6:0], 1'b0};
                bit_count <= bit_count - 1'b1;

                if (bit_count == 4'h1) begin
                    data_out <= {shift_reg_rx[6:0], miso};
                    busy <= 1'b0;
                    cs_active <= 1'b0;
                end
            end
        end
    end

endmodule
