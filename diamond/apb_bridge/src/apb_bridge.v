// AHB-to-APB Bridge - Simple bus bridge
// Target: LFE5U-45F (ECP5)
// Translates AHB-Lite transactions to APB

module apb_bridge (
    input         clk,
    input         reset_n,
    // AHB-Lite slave interface
    input  [31:0] haddr,
    input  [31:0] hwdata,
    input         hwrite,
    input         hsel,
    input  [1:0]  htrans,
    output reg [31:0] hrdata,
    output reg        hready,
    // APB master interface
    output reg [31:0] paddr,
    output reg [31:0] pwdata,
    output reg        pwrite,
    output reg        psel,
    output reg        penable,
    input  [31:0]     prdata,
    input             pready
);

    localparam IDLE   = 2'b00;
    localparam SETUP  = 2'b01;
    localparam ACCESS = 2'b10;

    reg [1:0] state;
    reg [31:0] addr_reg;
    reg [31:0] wdata_reg;
    reg        write_reg;

    // AHB transfer types
    localparam HTRANS_IDLE = 2'b00;
    localparam HTRANS_NONSEQ = 2'b10;

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            state    <= IDLE;
            hready   <= 1'b1;
            hrdata   <= 32'd0;
            paddr    <= 32'd0;
            pwdata   <= 32'd0;
            pwrite   <= 1'b0;
            psel     <= 1'b0;
            penable  <= 1'b0;
            addr_reg <= 32'd0;
            wdata_reg<= 32'd0;
            write_reg<= 1'b0;
        end else begin
            case (state)
                IDLE: begin
                    penable <= 1'b0;
                    psel    <= 1'b0;
                    if (hsel && (htrans == HTRANS_NONSEQ)) begin
                        addr_reg  <= haddr;
                        write_reg <= hwrite;
                        hready    <= 1'b0;
                        state     <= SETUP;
                    end else begin
                        hready <= 1'b1;
                    end
                end

                SETUP: begin
                    paddr   <= addr_reg;
                    pwrite  <= write_reg;
                    psel    <= 1'b1;
                    penable <= 1'b0;
                    if (write_reg)
                        pwdata <= hwdata;
                    state <= ACCESS;
                end

                ACCESS: begin
                    penable <= 1'b1;
                    if (pready) begin
                        if (!write_reg)
                            hrdata <= prdata;
                        hready  <= 1'b1;
                        psel    <= 1'b0;
                        penable <= 1'b0;
                        state   <= IDLE;
                    end
                end

                default: state <= IDLE;
            endcase
        end
    end

endmodule
