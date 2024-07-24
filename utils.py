import os
import shutil
import requests
import subprocess


def panic(message: str):
    print(message)
    exit(1)


def download(link, out):
    # https://www.slingacademy.com/article/python-requests-module-how-to-download-files-from-urls/#Streaming_Large_Files
    with requests.get(link, stream=True) as r:
        r.raise_for_status()
        with open(out, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)


# TODO: make builds silent. only print build logs on error
def merge_apk(path: str):
    subprocess.run(
        ["java", "-jar", "./bins/apkeditor.jar", "m", "-i", path]
    ).check_returncode()


# TODO: make builds silent. only print build logs on error
def patch_apk(
    cli: str,
    integrations: str,
    patches: str,
    apk: str,
    includes: list[str] | None = None,
    excludes: list[str] | None = None,
    out: str | None = None,
):
    if out is not None:
        shutil.copyfile(apk, out)
        if not os.path.exists(out):
            raise Exception(f"Failed to copy file to {out}")
        apk = out

    command = [
        "java",
        "-jar",
        cli,
        "patch",
        "-b",
        patches,
        "-m",
        integrations,
        # use j-hc's keystore so we wouldn't need to reinstall
        "--keystore",
        "ks.keystore",
        "--keystore-entry-password",
        "123456789",
        "--keystore-password",
        "123456789",
        "--signer",
        "jhc",
        "--keystore-entry-alias",
        "jhc",
    ]

    if includes is not None:
        for i in includes:
            command.append("-i")
            command.append(i)

    if excludes is not None:
        for e in excludes:
            command.append("-e")
            command.append(e)

    command.append(apk)

    subprocess.run(command).check_returncode()

    # remove -patched from the apk to match out
    if out is not None:
        cli_output = f"{str(out).removesuffix(".apk")}-patched.apk"
        os.unlink(out)
        shutil.move(cli_output, out)