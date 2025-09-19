from argparse import ArgumentParser
import os
import yaml
from tqdm import tqdm
from datetime import datetime
import pandas as pd
import json 

import wheel
import task
import reporter
import player

def setup_new_experiment_dir(args):

    now = datetime.now()
    date_suffix = '-'.join((str(x) for x in [now.year, now.month, now.day, now.hour, now.minute]))
    if '/' in args['player']['name']:
        exp_prefix = args['player']['name'].split('/')[-1]
    else:
        exp_prefix = (args['player']['name'])

    new_root = os.path.join(args['reporting']['root'], f"{exp_prefix}-{date_suffix}/")

    if args['verbose']:
        tqdm.write(f"Constructing new results directory at {new_root}\n")

    args['reporting']['root'] = new_root
    os.makedirs(new_root, exist_ok=True)

    yaml.safe_dump(args, open(os.path.join(args['reporting']['root'], os.path.basename(args["experiment_config"])), 'w'))


def choose_player_class(args) -> player.Player:

    if args['player']['type'] == 'ollama':
        return player.OllamaPlayer(args)
    if args['player']['type'] == 'GPT':
        return player.GPTPlayer(args)
    elif args['player']['type'] == 'gemini':
        return player.GeminiPlayer(args)
    elif args['player']['type'] == 'mistral':
        return player.MistralPlayer(args)
    else:
        raise ValueError("Invalid guesser type; choose from (Ollama, GPT, gemini, mistral)")


def choose_task_class(args, expt_player, exp_report, wheel=None) -> task.Task:
    if args['player']['type'] in ['GPT', 'gemini', 'mistral', 'ollama']:
        return task.WheelOfFortuneTask(expt_player, exp_report, wheel, args['no_letter_loss'])
    else:
        raise ValueError("Invalid task or player type.")


if __name__ == '__main__':

    argp = ArgumentParser()
    argp.add_argument('-c', '--config_file', type=str, required=True, help='Path to the experiment configuration file.')
    cli_args = argp.parse_args()

    exp_config = os.path.join("../configs", cli_args.config_file)
    args = yaml.safe_load(open(exp_config, 'r'))
    args['experiment_config'] = exp_config

    if args['verbose']: tqdm.write("Configuration file loaded.")

    if "continue_from" not in args['reporting']: 
        setup_new_experiment_dir(args)
    else: 
        if args['verbose']: tqdm.write(f"Continuing from {args['reporting']['continue_from']}")

        args['reporting']['root'] = os.path.join(args['reporting']['root'], args['reporting']['continue_from'])

        sentences_done = []

        with open(os.path.join(args['reporting']['root'], 'report.jsonl'), 'r') as f:
            for line in f:
                try:
                    sentences_done.append(json.loads(line)['solution'])
                except Exception:
                    continue

        sentences_done = set(sentences_done)


    if args['verbose']: tqdm.write("Setting up game...")


    # Retrive classes.

    expt_player = choose_player_class(args)
    expt_reporter = reporter.Reporter(args)

    wheel = wheel.Wheel(args)
    expt_task = choose_task_class(args, expt_player, expt_reporter, wheel)

    # Loading data.
    df = pd.read_json(args['data']['path'], orient="records", lines=True)

    # Play the game
    if args['verbose']: game_loop = tqdm(df.iterrows(), total=len(df), desc="[Playing game...]")
    else: game_loop = df.iterrows()

    for idx, row in game_loop:

        if "continue_from" in args['reporting']:
            if row['sentence'] in sentences_done:
                continue

        expt_task.play_game(row['sentence'], row['category'])


    if args['verbose']: tqdm.write("\nGame complete. Compiling the report...\n")
    expt_task.clean_up()

    report = expt_reporter.final_report()
    json.dump(report, open(os.path.join(args['reporting']['root'], 'stats.json'), 'w'))


    if args['verbose']:
        tqdm.write(f"Final report:\n{report}")
        tqdm.write(f"Experiment complete.")

