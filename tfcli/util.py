import subprocess


def run_cmd(cmd: list, logger=None, cwd=None):
    proc = subprocess.Popen(
        cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, cwd=cwd)
    if logger:
        logger.info("running: {}".format(' '.join(cmd)))
    o, e = proc.communicate()
    if proc.returncode != 0 and logger:
        logger.error(o.decode())
        logger.error(e.decode())
    return proc.returncode
