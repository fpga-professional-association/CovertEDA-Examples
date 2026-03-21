// Blinky LED Top Module for Microchip PolarFire
// Device: MPF300T-1FCG484I
// Clock: 50 MHz

module blinky_top (
    input  clk,
    input  rst_n,
    output led
);

    // 25-bit counter for 1Hz blink (50MHz / 50M = 1Hz)
    reg [24:0] counter;
    reg led_reg;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            counter <= 25'h0;
            led_reg <= 1'b0;
        end else begin
            counter <= counter + 1'b1;
            if (counter == 25'd25000000 - 1) begin
                counter <= 25'h0;
                led_reg <= ~led_reg;
            end
        end
    end

    assign led = led_reg;

endmodule
