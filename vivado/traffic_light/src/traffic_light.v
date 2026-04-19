// =============================================================================
// Traffic Light FSM with Pedestrian Crossing
// Device: Xilinx Artix-7 XC7A35T
// =============================================================================

module traffic_light (
    input  wire       clk,
    input  wire       rst_n,
    input  wire       ped_request,   // Pedestrian crossing button
    output reg  [2:0] main_light,   // [2]=Red, [1]=Yellow, [0]=Green
    output reg  [2:0] side_light,   // [2]=Red, [1]=Yellow, [0]=Green
    output reg        ped_walk,      // Pedestrian walk signal
    output reg        ped_dont_walk  // Pedestrian don't walk signal
);

    // Timer parameters (small for simulation)
    parameter GREEN_TIME   = 20;
    parameter YELLOW_TIME  = 5;
    parameter PED_TIME     = 10;
    parameter ALL_RED_TIME = 2;

    // States
    localparam S_MAIN_GREEN   = 3'd0;
    localparam S_MAIN_YELLOW  = 3'd1;
    localparam S_ALL_RED_1    = 3'd2;
    localparam S_SIDE_GREEN   = 3'd3;
    localparam S_SIDE_YELLOW  = 3'd4;
    localparam S_ALL_RED_2    = 3'd5;
    localparam S_PED_WALK     = 3'd6;

    reg [2:0]  state;
    reg [7:0]  timer;
    reg        ped_pending;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state        <= S_MAIN_GREEN;
            timer        <= 8'd0;
            ped_pending  <= 1'b0;
            main_light   <= 3'b001;  // Green
            side_light   <= 3'b100;  // Red
            ped_walk     <= 1'b0;
            ped_dont_walk <= 1'b1;
        end else begin
            // Latch pedestrian request
            if (ped_request) begin
                ped_pending <= 1'b1;
            end

            case (state)
                S_MAIN_GREEN: begin
                    main_light    <= 3'b001;
                    side_light    <= 3'b100;
                    ped_walk      <= 1'b0;
                    ped_dont_walk <= 1'b1;
                    if (timer >= GREEN_TIME) begin
                        state <= S_MAIN_YELLOW;
                        timer <= 8'd0;
                    end else begin
                        timer <= timer + 1'b1;
                    end
                end

                S_MAIN_YELLOW: begin
                    main_light <= 3'b010;
                    side_light <= 3'b100;
                    if (timer >= YELLOW_TIME) begin
                        state <= S_ALL_RED_1;
                        timer <= 8'd0;
                    end else begin
                        timer <= timer + 1'b1;
                    end
                end

                S_ALL_RED_1: begin
                    main_light <= 3'b100;
                    side_light <= 3'b100;
                    if (timer >= ALL_RED_TIME) begin
                        if (ped_pending) begin
                            state <= S_PED_WALK;
                        end else begin
                            state <= S_SIDE_GREEN;
                        end
                        timer <= 8'd0;
                    end else begin
                        timer <= timer + 1'b1;
                    end
                end

                S_PED_WALK: begin
                    main_light    <= 3'b100;
                    side_light    <= 3'b100;
                    ped_walk      <= 1'b1;
                    ped_dont_walk <= 1'b0;
                    if (timer >= PED_TIME) begin
                        state       <= S_SIDE_GREEN;
                        timer       <= 8'd0;
                        ped_pending <= 1'b0;
                        ped_walk    <= 1'b0;
                        ped_dont_walk <= 1'b1;
                    end else begin
                        timer <= timer + 1'b1;
                    end
                end

                S_SIDE_GREEN: begin
                    main_light    <= 3'b100;
                    side_light    <= 3'b001;
                    ped_walk      <= 1'b0;
                    ped_dont_walk <= 1'b1;
                    if (timer >= GREEN_TIME) begin
                        state <= S_SIDE_YELLOW;
                        timer <= 8'd0;
                    end else begin
                        timer <= timer + 1'b1;
                    end
                end

                S_SIDE_YELLOW: begin
                    main_light <= 3'b100;
                    side_light <= 3'b010;
                    if (timer >= YELLOW_TIME) begin
                        state <= S_ALL_RED_2;
                        timer <= 8'd0;
                    end else begin
                        timer <= timer + 1'b1;
                    end
                end

                S_ALL_RED_2: begin
                    main_light <= 3'b100;
                    side_light <= 3'b100;
                    if (timer >= ALL_RED_TIME) begin
                        state <= S_MAIN_GREEN;
                        timer <= 8'd0;
                    end else begin
                        timer <= timer + 1'b1;
                    end
                end

                default: begin
                    state <= S_MAIN_GREEN;
                    timer <= 8'd0;
                end
            endcase
        end
    end

endmodule
