// SHA-256 Single-Block Hash Engine
// Target: LFE5U-85F (ECP5)
// Simplified: processes one 512-bit block, outputs 256-bit hash

module sha256_hash (
    input         clk,
    input         reset_n,
    input  [31:0] msg_word,
    input  [3:0]  msg_addr,     // 0-15: message word index
    input         msg_wr,
    input         start,
    output reg [255:0] hash_out,
    output reg         done
);

    // Initial hash values (first 32 bits of fractional parts of sqrt of first 8 primes)
    localparam H0 = 32'h6a09e667, H1 = 32'hbb67ae85;
    localparam H2 = 32'h3c6ef372, H3 = 32'ha54ff53a;
    localparam H4 = 32'h510e527f, H5 = 32'h9b05688c;
    localparam H6 = 32'h1f83d9ab, H7 = 32'h5be0cd19;

    reg [511:0] w_flat;      // Message schedule (16 x 32-bit words, packed)
    reg [31:0] a, b, c, d, e, f, g, h;
    reg [5:0]  round;
    reg        busy;

    // Simplified round constant (just use round number for simulation)
    wire [31:0] k;
    assign k = {26'd0, round};

    // SHA-256 functions
    function [31:0] ch;
        input [31:0] x, y, z;
        begin ch = (x & y) ^ (~x & z); end
    endfunction

    function [31:0] maj;
        input [31:0] x, y, z;
        begin maj = (x & y) ^ (x & z) ^ (y & z); end
    endfunction

    function [31:0] sigma0;
        input [31:0] x;
        begin sigma0 = {x[1:0], x[31:2]} ^ {x[12:0], x[31:13]} ^ (x >> 22); end
    endfunction

    function [31:0] sigma1;
        input [31:0] x;
        begin sigma1 = {x[5:0], x[31:6]} ^ {x[10:0], x[31:11]} ^ (x >> 25); end
    endfunction

    integer i;

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            hash_out <= 256'd0;
            done     <= 1'b0;
            busy     <= 1'b0;
            round    <= 6'd0;
            a <= 0; b <= 0; c <= 0; d <= 0;
            e <= 0; f <= 0; g <= 0; h <= 0;
            w_flat   <= 512'd0;
        end else begin
            done <= 1'b0;

            // Message loading
            if (msg_wr && !busy)
                w_flat[msg_addr*32 +: 32] <= msg_word;

            if (start && !busy) begin
                a <= H0; b <= H1; c <= H2; d <= H3;
                e <= H4; f <= H5; g <= H6; h <= H7;
                round <= 0;
                busy  <= 1;
            end else if (busy) begin
                if (round < 16) begin
                    // Compression round using message words
                    h <= g;
                    g <= f;
                    f <= e;
                    e <= d + sigma1(e) + ch(e, f, g) + k + w_flat[round[3:0]*32 +: 32];
                    d <= c;
                    c <= b;
                    b <= a;
                    a <= sigma0(a) + maj(a, b, c) + sigma1(e) + ch(e, f, g) + k + w_flat[round[3:0]*32 +: 32];
                    round <= round + 1;
                end else begin
                    hash_out <= {(H0+a), (H1+b), (H2+c), (H3+d),
                                 (H4+e), (H5+f), (H6+g), (H7+h)};
                    done <= 1;
                    busy <= 0;
                end
            end
        end
    end

endmodule
