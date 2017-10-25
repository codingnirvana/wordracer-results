import sys

SIZE = 7
EMPTY = '_'
POINTS = {7: 13, 6: 8, 5: 5, 4: 4, 3: 3, 2: 2, 1: 1}
board = [[EMPTY]*SIZE for n in xrange(SIZE)]

# used for testing, overwritten later
WORDS = ['ABAKAS', 'AAL', 'ABANDON', 'ABAS', 'ZYGOTE', 'ZYMASE']

# TODO: pick words with even distribution of alphabet
def sample_words():
    global WORDS

    SAMPLE_WORDS = []
    ALL_WORDS = [line.strip() for line in open('words.dat')]
    ALL_WORDS.sort(key=lambda word: -len(word))
    #print ALL_WORDS[:100]

    WORDS = ALL_WORDS[-100:]    
    WORDS += ALL_WORDS[:100]

    for i in xrange(100, len(ALL_WORDS) - 100):
        if i%250 == 0:
            WORDS.append(ALL_WORDS[i])
            
    WORDS = list(set(WORDS))
    WORDS.sort(key=lambda word: -len(word))    

def xy_to_num(x, y):
    return x + (y * SIZE)

def num_to_xy(num):
    return 11%SIZE, 11/SIZE

def contains(word, target):    
    j = 0
    for i in xrange(len(word)):
        if i >= len(target): break
        if word[i] != EMPTY and target[j] != word[i]: j = 0
        else: j += 1
    return j == len(word)

"""
    TODOS:
    * give importance to words containing opp_char
    * placeholder is checked naively - only extreme L2R and T2B
"""
def score_for(placeholder, word):
    count = 0;
    if placeholder.find(EMPTY) == -1: return -1  # all slots are filled    
    if not contains(placeholder, word): return -1
    for i in xrange(len(word)):        
        if placeholder[i] == word[i]: count += 2*POINTS[len(word)]
        elif placeholder[i] == EMPTY: count += POINTS[len(word)]        
    return count

def row_col_from_xy(x, y): # (1,2)
    row = [board[r][y] for r in xrange(SIZE)] # (0,2) ... (4,2)
    col = [board[x][c] for c in xrange(SIZE)] # (1,0) ... (1,4)
    return row, col

def word_scores(x, y, row_or_col,placeholder):
    candidates= {}    
    for word in WORDS:           
        score = score_for(placeholder, word)
        if score != -1:
            candidates[x, y, row_or_col, word] = score
    return candidates

def sorted_candidates():
    xys = [(i,j) for i in xrange(SIZE) for j in xrange(SIZE)]
    candidates = {}
    for x,y in xys:  # (1,2)
        if board[x][y] != EMPTY: continue
        row, col = row_col_from_xy(x, y)
        candidates.update(word_scores(x, y, 'R', ''.join(row)))
        candidates.update(word_scores(x, y, 'C', ''.join(col)))
    
    candidates = sorted(candidates.items(), key=lambda x: -x[1])  # sorted desc by score
    return candidates

def update_board(x, y, row_or_col, placeholder):   
    global board

    row, col = row_col_from_xy(x, y)
    if row_or_col == 'R':
        for r in xrange(SIZE):
            board[r][y] = placeholder[r]
    else:
        for c in xrange(SIZE):
            board[x][c] = placeholder[c] 

def print_board():
    pass
#    xys = [(i,j) for i in xrange(SIZE) for j in xrange(SIZE)]
#    count = 1
#    for x,y in xys:
#        sys.stdout.write(board[y][x])
#        if count%SIZE == 0: print ''
#        count += 1
#    print '\n'

def fill(candidates, char=None):    
    global board
    for (x,y,row_or_col,word), score in candidates:        
        row, col = row_col_from_xy(x, y)
        placeholder = row if row_or_col == 'R' else col       
        
        if char is not None:                      
            placeholder_word = ''.join(placeholder)            
            index = word.find(char)              
            if index == -1 or placeholder_word[index] != EMPTY: continue
            if row_or_col == 'R': x = index
            else: y = index

            if board[x][y] != EMPTY: continue
            
            placeholder[index] = char
            update_board(x, y, row_or_col, placeholder)                
            return (x,y), char
        else:            
            for i in xrange(len(word)):
                if row_or_col == 'R': x = i
                else: y = i

                if placeholder[i] == EMPTY and board[x][y] == EMPTY:                                             
                    placeholder[i] = word[i]                    
                    update_board(x, y, row_or_col, placeholder)
                    return (x,y), word[i]     

    # fill has not taken place            
    if len(candidates) == 0:
        # randomly pick an empty position
        xys = [(i,j) for i in xrange(SIZE) for j in xrange(SIZE)]          
        for x,y in xys:    
            if board[x][y] == EMPTY:
                to_fill = char if char is not None else 'X'
                board[x][y] = to_fill
                return (x, y), to_fill

    elif char is not None:
        # no matches found - have to sacrifice least potential placeholder        
        (x,y,row_or_col,word), score = candidates[-1]
        row, col = row_col_from_xy(x, y)
        placeholder = row if row_or_col == 'R' else col        
        for i in xrange(len(placeholder)):
            if placeholder[i] == EMPTY and board[x][y] == EMPTY:
                placeholder[i] = char
                update_board(x, y, row_or_col, placeholder)
                return (x,y), char


def calc_pos(opp_char=None):        
    candidates = sorted_candidates()
    (x,y), my_char = fill(candidates, opp_char)
    if opp_char is None:
        return my_char + ' ' + str(xy_to_num(x, y))
    else:        
        return str(xy_to_num(x, y))

def loop_and_play():
    while True:
        sys.stdout.write(calc_pos())
        sys.stdout.write('\n')
        sys.stdout.flush()

        print_board()        
        opp_char = raw_input()
        sys.stdout.write(calc_pos(opp_char))
        sys.stdout.write('\n')
        sys.stdout.flush()

        print_board()

def start():    
    sample_words()

    """
        The first line of input contains the starting letter which is automatically 
        placed in the center of the board (at position 24). 
    """
    starting_char = raw_input()
    board[SIZE/2][SIZE/2] = starting_char            
    print_board()
    """
        The second line of input specifies if you are the first one to start 
        or your opponent is starting first. A value of 1 indicates that you start 
        first and 0 otherwise.
    """
    first_or_second = raw_input()
    if first_or_second == '0':        
        opp_char = raw_input()
        sys.stdout.write(calc_pos(opp_char))
        sys.stdout.write('\n')
        sys.stdout.flush()

    loop_and_play()

start()
