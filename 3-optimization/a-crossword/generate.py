import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox(
                            (0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var, words in list(self.domains.items()):
            self.domains[var] = {
                word for word in words if len(word) == var.length}

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        if not self.crossword.overlaps[x, y]:
            return revised

        x_idx, y_idx = self.crossword.overlaps[x, y]

        for x_word in list(self.domains[x]):
            if len([y_word for y_word in self.domains[y] if y_word[y_idx] == x_word[x_idx]]) == 0:
                self.domains[x].remove(x_word)
                revised = True
        return revised

    def remove_duplicateds(self):
        """
        Remove all duplicated values. 
        If a domain contains only one word, 
        then this word couldn't be used for another domain.

        Return True if changes were made.
        Return False if not was changed.
        """
        duplicated_removed = False
        for var, words in list(self.domains.items()):
            if len(words) == 1:
                for v2, w2 in list(self.domains.items()):
                    if v2 is not var and list(words)[0] in w2:
                        self.domains[v2].remove(list(words)[0])
                        duplicated_removed = True
        return duplicated_removed

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            arcs = [(var, neighbor)
                    for var in self.domains for neighbor in self.crossword.neighbors(var)]

        while arcs:
            x, y = arcs.pop()
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for z in self.crossword.neighbors(x):
                    if z is not y:
                        arcs.append((z, x))
            # if not arcs:
            #     if self.remove_duplicateds():
            #         arcs = [(var, neighbor)
            #                 for var in self.domains for neighbor in self.crossword.neighbors(var)]

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return self.consistent(assignment) and len(assignment) == len(self.domains)

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        assignment_list = list(assignment.items())
        if not assignment_list:
            return True
        last_var, last_word = assignment_list[-1]
        for var, word in assignment_list[:-1]:
            if len(word) != var.length or last_word is word:
                return False
            if not self.crossword.overlaps[last_var, var]:
                continue
            l_idx, v_idx = self.crossword.overlaps[last_var, var]
            if last_word[l_idx] != word[v_idx]:
                return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        if not var:
            return []
        neighbors = self.crossword.neighbors(var)
        words = self.domains[var]
        word_count = {word: 0 for word in words}
        for n in neighbors:
            for word in self.domains[n].intersection(words):
                word_count[word] += 1
        return sorted(word_count.keys(), key=lambda w: word_count[w])

    def get_from_neighbors(self, variable, assignment):
        '''
        Retrieve neighbors from a variable to fill next word.
        '''
        neighbors = self.crossword.neighbors(variable)
        temp_domains = dict()
        for n in neighbors:
            temp_domains[n] = self.domains[n]
        grouped_domains = self.group_by_min_remain(temp_domains)
        for l, domains in grouped_domains:
            sorted_domains = self.sort_by_highest_neighbors(domains)
            for v in [i for i, d in sorted_domains if i not in assignment.keys()]:
                return v
        return None

    def group_by_min_remain(self, domains):
        grouped_by_min_remain_val = dict()
        for item in domains.items():
            l = len(item[1])
            if l not in grouped_by_min_remain_val:
                grouped_by_min_remain_val[l] = [item]
            else:
                grouped_by_min_remain_val[l].append(item)
        return sorted(
            grouped_by_min_remain_val.items(), key=lambda g: g[0])

    def sort_by_highest_neighbors(self, domains):
        return sorted(domains, key=lambda d: len(self.crossword.neighbors(d[0])), reverse=True)

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        if assignment:
            for i in [(idx * -1) for idx in range(1, len(list(assignment))+1)]:
                last_item = list(assignment)[i]
                result = self.get_from_neighbors(last_item, assignment)
                if result:
                    return result

        grouped_by_min_remain_val = self.group_by_min_remain(self.domains)
        for l, domains in grouped_by_min_remain_val:
            # sort all domains by highest neighbors.
            domains = self.sort_by_highest_neighbors(domains)
            # return variable that is not already assigned.
            for domain in domains:
                if domain[0] not in list(assignment.keys()):
                    return domain[0]
        return None

    def inferences(self, assignment):
        # TODO: apply know values to assignment.
        return dict()

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        inferences = dict()
        for value in self.order_domain_values(var, assignment):
            new_assignment = assignment.copy()
            new_assignment[var] = value
            if self.consistent(new_assignment):
                assignment[var] = value
                inferences = self.inferences(assignment)
                if inferences:
                    assignment.update(inferences)
                result = self.backtrack(new_assignment)
                if result is not None:
                    return result
            assignment = {key: value for key, value in assignment.items(
            ) if key is not var and key not in inferences.keys()}
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
