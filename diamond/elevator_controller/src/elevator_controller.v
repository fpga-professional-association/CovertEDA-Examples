// 4-Floor Elevator Controller FSM
// Target: LFE5U-25F (ECP5)

module elevator_controller (
    input        clk,
    input        reset_n,
    input  [3:0] floor_request,  // one-hot: floor 1-4
    input  [3:0] floor_sensor,   // one-hot: which floor elevator is at
    output reg [1:0] current_floor,  // 0=floor1, 1=floor2, 2=floor3, 3=floor4
    output reg       door_open,
    output reg       motor_up,
    output reg       motor_down,
    output reg [3:0] floor_led       // indicator for each floor
);

    localparam IDLE     = 3'd0;
    localparam MOVE_UP  = 3'd1;
    localparam MOVE_DN  = 3'd2;
    localparam DOOR_OP  = 3'd3;
    localparam DOOR_WAIT= 3'd4;

    reg [2:0] state;
    reg [1:0] target_floor;
    reg [7:0] door_timer;
    reg [3:0] pending_requests;

    // Find nearest request
    function [1:0] find_target;
        input [3:0] requests;
        input [1:0] current;
        integer i;
        reg [1:0] best;
        reg found;
        begin
            best = current;
            found = 0;
            for (i = 0; i < 4; i = i + 1) begin
                if (requests[i] && !found) begin
                    best = i[1:0];
                    found = 1;
                end
            end
            find_target = best;
        end
    endfunction

    always @(posedge clk or negedge reset_n) begin
        if (!reset_n) begin
            state           <= IDLE;
            current_floor   <= 2'd0;
            target_floor    <= 2'd0;
            door_open       <= 1'b0;
            motor_up        <= 1'b0;
            motor_down      <= 1'b0;
            floor_led       <= 4'b0001;
            door_timer      <= 8'd0;
            pending_requests<= 4'd0;
        end else begin
            // Latch new requests
            pending_requests <= pending_requests | floor_request;

            case (state)
                IDLE: begin
                    motor_up   <= 0;
                    motor_down <= 0;
                    door_open  <= 0;
                    if (pending_requests != 0) begin
                        target_floor <= find_target(pending_requests, current_floor);
                        if (find_target(pending_requests, current_floor) > current_floor)
                            state <= MOVE_UP;
                        else if (find_target(pending_requests, current_floor) < current_floor)
                            state <= MOVE_DN;
                        else
                            state <= DOOR_OP;
                    end
                end

                MOVE_UP: begin
                    motor_up   <= 1;
                    motor_down <= 0;
                    if (current_floor < target_floor)
                        current_floor <= current_floor + 1;
                    else
                        state <= DOOR_OP;
                end

                MOVE_DN: begin
                    motor_up   <= 0;
                    motor_down <= 1;
                    if (current_floor > target_floor)
                        current_floor <= current_floor - 1;
                    else
                        state <= DOOR_OP;
                end

                DOOR_OP: begin
                    motor_up   <= 0;
                    motor_down <= 0;
                    door_open  <= 1;
                    door_timer <= 8'd10;
                    pending_requests[current_floor] <= 1'b0;
                    state <= DOOR_WAIT;
                end

                DOOR_WAIT: begin
                    if (door_timer > 0)
                        door_timer <= door_timer - 1;
                    else begin
                        door_open <= 0;
                        state     <= IDLE;
                    end
                end

                default: state <= IDLE;
            endcase

            // Update floor LED
            floor_led <= (4'b0001 << current_floor);
        end
    end

endmodule
