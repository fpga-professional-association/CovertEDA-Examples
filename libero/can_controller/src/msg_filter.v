// CAN Message Filter

module msg_filter (
    input  [31:0] msg_id,
    input  [31:0] filter_id,
    input  [31:0] filter_mask,
    output match
);

    wire [31:0] masked_id;
    wire [31:0] masked_filter;

    assign masked_id = msg_id & filter_mask;
    assign masked_filter = filter_id & filter_mask;
    assign match = (masked_id == masked_filter);

endmodule
