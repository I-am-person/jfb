import random
import hashlib


def randstr():
    return hashlib.sha256(random.randbytes(20)).hexdigest()[:20]


class Shuffler(object):

    def __init__(self):
        self.src = []
        self.gen = {}
        self.hash = None

    def gen_func(self, body, prefix):
        fname = f"{prefix}_{randstr()}"
        return fname, f"def {fname}():\n    return {body}\n"

    def generate_sum(self, target_sum):
        numbers = list(self.gen.keys())
        result = []

        while target_sum > 0:
            choice = target_sum + 1
            while choice > target_sum:
                choice = random.choice(numbers)

            result.append(self.gen[choice])
            target_sum -= choice

        return result

    def gen_program(self):
        for n in [1, 2, 5]:
            (_, f) = self.gen_func(n, "fn")
            self.gen[n] = n

        for _ in range(0x100):
            sum = random.randint(10, 0x100)
            body = " + ".join(map(str, self.generate_sum(sum)))
            (fname, f) = self.gen_func(body, "fn")
            if sum not in self.gen:
                self.gen[sum] = fname + "()"
                self.src.append(f)

        for sum in range(1, 0x400):
            body = " + ".join(map(str, self.generate_sum(sum)))
            (fname, f) = self.gen_func(body, "entry")
            if sum == 42:
                self.hash = fname
            self.src.append(f)

        random.shuffle(self.src)
        return self.src, self.hash


if __name__ == "__main__":
    import sys
    from subprocess import Popen

    out_dir = sys.argv[1]

    src, hash = Shuffler().gen_program()

    open(f"{out_dir}/main.py", "w").write("\n".join(src))
    open(f"{out_dir}/qlpack.yml", "w").write(
        """---
library: false
dependencies:
  codeql/python-queries: ^1.0.1"""
    )
    ch = Popen(
        [
            "codeql",
            "database",
            "create",
            f"{out_dir}/db",
            "--language=python",
        ],
        stdout=-1,
        cwd=out_dir,
    )
    streamdata = ch.communicate()[0]
    rc = ch.returncode
    if rc:
        print({"creating db": streamdata.decode()})
    open(f"{out_dir}/hash", "w").write(hash)
