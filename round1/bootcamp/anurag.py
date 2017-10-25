import sys
import numpy as np
from collections import defaultdict

SIZE = 7
EMPTY = '_'
board = np.array([[EMPTY]*SIZE for n in xrange(SIZE)])
board_T = board.T
letters = [str(unichr(l)) for l in range(65,91)]
trick_counter=0
trick_word=''
trick_word_counter=0
word_map = defaultdict(set)

xys = [(i,j) for i in xrange(SIZE) for j in xrange(SIZE)]

def build_worddict():
    global word_map
    global trick_word
    for line in open('words.dat'):
        line = line.strip('\n')
        for i in range(len(line)-1):
            word_map[line[:i+1]].add(line[:i+2])
        for i in range(1, len(line)):
            word_map[line[1:i+1]].add(line[:i+1])
        word_map[line].add(1)
        if len(line)==SIZE:
            trick_word=line


def xy_to_num(x, y):
    return (x * SIZE) + y

def print_board():
    xys = [(i,j) for i in xrange(SIZE) for j in xrange(SIZE)]
    count = 1
    for x,y in xys:
        sys.stdout.write(board[x][y])
        if count%SIZE == 0: print ''
        count += 1
    print '\n'

def loop_and_play():
    while True:
        sys.stdout.write(pick_letter())
        sys.stdout.write('\n')
        sys.stdout.flush()

        opp_char = raw_input()
        sys.stdout.write(place_letter(opp_char))
        sys.stdout.write('\n')
        sys.stdout.flush()

def start():
    build_worddict()

    """
        The first line of input contains the starting letter which is automatically 
        placed in the center of the board (at position 24). 
    """
    starting_char = raw_input()
    board[SIZE/2][SIZE/2] = starting_char
    board_T = board.T
    """
        The second line of input specifies if you are the first one to start 
        or your opponent is starting first. A value of 1 indicates that you start 
        first and 0 otherwise.
    """
    first_or_second = raw_input()
    if first_or_second == '0':
        opp_char = raw_input()
        sys.stdout.write(place_letter(opp_char))
        sys.stdout.write('\n')
        sys.stdout.flush()

    loop_and_play()

"""
    ---------------------------- TODO: implement your logic here --------------------------------
"""

def count_board(board):
    counter = []
    for i in range(len(board)):
        count = 0
        for j in range(len(board)):
            if board[i][j]=='_':
                count+=1
        counter.append(count)
    return counter

def trick_chance():
    global trick_counter
    global trick_word
    global trick_word_counter
    global board
    global board_T
    x, y =xys[trick_counter]
    chosen_letter = trick_word[trick_word_counter]
    board[x][y]=chosen_letter
    board_T=board.T
    trick_word_counter+=1
    trick_word_counter%=SIZE
    trick_counter+=1
    return chosen_letter + ' ' + str(xy_to_num(x,y))

def pick_letter():
    # TODO: Your chance to pick a letter of your choice
    global trick_counter
    if trick_counter<21:
        return trick_chance()
    letter_possibility=[]
    for letter in letters:
        poss = check_possibility(letter)
        if len(poss)!=0:
            letter_possibility.append([letter, poss[0]])
    if len(letter_possibility)==0:
        chosen_letter = str(unichr(np.random.randint(65,90)))
        pos = place_letter(chosen_letter)

    else:
        letter_possibility=sorted(letter_possibility,key = lambda x:x[1][2], reverse=True)
        pos = place_letter(letter_possibility[0][0])
        chosen_letter = letter_possibility[0][0]
    return  chosen_letter + ' ' + pos

def check_possibility(letter):
    global board
    global board_T
    possible_places=[]
    # Board forward horizontal
    for i in range(3,SIZE):
        j=0
        while(j<SIZE):
            while(j<SIZE and board[i][j]=='_'): j+=1
            if j==SIZE: break
            k=j+1
            while(k<SIZE and board[i][k]!='_'): k+=1
            if k==SIZE: break
            curr = ''.join(board[i,j:k])
            if curr+letter in word_map[curr] and 1 in word_map[curr+letter]:
                possible_places.append([i,k,len(curr)+1, int(1 in word_map[curr+letter])])
            j+=1
    # Board_T forward horizontal
    for i in xrange(SIZE):
        j=3
        while(j<SIZE):
            while(j<SIZE and board_T[i][j]=='_'): j+=1
            if j==SIZE: break
            k=j+1
            while(k<SIZE and board_T[i][k]!='_'): k+=1
            if k==SIZE: break
            curr = ''.join(board_T[i,j:k])
            if curr+letter in word_map[curr] and 1 in word_map[curr+letter]:
                possible_places.append([k,i,len(curr)+1, int(1 in word_map[curr+letter])])
            j+=1
    # Board reverse horizontal
    for i in range(3,SIZE):
        j=0
        while(j<SIZE):
            while(j<SIZE and board[i][j]=='_'): j+=1
            if j==SIZE: break
            k=j+1
            while(k<SIZE and board[i][k]!='_'): k+=1
            if k==SIZE: break
            if j>0 and board[i][j-1]=='_':
                curr = ''.join(board[i,j:k])
                if letter+curr in word_map[curr] and 1 in word_map[letter+curr]:
                    possible_places.append([i,j-1,len(curr)+1, int(1 in word_map[letter+curr])])
            j=k
    # Board_T reverse horizontal
    for i in xrange(3, SIZE):
        j=3
        while(j<SIZE):
            while(j<SIZE and board_T[i][j]=='_'): j+=1
            if j==SIZE: break
            k=j+1
            while(k<SIZE and board_T[i][k]!='_'): k+=1
            if k==SIZE: break
            if j>3 and board_T[i][j-1]=='_':
                curr = ''.join(board_T[i,j:k])
                if letter+curr in word_map[curr] and 1 in word_map[letter+curr]:
                    possible_places.append([j-1,i,len(curr)+1, int(1 in word_map[letter+curr])])
            j=k
    return sorted(possible_places, key=lambda x: x[2], reverse=True)

def place_letter(letter=None):
    # TODO: Place the letter at a position of your choice
    global board
    global board_T
    possible_places=check_possibility(letter)

    if len(possible_places) == 0:
        ind = np.argmax(count_board(board)[3:])+3
        for j in range(SIZE):
            if board[ind][j]=='_':
                p_x, p_y = ind, j
                break

    else:
        flag = 0
        for chance in possible_places:
            if chance[3]==1:
                flag = 1
                break
        if flag == 0:
            chance = possible_places[0]
        p_x, p_y = chance[0], chance[1]

    board[p_x][p_y]=letter
    board_T = board.T
    return str(xy_to_num(p_x, p_y))


start()