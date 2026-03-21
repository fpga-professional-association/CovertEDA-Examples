// =============================================================================
// UART Transmitter Module with 16x oversampling
// =============================================================================

module uart_tx (
    input  wire         clk,          // 16x baud clock
    input  wire         rst_n,
    input  wire [7:0]   data_in,
    input  wire         data_valid,
    output reg          data_ready,
    output reg          uart_tx
);

    // State machine states
    localparam IDLE     = 3'b000,
               START    = 3'b001,
               DATA     = 3'b010,
               STOP     = 3'b011,
               DONE     = 3'b100;

    reg [2:0]  state, next_state;
    reg [3:0]  sample_cnt;
    reg [3:0]  bit_cnt;
    reg [7:0]  shift_reg;

    // Main state machine
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            sample_cnt <= 4'b0;
            bit_cnt <= 4'b0;
            shift_reg <= 8'b0;
            uart_tx <= 1'b1;          // Idle = high
            data_ready <= 1'b1;
        end else begin
            state <= next_state;

            case (state)
                IDLE: begin
                    uart_tx <= 1'b1;
                    data_ready <= 1'b1;
                    if (data_valid) begin
                        shift_reg <= data_in;
                        sample_cnt <= 4'b0;
                    end
                end

                START: begin
                    uart_tx <= 1'b0;           // Start bit (low)
                    data_ready <= 1'b0;
                    if (sample_cnt == 4'd15) begin
                        sample_cnt <= 4'b0;
                        bit_cnt <= 4'b0;
                    end else begin
                        sample_cnt <= sample_cnt + 1'b1;
                    end
                end

                DATA: begin
                    uart_tx <= shift_reg[0];
                    if (sample_cnt == 4'd15) begin
                        sample_cnt <= 4'b0;
                        shift_reg <= {1'b0, shift_reg[7:1]};
                        if (bit_cnt == 4'd7) begin
                            bit_cnt <= 4'b0;
                        end else begin
                            bit_cnt <= bit_cnt + 1'b1;
                        end
                    end else begin
                        sample_cnt <= sample_cnt + 1'b1;
                    end
                end

                STOP: begin
                    uart_tx <= 1'b1;           // Stop bit (high)
                    if (sample_cnt == 4'd15) begin
                        sample_cnt <= 4'b0;
                    end else begin
                        sample_cnt <= sample_cnt + 1'b1;
                    end
                end

                DONE: begin
                    uart_tx <= 1'b1;
                end
            endcase
        end
    end

    // Next state logic
    always @(*) begin
        next_state = state;
        case (state)
            IDLE:  if (data_valid) next_state = START;
            START: if (sample_cnt == 4'd15) next_state = DATA;
            DATA:  if (bit_cnt == 4'd7 && sample_cnt == 4'd15) next_state = STOP;
            STOP:  if (sample_cnt == 4'd15) next_state = DONE;
            DONE:  next_state = IDLE;
        endcase
    end

endmodule
