// =============================================================================
// Traffic Generator Module
// =============================================================================

module traffic_gen_standalone #(
    parameter ADDR_WIDTH = 28,
    parameter DATA_WIDTH = 64
) (
    input  wire                    clk,
    input  wire                    rst_n,
    input  wire                    enable,
    input  wire [7:0]              pattern_sel,
    output reg  [ADDR_WIDTH-1:0]   addr_out,
    output wire [DATA_WIDTH-1:0]   data_out,
    output wire                    write_en,
    output reg                     done
);

    reg [ADDR_WIDTH-1:0] addr_cnt;
    reg [15:0] word_cnt;
    localparam MAX_WORDS = 16'hFFFF;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            addr_cnt <= {ADDR_WIDTH{1'b0}};
            word_cnt <= 16'b0;
            done <= 1'b0;
        end else begin
            if (enable && !done) begin
                if (word_cnt >= MAX_WORDS) begin
                    done <= 1'b1;
                    word_cnt <= 16'b0;
                end else begin
                    word_cnt <= word_cnt + 1'b1;
                    addr_cnt <= addr_cnt + 1'b1;
                    addr_out <= addr_cnt;
                end
            end else if (!enable) begin
                done <= 1'b0;
                addr_cnt <= {ADDR_WIDTH{1'b0}};
                word_cnt <= 16'b0;
            end
        end
    end

    // Pattern data
    reg [31:0] data_32;
    always @(*) begin
        case (pattern_sel)
            8'h00: data_32 = 32'h00000000;
            8'h01: data_32 = 32'hFFFFFFFF;
            8'h02: data_32 = 32'hAAAAAAAA;
            8'h03: data_32 = 32'h55555555;
            8'h04: data_32 = {addr_cnt[15:0], 16'h0000};
            8'h05: data_32 = addr_cnt[31:0];
            default: data_32 = 32'hDEADBEEF;
        endcase
    end

    assign data_out = {data_32, data_32};
    assign write_en = enable && !done;

endmodule
