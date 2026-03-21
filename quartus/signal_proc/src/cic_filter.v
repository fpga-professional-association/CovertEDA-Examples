// CIC (Cascade Integrator-Comb) Filter - Polyphase Decimator
// Generic parameterizable CIC implementation

module cic_filter #(
    parameter N = 5,           // Number of stages
    parameter R = 16           // Decimation factor
) (
    input  clk,
    input  rst,
    input  [31:0] i_data_in,
    input  [31:0] q_data_in,
    input  data_valid_in,
    input  [15:0] decim_rate,
    output [31:0] i_data_out,
    output [31:0] q_data_out,
    output data_valid_out
);

    // Integrator stages
    reg [47:0] i_int [0:N-1];
    reg [47:0] q_int [0:N-1];

    // Comb stages
    reg [47:0] i_comb [0:N-1];
    reg [47:0] q_comb [0:N-1];
    reg [47:0] i_comb_d [0:N-1];
    reg [47:0] q_comb_d [0:N-1];

    // Decimation counter
    reg [15:0] decim_count;
    reg decim_valid;

    integer i;

    // Integrator stage
    always @(posedge clk or posedge rst) begin
        if (rst) begin
            for (i = 0; i < N; i = i + 1) begin
                i_int[i] <= 48'b0;
                q_int[i] <= 48'b0;
            end
        end else if (data_valid_in) begin
            i_int[0] <= i_int[0] + i_data_in;
            q_int[0] <= q_int[0] + q_data_in;

            for (i = 1; i < N; i = i + 1) begin
                i_int[i] <= i_int[i] + i_int[i-1];
                q_int[i] <= q_int[i] + q_int[i-1];
            end
        end
    end

    // Decimation control
    always @(posedge clk or posedge rst) begin
        if (rst) begin
            decim_count <= 16'b0;
            decim_valid <= 1'b0;
        end else if (data_valid_in) begin
            if (decim_count == decim_rate - 1) begin
                decim_count <= 16'b0;
                decim_valid <= 1'b1;
            end else begin
                decim_count <= decim_count + 1;
                decim_valid <= 1'b0;
            end
        end
    end

    // Comb stage
    always @(posedge clk or posedge rst) begin
        if (rst) begin
            for (i = 0; i < N; i = i + 1) begin
                i_comb[i] <= 48'b0;
                q_comb[i] <= 48'b0;
                i_comb_d[i] <= 48'b0;
                q_comb_d[i] <= 48'b0;
            end
        end else if (decim_valid) begin
            // First comb stage
            i_comb[0] <= i_int[N-1] - i_comb_d[0];
            q_comb[0] <= q_int[N-1] - q_comb_d[0];
            i_comb_d[0] <= i_comb[0];
            q_comb_d[0] <= q_comb[0];

            // Subsequent comb stages
            for (i = 1; i < N; i = i + 1) begin
                i_comb[i] <= i_comb[i-1] - i_comb_d[i];
                q_comb[i] <= q_comb[i-1] - q_comb_d[i];
                i_comb_d[i] <= i_comb[i];
                q_comb_d[i] <= q_comb[i];
            end
        end
    end

    // Output assignment (truncate to 32 bits)
    assign i_data_out = i_comb[N-1][31:0];
    assign q_data_out = q_comb[N-1][31:0];
    assign data_valid_out = decim_valid;

endmodule
