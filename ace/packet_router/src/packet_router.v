// 4-Port Packet Router with Header-Based Forwarding
// Device: Achronix Speedster7t AC7t1500
// Routes 8-bit data with 2-bit destination in header byte

module packet_router (
    input         clk,
    input         rst_n,

    // Input port
    input  [7:0]  in_data,
    input         in_valid,
    output        in_ready,

    // Output ports 0-3
    output [7:0]  out0_data,
    output        out0_valid,
    output [7:0]  out1_data,
    output        out1_valid,
    output [7:0]  out2_data,
    output        out2_valid,
    output [7:0]  out3_data,
    output        out3_valid
);

    localparam S_IDLE   = 2'd0;
    localparam S_HEADER = 2'd1;
    localparam S_DATA   = 2'd2;

    reg [1:0] state;
    reg [1:0] dest;
    reg [5:0] pkt_len;
    reg [5:0] byte_cnt;
    reg [7:0] data_r;
    reg       valid_r;

    assign in_ready = (state == S_IDLE) || (state == S_HEADER);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state    <= S_IDLE;
            dest     <= 2'd0;
            pkt_len  <= 6'd0;
            byte_cnt <= 6'd0;
            data_r   <= 8'd0;
            valid_r  <= 1'b0;
        end else begin
            valid_r <= 1'b0;
            case (state)
                S_IDLE: begin
                    if (in_valid) begin
                        // Header byte: [7:6]=dest, [5:0]=length
                        dest    <= in_data[7:6];
                        pkt_len <= in_data[5:0];
                        byte_cnt <= 6'd0;
                        state   <= S_DATA;
                    end
                end
                S_DATA: begin
                    if (in_valid) begin
                        data_r   <= in_data;
                        valid_r  <= 1'b1;
                        byte_cnt <= byte_cnt + 1'b1;
                        if (byte_cnt == pkt_len - 1)
                            state <= S_IDLE;
                    end
                end
                default: state <= S_IDLE;
            endcase
        end
    end

    // Demux to output ports
    assign out0_data  = data_r;
    assign out0_valid = valid_r & (dest == 2'd0);
    assign out1_data  = data_r;
    assign out1_valid = valid_r & (dest == 2'd1);
    assign out2_data  = data_r;
    assign out2_valid = valid_r & (dest == 2'd2);
    assign out3_data  = data_r;
    assign out3_valid = valid_r & (dest == 2'd3);

endmodule
