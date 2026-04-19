// Moving Average Filter - 8-sample, 16-bit
// Quartus / Cyclone IV E (EP4CE6)

module moving_average (
    input         clk,
    input         rst_n,
    input         valid_in,
    input  [15:0] din,
    output [15:0] dout,
    output        valid_out
);

    reg [15:0] samples [0:7];
    reg [2:0]  wr_idx;
    reg [18:0] sum;  // 16 bits + 3 bits for 8 samples
    reg        filled;
    reg [2:0]  sample_count;

    reg [15:0] dout_reg;
    reg        valid_out_reg;

    assign dout      = dout_reg;
    assign valid_out = valid_out_reg;

    integer i;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            wr_idx        <= 3'd0;
            sum           <= 19'd0;
            filled        <= 1'b0;
            sample_count  <= 3'd0;
            dout_reg      <= 16'd0;
            valid_out_reg <= 1'b0;
            for (i = 0; i < 8; i = i + 1)
                samples[i] <= 16'd0;
        end else begin
            valid_out_reg <= 1'b0;

            if (valid_in) begin
                // Subtract the oldest sample, add the new one
                sum <= sum - {3'b0, samples[wr_idx]} + {3'b0, din};
                samples[wr_idx] <= din;
                wr_idx <= wr_idx + 3'd1;

                if (!filled) begin
                    sample_count <= sample_count + 3'd1;
                    if (sample_count == 3'd7)
                        filled <= 1'b1;
                end

                // Output average (divide by 8 = right shift 3)
                if (filled) begin
                    dout_reg <= (sum - {3'b0, samples[wr_idx]} + {3'b0, din}) >> 3;
                    valid_out_reg <= 1'b1;
                end
            end
        end
    end

endmodule
