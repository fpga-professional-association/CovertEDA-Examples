// Encoder Interface for Motor Speed Measurement

module encoder_intf (
    input  clk,
    input  rst_n,
    input  encoder_a,
    input  encoder_b,
    output [15:0] encoder_count,
    output [15:0] speed
);

    reg encoder_a_r1, encoder_a_r2;
    reg encoder_b_r1, encoder_b_r2;
    reg [15:0] count;
    reg [15:0] count_latched;
    reg [19:0] count_clks;

    // Synchronization
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            encoder_a_r1 <= 1'b0;
            encoder_a_r2 <= 1'b0;
            encoder_b_r1 <= 1'b0;
            encoder_b_r2 <= 1'b0;
        end else begin
            encoder_a_r1 <= encoder_a;
            encoder_a_r2 <= encoder_a_r1;
            encoder_b_r1 <= encoder_b;
            encoder_b_r2 <= encoder_b_r1;
        end
    end

    // Quadrature decoder
    wire a_edge = encoder_a_r2 ^ encoder_a_r1;
    wire dir = encoder_a_r2 ^ encoder_b_r2;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            count <= 16'h0;
            count_clks <= 20'h0;
            count_latched <= 16'h0;
        end else begin
            if (a_edge) begin
                count <= dir ? (count + 1'b1) : (count - 1'b1);
            end

            count_clks <= count_clks + 1'b1;
            if (count_clks == 20'd100000) begin  // Sample every 1ms @ 100MHz
                count_latched <= count;
                count_clks <= 20'h0;
            end
        end
    end

    assign encoder_count = count;
    assign speed = count_latched;

endmodule
