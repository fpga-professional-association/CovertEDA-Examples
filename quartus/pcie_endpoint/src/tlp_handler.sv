// PCIe Transaction Layer Packet (TLP) Handler
// Processes incoming and outgoing TLP packets

module tlp_handler (
    input  clk,
    input  rst,

    // TLP Input (from PCIe Core)
    input  [63:0] tlp_data_in,
    input  [7:0] tlp_be_in,
    input  tlp_valid_in,
    output tlp_ready_out,

    // Application Output
    output [63:0] app_data_out,
    output [7:0] app_be_out,
    output app_valid_out,
    input  app_ready_in
);

    localparam TLP_HDR_SIZE = 4;  // 128-bit header = 16 bytes
    localparam TLP_STATE_IDLE = 3'b000;
    localparam TLP_STATE_HEADER = 3'b001;
    localparam TLP_STATE_PAYLOAD = 3'b010;
    localparam TLP_STATE_WAIT = 3'b011;

    reg [2:0] state;
    reg [63:0] payload_data;
    reg [7:0] payload_be;
    reg [11:0] payload_size;
    reg [9:0] byte_count;

    // TLP Header fields
    reg [31:0] tlp_hdr0;
    reg [31:0] tlp_hdr1;
    wire [6:0] tlp_type;
    wire tlp_fmt;

    // Extract TLP format and type
    assign tlp_fmt = tlp_hdr0[31];
    assign tlp_type = tlp_hdr0[30:24];

    // Determine payload size from TLP header
    always @(*) begin
        if (tlp_fmt) begin
            payload_size = {tlp_hdr1[9:0], 2'b00};  // Length field in DW
        end else begin
            payload_size = 12'b0;  // Completion has no payload
        end
    end

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            state <= TLP_STATE_IDLE;
            byte_count <= 10'b0;
        end else begin
            case (state)
                TLP_STATE_IDLE: begin
                    byte_count <= 10'b0;
                    if (tlp_valid_in) begin
                        tlp_hdr0 <= tlp_data_in[63:32];
                        state <= TLP_STATE_HEADER;
                    end
                end

                TLP_STATE_HEADER: begin
                    if (tlp_valid_in) begin
                        tlp_hdr1 <= tlp_data_in[31:0];
                        if (payload_size > 0) begin
                            state <= TLP_STATE_PAYLOAD;
                        end else begin
                            state <= TLP_STATE_WAIT;
                        end
                    end
                end

                TLP_STATE_PAYLOAD: begin
                    if (tlp_valid_in && app_ready_in) begin
                        byte_count <= byte_count + 8;
                        if (byte_count >= payload_size) begin
                            state <= TLP_STATE_IDLE;
                        end
                    end
                end

                TLP_STATE_WAIT: begin
                    if (app_ready_in) begin
                        state <= TLP_STATE_IDLE;
                    end
                end

                default: state <= TLP_STATE_IDLE;
            endcase
        end
    end

    // Output assignment
    assign app_data_out = tlp_data_in;
    assign app_be_out = tlp_be_in;
    assign app_valid_out = (state == TLP_STATE_PAYLOAD) ? tlp_valid_in : 1'b0;
    assign tlp_ready_out = (state != TLP_STATE_WAIT) ? 1'b1 : 1'b0;

endmodule
