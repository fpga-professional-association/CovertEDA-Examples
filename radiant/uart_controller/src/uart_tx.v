// =============================================================================
// Module: uart_tx
// Description: UART transmitter with 8 data bits, 1 start, 1 stop bit
// =============================================================================

module uart_tx (
    input   wire        clk,        // System clock
    input   wire        baud_clk,   // Baud rate clock (16x oversampling)
    input   wire        rst_n,      // Reset
    input   wire [7:0]  data_in,    // Data to transmit
    input   wire        data_valid, // Data valid flag
    output  wire        tx_ready,   // Ready to accept data
    output  reg         tx          // Serial output
);

    // State machine states
    parameter IDLE   = 3'b000;
    parameter START  = 3'b001;
    parameter DATA   = 3'b010;
    parameter STOP   = 3'b011;

    reg [2:0] state, next_state;
    reg [3:0] bit_count;
    reg [3:0] sample_count;
    reg [7:0] shift_reg;
    wire ready;

    assign ready = (state == IDLE);
    assign tx_ready = ready;

    // State machine
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            bit_count <= 4'h0;
            sample_count <= 4'h0;
            shift_reg <= 8'h0;
            tx <= 1'b1;  // Idle state is high
        end else if (baud_clk) begin
            state <= next_state;

            case (state)
                IDLE: begin
                    tx <= 1'b1;
                    if (data_valid) begin
                        shift_reg <= data_in;
                    end
                end

                START: begin
                    tx <= 1'b0;  // Start bit
                    sample_count <= sample_count + 1'b1;
                end

                DATA: begin
                    tx <= shift_reg[0];
                    sample_count <= sample_count + 1'b1;
                    if (sample_count == 4'hF) begin
                        sample_count <= 4'h0;
                        shift_reg <= {1'b0, shift_reg[7:1]};
                        bit_count <= bit_count + 1'b1;
                    end
                end

                STOP: begin
                    tx <= 1'b1;  // Stop bit
                    sample_count <= sample_count + 1'b1;
                end

                default: state <= IDLE;
            endcase
        end
    end

    // Next state logic
    always @(*) begin
        next_state = state;

        case (state)
            IDLE: begin
                if (data_valid) next_state = START;
            end

            START: begin
                if (sample_count == 4'hF) next_state = DATA;
            end

            DATA: begin
                if (bit_count == 4'h8) next_state = STOP;
            end

            STOP: begin
                if (sample_count == 4'hF) next_state = IDLE;
            end

            default: next_state = IDLE;
        endcase
    end

endmodule
