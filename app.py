from flask import Flask, request, jsonify
from subprocess import Popen
import os
import re

FLAG = os.getenv("FLAG", "SEKAI{}")

app = Flask(__name__)


@app.route("/submit", methods=["POST"])
def submit():
    query = request.json.get("query")

    for i in range(0, 2):
        basedir = f"/opt/db/{i}"
        expected = open(f"{basedir}/hash").read()
        open(f"{basedir}/query.ql", "w").write(query)
        ch = Popen(
            [
                "codeql",
                "query",
                "run",
                "-q",
                "-d",
                f"{basedir}/db",
                f"{basedir}/query.ql",
            ],
            stdout=-1,
            cwd=basedir,
        )
        streamdata = ch.communicate()[0]
        rc = ch.returncode
        if rc:
            return jsonify({"error": streamdata.decode()})

        lline = streamdata.decode().splitlines()[-1]
        match = re.search(r"entry_[0-9a-f]{20}", lline)
        if not (match and expected == match.group(0)):
            return "fail"

    return FLAG


if __name__ == "__main__":
    app.run(host="0", port=1337, threaded=False)
