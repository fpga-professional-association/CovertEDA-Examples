// =============================================================================
// Design      : Blinky LED Controller
// Module      : blinky_top
// Description : Simple counter-based LED blinker with 4 independent LEDs
// Device      : LIFCL-40-7BG400I
// Frequency   : 25 MHz
// =============================================================================

module blinky_top (
    input   wire        clk,        // 25 MHz system clock
    input   wire        rst_n,      // Active-low asynchronous reset
    output  reg [3:0]   led         // LED outputs
);

    // Parameters
    parameter FREQ_HZ = 25_000_000;
    parameter BLINK_FREQ_HZ = 1;
    parameter COUNT_MAX = FREQ_HZ / (2 * BLINK_FREQ_HZ) - 1;

    // Internal signals
    reg [23:0]  counter;
    wire        counter_done;
    reg [3:0]   led_shift;

    // Counter logic for blink rate
    assign counter_done = (counter == COUNT_MAX);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            counter <= 24'h0;
        end else begin
            if (counter_done) begin
                counter <= 24'h0;
            end else begin
                counter <= counter + 1'b1;
            end
        end
    end

    // LED shift register - creates chasing pattern
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            led_shift <= 4'b0001;
        end else begin
            if (counter_done) begin
                led_shift <= {led_shift[2:0], led_shift[3]};
            end
        end
    end

    // Output assignment
    always @(*) begin
        led = led_shift;
    end

endmodule
