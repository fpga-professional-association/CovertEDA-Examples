// SPI Master Module

module spi_master (
    input  clk,
    input  rst_n,
    output reg cs_n,
    output reg sclk,
    output reg mosi,
    input  miso,
    input  [7:0] tx_data,
    output reg [7:0] rx_data,
    output reg busy
);

    localparam IDLE = 2'b00;
    localparam TRANSFER = 2'b01;
    localparam DONE = 2'b10;

    reg [1:0] state, next_state;
    reg [3:0] bit_count;
    reg [7:0] shift_reg;
    reg [7:0] div_count;
    reg sclk_enable;

    parameter DIV = 5;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            busy <= 1'b0;
            cs_n <= 1'b1;
            sclk <= 1'b0;
            mosi <= 1'b0;
            bit_count <= 4'h0;
            div_count <= 8'h0;
        end else begin
            state <= next_state;

            if (state == IDLE) begin
                busy <= 1'b0;
                cs_n <= 1'b1;
                sclk <= 1'b0;
            end else if (state == TRANSFER) begin
                busy <= 1'b1;
                cs_n <= 1'b0;

                if (div_count == DIV - 1) begin
                    div_count <= 8'h0;
                    sclk <= !sclk;
                    if (!sclk) begin
                        mosi <= shift_reg[7];
                        shift_reg <= {shift_reg[6:0], miso};
                    end else begin
                        if (bit_count == 4'h7) begin
                            rx_data <= {shift_reg[6:0], miso};
                        end
                        bit_count <= bit_count + 1'b1;
                    end
                end else begin
                    div_count <= div_count + 1'b1;
                end
            end
        end
    end

    always @* begin
        case (state)
            IDLE: begin
                next_state = TRANSFER;
                shift_reg = tx_data;
                bit_count = 4'h0;
            end
            TRANSFER: begin
                if (bit_count == 4'h8 && sclk == 1'b0) begin
                    next_state = DONE;
                end else begin
                    next_state = TRANSFER;
                end
            end
            DONE: begin
                next_state = IDLE;
            end
            default: next_state = IDLE;
        endcase
    end

endmodule
