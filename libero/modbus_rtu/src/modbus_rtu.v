// Modbus RTU Frame Parser
// Target: MPF100T (PolarFire)
// Parses incoming serial bytes into Modbus frames

module modbus_rtu (
    input         clk,
    input         reset_n,
    input  [7:0]  rx_byte,
    input         rx_valid,
    output reg [7:0] slave_addr,
    output reg [7:0] func_code,
    output reg [15:0] reg_addr,
    output reg [15:0] reg_value,
    output reg        frame_valid,
    output reg        crc_error
);

    localparam IDLE     = 3'd0;
    localparam ADDR     = 3'd1;
    localparam FUNC     = 3'd2;
    localparam DATA_HI  = 3'd3;
    localparam DATA_LO  = 3'd4;
    localparam VAL_HI   = 3'd5;
    localparam VAL_LO   = 3'd6;
    localparam CRC      = 3'd7;

    reg [2:0]  state;
    reg [15:0] crc_reg;
    reg [7:0]  byte_buf;
    reg [3:0]  timeout_cnt;

    // Simplified CRC-16: XOR accumulator for simulation
    function [15:0] crc_update;
        input [15:0] crc;
        input [7:0]  data;
        begin
            crc_update = crc ^ {8'h00, data};
            crc_update = {1'b0, crc_update[15:1]} ^ (crc_update[0] ? 16'hA001 : 16'h0000);
        end
    endfunction

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            state       <= IDLE;
            slave_addr  <= 8'd0;
            func_code   <= 8'd0;
            reg_addr    <= 16'd0;
            reg_value   <= 16'd0;
            frame_valid <= 1'b0;
            crc_error   <= 1'b0;
            crc_reg     <= 16'hFFFF;
            timeout_cnt <= 4'd0;
        end else begin
            frame_valid <= 1'b0;
            crc_error   <= 1'b0;

            // Timeout: if no byte for 15 cycles, reset to IDLE
            if (state != IDLE && !rx_valid) begin
                timeout_cnt <= timeout_cnt + 1;
                if (timeout_cnt == 4'd15) begin
                    state <= IDLE;
                    timeout_cnt <= 0;
                end
            end

            if (rx_valid) begin
                timeout_cnt <= 0;
                crc_reg <= crc_update(crc_reg, rx_byte);

                case (state)
                    IDLE: begin
                        crc_reg    <= crc_update(16'hFFFF, rx_byte);
                        slave_addr <= rx_byte;
                        state      <= FUNC;
                    end

                    FUNC: begin
                        func_code <= rx_byte;
                        state     <= DATA_HI;
                    end

                    DATA_HI: begin
                        reg_addr[15:8] <= rx_byte;
                        state <= DATA_LO;
                    end

                    DATA_LO: begin
                        reg_addr[7:0] <= rx_byte;
                        state <= VAL_HI;
                    end

                    VAL_HI: begin
                        reg_value[15:8] <= rx_byte;
                        state <= VAL_LO;
                    end

                    VAL_LO: begin
                        reg_value[7:0] <= rx_byte;
                        frame_valid <= 1'b1;
                        state <= IDLE;
                    end

                    default: state <= IDLE;
                endcase
            end
        end
    end

endmodule
