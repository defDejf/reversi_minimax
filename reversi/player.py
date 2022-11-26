import copy
import time

FREE_TILE = -1
TIME_LIMIT = 0.8


class MyPlayer:
    '''Minimax player with alpha-beta pruning, adjusts depth dynamically'''

    def __init__(self, my_color, opponent_color):
        self.name = 'skopadav'
        self.my_color = my_color
        self.opponent_color = opponent_color
        self.depth = 5

    def move(self, board):
        start = time.time()
        move, end_depth = self.run_nodes(board, self.my_color, self.depth, time.time() + TIME_LIMIT)
        if (time.time() - start) < TIME_LIMIT:
            self.depth += 1
        if end_depth > 0:
            self.depth -= 1
        return move

    def get_free_positions(self, board):
        free_pos = []
        for r in range(len(board)):
            for c in range(len(board[r])):
                if board[r][c] == FREE_TILE:
                    free_pos.append((r, c))
        return free_pos

    # valid moves are stored in format:
    # [(tested_move),[[(line1_turned_stone1),(line1_turned_stone2)...],[(line2_turned_stone1),(line2_turned_stone1)...]...]]
    def get_valid_moves(self, board, color):
        valid_moves_w_lines = []
        start_pos = self.get_free_positions(board)
        if start_pos:
            for pos in start_pos:
                pos_w_lines = self.search_all_directions(pos, board, color)
                if pos_w_lines:
                    valid_moves_w_lines.append(pos_w_lines)
        return valid_moves_w_lines

    def search_all_directions(self, pos, board, color):
        # direction is in format (row_increment, column_increment)
        directions = [(-1, 0),  # up
                      (-1, 1),  # up-right
                      (0, 1),  # right
                      (1, 1),  # down-right
                      (1, 0),  # down
                      (1, -1),  # down-left
                      (0, -1),  # left
                      (-1, -1)]  # up-left

        lines = []

        for direction in directions:
            line = self.search_in_direction(pos, direction, board, color)
            if line:
                lines.append(line)
        if lines:
            pos_w_lines = [pos, lines]
            return pos_w_lines

    def search_in_direction(self, pos, direction, board, color):
        border = len(board) - 1
        line = []
        row = pos[0]
        clm = pos[1]
        while (row <= border and clm <= border) and (row >= 0 and clm >= 0):
            if (row + direction[0] > border or clm + direction[1] > border) or \
                    (row + direction[0] < 0 or clm + direction[1] < 0):
                return []
            else:
                row += direction[0]
                clm += direction[1]
            if board[row][clm] == abs(color - 1):
                line.append((row, clm))
            elif board[row][clm] == color:
                return line
            elif board[row][clm] == FREE_TILE:
                return []

    def calculate_board_weighted(self, board):
        tile_values = [
            [1000, -10, 20, 10, 10, 20, -10, 1000],
            [-10, -10, 20, 1, 1, 20, -10, -10],
            [20, 20, 20, 1, 1, 20, 20, 20],
            [10, 1, 1, 5, 5, 1, 1, 10],
            [10, 1, 1, 5, 5, 1, 1, 10],
            [20, 20, 20, 1, 1, 20, 20, 20],
            [-10, -10, 20, 1, 1, 20, -10, -10],
            [1000, -10, 20, 10, 10, 20, -10, 1000]]
        my_score = 0
        opponent_score = 0
        my_score_weighted = 0
        opponent_score_weighted = 0
        free_tiles_count = 0
        for r in range(len(board)):
            for c in range(len(board)):
                if board[r][c] == self.my_color:
                    my_score += 1
                    my_score_weighted += tile_values[r][c]
                elif board[r][c] == self.opponent_color:
                    opponent_score += 1
                    opponent_score_weighted += tile_values[r][c]
                else:
                    free_tiles_count += 1
        if free_tiles_count > 0:
            return my_score_weighted, opponent_score_weighted
        else:
            return my_score, opponent_score

    def update_board(self, board, valid_move, color):
        new_board = copy.deepcopy(board)
        new_board[valid_move[0][0]][valid_move[0][1]] = color
        for line in valid_move[1]:
            for position in line:
                new_board[position[0]][position[1]] = color
        return new_board

    def min_node(self, board, color, depth, end_time, alpha, beta):
        moves = self.get_valid_moves(board, color)
        if moves == [] or (time.time() >= end_time) or depth == 0:
            my_score, opp_score = self.calculate_board_weighted(board)
            return opp_score, depth
        else:
            tmp_min_score = 999999
            for move in moves:
                new_board = self.update_board(board, move, color)
                new_score, end_depth = self.max_node(new_board, abs(color-1), depth - 1, end_time, alpha, beta)
                if new_score < tmp_min_score:
                    tmp_min_score = new_score
                    beta = min(tmp_min_score, beta)
                    print("pruned min")
                if beta <= alpha:
                    break
            return tmp_min_score, end_depth

    def max_node(self, board, color, depth, end_time, alpha, beta):
        moves = self.get_valid_moves(board, color)
        if moves == [] or (time.time() >= end_time) or depth == 0:
            my_score, opp_score = self.calculate_board_weighted(board)
            return my_score, depth
        else:
            tmp_max_score = -999999
            for move in moves:
                new_board = self.update_board(board, move, color)
                new_score, end_depth = self.min_node(new_board, abs(color-1), depth - 1, end_time, alpha, beta)
                if new_score > tmp_max_score:
                    tmp_max_score = new_score
                    alpha = max(alpha, tmp_max_score)
                    print("pruned max")
                if beta <= alpha:
                    break
            return tmp_max_score, end_depth

    def run_nodes(self, board, color, depth, end_time):
        best_score = -999999
        valid_moves = self.get_valid_moves(board, color)
        for move in valid_moves:
            new_board = self.update_board(board, move, color)
            score_for_move, end_depth = self.min_node(new_board, abs(color-1), depth-1, end_time, -999999, 999999)
            if score_for_move > best_score:
                best_score = score_for_move
                move_to_make = move[0]
        return move_to_make, end_depth
