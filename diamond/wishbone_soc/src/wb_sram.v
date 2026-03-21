// Wishbone SRAM Slave - 4 KB of embedded memory
// Uses EBR blocks for storage

module wb_sram (
    input clk,
    input reset_n,
    input [11:0] wb_addr,
    input [31:0] wb_data_wr,
    output reg [31:0] wb_data_rd,
    input [3:0] wb_sel,
    input wb_we,
    input wb_cyc,
    input wb_stb,
    output reg wb_ack
);

    // 1024 x 32-bit SRAM (4 KB)
    reg [31:0] sram [0:1023];
    reg wb_ack_r;

    // SRAM read/write logic
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            wb_data_rd <= 32'h00000000;
            wb_ack <= 1'b0;
            wb_ack_r <= 1'b0;
        end else begin
            wb_ack_r <= wb_stb && wb_cyc;
            wb_ack <= wb_ack_r;

            if (wb_stb && wb_cyc) begin
                // Read data
                wb_data_rd <= sram[wb_addr[11:2]];

                // Write data (only selected bytes)
                if (wb_we) begin
                    if (wb_sel[0]) sram[wb_addr[11:2]][7:0] <= wb_data_wr[7:0];
                    if (wb_sel[1]) sram[wb_addr[11:2]][15:8] <= wb_data_wr[15:8];
                    if (wb_sel[2]) sram[wb_addr[11:2]][23:16] <= wb_data_wr[23:16];
                    if (wb_sel[3]) sram[wb_addr[11:2]][31:24] <= wb_data_wr[31:24];
                end
            end
        end
    end

    // Initialize SRAM with test pattern
    initial begin
        integer i;
        for (i = 0; i < 1024; i = i + 1) begin
            sram[i] = {i[7:0], i[7:0], i[7:0], i[7:0]};
        end
    end

endmodule
