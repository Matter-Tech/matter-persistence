if [[ $(which python) == *"matter-persistence"* ]]; then
  "$@"
else
  hatch run "$@"
fi
exit $?