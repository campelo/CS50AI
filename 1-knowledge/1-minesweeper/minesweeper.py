import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count
        self.safes = set()
        self.mines = set()
        self.check_known_cells()
    
    def __eq__(self, other):
        return self.cells == other.cells and self.safes == other.safes and self.mines == other.mines and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def unknown_cells(self):
        return self.cells.difference(self.mines.union(self.safes))

    def current_unknown_data(self):
        return (self.unknown_cells(), self.count - len(self.mines))

    def check_known_cells(self):
        uCells, uCount = self.current_unknown_data()
        if len(uCells) > 0 and uCount == 0:
            self.safes.update(uCells)
            uCells, uCount = self.current_unknown_data()
        if len(uCells) > 0 and uCount == len(uCells):
            self.mines.update(uCells)

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        return self.mines

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        return self.safes

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if (cell not in self.cells or cell in self.mines):
            return
        self.mines.add(cell)
        self.check_known_cells()

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if (cell not in self.cells or cell in self.safes):
            return
        self.safes.add(cell)
        self.check_known_cells()

class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        if cell in self.mines:
            return
        print(f"mine {cell}")
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        if cell in self.safes:
            return
        print(f"safe {cell}")
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        self.moves_made.add(cell)

        self.mark_safe(cell)
        
        cells = []
        i,j = cell
        for row in range(i-1, i+2):
            if row < 0 or row > self.height-1:
                continue
            for col in range(j-1, j+2):
                if col < 0 or col > self.width - 1 or (row, col) in self.moves_made.union(self.safes):
                    continue
                cells.append((row, col))
        self.knowledge.append(Sentence(cells, count))

        for k in self.knowledge:
            for s in k.known_safes():
                self.mark_safe(s)
            for m in k.known_mines():
                self.mark_mine(m)

        if len(self.knowledge) > 1:
            for iK in range(0, len(self.knowledge)):
                for jK in range(0, len(self.knowledge)):
                    if (iK == jK):
                        continue
                    iCells, iCount = self.knowledge[iK].current_unknown_data()
                    jCells, jCount = self.knowledge[jK].current_unknown_data()
                    if iCells.issubset(jCells):
                        newCells = jCells.difference(iCells)
                        newCount = jCount - iCount
                        if not newCells:
                            continue
                        newSentence = Sentence(newCells, newCount)
                        if (newSentence in self.knowledge):
                            continue
                        for s in newSentence.known_safes():
                            self.mark_safe(s)
                        for m in newSentence.known_mines():
                            self.mark_mine(m)
                        self.knowledge.append(newSentence)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for safe in self.safes:
            if safe not in self.moves_made:
                return safe
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        i = 0
        j = -1
        cell = (random.randint(0,self.height-1), random.randint(0,self.width-1))
        while (cell in self.mines.union(self.moves_made)):
            if j == self.width-1:
                i += 1
                j = -1
            j+=1
            if (i == self.height-1 and j == self.width-1):
                return None
            cell = (i, j)
        return cell
