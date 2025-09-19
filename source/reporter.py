import numpy as np
from tqdm import tqdm
import os
import json

class Reporter():

    def __init__(self, args):
        self.args = args
        self.round_guesses = []
        self.current_guesses = []

        self.reporting_method_dict = {
            'attempts': self.attempts,
            'completion%': self.completion,
            'wheel': self.wheel,
            'letter_distribution': self.letter_distribution,
        }

        self.reporting_method = []
        for method in args['reporting']['method']:
            if method not in self.reporting_method_dict:
                 tqdm.write(f"Invalid reporting method; choose ({f', '.join(list(self.reporting_method_dict.keys()))})")
            
            else: self.reporting_method.append(method)

        if len(self.reporting_method) == 0:
            raise ValueError("No valid reporting method selected; choose (attempts, completion%)")
        
        self.log_file = os.path.join(args['reporting']['root'], "report.jsonl")

        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                f.write("")

        else:
            with open(self.log_file, 'r') as f:
                round = []
                for line in f:
                    if line.strip() != "": 
                        round.append(json.loads(line.strip()))
                    else:
                        self.round_guesses.append(round)
                        round = []

    def new_round(self):
        self.current_guesses = []

    def log(self, letter, masked_sentence, guess, solution, budget="/", wheel_reward="/", letter_occurences="/"):
        self.current_guesses.append({"letter": letter, "masked": masked_sentence, "guess": guess, "solution": solution, "budget": budget, "wheel_reward": wheel_reward, "letter_occurences": letter_occurences})
        with open(self.log_file, 'a') as out:
            jout = json.dumps({"letter": letter, "masked": masked_sentence, "guess": guess, "solution": solution, "budget": budget, "wheel_reward": wheel_reward, "letter_occurences": letter_occurences}) + '\n'
            out.write(jout)

    def round_end(self):
        self.round_guesses.append(self.current_guesses)

        with open(self.log_file, 'a') as out:          
            out.write("\n")


    def final_report(self):
        report = {}
        for method in self.reporting_method:
            report[method] = self.reporting_method_dict[method]()

        return report


    def attempts(self):
        attempts = []

        for round in self.round_guesses:
            attempts.append(len(round))
        print(len(attempts))

        if len(attempts) == 0:
            return {
                'mean': 0,
                'std': 0,
                '1st_quartile': 0,
                'median': 0,
                '3rd_quartile': 0,
            }
        return {
            'mean': f"{np.mean(attempts):.2f}",
            'std': f"{np.std(attempts):.2f}",
            '1st_quartile': f"{np.percentile(attempts, 25):.2f}",
            'median': f"{np.median(attempts):.2f}",
            '3rd_quartile': f"{np.percentile(attempts, 75):.2f}",
        }
    
    def completion(self):

        perc_completion = []
        for r in self.round_guesses:
            if r[-1]['guess'] != r[-1]['solution'] or r[-1]['letter'] == "INSUFFICENT BUDGET":
                continue
            perc_completion.append((1 - r[-1]["masked"].count("_") / len(r[-1]["masked"].replace(" ", ""))) * 100)

        if len(perc_completion) == 0:
            return {
                'mean': 0,
                'std': 0,
                '1st_quartile': 0,
                'median': 0,
                '3rd_quartile': 0,
            }

        return {
            'mean': f"{np.mean(perc_completion):.2f}",
            'std': f"{np.std(perc_completion):.2f}",
            '1st_quartile': f"{np.percentile(perc_completion, 25):.2f}",
            'median': f"{np.median(perc_completion):.2f}",
            '3rd_quartile': f"{np.percentile(perc_completion, 75):.2f}",
        }

    def wheel(self):
        lost_matches = 0
        right_guesses = 0
        right_completion_len = 0
        wrong_completion_len = 0
        insufficent_budget = 0
        instruction_error = 0
        round_limit_error = 0
        letter_not_in_sentence = 0
        vowel_not_allowed_error = 0
        consonant_not_allowed_error = 0
        guess_error = 0
        total = len(self.round_guesses)
        vowels_buyed = []
        budget_mean = []
        word_missmatch_guess = 0
        letter_missmatch_guess = 0
        nearly_right_guesses = 0 


    
        for r in self.round_guesses:
            if r[-1]['guess'] != r[-1]['solution']: 
                lost_matches += 1
                wrong_completion_len += len(r[-1]['solution'].replace(" ", ""))
                if r[-1]['letter'] == "INSUFFICENT BUDGET": 
                    insufficent_budget += 1
                elif r[-1]['letter'] == "ERROR": 
                    round_limit_error +=1
                elif r[-1]['letter'] == "INSTRUCTION ERROR":  
                    instruction_error += 1
                elif r[-1]['letter'] == "VOWEL NOT ALLOWED": 
                    vowel_not_allowed_error += 1
                elif r[-1]['letter'] == "CONSONANT NOT ALLOWED": 
                    consonant_not_allowed_error += 1
                elif r[-1]['letter_occurences'] == 0 and not self.args['no_letter_loss']: 
                    letter_not_in_sentence += 1
                else: 
                    guess_error += 1
                    local_word_missmatch = len(r[-1]['guess'].split(" ")) != len(r[-1]['solution'].split(" "))
                    if local_word_missmatch:
                        word_missmatch_guess += 1

                    
                    if len(r[-1]['guess'].replace(" ", "")) != len(r[-1]['solution'].replace(" ", "")):
                        letter_missmatch_guess += 1
                    if not local_word_missmatch and abs(len(r[-1]['guess'].replace(" ", "")) - len(r[-1]['solution'].replace(" ", ""))) <= 2:
                        nearly_right_guesses += 1
                continue

            if r[-1]['guess'] == r[-1]['solution']: 
                right_completion_len += len(r[-1]['solution'].replace(" ", ""))
                right_guesses += 1

                round_this_game = len(r)
                budget_this_game = 0
                vowels_this_game = 0
                for i in range(len(r)):
                    if r[i]['letter'] == "_": 
                        continue
                    if len(r[i]['letter']) > 1:
                        continue
                    if r[i]['letter'] in ["A", "E", "I", "O", "U"]:
                        vowels_this_game += 1

                    budget_this_game += r[i]['budget']
                vowels_buyed.append(vowels_this_game)
                budget_mean.append(budget_this_game/round_this_game)

    
        duplicated_letters = []


        for r in self.round_guesses:
            letters = [entry['letter'] for entry in r]
            letters.remove("_")
            letters = [letter for letter in letters if len(letter) == 1]

            letter_counts = {letter: letters.count(letter) for letter in set(letters)}

            for letter, count in letter_counts.items():
                letter_counts[letter] = count-1


            duplicated_letters_this_game = sum(count for count in letter_counts.values())

            duplicated_letters.append(duplicated_letters_this_game)




        if len(vowels_buyed) == 0:
            mean_vowels_buyed, std_vowels_buyed, first_quartile_vowels_buyed, median_vowels_buyed, third_quartile_vowels_buyed  = 0, 0, 0 , 0, 0
        else:
            mean_vowels_buyed = np.mean(vowels_buyed)
            std_vowels_buyed = np.std(vowels_buyed)
            first_quartile_vowels_buyed = np.percentile(vowels_buyed, 25)
            median_vowels_buyed = np.median(vowels_buyed)
            third_quartile_vowels_buyed = np.percentile(vowels_buyed, 75)

        if len(budget_mean) == 0:
            mean_budget, std_budget, first_quartile_budget, median_budget, third_quartile_budget = 0, 0, 0, 0, 0
        else:
            mean_budget = np.mean(budget_mean)
            std_budget = np.std(budget_mean)
            first_quartile_budget = np.percentile(budget_mean, 25)
            median_budget = np.median(budget_mean)
            third_quartile_budget = np.percentile(budget_mean, 75)

        if right_guesses == 0:
            right_guesses_len_metric = 0
            wrong_guesses_len_metric = wrong_completion_len/lost_matches
        else:
            right_guesses_len_metric = right_completion_len/right_guesses
            wrong_guesses_len_metric = wrong_completion_len/lost_matches


        return {
            '% lost matches': f"{lost_matches/total*100}",
            '% insufficent budget': f"{insufficent_budget/lost_matches*100:.2f}",
            '% round limit error': f"{round_limit_error/lost_matches*100:.2f}",
            '% win matches': f"{(total-lost_matches)/total*100}",
            'mean vowels buyed': f"{mean_vowels_buyed:.2f}",
            'std vowels buyed': f"{std_vowels_buyed:.2f}",
            '1st_quartile vowels buyed': f"{first_quartile_vowels_buyed:.2f}",
            'median vowels buyed': f"{median_vowels_buyed:.2f}",
            '3rd_quartile vowels buyed': f"{third_quartile_vowels_buyed:.2f}",
            'mean budget': f"{mean_budget:.2f}",
            'std budget': f"{std_budget:.2f}",
            '1st_quartile budget': f"{first_quartile_budget:.2f}",
            'median budget': f"{median_budget:.2f}",
            '3rd_quartile budget': f"{third_quartile_budget:.2f}",
            'mean duplicated letters': f"{np.mean(duplicated_letters):.2f}",
            'std duplicated letters': f"{np.std(duplicated_letters):.2f}",
            '% instruction_error': f"{instruction_error/lost_matches*100:.2f}",
            '% letter not in sentence': f"{letter_not_in_sentence/lost_matches*100:.2f}",
            '% vowel not allowed error': f"{vowel_not_allowed_error/lost_matches*100:.2f}",
            '% consonant not allowed error': f"{consonant_not_allowed_error/lost_matches*100:.2f}",
            '% guess error': f"{guess_error/lost_matches*100:.2f}",
            'right guesses length mean': f"{right_guesses_len_metric:.2f}",
            'wrong guesses length mean': f"{wrong_guesses_len_metric:.2f}",
        }
    
    def letter_distribution(self):
        letters = []
        letters_freq = {}
        for i, r in enumerate(self.round_guesses):
            if i == 0: continue
            letters = [entry['letter'] for entry in r]
            letters = [letter for letter in letters if len(letter) == 1]
            letters.remove("_")
            letters_freq[i] = letters


        letter_order = {}
        n_position = 3
        n_letters = 3
        for i in range(n_position):
            letter_order[i+1] = {}

        for element in letters_freq.items():
            n, letters = element
            for i, letter in enumerate(letters):
                if i > n_position-1:
                    break
                if letter in letter_order[i+1]:
                    letter_order[i+1][letter] += 1
                else: 
                    if len(letter_order[i+1]) > n_letters:
                        break
                    else:
                        letter_order[i+1][letter] = 1

        return {
            "letters_order": letter_order,
            "letters_freq": letters_freq
            }