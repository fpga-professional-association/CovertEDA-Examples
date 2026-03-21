// Blinky LED Controller
// Simple LED blinker on Cyclone IV E device
// 4 LEDs blinking at different rates

module blinky_top (
    input  clk_50m,
    input  rst_n,
    output [3:0] led
);

    // Divider counters for different blink rates
    reg [25:0] div_counter0;
    reg [26:0] div_counter1;
    reg [27:0] div_counter2;
    reg [28:0] div_counter3;

    reg [3:0] led_internal;

    assign led = led_internal;

    always @(posedge clk_50m or negedge rst_n) begin
        if (!rst_n) begin
            div_counter0 <= 26'd0;
            div_counter1 <= 27'd0;
            div_counter2 <= 28'd0;
            div_counter3 <= 29'd0;
            led_internal <= 4'b0000;
        end else begin
            // Counter 0: ~0.75 Hz (50M/2^26 = 0.745 Hz)
            div_counter0 <= div_counter0 + 26'd1;
            if (div_counter0 == 26'd33554432) begin
                div_counter0 <= 26'd0;
                led_internal[0] <= ~led_internal[0];
            end

            // Counter 1: ~0.37 Hz (50M/2^27 = 0.373 Hz)
            div_counter1 <= div_counter1 + 27'd1;
            if (div_counter1 == 27'd67108864) begin
                div_counter1 <= 27'd0;
                led_internal[1] <= ~led_internal[1];
            end

            // Counter 2: ~0.19 Hz (50M/2^28 = 0.186 Hz)
            div_counter2 <= div_counter2 + 28'd1;
            if (div_counter2 == 28'd134217728) begin
                div_counter2 <= 28'd0;
                led_internal[2] <= ~led_internal[2];
            end

            // Counter 3: ~0.09 Hz (50M/2^29 = 0.093 Hz)
            div_counter3 <= div_counter3 + 29'd1;
            if (div_counter3 == 29'd268435456) begin
                div_counter3 <= 29'd0;
                led_internal[3] <= ~led_internal[3];
            end
        end
    end

endmodule
