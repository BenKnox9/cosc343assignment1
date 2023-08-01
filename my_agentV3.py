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

        possible_codes = self.filter_codes(percepts)

        possible_guesses = self.minimax(possible_codes)

        return self.chooseNextGuess(possible_guesses, possible_codes)

    def filter_codes(self, percepts):
        """Returns a list of codes, excluding ones which were impossible based on the feedback given for the previous guess
              :param percepts: a tuple of four items: guess_counter, last_guess, in_place, in_colour
              :return: list of possible codes
              """
        guess_counter, last_guess, in_place, in_color = percepts
       # A temporary list to store codes that match the hints
        if guess_counter == 1:
            self.filtered_codes = self.all_possible_codes[:]

        temp_filtered_codes = []

        for code in self.filtered_codes:
            guess_in_place, guess_in_colour = self.eval_guess(
                list(code), last_guess)
            if guess_in_place == in_place and guess_in_colour == in_color and code != last_guess:
                temp_filtered_codes.append(code)

        # Update the filtered_codes attribute to the temporary list
        self.filtered_codes = temp_filtered_codes

        return self.filtered_codes

    def eval_guess(self, guess, target):
        black_pegs = 0
        white_pegs = 0
        guess_remaining = []
        target_remaining = []

        for i in range(self.code_length):
            if guess[i] == target[i]:
                black_pegs += 1
            else:
                guess_remaining.append(guess[i])
                target_remaining.append(target[i])

        for color in guess_remaining:
            if color in target_remaining:
                white_pegs += 1
                target_remaining.remove(color)

        return black_pegs, white_pegs

    def chooseNextGuess(self, possible_guesses, possible_codes):
        """Returns a code chosen at random from the list of possible codes, excluding ones which were impossible based on the feedback given for the previous guess
              :param percepts: a tuple of four items: guess_counter, last_guess, in_place, in_colour
              :return: The code chosen for the next guess
              """
        print("length of possible codes: ", len(possible_codes))
        # print(possible_codes)
        print("length of possible guesses: ", len(possible_guesses))
        # print(possible_guesses, '\n', '\n')

        for i in possible_codes:
            guess = i
            if guess in possible_guesses:
                return list(guess)

        # if len(possible_guesses) > len(possible_codes):
        #     return list(random.choice(possible_codes))

        if possible_guesses:
            return list(random.choice(possible_guesses))
        else:
            return list(random.choice(self.all_possible_codes))

    ''' V2 '''
    # def minimax(self, possible_guesses):
    #     all_possible_codes = self.get_all_codes()
    #     scores = {}

    #     for guess in possible_guesses:
    #         guess_score = 0
    #         for code in all_possible_codes:
    #             pegScore = self.eval_guess(list(guess), list(code))
    #             pegScore_str = str(pegScore)
    #             scores[guess] = scores.get(guess, {})
    #             scores[guess][pegScore_str] = scores[guess].get(
    #                 pegScore_str, 0) + 1

    #         max_value = max(scores[guess].values())
    #         guess_score = max_value
    #         scores[guess] = guess_score

    #     min_score = min(scores.values())
    #     nextGuesses = [guess for guess,
    #                    score in scores.items() if score == min_score]

    #     return nextGuesses
    ''' ORIGINAL '''

    def minimax(self, possible_guesses):
        """Returns a list of codes which could be potential next guesses based on the minimax technique
            :param possible_guesses: a list of codes which are possible guesses returned from the filter_codes method
            :return: list of possible codes
            """
        scoreCount = {}
        score = {}

        nextGuesses = []

        for i in possible_guesses:
            for j in self.all_possible_codes:
                # JUST ADDED list() around i and j
                pegScore = self.eval_guess(list(i), list(j))
                # print(" i:  ", i, '\n', "j:  ", j)
                # print("pegscore:  ", pegScore)
                pegScore_str = str(pegScore)
                if pegScore_str in scoreCount:
                    scoreCount[pegScore_str] += 1
                else:
                    scoreCount[pegScore_str] = 1

            max_value = max(scoreCount.values())  # the score of each code i
            score[i] = max_value
            scoreCount.clear()

        min_value = min(score.values())

        for key, value in score.items():
            if value == min_value:
                nextGuesses.append(key)
        return nextGuesses


"""
References:
https://github.com/NathanDuran/Mastermind-Five-Guess-Algorithm 
https://betterprogramming.pub/solving-mastermind-641411708d01
chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/http://www.cs.uni.edu/~wallingf/teaching/cs3530/resources/knuth-mastermind.pdf



"""
