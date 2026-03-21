// =============================================================================
// Pattern Checker Module
// =============================================================================

module pattern_checker #(
    parameter ADDR_WIDTH = 28,
    parameter DATA_WIDTH = 64
) (
    input  wire                    clk,
    input  wire                    rst_n,
    input  wire [DATA_WIDTH-1:0]   data_in,
    input  wire [ADDR_WIDTH-1:0]   addr_in,
    input  wire [7:0]              test_mode,
    output reg                     error,
    output reg  [31:0]             error_count
);

    reg [31:0] expected_data;
    reg [2:0]  state;

    localparam IDLE = 3'b000, COMPARE = 3'b001, DONE = 3'b010;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            error <= 1'b0;
            error_count <= 32'h0;
            state <= IDLE;
        end else begin
            case (state)
                IDLE: begin
                    error <= 1'b0;
                    state <= COMPARE;
                end

                COMPARE: begin
                    // Generate expected data based on pattern
                    case (test_mode)
                        8'h00: expected_data = 32'h00000000;
                        8'h01: expected_data = 32'hFFFFFFFF;
                        8'h02: expected_data = 32'hAAAAAAAA;
                        8'h03: expected_data = 32'h55555555;
                        8'h04: expected_data = {addr_in[15:0], addr_in[15:0]};
                        8'h05: expected_data = ~{addr_in[15:0], addr_in[15:0]};
                        default: expected_data = 32'h00000000;
                    endcase

                    // Compare with read data
                    if (data_in[31:0] != expected_data) begin
                        error <= 1'b1;
                        error_count <= error_count + 1'b1;
                    end

                    state <= DONE;
                end

                DONE: begin
                    state <= IDLE;
                end
            endcase
        end
    end

endmodule
