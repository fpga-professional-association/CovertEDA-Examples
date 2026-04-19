// 4-Master Round-Robin Wishbone Arbiter
// Target: MPF300T (PolarFire)

module wishbone_arbiter (
    input         clk,
    input         reset_n,
    // Master request/grant
    input  [3:0]  cyc_i,      // cycle request from each master
    output reg [3:0] gnt_o,   // grant to each master
    // Selected master signals (active master -> slave)
    input  [31:0] m0_adr, m1_adr, m2_adr, m3_adr,
    input  [31:0] m0_dat, m1_dat, m2_dat, m3_dat,
    input  [3:0]  m0_sel, m1_sel, m2_sel, m3_sel,
    input         m0_we,  m1_we,  m2_we,  m3_we,
    input         m0_stb, m1_stb, m2_stb, m3_stb,
    // Shared slave outputs
    output reg [31:0] s_adr_o,
    output reg [31:0] s_dat_o,
    output reg [3:0]  s_sel_o,
    output reg        s_we_o,
    output reg        s_stb_o,
    output reg        s_cyc_o
);

    reg [1:0] current_master;
    reg [1:0] last_granted;
    reg       bus_busy;

    // Round-robin priority encoder
    function [1:0] next_master;
        input [3:0] requests;
        input [1:0] last;
        reg [1:0] i;
        reg found;
        begin
            next_master = last;
            found = 0;
            for (i = 0; i < 3; i = i + 1) begin
                if (!found && requests[(last + i + 1) & 2'b11]) begin
                    next_master = (last + i + 1) & 2'b11;
                    found = 1;
                end
            end
            if (!found && requests[last])
                next_master = last;
        end
    endfunction

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            gnt_o          <= 4'b0000;
            current_master <= 2'd0;
            last_granted   <= 2'd0;
            bus_busy       <= 1'b0;
            s_adr_o <= 0; s_dat_o <= 0; s_sel_o <= 0;
            s_we_o  <= 0; s_stb_o <= 0; s_cyc_o <= 0;
        end else begin
            if (!bus_busy) begin
                if (cyc_i != 0) begin
                    current_master <= next_master(cyc_i, last_granted);
                    bus_busy       <= 1'b1;
                    gnt_o          <= 4'b0001 << next_master(cyc_i, last_granted);
                    last_granted   <= next_master(cyc_i, last_granted);
                end else begin
                    gnt_o   <= 4'b0000;
                    s_cyc_o <= 1'b0;
                    s_stb_o <= 1'b0;
                end
            end else begin
                // Current master lost cyc -> release bus
                if (!cyc_i[current_master]) begin
                    bus_busy <= 1'b0;
                    gnt_o    <= 4'b0000;
                    s_cyc_o  <= 1'b0;
                    s_stb_o  <= 1'b0;
                end
            end

            // Mux active master to slave
            case (current_master)
                2'd0: begin s_adr_o<=m0_adr; s_dat_o<=m0_dat; s_sel_o<=m0_sel; s_we_o<=m0_we; s_stb_o<=m0_stb; s_cyc_o<=cyc_i[0]; end
                2'd1: begin s_adr_o<=m1_adr; s_dat_o<=m1_dat; s_sel_o<=m1_sel; s_we_o<=m1_we; s_stb_o<=m1_stb; s_cyc_o<=cyc_i[1]; end
                2'd2: begin s_adr_o<=m2_adr; s_dat_o<=m2_dat; s_sel_o<=m2_sel; s_we_o<=m2_we; s_stb_o<=m2_stb; s_cyc_o<=cyc_i[2]; end
                2'd3: begin s_adr_o<=m3_adr; s_dat_o<=m3_dat; s_sel_o<=m3_sel; s_we_o<=m3_we; s_stb_o<=m3_stb; s_cyc_o<=cyc_i[3]; end
            endcase
        end
    end

endmodule
