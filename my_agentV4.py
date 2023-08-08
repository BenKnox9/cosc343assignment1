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
        self.next_guesses_cache = {}
        self.all_guess_evals = {}

    def get_all_codes(self):
        """Returns a list of all codes
              :return: list of all codes
              """
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
            return self.initialGuess()

        possible_codes = self.filter_codes(percepts)

        # At this point the last guess will always be the same, so minimax method results can be cached

        possible_guesses = self.minimax(possible_codes)

        return self.chooseNextGuess(possible_guesses, possible_codes)

    def initialGuess(self):
        """Returns an initial guess based on the code_length and available colors.
            The initial guess will repeat each available color twice, and if code_length
            is greater than the number of colors, it will append the last available color to the repeated pattern.

                :return: Initial guess
            """
        initial_guess = []
        idxI = 0
        num_colors = len(self.colours)

        # Initial code will be two of each colour until code_length is reached, or exceeds num_colours
        for i in range(1, min(self.code_length // 2 + 1, num_colors + 1)):
            initial_guess.extend([self.colours[i - 1]] * 2)
            idxI = i

        # If code_length is odd, add an extra element of the last color
        if self.code_length % 2 != 0 and num_colors > 0:
            if idxI < num_colors:
                initial_guess.append(self.colours[idxI])
            else:
                initial_guess.append(self.colours[num_colors - 1])

        # If code_length is greater than the number of colors, append the last available color
        while len(initial_guess) < self.code_length and num_colors > 0:
            initial_guess.append(self.colours[num_colors - 1])

        return initial_guess

    def filter_codes(self, percepts):
        """Returns a list of codes, excluding ones which were impossible based on the feedback given for the previous guess
              :param percepts: a tuple of four items: guess_counter, last_guess, in_place, in_colour
              :return: list of possible codes
              """
        guess_counter, last_guess, in_place, in_color = percepts

        if guess_counter == 1:
            self.filtered_codes = self.all_possible_codes[:]

       # A temporary list to store codes that match the hints
        temp_filtered_codes = []

        # Compare the feedback received on the previous guess against the feedback of every code evaluated with that previous guess
        # remove all codes who's feedback does not match
        for code in self.filtered_codes:
            guess_in_place, guess_in_colour = self.eval_guess(
                list(code), last_guess)
            if guess_in_place == in_place and guess_in_colour == in_color and code != last_guess:
                temp_filtered_codes.append(code)

        # Update the filtered_codes attribute to the temporary list
        self.filtered_codes = temp_filtered_codes

        return self.filtered_codes

    def eval_guess(self, guess, target):
        """Returns number of pegs in place and number of pegs in colour
              :param guess: code which has been guessed
                    target: code which the guess is being measured against

              :return: in_place: number of items in the guess which were in place
                      in_colour: number of items in the guess which were the right colour, not including ones which were in_place
              """
        in_place = 0
        in_colour = 0
        guess_remaining = []
        target_remaining = []

        # Check for in_place
        for i in range(self.code_length):
            if guess[i] == target[i]:
                in_place += 1
            else:
                guess_remaining.append(guess[i])
                target_remaining.append(target[i])

        # Check for in_colour
        for color in guess_remaining:
            if color in target_remaining:
                in_colour += 1
                target_remaining.remove(color)

        return in_place, in_colour

    def chooseNextGuess(self, possible_guesses, possible_codes):
        """Returns a code chosen at random from the list of possible codes, excluding ones which were impossible based on the feedback given for the previous guess
              :param possible_guesses: a list of codes which are possible guesses returned from the filter_codes method
                       possible_codes: a list of codes which will be most effective based on the feedback previously received
              :return: The code chosen for the next guess
              """
        print("length of possible codes: ", len(possible_codes))
        print("length of possible guesses: ", len(possible_guesses))
        # print("Possible codes: ", possible_codes)
        # print("Possible guesses: ", possible_guesses)

        # Try and choose a code which is both a possible code, and has been recognised as a good guess
        for i in possible_guesses:
            guess = i
            if guess in possible_codes:
                return list(guess)

        if possible_guesses:
            return list(possible_guesses[0])
        if possible_codes:
            return list(possible_codes[0])
        return list(random.choice(self.all_possible_codes))

    def minimax(self, possible_codes):
        """Returns a list of codes which could be potential next guesses based on the minimax technique
                :param possible_codes: a list of codes which are possible guesses returned from the filter_codes method
                :return: list of possible codes
            """
        scoreCount = {}
        score = {}

        nextGuesses = []

        # Evaluate every code against a target of all of the codes which are possible answers.
        for i in self.all_possible_codes:
            for j in possible_codes:
                pegScore = self.eval_guess(list(i), list(j))

                # For every set of feedback already stored as a key in the scoreCount dictionary, increment its value.
                pegScore_str = str(pegScore)
                if pegScore_str in scoreCount:
                    scoreCount[pegScore_str] += 1
                # Otherwise add that feedback as a key, with a value of 1
                else:
                    scoreCount[pegScore_str] = 1

            max_value = max(scoreCount.values())  # the score of each code i
            score[i] = max_value
            scoreCount.clear()

        # Choose the group with the smallest max value
        min_value = min(score.values())

        for key, value in score.items():
            if value == min_value:
                nextGuesses.append(key)
        return nextGuesses

    def minimax_cached(self, possible_codes, in_place, in_colour):
        """Returns a list of guesses which will be most effective based on the feedback previously received
              :param possible_codes: The list of codes which are possible based on the feedback of the previous guesses
                           in_place: number of items in the guess which were in place
                          in_colour: number of items in the guess which were the right colour, not including ones which were in_place
              :return: list of next guesses
              """
        feedback_str = str(in_place) + ", " + \
            str(in_colour)  # Used as the key in the dictionary

        # If minimax has already been run for this set of feedback, return the cached dictionary
        if feedback_str in self.next_guesses_cache:
            return self.next_guesses_cache[feedback_str]

        # Else compute next_guesses and save it in the next_guesses_cache dictionary
        else:
            next_guesses = self.minimax(possible_codes)
            self.next_guesses_cache[feedback_str] = next_guesses
            return next_guesses

    def eval_guess_cached(self, guess, target):
        """
        This method would take up around 16GB of memory to cache every evaluation"""
        # Used as the key in the dictionary
        evalString = str(guess) + str(target)

        # If this evaluation has already been computed, return the cached result
        if evalString in self.all_guess_evals:
            return self.all_guess_evals[evalString]

        # Else compute the result and save it in the all_guess_evals dictionary
        else:
            score = self.eval_guess(guess, target)
            self.all_guess_evals[evalString] = score
            return score


"""
References:
https://github.com/NathanDuran/Mastermind-Five-Guess-Algorithm 
https://betterprogramming.pub/solving-mastermind-641411708d01
chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/http://www.cs.uni.edu/~wallingf/teaching/cs3530/resources/knuth-mastermind.pdf

"""
