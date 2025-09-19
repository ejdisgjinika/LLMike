import re
import reporter
import player
import prompt
from tqdm import tqdm

class Task():

    def __init__(self, expt_player: player.Player, exp_report: reporter.Reporter):
        
        self.player = expt_player
        self.reporter = exp_report


    def add_letter_to_masked_sentence(self, letter, masked_sentence, sentence):
        new_masked_sentence = ""
        
        occ = 0
        for i, c in enumerate(sentence):
            if c == letter: new_masked_sentence += c; occ += 1
            else: new_masked_sentence += masked_sentence[i]

        if occ == 0: presence = "not present"
        elif occ == 1: presence = "1 occurence"
        else: presence = f"{occ} occurences"

        if masked_sentence == new_masked_sentence:
            return masked_sentence, 0, "not present"
        return new_masked_sentence, occ, presence


    def play_game(self, sentence, category):
        raise NotImplementedError

class WheelOfFortuneTask(Task):

    def __init__(self, expt_player, exp_report, wheel, no_letter_loss=False):
        super(WheelOfFortuneTask, self).__init__(expt_player, exp_report)

        self.wheel = wheel
        self.no_letter_loss = no_letter_loss

        if self.no_letter_loss:
            print("No letter loss mode active")


        self.prompt_retriever = prompt.Prompt(self.wheel, no_letter_loss)

        self.system_prompt = self.prompt_retriever.get_system_prompt()
        self.example = self.prompt_retriever.get_example()

        self.templates = self.prompt_retriever.get_templates()


    def play_game(self, sentence, category):
        conversation = self.example.copy()

        masked_sentence = "".join(["_" if w != " " else " " for w in sentence])

        self.reporter.new_round()
        self.player.reset_player(self.system_prompt)

        budget = 0
        tries = 0

        single_consonant = r"^[BCDFGHJKLMNPQRSTVWXYZ]$"
        single_vowel = r"^[AEIOU]$"

        conversation.append(
            (
                "user", 
                self.templates['game'].format(
                    category=category, 
                    words=len(sentence.split(" ")), 
                    letters=len(sentence.replace(" ", "")), 
                    sentence=masked_sentence,
                    budget=budget
                )
            )
        )

        llm_msg, guess = self.player.make_guess(conversation)

        conversation.append(("assistant", llm_msg))
        self.reporter.log("_", masked_sentence, guess, sentence, budget)


        while guess != sentence and tries < 20:
            if tries > 20: break
            tries += 1
            conversation.append(("user", self.templates['user_wrong_result'].format(budget=budget)))

            llm_msg, action = self.player.make_guess(conversation)
            valid_action = "[SPIN]"


            if action == valid_action:
                conversation.append(("assistant", llm_msg))

                reward = self.wheel.spin_wheel()
                ammount = int(reward.replace("$", ""))
                conversation.append(
                    (
                        "user", 
                        self.templates['user_update_reward'].format(
                            reward=reward, 
                            budget=budget
                        )
                    )
                )
                llm_msg, letter = self.player.get_letter(conversation) 

                letter = letter.upper()
                conversation.append(("assistant", llm_msg))


                if re.match(single_consonant, letter) == None:
                    self.reporter.log("VOWEL NOT ALLOWED", masked_sentence, guess, sentence, budget)
                    break

                masked_sentence, presence, presence_text = self.add_letter_to_masked_sentence(letter, masked_sentence, sentence)

                if presence == 0:
                    self.reporter.log(letter, masked_sentence, guess, sentence, budget, ammount, presence)
                    if self.no_letter_loss: 
                        budget = 0
                        continue
                    else: break
                budget += ammount * presence 
                conversation.append(
                    (
                        "user", 
                        self.templates['user_round'].format(
                            category=category, 
                            words=len(sentence.split(" ")), 
                            letters=len(sentence.replace(" ", "")), 
                            presence=presence_text, 
                            sentence=masked_sentence
                        )
                    )
                )
                llm_msg, guess = self.player.make_guess(conversation)
                conversation.append(("assistant", llm_msg))
                self.reporter.log(letter, masked_sentence, guess, sentence, budget, ammount, presence)

            elif action.startswith("[BUY"):
                conversation.append(("assistant", llm_msg))



                vowel = action.upper().replace("[BUY VOWEL]", "").strip()
                vowel = vowel.replace("VOWEL:", "").strip()
                vowel = vowel.replace("\n","").replace(" ","").upper()

                if vowel == "PASS":
                    self.reporter.log("INSTRUCTION ERROR", masked_sentence, guess, sentence, budget-250)
                    break

                if re.match(single_vowel, vowel) == None:
                    self.reporter.log("CONSONANT NOT ALLOWED", masked_sentence, guess, sentence, budget-250)
                    break

                if budget < 250:
                    self.reporter.log("INSUFFICENT BUDGET", masked_sentence, guess, sentence, budget-250) 
                    break
                budget -= 250

                masked_sentence, presence, presence_text = self.add_letter_to_masked_sentence(vowel, masked_sentence, sentence)
                if presence == 0:
                    self.reporter.log(vowel, masked_sentence, guess, sentence, budget, "/", presence)
                    if self.no_letter_loss: 
                        budget = 0
                        continue
                    else: 
                        break
                
                conversation.append(
                    (
                        "user", 
                        self.templates['user_round'].format(
                            category=category, 
                            words=len(sentence.split(" ")), 
                            letters=len(sentence.replace(" ", "")), 
                            presence=presence_text, 
                            sentence=masked_sentence
                        )
                    )
                )
                llm_msg, guess = self.player.make_guess(conversation)
                guess = guess.upper()
                conversation.append(("assistant", llm_msg))
                self.reporter.log(vowel, masked_sentence, guess, sentence, budget, "/", presence)
            else:
                self.reporter.log("INSTRUCTION ERROR", masked_sentence, guess, sentence, budget-250)
                break

            if guess != sentence and guess != "PASS":
                conversation.append(("user", self.templates['user_wrong_result'].format(budget=budget)))
                break

                
        if tries >= 20: self.reporter.log("ERROR", masked_sentence, guess, sentence, budget)
        self.reporter.round_end()


    def clean_up(self):
        if isinstance(self.player, player.OllamaPlayer):
            self.player.clear_model()
