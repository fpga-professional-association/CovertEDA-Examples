// PWM DAC

module pwm_dac (
    input  clk,
    input  rst_n,
    input  [7:0] sample,
    input  sample_valid,
    output pwm_out
);

    reg [7:0] counter;
    reg [7:0] sample_latch;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            counter <= 8'h0;
            sample_latch <= 8'h0;
        end else begin
            counter <= counter + 1'b1;
            if (sample_valid) begin
                sample_latch <= sample;
            end
        end
    end

    assign pwm_out = (counter < sample_latch);

endmodule
