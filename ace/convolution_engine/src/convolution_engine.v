// 3x3 Convolution Engine for Image Processing
// Device: Achronix Speedster7t AC7t1500
// Computes weighted sum of 9 pixel values with signed coefficients

module convolution_engine (
    input             clk,
    input             rst_n,
    input  [7:0]      pixel_in,
    input             pixel_valid,
    input  signed [7:0] coeff_0, coeff_1, coeff_2,
    input  signed [7:0] coeff_3, coeff_4, coeff_5,
    input  signed [7:0] coeff_6, coeff_7, coeff_8,
    output [15:0]     result,
    output            result_valid
);

    // Shift register for 9 pixels (3x3 window serialized)
    reg [7:0] sr [0:8];
    reg [3:0] cnt;
    reg       computing;

    reg signed [15:0] accum;
    reg               result_v;

    assign result       = accum[15:0];
    assign result_valid = result_v;

    integer i;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (i = 0; i < 9; i = i + 1)
                sr[i] <= 8'd0;
            cnt       <= 4'd0;
            computing <= 1'b0;
            accum     <= 16'd0;
            result_v  <= 1'b0;
        end else begin
            result_v <= 1'b0;
            if (pixel_valid) begin
                // Shift new pixel in
                for (i = 8; i > 0; i = i - 1)
                    sr[i] <= sr[i-1];
                sr[0] <= pixel_in;

                if (cnt < 4'd8)
                    cnt <= cnt + 1'b1;
                else
                    computing <= 1'b1;
            end

            if (computing && pixel_valid) begin
                accum <= $signed({1'b0, sr[0]}) * coeff_0 +
                         $signed({1'b0, sr[1]}) * coeff_1 +
                         $signed({1'b0, sr[2]}) * coeff_2 +
                         $signed({1'b0, sr[3]}) * coeff_3 +
                         $signed({1'b0, sr[4]}) * coeff_4 +
                         $signed({1'b0, sr[5]}) * coeff_5 +
                         $signed({1'b0, sr[6]}) * coeff_6 +
                         $signed({1'b0, sr[7]}) * coeff_7 +
                         $signed({1'b0, sr[8]}) * coeff_8;
                result_v <= 1'b1;
            end
        end
    end

endmodule
