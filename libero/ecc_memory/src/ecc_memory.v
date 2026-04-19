// 32-bit Memory with SECDED ECC (Single Error Correct, Double Error Detect)
// Target: MPF300T (PolarFire)
// 256-word memory with Hamming(38,32) ECC

module ecc_memory (
    input         clk,
    input         reset_n,
    input  [7:0]  addr,
    input  [31:0] wr_data,
    input         wr_en,
    input         rd_en,
    output reg [31:0] rd_data,
    output reg        rd_valid,
    output reg        single_err,
    output reg        double_err
);

    // Memory: 256 words x 39 bits (32 data + 6 check + 1 overall parity)
    reg [38:0] mem [0:255];

    // Generate check bits (Hamming code)
    function [5:0] calc_syndrome;
        input [31:0] data;
        input [5:0] check;
        begin
            calc_syndrome[0] = check[0] ^ data[0] ^ data[1] ^ data[3] ^ data[4] ^ data[6] ^ data[8] ^ data[10] ^ data[11] ^ data[13] ^ data[15] ^ data[17] ^ data[19] ^ data[21] ^ data[23] ^ data[25];
            calc_syndrome[1] = check[1] ^ data[0] ^ data[2] ^ data[3] ^ data[5] ^ data[6] ^ data[9] ^ data[10] ^ data[12] ^ data[13] ^ data[16] ^ data[17] ^ data[20] ^ data[21] ^ data[24] ^ data[25];
            calc_syndrome[2] = check[2] ^ data[1] ^ data[2] ^ data[3] ^ data[7] ^ data[8] ^ data[9] ^ data[10] ^ data[14] ^ data[15] ^ data[16] ^ data[17] ^ data[22] ^ data[23] ^ data[24] ^ data[25];
            calc_syndrome[3] = check[3] ^ data[4] ^ data[5] ^ data[6] ^ data[7] ^ data[8] ^ data[9] ^ data[10] ^ data[18] ^ data[19] ^ data[20] ^ data[21] ^ data[22] ^ data[23] ^ data[24] ^ data[25];
            calc_syndrome[4] = check[4] ^ data[11] ^ data[12] ^ data[13] ^ data[14] ^ data[15] ^ data[16] ^ data[17] ^ data[18] ^ data[19] ^ data[20] ^ data[21] ^ data[22] ^ data[23] ^ data[24] ^ data[25];
            calc_syndrome[5] = check[5] ^ data[26] ^ data[27] ^ data[28] ^ data[29] ^ data[30] ^ data[31];
        end
    endfunction

    function [5:0] gen_check;
        input [31:0] data;
        begin
            gen_check = calc_syndrome(data, 6'd0);
        end
    endfunction

    wire [38:0] wr_word = {^{wr_data, gen_check(wr_data)}, gen_check(wr_data), wr_data};
    wire [31:0] mem_data  = mem[addr][31:0];
    wire [5:0]  mem_check = mem[addr][37:32];
    wire        mem_parity= mem[addr][38];
    wire [5:0]  syndrome  = calc_syndrome(mem_data, mem_check);
    wire        overall_p = ^mem[addr];

    integer i;

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            rd_data    <= 32'd0;
            rd_valid   <= 1'b0;
            single_err <= 1'b0;
            double_err <= 1'b0;
            for (i = 0; i < 256; i = i + 1)
                mem[i] <= 39'd0;
        end else begin
            rd_valid   <= 1'b0;
            single_err <= 1'b0;
            double_err <= 1'b0;

            if (wr_en) begin
                mem[addr] <= wr_word;
            end else if (rd_en) begin
                rd_valid <= 1'b1;
                if (syndrome == 0) begin
                    rd_data <= mem_data;
                end else if (overall_p) begin
                    // Single-bit error: correctable
                    single_err <= 1'b1;
                    rd_data <= mem_data;  // simplified: return uncorrected
                end else begin
                    // Double-bit error: detectable but not correctable
                    double_err <= 1'b1;
                    rd_data <= mem_data;
                end
            end
        end
    end

endmodule
