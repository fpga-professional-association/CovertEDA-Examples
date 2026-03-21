// =============================================================================
// Module: i2c_slave
// Description: I2C slave receiver with standard clock stretching
// =============================================================================

module i2c_slave (
    input   wire        clk,        // System clock
    input   wire        rst_n,      // Reset
    inout   wire        sda,        // I2C data
    inout   wire        scl,        // I2C clock
    output  wire [7:0]  addr_out,   // Slave address
    output  wire [31:0] data_out,   // Data output
    input   wire [31:0] data_in,    // Data input
    output  wire        write_en,   // Write enable
    output  reg         busy        // Busy flag
);

    // I2C interface - open-drain outputs
    wire sda_in, scl_in;
    reg sda_out, scl_out;

    assign sda = sda_out ? 1'bz : 1'b0;
    assign scl = scl_out ? 1'bz : 1'b0;
    assign sda_in = sda;
    assign scl_in = scl;

    // State machine
    parameter IDLE = 3'b000;
    parameter ADDR = 3'b001;
    parameter ACK1 = 3'b010;
    parameter DATA = 3'b011;
    parameter ACK2 = 3'b100;

    reg [2:0] state;
    reg [3:0] bit_count;
    reg [7:0] addr_shift;
    reg [31:0] data_shift;
    reg scl_sync, scl_sync2;
    reg sda_sync, sda_sync2;

    // Edge detection
    wire scl_falling = scl_sync2 & ~scl_sync;
    wire scl_rising = ~scl_sync2 & scl_sync;
    wire sda_falling = sda_sync2 & ~sda_sync;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            scl_sync <= 1'b1;
            scl_sync2 <= 1'b1;
            sda_sync <= 1'b1;
            sda_sync2 <= 1'b1;
        end else begin
            scl_sync <= scl_in;
            scl_sync2 <= scl_sync;
            sda_sync <= sda_in;
            sda_sync2 <= sda_sync;
        end
    end

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            busy <= 1'b0;
            sda_out <= 1'b1;
            scl_out <= 1'b1;
            bit_count <= 4'h0;
        end else begin
            case (state)
                IDLE: begin
                    if (sda_falling & scl_sync2) begin
                        // START condition detected
                        state <= ADDR;
                        busy <= 1'b1;
                        bit_count <= 4'h0;
                    end
                end

                ADDR: begin
                    if (scl_falling) begin
                        addr_shift <= {addr_shift[6:0], sda_sync2};
                        bit_count <= bit_count + 1'b1;
                        if (bit_count == 4'h6) begin
                            state <= ACK1;
                        end
                    end
                end

                ACK1: begin
                    if (scl_falling) begin
                        sda_out <= 1'b0;  // Pull SDA low for ACK
                        bit_count <= 4'h0;
                        state <= DATA;
                    end
                    if (scl_rising) begin
                        sda_out <= 1'b1;  // Release SDA
                    end
                end

                DATA: begin
                    if (scl_falling) begin
                        data_shift <= {data_shift[30:0], sda_sync2};
                        bit_count <= bit_count + 1'b1;
                        if (bit_count == 4'hF) begin
                            state <= ACK2;
                        end
                    end
                end

                ACK2: begin
                    if (scl_falling) begin
                        sda_out <= 1'b0;  // Pull low for ACK
                        state <= IDLE;
                        busy <= 1'b0;
                    end
                end

                default: state <= IDLE;
            endcase
        end
    end

    assign addr_out = addr_shift[7:1];  // Remove R/W bit
    assign data_out = data_shift;
    assign write_en = (state == DATA) & scl_rising;

endmodule
