// Packet Builder

module packet_builder (
    input  clk,
    input  rst_n,
    input  [63:0] in_data,
    input  in_valid,
    output [63:0] out_data,
    output out_valid
);

    reg [127:0] packet_buf;
    reg [1:0] count;
    reg pkt_valid;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            count <= 2'h0;
            pkt_valid <= 1'b0;
        end else if (in_valid) begin
            packet_buf <= {packet_buf[63:0], in_data};
            count <= count + 1'b1;

            if (count == 2'h1) begin
                pkt_valid <= 1'b1;
            end
        end else begin
            pkt_valid <= 1'b0;
        end
    end

    assign out_data = packet_buf[127:64];
    assign out_valid = pkt_valid;

endmodule
