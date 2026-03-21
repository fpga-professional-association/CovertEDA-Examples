// =============================================================================
// Scatter-Gather Engine
// =============================================================================

module sg_engine (
    input  wire         clk,
    input  wire         rst_n,
    input  wire         enable,
    input  wire [31:0]  sg_ptr,
    output reg          sg_valid,
    output reg  [31:0]  src_addr,
    output reg  [31:0]  dst_addr,
    output reg  [31:0]  length
);

    reg [31:0] sg_index;
    reg [2:0] state;

    localparam IDLE = 3'b000, FETCH_SRC = 3'b001, FETCH_DST = 3'b010,
               FETCH_LEN = 3'b011, DONE = 3'b100;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            sg_valid <= 1'b0;
            sg_index <= 32'h0;
            src_addr <= 32'h0;
            dst_addr <= 32'h0;
            length <= 32'h0;
        end else begin
            case (state)
                IDLE: begin
                    sg_valid <= 1'b0;
                    if (enable) begin
                        state <= FETCH_SRC;
                        sg_index <= 32'h0;
                    end
                end

                FETCH_SRC: begin
                    // Simulate reading from descriptor table
                    src_addr <= sg_ptr + sg_index;
                    state <= FETCH_DST;
                end

                FETCH_DST: begin
                    dst_addr <= sg_ptr + sg_index + 8;
                    state <= FETCH_LEN;
                end

                FETCH_LEN: begin
                    length <= sg_ptr + sg_index + 16;
                    state <= DONE;
                end

                DONE: begin
                    sg_valid <= 1'b1;
                    sg_index <= sg_index + 24;
                    state <= IDLE;
                end
            endcase
        end
    end

endmodule
