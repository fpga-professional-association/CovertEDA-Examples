// =============================================================================
// Design      : Frequency Counter
// Module      : frequency_counter
// Description : Frequency counter measuring input signal period
// Device      : LIFCL-40-7BG400I
// Frequency   : 25 MHz
// =============================================================================

module frequency_counter #(
    parameter GATE_BITS = 8  // Gate time = 2^GATE_BITS clock cycles
)(
    input   wire        clk,
    input   wire        rst_n,
    input   wire        sig_in,         // Signal to measure
    output  reg  [31:0] freq_count,     // Measured edge count in gate period
    output  reg  [31:0] period_count,   // Clock cycles between rising edges
    output  reg         valid           // Measurement valid strobe
);

    reg sig_sync0, sig_sync1, sig_sync2;
    wire sig_rising;

    reg [GATE_BITS-1:0] gate_cnt;
    reg [31:0] edge_cnt;
    reg [31:0] period_cnt;
    reg [31:0] period_lat;
    reg        gate_active;

    // Double-sync the input signal
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sig_sync0 <= 1'b0;
            sig_sync1 <= 1'b0;
            sig_sync2 <= 1'b0;
        end else begin
            sig_sync0 <= sig_in;
            sig_sync1 <= sig_sync0;
            sig_sync2 <= sig_sync1;
        end
    end

    assign sig_rising = sig_sync1 & ~sig_sync2;

    // Gate timer
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            gate_cnt    <= {GATE_BITS{1'b0}};
            gate_active <= 1'b1;
        end else begin
            gate_cnt <= gate_cnt + 1'b1;
            if (gate_cnt == {GATE_BITS{1'b1}})
                gate_active <= 1'b1;
        end
    end

    // Edge counter within gate period
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            edge_cnt   <= 32'd0;
            freq_count <= 32'd0;
            valid      <= 1'b0;
        end else begin
            if (gate_cnt == {GATE_BITS{1'b1}}) begin
                freq_count <= edge_cnt;
                edge_cnt   <= 32'd0;
                valid      <= 1'b1;
            end else begin
                if (sig_rising)
                    edge_cnt <= edge_cnt + 32'd1;
                valid <= 1'b0;
            end
        end
    end

    // Period measurement (clocks between rising edges)
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            period_cnt   <= 32'd0;
            period_count <= 32'd0;
        end else begin
            if (sig_rising) begin
                period_count <= period_cnt;
                period_cnt   <= 32'd1;
            end else begin
                period_cnt <= period_cnt + 32'd1;
            end
        end
    end

endmodule
