import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QGridLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QKeyEvent


class SudokuCell(QLineEdit):
    def __init__(self, row, col, parent_grid):
        super().__init__()
        self.row = row
        self.col = col
        self.parent_grid = parent_grid
        self.setFixedSize(50, 50)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFont(QFont("Arial", 16))
        self.setMaxLength(1)

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        text = event.text()
        modifiers = event.modifiers()

        if text.isdigit() and "1" <= text <= "9":
            self.setText(text)
            self._move_focus_right()
            return

        if key == Qt.Key.Key_Space:
            self.setText("")
            self._move_focus_right()
            return

        if key in (Qt.Key.Key_Enter, Qt.Key.Key_Return):
            if modifiers == Qt.KeyboardModifier.ShiftModifier:
                self._move_focus_up()
            else:
                self._move_focus_down()
            return

        if key in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete):
            if self.text() == "":
                self._move_focus_left()
            else:
                self.setText("")
            return

        if key in (Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down):
            super().keyPressEvent(event)
            return

        if key == Qt.Key.Key_Tab:
            super().keyPressEvent(event)
            return

    def _move_focus_right(self):
        next_row, next_col = self.row, self.col + 1
        if next_col >= 9:
            next_col = 0
            next_row += 1
        if next_row < 9:
            self._set_focus_to(next_row, next_col)

    def _move_focus_left(self):
        prev_row, prev_col = self.row, self.col - 1
        if prev_col < 0:
            prev_col = 8
            prev_row -= 1
        if prev_row >= 0:
            self._set_focus_to(prev_row, prev_col)

    def _move_focus_down(self):
        next_row = self.row + 1
        if next_row < 9:
            self._set_focus_to(next_row, self.col)

    def _move_focus_up(self):
        prev_row = self.row - 1
        if prev_row >= 0:
            self._set_focus_to(prev_row, self.col)

    def _set_focus_to(self, row, col):
        cell = self.parent_grid[row][col]
        cell.setFocus()
        cell.selectAll()


class SudokuSolverApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Решатель Судоку")
        self.setGeometry(300, 300, 620, 720)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.grid_inputs = [[None for _ in range(9)] for _ in range(9)]
        grid_layout = QGridLayout()
        grid_layout.setSpacing(2)

        for i in range(9):
            for j in range(9):
                cell = SudokuCell(i, j, self.grid_inputs)
                if (i // 3 + j // 3) % 2 == 0:
                    cell.setStyleSheet("background-color: #f0f0f0;")
                else:
                    cell.setStyleSheet("background-color: #ffffff;")
                self.grid_inputs[i][j] = cell
                grid_layout.addWidget(cell, i, j)

        self.solve_button = QPushButton("Решить")
        self.solve_button.setFont(QFont("Arial", 12))
        self.solve_button.clicked.connect(self.solve_sudoku)

        self.reset_button = QPushButton("Решить заново")
        self.reset_button.setFont(QFont("Arial", 12))
        self.reset_button.clicked.connect(self.reset_board)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.solve_button)
        button_layout.addWidget(self.reset_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(grid_layout)
        main_layout.addLayout(button_layout)

        central_widget.setLayout(main_layout)
        self.grid_inputs[0][0].setFocus()

    def get_board_from_ui(self):
        board = [[0 for _ in range(9)] for _ in range(9)]
        for i in range(9):
            for j in range(9):
                text = self.grid_inputs[i][j].text().strip()
                if text.isdigit() and "1" <= text <= "9":
                    board[i][j] = int(text)
        return board

    def set_board_to_ui(self, board):
        for i in range(9):
            for j in range(9):
                val = board[i][j]
                self.grid_inputs[i][j].setText(str(val) if val != 0 else "")

    def reset_board(self):
        for i in range(9):
            for j in range(9):
                self.grid_inputs[i][j].setText("")
        self.grid_inputs[0][0].setFocus()

    def is_valid(self, board, row, col, num):
        for j in range(9):
            if board[row][j] == num:
                return False
        for i in range(9):
            if board[i][col] == num:
                return False
        sr, sc = 3 * (row // 3), 3 * (col // 3)
        for r in range(sr, sr + 3):
            for c in range(sc, sc + 3):
                if board[r][c] == num:
                    return False
        return True

    def find_empty(self, board):
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    return i, j
        return None

    def solve_sudoku_logic(self, board):
        empty = self.find_empty(board)
        if not empty:
            return True
        row, col = empty
        for num in range(1, 10):
            if self.is_valid(board, row, col, num):
                board[row][col] = num
                if self.solve_sudoku_logic(board):
                    return True
                board[row][col] = 0
        return False

    def solve_sudoku(self):
        board = self.get_board_from_ui()
        if self.solve_sudoku_logic(board):
            self.set_board_to_ui(board)
        else:
            QMessageBox.warning(self, "Ошибка", "Судоку не имеет решения!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SudokuSolverApp()
    window.show()
    sys.exit(app.exec())
