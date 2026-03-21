// WS2812B Transmitter

module ws2812_tx (
    input  clk,
    input  rst_n,
    input  [23:0] color,
    input  color_valid,
    output ws2812_out
);

    reg [23:0] color_shift;
    reg [5:0] bit_count;
    reg [4:0] cycle_count;
    reg transmitting;
    reg out_bit;

    // WS2812B timing:
    // T0H = 350ns, T0L = 800ns
    // T1H = 700ns, T1L = 600ns
    // At 12MHz: bit period = 1.2us / 12MHz = 0.1us per clk
    // So: T0 = 350ns = 4 clocks on, 8 off (350 + 800 = 1150ns / 100ns ~= 12 clocks)

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            transmitting <= 1'b0;
            bit_count <= 6'h0;
            cycle_count <= 5'h0;
        end else if (color_valid && !transmitting) begin
            color_shift <= color;
            transmitting <= 1'b1;
            bit_count <= 6'h0;
            cycle_count <= 5'h0;
        end else if (transmitting) begin
            cycle_count <= cycle_count + 1'b1;

            if (cycle_count == 5'd11) begin
                cycle_count <= 5'h0;
                bit_count <= bit_count + 1'b1;
                color_shift <= {color_shift[22:0], 1'b0};

                if (bit_count == 6'd23) begin
                    transmitting <= 1'b0;
                end
            end
        end
    end

    always @* begin
        if (cycle_count < 5'd4) begin
            out_bit = color_shift[23];
        end else begin
            out_bit = 1'b0;
        end
    end

    assign ws2812_out = (transmitting) ? out_bit : 1'b0;

endmodule
