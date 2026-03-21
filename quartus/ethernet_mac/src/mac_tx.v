// Ethernet MAC Transmit Controller

module mac_tx (
    input  clk,
    input  rst,
    output [3:0] mii_txd,
    output mii_tx_en,
    output mii_tx_er,
    input  mii_tx_clk,
    input  [47:0] mac_addr,
    input  [15:0] eth_type,
    input  [7:0] tx_data,
    input  tx_valid,
    output tx_ready
);

    localparam IDLE = 3'b000;
    localparam PREAMBLE = 3'b001;
    localparam SFD = 3'b010;
    localparam HEADER = 3'b011;
    localparam DATA = 3'b100;
    localparam CRC = 3'b101;
    localparam IFG = 3'b110;

    reg [2:0] state, next_state;
    reg [15:0] byte_cnt;
    reg [3:0] nibble_cnt;
    reg [31:0] crc_reg;
    reg mii_txd_r;
    reg mii_tx_en_r;

    assign mii_txd = {mii_txd_r, 3'b000};
    assign mii_tx_en = mii_tx_en_r;
    assign mii_tx_er = 1'b0;
    assign tx_ready = (state == IDLE) || (state == DATA && tx_valid);

    always @(posedge mii_tx_clk or posedge rst) begin
        if (rst) begin
            state <= IDLE;
            byte_cnt <= 16'b0;
            mii_tx_en_r <= 1'b0;
        end else begin
            state <= next_state;
            case (state)
                IDLE: begin
                    mii_tx_en_r <= 1'b0;
                    byte_cnt <= 16'b0;
                end
                PREAMBLE: begin
                    mii_txd_r <= 4'h5;
                    mii_tx_en_r <= 1'b1;
                    if (byte_cnt < 7) byte_cnt <= byte_cnt + 1;
                end
                SFD: begin
                    mii_txd_r <= 4'hD;
                    mii_tx_en_r <= 1'b1;
                end
                HEADER: begin
                    mii_tx_en_r <= 1'b1;
                    byte_cnt <= byte_cnt + 1;
                end
                DATA: begin
                    if (tx_valid) begin
                        mii_txd_r <= tx_data[3:0];
                        mii_tx_en_r <= 1'b1;
                        byte_cnt <= byte_cnt + 1;
                    end
                end
                CRC: begin
                    mii_txd_r <= crc_reg[3:0];
                    mii_tx_en_r <= 1'b1;
                    crc_reg <= crc_reg >> 4;
                    byte_cnt <= byte_cnt + 1;
                end
                IFG: begin
                    mii_tx_en_r <= 1'b0;
                    byte_cnt <= byte_cnt + 1;
                end
            endcase
        end
    end

    always @(*) begin
        next_state = state;
        case (state)
            IDLE: next_state = PREAMBLE;
            PREAMBLE: next_state = (byte_cnt == 7) ? SFD : PREAMBLE;
            SFD: next_state = HEADER;
            HEADER: next_state = (byte_cnt == 14) ? DATA : HEADER;
            DATA: next_state = tx_valid ? DATA : CRC;
            CRC: next_state = (byte_cnt == 4) ? IFG : CRC;
            IFG: next_state = (byte_cnt == 12) ? IDLE : IFG;
        endcase
    end

endmodule
