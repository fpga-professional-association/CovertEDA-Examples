// Servo Controller - 4-channel RC servo PWM generator
// 50Hz base frequency, 1-2ms pulse width
// Quartus / Cyclone IV E (EP4CE6)
// Designed for 50MHz clock: period = 20ns, 50Hz = 1,000,000 counts

module servo_controller (
    input        clk,
    input        rst_n,
    input  [1:0] ch_sel,      // channel select
    input  [15:0] position,   // 0=1ms, 65535=2ms pulse width
    input        wr_en,       // write position
    output [3:0] servo_pwm    // PWM outputs
);

    // For simulation: use shorter period (1000 counts instead of 1M)
    parameter PERIOD_COUNT = 20'd1000;
    parameter MIN_PULSE    = 20'd50;   // 1ms equivalent
    parameter MAX_PULSE    = 20'd100;  // 2ms equivalent

    reg [19:0] counter;
    reg [19:0] pulse_width [0:3];
    reg [3:0]  pwm_reg;

    assign servo_pwm = pwm_reg;

    // Scale 16-bit position to pulse width range
    wire [19:0] scaled_pulse;
    assign scaled_pulse = MIN_PULSE + ((position * (MAX_PULSE - MIN_PULSE)) >> 16);

    integer i;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            counter <= 20'd0;
            pwm_reg <= 4'b0000;
            for (i = 0; i < 4; i = i + 1)
                pulse_width[i] <= MIN_PULSE + ((MAX_PULSE - MIN_PULSE) >> 1); // center
        end else begin
            // Write position to selected channel
            if (wr_en) begin
                pulse_width[ch_sel] <= scaled_pulse;
            end

            // Main counter
            if (counter >= PERIOD_COUNT - 1)
                counter <= 20'd0;
            else
                counter <= counter + 20'd1;

            // Generate PWM for each channel
            for (i = 0; i < 4; i = i + 1) begin
                if (counter < pulse_width[i])
                    pwm_reg[i] <= 1'b1;
                else
                    pwm_reg[i] <= 1'b0;
            end
        end
    end

endmodule
