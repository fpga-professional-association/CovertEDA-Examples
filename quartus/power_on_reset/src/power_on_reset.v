// Power-On Reset Generator - Configurable delay
// Quartus / Cyclone IV E (EP4CE6)
// Generates active-low reset for configurable number of clock cycles after power-on

module power_on_reset (
    input        clk,
    input  [7:0] delay_cfg,   // delay in clock cycles (0-255)
    input        force_rst,   // external force reset
    output       rst_n_out,   // generated reset (active-low)
    output       rst_done,    // reset sequence complete
    output [7:0] count_out    // current counter value (for debug)
);

    reg [7:0] counter;
    reg       rst_complete;
    reg       rst_out_reg;

    assign rst_n_out  = rst_out_reg;
    assign rst_done   = rst_complete;
    assign count_out  = counter;

    always @(posedge clk) begin
        if (force_rst) begin
            counter      <= 8'd0;
            rst_complete <= 1'b0;
            rst_out_reg  <= 1'b0;
        end else if (!rst_complete) begin
            if (counter >= delay_cfg) begin
                rst_complete <= 1'b1;
                rst_out_reg  <= 1'b1;
            end else begin
                counter     <= counter + 8'd1;
                rst_out_reg <= 1'b0;
            end
        end else begin
            rst_out_reg <= 1'b1;
        end
    end

endmodule
