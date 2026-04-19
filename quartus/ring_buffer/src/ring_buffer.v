// Ring Buffer - 16-entry x 16-bit circular buffer
// Quartus / Cyclone IV E (EP4CE6)

module ring_buffer (
    input        clk,
    input        rst_n,
    input        wr_en,
    input        rd_en,
    input  [15:0] din,
    output [15:0] dout,
    output       full,
    output       empty,
    output [4:0] count
);

    reg [15:0] mem [0:15];
    reg [3:0]  wr_ptr;
    reg [3:0]  rd_ptr;
    reg [4:0]  cnt;

    assign full  = (cnt == 5'd16);
    assign empty = (cnt == 5'd0);
    assign count = cnt;

    reg [15:0] dout_reg;
    assign dout = dout_reg;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            wr_ptr   <= 4'd0;
            rd_ptr   <= 4'd0;
            cnt      <= 5'd0;
            dout_reg <= 16'd0;
        end else begin
            // Write operation
            if (wr_en && !full) begin
                mem[wr_ptr] <= din;
                wr_ptr <= wr_ptr + 4'd1;
            end

            // Read operation
            if (rd_en && !empty) begin
                dout_reg <= mem[rd_ptr];
                rd_ptr <= rd_ptr + 4'd1;
            end

            // Update count
            if (wr_en && !full && !(rd_en && !empty))
                cnt <= cnt + 5'd1;
            else if (rd_en && !empty && !(wr_en && !full))
                cnt <= cnt - 5'd1;
        end
    end

endmodule
