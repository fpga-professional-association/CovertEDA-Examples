// =============================================================================
// Descriptor Cache for Scatter-Gather
// =============================================================================

module descriptor_cache #(
    parameter CACHE_SIZE = 16
) (
    input  wire                 clk,
    input  wire                 rst_n,
    input  wire                 cache_enable,
    input  wire [31:0]          descriptor_base,
    output wire [127:0]         descriptor_out,
    output wire                 cache_valid,
    input  wire                 descriptor_ready
);

    reg [127:0] cache [0:CACHE_SIZE-1];
    reg [4:0] cache_ptr;
    reg cache_dirty;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            cache_ptr <= 5'h0;
            cache_dirty <= 1'b1;
        end else begin
            if (cache_enable && descriptor_ready) begin
                cache_ptr <= cache_ptr + 1'b1;
            end
            if (!cache_enable) begin
                cache_ptr <= 5'h0;
                cache_dirty <= 1'b1;
            end
        end
    end

    assign descriptor_out = cache[cache_ptr[3:0]];
    assign cache_valid = !cache_dirty;

endmodule
