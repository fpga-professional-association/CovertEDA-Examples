// HDLC Frame Encoder with Zero Insertion
// Target: MPF100T (PolarFire)
// Inserts a 0 after five consecutive 1s in the data stream

module hdlc_framer (
    input        clk,
    input        reset_n,
    input        data_in,
    input        data_valid,
    input        frame_start,
    input        frame_end,
    output reg   data_out,
    output reg   out_valid,
    output reg   busy
);

    localparam FLAG = 8'h7E;  // 01111110

    localparam IDLE     = 3'd0;
    localparam SEND_FLAG= 3'd1;
    localparam DATA     = 3'd2;
    localparam STUFF    = 3'd3;
    localparam END_FLAG = 3'd4;

    reg [2:0] state;
    reg [2:0] ones_cnt;
    reg [2:0] flag_bit;
    reg [7:0] flag_shift;

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            state     <= IDLE;
            data_out  <= 1'b1;
            out_valid <= 1'b0;
            busy      <= 1'b0;
            ones_cnt  <= 3'd0;
            flag_bit  <= 3'd0;
            flag_shift<= FLAG;
        end else begin
            out_valid <= 1'b0;

            case (state)
                IDLE: begin
                    busy <= 1'b0;
                    data_out <= 1'b1;  // idle line
                    if (frame_start) begin
                        state <= SEND_FLAG;
                        flag_shift <= FLAG;
                        flag_bit <= 0;
                        busy <= 1'b1;
                    end
                end

                SEND_FLAG: begin
                    data_out  <= flag_shift[0];
                    out_valid <= 1'b1;
                    flag_shift <= {1'b0, flag_shift[7:1]};
                    flag_bit <= flag_bit + 1;
                    if (flag_bit == 7) begin
                        state    <= DATA;
                        ones_cnt <= 0;
                    end
                end

                DATA: begin
                    if (frame_end) begin
                        state <= END_FLAG;
                        flag_shift <= FLAG;
                        flag_bit <= 0;
                    end else if (data_valid) begin
                        data_out  <= data_in;
                        out_valid <= 1'b1;
                        if (data_in) begin
                            ones_cnt <= ones_cnt + 1;
                            if (ones_cnt == 4) begin
                                state <= STUFF;
                            end
                        end else begin
                            ones_cnt <= 0;
                        end
                    end
                end

                STUFF: begin
                    // Insert a zero after 5 consecutive ones
                    data_out  <= 1'b0;
                    out_valid <= 1'b1;
                    ones_cnt  <= 0;
                    state     <= DATA;
                end

                END_FLAG: begin
                    data_out  <= flag_shift[0];
                    out_valid <= 1'b1;
                    flag_shift <= {1'b0, flag_shift[7:1]};
                    flag_bit <= flag_bit + 1;
                    if (flag_bit == 7)
                        state <= IDLE;
                end

                default: state <= IDLE;
            endcase
        end
    end

endmodule
