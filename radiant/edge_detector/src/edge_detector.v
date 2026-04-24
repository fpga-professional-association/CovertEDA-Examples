// =============================================================================
// Design      : Edge Detector
// Module      : edge_detector
// Description : Multi-channel edge detector (rising/falling/both)
// Device      : LIFCL-40-7BG400I
// Frequency   : 25 MHz
// =============================================================================

module edge_detector #(
    parameter CHANNELS = 4
)(
    input   wire                    clk,
    input   wire                    rst_n,
    input   wire [CHANNELS-1:0]     sig_in,        // Input signals
    input   wire [1:0]              mode,           // 00=rising, 01=falling, 10=both, 11=off
    output  reg  [CHANNELS-1:0]     edge_detect,   // Edge detected pulse
    output  reg  [CHANNELS-1:0]     edge_rising,   // Rising edge pulse
    output  reg  [CHANNELS-1:0]     edge_falling   // Falling edge pulse
);

    reg [CHANNELS-1:0] sig_sync0, sig_sync1, sig_prev;
    wire [CHANNELS-1:0] rising, falling;

    // Two-stage synchronizer
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sig_sync0 <= {CHANNELS{1'b0}};
            sig_sync1 <= {CHANNELS{1'b0}};
        end else begin
            sig_sync0 <= sig_in;
            sig_sync1 <= sig_sync0;
        end
    end

    // Previous value register
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sig_prev <= {CHANNELS{1'b0}};
        end else begin
            sig_prev <= sig_sync1;
        end
    end

    assign rising  = sig_sync1 & ~sig_prev;
    assign falling = ~sig_sync1 & sig_prev;

    // Edge detection output based on mode
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            edge_detect  <= {CHANNELS{1'b0}};
            edge_rising  <= {CHANNELS{1'b0}};
            edge_falling <= {CHANNELS{1'b0}};
        end else begin
            edge_rising  <= rising;
            edge_falling <= falling;
            case (mode)
                2'b00:   edge_detect <= rising;
                2'b01:   edge_detect <= falling;
                2'b10:   edge_detect <= rising | falling;
                2'b11:   edge_detect <= {CHANNELS{1'b0}};
                default: edge_detect <= {CHANNELS{1'b0}};
            endcase
        end
    end

endmodule
