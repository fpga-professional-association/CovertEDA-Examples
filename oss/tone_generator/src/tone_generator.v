// Musical Tone Generator (Square Wave)
// Device: iCE40UP5K
// Generates square wave at programmable frequency

module tone_generator (
    input         clk,
    input         rst_n,
    input  [15:0] half_period,  // clk cycles for half period
    input         enable,
    output        tone_out
);

    reg [15:0] counter;
    reg        toggle;

    assign tone_out = enable ? toggle : 1'b0;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            counter <= 16'd0;
            toggle  <= 1'b0;
        end else if (enable) begin
            if (counter >= half_period) begin
                counter <= 16'd0;
                toggle  <= ~toggle;
            end else begin
                counter <= counter + 1'b1;
            end
        end else begin
            counter <= 16'd0;
            toggle  <= 1'b0;
        end
    end

endmodule
