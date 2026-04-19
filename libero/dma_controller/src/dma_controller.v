// Simple 2-Channel DMA Controller
// Target: MPF300T (PolarFire)

module dma_controller (
    input         clk,
    input         reset_n,
    // Channel 0 configuration
    input  [31:0] ch0_src_addr,
    input  [31:0] ch0_dst_addr,
    input  [15:0] ch0_length,
    input         ch0_start,
    output reg    ch0_done,
    // Channel 1 configuration
    input  [31:0] ch1_src_addr,
    input  [31:0] ch1_dst_addr,
    input  [15:0] ch1_length,
    input         ch1_start,
    output reg    ch1_done,
    // Memory interface
    output reg [31:0] mem_addr,
    output reg [31:0] mem_wdata,
    input  [31:0]     mem_rdata,
    output reg        mem_rd,
    output reg        mem_wr,
    input             mem_ready,
    output reg        busy
);

    localparam IDLE    = 3'd0;
    localparam READ    = 3'd1;
    localparam WRITE   = 3'd2;
    localparam NEXT    = 3'd3;

    reg [2:0]  state;
    reg        active_ch;     // 0 or 1
    reg [31:0] src_addr, dst_addr;
    reg [15:0] remaining;
    reg [31:0] data_buf;

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            state     <= IDLE;
            ch0_done  <= 1'b0;
            ch1_done  <= 1'b0;
            mem_addr  <= 32'd0;
            mem_wdata <= 32'd0;
            mem_rd    <= 1'b0;
            mem_wr    <= 1'b0;
            busy      <= 1'b0;
            active_ch <= 1'b0;
            src_addr  <= 32'd0;
            dst_addr  <= 32'd0;
            remaining <= 16'd0;
            data_buf  <= 32'd0;
        end else begin
            ch0_done <= 1'b0;
            ch1_done <= 1'b0;

            case (state)
                IDLE: begin
                    mem_rd <= 0;
                    mem_wr <= 0;
                    busy   <= 0;
                    if (ch0_start) begin
                        src_addr  <= ch0_src_addr;
                        dst_addr  <= ch0_dst_addr;
                        remaining <= ch0_length;
                        active_ch <= 0;
                        busy      <= 1;
                        state     <= READ;
                    end else if (ch1_start) begin
                        src_addr  <= ch1_src_addr;
                        dst_addr  <= ch1_dst_addr;
                        remaining <= ch1_length;
                        active_ch <= 1;
                        busy      <= 1;
                        state     <= READ;
                    end
                end

                READ: begin
                    mem_addr <= src_addr;
                    mem_rd   <= 1;
                    mem_wr   <= 0;
                    if (mem_ready) begin
                        data_buf <= mem_rdata;
                        mem_rd   <= 0;
                        state    <= WRITE;
                    end
                end

                WRITE: begin
                    mem_addr  <= dst_addr;
                    mem_wdata <= data_buf;
                    mem_wr    <= 1;
                    mem_rd    <= 0;
                    if (mem_ready) begin
                        mem_wr <= 0;
                        state  <= NEXT;
                    end
                end

                NEXT: begin
                    src_addr  <= src_addr + 4;
                    dst_addr  <= dst_addr + 4;
                    remaining <= remaining - 1;
                    if (remaining <= 1) begin
                        if (active_ch == 0)
                            ch0_done <= 1;
                        else
                            ch1_done <= 1;
                        state <= IDLE;
                    end else begin
                        state <= READ;
                    end
                end

                default: state <= IDLE;
            endcase
        end
    end

endmodule
