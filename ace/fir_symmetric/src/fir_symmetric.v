// 16-Tap Symmetric FIR Filter
// Device: Achronix Speedster7t AC7t1500
// Exploits symmetry: h[k] = h[15-k], so only 8 unique coefficients

module fir_symmetric (
    input                clk,
    input                rst_n,
    input  signed [15:0] data_in,
    input                data_valid,
    output signed [31:0] data_out,
    output               data_out_valid
);

    // 8 unique coefficients (symmetric)
    reg signed [15:0] coeff [0:7];
    reg signed [15:0] sr [0:15];
    reg signed [31:0] accum;
    reg               valid_r;
    reg [4:0]         fill_cnt;

    assign data_out       = accum;
    assign data_out_valid = valid_r;

    // Pre-add symmetric pairs and multiply
    wire signed [16:0] pair [0:7];
    wire signed [31:0] prod [0:7];

    genvar g;
    generate
        for (g = 0; g < 8; g = g + 1) begin : SYM
            assign pair[g] = sr[g] + sr[15-g];
            assign prod[g] = pair[g] * coeff[g];
        end
    endgenerate

    integer i;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (i = 0; i < 16; i = i + 1)
                sr[i] <= 16'd0;
            for (i = 0; i < 8; i = i + 1)
                coeff[i] <= 16'd0;
            accum    <= 32'd0;
            valid_r  <= 1'b0;
            fill_cnt <= 5'd0;
            // Default coefficients (simple low-pass)
            coeff[0] <= 16'd1;
            coeff[1] <= 16'd2;
            coeff[2] <= 16'd3;
            coeff[3] <= 16'd4;
            coeff[4] <= 16'd5;
            coeff[5] <= 16'd4;
            coeff[6] <= 16'd3;
            coeff[7] <= 16'd2;
        end else begin
            valid_r <= 1'b0;
            if (data_valid) begin
                // Shift register
                for (i = 15; i > 0; i = i - 1)
                    sr[i] <= sr[i-1];
                sr[0] <= data_in;

                if (fill_cnt < 5'd15)
                    fill_cnt <= fill_cnt + 1'b1;
                else begin
                    accum <= prod[0] + prod[1] + prod[2] + prod[3] +
                             prod[4] + prod[5] + prod[6] + prod[7];
                    valid_r <= 1'b1;
                end
            end
        end
    end

endmodule
