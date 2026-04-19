// Token Bucket Rate Limiter
// Device: Achronix Speedster7t AC7t1500
// Allows/blocks requests based on token availability

module rate_limiter (
    input         clk,
    input         rst_n,
    input  [7:0]  max_tokens,
    input  [7:0]  refill_rate,   // tokens added per refill_interval cycles
    input  [15:0] refill_interval,
    input         request,
    output        grant,
    output [7:0]  token_count
);

    reg [7:0]  tokens;
    reg [15:0] refill_cnt;
    reg        grant_r;

    assign grant       = grant_r;
    assign token_count = tokens;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            tokens     <= max_tokens;
            refill_cnt <= 16'd0;
            grant_r    <= 1'b0;
        end else begin
            grant_r <= 1'b0;

            // Refill timer
            if (refill_cnt >= refill_interval) begin
                refill_cnt <= 16'd0;
                if (tokens + refill_rate > max_tokens)
                    tokens <= max_tokens;
                else
                    tokens <= tokens + refill_rate;
            end else begin
                refill_cnt <= refill_cnt + 1'b1;
            end

            // Grant request if tokens available
            if (request && tokens > 8'd0) begin
                tokens  <= tokens - 1'b1;
                grant_r <= 1'b1;
            end
        end
    end

endmodule
