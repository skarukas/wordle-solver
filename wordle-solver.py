import argparse
import time
import sys
import random


INVALID_WORD = "INVALID_WORD"
WIN = "WIN"
NO_MORE_TRIES = "NO_MORE_TRIES"
special_responses = [INVALID_WORD, WIN, NO_MORE_TRIES]

GREEN = "G"
YELLOW = "Y"
GREY = "X"
letter_responses = [GREEN, YELLOW, GREY]

STRATEGY_RANDOM = 'random'
STRATEGY_EXPECTIMAX = 'expectimax'
STRATEGY_FREQUENCY= 'frequency'
strategies = [STRATEGY_RANDOM, STRATEGY_EXPECTIMAX, STRATEGY_FREQUENCY]

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str, default="norvig_count_1w.txt", help="The corpus from which the words are drawn. Each line may either be in the format 'word1' or 'word1 freq1'.")
    parser.add_argument("--strategy", type=str, default=STRATEGY_EXPECTIMAX, choices=strategies, help="How the bot should decide the guessed word")
    parser.add_argument("--length", type=int, default=5, help="The length of the word")
    parser.add_argument("--tries", type=int, default=6, help="The number of tries we have to guess the word")
    args = parser.parse_args()
    return vars(args)


class Corpus:
    def __init__(self, file):
        self.total_freq = 0
        self.word_freqs = {}

        for line in file:
            split = line.split(" ")
            if len(split) == 1:
                split = line.split("\t")
            split = [*filter(lambda w: w != "", split)]
            word = split[0].upper()
            if len(word) == config['length']:
                freq = float(split[1]) if len(split) == 2 else 1
                self.word_freqs[word] = freq
                self.total_freq += freq

    def remove(self, word):
        word = word.upper()
        print(word)
        freq = self.word_freqs.pop(word, 0)
        print(word in self.word_freqs.keys())
        self.total_freq -= freq

    def get_probability(self, word):
        word = word.upper()
        return self.word_freqs.get(word, 0) / self.total_freq

    def words(self):
        return [*self.word_freqs.keys()]

    def __contains__(self, word):
        return word.upper() in self.word_freqs.keys()


def letter_filter(letter, possible_posns):
    def inner(word):
        """
        Returns true only if the letter can be found 
            in any of the possible posns in the word
        """
        for p in possible_posns:
            if word[p] == letter:
                return True
        return False

    return inner


def filter_words(words, green_letters: dict, yellow_letters: dict, grey_letters: dict):
    """
    Each dict is position: letter
        green = letter is in the correct position
        yellow = letter is in the incorrect position but exists in the word
        grey = letter does not exist in the word
    """

    # green filter
    for posn, letter in green_letters.items():
        possible_posns = [posn]
        words = [*filter(letter_filter(letter, possible_posns), words)]

    # yellow filter
    for posn, letter in yellow_letters.items():
        all_posns = set(range(config['length']))
        green_posns = set(green_letters.keys())
        possible_posns = (all_posns - green_posns) - set([posn])
        words = [*filter(lambda w: w[posn] != letter, words)]
        words = [*filter(letter_filter(letter, possible_posns), words)]
    
    # grey filter
    #  note: has to come last because green letters show up grey if repeated
    for posn, letter in grey_letters.items():
        not_contains = lambda w: letter not in w
        words = [*filter(not_contains, words)]

    return words


def cope():
    print("Wow...I'm an idiot.")
    time.sleep(1)
    print("...")
    time.sleep(2)
    print("a stupid idiot computer.")
    time.sleep(2)
    print("...")
    time.sleep(2)
    print("so...")
    time.sleep(2)
    print("...")
    true_word = input("what was the real word? I need to know\n")
    time.sleep(1)

    if true_word in corpus:
        print(f"'{true_word.upper()}'??? How could I be so stupid??")
    else:
        print(f"'{true_word.upper()}'??? I didn't even know that was a word...")
    sys.exit(0)


def gloat():
    print("I knew it! I'm the smartest")
    sys.exit(0)


def invalid_word():
    print(f"{curr_guess} isn't a word? Why is it in my dictionary, then?")
    curr_words.remove(curr_guess)
    print("This is embarassing, let me try again.")


def decode_response(chars):
    green_letters = {}
    yellow_letters = {}
    grey_letters = {}

    for i, c in enumerate(chars):
        if c == GREEN:
            green_letters[i] = curr_guess[i]
        elif c == YELLOW:
            yellow_letters[i] = curr_guess[i]
        else:
            grey_letters[i] = curr_guess[i]

    return {
        "green_letters": green_letters,
        "yellow_letters": yellow_letters,
        "grey_letters": grey_letters
    }


def get_response():
    global curr_guess
    user_input = input(f"""Enter the response.
Either:
- Use the format {GREEN} {GREY} {GREEN} {GREY} {YELLOW}, where {GREEN}=green, {YELLOW}=yellow, and {GREY}=grey
- Or enter one of the following: {", ".join(special_responses)}
- Or, if you ignored my suggestion, type the word you guessed, then I'll ask again
- If you want another guess, press enter. No promises that it's not the same
""")
    user_input = user_input.upper().rstrip()

    if user_input == WIN:
        gloat()
    elif user_input == NO_MORE_TRIES:
        cope()
    elif user_input == INVALID_WORD:
        invalid_word()
        # return previous response again
        return curr_response
    elif user_input == "":
        # return previous response again
        return curr_response
    elif len(user_input) == config['length']:
        curr_guess = user_input
        print(f"You ignored me and guessed {curr_guess}. How'd that turn out for you?")
        return get_response()

    chars = user_input.split(" ")
    if len(chars) != config['length'] or not all(map(letter_responses.__contains__, chars)):
        print("I don't understand this response. Make sure it's in the right format.")
        return get_response()
    else:
        return decode_response(chars)


def guess_word(words):
    """
    Make a guess as to what word is the solution.
    """
    if config['strategy'] == STRATEGY_RANDOM:
        idx = random.randint(0, len(words)-1)
        best_word = words[idx]
    else:
        best_word = max(words, key=lambda w: corpus.get_probability(w))
    return best_word


if __name__ == "__main__":
    config = parse_args()
    with open(config['file'], "r") as f:
        print(f"Reading in {config['file']}...")
        corpus = Corpus(f)

    curr_response = {
        "green_letters": {},
        "yellow_letters": {},
        "grey_letters": {}
    }
    curr_words = corpus.words()
    while True:
        curr_guess = guess_word(curr_words).upper()
        print(f"My guess is {curr_guess.upper()}.")
        curr_response = get_response()
        curr_words = filter_words(curr_words, **curr_response)