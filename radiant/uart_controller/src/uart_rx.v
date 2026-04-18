// =============================================================================
// Module: uart_rx
// Description: UART receiver with 8 data bits, 1 start, 1 stop bit
//              Uses 16x oversampling with mid-bit sampling
// =============================================================================

module uart_rx (
    input   wire        clk,        // System clock
    input   wire        baud_clk,   // Baud rate clock (16x oversampling)
    input   wire        rst_n,      // Reset
    input   wire        rx,         // Serial input
    output  reg [7:0]   data_out,   // Received data
    output  reg         data_valid  // Data valid flag
);

    // State machine states
    parameter IDLE   = 3'b000;
    parameter START  = 3'b001;
    parameter DATA   = 3'b010;
    parameter STOP   = 3'b011;
    parameter VALID  = 3'b100;

    reg [2:0] state, next_state;
    reg [3:0] bit_count;
    reg [3:0] sample_count;
    reg [7:0] shift_reg;
    reg rx_sync, rx_sync2;

    // Synchronize RX input (2-stage synchronizer for metastability)
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            rx_sync <= 1'b1;
            rx_sync2 <= 1'b1;
        end else begin
            rx_sync <= rx;
            rx_sync2 <= rx_sync;
        end
    end

    // State machine
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            bit_count <= 4'h0;
            sample_count <= 4'h0;
            shift_reg <= 8'h0;
            data_out <= 8'h0;
            data_valid <= 1'b0;
        end else if (baud_clk) begin
            state <= next_state;

            case (state)
                IDLE: begin
                    data_valid <= 1'b0;
                    bit_count <= 4'h0;
                    sample_count <= 4'h0;
                end

                START: begin
                    // Count to mid-bit (8 samples at 16x = half bit period)
                    if (sample_count == 4'h7)
                        sample_count <= 4'h0;
                    else
                        sample_count <= sample_count + 1'b1;
                end

                DATA: begin
                    // Count 16 samples per bit, sample at mid-point
                    if (sample_count == 4'hF) begin
                        sample_count <= 4'h0;
                        shift_reg <= {rx_sync2, shift_reg[7:1]};
                        bit_count <= bit_count + 1'b1;
                    end else begin
                        sample_count <= sample_count + 1'b1;
                    end
                end

                STOP: begin
                    if (sample_count == 4'hF)
                        sample_count <= 4'h0;
                    else
                        sample_count <= sample_count + 1'b1;
                end

                VALID: begin
                    data_valid <= 1'b1;
                    data_out <= shift_reg;
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
                if (!rx_sync2) next_state = START;
            end

            START: begin
                // After 8 samples (mid-bit), move to DATA
                if (sample_count == 4'h7) next_state = DATA;
            end

            DATA: begin
                // After all 8 data bits received
                if (bit_count == 4'h8) next_state = STOP;
            end

            STOP: begin
                // Wait full bit period for stop bit
                if (sample_count == 4'hF) next_state = VALID;
            end

            VALID: begin
                next_state = IDLE;
            end

            default: next_state = IDLE;
        endcase
    end

endmodule
