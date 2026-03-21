// =============================================================================
// LED Blinker Top Module
// Device: Xilinx Artix-7 XC7A35T-1CPG236C
// Clock: 100 MHz
// =============================================================================

module blinky_top (
    input  wire       clk_in,      // 100 MHz clock input
    input  wire       rst_n,       // Active-low reset
    output wire [3:0] led_out,     // 4 LEDs (LEDS4, LEDS3, LEDS2, LEDS1)
    input  wire [1:0] btn_in       // 2 push buttons for mode select
);

    parameter PRESCALE_WIDTH = 27;
    parameter MAX_COUNT = 27'd100_000_000; // 100M / 100M = 1 second prescaler

    reg [PRESCALE_WIDTH-1:0] prescaler_cnt;
    reg [1:0]                mode_reg;
    reg [3:0]                led_reg;

    // Synchronize button input (debounce)
    reg [1:0] btn_sync_r;
    reg [1:0] btn_sync_rr;
    wire [1:0] btn_sync = btn_sync_rr;

    // Debounced button
    reg [1:0] btn_edge;
    reg [1:0] btn_prev;

    always @(posedge clk_in or negedge rst_n) begin
        if (!rst_n) begin
            btn_sync_r  <= 2'b00;
            btn_sync_rr <= 2'b00;
            btn_prev    <= 2'b00;
            btn_edge    <= 2'b00;
        end else begin
            btn_sync_r  <= btn_in;
            btn_sync_rr <= btn_sync_r;
            btn_prev    <= btn_sync;
            btn_edge    <= btn_sync & ~btn_prev;  // Rising edge detector
        end
    end

    // Mode selection via button
    always @(posedge clk_in or negedge rst_n) begin
        if (!rst_n) begin
            mode_reg <= 2'b00;
        end else if (btn_edge[0]) begin
            mode_reg <= mode_reg + 1'b1;
        end
    end

    // Prescaler and LED pattern generation
    always @(posedge clk_in or negedge rst_n) begin
        if (!rst_n) begin
            prescaler_cnt <= {PRESCALE_WIDTH{1'b0}};
            led_reg       <= 4'b0001;
        end else begin
            if (prescaler_cnt >= MAX_COUNT) begin
                prescaler_cnt <= {PRESCALE_WIDTH{1'b0}};

                case (mode_reg)
                    2'b00: led_reg <= {led_reg[2:0], led_reg[3]};      // Rotate left
                    2'b01: led_reg <= {led_reg[0], led_reg[3:1]};      // Rotate right
                    2'b10: led_reg <= led_reg ^ 4'b1111;               // Toggle all
                    2'b11: led_reg <= led_reg + 1'b1;                  // Count up
                endcase
            end else begin
                prescaler_cnt <= prescaler_cnt + 1'b1;
            end
        end
    end

    assign led_out = led_reg;

endmodule
