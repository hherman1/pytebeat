#!/usr/bin/python
# -*- coding: utf-8 -*-
# next items:
# - an SDL one-line text editor so I can dump Tkinter!
# - vertical waveform display
# - integer object has no attribute astype
# - improve parse errors

import sys, wave, os, time, subprocess, pygame, shuntparse, Numeric, sdltextfield

rate = 8000

current_formula = None
t = 0
interval = 33
last_time = start = time.time() + 1
    
def run_mainloop(error, formula, outfd, screen):
    global current_formula, t, last_time, start

    needed = int(min(rate * (time.time() - start + 1.5*interval/1000.0) - t,
                     3 * interval / 1000.0 * rate))
        
    while needed % 8 != 0:
        needed += 1
    print time.time() - last_time, needed

    try:
        current_formula = shuntparse.parse(shuntparse.tokenize(formula.text))
    except:
        _, exc, _ = sys.exc_info()
        error.text=repr(exc)
    else:
        error.text=''

    output = ''

    try:
        output = current_formula.eval({'t': Numeric.arange(t, t+needed)}).astype(Numeric.UInt8).tostring()
        t += needed
    except:
        error.text=str(sys.exc_info()[1])
    
    event = pygame.event.poll()
    if event.type in [pygame.QUIT, pygame.MOUSEBUTTONDOWN]:
        sys.exit()
    elif event.type == pygame.KEYDOWN:
        formula.handle_key(event)
    elif event.type == pygame.NOEVENT:
        screen.fill(0)
        formula.draw(screen)
        error.draw(screen)

        if len(output) > 1:
            pygame.draw.lines(screen, (255, 255, 255), False,
                              list(enumerate(map(ord, output))))
        pygame.display.flip()

    outstart = time.time()
    outfd.write(output)
    outfd.flush()
    last_time = time.time()

    # hacky kludge to keep us from getting too far behind if for some
    # reason the audio output isn’t draining fast enough
    if last_time - outstart > interval * 0.1:
        print "buffer overrun of %f" % (last_time - outstart)
        start += (last_time - outstart) / 2

def make_window():
    outfd = open('/dev/dsp', 'w')
    pygame.init()
    screen = pygame.display.set_mode((0, 0))
    formula = sdltextfield.TextField((10, 266))
    formula.text = 'a = t * (t>>10 & 42), t >> 4'
    #entry = Tkinter.Entry(window, textvariable=formula, font='Monospace 32', background=bg, foreground='blue', insertbackground='blue')
    error = sdltextfield.TextField((10, 300))
    #error = Tkinter.Label(window, font='VeraSans 32', background=bg, foreground='red')
    while True:
        run_mainloop(error, formula, outfd, screen)
        pygame.time.delay(interval)

if __name__ == '__main__':
    make_window()
