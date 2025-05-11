# solace-demo-observability
Demo of the Solace PubSub+ monitoring and observability capabilities with focus on OpenTelemetry, using:

- Syslog Forwarding for logs
- Insights for monitoring metrics
- Distributed Tracing for opentelemetry based traces

Introduction
---
This Solace PubSub+ observability demo was initially based on work from my colleague Daniel Brunold [@dabgmx](https://www.github.com/dabgmx) and drew its inspiration from the Solace Codelabs. In addition it also makes use of some tips & tricks from another colleague Benjamin Gottstein [@benjamingottstein](https://github.com/benjamingottstein). Everything brought together by Emil Zegers [@taatuut](https://www.github.com/taatuut)

Background
---
In folder `docs` you find file `SolacePubSub+DistributedTracingDemo.pdf` describing the prerequisites and step-by-step setup, and file `SolacePubSub+DistributedTracingDemo.pdf` with an introduction on Solace PubSub+ Distributed Tracing.

Code
---
The code for this demo was developed on a Mac, should work on Linux too and hints are given for Windows where commands differ.

First step is to get the `solace-demo-observability` repo, e.g. using a code editor or in a terminal run:

`git clone https://github.com/SolaceLabs/solace-demo-observability.git`

Open the code in your favorite code editor like Visual Studio Code myself.

Run
---
This section provides a short summary to get everything running when the required components are available, make sure to follow the steps in document `docs/SolacePubSub+DistributedTracingDemo.pdf` first.

Open four terminals (using Terminal or something like iTerm). Create and set values for required environment variables for yaml file and SDKPerf in .env file, see sample.env file for neede variables. In every terminal run `source /path/to/.env`.

_Start Jaeger_

```
cd ~/jaeger/jaeger-1.53.0-darwin-amd64/
./jaeger-all-in-one
```

Or detached `nohup ./jaeger-all-in-one > /dev/null 2>&1 &`

To stop kill the process with `Control-C`.

In case you need to kill a detached process get pid for the port Jaeger is running on and then kill the process. For example for Mac and Linux:

```
sudo lsof -i tcp:4317
Password:
COMMAND     PID       USER   FD   TYPE             DEVICE SIZE/OFF NODE NAME
jaeger-al 52983 emilzegers   13u  IPv6 0x7abfc551d38db5d9      0t0  TCP *:4317 (LISTEN)
jaeger-al 52983 emilzegers   26u  IPv6 0x7abfc551d38dc5d9      0t0  TCP localhost:53137->localhost:4317 (ESTABLISHED)
jaeger-al 52983 emilzegers   27u  IPv6 0x7abfc551d38dcdd9      0t0  TCP localhost:4317->localhost:53137 (ESTABLISHED)
kill -15 52983
sudo lsof -i tcp:4317

```

Navigate to http://localhost:16686 to access the Jaeger UI.

_Start OTEL collector_

```
cd ~/otelcol/otelcol-contrib_0.96.0_darwin_arm64
./otelcol-contrib --config=../otel-collector-config-single.yaml
```

To stop kill the process with `Control-C`.

_Start 3.1	Solace SDKPerf_

SDKPerf acts as both publisher and consumer in this sertup. Topics and queues must be generated upfront, see documentation.

Run repeatedly every 10 seconds.

Run `source /path/to/.env`

```
cd ~/sdkperf/sdkperf-jcsmp-8.4.17.5
while true; do ./sdkperf_java.sh -cip=$SDKPERF_cip -cu=$SDKPERF_cu -cp=$SDKPERF_cp -ptl='demo/trace' -sql='queue-trace1,queue-trace2' -mt=persistent -mn=1 -mr=1 -msa=32768 -q -tsn="myTravel" -bag="destination=nice,country=france,datefrom=20240719,dateto-20240802,customerid=emilzegers@solace.com" -tcc -tcrc -tecip="http://localhost:4317"; sleep 10; done
```

To stop kill the process with `Control-C`.

_Start Python script for simple OTEL endpoint_

A simple OTEL endpoint in the form of a Python script that processes incoming POST requests with metrics in (gzipped) JSON from an otel collector exporter and just displays the data received.

`python3 simpleotelendpoint.py`

To stop kill the process with `Control-C`.

Navigate to http://localhost:3317 to view the received data (port is hardcoded in the Python script, change if necessary).

The script simpleotelendpoint.py displays data received in JSON format. See section `otlphttp/jsontest` in `my.aml` for the configuration of the exporter. Could work with protobuf too but then you need to know the format/schema so json is easier :-)

Need to use (at least?) version 0.96.0 of the OTEL Collector. Exporting JSON was not available in the 0.92.0 version of the OTEL Collector.

When hitting `UnicodeDecodeError: 'utf-8' codec can't decode byte 0x8b in position 1: invalid start byte` the data received is `gzip` compressed which is default (gzip's magic number is 0x1f 0x8b, consistent with above UnicodeDecodeError). To disable use `compression: none`, see https://github.com/open-telemetry/opentelemetry-collector/blob/main/exporter/otlphttpexporter/README.md or add decompressing to the code as an alternative.

To test the script:

Start script `python3 simpleotelendpoint.py`

GET request `http://localhost:3317/?test=ok`

POST request `curl -X POST -d "this works too" http://localhost:3317/`

Links
---

https://opentelemetry.io/docs/collector/configuration/

https://opentelemetry.io/ecosystem/registry/

https://github.com/open-telemetry/opentelemetry-collector/commit/e8748663d34dd0c2af1878eee45395c35c9b58c5

https://piehost.com/blog/python-websocket

https://github.com/open-telemetry/opentelemetry-collector/issues/6945

https://github.com/open-telemetry/opentelemetry-collector/pull/9276

https://github.com/open-telemetry/opentelemetry-python/issues/1003

https://opentelemetry.io/docs/specs/otel/protocol/file-exporter/

Other
---

Sudden issue with `git push`, also seen in other repos:

```
git push
...
error: RPC failed; HTTP 400 curl 22 The requested URL returned error: 400
send-pack: unexpected disconnect while reading sideband packet
...
fatal: the remote end hung up unexpectedly
Everything up-to-date
```

Solved by running `git config --global http.postBuffer 524288000`
