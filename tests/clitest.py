from epydocutil import TerminalController 
import sys

term = TerminalController()

percent = 0.40
message = "We are great"
background = "." * 80
dots = int(len(background)  * percent)

sys.stdout.write(term.CLEAR_LINE + '%3d%% '%(100*percent) + term.GREEN + '[' + term.BOLD + '='*dots + background[dots:] + term.NORMAL + term.GREEN + '] ' + term.NORMAL + message + term.BOL) 
sys.stdout.flush()
raw_input()
