// 3-Phase Motor PWM Top Module
// Device: MPF200T-1FCG484I

module motor_top (
    input  clk,
    input  rst_n,
    input  [15:0] speed_cmd,
    input  encoder_a,
    input  encoder_b,
    output pwm_u,
    output pwm_v,
    output pwm_w,
    output pwm_u_n,
    output pwm_v_n,
    output pwm_w_n,
    output [15:0] encoder_count,
    output [15:0] speed_measured
);

    // PWM generator
    wire [15:0] duty_u, duty_v, duty_w;
    wire pwm_clk;

    pwm_gen pwm_inst (
        .clk(clk),
        .rst_n(rst_n),
        .speed_cmd(speed_cmd),
        .pwm_u(pwm_u),
        .pwm_v(pwm_v),
        .pwm_w(pwm_w),
        .duty_u(duty_u),
        .duty_v(duty_v),
        .duty_w(duty_w)
    );

    // Dead time insertion
    dead_time deadtime_inst (
        .clk(clk),
        .rst_n(rst_n),
        .pwm_u(pwm_u),
        .pwm_v(pwm_v),
        .pwm_w(pwm_w),
        .pwm_u_n(pwm_u_n),
        .pwm_v_n(pwm_v_n),
        .pwm_w_n(pwm_w_n)
    );

    // Encoder interface
    encoder_intf enc_inst (
        .clk(clk),
        .rst_n(rst_n),
        .encoder_a(encoder_a),
        .encoder_b(encoder_b),
        .encoder_count(encoder_count),
        .speed(speed_measured)
    );

endmodule
