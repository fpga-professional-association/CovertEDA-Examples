// Pseudo-Random Binary Sequence (PRBS) Checker
// Verifies received PRBS pattern and detects bit errors
// Reports error count and pattern lock status

module prbs_check #(
    parameter WIDTH = 32
) (
    input clk,
    input reset_n,
    input enable,
    input [WIDTH-1:0] prbs_in,
    output reg [7:0] prbs_err,
    output reg locked
);

    // PRBS checker state machine
    reg [23:0] check_counter;
    reg [23:0] error_counter;
    reg [6:0] lfsr_check;
    wire [6:0] feedback;

    // Expected PRBS7 feedback
    assign feedback = {
        lfsr_check[5] ^ lfsr_check[6],
        lfsr_check[4] ^ lfsr_check[6],
        lfsr_check[5],
        lfsr_check[4],
        lfsr_check[3],
        lfsr_check[2],
        lfsr_check[1] ^ lfsr_check[6]
    };

    // Error detection and accumulation
    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            check_counter <= 24'h000000;
            error_counter <= 24'h000000;
            lfsr_check <= 7'b0000001;
            prbs_err <= 8'h00;
            locked <= 1'b0;
        end else if (enable) begin
            // Compare input with expected pattern
            if (prbs_in[0] != lfsr_check[0]) begin
                error_counter <= error_counter + 1'b1;
            end

            // Shift expected pattern
            lfsr_check <= feedback;

            // Increment check counter
            check_counter <= check_counter + 1'b1;

            // Every 256 clocks, update error rate
            if (check_counter == 24'hFFFFFF) begin
                check_counter <= 24'h000000;
                prbs_err <= (error_counter[7:0] > 8'd20) ? 8'hFF : error_counter[7:0];
                error_counter <= 24'h000000;

                // Lock when errors are below threshold
                if (error_counter[7:0] < 8'd5) begin
                    locked <= 1'b1;
                end else begin
                    locked <= 1'b0;
                end
            end
        end
    end

endmodule
