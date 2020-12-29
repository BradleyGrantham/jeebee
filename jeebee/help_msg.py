help_msg = """
--------
__**Accept a GB Variant; S&D Best of 3**__
`jeebee accept player1 player2 player3`
- *the players must be gamebattles usernames - case doesn't matter*
- *if you only want kbm matches, add `kbm` to the end*
- *it will pick the match with the lowest dispute rate*

__**Post a GB Variant; S&D Best of 3**__
`jeebee post player1 player2 player3`
- *same caveats as above*

__**Report the last match**__
`jeebee report win`
- *anything other than `{"w", "win", "wi", "victory", "dub"}` will be reported as a loss

__**List available matches**__
`jeebee find`
- *finds gb variant s&d matches*
- *add `kbm` to limit to just kbm matches*
- *or add `all` to show all matches*

__**Show any active matches**__
`jeebee match`

__**Show last match**__
`jeebee match last`

__**Show win percentage**__
`jeebee win-perc`
- *by default this shows the win percentage over all games*
- *add a number after to limit to a certain number of games*
--------
"""
