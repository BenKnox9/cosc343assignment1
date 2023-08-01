__author__ = "Ben Knox"
__organization__ = "COSC343/AIML402, University of Otago"
__email__ = "knobe957@student.otago.ac.nz"

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
        self.filtered_codes = self.all_possible_codes[:]
        self.knuth_codes = []

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

        # First guess is always 2 lots of each colour next to each other
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

        self.knuth_codes.append(last_guess)
        possible_codes = self.filter_codes(percepts)
        new_guess = self.mini_max(self.knuth_codes, possible_codes)
        print("length of possible codes: ", len(possible_codes))

        if new_guess:
            return list(random.choice(new_guess))
        elif possible_codes:
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

    """
    Version 1, works but not too well"""
    # def filter_codes(self, percepts):
    #     print("FILTER CODES")
    #     removed_codes = set()
    #     filtered_codes = []
    #     guess_counter, last_guess, in_place, in_color = percepts

    #     for code in self.all_possible_codes:
    #         if code in removed_codes:  # Skip codes that have already been removed
    #             continue

    #         guess_in_place, guess_in_colour = self.eval_guess(
    #             list(code), last_guess)
    #         if guess_in_place == in_place and guess_in_colour == in_color:
    #             filtered_codes.append(code)
    #         else:
    #             removed_codes.add(code)

    #     return filtered_codes
    """Version 2, works very well but only for first round"""
    # def filter_codes(self, percepts):
    #     guess_counter, last_guess, in_place, in_color = percepts
    #     # A temporary list to store codes that match the hints
    #     temp_filtered_codes = []

    #     for code in self.filtered_codes:
    #         guess_in_place, guess_in_colour = self.eval_guess(
    #             list(code), last_guess)
    #         if guess_in_place == in_place and guess_in_colour == in_color:
    #             temp_filtered_codes.append(code)

    #     # Update the filtered_codes attribute to the temporary list
    #     self.filtered_codes = temp_filtered_codes

    #     return self.filtered_codes
    """Version 3, works"""

    def filter_codes(self, percepts):
        guess_counter, last_guess, in_place, in_color = percepts
        # A temporary list to store codes that match the hints
        if guess_counter == 1:
            self.filtered_codes = self.all_possible_codes[:]

        temp_filtered_codes = []

        for code in self.filtered_codes:
            guess_in_place, guess_in_colour = self.eval_guess(
                list(code), last_guess)
            if guess_in_place == in_place and guess_in_colour == in_color:
                temp_filtered_codes.append(code)

        # Update the filtered_codes attribute to the temporary list
        self.filtered_codes = temp_filtered_codes

        return self.filtered_codes

    def eval_guess(self, guess, target):
        """ 
            STOLEN FROM mastermind.py, THANK YOU LECH!

            Evaluates a guess against a target
            :param guess: a R x C numpy array of valid colour characters that constitutes a guess
                    target: a R x C numpy array of valid colour characters that constitutes target solution
            :return: a tuple of 4 vectors:
                    R-dimensional vector that gives the number of correct colours in place in each row of the
                                    guess against the target
                    R-dimensional vector that gives the number of correct colours out of place in each row of the
                                    guess against the target
                    C-dimensional vector that gives the number of correct colours in place in each column of the
                                    guess against the target
                    C-dimensional vector that gives the number of correct colours out of place in each column of the
                                    guess against the target

          """
        guess = np.reshape(guess, (-1))
        target = np.reshape(target, (-1))

        I = np.where(guess == target)[0]
        in_place = len(I)
        I = np.where(guess != target)[0]
        state = np.zeros(np.shape(target))

        in_colour = 0
        for i in I:
            a = target[i]
            for j in I:
                if state[j] != 0:
                    continue

                b = guess[j]

                if a == b:
                    in_colour += 1
                    state[j] = -1
                    break

        return in_place, in_colour

    def mini_max(self, knuth_codes, possible_codes):
        scores = {}
        print(len(possible_codes))
        for code in possible_codes:
            times_found = {}
            for code_to_crack in knuth_codes:
                feedback = self.eval_guess(code_to_crack, code)
                feedback_str = str(feedback)
                times_found[feedback_str] = times_found.get(
                    feedback_str, 0) + 1
            maximum = max(times_found.values())
            scores[code] = maximum
            print("scores")

        minimum = min(scores.values())
        guess_codes = [
            code for code in possible_codes if scores[code] == minimum]

        return guess_codes


"""
References:
https://github.com/NathanDuran/Mastermind-Five-Guess-Algorithm 
https://betterprogramming.pub/solving-mastermind-641411708d01
chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/http://www.cs.uni.edu/~wallingf/teaching/cs3530/resources/knuth-mastermind.pdf



"""
