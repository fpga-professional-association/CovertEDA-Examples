// RGB LED Driver with 24-bit Color and Breathing Effect
// Device: iCE40UP5K
// PWM-based RGB with optional breathing (triangle modulation)

module rgb_led_driver (
    input         clk,
    input         rst_n,
    input  [7:0]  red,
    input  [7:0]  green,
    input  [7:0]  blue,
    input         breathe_en,
    output        led_r,
    output        led_g,
    output        led_b
);

    reg [7:0]  pwm_cnt;
    reg [15:0] breathe_cnt;
    reg [7:0]  breathe_val;  // 0-255 modulation
    reg        breathe_dir;

    // Breathing: slow triangle wave
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            breathe_cnt <= 16'd0;
            breathe_val <= 8'd0;
            breathe_dir <= 1'b1;
        end else begin
            breathe_cnt <= breathe_cnt + 1'b1;
            if (breathe_cnt == 16'hFFFF) begin
                if (breathe_dir) begin
                    if (breathe_val == 8'hFF)
                        breathe_dir <= 1'b0;
                    else
                        breathe_val <= breathe_val + 1'b1;
                end else begin
                    if (breathe_val == 8'h00)
                        breathe_dir <= 1'b1;
                    else
                        breathe_val <= breathe_val - 1'b1;
                end
            end
        end
    end

    // PWM counter
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            pwm_cnt <= 8'd0;
        else
            pwm_cnt <= pwm_cnt + 1'b1;
    end

    // Modulated duty cycles
    wire [15:0] mod_r = breathe_en ? (red   * breathe_val) : {red,   8'hFF};
    wire [15:0] mod_g = breathe_en ? (green * breathe_val) : {green, 8'hFF};
    wire [15:0] mod_b = breathe_en ? (blue  * breathe_val) : {blue,  8'hFF};

    assign led_r = (pwm_cnt < mod_r[15:8]);
    assign led_g = (pwm_cnt < mod_g[15:8]);
    assign led_b = (pwm_cnt < mod_b[15:8]);

endmodule
