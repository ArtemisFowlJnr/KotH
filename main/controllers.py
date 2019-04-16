import os, subprocess


class Bot(object):
    def __init__(self, file, target):
        self.file = file
        self.name = ''.join(file.split('__')[:-1])
        self.target = target


class BotFail:
    """
    See get_action for description
    """
    def __init__(self, filename, timeout=False, error=None, invalid=False):
        self.filename = filename
        self.timeout = timeout
        self.error = error
        self.invalid = invalid

    __slots__ = 'filename', 'timeout', 'error', 'invalid'
        
        

def get_action(filename, retry=1, timeout=5,
               validate=lambda _, _: True, get_input=lambda _: ''):
    """
    Get an action from the bot in filename.
    Params:
    validate  - called with program output and the filename
                in that order, and should return a boolean
                value indicating whether the program output
                was valid
    get_input - called with the filename, should return a
                string, which will be stdin for the program
    filename  - the name of the program to be executed
    retry     - the maximum number of times the program will
                be run (retry after bad output). 0 means
                forever (until it gives a valid output)
    timeout   - how long to wait for the program, in seconds.
                0 means forever

    Returns the action (as a string) or a BotFail class,
    which will contain the following:
    filename  - the filename of the bot
    timeout   - boolean, indicating if the fail was due to
                it reaching maximum time
    error     - if the fail was due to an error, a string
                containing that error, otherwise None
    invalid   - boolean indicating if the fail was due to
                validate returning false
    """
    retry = int(retry)
    always = not retry
    timeout = float(timeout)
    fail = None
    while retry or always:
        text = get_input(filename)
        numfile = open('input', 'w')
        numfile.write(str(get_input()))
        numfile.close()
        open('command', 'w').close()
        open('error', 'w').close()
        stdin = open('input')
        stdout = open('output', 'w')
        stderr = open('error', 'w')
        try:
            subprocess.run([os.path.join(os.getcwd(), 'bots', bot.file)],
                           timeout=timeout or None, stdin=stdin, stdout=stdout,
                           stderr=stderr, shell=True)
        except subprocess.TimeoutExpired:
            fail = BotFail(filename, True)
            for f in (stdin, stdout, stderr):
                f.close()
            retry -= 1
            break
        for f in (stdin, stdout, stderr):
            f.close()
        stderr = open('error')
        errors = stderr.read().strip()
        stderr.close()
        if errors:
            fail = BotFail(filename, error=errors)
            retry -= 1
            break
        file = open('command')
        command = file.read().strip()
        file.close()
        if validate(command):
            fail = BotFail(filename, invalid=True)
            retry -= 1
            break
    return fail or command

def tournament(bots, game, per_game=[2], t_type='ao'):
    """
    Run a set of games between the bots.
    Parameters:
    bots       - a list of competeing bots (filnames)
    game       - a function to be called with a list
                 of bots for that round. Should return
                 either a dictionary of filename: score,
                 a list of filenames ordered by position
                 (best first) or a single winning
                 filename
    per_game   - an iterable of intigers which represent
                 acceptable numbers of players per game
    t_type     - the type of tounament, which specifies
                 what rounds to play:
                 'a' - every possible combination.
                       modifier 'o' means that order
                       matters
                 'e' - minimum games so that everyone
                       plays the same number
                 's' - minimum so that everyone has
                       played x times. modify with number
                       'x', eg. s3, s62
                 'g' - run it in near-even groups,
                       then take the top x for the next
                       round. modify with number x.
    Returns a dictionary of filename: points
    """
    scores = {}
    for b in bots:
        scores[b] = 0
    for a in bots:
        for b in bots:
            if a != b:
                scores[round_(a, b)] += 1
    return scores
    ### above is for defaults only, FIXME


def table(scores):
    """
    Create a table of results. Works best with return
    from tournament function. Filenames should be in
    form 'botname__username.foo'.
    """
    names = sorted(list(scores), key=lambda x: scores[x], reverse=True)
    table = '''name                |creator             |score
    --------------------+--------------------+-----'''
    for i in names:
        name = ''.join(i.split('__')[:-1])
        if len(name) > 20:
            pname = name[:17] + '...'
        else:
            pname = name + ' '*(20-len(name))
        make = ''.join(''.join(i.split('__')[-1]).split('.')[:-1])
        if len(make) > 20:
            pmake = make[:17] + '...'
        else:
            pmake = make + ' '*(20-len(make))
        table += '\n' + pname + '|' + pmake + '|', scores[i]
    return table

def setup():
    bots = os.listdir('bots')

     
