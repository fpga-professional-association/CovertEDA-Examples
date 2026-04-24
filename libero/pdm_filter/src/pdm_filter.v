// PDM to PCM Decimation Filter
// Target: MPF100T (PolarFire)
// CIC-like decimation: accumulate PDM bits, decimate by 64

module pdm_filter (
    input         clk,
    input         reset_n,
    input         pdm_in,
    input         pdm_valid,
    output reg [15:0] pcm_out,
    output reg        pcm_valid
);

    localparam DECIMATE = 64;

    reg [15:0] accumulator;
    reg [5:0]  sample_cnt;

    // Simple integrator stage
    reg [15:0] integrator;
    reg [15:0] comb_delay;

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            accumulator <= 16'd0;
            sample_cnt  <= 6'd0;
            pcm_out     <= 16'd0;
            pcm_valid   <= 1'b0;
            integrator  <= 16'd0;
            comb_delay  <= 16'd0;
        end else begin
            pcm_valid <= 1'b0;

            if (pdm_valid) begin
                // Integrate: accumulate PDM samples
                if (pdm_in)
                    integrator <= integrator + 1;

                sample_cnt <= sample_cnt + 1;

                if (sample_cnt == DECIMATE - 1) begin
                    sample_cnt <= 0;
                    // Comb stage: difference from previous
                    pcm_out    <= integrator - comb_delay;
                    comb_delay <= integrator;
                    pcm_valid  <= 1'b1;
                end
            end
        end
    end

endmodule
