// =============================================================================
// Module: wb_master
// Description: Wishbone master that translates I2C transactions
// =============================================================================

module wb_master (
    input   wire        clk,            // System clock
    input   wire        rst_n,          // Reset
    input   wire [7:0]  i2c_addr,       // I2C slave address
    input   wire [31:0] i2c_data_o,     // I2C output data
    output  reg [31:0]  i2c_data_i,     // I2C input data
    input   wire        i2c_we,         // I2C write enable
    input   wire        i2c_busy,       // I2C busy flag

    // Wishbone interface
    output  reg [31:0]  wb_addr,        // Address
    output  reg [31:0]  wb_data_o,      // Write data
    input   wire [31:0] wb_data_i,      // Read data
    output  reg         wb_we,          // Write enable
    output  reg [3:0]   wb_sel,         // Byte select
    output  reg         wb_cyc,         // Cycle
    output  reg         wb_stb,         // Strobe
    input   wire        wb_ack          // Acknowledge
);

    // State machine for Wishbone transactions
    parameter IDLE = 2'b00;
    parameter ADDR = 2'b01;
    parameter DATA = 2'b10;
    parameter WAIT = 2'b11;

    reg [1:0] state;
    reg i2c_busy_r;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            wb_cyc <= 1'b0;
            wb_stb <= 1'b0;
            wb_we <= 1'b0;
            wb_sel <= 4'hF;
            i2c_busy_r <= 1'b0;
        end else begin
            i2c_busy_r <= i2c_busy;

            case (state)
                IDLE: begin
                    if (i2c_we & !i2c_busy_r) begin
                        // Start of I2C transaction
                        wb_addr <= {24'h0, i2c_addr};
                        wb_data_o <= i2c_data_o;
                        wb_we <= 1'b1;
                        wb_cyc <= 1'b1;
                        wb_stb <= 1'b1;
                        state <= WAIT;
                    end
                end

                WAIT: begin
                    if (wb_ack) begin
                        i2c_data_i <= wb_data_i;
                        wb_cyc <= 1'b0;
                        wb_stb <= 1'b0;
                        state <= IDLE;
                    end
                end

                default: state <= IDLE;
            endcase
        end
    end

endmodule
