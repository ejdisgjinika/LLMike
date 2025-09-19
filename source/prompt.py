import player


class Prompt():

    def __init__(self, wheel, no_letter_loss=False):
        
        self.model = None

        self.wheel = wheel
        self.no_letter_loss = no_letter_loss


        self.system_prompts = f"""You are a participant in the famous tv quiz show "Wheel of Fortune" and the user is the game master.
                Following there are the game instructions and an example of a game.
                ### INSTRUCTIONS ###
                1) At the start, the user will give you a category and a masquerade sentence where each letter is covered by an underscore "_" and the words are separated by spaces " ". You start with a [BUGDET 0$] and you can earn money by spinning the Wheel.
                2) For each [ROUND] you can choose to (1) [SPIN] or (2) [BUY VOWEL] for 250.
                If you choose [SPIN], you receive from the Wheel a [REWARD] in $; after each spin, you have to think which consonant is better to choose in order to complete the sentence. You have to choose a SINGLE UPPERCASE CONSONANT between B, C, D, F, G, J, K, L, M, N, P, Q, S, T, V, X, Z, H, R, W, Y that you think is contained in the hidden sentence and is not already present in the masked sentence. You have to ensure that you have choose a consonant otherwise you [LOSE] the game.
                If the consonant is contained the user will tell you how many occurrences there are and you will see the consonant appear in the correct position replacing the underscores and earn the reward times the occurrences; if the consonant is not contained you [LOSE] the game.
                You can chose [BUY VOWEL] only if you have more than [BUDGET 250$] You have to check if you can buy a vowel considering the budget you have and the cost of a vowel (250$). If you choose [BUY VOWEL] you have to choose a vowel between A, E, I, O, U. You have to follow this sintax: "[BUY VOWEL] [AEIOU]" as in the example .If you choose a vowel that is not contained in the sentence you [LOSE] the game.
                3) After each round you can make a [GUESS] providing the solution or responding with a \"Pass\". If you \"Pass\" you skip the round otherwise if you try a guess and it's wrong you [LOSE] the game. Before answering, check that the number of words and letters of your [GUESS] match the sentence.
                ### GOAL ###
                1) You don't have to [LOSE] the game: you can [LOSE] the game if you chose a letter that is not contained in the sentence or if you make a wrong [GUESS]. 
                2) Maximixe your [BUDGET]

                Do not make any comment, just provide the requested information.
                """

        self.system_prompts_no_letter_loss = f"""You are a participant in the famous tv quiz show "Wheel of Fortune" and the user is the game master.
                Following there are the game instructions and an example of a game.
                ### INSTRUCTIONS ###
                1) At the start, the user will give you a category and a masquerade sentence where each letter is covered by an underscore "_" and the words are separated by spaces " ". You start with a [BUGDET 0$] and you can earn money by spinning the Wheel.
                2) For each [ROUND] you can choose to (1) [SPIN] or (2) [BUY VOWEL] for 250.
                If you choose [SPIN], you receive from the Wheel a [REWARD] in $; after each spin, you have to think which consonant is better to choose in order to complete the sentence. You have to choose a SINGLE UPPERCASE CONSONANT between B, C, D, F, G, J, K, L, M, N, P, Q, S, T, V, X, Z, H, R, W, Y that you think is contained in the hidden sentence and is not already present in the masked sentence. You have to ensure that you have choose a consonant otherwise you [LOSE] the game.
                If the consonant is contained the user will tell you how many occurrences there are and you will see the consonant appear in the correct position replacing the underscores and earn the reward times the occurrences; if the consonant is not contained your budget wil be reset!
                YYou can chose [BUY VOWEL] only if you have more than [BUDGET 250$] You have to check if you can buy a vowel considering the budget you have and the cost of a vowel (250$). If you choose [BUY VOWEL] you have to choose a vowel between A, E, I, O, U. You have to follow this sintax: "[BUY VOWEL] Vowel: [AEIOU]" as in the example .If you choose a vowel that is not contained your [BUDGET] will be reset.
                3) After each round you can make a [GUESS] providing the solution or responding with a \"Pass\". If you \"Pass\" you skip the round otherwise if you try a guess and it's wrong you [LOSE] the game. Before answering, check that the number of words and letters of your [GUESS] match the sentence.
                ### GOAL ###
                1) You don't have to [LOSE] the game: you can [LOSE] the game if you make a wrong [GUESS]. 
                2) Maximixe your [BUDGET]

                Do not make any comment, just provide the requested information.
                """


    
        # prima iterazione
        self.game_template = """
            [GAME]
            Category: {category} - {words} word - {letters} letters
            Sentence: {sentence}
            [BUDGET {budget}$]
            [GUESS]
        """

        self.user_wrong_result_template = """
            [ROUND]
            [BUDGET {budget}$]
            [SELECT ACTION]
        """

        self.user_round_template = """
            Category: {category} - {words} word - {letters} letters
            Occurence: {presence}
            Sentence: {sentence}
            [GUESS]
        """


        self.user_update_reward_template = """
            [REWARD]
            Sector: {reward}$
        """


    def get_system_prompt(self):
        return self.system_prompts

        
    def get_example(self):
        return [
            ("system", self.get_system_prompt()),
            ("user", "[GAME] \n Category: Animal - 2 word - 7 letters \n Sentence: ____ ___ \n [BUDGET 0$] \n [GUESS]"),
            ("assistant", "PASS"),
            ("user", "[ROUND] \n [BUDGET 0$] \n [SELECT ACTION]"),
            ("assistant", "[SPIN]"),
            ("user", "[REWARD] \n Sector: 400$ \n"),
            ("assistant", "Consonant: G"),
            ("user", "Occurrence: 1 \n Sentence: G___ ___ \n [GUESS]"),
            ("assistant", "PASS"),
            ("user", "[ROUND] \n [BUDGET 400$] \n [SELECT ACTION]"),
            ("assistant", "[BUY VOWEL] Vowel: A \n"),
            ("user", " Occurrence: 1 \n Sentence: G___ _A_ \n [GUESS]"),
            ("assistant", "PASS"),
            ("user", "[ROUND] \n [BUDGET 150$] \n [SELECT ACTION]"),
            ("assistant", "[SPIN]"),
            ("user", "[REWARD] \n Sector: 150$ \n"),
            ("assistant", "Consonant: D"),
            ("user", "Occurrence: 1 \n Sentence: G__D _A_ \n [GUESS]"),
            ("assistant", "PASS"),
            ("user", "[ROUND] \n [BUDGET 300$] \n [SELECT ACTION]"),
            ("assistant", "[BUY VOWEL] Vowel: O \n"),
            ("user", " Occurrence: 2 \n Sentence: GOOD _A_ \n [GUESS]"),
            ("assistant", "GOOD RAT"),
        ]
        

    
    def get_templates(self):
        """
        Returns a dict containing the templates for:
        - game | key: game
        - user round | key: user_round
        - user wrong result | key: user_wrong_result
        - user update reward | key: user_update_reward
        """
        return {
            "game": self.game_template,
            "user_round": self.user_round_template,
            "user_wrong_result": self.user_wrong_result_template,
            "user_update_reward": self.user_update_reward_template,
        }
