// =============================================================================
// PWM Input Measurement (Period + Duty Cycle)
// Device: Xilinx Artix-7 XC7A35T
// Measures period and high-time of an input signal in clock cycles
// =============================================================================

module pulse_width_measure (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        signal_in,    // PWM input signal
    output reg  [31:0] period,       // Measured period in clock cycles
    output reg  [31:0] high_time,    // Measured high time in clock cycles
    output reg         valid         // New measurement available
);

    // Synchronizer for input signal
    reg sig_sync1, sig_sync2;
    reg sig_prev;

    wire sig_rise = sig_sync2 & ~sig_prev;
    wire sig_fall = ~sig_sync2 & sig_prev;

    // Counters
    reg [31:0] period_cnt;
    reg [31:0] high_cnt;
    reg        measuring;

    // Synchronize input
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sig_sync1 <= 1'b0;
            sig_sync2 <= 1'b0;
            sig_prev  <= 1'b0;
        end else begin
            sig_sync1 <= signal_in;
            sig_sync2 <= sig_sync1;
            sig_prev  <= sig_sync2;
        end
    end

    // Period and high-time measurement
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            period_cnt <= 32'd0;
            high_cnt   <= 32'd0;
            period     <= 32'd0;
            high_time  <= 32'd0;
            valid      <= 1'b0;
            measuring  <= 1'b0;
        end else begin
            valid <= 1'b0;

            if (sig_rise) begin
                if (measuring) begin
                    // Complete measurement
                    period    <= period_cnt;
                    high_time <= high_cnt;
                    valid     <= 1'b1;
                end
                // Start new measurement
                period_cnt <= 32'd1;
                high_cnt   <= 32'd1;
                measuring  <= 1'b1;
            end else if (measuring) begin
                period_cnt <= period_cnt + 1'b1;
                if (sig_sync2) begin
                    high_cnt <= high_cnt + 1'b1;
                end
            end
        end
    end

endmodule
