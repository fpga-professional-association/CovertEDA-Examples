// 3-Sample Median Filter
// Device: Achronix Speedster7t AC7t1500
// Outputs the median of three consecutive 8-bit samples

module median_filter (
    input        clk,
    input        rst_n,
    input  [7:0] data_in,
    input        data_valid,
    output [7:0] data_out,
    output       data_out_valid
);

    reg [7:0] s0, s1, s2;
    reg [1:0] cnt;
    reg [7:0] median_r;
    reg       valid_r;

    assign data_out       = median_r;
    assign data_out_valid = valid_r;

    // Sorting network for 3 elements
    wire [7:0] lo_01 = (s0 < s1) ? s0 : s1;
    wire [7:0] hi_01 = (s0 < s1) ? s1 : s0;
    wire [7:0] lo_12 = (hi_01 < s2) ? hi_01 : s2;
    wire [7:0] hi_12 = (hi_01 < s2) ? s2 : hi_01;
    wire [7:0] mid   = (lo_01 > lo_12) ? lo_01 : lo_12;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            s0      <= 8'd0;
            s1      <= 8'd0;
            s2      <= 8'd0;
            cnt     <= 2'd0;
            median_r <= 8'd0;
            valid_r <= 1'b0;
        end else begin
            valid_r <= 1'b0;
            if (data_valid) begin
                s2 <= s1;
                s1 <= s0;
                s0 <= data_in;
                if (cnt < 2'd2)
                    cnt <= cnt + 1'b1;
                else begin
                    median_r <= mid;
                    valid_r  <= 1'b1;
                end
            end
        end
    end

endmodule
