// Stepper Motor Driver - Full/Half step, 4-phase output
// Quartus / Cyclone IV E (EP4CE6)

module stepper_driver (
    input        clk,
    input        rst_n,
    input        enable,
    input        direction,   // 0=CW, 1=CCW
    input        half_step,   // 0=full step, 1=half step
    input        step_pulse,  // advance one step on rising edge
    output [3:0] phase_out    // 4-phase driver output (A, B, C, D)
);

    reg [2:0] step_idx;  // 0-7 for half step, 0-3 for full step
    reg [3:0] phase_reg;
    reg       step_prev;

    assign phase_out = phase_reg;

    // Full step sequence: AB, BC, CD, DA
    // Half step sequence: A, AB, B, BC, C, CD, D, DA

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            step_idx  <= 3'd0;
            phase_reg <= 4'b0001;
            step_prev <= 1'b0;
        end else begin
            step_prev <= step_pulse;

            if (enable && step_pulse && !step_prev) begin
                // Rising edge of step_pulse
                if (half_step) begin
                    // Half step: 8 states
                    if (direction)
                        step_idx <= (step_idx == 3'd0) ? 3'd7 : step_idx - 3'd1;
                    else
                        step_idx <= (step_idx == 3'd7) ? 3'd0 : step_idx + 3'd1;
                end else begin
                    // Full step: 4 states (use idx 0,2,4,6)
                    if (direction)
                        step_idx <= (step_idx == 3'd0) ? 3'd6 : step_idx - 3'd2;
                    else
                        step_idx <= (step_idx == 3'd6) ? 3'd0 : step_idx + 3'd2;
                end
            end

            // Decode step index to phase outputs
            case (step_idx)
                3'd0: phase_reg <= 4'b0001;  // A
                3'd1: phase_reg <= 4'b0011;  // AB
                3'd2: phase_reg <= 4'b0010;  // B
                3'd3: phase_reg <= 4'b0110;  // BC
                3'd4: phase_reg <= 4'b0100;  // C
                3'd5: phase_reg <= 4'b1100;  // CD
                3'd6: phase_reg <= 4'b1000;  // D
                3'd7: phase_reg <= 4'b1001;  // DA
            endcase
        end
    end

endmodule
