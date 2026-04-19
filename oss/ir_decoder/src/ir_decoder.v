// NEC IR Remote Decoder
// Device: iCE40UP5K
// Decodes NEC protocol: 9ms leader, 4.5ms space, 32 data bits

module ir_decoder (
    input         clk,
    input         rst_n,
    input         ir_in,       // active-low IR input
    output [7:0]  address,
    output [7:0]  command,
    output        data_valid,
    output        error
);

    // Timing at 12 MHz: 1 tick = 83.3ns
    // 562.5us pulse = 6750 ticks, 9ms = 108000, 4.5ms = 54000
    parameter LEADER_MIN  = 20'd90000;
    parameter LEADER_MAX  = 20'd126000;
    parameter SPACE_MIN   = 20'd40000;
    parameter SPACE_MAX   = 20'd68000;
    parameter BIT_THRESH  = 20'd10125;  // 843.75us threshold between 0 and 1

    reg [2:0] state;
    reg [19:0] timer;
    reg [31:0] shift_reg;
    reg [5:0] bit_cnt;
    reg       ir_prev;
    reg [7:0] addr_r, cmd_r;
    reg       valid_r, error_r;

    localparam S_IDLE   = 3'd0;
    localparam S_LEADER = 3'd1;
    localparam S_SPACE  = 3'd2;
    localparam S_DATA_MARK  = 3'd3;
    localparam S_DATA_SPACE = 3'd4;
    localparam S_DONE   = 3'd5;

    assign address    = addr_r;
    assign command    = cmd_r;
    assign data_valid = valid_r;
    assign error      = error_r;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state     <= S_IDLE;
            timer     <= 20'd0;
            shift_reg <= 32'd0;
            bit_cnt   <= 6'd0;
            ir_prev   <= 1'b1;
            addr_r    <= 8'd0;
            cmd_r     <= 8'd0;
            valid_r   <= 1'b0;
            error_r   <= 1'b0;
        end else begin
            ir_prev <= ir_in;
            valid_r <= 1'b0;
            error_r <= 1'b0;

            case (state)
                S_IDLE: begin
                    if (ir_prev && !ir_in) begin
                        // Falling edge: start of leader
                        timer <= 20'd0;
                        state <= S_LEADER;
                    end
                end
                S_LEADER: begin
                    timer <= timer + 1'b1;
                    if (!ir_prev && ir_in) begin
                        // Rising edge: end of leader
                        if (timer >= LEADER_MIN && timer <= LEADER_MAX) begin
                            timer <= 20'd0;
                            state <= S_SPACE;
                        end else begin
                            error_r <= 1'b1;
                            state   <= S_IDLE;
                        end
                    end
                end
                S_SPACE: begin
                    timer <= timer + 1'b1;
                    if (ir_prev && !ir_in) begin
                        if (timer >= SPACE_MIN && timer <= SPACE_MAX) begin
                            timer   <= 20'd0;
                            bit_cnt <= 6'd0;
                            state   <= S_DATA_MARK;
                        end else begin
                            error_r <= 1'b1;
                            state   <= S_IDLE;
                        end
                    end
                end
                S_DATA_MARK: begin
                    timer <= timer + 1'b1;
                    if (!ir_prev && ir_in) begin
                        timer <= 20'd0;
                        state <= S_DATA_SPACE;
                    end
                end
                S_DATA_SPACE: begin
                    timer <= timer + 1'b1;
                    if (ir_prev && !ir_in) begin
                        // Falling edge: decode bit
                        shift_reg <= {shift_reg[30:0], (timer > BIT_THRESH) ? 1'b1 : 1'b0};
                        bit_cnt   <= bit_cnt + 1'b1;
                        timer     <= 20'd0;
                        if (bit_cnt == 6'd31)
                            state <= S_DONE;
                        else
                            state <= S_DATA_MARK;
                    end
                end
                S_DONE: begin
                    addr_r  <= shift_reg[31:24];
                    cmd_r   <= shift_reg[15:8];
                    valid_r <= 1'b1;
                    state   <= S_IDLE;
                end
            endcase
        end
    end

endmodule
