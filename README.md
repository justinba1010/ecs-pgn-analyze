# Chess Stockfish Tool

Analyze Bulk Games with Stockfish

1. Build Image

`docker buildx build --platform linux/amd64 . -t stockfish_amd64`

2. Tag Image

Use Your AWS Region
`docker tag stockfish_amd64:latest {aws_account_id}.dkr.ecr.us-east-1.amazonaws.com/stockfish:latest`

3. Upload Image

`docker push 719534417516.dkr.ecr.us-east-1.amazonaws.com/stockfish:latest`

4. For a Fargate Task Defintion
  a. Create Task Role (read only of directory for your pgns uploaded to s3)
  b. Create Task Definition

5. Example Kick off Task (Example
  a. With games in pgn folder

```
aws ecs run-task --task-definition Stockfish --launch-type=FARGATE --cluster ${cluster_name} --overrides '{"containerOverrides": [{"name":"container", "cpu": 8192, "memory": 16384, "command": ["--depth=15", "--hash=14336", "--threads=16", "--file=agames.pgn", "--ecs=true"]}], "cpu": "8192", "memory": "16384"}' --network-configuration='{"awsvpcConfiguration": {"subnets": ["{substitute}"], "securityGroups": ["{substitute}"], "assignPublicIp": "ENABLED"}}'
```

or for a pgn file loaded from lichess:

```
aws ecs run-task --task-definition Stockfish --launch-type=FARGATE --cluster Justin --overrides '{"containerOverrides": [{"name":"container", "cpu": 8192, "memory": 16384, "command": ["--depth=15", "--hash=14336", "--threads=16", "--url", "https://lichess.org/game/export/it94rdk5?evals=0&clocks=0"]}], "cpu": "8192", "memory": "16384"}' --network-configuration='{"awsvpcConfiguration": {"subnets": ["{substitute}"], "securityGroups": ["{substitute}"], "assignPublicIp": "ENABLED"}}'
```

6. Get Annotated PGN (Example)

```
aws logs get-log-events --log-group-name /ecs/Stockfish --log-stream-name ecs/container/deebe83dbba14ec5bf301770fc445634 | jq -r '.events[] | .message' 
[Event "≤2000 Blitz Arena"]
[Site "https://lichess.org/it94rdk5"]
[Date "2022.12.24"]
[Round "?"]
[White "Justinba1010"]
[Black "ST009"]
[Result "1-0"]
[BlackElo "1862"]
[BlackRatingDiff "-10"]
[ECO "C44"]
[Opening "Scotch Game: Lolli Variation"]
[Termination "Normal"]
[TimeControl "180+2"]
[UTCDate "2022.12.24"]
[UTCTime "01:53:54"]
[Variant "Standard"]
[WhiteElo "1489"]
[WhiteRatingDiff "+11"]
[ZA_White_Accuracy "0.761"]
[ZB_Black_Accuracy "0.627"]
1. e4 Nc6 2. Nf3 e5 3. d4 Nxd4 4. Nxd4 exd4 5. Qxd4 Qf6 6. e5 Qf5 { Blunder; Accuracy: 0.45 } 7. Bd3 Qe6 8. O-O c5 { Blunder; Accuracy: 0.48 } 9. Qc4 Qxc4 10. Bxc4 a6 11. a4 Ne7 12. Be3 Nc6 13. f4 Nb4 14. Bb3 { Blunder; Accuracy: 0.19 } 14... d5 { Blunder; Accuracy: 0.30 } 15. exd6 Bxd6 16. c3 Nd3 17. Rd1 Bf5 { Blunder; Accuracy: 0.46 } 18. Bc2 { Blunder; Accuracy: 0.48 } 18... c4 { Blunder; Accuracy: 0.43 } 19. Ra2 { Blunder; Accuracy: 0.23 } 19... Be7 { Blunder; Accuracy: 0.48 } 20. Na3 Nxb2 21. Rd2 Bxa3 { Blunder; Accuracy: 0.06 } 22. Bxf5 O-O 23. Rxa3 Nd3 24. Bxd3 cxd3 25. Rxd3 Rfe8 26. Bf2 Rad8 27. Rxd8 Rxd8 28. Bb6 Rd1+ 29. Kf2 Rb1 30. a5 f6 31. Ra4 Rb3 32. c4 Kf7 33. c5 Ke6 34. Re4+ Kd5 35. Re3 Rb4 36. Kf3 f5 37. g3 Kc4 38. Re7 Rb3+ 39. Kg2 Rb2+ 40. Kh3 Kd3 41. Rxb7 Ke3 42. Rxg7 Kf3 43. c6 Rc2 44. c7 Rc1 45. Rg8 Ke2 46. c8=Q Rh1 47. Qc4+ Kf3 1-0
```
