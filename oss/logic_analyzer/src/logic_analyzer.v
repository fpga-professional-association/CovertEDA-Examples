// Simple 8-Channel Logic Analyzer with Trigger
// Device: ECP5 LFE5U-25F
// Captures 8-bit samples into buffer on trigger

module logic_analyzer (
    input        clk,
    input        rst_n,
    input  [7:0] probe_in,
    input  [7:0] trigger_pattern,
    input  [7:0] trigger_mask,
    input        arm,
    output [7:0] read_data,
    input  [7:0] read_addr,
    input        read_en,
    output       triggered,
    output       capture_done
);

    parameter DEPTH = 256;

    reg [7:0] buffer [0:255];
    reg [7:0] wr_ptr;
    reg [1:0] state;
    reg       triggered_r;
    reg       done_r;
    reg [7:0] read_data_r;

    localparam S_IDLE    = 2'd0;
    localparam S_ARMED   = 2'd1;
    localparam S_CAPTURE = 2'd2;
    localparam S_DONE    = 2'd3;

    assign triggered    = triggered_r;
    assign capture_done = done_r;
    assign read_data    = read_data_r;

    wire trigger_match = ((probe_in & trigger_mask) == (trigger_pattern & trigger_mask));

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state       <= S_IDLE;
            wr_ptr      <= 8'd0;
            triggered_r <= 1'b0;
            done_r      <= 1'b0;
            read_data_r <= 8'd0;
        end else begin
            case (state)
                S_IDLE: begin
                    triggered_r <= 1'b0;
                    done_r      <= 1'b0;
                    if (arm) begin
                        wr_ptr <= 8'd0;
                        state  <= S_ARMED;
                    end
                end
                S_ARMED: begin
                    if (trigger_match) begin
                        triggered_r <= 1'b1;
                        state       <= S_CAPTURE;
                        buffer[0]   <= probe_in;
                        wr_ptr      <= 8'd1;
                    end
                end
                S_CAPTURE: begin
                    buffer[wr_ptr] <= probe_in;
                    wr_ptr         <= wr_ptr + 1'b1;
                    if (wr_ptr == 8'hFF) begin
                        done_r <= 1'b1;
                        state  <= S_DONE;
                    end
                end
                S_DONE: begin
                    if (read_en)
                        read_data_r <= buffer[read_addr];
                end
            endcase
        end
    end

endmodule
