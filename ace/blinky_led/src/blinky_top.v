// Blinky LED for Achronix Speedster7t
// Device: AC7t1500ES0
// Clock: 100 MHz

module blinky_top (
    input  clk,
    input  rst_n,
    output led
);

    // 100 MHz / 50M = 2 Hz blink
    reg [25:0] counter;
    reg led_reg;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            counter <= 26'h0;
            led_reg <= 1'b0;
        end else begin
            counter <= counter + 1'b1;
            if (counter == 26'd50000000 - 1) begin
                counter <= 26'h0;
                led_reg <= ~led_reg;
            end
        end
    end

    assign led = led_reg;

endmodule
