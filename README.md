# jeebee
---

## Build and run
```
rsync -e "ssh -i Downloads/bradley.pem" -avzr repos/discord-gb.gg/ ubuntu@54.246.79.130:~/discord-gb.gg/
ssh ubuntu@54.246.79.130 -i Downloads/bradley.pem
cd discord-gb.gg/
sudo docker build -t bot . && docker run -itd bot
```