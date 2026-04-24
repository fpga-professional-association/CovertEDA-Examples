// SPI Flash Read-Only Controller
// Device: iCE40UP5K
// Issues read commands (0x03) and receives data bytes

module spi_flash_reader (
    input         clk,
    input         rst_n,
    input  [23:0] address,
    input         start,
    output [7:0]  data_out,
    output        data_valid,
    output        busy,

    // SPI interface
    output        spi_clk,
    output        spi_cs_n,
    output        spi_mosi,
    input         spi_miso
);

    reg [2:0] state;
    reg [5:0] bit_cnt;
    reg [7:0] shift_out;
    reg [7:0] shift_in;
    reg [7:0] clk_div;
    reg       sclk_r;
    reg       cs_r;
    reg       mosi_r;
    reg [7:0] data_r;
    reg       valid_r;

    localparam S_IDLE   = 3'd0;
    localparam S_CMD    = 3'd1;
    localparam S_ADDR2  = 3'd2;
    localparam S_ADDR1  = 3'd3;
    localparam S_ADDR0  = 3'd4;
    localparam S_DATA   = 3'd5;
    localparam S_DONE   = 3'd6;

    parameter CLK_DIV = 8'd3;

    assign spi_clk   = sclk_r;
    assign spi_cs_n  = cs_r;
    assign spi_mosi  = mosi_r;
    assign data_out  = data_r;
    assign data_valid = valid_r;
    assign busy      = (state != S_IDLE);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state    <= S_IDLE;
            bit_cnt  <= 6'd0;
            shift_out <= 8'd0;
            shift_in <= 8'd0;
            clk_div  <= 8'd0;
            sclk_r   <= 1'b0;
            cs_r     <= 1'b1;
            mosi_r   <= 1'b0;
            data_r   <= 8'd0;
            valid_r  <= 1'b0;
        end else begin
            valid_r <= 1'b0;

            case (state)
                S_IDLE: begin
                    cs_r   <= 1'b1;
                    sclk_r <= 1'b0;
                    if (start) begin
                        cs_r      <= 1'b0;
                        shift_out <= 8'h03; // Read command
                        bit_cnt   <= 6'd0;
                        clk_div   <= 8'd0;
                        state     <= S_CMD;
                    end
                end
                S_CMD, S_ADDR2, S_ADDR1, S_ADDR0, S_DATA: begin
                    clk_div <= clk_div + 1'b1;
                    if (clk_div == CLK_DIV) begin
                        clk_div <= 8'd0;
                        sclk_r  <= ~sclk_r;
                        if (!sclk_r) begin
                            // Rising edge: output bit
                            mosi_r <= shift_out[7];
                        end else begin
                            // Falling edge: shift and sample
                            shift_out <= {shift_out[6:0], 1'b0};
                            shift_in  <= {shift_in[6:0], spi_miso};
                            bit_cnt   <= bit_cnt + 1'b1;
                            if (bit_cnt[2:0] == 3'd7) begin
                                case (state)
                                    S_CMD:   begin shift_out <= address[23:16]; state <= S_ADDR2; end
                                    S_ADDR2: begin shift_out <= address[15:8];  state <= S_ADDR1; end
                                    S_ADDR1: begin shift_out <= address[7:0];   state <= S_ADDR0; end
                                    S_ADDR0: begin shift_out <= 8'd0;           state <= S_DATA;  end
                                    S_DATA:  state <= S_DONE;
                                    default: state <= S_IDLE;
                                endcase
                            end
                        end
                    end
                end
                S_DONE: begin
                    cs_r    <= 1'b1;
                    sclk_r  <= 1'b0;
                    data_r  <= shift_in;
                    valid_r <= 1'b1;
                    state   <= S_IDLE;
                end
            endcase
        end
    end

endmodule
