# Fabric on two organizations
Hyperledger Fabricの2.4.0で動かす想定です

# test.py
２つの組織でのテストを行うためのスクリプト．
- チェーンコードの実行
- ブロック情報の取得

## 使い方
`peer_address`，`tls_cert_path`，`channel_name`，`chaincode_name`，`query_key`を適切に設定する．
fabricのバージョンは2.4.0の想定だが，別のバージョンを使用する場合はpeerコマンドのオプションが変わっている可能性があるため，適宜変更する（https://hyperledger-fabric.readthedocs.io/en/release-1.3/peer-commands.html）．

実行結果のサンプルについては，`test_result_sample.txt`を参照．

# ネットワーク構築手順
Dockerの操作については`Docker操作メモ`を参照

## 前提条件
- Ubuntu 2台
- Docker
- Git
- Go

## 下準備

以下を両方のマシンにクローン

```bash
git clone git@github.com:tkkwa01/fabric_on_2org.git
```

## Docker Swarmの準備

VM1で以下を実行しSwarmを初期化
```bash
$ docker swarm init  --advertise-addr 10.1.140.1

Swarm initialized: current node (fqkmevpug6y2yshu3v703v0d0) is now a manager.

To add a worker to this swarm, run the following command:

    docker swarm join --token SWMTKN-1-2g2nfysn7m50cu0mix3qvx5ubsm9y44ngamk5ohdpdwpwjxu33-a9hsyml3zvdn43c9zgxqyo5ts 10.1.140.1:2377

To add a manager to this swarm, run 'docker swarm join-token manager' and follow the instructions.
```

マネージャとして参加させるためのトークンを生成

```bash
$ docker swarm join-token manager
To add a manager to this swarm, run the following command:

    docker swarm join --token SWMTKN-1-0vj7ida1xraigpqjahkvgb76ngrg8608oy9v1yizkd0rk4gact-emr96hzkm1uwpciww0j7xhojv 10.1.140.1:2377
```

VM2で以下を実行し，Swarmに参加（上の出力のコマンド）

```bash
docker swarm join --token SWMTKN-1-0vj7ida1xraigpqjahkvgb76ngrg8608oy9v1yizkd0rk4gact-emr96hzkm1uwpciww0j7xhojv 10.1.140.1:2377
```

VM1で以下のコマンドを実行

```bash
docker network create  --driver overlay   --attachable first-network
```

以下のコマンドをVM1と2で実行し，正常に参加できていることを確認

```bash
$ docker network ls

NETWORK ID     NAME              DRIVER    SCOPE
zpazjk64rhw3   first-network     overlay   swarm
```

## ネットワーク作成

VM1上で，以下２つを実行

```bash
./host1up.sh
./host2up.sh
```

以下で出力を確認する

```bash
$ docker ps

CONTAINER ID   IMAGE                               COMMAND             CREATED              STATUS          PORTS                                                     NAMES
c2483a9f8a1b   hyperledger/fabric-peer:latest      "peer node start"   40 seconds ago       Up 32 seconds   7051/tcp, 0.0.0.0:8051->8051/tcp, :::8051->8051/tcp       peer1.org1.example.com
50098714ce03   hyperledger/fabric-orderer:latest   "orderer"           40 seconds ago       Up 32 seconds   7050/tcp, 0.0.0.0:8050->8050/tcp, :::8050->8050/tcp       orderer2.example.com
882380f987ea   hyperledger/fabric-tools:latest     "/bin/bash"         About a minute ago   Up 45 seconds                                                             cli
f37ce80321b6   hyperledger/fabric-orderer:latest   "orderer"           About a minute ago   Up 59 seconds   7050/tcp, 0.0.0.0:11050->11050/tcp, :::11050->11050/tcp   orderer5.example.com
d77b7d210e43   hyperledger/fabric-peer:latest      "peer node start"   About a minute ago   Up 54 seconds   0.0.0.0:7051->7051/tcp, :::7051->7051/tcp                 peer0.org1.example.com
cb1ccfc51ad9   hyperledger/fabric-orderer:latest   "orderer"           About a minute ago   Up 57 seconds   0.0.0.0:7050->7050/tcp, :::7050->7050/tcp                 orderer.example.com

```

VM2で以下を実行

```bash
./host3up.sh
./host4up.sh
```

出力を確認

```bash
$ docker ps

CONTAINER ID   IMAGE                               COMMAND             CREATED         STATUS              PORTS                                                     NAMES
bb57018733b0   hyperledger/fabric-peer:latest      "peer node start"   2 minutes ago   Up About a minute   7051/tcp, 0.0.0.0:10051->10051/tcp, :::10051->10051/tcp   peer1.org2.example.com
41cf0de105e6   hyperledger/fabric-orderer:latest   "orderer"           2 minutes ago   Up About a minute   7050/tcp, 0.0.0.0:10050->10050/tcp, :::10050->10050/tcp   orderer4.example.com
fc6ae503c96c   hyperledger/fabric-orderer:latest   "orderer"           2 minutes ago   Up 2 minutes        7050/tcp, 0.0.0.0:9050->9050/tcp, :::9050->9050/tcp       orderer3.example.com
b71aa60235f3   hyperledger/fabric-peer:latest      "peer node start"   2 minutes ago   Up 2 minutes        7051/tcp, 0.0.0.0:9051->9051/tcp, :::9051->9051/tcp       peer0.org2.example.com
```

### 注意事項

ここで docker ps -aをした結果`Exited (2)` が出るようなら，一度dockerを全て落としてやり直す．コンテナを全て停止，コンテナを全て削除，全てのボリュームの削除をする．

**`Exited (2)`を無視して先に進めることはできない．**

## チャネル作成

チャネルを作る(VPS1)

```bash
$ ./mychannelup.sh 

2024-12-12 10:42:50.768 UTC 0001 INFO [channelCmd] InitCmdFactory -> Endorser and orderer connections initialized
2024-12-12 10:42:50.830 UTC 0002 INFO [cli.common] readBlock -> Expect block, but got status: &{NOT_FOUND}
2024-12-12 10:42:50.841 UTC 0003 INFO [channelCmd] InitCmdFactory -> Endorser and orderer connections initialized
2024-12-12 10:42:51.044 UTC 0004 INFO [cli.common] readBlock -> Expect block, but got status: &{NOT_FOUND}
2024-12-12 10:42:51.057 UTC 0005 INFO [channelCmd] InitCmdFactory -> Endorser and orderer connections initialized
2024-12-12 10:42:51.259 UTC 0006 INFO [cli.common] readBlock -> Expect block, but got status: &{NOT_FOUND}
2024-12-12 10:42:51.271 UTC 0007 INFO [channelCmd] InitCmdFactory -> Endorser and orderer connections initialized
2024-12-12 10:42:52.348 UTC 0008 INFO [cli.common] readBlock -> Expect block, but got status: &{SERVICE_UNAVAILABLE}
2024-12-12 10:42:52.358 UTC 0009 INFO [channelCmd] InitCmdFactory -> Endorser and orderer connections initialized
2024-12-12 10:42:52.561 UTC 000a INFO [cli.common] readBlock -> Expect block, but got status: &{SERVICE_UNAVAILABLE}
2024-12-12 10:42:52.569 UTC 000b INFO [channelCmd] InitCmdFactory -> Endorser and orderer connections initialized
2024-12-12 10:42:52.772 UTC 000c INFO [cli.common] readBlock -> Expect block, but got status: &{SERVICE_UNAVAILABLE}
2024-12-12 10:42:52.780 UTC 000d INFO [channelCmd] InitCmdFactory -> Endorser and orderer connections initialized
2024-12-12 10:42:52.983 UTC 000e INFO [cli.common] readBlock -> Expect block, but got status: &{SERVICE_UNAVAILABLE}
2024-12-12 10:42:52.992 UTC 000f INFO [channelCmd] InitCmdFactory -> Endorser and orderer connections initialized
2024-12-12 10:42:53.195 UTC 0010 INFO [cli.common] readBlock -> Expect block, but got status: &{SERVICE_UNAVAILABLE}
2024-12-12 10:42:53.203 UTC 0011 INFO [channelCmd] InitCmdFactory -> Endorser and orderer connections initialized
2024-12-12 10:42:53.408 UTC 0012 INFO [cli.common] readBlock -> Expect block, but got status: &{SERVICE_UNAVAILABLE}
2024-12-12 10:42:53.417 UTC 0013 INFO [channelCmd] InitCmdFactory -> Endorser and orderer connections initialized
2024-12-12 10:42:53.625 UTC 0014 INFO [cli.common] readBlock -> Received block: 0
2024-12-12 10:42:59.403 UTC 0001 INFO [channelCmd] InitCmdFactory -> Endorser and orderer connections initialized
2024-12-12 10:43:01.880 UTC 0002 INFO [channelCmd] executeJoin -> Successfully submitted proposal to join channel
2024-12-12 10:43:02.296 UTC 0001 INFO [channelCmd] InitCmdFactory -> Endorser and orderer connections initialized
2024-12-12 10:43:04.984 UTC 0002 INFO [channelCmd] executeJoin -> Successfully submitted proposal to join channel
2024-12-12 10:43:05.400 UTC 0001 INFO [channelCmd] InitCmdFactory -> Endorser and orderer connections initialized
2024-12-12 10:43:06.162 UTC 0002 INFO [channelCmd] executeJoin -> Successfully submitted proposal to join channel
2024-12-12 10:43:06.572 UTC 0001 INFO [channelCmd] InitCmdFactory -> Endorser and orderer connections initialized
2024-12-12 10:43:07.473 UTC 0002 INFO [channelCmd] executeJoin -> Successfully submitted proposal to join channel
2024-12-12 10:43:07.872 UTC 0001 INFO [channelCmd] InitCmdFactory -> Endorser and orderer connections initialized
2024-12-12 10:43:07.911 UTC 0002 INFO [channelCmd] update -> Successfully submitted channel update
2024-12-12 10:43:08.360 UTC 0001 INFO [channelCmd] InitCmdFactory -> Endorser and orderer connections initialized
2024-12-12 10:43:08.405 UTC 0002 INFO [channelCmd] update -> Successfully submitted channel update
```

チャネルが作られたことを確認する(VPS1)

```bash
$ docker exec cli peer channel list

2024-12-12 10:43:22.359 UTC 0001 INFO [channelCmd] InitCmdFactory -> Endorser and orderer connections initialized
Channels peers has joined: 
mychannel
```

台帳を確認する(VPS1)

```bash
$ docker exec peer0.org1.example.com peer channel getinfo -c mychannel

2024-12-12 10:43:44.876 UTC 0001 INFO [channelCmd] InitCmdFactory -> Endorser and orderer connections initialized
Blockchain info: {"height":3,"currentBlockHash":"1hO4oKOm+lKNTj1MaK/jcb0vRIfZAI6A7QDJLt9TIv0=","previousBlockHash":"6W2/F1oi0u3K2zbfRBRpS9h2M+Q/HMyDmQUOwVhUhlU="}
```

VPS2で台帳が同期されていることを確認する

```bash
$ docker exec peer0.org2.example.com peer channel getinfo -c mychannel

2024-12-12 10:43:53.527 UTC 0001 INFO [channelCmd] InitCmdFactory -> Endorser and orderer connections initialized
Blockchain info: {"height":3,"currentBlockHash":"1hO4oKOm+lKNTj1MaK/jcb0vRIfZAI6A7QDJLt9TIv0=","previousBlockHash":"6W2/F1oi0u3K2zbfRBRpS9h2M+Q/HMyDmQUOwVhUhlU="}
```

## チェーンコード

チェインコードサンプルをクローンする

```bash
git clone git@github.com:novrian6/chaincode_hyperledger.git
```

フォルダ名を `chaincode` に変更し，一つ上のディレクトリに移動させる

chaincodeディレクトリの場所の指定があるので `host1.yaml`の以下の箇所を環境に合わせて変更する

```bash
volumes:
        - /var/run/:/host/var/run/
        - /home/チェーンコードを置いている場所/chaincode/:/opt/gopath/src/github.com/chaincode
```

例えば，

```bash
user名
├── test
│   ├── chaincode
│   │   ├─asset-transfer-basic
│   │     ├─chaincode-go
│   │  
│   ├── multihost_2org_hyperledger
```

のようなディレクトリ構成の場合，

```bash
/home/user名/test/chaincode/:/opt/gopath/src/github.com/chaincode
```

のようになる

`chaincode/asset-transfer-basic/chaincode-go` に移動し，以下のコマンドを実行する

```bash
GO111MODULE=on go mod vendor
```

`chaincode/asset-transfer-basic/chaincode-go` 内で以下のコマンドを実行

```bash
docker exec cli peer lifecycle chaincode package basic1.tar.gz --label basic1 --path /opt/gopath/src/github.com/chaincode/asset-transfer-basic/chaincode-go
```

`docker exec -it cli bash` を実行し，コンテナ内でlsコマンドをうち，以下のようになっていれば正しい

```bash
bash-5.1# ls

basic1.tar.gz      channel-artifacts  crypto             scripts
```

`exit` と入力してコンテナから抜ける

チェーンコードをインストールする

```bash
$ docker exec cli peer lifecycle chaincode install basic1.tar.gz

2024-12-12 12:11:38.815 UTC 0001 INFO [cli.lifecycle.chaincode] submitInstallProposal -> Installed remotely: response:<status:200 payload:"\nGbasic1:87aaa46d2ace4f5c4f17b69c151adc1e3cedf5edcb09e4358f57ce7c5ece25fa\022\006basic1" > 
2024-12-12 12:11:38.816 UTC 0002 INFO [cli.lifecycle.chaincode] submitInstallProposal -> Chaincode code package identifier: basic1:87aaa46d2ace4f5c4f17b69c151adc1e3cedf5edcb09e4358f57ce7c5ece25fa
```

`basic1:87aaa46d2ace4f5c4f17b69c151adc1e3cedf5edcb09e4358f57ce7c5ece25fa` はメモしとく

VPS2にもチェーンコードをインストールするが，VPS1上で実行する

以下のコマンド

```bash
$ docker exec  -e CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org2.example.com/users/Admin@org2.example.com/msp  -e CORE_PEER_ADDRESS=peer0.org2.example.com:9051 -e CORE_PEER_LOCALMSPID=Org2MSP -e CORE_PEER_TLS_ROOTCERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt cli peer lifecycle chaincode install basic1.tar.gz

2024-12-12 12:19:33.369 UTC 0001 INFO [cli.lifecycle.chaincode] submitInstallProposal -> Installed remotely: response:<status:200 payload:"\nGbasic1:87aaa46d2ace4f5c4f17b69c151adc1e3cedf5edcb09e4358f57ce7c5ece25fa\022\006basic1" > 
2024-12-12 12:19:33.370 UTC 0002 INFO [cli.lifecycle.chaincode] submitInstallProposal -> Chaincode code package identifier: basic1:87aaa46d2ace4f5c4f17b69c151adc1e3cedf5edcb09e4358f57ce7c5ece25fa

```

以下のコマンドで，出力を確認(VPS1, 2)

```bash
$ docker images dev-*

REPOSITORY                                                                                                                                                            TAG       IMAGE ID       CREATED          SIZE
dev-peer0.org1.example.com-basic1-87aaa46d2ace4f5c4f17b69c151adc1e3cedf5edcb09e4358f57ce7c5ece25fa-dfebd90cdb1767ef7a6d4075ed2f55f2b9f99b267fed207bff4de5748bed79a1   latest    d97633688247   21 minutes ago   23.5MB
```

さっきメモした文字列と一致すると思う

### チェーンコード承認

承認ステータスを確認する(VPS1)

```bash
$ docker exec cli peer lifecycle chaincode checkcommitreadiness --channelID mychannel --name basic1 --version 1 --sequence 1

Chaincode definition for chaincode 'basic1', version '1', sequence '1' on channel 'mychannel' approval status by org:
Org1MSP: false
Org2MSP: false
```

以下のコードで組織１でチェーンコードを承認する(VPS1)

IDはさっきメモした文字列に置き換えてください

```bash
$ docker exec cli peer lifecycle chaincode approveformyorg --tls --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem --channelID mychannel --name basic1 --version 1 --sequence 1 --waitForEvent --package-id basic1:87aaa46d2ace4f5c4f17b69c151adc1e3cedf5edcb09e4358f57ce7c5ece25fa

2024-12-12 13:01:34.436 UTC 0001 INFO [cli.lifecycle.chaincode] setOrdererClient -> Retrieved channel (mychannel) orderer endpoint: orderer.example.com:7050
2024-12-12 13:01:38.701 UTC 0002 INFO [chaincodeCmd] ClientWait -> txid [bd78ba20ac8ecb5701853597c1c3740d8787c6b40e4be74c60a0b790e7121a71] committed with status (VALID) at peer0.org1.example.com:7051
```

同じく組織2で承認する(VPS1)

```bash
$ docker exec -e CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org2.example.com/users/Admin@org2.example.com/msp -e CORE_PEER_ADDRESS=peer0.org2.example.com:9051 -e CORE_PEER_LOCALMSPID=Org2MSP -e CORE_PEER_TLS_ROOTCERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt cli peer lifecycle chaincode approveformyorg --tls --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem --channelID mychannel --name basic1 --version 1 --sequence 1 --waitForEvent --package-id basic1:87aaa46d2ace4f5c4f17b69c151adc1e3cedf5edcb09e4358f57ce7c5ece25fa

2024-12-12 13:04:56.115 UTC 0001 INFO [cli.lifecycle.chaincode] setOrdererClient -> Retrieved channel (mychannel) orderer endpoint: orderer.example.com:7050
2024-12-12 13:04:59.277 UTC 0002 INFO [chaincodeCmd] ClientWait -> txid [91185025782d07d43fcff548c237172c1d98876d49981f8ac76c47e6c9795197] committed with status (VALID) at peer0.org2.example.com:9051
```

もう一度承認ステータスを確認

```bash
$ docker exec cli peer lifecycle chaincode checkcommitreadiness --channelID mychannel --name basic1 --version 1 --sequence 1

Chaincode definition for chaincode 'basic1', version '1', sequence '1' on channel 'mychannel' approval status by org:
Org1MSP: true
Org2MSP: true
```

下２つが `true`に変わっていることを確認

チェーンコードをチャンネルにコミット(VPS1)

```bash
$ docker exec cli peer lifecycle chaincode commit -o orderer.example.com:7050 --tls --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem --peerAddresses peer0.org1.example.com:7051 --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt --peerAddresses peer0.org2.example.com:9051 --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt --channelID mychannel --name basic1 --version 1 --sequence 1

2024-12-12 13:07:29.020 UTC 0001 INFO [chaincodeCmd] ClientWait -> txid [a1a4e7cd144a1973d08bd6c3d1ede0d5df21b89861809353138439e5d0341277] committed with status (VALID) at peer0.org2.example.com:9051
2024-12-12 13:07:29.172 UTC 0002 INFO [chaincodeCmd] ClientWait -> txid [a1a4e7cd144a1973d08bd6c3d1ede0d5df21b89861809353138439e5d0341277] committed with status (VALID) at peer0.org1.example.com:7051
```

コミットステータスを確認

```bash
$ docker exec cli peer lifecycle chaincode querycommitted --channelID mychannel --name basic1

Committed chaincode definition for chaincode 'basic1' on channel 'mychannel':
Version: 1, Sequence: 1, Endorsement Plugin: escc, Validation Plugin: vscc, Approvals: [Org1MSP: true, Org2MSP: true]
```

### チェーンコードのテスト

InitLedgerという，台帳を初期化するチェーンコードを呼び出す

```bash
$ docker exec cli peer chaincode invoke -o orderer5.example.com:11050 --tls true --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer5.example.com/msp/tlscacerts/tlsca.example.com-cert.pem -C mychannel -n basic1 --peerAddresses peer0.org1.example.com:7051 --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt --peerAddresses peer0.org2.example.com:9051 --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt -c '{"Args":["initLedger"]}'

2024-12-12 13:11:08.579 UTC 0001 INFO [chaincodeCmd] chaincodeInvokeOrQuery -> Chaincode invoke successful. result: status:200 
```

GetAllAssetsを呼び出す

```bash
$ docker exec cli peer chaincode invoke -o orderer5.example.com:11050 --tls true --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer5.example.com/msp/tlscacerts/tlsca.example.com-cert.pem -C mychannel -n basic1 --peerAddresses peer0.org1.example.com:7051 --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt --peerAddresses peer0.org2.example.com:9051 --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt -c '{"Args":["GetAllAssets"]}'

2024-12-12 13:11:33.033 UTC 0001 INFO [chaincodeCmd] chaincodeInvokeOrQuery -> Chaincode invoke successful. result: status:200 payload:"[{\"AppraisedValue\":300,\"Color\":\"blue\",\"ID\":\"asset1\",\"Owner\":\"Tomoko\",\"Size\":5},{\"AppraisedValue\":400,\"Color\":\"red\",\"ID\":\"asset2\",\"Owner\":\"Brad\",\"Size\":5},{\"AppraisedValue\":500,\"Color\":\"green\",\"ID\":\"asset3\",\"Owner\":\"Jin Soo\",\"Size\":10},{\"AppraisedValue\":600,\"Color\":\"yellow\",\"ID\":\"asset4\",\"Owner\":\"Max\",\"Size\":10},{\"AppraisedValue\":700,\"Color\":\"black\",\"ID\":\"asset5\",\"Owner\":\"Adriana\",\"Size\":15},{\"AppraisedValue\":800,\"Color\":\"white\",\"ID\":\"asset6\",\"Owner\":\"Michel\",\"Size\":15}]" 
```

CreateAsset

```bash
$ docker exec cli peer chaincode invoke -o orderer5.example.com:11050 --tls true --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer5.example.com/msp/tlscacerts/tlsca.example.com-cert.pem -C mychannel -n basic1 --peerAddresses peer0.org1.example.com:7051 --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt --peerAddresses peer0.org2.example.com:9051 --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt -c '{"Args":["CreateAsset", "testasset", "SomeOwner", "100", "SomeDescription", "1633036800"]}'

2024-12-12 13:22:25.075 UTC 0001 INFO [chaincodeCmd] chaincodeInvokeOrQuery -> Chaincode invoke successful. result: status:200 
```

ReadAsset

キーに基づいたデータを表示させる

```bash
$ docker exec cli peer chaincode query -C mychannel -n basic1 -c '{"Args":["ReadAsset","asset1"]}' --peerAddresses peer0.org1.example.com:7051 --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt

{"AppraisedValue":300,"Color":"blue","ID":"asset1","Owner":"Tomoko","Size":5}
```

# Docker操作メモ
とりあえず全部破壊してやり直したくなったら以下を参考に実行してください

### 全てのコンテナを停止

```bash
docker stop $(docker ps -a -q)
```

### 全てのコンテナを削除

```bash
docker rm $(docker ps -a -q)
```

### 全てのイメージを削除

```bash
docker rmi -f $(docker images -q)
```

### 全てのボリュームを削除

```bash
docker volume rm $(docker volume ls -q)
```

### ネットワーク削除

```bash
docker network prune -f
```

### Swarmを抜ける

```bash
docker swarm leave --force
```

### 再起動

```bash
sudo systemctl restart docker
```

