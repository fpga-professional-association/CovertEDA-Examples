// N-LED Chaser with Speed Control
// Device: iCE40UP5K
// Shifts a lit LED across N positions with configurable speed

module led_chaser #(
    parameter N_LEDS = 8
)(
    input                clk,
    input                rst_n,
    input  [7:0]         speed,     // higher = slower
    input                direction, // 0=left, 1=right
    output [N_LEDS-1:0]  leds
);

    reg [N_LEDS-1:0] led_reg;
    reg [23:0] divider;
    wire tick;

    assign leds = led_reg;

    // Speed divider: tick rate = clk / (speed * 256 + 1)
    assign tick = (divider == {speed, 16'd0});

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            led_reg <= {{(N_LEDS-1){1'b0}}, 1'b1};
            divider <= 24'd0;
        end else begin
            if (tick) begin
                divider <= 24'd0;
                if (direction)
                    led_reg <= {led_reg[0], led_reg[N_LEDS-1:1]};
                else
                    led_reg <= {led_reg[N_LEDS-2:0], led_reg[N_LEDS-1]};
            end else begin
                divider <= divider + 1'b1;
            end
        end
    end

endmodule
