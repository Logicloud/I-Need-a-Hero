import loading  # stfu pycharm, I swear this is used

import re
import os
import time
import configparser
import ast

try:
    from PIL import Image
except (ImportError, ModuleNotFoundError):
    print("You didn't run setup.bat first! Try again after you do that.")
    raise SystemExit

from get_counters import get_counter  # naming is hard
import namenum_converter as conv

config = configparser.ConfigParser()
with open('settings.ini', 'r+') as configfile:
    config.read('settings.ini')
    delete_thresehold = int(config['MAIN']['delete_thresehold'])
    process_threshold = int(config['MAIN']['process_threshold'])
    low_precision = ast.literal_eval(config['MAIN']['low_precision'])
    process_allies = ast.literal_eval(config['MAIN']['process_allies'])
    dev = ast.literal_eval(config['MAIN']['dev'])

heroes = ['ana', 'bastion', 'dva', 'genji', 'hanzo',
          'junkrat', 'lucio', 'mccree', 'mei', 'mercy',
          'pharah', 'reaper', 'reinhardt', 'roadhog', 'soldier',
          'sombra', 'symmetra', 'torbjorn', 'tracer', 'widowmaker',
          'winston', 'zarya', 'zenyatta', 'unknown', 'loading',
          'anadead', 'bastiondead', 'dvadead', 'genjidead', 'junkratdead',
          'luciodead', 'mccreedead', 'meidead', 'pharahdead', 'reaperdead',
          'roadhogdead', 'soldierdead', 'sombradead', 'torbjorndead', 'tracerdead',
          'zaryadead', 'zenyattadead', 'hanzodead', 'mercydead', 'orisadead',
          'reinhardtdead', 'symmetradead', 'widowmakerdead', 'winstondead']

heroes_normal = []
for i in heroes:
    hero = conv.strip_dead(i)
    if ('unknown' not in hero) and ('loading' not in hero):
        heroes_normal.append(hero)

if process_allies:
    filenames = ['ally1', 'ally2', 'ally3', 'ally4', 'ally5', 'ally6',
                 'enemy1', 'enemy2', 'enemy3', 'enemy4', 'enemy5', 'enemy6']
else:
    filenames = ['enemy1', 'enemy2', 'enemy3', 'enemy4', 'enemy5', 'enemy6']
if dev:
    print('FYI, developer mode is on.')
    dev_file = 'bettercrop.jpg'

inputs_before = os.listdir('Overwatch')

print('Loading complete. Hold tab and press the "print screen" button to analyze and get counters.')

while True:
    time.sleep(0.5)  # to stop high cpu usage while waiting
    continue_ = False
    inputs_after = os.listdir('Overwatch')
    if len(inputs_after) > len(inputs_before):
        continue_ = True
    if len(inputs_after) < len(inputs_before):
        continue_ = False
        inputs_before = os.listdir('Overwatch')
    if continue_ or dev:
        # starting analysis
        time.sleep(0.1)
        inputs_diff = list(set(os.listdir('Overwatch')) - set(inputs_before))
        current_filename = str(inputs_diff)[2:-2]
        print("\nProcessing " + current_filename)
        if not dev:
            screenshot = Image.open('Overwatch/' + inputs_diff[0]).resize((1920, 1080))
        else:
            screenshot = Image.open(dev_file).resize((1920, 1080))

        ally1 = screenshot.crop((443, 584, 519, 660))
        ally2 = screenshot.crop((634, 584, 710, 660))
        ally3 = screenshot.crop((826, 584, 902, 660))
        ally4 = screenshot.crop((1019, 584, 1095, 660))
        ally5 = screenshot.crop((1210, 584, 1286, 660))
        ally6 = screenshot.crop((1402, 584, 1478, 660))
        enemy1 = screenshot.crop((443, 279, 519, 355))
        enemy2 = screenshot.crop((634, 279, 710, 355))
        enemy3 = screenshot.crop((826, 279, 902, 355))
        enemy4 = screenshot.crop((1019, 279, 1095, 355))
        enemy5 = screenshot.crop((1210, 279, 1286, 355))
        enemy6 = screenshot.crop((1402, 279, 1478, 355))

        ally1.save('output/ally1.png')
        ally2.save('output/ally2.png')
        ally3.save('output/ally3.png')
        ally4.save('output/ally4.png')
        ally5.save('output/ally5.png')
        ally6.save('output/ally6.png')
        enemy1.save('output/enemy1.png')
        enemy2.save('output/enemy2.png')
        enemy3.save('output/enemy3.png')
        enemy4.save('output/enemy4.png')
        enemy5.save('output/enemy5.png')
        enemy6.save('output/enemy6.png')

        allied_team = []
        enemy_team = []
        total_confidence = []

        h = 0
        for h in range(0, len(filenames)):
            unknown = Image.open('output/' + filenames[h] + '.png').load()

            confidences = []
            for i in heroes:
                confidences.append(0)
            #print(confidences)

            x = 0
            y = 0
            j = 0
            if low_precision:
                step = 2
            else:
                step = 1
            for j in range(0, len(heroes)):
                learned_image = Image.open('learned/' + heroes[j] + '.png').load()
                for x in range(0, 75, step):
                    for y in range(0, 75, step):
                        input_color = unknown[x, y]
                        input_color = int(re.sub('[^0-9]', '', str(input_color)[1:4]))  # sorry

                        learned_color = learned_image[x, y]
                        learned_color = int(re.sub('[^0-9]', '', str(learned_color)[1:4]))

                        confidences[j] += abs(input_color - learned_color)
                confidences[j] = 1 - (confidences[j] / 1434375)

            likely_name = ''
            likely_num = 0
            i = 0
            for i in range(0, len(confidences)):
                #print(heroes[i] + ': ' + str(confidences[i]))
                if confidences[i] > likely_num:
                    likely_num = confidences[i]
                    likely_name = heroes[i]

            if 'ally' in filenames[h]:
                allied_team.append(likely_name)
            elif 'enemy' in filenames[h]:
                enemy_team.append(likely_name)

            print("For " + filenames[h] + ":")

            print_conf = int(likely_num * 100)
            print("Most likely is " + likely_name
                  + ", with a confidence of " + str(print_conf) + "%")
            total_confidence.append(print_conf)

            prev_name = likely_name
            likely_name = ''
            likely_num = 0
            i = 0
            for i in range(0, len(confidences)):
                if confidences[i] > likely_num and heroes[i] != prev_name:
                    likely_num = confidences[i]
                    likely_name = heroes[i]
            print_conf = int(likely_num * 100)
            print("Second most is " + likely_name
                  + ", with a confidence of " + str(print_conf) + "%")

        print('\n')
        enemy_team_fancy = ''
        for i in enemy_team:
            hero = conv.fancify(i)
            enemy_team_fancy += (hero + ', ')
        print("Enemy team: " + enemy_team_fancy[:-2])
        if process_allies:
            allied_team_fancy = ''
            for i in allied_team:
                hero = conv.fancify(i)
                allied_team_fancy += (hero + ', ')
            print("Allied team: " + allied_team_fancy[:-2])

        total_conf_average = int(sum(total_confidence) / float(len(total_confidence)))
        print("Confidence: " + str(total_conf_average) + '%')

        if total_conf_average > process_threshold and process_allies:
            allied_team_counter = 0
            for i in enemy_team:
                for j in allied_team:
                    cross_team_counter = get_counter(i, j)
                    allied_team_counter -= cross_team_counter
            #print(allied_team_counter)
            if allied_team_counter < 0:
                print("Your team has an counter advantage of " + str(-allied_team_counter))
            else:
                print("The enemy team has an counter advantage of " + str(allied_team_counter))

        enemy_is_heroes = True
        j = 0
        for i in enemy_team:
            if (i == 'loading') or (i == 'unknown'):
                j += 1
        if j == 6:
            enemy_is_heroes = False

        if enemy_is_heroes and (total_conf_average > process_threshold):  # is this valid to get counters from
            all_counters = {}  # begin getting counters

            for any_hero in heroes_normal:
                all_counters[any_hero] = 0
                for enemy_hero in enemy_team:
                    enemy_hero = conv.strip_dead(enemy_hero)
                    if ('unknown' not in any_hero) and ('loading' not in any_hero):
                        countered = get_counter(any_hero, enemy_hero)
                        all_counters[any_hero] -= countered

            sorted_counters = sorted(all_counters.items(), reverse=True, key=lambda z: z[1])  # wtf
            final_counters = ''
            #print(sorted_counters)

            for hero in sorted_counters:
                just_name = hero[0]
                just_num = hero[1]
                full_counter = conv.fancify(just_name) + ': ' + str(just_num)
                final_counters += (full_counter + ', ')
            print('\n')   # end getting counters

            print("Counters (higher is better): ")
            print(final_counters[:-2] + '\n')
        elif not enemy_is_heroes:
            print("\nThe enemy team appears to be all loading or unknown, which counters can't be calculated from.")

        if total_conf_average > delete_thresehold and not dev:
            os.remove('Overwatch/' + inputs_diff[0])
            print("Deleted " + current_filename + ' (needed ' + str(delete_thresehold)
                  + '% confidence, got ' + str(total_conf_average) + '%)')
        else:
            print("Didn't delete " + current_filename + ' (needs ' + str(delete_thresehold)
                  + '% confidence, got ' + str(total_conf_average) + '%)')
            if delete_thresehold >= 100:
                print("The delete threshold is currently 100%, which means that even tab menu screenshots aren't"
                      " deleted. Be sure to clean the screenshots folder out manually every now and then.")
        inputs_before = os.listdir('Overwatch')

        if dev:
            raise SystemExit

        print('\n')
        print('Analysis complete. Hold tab and press the "print screen" button to get a new set of counters.')
