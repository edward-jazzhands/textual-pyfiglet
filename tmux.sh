#!/bin/bash

# Use `just tmux` to set permissions and run this script.

# This script is designed for a terminal that is maximized on a wide screen.
# It will, with a single command:
# - Starts a new tmux session (or uses current one if already in tmux)
# - Splits the window horizontally (left and right panes)
# - Adjusts the width of the panes to be roughly 2/3 and 1/3 of the screen
# - Runs the textual dev console on the right (small) side
# - Runs the textual app on the left (large) side in dev mode
# - Focuses on the left pane so that the app starts focused
# - Attaches to the tmux session if not already in one

if [ -n "$TMUX" ]; then

    @echo "Already inside tmux. Please detach first."

else
    # Not inside tmux, create a new session
    
    # Start a new tmux session named "textual_session"
    # -d is for detached mode, -s is for session name 'textual_session_1'
    tmux new-session -d -s textual_session_1    

    # Rename the first window
    tmux rename-window -t textual_session_1:0 'Main'

    # Split the window horizontally
    tmux split-window -h        

    # Resize the right pane to roughly 1/3 of screen width
    tmux resize-pane -t textual_session_1:0.1 -x 7   

    # Send keys to the right pane (console)
    tmux send-keys -t textual_session_1:0.1 'just console' C-m

    # Wait for console to boot
    sleep 2  

    # Send keys to the left pane (app)
    tmux send-keys -t textual_session_1:0.0 'just run-dev' C-m

    # Select left pane to focus on the app
    tmux select-pane -t textual_session_1:0.0

    # Attach to the new session
    tmux attach-session -t textual_session_1
fi