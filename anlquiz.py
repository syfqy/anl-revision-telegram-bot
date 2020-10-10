import random


# Create class object Question

class Question():
    def __init__(self, text, choices, answer):
        self.text = text
        self.choices = choices
        self.answer = answer
        self.letters = ["A", "B", "C"]

    def __str__(self):
        return f"{self.text}, {self.choices}"

    def ask(self):
        return self.text

    def show_choices(self):
        return (f"{self.letters[0]}. {self.choices[0]}\n{self.letters[1]}. {self.choices[1]}\n{self.letters[2]}. {self.choices[2]}")


    def show_answer(self):
        print(f"The correct answer is {self.answer}")

# Create class object Quiz
# Quiz is simply a list of Question objects, with length num_q where num_q is user-specified

class Quiz():

    def __init__(self, module, num_q, workb):
        wb = workb
        sheet = wb.get_sheet_by_name(f'{module}')
        og_quiz = create_quiz(sheet)
        random.shuffle(og_quiz)
        self.quiz = og_quiz[0:num_q]
        self.q_counter = 0
        self.user_score = 0

    def ask(self):
        return self.quiz[self.q_counter].ask()

    def show_choices(self):
        return self.quiz[self.q_counter].show_choices()

    def show_answer(self):
        return self.quiz[self.q_counter].answer


# Create quiz function to instantiate full-length Quiz
# og is then shuffled and sliced into new quiz with length num_q

def create_quiz(sheet):
    og_quiz = []
    row = range(2,41)
    for r in row:
        q = sheet.cell(r, 2).value
        a1 = sheet.cell(r, 3).value
        a2 = sheet.cell(r, 4).value
        a3 = sheet.cell(r, 5).value
        ca = sheet.cell(r, 6).value
        newq=Question(q, [a1,a2,a3],ca)
        og_quiz.append(newq)
    return og_quiz



# Function to ask number of questions in quiz

def ask_num():
    valid_nums = [10,15,20]
    while True:
        try:
            num = int(input("How many questions do you want to try?"))
            if num in valid_nums:
                result = num
                break
            else:
                print("Sorry, please enter 10, 15 or 20")
                pass
        except:
            print("Sorry, please enter 10, 20 or 30")
    return num


# In[18]:


# Function to insantiate quiz by randomly selecting questions based on user


# In[22]:


# Function to check user answer
def check_ans(question, answer):
    if user_ans == question.answer:
        print("That is correct!")
        result = 1
    else:
        print("Sorry, that is the wrong answer")
        result = 0
    return result


# In[23]:


# Function to ask user for his answer
def ask_user():
    valid_ans = ["A","B","C","S","Q"]
    while True:
        ans = input("Enter your answer: (Or enter S to skip this question or Q to end the quiz)")
        if ans.upper() in valid_ans:
            break
        else:
            print("Sorry, please enter A,B or C only\nOtherwise, enter S to skip or Q to end the quiz")
    return ans.upper()


# In[31]:
if __name__ == '__main__':

    '''
    This is a telegram bot to help students with their ANL305 Revision
    '''
# Step 1: Welcome message
    print("Welcome to ANL305 Revision Questions")

# Step 2: Enter number of q
    num_q = ask_num()

# Step 3: Intialize quiz
    this_quiz = create_quiz(og_quiz, num_q)

# Step 4: While loop to ask questions until user quits or last question answered
    playing = True
    i=0
    score = 0
    while playing and i<num_q:
        print(f"Question {i+1}")
        curr_q = this_quiz[i]
        curr_q.ask()
        print("\n")
        curr_q.show_choices()
        user_ans = ask_user()
        if user_ans == "S":
            print("Skipped")
            i+=1
            pass
        elif user_ans =="Q":
            print("Quit")
            break
        else:
            result = check_ans(curr_q, user_ans)
            print("\n")
            if result == 1:
                score+=1
                i +=1
            else:
                i+=1
    print(f"Your score is {score}/{num_q}")
    print("Thank you for playing, goodbye")
    









