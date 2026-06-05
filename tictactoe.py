import math
import random
from hand_tracker import HandTracker as HT

class TicTacToeMode:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.board = [['', '', ''], ['', '', ''], ['', '', '']]
        self.player_turn = True
        self.winner = None
        self.game_over = False
        self.was_pinching = False
        self.ai_delay_frames = 0
        self.cursor_x = -1
        self.cursor_y = -1
        self.is_pinching = False

    def ai_move(self):
        if self.game_over: return
        b = self.board
        def win_or_block(mark):
            for i in range(3):
                if b[i].count(mark) == 2 and b[i].count('') == 1:
                    return (i, b[i].index(''))
                col = [b[0][i], b[1][i], b[2][i]]
                if col.count(mark) == 2 and col.count('') == 1:
                    return (col.index(''), i)
            d1 = [b[0][0], b[1][1], b[2][2]]
            if d1.count(mark) == 2 and d1.count('') == 1: return (d1.index(''), d1.index(''))
            d2 = [b[0][2], b[1][1], b[2][0]]
            if d2.count(mark) == 2 and d2.count('') == 1: return (d2.index(''), 2-d2.index(''))
            return None

        move = win_or_block('O') or win_or_block('X')
        if not move:
            empty = [(r, c) for r in range(3) for c in range(3) if b[r][c] == '']
            if empty: move = random.choice(empty)
                
        if move:
            self.board[move[0]][move[1]] = 'O'
            self._check_winner()
            
        self.player_turn = True

    def _check_winner(self):
        b = self.board
        for i in range(3):
            if b[i][0] == b[i][1] == b[i][2] != '': self.winner = b[i][0]
            if b[0][i] == b[1][i] == b[2][i] != '': self.winner = b[0][i]
        if b[0][0] == b[1][1] == b[2][2] != '': self.winner = b[0][0]
        if b[0][2] == b[1][1] == b[2][0] != '': self.winner = b[0][2]
        
        if self.winner:
            self.game_over = True
        elif all(b[r][c] != '' for r in range(3) for c in range(3)):
            self.winner = 'Tie'
            self.game_over = True

    def process(self, landmarks, frame_w, frame_h):
        # Grid bounds in backend logic:
        # Match CSS width: 70% exactly
        grid_size = frame_w * 0.7
        cx, cy = frame_w / 2, frame_h / 2
        top_x, top_y = cx - grid_size/2, cy - grid_size/2
        cell_size = grid_size / 3

        if landmarks:
            lms = landmarks[0]
            ix, iy, _ = lms[HT.INDEX_TIP]
            tx, ty, _ = lms[HT.THUMB_TIP]
            
            self.cursor_x = ix / frame_w
            self.cursor_y = iy / frame_h
            
            dist = math.hypot(tx-ix, ty-iy)
            # Relax pinch distance slightly
            is_pinch = dist < 50
            self.is_pinching = is_pinch
            
            if is_pinch:
                if not self.was_pinching:
                    self.was_pinching = True
                    if self.game_over:
                        self.reset()
                    elif self.player_turn:
                        # Check cell
                        if top_x < ix < top_x + grid_size and top_y < iy < top_y + grid_size:
                            c = int((ix - top_x) // cell_size)
                            r = int((iy - top_y) // cell_size)
                            if 0 <= c <= 2 and 0 <= r <= 2 and self.board[r][c] == '':
                                self.board[r][c] = 'X'
                                self._check_winner()
                                if not self.game_over:
                                    self.player_turn = False
                                    self.ai_delay_frames = 15
            else:
                self.was_pinching = False
        else:
            self.cursor_x = -1
            self.cursor_y = -1
            self.is_pinching = False
            
        if not self.player_turn and not self.game_over:
            self.ai_delay_frames -= 1
            if self.ai_delay_frames <= 0:
                self.ai_move()

        return {
            "board": self.board,
            "player_turn": self.player_turn,
            "game_over": self.game_over,
            "winner": self.winner,
            "cursor": {"x": self.cursor_x, "y": self.cursor_y, "pinching": self.is_pinching}
        }
