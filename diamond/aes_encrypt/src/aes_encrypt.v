// AES-128 Encryption - Round-based implementation
// Target: LFE5U-85F (ECP5)
// Simplified: SubBytes uses a small combinational S-box approximation

module aes_encrypt (
    input         clk,
    input         reset_n,
    input  [127:0] plaintext,
    input  [127:0] key,
    input          start,
    output reg [127:0] ciphertext,
    output reg         done
);

    reg [3:0]   round;
    reg [127:0] state;
    reg [127:0] round_key;
    reg         busy;

    // Simplified S-box: XOR-based substitution for simulation
    function [7:0] sbox;
        input [7:0] b;
        begin
            sbox = b ^ {b[6:0], b[7]} ^ {b[5:0], b[7:6]} ^ 8'h63;
        end
    endfunction

    // Apply SubBytes to full state
    function [127:0] sub_bytes;
        input [127:0] s;
        integer i;
        begin
            for (i = 0; i < 16; i = i + 1)
                sub_bytes[i*8 +: 8] = sbox(s[i*8 +: 8]);
        end
    endfunction

    // ShiftRows
    function [127:0] shift_rows;
        input [127:0] s;
        begin
            // Row 0: no shift
            shift_rows[127:120] = s[127:120];
            shift_rows[95:88]   = s[95:88];
            shift_rows[63:56]   = s[63:56];
            shift_rows[31:24]   = s[31:24];
            // Row 1: shift left 1
            shift_rows[119:112] = s[87:80];
            shift_rows[87:80]   = s[55:48];
            shift_rows[55:48]   = s[23:16];
            shift_rows[23:16]   = s[119:112];
            // Row 2: shift left 2
            shift_rows[111:104] = s[47:40];
            shift_rows[47:40]   = s[111:104];
            shift_rows[79:72]   = s[15:8];
            shift_rows[15:8]    = s[79:72];
            // Row 3: shift left 3
            shift_rows[103:96]  = s[7:0];
            shift_rows[71:64]   = s[103:96];
            shift_rows[39:32]   = s[71:64];
            shift_rows[7:0]     = s[39:32];
        end
    endfunction

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            state      <= 128'd0;
            round_key  <= 128'd0;
            round      <= 4'd0;
            ciphertext <= 128'd0;
            done       <= 1'b0;
            busy       <= 1'b0;
        end else begin
            done <= 1'b0;
            if (start && !busy) begin
                state     <= plaintext ^ key;
                round_key <= key;
                round     <= 4'd1;
                busy      <= 1'b1;
            end else if (busy) begin
                if (round <= 4'd10) begin
                    // Simplified round: SubBytes, ShiftRows, AddRoundKey
                    state <= shift_rows(sub_bytes(state)) ^ round_key;
                    round <= round + 1;
                end else begin
                    ciphertext <= state;
                    done       <= 1'b1;
                    busy       <= 1'b0;
                end
            end
        end
    end

endmodule
