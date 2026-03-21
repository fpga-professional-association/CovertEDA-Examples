// =============================================================================
// UART Receiver Module with 16x oversampling
// =============================================================================

module uart_rx (
    input  wire         clk,          // 16x baud clock
    input  wire         rst_n,
    input  wire         uart_rx,      // RX line (active low)
    output reg  [7:0]   data_out,
    output reg          data_valid,
    input  wire         data_ready
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
    reg [2:0]  rx_sync;   // Triple-stage synchronizer

    // Synchronize async RX input
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            rx_sync <= 3'b111;
        end else begin
            rx_sync <= {rx_sync[1:0], uart_rx};
        end
    end

    wire rx_sync_in = rx_sync[2];

    // Main state machine
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            sample_cnt <= 4'b0;
            bit_cnt <= 4'b0;
            shift_reg <= 8'b0;
            data_out <= 8'b0;
            data_valid <= 1'b0;
        end else begin
            state <= next_state;

            case (state)
                IDLE: begin
                    data_valid <= 1'b0;
                    if (!rx_sync_in) begin
                        sample_cnt <= 4'b0;
                    end
                end

                START: begin
                    if (sample_cnt == 4'd7) begin
                        sample_cnt <= 4'b0;
                        bit_cnt <= 4'b0;
                    end else begin
                        sample_cnt <= sample_cnt + 1'b1;
                    end
                end

                DATA: begin
                    if (sample_cnt == 4'd15) begin
                        sample_cnt <= 4'b0;
                        shift_reg <= {rx_sync_in, shift_reg[7:1]};
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
                    if (sample_cnt == 4'd15) begin
                        sample_cnt <= 4'b0;
                        data_out <= shift_reg;
                        data_valid <= 1'b1;
                    end else begin
                        sample_cnt <= sample_cnt + 1'b1;
                    end
                end

                DONE: begin
                    if (data_ready) begin
                        data_valid <= 1'b0;
                    end
                end
            endcase
        end
    end

    // Next state logic
    always @(*) begin
        next_state = state;
        case (state)
            IDLE:  if (!rx_sync_in) next_state = START;
            START: if (sample_cnt == 4'd7) next_state = DATA;
            DATA:  if (bit_cnt == 4'd7 && sample_cnt == 4'd15) next_state = STOP;
            STOP:  if (sample_cnt == 4'd15) next_state = DONE;
            DONE:  if (data_ready) next_state = IDLE;
        endcase
    end

endmodule
