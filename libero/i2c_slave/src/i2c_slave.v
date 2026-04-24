// I2C Slave with 256-byte Register Map
// Target: MPF100T (PolarFire)

module i2c_slave #(
    parameter SLAVE_ADDR = 7'h50
)(
    input        clk,
    input        reset_n,
    input        scl_in,
    input        sda_in,
    output reg   sda_out,
    output reg   sda_oe,      // 1 = drive SDA low
    // Register interface
    output reg [7:0] reg_addr,
    output reg [7:0] reg_wdata,
    output reg       reg_wr,
    input  [7:0]     reg_rdata
);

    localparam IDLE      = 4'd0;
    localparam ADDR_BYTE = 4'd1;
    localparam ADDR_ACK  = 4'd2;
    localparam REG_BYTE  = 4'd3;
    localparam REG_ACK   = 4'd4;
    localparam WR_BYTE   = 4'd5;
    localparam WR_ACK    = 4'd6;
    localparam RD_BYTE   = 4'd7;
    localparam RD_ACK    = 4'd8;

    reg [3:0]  state;
    reg [7:0]  shift_reg;
    reg [2:0]  bit_cnt;
    reg        rw_bit;     // 0=write, 1=read

    reg scl_d1, scl_d2, sda_d1, sda_d2;
    wire scl_rise = ~scl_d2 & scl_d1;
    wire scl_fall = scl_d2 & ~scl_d1;
    wire start_cond = scl_d2 & sda_d2 & ~sda_d1;  // SDA falls while SCL high
    wire stop_cond  = scl_d2 & ~sda_d2 & sda_d1;  // SDA rises while SCL high

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            scl_d1 <= 1; scl_d2 <= 1;
            sda_d1 <= 1; sda_d2 <= 1;
        end else begin
            scl_d1 <= scl_in; scl_d2 <= scl_d1;
            sda_d1 <= sda_in; sda_d2 <= sda_d1;
        end
    end

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            state     <= IDLE;
            shift_reg <= 8'd0;
            bit_cnt   <= 3'd0;
            rw_bit    <= 1'b0;
            sda_out   <= 1'b1;
            sda_oe    <= 1'b0;
            reg_addr  <= 8'd0;
            reg_wdata <= 8'd0;
            reg_wr    <= 1'b0;
        end else begin
            reg_wr <= 1'b0;

            if (stop_cond) begin
                state  <= IDLE;
                sda_oe <= 0;
            end

            if (start_cond) begin
                state   <= ADDR_BYTE;
                bit_cnt <= 0;
                sda_oe  <= 0;
            end

            case (state)
                ADDR_BYTE: begin
                    if (scl_rise) begin
                        shift_reg <= {shift_reg[6:0], sda_d2};
                        bit_cnt   <= bit_cnt + 1;
                        if (bit_cnt == 7) begin
                            rw_bit <= sda_d2;
                            state  <= ADDR_ACK;
                        end
                    end
                end

                ADDR_ACK: begin
                    if (scl_fall) begin
                        if (shift_reg[7:1] == SLAVE_ADDR) begin
                            sda_oe  <= 1;   // ACK
                            sda_out <= 0;
                            bit_cnt <= 0;
                            state   <= rw_bit ? RD_BYTE : REG_BYTE;
                        end else begin
                            sda_oe <= 0;    // NACK
                            state  <= IDLE;
                        end
                    end
                end

                REG_BYTE: begin
                    if (scl_fall) sda_oe <= 0;
                    if (scl_rise) begin
                        shift_reg <= {shift_reg[6:0], sda_d2};
                        bit_cnt   <= bit_cnt + 1;
                        if (bit_cnt == 7) begin
                            reg_addr <= {shift_reg[6:0], sda_d2};
                            state    <= REG_ACK;
                        end
                    end
                end

                REG_ACK: begin
                    if (scl_fall) begin
                        sda_oe  <= 1;
                        sda_out <= 0;  // ACK
                        bit_cnt <= 0;
                        state   <= WR_BYTE;
                    end
                end

                WR_BYTE: begin
                    if (scl_fall) sda_oe <= 0;
                    if (scl_rise) begin
                        shift_reg <= {shift_reg[6:0], sda_d2};
                        bit_cnt   <= bit_cnt + 1;
                        if (bit_cnt == 7) begin
                            reg_wdata <= {shift_reg[6:0], sda_d2};
                            reg_wr    <= 1;
                            state     <= WR_ACK;
                        end
                    end
                end

                WR_ACK: begin
                    if (scl_fall) begin
                        sda_oe  <= 1;
                        sda_out <= 0;
                        bit_cnt <= 0;
                        reg_addr <= reg_addr + 1;
                        state    <= WR_BYTE;
                    end
                end

                RD_BYTE: begin
                    if (scl_fall) begin
                        sda_oe  <= 1;
                        sda_out <= reg_rdata[7 - bit_cnt];
                        bit_cnt <= bit_cnt + 1;
                        if (bit_cnt == 7)
                            state <= RD_ACK;
                    end
                end

                RD_ACK: begin
                    if (scl_fall) begin
                        sda_oe  <= 0;  // Release for master ACK/NACK
                        bit_cnt <= 0;
                        reg_addr <= reg_addr + 1;
                    end
                    if (scl_rise) begin
                        if (sda_d2 == 0)  // Master ACK
                            state <= RD_BYTE;
                        else              // Master NACK
                            state <= IDLE;
                    end
                end

                default: begin
                    sda_oe <= 0;
                end
            endcase
        end
    end

endmodule
