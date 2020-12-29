# jeebee
---

## Build and run
```
rsync -e "ssh -i Downloads/bradley.pem" -avzr repos/discord-gb.gg/ ubuntu@54.246.79.130:~/discord-gb.gg/
ssh ubuntu@54.246.79.130 -i Downloads/bradley.pem
cd discord-gb.gg/
sudo docker build -t bot . && docker run -itd bot
```

## TODO
- [ ] Change prints to logs
- [ ] Log more stuff
- [ ] Cancel games
- [ ] @ people when a game is found
- [ ] Use peoples discord usernames to find a match
- [ ] If we have posted a match but a similar one gets posted, remove our post
and accept the other one
