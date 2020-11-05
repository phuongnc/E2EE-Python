ARG=$1
if [ ${#ARG} -gt 0 ]; then
    if [ $ARG == '-g' ] || [ $ARG == '-group' ]; then
      echo '~~~~~ Build docker GRPC Signal Group ~~~~~'
      docker build --no-cache -t group-signalc -f ./.docker/Dockerfile .
      echo '~~~~~ Build Success. Start running ~~~~~'
      docker run --env SERVER_TYPE=group --env PORT=50052 --name group-signalc -p 50052:50052 group-signalc
    else
      echo '~~~~~ Build docker GRPC Signal Peer2Peer ~~~~~'
      docker build --no-cache -t peer-signalc -f ./.docker/Dockerfile .
      echo '~~~~~ Build Success. Start running ~~~~~'
      docker run --env SERVER_TYPE=p2p --env PORT=50051 --name peer-signalc -p 50051:50051 peer-signalc
    fi
else
    echo '~~~~~ Build Failed. Missing argument: -p (peer to peer) or -g (group) ~~~~~'
fi