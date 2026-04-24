// =============================================================================
// 2nd-Order IIR Biquad Filter, 16-bit
// Device: Xilinx Artix-7 XC7A35T
// Transfer: y[n] = b0*x[n] + b1*x[n-1] + b2*x[n-2] - a1*y[n-1] - a2*y[n-2]
// Fixed-point Q1.14 coefficients
// =============================================================================

module iir_filter (
    input  wire        clk,
    input  wire        rst_n,
    input  wire signed [15:0] x_in,
    input  wire        valid_in,
    output reg  signed [15:0] y_out,
    output reg         valid_out
);

    // Coefficients (Q1.14 format, loaded as parameters for testability)
    parameter signed [15:0] B0 = 16'sd4096;   // ~0.25
    parameter signed [15:0] B1 = 16'sd8192;   // ~0.50
    parameter signed [15:0] B2 = 16'sd4096;   // ~0.25
    parameter signed [15:0] A1 = 16'sd0;      // 0
    parameter signed [15:0] A2 = 16'sd0;      // 0

    // State registers
    reg signed [15:0] x_d1, x_d2;  // x[n-1], x[n-2]
    reg signed [15:0] y_d1, y_d2;  // y[n-1], y[n-2]

    // Intermediate products (32-bit to hold multiplication result)
    wire signed [31:0] prod_b0, prod_b1, prod_b2;
    wire signed [31:0] prod_a1, prod_a2;

    assign prod_b0 = B0 * x_in;
    assign prod_b1 = B1 * x_d1;
    assign prod_b2 = B2 * x_d2;
    assign prod_a1 = A1 * y_d1;
    assign prod_a2 = A2 * y_d2;

    wire signed [31:0] sum;
    assign sum = prod_b0 + prod_b1 + prod_b2 - prod_a1 - prod_a2;

    // Scale back from Q1.14: shift right by 14
    wire signed [15:0] y_scaled;
    assign y_scaled = sum[29:14];

    // Pipeline register
    reg pipe_valid;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            x_d1      <= 16'sd0;
            x_d2      <= 16'sd0;
            y_d1      <= 16'sd0;
            y_d2      <= 16'sd0;
            y_out     <= 16'sd0;
            valid_out <= 1'b0;
            pipe_valid <= 1'b0;
        end else begin
            pipe_valid <= valid_in;
            valid_out  <= pipe_valid;

            if (valid_in) begin
                // Update delay line
                x_d1 <= x_in;
                x_d2 <= x_d1;
                y_d1 <= y_scaled;
                y_d2 <= y_d1;
            end

            if (pipe_valid) begin
                y_out <= y_scaled;
            end
        end
    end

endmodule
