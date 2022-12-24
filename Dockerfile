FROM alpine:latest AS builder

# Install dependencies
RUN apk add --no-cache git g++ make

RUN git clone --depth 1 --branch sf_15 https://github.com/official-stockfish/Stockfish.git

WORKDIR /Stockfish/src
RUN echo "arch:$( uname -m )" \
&& case $( uname -m ) in \
  x86_64) \
    make build ARCH=x86-64-modern \
  ;; \
  aarch64) \
    make build ARCH=armv8 \
  ;; \
  armv7l) \
    make build ARCH=armv7 \
  ;; \
  ppc64le) \
    make build ARCH=ppc-64 \
  ;; \
  *) \
    exit 1 \
  ;; \
esac

FROM alpine:latest

RUN apk add --no-cache libstdc++ ucspi-tcp6 \
 && addgroup -g 1000 stockfish \
 && adduser -u 1000 -G stockfish -HD stockfish

WORKDIR /stockfish/
USER stockfish:stockfish

COPY --chown=stockfish:stockfish --from=builder /Stockfish/src/stockfish /stockfish/
COPY --chown=stockfish:stockfish --from=builder /Stockfish/Copying.txt /stockfish/
COPY --chown=stockfish:stockfish --from=builder /Stockfish/src/*.nnue /stockfish/

EXPOSE 23249

USER root:root

RUN apk add --no-cache python3 py3-pip

RUN pip3 install stockfish chess requests boto3
RUN touch /stockfish/logs
RUN chmod 777 /stockfish/stockfish
RUN chmod 777 /stockfish/logs
RUN touch /games.pgn && chmod 777 /games.pgn

USER stockfish:stockfish


COPY game.py /game.py
COPY command.py /command.py
#COPY models.py /usr/lib/python3.9/site-packages/stockfish/models.py

ENTRYPOINT ["python3", "/command.py"]
