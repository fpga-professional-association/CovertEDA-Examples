// Digital Phase Frequency Detector
// Device: iCE40UP5K
// Outputs UP/DOWN pulses based on phase difference between ref and fb clocks

module phase_detector (
    input      clk,
    input      rst_n,
    input      ref_clk,
    input      fb_clk,
    output     up,
    output     down,
    output reg [15:0] phase_diff
);

    reg ref_prev, fb_prev;
    reg up_r, down_r;
    reg [15:0] ref_cnt, fb_cnt;

    assign up   = up_r;
    assign down = down_r;

    // Edge detection
    wire ref_rising = ref_clk & ~ref_prev;
    wire fb_rising  = fb_clk  & ~fb_prev;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            ref_prev   <= 1'b0;
            fb_prev    <= 1'b0;
            up_r       <= 1'b0;
            down_r     <= 1'b0;
            ref_cnt    <= 16'd0;
            fb_cnt     <= 16'd0;
            phase_diff <= 16'd0;
        end else begin
            ref_prev <= ref_clk;
            fb_prev  <= fb_clk;

            // Classic PFD logic
            if (ref_rising && fb_rising) begin
                up_r   <= 1'b0;
                down_r <= 1'b0;
                phase_diff <= (ref_cnt > fb_cnt) ?
                              (ref_cnt - fb_cnt) : (fb_cnt - ref_cnt);
                ref_cnt <= 16'd0;
                fb_cnt  <= 16'd0;
            end else if (ref_rising) begin
                up_r    <= 1'b1;
                ref_cnt <= 16'd0;
            end else if (fb_rising) begin
                down_r <= 1'b1;
                fb_cnt <= 16'd0;
            end else begin
                ref_cnt <= ref_cnt + 1'b1;
                fb_cnt  <= fb_cnt + 1'b1;
            end
        end
    end

endmodule
