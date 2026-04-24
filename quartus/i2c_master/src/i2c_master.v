// I2C Master Controller - Byte read/write
// Quartus / Cyclone V GX
// Simple I2C master with start, stop, byte TX/RX

module i2c_master (
    input        clk,
    input        rst_n,
    input        start,       // initiate transaction
    input        rw,          // 0=write, 1=read
    input  [6:0] slave_addr,  // 7-bit slave address
    input  [7:0] data_in,     // data to write
    output [7:0] data_out,    // data read
    output       busy,        // transaction in progress
    output       done,        // transaction complete pulse
    output       ack_err,     // no ACK received
    output       scl_out,     // I2C clock
    output       sda_out,     // I2C data output
    input        sda_in       // I2C data input
);

    localparam IDLE    = 3'd0;
    localparam START_S = 3'd1;
    localparam ADDR    = 3'd2;
    localparam ACK1    = 3'd3;
    localparam DATA    = 3'd4;
    localparam ACK2    = 3'd5;
    localparam STOP_S  = 3'd6;

    // Clock divider for SCL (short for simulation)
    parameter SCL_DIV = 4;

    reg [2:0]  state;
    reg [3:0]  bit_cnt;
    reg [7:0]  shift_reg;
    reg [7:0]  data_out_reg;
    reg        scl_reg;
    reg        sda_reg;
    reg        busy_reg;
    reg        done_reg;
    reg        ack_err_reg;
    reg [3:0]  clk_cnt;
    reg        clk_phase;  // 0=SCL low phase, 1=SCL high phase
    reg        rw_reg;

    assign data_out = data_out_reg;
    assign busy     = busy_reg;
    assign done     = done_reg;
    assign ack_err  = ack_err_reg;
    assign scl_out  = scl_reg;
    assign sda_out  = sda_reg;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state        <= IDLE;
            bit_cnt      <= 4'd0;
            shift_reg    <= 8'd0;
            data_out_reg <= 8'd0;
            scl_reg      <= 1'b1;
            sda_reg      <= 1'b1;
            busy_reg     <= 1'b0;
            done_reg     <= 1'b0;
            ack_err_reg  <= 1'b0;
            clk_cnt      <= 4'd0;
            clk_phase    <= 1'b0;
            rw_reg       <= 1'b0;
        end else begin
            done_reg <= 1'b0;

            // SCL clock generation
            if (state != IDLE) begin
                clk_cnt <= clk_cnt + 4'd1;
                if (clk_cnt >= SCL_DIV - 1) begin
                    clk_cnt   <= 4'd0;
                    clk_phase <= ~clk_phase;
                    scl_reg   <= ~clk_phase;
                end
            end

            case (state)
                IDLE: begin
                    scl_reg <= 1'b1;
                    sda_reg <= 1'b1;
                    if (start) begin
                        state       <= START_S;
                        busy_reg    <= 1'b1;
                        ack_err_reg <= 1'b0;
                        rw_reg      <= rw;
                        shift_reg   <= {slave_addr, rw};
                        clk_cnt     <= 4'd0;
                        clk_phase   <= 1'b0;
                    end
                end

                START_S: begin
                    // SDA goes low while SCL is high (START condition)
                    sda_reg <= 1'b0;
                    if (clk_cnt == SCL_DIV - 1) begin
                        state   <= ADDR;
                        bit_cnt <= 4'd0;
                        scl_reg <= 1'b0;
                    end
                end

                ADDR: begin
                    if (clk_phase == 1'b0 && clk_cnt == 0) begin
                        // Put bit on SDA during SCL low
                        sda_reg   <= shift_reg[7];
                        shift_reg <= {shift_reg[6:0], 1'b0};
                        bit_cnt   <= bit_cnt + 4'd1;
                    end
                    if (bit_cnt >= 4'd8 && clk_phase == 1'b1 && clk_cnt == 0) begin
                        state   <= ACK1;
                        sda_reg <= 1'b1;  // release SDA for ACK
                    end
                end

                ACK1: begin
                    if (clk_phase == 1'b1 && clk_cnt == SCL_DIV/2) begin
                        // Sample ACK
                        if (sda_in == 1'b1)
                            ack_err_reg <= 1'b1;  // NACK

                        if (rw_reg) begin
                            state   <= DATA;
                            bit_cnt <= 4'd0;
                            sda_reg <= 1'b1;  // release for read
                        end else begin
                            state     <= DATA;
                            bit_cnt   <= 4'd0;
                            shift_reg <= data_in;
                        end
                    end
                end

                DATA: begin
                    if (rw_reg) begin
                        // Read mode: sample SDA on SCL high
                        if (clk_phase == 1'b1 && clk_cnt == SCL_DIV/2) begin
                            shift_reg <= {shift_reg[6:0], sda_in};
                            bit_cnt   <= bit_cnt + 4'd1;
                        end
                    end else begin
                        // Write mode: put data on SDA during SCL low
                        if (clk_phase == 1'b0 && clk_cnt == 0) begin
                            sda_reg   <= shift_reg[7];
                            shift_reg <= {shift_reg[6:0], 1'b0};
                            bit_cnt   <= bit_cnt + 4'd1;
                        end
                    end

                    if (bit_cnt >= 4'd8 && clk_phase == 1'b1 && clk_cnt == 0) begin
                        state <= ACK2;
                        if (rw_reg) begin
                            data_out_reg <= shift_reg;
                            sda_reg      <= 1'b1;  // NACK for read (single byte)
                        end else begin
                            sda_reg <= 1'b1;  // release for ACK
                        end
                    end
                end

                ACK2: begin
                    if (clk_phase == 1'b1 && clk_cnt == SCL_DIV/2) begin
                        if (!rw_reg && sda_in == 1'b1)
                            ack_err_reg <= 1'b1;
                        state <= STOP_S;
                    end
                end

                STOP_S: begin
                    // STOP: SDA goes high while SCL is high
                    if (clk_phase == 1'b1) begin
                        sda_reg <= 1'b0;
                    end
                    if (clk_cnt == SCL_DIV - 1 && clk_phase == 1'b1) begin
                        sda_reg  <= 1'b1;
                        scl_reg  <= 1'b1;
                        state    <= IDLE;
                        busy_reg <= 1'b0;
                        done_reg <= 1'b1;
                    end
                end
            endcase
        end
    end

endmodule
