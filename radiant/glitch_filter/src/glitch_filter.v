// =============================================================================
// Design      : Glitch Filter
// Module      : glitch_filter
// Description : Digital glitch filter with configurable threshold
// Device      : LIFCL-40-7BG400I
// Frequency   : 25 MHz
// =============================================================================

module glitch_filter #(
    parameter WIDTH     = 4,       // Number of filter channels
    parameter CNT_BITS  = 4        // 2^CNT_BITS clock cycles threshold
)(
    input   wire                clk,
    input   wire                rst_n,
    input   wire [WIDTH-1:0]    sig_in,        // Raw input signals
    input   wire [CNT_BITS-1:0] threshold,     // Number of stable cycles required
    output  reg  [WIDTH-1:0]    sig_out,       // Filtered output signals
    output  reg  [WIDTH-1:0]    glitch_flag    // Glitch detected flag (pulse)
);

    reg [WIDTH-1:0] sig_sync0, sig_sync1;
    reg [CNT_BITS-1:0] cnt [0:WIDTH-1];
    reg [WIDTH-1:0] sig_prev;

    integer i;

    // Two-stage synchronizer
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sig_sync0 <= {WIDTH{1'b0}};
            sig_sync1 <= {WIDTH{1'b0}};
        end else begin
            sig_sync0 <= sig_in;
            sig_sync1 <= sig_sync0;
        end
    end

    // Glitch filter logic
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sig_out     <= {WIDTH{1'b0}};
            glitch_flag <= {WIDTH{1'b0}};
            sig_prev    <= {WIDTH{1'b0}};
            for (i = 0; i < WIDTH; i = i + 1)
                cnt[i] <= {CNT_BITS{1'b0}};
        end else begin
            sig_prev <= sig_sync1;
            for (i = 0; i < WIDTH; i = i + 1) begin
                if (sig_sync1[i] != sig_out[i]) begin
                    // Input differs from output -- count stable time
                    if (cnt[i] >= threshold) begin
                        // Threshold met: accept the new value
                        sig_out[i]     <= sig_sync1[i];
                        cnt[i]         <= {CNT_BITS{1'b0}};
                        glitch_flag[i] <= 1'b0;
                    end else if (sig_sync1[i] == sig_prev[i]) begin
                        // Input stable: increment counter
                        cnt[i]         <= cnt[i] + 1'b1;
                        glitch_flag[i] <= 1'b0;
                    end else begin
                        // Input bounced: reset counter and flag glitch
                        cnt[i]         <= {CNT_BITS{1'b0}};
                        glitch_flag[i] <= 1'b1;
                    end
                end else begin
                    cnt[i]         <= {CNT_BITS{1'b0}};
                    glitch_flag[i] <= 1'b0;
                end
            end
        end
    end

endmodule
