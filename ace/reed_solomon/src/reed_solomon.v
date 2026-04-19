// RS(255,223) Encoder - Simplified GF(2^8) Implementation
// Device: Achronix Speedster7t AC7t1500
// Generates 32 parity bytes for 223 data bytes

module reed_solomon (
    input        clk,
    input        rst_n,
    input  [7:0] data_in,
    input        data_valid,
    input        sof,         // start of frame
    output [7:0] parity_out,
    output       parity_valid,
    output       busy
);

    localparam N_PARITY = 32;

    reg [7:0] syndrome [0:N_PARITY-1];
    reg [7:0] byte_cnt;
    reg [1:0] state;
    reg [4:0] parity_idx;
    reg [7:0] parity_r;
    reg       parity_v;

    localparam S_IDLE   = 2'd0;
    localparam S_DATA   = 2'd1;
    localparam S_PARITY = 2'd2;

    assign busy         = (state != S_IDLE);
    assign parity_out   = parity_r;
    assign parity_valid = parity_v;

    // Simplified GF(2^8) multiply by alpha (x^8 + x^4 + x^3 + x^2 + 1)
    function [7:0] gf_mul2;
        input [7:0] a;
        begin
            if (a[7])
                gf_mul2 = (a << 1) ^ 8'h1D;
            else
                gf_mul2 = a << 1;
        end
    endfunction

    integer i;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state     <= S_IDLE;
            byte_cnt  <= 8'd0;
            parity_idx <= 5'd0;
            parity_r  <= 8'd0;
            parity_v  <= 1'b0;
            for (i = 0; i < N_PARITY; i = i + 1)
                syndrome[i] <= 8'd0;
        end else begin
            parity_v <= 1'b0;
            case (state)
                S_IDLE: begin
                    if (sof && data_valid) begin
                        for (i = 0; i < N_PARITY; i = i + 1)
                            syndrome[i] <= 8'd0;
                        byte_cnt <= 8'd1;
                        // Feed first byte
                        syndrome[0] <= data_in;
                        state <= S_DATA;
                    end
                end
                S_DATA: begin
                    if (data_valid) begin
                        // LFSR shift with feedback
                        syndrome[0] <= data_in ^ gf_mul2(syndrome[N_PARITY-1]);
                        for (i = 1; i < N_PARITY; i = i + 1)
                            syndrome[i] <= syndrome[i-1] ^ gf_mul2(syndrome[N_PARITY-1]);
                        byte_cnt <= byte_cnt + 1'b1;
                        if (byte_cnt == 8'd222)
                            state <= S_PARITY;
                    end
                end
                S_PARITY: begin
                    parity_r   <= syndrome[parity_idx];
                    parity_v   <= 1'b1;
                    parity_idx <= parity_idx + 1'b1;
                    if (parity_idx == N_PARITY - 1) begin
                        state      <= S_IDLE;
                        parity_idx <= 5'd0;
                    end
                end
            endcase
        end
    end

endmodule
