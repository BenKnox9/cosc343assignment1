__author__ = "<your name>"
__organization__ = "COSC343/AIML402, University of Otago"
__email__ = "<your e-mail>"

import itertools
import numpy as np
import random


class MastermindAgent():
    """
              A class that encapsulates the code dictating the
              behaviour of the agent playing the game of Mastermind.

              ...

              Attributes
              ----------
              code_length: int
                  the length of the code to guess
              colours : list of char
                  a list of colours represented as characters
              num_guesses : int
                  the max. number of guesses per game

              Methods
              -------
              AgentFunction(percepts)
                  Returns the next guess of the colours on the board
              """

    def __init__(self, code_length,  colours, num_guesses):
        """
        :param code_length: the length of the code to guess
        :param colours: list of letter representing colours used to play
        :param num_guesses: the max. number of guesses per game
        """

        self.code_length = code_length
        self.colours = colours
        self.num_guesses = num_guesses
        self.all_possible_codes = self.get_all_codes()

    def get_all_codes(self):
        return [''.join(code) for code in itertools.product(self.colours, repeat=self.code_length)]

    def AgentFunction(self, percepts):
        """Returns the next board guess given state of the game in percepts

              :param percepts: a tuple of four items: guess_counter, last_guess, in_place, in_colour

                       , where

                       guess_counter - is an integer indicating how many guesses have been made, starting with 0 for
                                       initial guess;

                       last_guess - is a num_rows x num_cols structure with the copy of the previous guess

                       in_place - is the number of character in the last guess of correct colour and position

                       in_colour - is the number of characters in the last guess of correct colour but not in the
                                   correct position

              :return: list of chars - a list of code_length chars constituting the next guess
              """

        guess_counter, last_guess, in_place, in_color = percepts

        # Ignore the first guess (no information provided)
        if guess_counter == 0:
            initial_guess = []
            idxI = 0
            for i in range(1, self.code_length // 2 + 1):
                initial_guess.extend([self.colours[i - 1]] * 2)
                idxI = i

        # If self.code_length is odd, add an extra element of the last color
            if self.code_length % 2 != 0:
                initial_guess.append(self.colours[idxI])

            return initial_guess
        # Update the set of possible codes based on the hint feedback
        possible_codes = self.filter_codes(
            last_guess, in_place, in_color)

        # Generate the next guess using Knuth's algorithm
        # next_guess = self.knuth_algorithm()

        # return next_guess
        if possible_codes:
            return list(random.choice(possible_codes))
        else:
            return list(random.choice(self.all_possible_codes))
        # Return the next guess from the filtered set of possible codes
        # if possible_codes:
        #     return list(random.choice(possible_codes))
        # else:
        #     return list(random.choice(self.all_possible_codes))
        # # Extract different parts of percepts.
        # guess_counter, last_guess, in_place, in_colour = percepts

        # # Create an list of colour caracters.   Currently all the guesses are the first colour,
        # # 'B' - probably good idea to replace this logic with a better guess
        # actions = [self.colours[0]]*self.code_length

        # # Return a random guess
        # return actions

    """ TODO: remove all code combinations which do not match the previous guess
    https://github.com/NathanDuran/Mastermind-Five-Guess-Algorithm """

    def filter_codes(self, last_guess, in_place, in_color):
        possible_codes = []
        for code in self.all_possible_codes:
            count_in_place = 0
            count_in_color = 0
            for i in range(self.code_length):
                if last_guess[i] == code[i]:
                    count_in_place += 1
                elif last_guess[i] in code:
                    count_in_color += 1
            if count_in_place == in_place and count_in_color == in_color:
                possible_codes.append(code)
        return possible_codes
