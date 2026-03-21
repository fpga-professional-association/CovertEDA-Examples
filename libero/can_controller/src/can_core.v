// CAN 2.0B Core

module can_core (
    input  clk,
    input  rst_n,
    input  bit_clk,
    input  bit_strobe,
    input  can_rx,
    output reg can_tx,
    input  [31:0] tx_id,
    input  [63:0] tx_data,
    input  [3:0]  tx_dlc,
    input  tx_valid,
    output reg tx_ready,
    output [31:0] rx_id,
    output [63:0] rx_data,
    output [3:0]  rx_dlc,
    output rx_valid
);

    localparam IDLE = 3'b000;
    localparam TX_ARB = 3'b001;
    localparam TX_CONTROL = 3'b010;
    localparam TX_DATA = 3'b011;
    localparam TX_CRC = 3'b100;
    localparam RX = 3'b101;

    reg [2:0] state, next_state;
    reg [7:0] bit_count;
    reg [31:0] tx_arb_id;
    reg [63:0] tx_payload;
    reg [3:0] dlc_reg;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            can_tx <= 1'b1;  // Recessive
            tx_ready <= 1'b1;
            bit_count <= 8'h0;
        end else begin
            state <= next_state;

            if (state == TX_ARB && bit_strobe) begin
                bit_count <= bit_count + 1'b1;
                if (bit_count < 11) begin
                    can_tx <= tx_arb_id[30 - bit_count];
                end
            end else if (state == TX_DATA && bit_strobe) begin
                bit_count <= bit_count + 1'b1;
                if (bit_count < (dlc_reg << 3)) begin
                    can_tx <= tx_payload[63 - (bit_count % 64)];
                end
            end
        end
    end

    always @* begin
        case (state)
            IDLE: begin
                tx_ready = 1'b1;
                if (tx_valid) begin
                    next_state = TX_ARB;
                end else begin
                    next_state = IDLE;
                end
            end
            TX_ARB: begin
                tx_ready = 1'b0;
                if (bit_count >= 11) begin
                    next_state = TX_CONTROL;
                end else begin
                    next_state = TX_ARB;
                end
            end
            TX_CONTROL: begin
                next_state = TX_DATA;
            end
            TX_DATA: begin
                if (bit_count >= (dlc_reg << 3)) begin
                    next_state = TX_CRC;
                end else begin
                    next_state = TX_DATA;
                end
            end
            TX_CRC: begin
                next_state = IDLE;
            end
            default: next_state = IDLE;
        endcase
    end

    always @(posedge clk) begin
        if (state == IDLE && tx_valid) begin
            tx_arb_id <= tx_id;
            tx_payload <= tx_data;
            dlc_reg <= tx_dlc;
        end
    end

    assign rx_id = 32'h0;
    assign rx_data = 64'h0;
    assign rx_dlc = 4'h0;
    assign rx_valid = 1'b0;

endmodule
