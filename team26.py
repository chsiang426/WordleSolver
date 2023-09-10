import sys
import math

def calculate_entropies(answer_words, pos_words, i_word):
    e_dict = {}

    for word in answer_words:
        result = evaluate_guess_results(i_word, word)
        if result not in e_dict:
            e_dict[result] = 1
        else:
            e_dict[result] = e_dict[result]+1

    entropy = 0
    for i in e_dict.values():
        p = i/len(answer_words)
        entropy = entropy-p*math.log2(p)
    return entropy

def play(ans, first_word, answers_file):
    guess_results = ""
    res = ""
    
    answer_words = load_words(answers_file)
    pos_words = load_words(answers_file)
    number_of_guesses = 0 
    time = 1
    
    res += f"{ans}\n"
    while len(pos_words) > 0:
        #print(pos_words)
        if time == 1:
            current_guess = first_word
        else:
            current_guess = pick_word(answer_words, pos_words)
        #print(current_guess)
        number_of_guesses += 1

        guess_results = evaluate_guess_results(ans, current_guess) 

        copy_guess_result = change_format(guess_results)
        res += f"{time}; {current_guess}; \"{copy_guess_result}\"\n"
        
        if ('0' in guess_results)|('2' in guess_results)|('4' in guess_results):
            guess_results = transform(guess_results)
        elif '3' in guess_results:
            next_guess = ""
            for i in range(len(guess_results)):
                if guess_results[i] == '3':
                    next_guess += current_guess[i].swapcase()
                else:
                    next_guess += current_guess[i]
            time+=1
            number_of_guesses += 1
            guess_results = "1111111"
            copy_guess_result = change_format(guess_results)
            res += f"{time}; {next_guess}; \"{copy_guess_result}\"\n"
            
        if guess_results == "1111111":
            break

        pos_words = filter_words(pos_words, current_guess, guess_results)

        time+=1

    if guess_results == "1111111":
        pass
    else:
        print("Could not guess word")
        sys.exit()

    return number_of_guesses, res

def change_format(s):
    result = ""
    for i in range(len(s)):
        if i != (len(s)-1):
            result += s[i]+','
        else:
            result += s[i]
    return result

def load_words(answers_file):
    answer_words = []

    # load all answer words
    with open(answers_file, "r", newline="") as f:
        for word in f:
            word = word.strip()
            if len(word) == 7 and word.isalpha():
                answer_words.append(word)

    return answer_words

def filter_words(words, guess_word, guess_result):
    return [word for word in words if match_guess_result(word, guess_word, guess_result)]

def transform(ori_result):
    result = ""
    for a in ori_result:
        if a == '3':
            result = result+'1'
        elif a == '4':
            result = result+'2'
        else:
            result = result+a
    return result

def pick_word(answer_words, pos_words):
    best_word = ""
    max_entropy = 0
    for word in pos_words:
        entropy =  calculate_entropies(answer_words, pos_words, word)
        if entropy > max_entropy:
            max_entropy = entropy
            best_word = word
    return best_word

def match_guess_result(word, guess_word, guess_result):
    for i in range(len(guess_result)):
        if guess_result[i] == "1" and word[i] != guess_word[i]:
            return False
        elif guess_result[i] == "2":
            if guess_word[i] == word[i]:
                return False
            elif guess_word[i] not in word:
                return False
        elif guess_result[i] == "3" and word[i] != guess_word[i].swapcase():
            return False
        elif guess_result[i] == '4':
            guess_char = guess_word[i].swapcase()
            if guess_word[i] == guess_word[i].swapcase():
                return False
            elif guess_word[i].swapcase() not in word:
                return False
        elif guess_result[i] == "0":
            if word[i] == guess_word[i]:
                return False

            wrong_letter_instances_guess = find_letter_indexes_in_word(guess_word, guess_word[i])
            okCount = 0
            for j in wrong_letter_instances_guess:
                if guess_result[j] != "0":
                    okCount += 1
            wrong_letter_instances_word = find_letter_indexes_in_word(word, guess_word[i])
            if len(wrong_letter_instances_word) > okCount:
                return False

    return True

def find_letter_indexes_in_word(word, letter):
    return [i for i, ltr in enumerate(word) if ltr == letter]

# return guess results for a given word
def evaluate_guess_results(correct, guess):
    result = '0'* len(correct)
    
    #字母正確、位置正確、大小寫正確
    for index in (range(len(correct))):
        if guess[index] == correct[index]:
            result = result[:index] + '1' + result[(index+1):]
            correct = correct.replace(guess[index], '@', 1)        

    #字母正確、位置正確、大小寫不正確
    for index in range(len(correct)):
        if guess[index] != correct[index]:
            guess_char = guess[index].swapcase()
            if guess_char == correct[index]:
                result = result[:index] + '3' + result[(index+1):]
                correct = correct.replace(guess_char, '@', 1)        

    #字母正確、位置不正確、大小寫正確
    for index in range(len(correct)):
        if guess[index] in correct and result[index] == '0':
            result = result[:index] + '2' + result[(index+1):]
            correct = correct.replace(guess[index], '@', 1)     

    #字母正確、位置不正確、大小寫不正確。
    for index in range(len(correct)):   
        if guess[index] not in correct and result[index] == '0':
            guess_char = guess[index].swapcase()
            if guess_char in correct and result[index] == '0':
                result = result[:index] + '4' + result[(index+1):]
                correct = correct.replace(guess_char, '@', 1)        

    return result


if __name__ == "__main__":
    sum = 0
    answers = []       
    all_words = [] 
    if len(sys.argv)!=4:
        print("Error")
        sys.exit(0)
    answers_file = sys.argv[1]
    test_words_file = sys.argv[2]
    response_file = sys.argv[3]

    with open(test_words_file, "r", newline="") as f:
        for word in f:
            word = word.strip() 
            if len(word) == 7 and word.isalpha():          
                answers.append(word)
    
    all_words = load_words(answers_file)
                
    first_word = pick_word(all_words, all_words)

    with open(response_file, "w", newline="") as f:
        for ans in answers:
            total_guesses = 0
            total_guesses, result = play(ans, first_word, answers_file)
            print(total_guesses)
            print(result)
            f.write(f"{result}{total_guesses}\n")