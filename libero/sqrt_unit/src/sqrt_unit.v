// 32-bit Integer Square Root - Sequential implementation
// Target: MPF100T (PolarFire)
// Uses non-restoring algorithm, 16 cycles per computation

module sqrt_unit (
    input         clk,
    input         reset_n,
    input  [31:0] operand,
    input         start,
    output reg [15:0] result,
    output reg        done,
    output reg        busy
);

    reg [31:0] remainder;
    reg [31:0] radicand;
    reg [15:0] root;
    reg [4:0]  iteration;

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            result    <= 16'd0;
            done      <= 1'b0;
            busy      <= 1'b0;
            remainder <= 32'd0;
            radicand  <= 32'd0;
            root      <= 16'd0;
            iteration <= 5'd0;
        end else begin
            done <= 1'b0;

            if (start && !busy) begin
                radicand  <= operand;
                remainder <= 32'd0;
                root      <= 16'd0;
                iteration <= 5'd15;
                busy      <= 1'b1;
            end else if (busy) begin
                // Non-restoring square root algorithm
                remainder <= {remainder[29:0], radicand[31:30]};
                radicand  <= {radicand[29:0], 2'b00};

                if ({remainder[29:0], radicand[31:30]} >= {root, 2'b01}) begin
                    remainder <= {remainder[29:0], radicand[31:30]} - {root, 2'b01};
                    root      <= {root[14:0], 1'b1};
                end else begin
                    root <= {root[14:0], 1'b0};
                end

                if (iteration == 0) begin
                    result <= root;
                    done   <= 1'b1;
                    busy   <= 1'b0;
                end else begin
                    iteration <= iteration - 1;
                end
            end
        end
    end

endmodule
