# Benchmarking tools for the Faster CPython project

## Usage

This code lets you set up your own Github repo to run pyperformance benchmarks on your own self-hosted Github Action runners.

### Set up the repo

Add bench_runner to your requirements.  Since there are no PyPI releases yet, you can install it from a tag in the git repo:

```
git+https://github.com/faster-cpython/bench_runner@v0.2.2#egg=bench_runner
```

Create a virtual environment and install your requirements to it.

Run the install script to generate the files to make the Github Actions work (from the root of your repo):

```
$ python -m bench_runner.scripts.install
```

This will create some files in `.github/workflows` as well as some configuration files at the root of your repo.
Commit them to your repository.

### Add some self-hosted runners

Provision the machine according to the [provisioning instructions](PROVISIONING.md).

Then, add it to the pool of runners by following the instructions on Github's
`Settings -> Actions -> Runners -> Add New Runner` to add a new runner.

The default responses to all questions should be fine *except* pay careful attention to set the labels correctly.
Each runner must have the following labels:
  - One of `linux`, `macos` or `windows`.
  - `bare-metal` (to distinguish it from VMs in the cloud).
  - `$os-$arch-$nickname`, where:
    - `$os` is one of `linux`, `macos`, `windows`
    - `$arch` is one of `x86_64` or `arm64` (others may be supported in future)
    - `$nickname` is a unique nickname for the runner.

Once the runner is set up, [enable it as a
service](https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/configuring-the-self-hosted-runner-application-as-a-service)
so it will start automatically on boot.

In addition, the metadata about the runner must be added to `runners.ini`, for example:

```
[linux]
os = linux
arch = x86_64
hostname = pyperf
```

**TODO**: Describe the special pystats runner

### Configure your repo

#### Set of benchmarks

By default, all of the benchmarks in `pyperformance` and `python-macrobenchmarks` are run.  To configure the set of benchmarks, or add more, edit the `benchmarks.manifest` file.
The format of this file is documented with `pyperformance`.

#### Reference versions

All benchmarked commits are automatically compared to key "reference" versions, as well as their merge base, if available.

The reference versions are defined in the `bases.txt` file.

Don't forget to actually collect benchmark data for those tags -- it's doesn't happen automatically.

#### Longitudinal plot

**TODO**: The longitudinal plot isn't currently configurable.

## Developer

To learn how to hack on this project, see the full [developer documentation](DEVELOPER.md).
