#!/bin/bash
# Display window title as iTerm badge temporarily
set_iterm_badge() {
  printf "\ePtmux;\e\e]1337;SetBadgeFormat=%s\a\e\\" $(echo -n "$*" | base64)
}
WINDOW_NAME=$(\
  tmux list-panes -t ${TMUX_PANE} -F "#{pane_id} #{window_name}" | \
  grep -e "^${TMUX_PANE}" | cut -d ' ' -f 2-)
echo "Window name: $WINDOW_NAME"
set_iterm_badge "$WINDOW_NAME"
sleep 2
set_iterm_badge ""
