// Dead Time Insertion for Motor PWM

module dead_time (
    input  clk,
    input  rst_n,
    input  pwm_u,
    input  pwm_v,
    input  pwm_w,
    output pwm_u_n,
    output pwm_v_n,
    output pwm_w_n
);

    // 100ns dead time @ 100MHz = 10 clock cycles
    reg [3:0] delay_u, delay_v, delay_w;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            delay_u <= 4'h0;
            delay_v <= 4'h0;
            delay_w <= 4'h0;
        end else begin
            delay_u <= {delay_u[2:0], pwm_u};
            delay_v <= {delay_v[2:0], pwm_v};
            delay_w <= {delay_w[2:0], pwm_w};
        end
    end

    assign pwm_u_n = ~delay_u[3];
    assign pwm_v_n = ~delay_v[3];
    assign pwm_w_n = ~delay_w[3];

endmodule
