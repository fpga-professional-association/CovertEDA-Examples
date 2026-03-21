// PWM Audio Player Top Module
// Device: iCE40UP5K

module audio_top (
    input  clk,
    input  rst_n,
    output pwm_out
);

    wire [7:0] sample;
    wire sample_valid;

    pwm_dac dac_inst (
        .clk(clk),
        .rst_n(rst_n),
        .sample(sample),
        .sample_valid(sample_valid),
        .pwm_out(pwm_out)
    );

    sample_rom rom_inst (
        .clk(clk),
        .addr(addr),
        .data(sample),
        .valid(sample_valid)
    );

endmodule
