// =============================================================================
// Single PWM Channel
// =============================================================================

module pwm_channel (
    input  wire       clk,
    input  wire       rst_n,
    input  wire [7:0] duty_cycle,    // 0-255 (0-100%)
    output wire       pwm_out
);

    reg [7:0] counter;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            counter <= 8'h00;
        end else begin
            counter <= counter + 1'b1;
        end
    end

    assign pwm_out = (counter < duty_cycle);

endmodule
