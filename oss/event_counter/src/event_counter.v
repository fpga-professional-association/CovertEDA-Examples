// Multi-Channel Event Counter with Latch
// Device: iCE40UP5K
// 4-channel event counter with snapshot latch

module event_counter (
    input         clk,
    input         rst_n,
    input  [3:0]  events,      // 4 event inputs
    input         latch,       // capture snapshot
    input         clear,       // clear all counters
    input  [1:0]  read_sel,    // select channel to read
    output [15:0] count_out,
    output        count_valid
);

    reg [15:0] counters [0:3];
    reg [15:0] latched  [0:3];
    reg [3:0]  events_prev;
    reg [15:0] read_r;
    reg        valid_r;

    assign count_out   = read_r;
    assign count_valid = valid_r;

    integer i;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (i = 0; i < 4; i = i + 1) begin
                counters[i] <= 16'd0;
                latched[i]  <= 16'd0;
            end
            events_prev <= 4'd0;
            read_r      <= 16'd0;
            valid_r     <= 1'b0;
        end else begin
            valid_r     <= 1'b0;
            events_prev <= events;

            if (clear) begin
                for (i = 0; i < 4; i = i + 1)
                    counters[i] <= 16'd0;
            end else begin
                // Count rising edges on each channel
                for (i = 0; i < 4; i = i + 1) begin
                    if (events[i] && !events_prev[i])
                        if (counters[i] < 16'hFFFF)
                            counters[i] <= counters[i] + 1'b1;
                end
            end

            if (latch) begin
                for (i = 0; i < 4; i = i + 1)
                    latched[i] <= counters[i];
            end

            // Read latched value
            read_r  <= latched[read_sel];
            valid_r <= 1'b1;
        end
    end

endmodule
