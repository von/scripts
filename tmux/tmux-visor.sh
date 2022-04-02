#!/usr/bin/env bash
# Toggle marked pane as a visor in tmux

if test $(tmux display-message -p '#{window_marked_flag}') == "1" ; then
  #  Marked pane is in current window, so we are sending it away.
  # -d == don't make new window the default
  # The 'brake-pane' clears the mark, hence the re-set
  id=$(tmux break-pane -d -n visor -s '{marked}' -P -F "#{pane_id}")
  tmux select-pane -t ${id} -m
else
  if test $(tmux display-message -p '#{pane_marked_set}') == "1" ; then
    # The 'join-pane' clears the mark, hence the re-set
    tmux join-pane \; select-pane -m
  else
    # No marked pane exists, create one and mark it
    tmux split-pane \; select-pane -m
  fi
fi
exit 0
