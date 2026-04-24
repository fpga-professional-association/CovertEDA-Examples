// =============================================================================
// Design      : PID Controller
// Module      : pid_controller
// Description : 16-bit PID controller with setpoint, feedback, output
// Device      : LIFCL-40-7BG400I
// Frequency   : 25 MHz
// =============================================================================

module pid_controller (
    input   wire                clk,
    input   wire                rst_n,
    input   wire                update,         // Update strobe
    input   wire signed [15:0]  setpoint,       // Desired value
    input   wire signed [15:0]  feedback,       // Measured value
    input   wire [7:0]          kp,             // Proportional gain
    input   wire [7:0]          ki,             // Integral gain
    input   wire [7:0]          kd,             // Derivative gain
    output  reg  signed [15:0]  pid_out,        // Controller output
    output  reg                 out_valid       // Output valid strobe
);

    reg signed [15:0] error;
    reg signed [15:0] error_prev;
    reg signed [31:0] integral;
    reg signed [15:0] derivative;
    reg signed [31:0] p_term, i_term, d_term;
    reg signed [31:0] sum;

    // Saturation limits
    localparam signed [31:0] INT_MAX =  32'sd32767;
    localparam signed [31:0] INT_MIN = -32'sd32768;
    localparam signed [31:0] INTEG_MAX =  32'sd1000000;
    localparam signed [31:0] INTEG_MIN = -32'sd1000000;

    // Saturate function
    function signed [15:0] saturate;
        input signed [31:0] val;
        begin
            if (val > INT_MAX)
                saturate = 16'sd32767;
            else if (val < INT_MIN)
                saturate = -16'sd32768;
            else
                saturate = val[15:0];
        end
    endfunction

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            error      <= 16'sd0;
            error_prev <= 16'sd0;
            integral   <= 32'sd0;
            derivative <= 16'sd0;
            p_term     <= 32'sd0;
            i_term     <= 32'sd0;
            d_term     <= 32'sd0;
            sum        <= 32'sd0;
            pid_out    <= 16'sd0;
            out_valid  <= 1'b0;
        end else if (update) begin
            // Compute error
            error <= setpoint - feedback;

            // Proportional term
            p_term <= $signed({1'b0, kp}) * error;

            // Integral term with anti-windup
            if (integral + error > INTEG_MAX)
                integral <= INTEG_MAX;
            else if (integral + error < INTEG_MIN)
                integral <= INTEG_MIN;
            else
                integral <= integral + error;
            i_term <= $signed({1'b0, ki}) * integral[15:0];

            // Derivative term
            derivative <= error - error_prev;
            d_term <= $signed({1'b0, kd}) * derivative;
            error_prev <= error;

            // Sum and saturate
            sum <= p_term + i_term + d_term;
            pid_out   <= saturate(sum >>> 8);
            out_valid <= 1'b1;
        end else begin
            out_valid <= 1'b0;
        end
    end

endmodule
