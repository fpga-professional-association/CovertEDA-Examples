// Clock Divider - Programmable divider with 8-bit divisor
// Quartus / Cyclone IV E (EP4CE6)
// Output frequency = input frequency / (2 * (divisor + 1))

module clock_divider (
    input        clk,
    input        rst_n,
    input  [7:0] divisor,     // division ratio
    input        load,        // load new divisor
    output       clk_out,     // divided clock output
    output       tick         // one-cycle pulse at each clk_out edge
);

    reg [7:0] div_reg;
    reg [7:0] counter;
    reg       clk_out_reg;
    reg       tick_reg;

    assign clk_out = clk_out_reg;
    assign tick    = tick_reg;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            div_reg     <= 8'd0;
            counter     <= 8'd0;
            clk_out_reg <= 1'b0;
            tick_reg    <= 1'b0;
        end else begin
            tick_reg <= 1'b0;

            if (load) begin
                div_reg <= divisor;
                counter <= 8'd0;
                clk_out_reg <= 1'b0;
            end else begin
                if (counter >= div_reg) begin
                    counter     <= 8'd0;
                    clk_out_reg <= ~clk_out_reg;
                    tick_reg    <= 1'b1;
                end else begin
                    counter <= counter + 8'd1;
                end
            end
        end
    end

endmodule
