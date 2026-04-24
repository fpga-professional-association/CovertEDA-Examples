// =============================================================================
// Watchdog Timer with Timeout and Reset Output
// Device: Xilinx Artix-7 XC7A35T
// =============================================================================

module timer_watchdog (
    input  wire        clk,
    input  wire        rst_n,
    input  wire [31:0] timeout_val,  // Timeout threshold
    input  wire        kick,         // Watchdog kick/pet (resets counter)
    input  wire        enable,       // Enable watchdog
    output reg         wdt_reset,    // Watchdog timeout reset output
    output reg         wdt_warning,  // Warning (counter > 75% of timeout)
    output reg  [31:0] counter       // Current counter value
);

    wire [31:0] warning_threshold;
    assign warning_threshold = timeout_val - (timeout_val >> 2);  // 75%

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            counter     <= 32'd0;
            wdt_reset   <= 1'b0;
            wdt_warning <= 1'b0;
        end else if (!enable) begin
            counter     <= 32'd0;
            wdt_reset   <= 1'b0;
            wdt_warning <= 1'b0;
        end else if (kick) begin
            counter     <= 32'd0;
            wdt_reset   <= 1'b0;
            wdt_warning <= 1'b0;
        end else begin
            if (counter >= timeout_val && timeout_val != 32'd0) begin
                wdt_reset <= 1'b1;
            end else begin
                counter <= counter + 1'b1;
                wdt_reset <= 1'b0;
            end

            // Warning at 75% of timeout
            if (counter >= warning_threshold && timeout_val != 32'd0) begin
                wdt_warning <= 1'b1;
            end else begin
                wdt_warning <= 1'b0;
            end
        end
    end

endmodule
