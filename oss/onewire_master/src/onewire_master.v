// 1-Wire Bus Master (Dallas/Maxim Protocol)
// Device: iCE40UP5K
// Supports reset, write-bit, and read-bit operations

module onewire_master (
    input        clk,
    input        rst_n,
    input  [1:0] cmd,        // 0=idle, 1=reset, 2=write_bit, 3=read_bit
    input        cmd_valid,
    input        write_bit,
    output       read_bit,
    output       busy,
    output       presence,
    output       ow_out,     // drive low
    output       ow_oe,      // output enable (active high)
    input        ow_in       // sampled input
);

    // Timing at 12 MHz (83.3ns per tick)
    parameter T_RESET    = 16'd5760;  // 480us
    parameter T_PRESENCE = 16'd720;   // 60us wait
    parameter T_SLOT     = 16'd720;   // 60us slot
    parameter T_LOW0     = 16'd720;   // 60us for write-0
    parameter T_LOW1     = 16'd72;    // 6us for write-1
    parameter T_SAMPLE   = 16'd108;   // 9us for read sample

    reg [2:0] state;
    reg [15:0] timer;
    reg       read_bit_r;
    reg       presence_r;
    reg       ow_out_r;
    reg       ow_oe_r;

    localparam S_IDLE     = 3'd0;
    localparam S_RESET_LO = 3'd1;
    localparam S_RESET_HI = 3'd2;
    localparam S_WRITE_LO = 3'd3;
    localparam S_WRITE_HI = 3'd4;
    localparam S_READ_LO  = 3'd5;
    localparam S_READ_HI  = 3'd6;

    assign read_bit  = read_bit_r;
    assign busy      = (state != S_IDLE);
    assign presence  = presence_r;
    assign ow_out    = ow_out_r;
    assign ow_oe     = ow_oe_r;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state      <= S_IDLE;
            timer      <= 16'd0;
            read_bit_r <= 1'b1;
            presence_r <= 1'b0;
            ow_out_r   <= 1'b1;
            ow_oe_r    <= 1'b0;
        end else begin
            case (state)
                S_IDLE: begin
                    ow_oe_r  <= 1'b0;
                    ow_out_r <= 1'b1;
                    if (cmd_valid) begin
                        timer <= 16'd0;
                        case (cmd)
                            2'd1: begin // Reset
                                ow_oe_r  <= 1'b1;
                                ow_out_r <= 1'b0;
                                state    <= S_RESET_LO;
                            end
                            2'd2: begin // Write bit
                                ow_oe_r  <= 1'b1;
                                ow_out_r <= 1'b0;
                                state    <= S_WRITE_LO;
                            end
                            2'd3: begin // Read bit
                                ow_oe_r  <= 1'b1;
                                ow_out_r <= 1'b0;
                                state    <= S_READ_LO;
                            end
                            default: ;
                        endcase
                    end
                end
                S_RESET_LO: begin
                    timer <= timer + 1'b1;
                    if (timer >= T_RESET) begin
                        ow_oe_r  <= 1'b0;  // Release bus
                        ow_out_r <= 1'b1;
                        timer    <= 16'd0;
                        state    <= S_RESET_HI;
                    end
                end
                S_RESET_HI: begin
                    timer <= timer + 1'b1;
                    if (timer == T_PRESENCE)
                        presence_r <= ~ow_in;  // Presence = bus pulled low
                    if (timer >= T_RESET) begin
                        state <= S_IDLE;
                    end
                end
                S_WRITE_LO: begin
                    timer <= timer + 1'b1;
                    if (write_bit) begin
                        // Write-1: short low pulse
                        if (timer >= T_LOW1) begin
                            ow_oe_r <= 1'b0;
                            ow_out_r <= 1'b1;
                            state    <= S_WRITE_HI;
                            timer    <= 16'd0;
                        end
                    end else begin
                        // Write-0: long low pulse
                        if (timer >= T_LOW0) begin
                            ow_oe_r <= 1'b0;
                            ow_out_r <= 1'b1;
                            state    <= S_WRITE_HI;
                            timer    <= 16'd0;
                        end
                    end
                end
                S_WRITE_HI: begin
                    timer <= timer + 1'b1;
                    if (timer >= T_LOW1) begin
                        state <= S_IDLE;
                    end
                end
                S_READ_LO: begin
                    timer <= timer + 1'b1;
                    if (timer >= T_LOW1) begin
                        ow_oe_r  <= 1'b0;  // Release
                        ow_out_r <= 1'b1;
                        timer    <= 16'd0;
                        state    <= S_READ_HI;
                    end
                end
                S_READ_HI: begin
                    timer <= timer + 1'b1;
                    if (timer == T_SAMPLE)
                        read_bit_r <= ow_in;
                    if (timer >= T_SLOT) begin
                        state <= S_IDLE;
                    end
                end
            endcase
        end
    end

endmodule
