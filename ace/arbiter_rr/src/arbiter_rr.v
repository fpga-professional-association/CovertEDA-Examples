// 8-Port Round-Robin Arbiter
// Device: Achronix Speedster7t AC7t1500
// Fair scheduling across 8 request ports

module arbiter_rr (
    input        clk,
    input        rst_n,
    input  [7:0] request,
    output [7:0] grant,
    output [2:0] grant_id,
    output       grant_valid
);

    reg [2:0] last_grant;
    reg [7:0] grant_r;
    reg [2:0] grant_id_r;
    reg       grant_valid_r;

    assign grant       = grant_r;
    assign grant_id    = grant_id_r;
    assign grant_valid = grant_valid_r;

    // Masked request: mask out ports at or below last_grant
    wire [7:0] mask;
    wire [7:0] masked_req;
    wire [7:0] unmasked_req;

    genvar g;
    generate
        for (g = 0; g < 8; g = g + 1) begin : MASK
            assign mask[g] = (g[2:0] > last_grant) ? 1'b1 : 1'b0;
        end
    endgenerate

    assign masked_req   = request & mask;
    assign unmasked_req = request;

    // Priority encoder for masked requests (higher-priority ports first)
    function [2:0] find_first;
        input [7:0] req;
        integer i;
        begin
            find_first = 3'd0;
            for (i = 7; i >= 0; i = i - 1)
                if (req[i]) find_first = i[2:0];
        end
    endfunction

    wire [2:0] masked_winner   = find_first(masked_req);
    wire [2:0] unmasked_winner = find_first(unmasked_req);
    wire       has_masked      = |masked_req;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            last_grant    <= 3'd7;
            grant_r       <= 8'd0;
            grant_id_r    <= 3'd0;
            grant_valid_r <= 1'b0;
        end else begin
            grant_r       <= 8'd0;
            grant_valid_r <= 1'b0;

            if (|request) begin
                if (has_masked) begin
                    grant_r[masked_winner] <= 1'b1;
                    grant_id_r    <= masked_winner;
                    last_grant    <= masked_winner;
                end else begin
                    grant_r[unmasked_winner] <= 1'b1;
                    grant_id_r    <= unmasked_winner;
                    last_grant    <= unmasked_winner;
                end
                grant_valid_r <= 1'b1;
            end
        end
    end

endmodule
