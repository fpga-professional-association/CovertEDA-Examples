// Blinky LED for iCE40UP5K using OSS CAD Suite
// Device: iCE40UP5K-SG48I

module blinky_top (
    input  clk,
    input  rst_n,
    output led
);

    reg [23:0] counter;
    reg led_reg;

    always @(posedge clk) begin
        if (!rst_n) begin
            counter <= 24'h0;
            led_reg <= 1'b0;
        end else begin
            counter <= counter + 1'b1;
            if (counter == 24'd12000000) begin
                counter <= 24'h0;
                led_reg <= ~led_reg;
            end
        end
    end

    assign led = led_reg;

endmodule
