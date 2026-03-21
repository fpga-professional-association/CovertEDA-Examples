// =============================================================================
// Design      : DSP FIR Filter
// Module      : fir_top
// Description : 8-tap FIR filter using DSP blocks for MAC operations
// Device      : LIFCL-40-7BG400I
// Frequency   : 100 MHz
// Bit Width   : 16-bit input, 32-bit output
// =============================================================================

module fir_top (
    input   wire        clk,        // 100 MHz system clock
    input   wire        rst_n,      // Active-low reset
    input   wire [15:0] data_in,    // Input sample
    output  wire [31:0] data_out,   // Filter output
    input   wire        valid_in,   // Input valid flag
    output  wire        valid_out   // Output valid flag
);

    // Delay line for tapped filter
    reg [15:0] taps[0:7];
    wire [31:0] mac_results[0:7];
    wire [31:0] accumulator;

    // Shift input through delay line
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            taps[0] <= 16'h0;
            taps[1] <= 16'h0;
            taps[2] <= 16'h0;
            taps[3] <= 16'h0;
            taps[4] <= 16'h0;
            taps[5] <= 16'h0;
            taps[6] <= 16'h0;
            taps[7] <= 16'h0;
        end else if (valid_in) begin
            taps[0] <= data_in;
            taps[1] <= taps[0];
            taps[2] <= taps[1];
            taps[3] <= taps[2];
            taps[4] <= taps[3];
            taps[5] <= taps[4];
            taps[6] <= taps[5];
            taps[7] <= taps[6];
        end
    end

    // Create 8 MAC units (multiply-accumulate using DSP blocks)
    fir_mac mac0 (.sample(taps[0]), .coeff(16'h0C3B), .mac_in(32'h0), .mac_out(mac_results[0]));
    fir_mac mac1 (.sample(taps[1]), .coeff(16'h1F4A), .mac_in(mac_results[0]), .mac_out(mac_results[1]));
    fir_mac mac2 (.sample(taps[2]), .coeff(16'h2B5C), .mac_in(mac_results[1]), .mac_out(mac_results[2]));
    fir_mac mac3 (.sample(taps[3]), .coeff(16'h2F6D), .mac_in(mac_results[2]), .mac_out(mac_results[3]));
    fir_mac mac4 (.sample(taps[4]), .coeff(16'h2F6D), .mac_in(mac_results[3]), .mac_out(mac_results[4]));
    fir_mac mac5 (.sample(taps[5]), .coeff(16'h2B5C), .mac_in(mac_results[4]), .mac_out(mac_results[5]));
    fir_mac mac6 (.sample(taps[6]), .coeff(16'h1F4A), .mac_in(mac_results[5]), .mac_out(mac_results[6]));
    fir_mac mac7 (.sample(taps[7]), .coeff(16'h0C3B), .mac_in(mac_results[6]), .mac_out(mac_results[7]));

    // Output assignment
    assign data_out = mac_results[7];
    assign valid_out = valid_in;  // Pipelined output

endmodule
