// =============================================================================
// Design      : Programmable Timer/Counter
// Module      : counter_timer
// Description : 32-bit timer/counter with prescaler and compare match output
// Device      : LIFCL-40-7BG400I
// Frequency   : 25 MHz
// =============================================================================

module counter_timer (
    input   wire        clk,
    input   wire        rst_n,
    input   wire        enable,
    input   wire [7:0]  prescaler,      // Clock divider value
    input   wire [31:0] compare_val,    // Compare match value
    input   wire        clear,          // Synchronous counter clear
    output  reg  [31:0] count,          // Current counter value
    output  reg         match,          // Compare match output
    output  reg         overflow        // Counter overflow flag
);

    reg [7:0] prescale_cnt;
    wire      prescale_tick;

    // Prescaler divider
    assign prescale_tick = (prescale_cnt == prescaler);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            prescale_cnt <= 8'd0;
        end else if (enable) begin
            if (prescale_tick || clear) begin
                prescale_cnt <= 8'd0;
            end else begin
                prescale_cnt <= prescale_cnt + 8'd1;
            end
        end
    end

    // Main 32-bit counter
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            count    <= 32'd0;
            overflow <= 1'b0;
        end else if (clear) begin
            count    <= 32'd0;
            overflow <= 1'b0;
        end else if (enable && prescale_tick) begin
            if (count == 32'hFFFFFFFF) begin
                count    <= 32'd0;
                overflow <= 1'b1;
            end else begin
                count    <= count + 32'd1;
                overflow <= 1'b0;
            end
        end else begin
            overflow <= 1'b0;
        end
    end

    // Compare match
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            match <= 1'b0;
        end else begin
            match <= (count == compare_val) && enable;
        end
    end

endmodule
