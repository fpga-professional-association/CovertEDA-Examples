// RGB to YCbCr Color Space Converter - 8-bit per channel
// Target: LFE5U-25F (ECP5)
// ITU-R BT.601 approximation using fixed-point arithmetic

module color_space_conv (
    input        clk,
    input        reset_n,
    input        valid_in,
    input  [7:0] r_in,
    input  [7:0] g_in,
    input  [7:0] b_in,
    output reg [7:0] y_out,
    output reg [7:0] cb_out,
    output reg [7:0] cr_out,
    output reg       valid_out
);

    // Fixed-point coefficients (Q8 format, multiply then >>8)
    // Y  =  0.299*R + 0.587*G + 0.114*B
    // Cb = -0.169*R - 0.331*G + 0.500*B + 128
    // Cr =  0.500*R - 0.419*G - 0.081*B + 128
    localparam signed [15:0] COEFF_YR  = 16'd77;   // 0.299 * 256
    localparam signed [15:0] COEFF_YG  = 16'd150;  // 0.587 * 256
    localparam signed [15:0] COEFF_YB  = 16'd29;   // 0.114 * 256

    localparam signed [15:0] COEFF_CBR = -16'sd43;  // -0.169 * 256
    localparam signed [15:0] COEFF_CBG = -16'sd85;  // -0.331 * 256
    localparam signed [15:0] COEFF_CBB = 16'd128;   //  0.500 * 256

    localparam signed [15:0] COEFF_CRR = 16'd128;   //  0.500 * 256
    localparam signed [15:0] COEFF_CRG = -16'sd107; // -0.419 * 256
    localparam signed [15:0] COEFF_CRB = -16'sd21;  // -0.081 * 256

    reg signed [23:0] y_calc, cb_calc, cr_calc;

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            y_out     <= 8'd0;
            cb_out    <= 8'd0;
            cr_out    <= 8'd0;
            valid_out <= 1'b0;
        end else begin
            valid_out <= valid_in;
            if (valid_in) begin
                y_calc  = COEFF_YR * r_in + COEFF_YG * g_in + COEFF_YB * b_in;
                cb_calc = COEFF_CBR * r_in + COEFF_CBG * g_in + COEFF_CBB * b_in + (128 << 8);
                cr_calc = COEFF_CRR * r_in + COEFF_CRG * g_in + COEFF_CRB * b_in + (128 << 8);

                // Clamp to 0-255
                y_out  <= (y_calc[23]) ? 8'd0 : (y_calc[23:8] > 255) ? 8'd255 : y_calc[15:8];
                cb_out <= (cb_calc[23]) ? 8'd0 : (cb_calc[23:8] > 255) ? 8'd255 : cb_calc[15:8];
                cr_out <= (cr_calc[23]) ? 8'd0 : (cr_calc[23:8] > 255) ? 8'd255 : cr_calc[15:8];
            end
        end
    end

endmodule
