// Bus Monitor - Bus activity monitor with transaction counter
// Quartus / Cyclone IV E (EP4CE6)
// Monitors a simple bus interface and counts transactions

module bus_monitor (
    input         clk,
    input         rst_n,
    input         bus_valid,    // bus transaction valid
    input         bus_ready,    // bus target ready
    input         bus_wr,       // 1=write, 0=read
    input  [7:0]  bus_addr,     // bus address
    input  [7:0]  bus_data,     // bus data
    output [15:0] total_count,  // total transaction count
    output [15:0] wr_count,     // write transaction count
    output [15:0] rd_count,     // read transaction count
    output [7:0]  last_addr,    // last transaction address
    output [7:0]  last_data,    // last transaction data
    output        bus_active    // bus currently active
);

    reg [15:0] total_reg;
    reg [15:0] wr_reg;
    reg [15:0] rd_reg;
    reg [7:0]  last_addr_reg;
    reg [7:0]  last_data_reg;
    reg        active_reg;

    assign total_count = total_reg;
    assign wr_count    = wr_reg;
    assign rd_count    = rd_reg;
    assign last_addr   = last_addr_reg;
    assign last_data   = last_data_reg;
    assign bus_active  = active_reg;

    wire transaction = bus_valid & bus_ready;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            total_reg     <= 16'd0;
            wr_reg        <= 16'd0;
            rd_reg        <= 16'd0;
            last_addr_reg <= 8'd0;
            last_data_reg <= 8'd0;
            active_reg    <= 1'b0;
        end else begin
            active_reg <= bus_valid;

            if (transaction) begin
                total_reg     <= total_reg + 16'd1;
                last_addr_reg <= bus_addr;
                last_data_reg <= bus_data;

                if (bus_wr)
                    wr_reg <= wr_reg + 16'd1;
                else
                    rd_reg <= rd_reg + 16'd1;
            end
        end
    end

endmodule
