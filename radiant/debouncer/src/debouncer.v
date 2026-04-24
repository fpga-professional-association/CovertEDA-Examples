// =============================================================================
// Design      : Button Debouncer
// Module      : debouncer
// Description : 4-channel button debouncer with configurable delay
// Device      : LIFCL-40-7BG400I
// Frequency   : 25 MHz
// =============================================================================

module debouncer #(
    parameter DEBOUNCE_BITS = 4   // 2^DEBOUNCE_BITS cycles of stable input
)(
    input   wire        clk,
    input   wire        rst_n,
    input   wire [3:0]  btn_in,       // Raw button inputs
    output  reg  [3:0]  btn_out,      // Debounced outputs
    output  reg  [3:0]  btn_rising,   // Rising edge pulse
    output  reg  [3:0]  btn_falling   // Falling edge pulse
);

    localparam COUNT_MAX = (1 << DEBOUNCE_BITS) - 1;

    reg [DEBOUNCE_BITS-1:0] cnt [0:3];
    reg [3:0] btn_sync0, btn_sync1;
    reg [3:0] btn_prev;

    integer i;

    // Two-stage synchronizer
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            btn_sync0 <= 4'd0;
            btn_sync1 <= 4'd0;
        end else begin
            btn_sync0 <= btn_in;
            btn_sync1 <= btn_sync0;
        end
    end

    // Debounce counter per channel
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (i = 0; i < 4; i = i + 1) begin
                cnt[i]  <= {DEBOUNCE_BITS{1'b0}};
            end
            btn_out <= 4'd0;
        end else begin
            for (i = 0; i < 4; i = i + 1) begin
                if (btn_sync1[i] != btn_out[i]) begin
                    if (cnt[i] == COUNT_MAX[DEBOUNCE_BITS-1:0]) begin
                        btn_out[i] <= btn_sync1[i];
                        cnt[i]     <= {DEBOUNCE_BITS{1'b0}};
                    end else begin
                        cnt[i] <= cnt[i] + 1'b1;
                    end
                end else begin
                    cnt[i] <= {DEBOUNCE_BITS{1'b0}};
                end
            end
        end
    end

    // Edge detection
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            btn_prev    <= 4'd0;
            btn_rising  <= 4'd0;
            btn_falling <= 4'd0;
        end else begin
            btn_prev    <= btn_out;
            btn_rising  <= btn_out & ~btn_prev;
            btn_falling <= ~btn_out & btn_prev;
        end
    end

endmodule
