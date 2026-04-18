// =============================================================================
// Design      : DSP FIR Filter
// Module      : fir_top
// Description : 8-tap FIR filter using pipelined MAC operations
// Device      : LIFCL-40-7BG400I
// Frequency   : 50 MHz
// Bit Width   : 16-bit input, 32-bit output
// =============================================================================

module fir_top (
    input   wire        clk,        // System clock
    input   wire        rst_n,      // Active-low reset
    input   wire [15:0] data_in,    // Input sample
    output  wire [31:0] data_out,   // Filter output
    input   wire        valid_in,   // Input valid flag
    output  wire        valid_out   // Output valid flag
);

    // Delay line for tapped filter
    reg [15:0] taps[0:7];
    wire [31:0] mac_results[0:7];
    wire [15:0] coeffs[0:7];

    // Coefficient ROM instances (one per tap for parallel access)
    genvar ci;
    generate
        for (ci = 0; ci < 8; ci = ci + 1) begin : coeff_gen
            coeff_rom coeff_i (.addr(ci[2:0]), .coeff(coeffs[ci]));
        end
    endgenerate

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

    // Create 8 pipelined MAC units using ROM coefficients
    fir_mac mac0 (.clk(clk), .rst_n(rst_n), .sample(taps[0]), .coeff(coeffs[0]), .mac_in(32'h0),           .mac_out(mac_results[0]));
    fir_mac mac1 (.clk(clk), .rst_n(rst_n), .sample(taps[1]), .coeff(coeffs[1]), .mac_in(mac_results[0]), .mac_out(mac_results[1]));
    fir_mac mac2 (.clk(clk), .rst_n(rst_n), .sample(taps[2]), .coeff(coeffs[2]), .mac_in(mac_results[1]), .mac_out(mac_results[2]));
    fir_mac mac3 (.clk(clk), .rst_n(rst_n), .sample(taps[3]), .coeff(coeffs[3]), .mac_in(mac_results[2]), .mac_out(mac_results[3]));
    fir_mac mac4 (.clk(clk), .rst_n(rst_n), .sample(taps[4]), .coeff(coeffs[4]), .mac_in(mac_results[3]), .mac_out(mac_results[4]));
    fir_mac mac5 (.clk(clk), .rst_n(rst_n), .sample(taps[5]), .coeff(coeffs[5]), .mac_in(mac_results[4]), .mac_out(mac_results[5]));
    fir_mac mac6 (.clk(clk), .rst_n(rst_n), .sample(taps[6]), .coeff(coeffs[6]), .mac_in(mac_results[5]), .mac_out(mac_results[6]));
    fir_mac mac7 (.clk(clk), .rst_n(rst_n), .sample(taps[7]), .coeff(coeffs[7]), .mac_in(mac_results[6]), .mac_out(mac_results[7]));

    // Output assignment
    assign data_out = mac_results[7];

    // Valid pipeline (8 MAC stages of latency)
    reg [7:0] valid_pipe;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            valid_pipe <= 8'h0;
        else
            valid_pipe <= {valid_pipe[6:0], valid_in};
    end
    assign valid_out = valid_pipe[7];

endmodule
