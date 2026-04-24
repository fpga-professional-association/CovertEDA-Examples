// 4-Channel Independent PWM Generator
// Device: iCE40UP5K
// Each channel has independent 8-bit duty cycle

module pwm_multi (
    input        clk,
    input        rst_n,
    input  [7:0] duty0,
    input  [7:0] duty1,
    input  [7:0] duty2,
    input  [7:0] duty3,
    output       pwm0,
    output       pwm1,
    output       pwm2,
    output       pwm3
);

    reg [7:0] counter;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            counter <= 8'd0;
        else
            counter <= counter + 1'b1;
    end

    assign pwm0 = (counter < duty0);
    assign pwm1 = (counter < duty1);
    assign pwm2 = (counter < duty2);
    assign pwm3 = (counter < duty3);

endmodule
