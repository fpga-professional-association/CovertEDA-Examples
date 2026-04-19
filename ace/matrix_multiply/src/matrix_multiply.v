// 4x4 Matrix Multiplier (16-bit elements)
// Device: Achronix Speedster7t AC7t1500
// Serialized input/output, computes C = A * B

module matrix_multiply (
    input                clk,
    input                rst_n,
    input  signed [15:0] a_in,
    input  signed [15:0] b_in,
    input                load_a,
    input                load_b,
    input                start,
    output signed [31:0] c_out,
    output               c_valid,
    output               busy
);

    reg signed [15:0] A [0:3][0:3];
    reg signed [15:0] B [0:3][0:3];
    reg signed [31:0] C_reg;
    reg               c_valid_r;
    reg               busy_r;

    reg [3:0] load_idx;
    reg [1:0] row, col, k;
    reg [1:0] state;

    localparam S_IDLE    = 2'd0;
    localparam S_COMPUTE = 2'd1;
    localparam S_OUTPUT  = 2'd2;

    reg signed [31:0] accum;
    reg signed [31:0] result [0:3][0:3];

    assign c_out   = C_reg;
    assign c_valid = c_valid_r;
    assign busy    = busy_r;

    integer i, j;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            load_idx  <= 4'd0;
            row       <= 2'd0;
            col       <= 2'd0;
            k         <= 2'd0;
            state     <= S_IDLE;
            C_reg     <= 32'd0;
            c_valid_r <= 1'b0;
            busy_r    <= 1'b0;
            accum     <= 32'd0;
            for (i = 0; i < 4; i = i + 1)
                for (j = 0; j < 4; j = j + 1) begin
                    A[i][j] <= 16'd0;
                    B[i][j] <= 16'd0;
                    result[i][j] <= 32'd0;
                end
        end else begin
            c_valid_r <= 1'b0;

            // Load matrices serially
            if (load_a) begin
                A[load_idx[3:2]][load_idx[1:0]] <= a_in;
                load_idx <= load_idx + 1'b1;
            end
            if (load_b) begin
                B[load_idx[3:2]][load_idx[1:0]] <= b_in;
                load_idx <= load_idx + 1'b1;
            end

            case (state)
                S_IDLE: begin
                    if (start) begin
                        state  <= S_COMPUTE;
                        busy_r <= 1'b1;
                        row    <= 2'd0;
                        col    <= 2'd0;
                        k      <= 2'd0;
                        accum  <= 32'd0;
                        load_idx <= 4'd0;
                    end
                end
                S_COMPUTE: begin
                    accum <= accum + A[row][k] * B[k][col];
                    if (k == 2'd3) begin
                        result[row][col] <= accum + A[row][k] * B[k][col];
                        k <= 2'd0;
                        accum <= 32'd0;
                        if (col == 2'd3) begin
                            col <= 2'd0;
                            if (row == 2'd3) begin
                                state <= S_OUTPUT;
                                row   <= 2'd0;
                                col   <= 2'd0;
                            end else
                                row <= row + 1'b1;
                        end else
                            col <= col + 1'b1;
                    end else
                        k <= k + 1'b1;
                end
                S_OUTPUT: begin
                    C_reg     <= result[row][col];
                    c_valid_r <= 1'b1;
                    if (col == 2'd3) begin
                        col <= 2'd0;
                        if (row == 2'd3) begin
                            state  <= S_IDLE;
                            busy_r <= 1'b0;
                        end else
                            row <= row + 1'b1;
                    end else
                        col <= col + 1'b1;
                end
            endcase
        end
    end

endmodule
