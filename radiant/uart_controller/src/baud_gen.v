// =============================================================================
// Module: baud_gen
// Description: Baud rate generator for 115200 bps from 50 MHz clock
// Generates 16x oversampling clock for UART
// =============================================================================

module baud_gen (
    input   wire    clk,        // 50 MHz input
    input   wire    rst_n,      // Reset
    output  reg     baud_clk    // 115200 * 16 baud clock output
);

    // Baud rate calculation: 50MHz / (115200 * 16) ≈ 27.126 count
    // We use counter value of 26 for closest match
    parameter BAUD_COUNT = 26;

    reg [5:0] counter;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            counter <= 6'h0;
            baud_clk <= 1'b0;
        end else begin
            if (counter == BAUD_COUNT) begin
                counter <= 6'h0;
                baud_clk <= ~baud_clk;
            end else begin
                counter <= counter + 1'b1;
            end
        end
    end

endmodule
