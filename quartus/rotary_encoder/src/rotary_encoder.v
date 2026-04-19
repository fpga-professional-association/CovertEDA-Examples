// Rotary Encoder - Quadrature decoder with 16-bit position counter
// Quartus / Cyclone IV E (EP4CE6)

module rotary_encoder (
    input         clk,
    input         rst_n,
    input         enc_a,
    input         enc_b,
    input         clear,       // clear position counter
    output [15:0] position,
    output        dir,         // 0=CW, 1=CCW
    output        step_event   // pulses on each step
);

    // Synchronize inputs (2-stage)
    reg [1:0] a_sync, b_sync;
    wire a_filt = a_sync[1];
    wire b_filt = b_sync[1];

    reg a_prev, b_prev;
    reg [15:0] pos_reg;
    reg        dir_reg;
    reg        step_reg;

    assign position   = pos_reg;
    assign dir        = dir_reg;
    assign step_event = step_reg;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            a_sync   <= 2'b00;
            b_sync   <= 2'b00;
            a_prev   <= 1'b0;
            b_prev   <= 1'b0;
            pos_reg  <= 16'd0;
            dir_reg  <= 1'b0;
            step_reg <= 1'b0;
        end else begin
            // Synchronize
            a_sync <= {a_sync[0], enc_a};
            b_sync <= {b_sync[0], enc_b};

            a_prev <= a_filt;
            b_prev <= b_filt;

            step_reg <= 1'b0;

            if (clear) begin
                pos_reg <= 16'd0;
            end else begin
                // Detect transitions on A
                if (a_filt && !a_prev) begin
                    // Rising edge of A
                    if (!b_filt) begin
                        // CW
                        pos_reg  <= pos_reg + 16'd1;
                        dir_reg  <= 1'b0;
                        step_reg <= 1'b1;
                    end else begin
                        // CCW
                        pos_reg  <= pos_reg - 16'd1;
                        dir_reg  <= 1'b1;
                        step_reg <= 1'b1;
                    end
                end else if (!a_filt && a_prev) begin
                    // Falling edge of A
                    if (b_filt) begin
                        // CW
                        pos_reg  <= pos_reg + 16'd1;
                        dir_reg  <= 1'b0;
                        step_reg <= 1'b1;
                    end else begin
                        // CCW
                        pos_reg  <= pos_reg - 16'd1;
                        dir_reg  <= 1'b1;
                        step_reg <= 1'b1;
                    end
                end
            end
        end
    end

endmodule
