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
        self.mines = set()
        self.safe = set()

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if self.count == len(self.cells) and self.count != 0:
            return self.cells
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.mines.add(cell)
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.safe.add(cell)
            self.cells.remove(cell)


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
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
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
        # Find neighboring cells
        neighbors = set()
        for i in range(cell[0]-1, cell[0]+2):
            for j in range(cell[1]-1, cell[1]+2):
                if (i, j) == cell:
                    continue
                if i in range(self.height) and j in range(self.width):
                    if (i, j) not in self.safes and (i, j) not in self.mines:
                            neighbors.add((i, j))
                    elif (i, j) in self.mines:
                        count -= 1
        if count == 0:
            for nei in neighbors:
                self.mark_safe(nei)
        if count == len(neighbors) and count > 0:
            for nei in neighbors:
                self.mark_mine(nei)
        # add new sentence to the knowledge
        new_sentence = Sentence(neighbors, count)
        self.knowledge.append(new_sentence)
    
        """
        Updates the AI's knowledge base, makes new inference marking additional 
        cells as safe or as mines if possible
        """
        
        made_inference = True
        while made_inference:
            made_inference = False
            
            for sentence in self.knowledge:
                if sentence.known_mines():
                    for cell in sentence.known_mines().copy():
                        self.mark_mine(cell)
                if sentence.known_safes():
                    for cell in sentence.known_safes().copy():
                        self.mark_safe(cell)

            newSentences = []
            for sentence1 in self.knowledge:
                for sentence2 in self.knowledge:
                    if sentence1 != sentence2 and sentence1.cells.issubset(sentence2.cells):
                        inferred_cells = sentence2.cells - sentence1.cells
                        inferred_count = sentence2.count - sentence1.count
                        inferred_sentence = Sentence(inferred_cells, inferred_count)    
                        if inferred_sentence not in self.knowledge and inferred_sentence not in newSentences:
                            newSentences.append(inferred_sentence)   
                            made_inference = True       
            self.knowledge.extend(newSentences)

        # made_inference = True
        # while made_inference:
        #     made_inference = False

        #     # determines cells known to be safe or mines
        #     all_safes, all_mines = set(), set()
        #     for sentence in self.knowledge:
        #         all_safes.update(sentence.known_safes())
        #         all_mines.update(sentence.known_mines())
            
        #     if all_safes:
        #         for cell in all_safes:
        #             self.mark_safe(cell)
        #     if all_mines:
        #         for cell in all_mines:
        #             self.mark_mine(cell)
            
        #     # remove empty sentences
        #     self.knowledge = [sentence for sentence in self.knowledge if len(sentence.cells) > 0]
            
        #     # infer new sentence from existing knowledge
        #     new_sentences = []
        #     for sentence1 in self.knowledge:
        #         for sentence2 in self.knowledge:
        #             if sentence1 != sentence2 and sentence1.cells.issubset(sentence2.cells):
        #                 inferred_cells = sentence2.cells - sentence1.cells
        #                 inferred_count = sentence2.count - sentence1.count
        #                 if inferred_count == 0:
        #                     for cell in inferred_cells:
        #                         self.mark_safe(cell)
        #                 if inferred_count == len(inferred_cells) and inferred_count > 0:
        #                     for cell in inferred_cells:
        #                         self.mark_mine(cell)
        #                 inferred_sentence = Sentence(inferred_cells, inferred_count)
        #                 if inferred_sentence not in self.knowledge and inferred_sentence not in new_sentences:
        #                     new_sentences.append(inferred_sentence)
            
        #     if new_sentences:
        #         made_inference = True
        #         self.knowledge.extend(new_sentences)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        all_cells = set(itertools.product(range(self.height), range(self.width)))
        available_moves = all_cells - self.moves_made - self.mines
        if available_moves:
            return random.choice(list(available_moves))
        return None