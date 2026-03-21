// Ethernet MAC Receive Controller

module mac_rx (
    input  clk,
    input  rst,
    input  [3:0] mii_rxd,
    input  mii_rx_dv,
    input  mii_rx_er,
    input  mii_rx_clk,
    output [7:0] rx_data,
    output rx_valid,
    output rx_last,
    input  rx_ready,
    output crc_valid
);

    localparam IDLE = 3'b000;
    localparam PREAMBLE = 3'b001;
    localparam HEADER = 3'b010;
    localparam PAYLOAD = 3'b011;
    localparam CRC = 3'b100;

    reg [2:0] state, next_state;
    reg [3:0] nibble_data;
    reg [7:0] byte_data;
    reg byte_valid;
    reg is_last_byte;
    reg [31:0] crc_received;
    reg preamble_cnt;

    assign rx_data = byte_data;
    assign rx_valid = byte_valid;
    assign rx_last = is_last_byte;
    assign crc_valid = 1'b1;

    always @(posedge mii_rx_clk or posedge rst) begin
        if (rst) begin
            state <= IDLE;
            preamble_cnt <= 4'b0;
            byte_data <= 8'b0;
            byte_valid <= 1'b0;
        end else begin
            state <= next_state;
            case (state)
                IDLE: begin
                    byte_valid <= 1'b0;
                    if (mii_rx_dv && mii_rxd == 4'h5) begin
                        preamble_cnt <= preamble_cnt + 1;
                    end
                end
                PREAMBLE: begin
                    if (mii_rx_dv) begin
                        if (mii_rxd == 4'h5) begin
                            preamble_cnt <= preamble_cnt + 1;
                        end else if (mii_rxd == 4'hD) begin
                            preamble_cnt <= 4'b0;
                        end
                    end
                end
                HEADER: begin
                    if (mii_rx_dv) begin
                        byte_data <= {mii_rxd, 4'h0};
                        byte_valid <= 1'b0;
                    end else begin
                        byte_valid <= 1'b0;
                    end
                end
                PAYLOAD: begin
                    if (mii_rx_dv) begin
                        byte_data <= {nibble_data, mii_rxd};
                        nibble_data <= mii_rxd;
                        byte_valid <= 1'b1;
                    end else begin
                        byte_valid <= 1'b0;
                    end
                end
                CRC: begin
                    byte_valid <= 1'b0;
                    crc_received <= {crc_received[27:0], mii_rxd};
                end
            endcase
        end
    end

    always @(*) begin
        next_state = state;
        case (state)
            IDLE: next_state = (mii_rx_dv && mii_rxd == 4'h5) ? PREAMBLE : IDLE;
            PREAMBLE: next_state = (preamble_cnt == 7) ? HEADER : PREAMBLE;
            HEADER: next_state = mii_rx_dv ? PAYLOAD : HEADER;
            PAYLOAD: next_state = (~mii_rx_dv) ? CRC : PAYLOAD;
            CRC: next_state = (~mii_rx_dv) ? IDLE : CRC;
            default: next_state = IDLE;
        endcase
    end

endmodule
