import json
from pathlib import Path
import platform
import shutil
import socket
import sys


from bench_runner import result as mod_result


DATA_PATH = Path(__file__).parent / "data"


def _copy_results(tmp_path):
    results_path = tmp_path / "results"
    shutil.copyfile(DATA_PATH / "bench_runner.toml", tmp_path / "bench_runner.toml")
    shutil.copytree(DATA_PATH / "results", tmp_path / "results")
    return results_path


def test_load_all_results(tmp_path):
    # results_path = _copy_results(tmp_path)
    # monkeypatch.chdir(tmp_path)
    results_path = tmp_path / "results"

    #results = mod_result.load_all_results(["3.12.0b1"], results_path)
    results = mod_result.load_all_results([], results_path)
    print("All results:")
    for result in results:
        print()
        print("result.cpython_hash:", result.cpython_hash, 
              "result.flags:", result.flags, 
              "result.bases:", result.bases)
        print()
        for base in result.bases.values():
            print("*"*20 , "SPECIAL")
            print("base.ref.version:", base.ref.version, "\nbase.ref.cpython_hash:", base.ref.cpython_hash, "\nbase.ref.flags:", base.ref.flags)
            print("\nbase.head.version:", base.head.version, "\nbase.head.cpython_hash:", base.head.cpython_hash, "\nbase.head.flags:", base.head.flags)
            print("---base.geometric_mean:", base.geometric_mean)
            print("\n\n")

tmp_path = Path(__file__).parent / "temp_path"
test_load_all_results(tmp_path)

def test_merge_base(tmp_path, monkeypatch):
    monkeypatch.chdir(DATA_PATH)

    results_path = _copy_results(tmp_path)

    # Hack up so one of the results has an explicit commit_merge_base
    result_with_base = (
        results_path
        / "bm-20221119-3.12.0a3+-b0e1f9c"
        / "bm-20221119-linux-x86_64-python-main-3.12.0a3+-b0e1f9c.json"
    )
    with open(result_with_base) as fd:
        contents = json.load(fd)
    contents["metadata"][
        "commit_merge_base"
    ] = "9d38120e335357a3b294277fd5eff0a10e46e043"
    with open(result_with_base, "w") as fd:
        json.dump(contents, fd)
    # End hack

    results = mod_result.load_all_results([], results_path)

    by_hash = {x.cpython_hash: x for x in results}

    head = by_hash["b0e1f9c"]
    comparison = head.bases["base"]

    assert head.commit_merge_base == "9d38120e335357a3b294277fd5eff0a10e46e043"
    assert comparison.ref.version == "3.10.4"
    assert comparison.head is head
    assert comparison.geometric_mean == "1.70x faster"


def test_from_scratch(monkeypatch):
    monkeypatch.chdir(DATA_PATH)

    python = sys.executable

    def get_git_hash(*args):
        return "b7e4f1d97c6e784d2dee182d2b81541ddcff5751"

    monkeypatch.setattr(mod_result.git, "get_git_hash", get_git_hash)

    def get_git_commit_date(*args):
        return "2022-11-19T20:47:09+00:00"

    monkeypatch.setattr(mod_result.git, "get_git_commit_date", get_git_commit_date)

    def gethostname(*args):
        return "pyperf"

    monkeypatch.setattr(socket, "gethostname", gethostname)

    result = mod_result.Result.from_scratch(
        python, "my-fork", "9d38120e335357a3b294277fd5eff0a10e46e043"
    )

    assert result.filename == Path(
        f"results/bm-20221119-{platform.python_version()}-b7e4f1d/"
        f"bm-20221119-{platform.system().lower()}-{platform.machine().lower()}"
        f"-my%2dfork-9d38120e335357a3b294-{platform.python_version()}-b7e4f1d.json"
    )

    assert result.runner == "linux x86_64 (linux)"
    assert result.system == "linux"

    result = mod_result.Result.from_scratch(
        python,
        "my-fork",
        "9d38120e335357a3b294277fd5eff0a10e46e043",
        flags=["PYTHON_UOPS", "BAR"],
    )

    assert result.filename == Path(
        f"results/bm-20221119-{platform.python_version()}-b7e4f1d-BAR,PYTHON_UOPS/"
        f"bm-20221119-{platform.system().lower()}-{platform.machine().lower()}"
        f"-my%2dfork-9d38120e335357a3b294-{platform.python_version()}-b7e4f1d.json"
    )
