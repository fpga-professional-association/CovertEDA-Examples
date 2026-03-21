// LED Blinker - Simple 4-LED blinker with prescaler
// Target: LFE5U-25F-6BG256C (ECP5)
// Oscillator: 25 MHz
// LED outputs toggle at 1 Hz each with different phases

module blinky_top (
    input clk,              // 25 MHz oscillator
    input reset_n,          // Active low reset
    output [3:0] led_out    // 4 LED outputs
);

    // Local parameters
    localparam PRESCALE_WIDTH = 25;
    localparam PRESCALE_VAL = 25_000_000;  // 1 second at 25 MHz
    localparam COUNTER_WIDTH = 28;

    // Internal signals
    reg [PRESCALE_WIDTH-1:0] prescale_counter;
    reg [COUNTER_WIDTH-1:0] led_counter;
    reg [3:0] led_shift;

    // Prescaler: divide 25 MHz to 1 Hz
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            prescale_counter <= {PRESCALE_WIDTH{1'b0}};
        end else begin
            if (prescale_counter >= PRESCALE_VAL - 1) begin
                prescale_counter <= {PRESCALE_WIDTH{1'b0}};
            end else begin
                prescale_counter <= prescale_counter + 1'b1;
            end
        end
    end

    // LED shift register - creates rotating pattern
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            led_shift <= 4'b0001;
        end else begin
            if (prescale_counter == PRESCALE_VAL - 1) begin
                led_shift <= {led_shift[2:0], led_shift[3]};
            end
        end
    end

    // Counter for LED blink sequences
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            led_counter <= {COUNTER_WIDTH{1'b0}};
        end else begin
            if (prescale_counter == PRESCALE_VAL - 1) begin
                led_counter <= led_counter + 1'b1;
            end
        end
    end

    // Output assignment
    assign led_out = led_shift;

endmodule
