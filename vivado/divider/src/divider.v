// =============================================================================
// 32-bit Unsigned Integer Divider (Sequential, Restoring Division)
// Device: Xilinx Artix-7 XC7A35T
// =============================================================================

module divider (
    input  wire        clk,
    input  wire        rst_n,
    input  wire [31:0] dividend,
    input  wire [31:0] divisor,
    input  wire        start,
    output reg  [31:0] quotient,
    output reg  [31:0] remainder,
    output reg         done,
    output reg         div_by_zero
);

    reg [5:0]  bit_cnt;
    reg [31:0] divisor_reg;
    reg [31:0] quotient_tmp;
    reg [32:0] remainder_tmp;  // Extra bit for subtraction
    reg        busy;

    localparam IDLE = 1'b0;
    localparam CALC = 1'b1;
    reg state;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            quotient     <= 32'd0;
            remainder    <= 32'd0;
            done         <= 1'b0;
            div_by_zero  <= 1'b0;
            busy         <= 1'b0;
            state        <= IDLE;
            bit_cnt      <= 6'd0;
            divisor_reg  <= 32'd0;
            quotient_tmp <= 32'd0;
            remainder_tmp <= 33'd0;
        end else begin
            done <= 1'b0;

            case (state)
                IDLE: begin
                    if (start) begin
                        if (divisor == 32'd0) begin
                            div_by_zero <= 1'b1;
                            quotient    <= 32'hFFFFFFFF;
                            remainder   <= dividend;
                            done        <= 1'b1;
                        end else begin
                            div_by_zero   <= 1'b0;
                            divisor_reg   <= divisor;
                            quotient_tmp  <= 32'd0;
                            remainder_tmp <= 33'd0;
                            bit_cnt       <= 6'd32;
                            busy          <= 1'b1;
                            state         <= CALC;
                            // Load dividend MSB first
                            remainder_tmp <= {32'd0, dividend[31]};
                            quotient_tmp  <= {dividend[30:0], 1'b0};
                        end
                    end
                end

                CALC: begin
                    if (bit_cnt == 6'd0) begin
                        quotient  <= quotient_tmp;
                        remainder <= remainder_tmp[31:0];
                        done      <= 1'b1;
                        busy      <= 1'b0;
                        state     <= IDLE;
                    end else begin
                        bit_cnt <= bit_cnt - 1'b1;

                        if (remainder_tmp >= {1'b0, divisor_reg}) begin
                            remainder_tmp <= {(remainder_tmp - {1'b0, divisor_reg}), quotient_tmp[31]};
                            quotient_tmp  <= {quotient_tmp[30:0], 1'b1};
                        end else begin
                            remainder_tmp <= {remainder_tmp[31:0], quotient_tmp[31]};
                            quotient_tmp  <= {quotient_tmp[30:0], 1'b0};
                        end
                    end
                end
            endcase
        end
    end

endmodule
