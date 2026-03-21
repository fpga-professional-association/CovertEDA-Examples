// PWM Generator for 3-Phase Motor

module pwm_gen (
    input  clk,
    input  rst_n,
    input  [15:0] speed_cmd,
    output reg pwm_u,
    output reg pwm_v,
    output reg pwm_w,
    output [15:0] duty_u,
    output [15:0] duty_v,
    output [15:0] duty_w
);

    reg [15:0] counter;
    reg [15:0] duty_u_reg, duty_v_reg, duty_w_reg;

    // 10 kHz PWM frequency (100 MHz / 10000)
    parameter PWM_PERIOD = 16'd10000;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            counter <= 16'h0;
            pwm_u <= 1'b0;
            pwm_v <= 1'b0;
            pwm_w <= 1'b0;
        end else begin
            counter <= counter + 1'b1;

            if (counter >= PWM_PERIOD) begin
                counter <= 16'h0;
            end

            // Sinusoidal modulation
            pwm_u <= (counter < duty_u_reg) ? 1'b1 : 1'b0;
            pwm_v <= (counter < duty_v_reg) ? 1'b1 : 1'b0;
            pwm_w <= (counter < duty_w_reg) ? 1'b1 : 1'b0;
        end
    end

    // Simplified 3-phase generator
    always @* begin
        duty_u_reg = speed_cmd;
        duty_v_reg = (speed_cmd > 3333) ? speed_cmd - 3333 : speed_cmd + 6667;
        duty_w_reg = (speed_cmd > 6666) ? speed_cmd - 6666 : speed_cmd + 3334;
    end

    assign duty_u = duty_u_reg;
    assign duty_v = duty_v_reg;
    assign duty_w = duty_w_reg;

endmodule
