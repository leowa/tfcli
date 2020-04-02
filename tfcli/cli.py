import click
import logging
import tempfile
from os import path
from glob import glob
import shutil
import json
import re
import subprocess

from . import format_logger
from .resources import RESOURCE_TYPES

logger = logging.getLogger("tfcli")


@click.group()
@click.option('--debug/--no-debug', default=False)
@click.option('--dry-run/--no-dry-run', default=False)
@click.pass_context
def cli(ctx: click.Context, debug, dry_run):
    ctx.ensure_object(dict)
    ctx.obj['debug'] = debug
    ctx.obj['dry-run'] = dry_run
    format_logger(logger, debug)


@cli.group()
@click.pass_context
def state(ctx: click.Context):
    pass


@state.command(name='extract')
@click.pass_context
@click.option('--out-file', '-o', help="output path for extracted resource state, default will be <resource>.tfstate", required=False)
@click.option('--state-file', '-s', default="terraform.tfstate", help="original terraform state file")
@click.argument('resources', nargs=-1)
def state_extract(ctx: click.Context, out_file: str, state_file, resources: list):
    if len(resources) < 1:
        click.echo("You should provide at least one resource to extract")
        exit(-1)
    if not out_file:
        if not path.exists("terraform.tfstate"):
            out_file = "terraform.tfstate"
        else:
            out_file = "{}.tfstate".format(
                '-'.join([re.sub("^aws_", "", _) for _ in resources]))
    dry_run = ctx.obj['dry-run']
    # format resources type to lower case
    resources = [_.lower() for _ in resources]
    logger.info('extract from state file:{}, resources:{} to output:{}'.format(
        state_file, resources, out_file))
    if not path.exists(state_file):
        raise FileNotFoundError(state_file)
    try:
        with open(state_file, 'rt') as sf:
            state_json = json.load(sf)
    except Exception as ex:
        logger.error("fail to parse state file. error:{}", ex)
        raise ex
    else:
        all_res = state_json['modules'][0]['resources']
        kept = dict()
        for k, v in all_res.items():
            _type = k.split('.')[0]
            if _type.lower() in resources:
                kept[k] = v
        state_json['modules'][0]['resources'] = kept
        if len(kept) == 0:
            logger.warning(
                "No resource state is found for {}".format(resources))
        else:
            if dry_run:
                click.echo('\n'.join(kept.keys()))
            else:
                with open(out_file, 'wt') as of:
                    json.dump(state_json, of, indent=2)


@state.command(name='import')
@click.pass_context
@click.option('--out-file', '-o', help="output path for extracted resource state, default will be terraform.tfstate or <resource>.tfstate", required=False)
@click.argument('tf', nargs=-1)
def state_import(ctx: click.Context, out_file: str, tf: list):
    if not tf:
        tf = glob("*.tf")
    if not out_file:
        if not path.exists("terraform.tfstate"):
            out_file = "terraform.tfstate"
        else:
            out_file = "{}.tfstate".format(
                '-'.join([re.sub("^aws_", "", _) for _ in tf]))
    if not shutil.which("terraform"):
        logger.error("could not find `terraform` command")
        exit(-1)

    resource_head = re.compile(
        r'^\s*resource\s+"([\w_-]+)"\s+"([\w_-]+)"\s+', re.MULTILINE)
    for item in tf:
        # match lines like this: resource "aws_autoscaling_group" "EC2ContainerService-devpi-EcsInstanceAsg-PN2TBOT7N8BD" {
        failed = []
        with open(item, 'rt') as fd:
            text = fd.read()
            for _type, _id in resource_head.findall(text):
                cmd = ["terraform", "import", "{0}.{1}".format(_type, _id), _id]
                proc = subprocess.Popen(
                    cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                logger.info("running: {}".format(' '.join(cmd)))
                o, e = proc.communicate()
                if proc.returncode != 0:
                    failed.append(' '.join(cmd))
                    click.echo(o)
                    click.echo(e)
        if failed:
            logger.error("The following importing failed:\n")
            click.echo("\n".join(failed))


@cli.command()
@click.pass_context
@click.argument('files', nargs=-1)
def migrate(ctx: click.Context, files):
    if not files:
        files = glob("*.tf")
    for tf in files:
        if not path.exists(tf):
            logger.warning("fail to find tf file:{}".format(tf))
        with open(tf, 'rt') as fd:
            lines = fd.read().splitlines()

        logger.info("processing:{}".format(tf))
        # rule 1: replace `tags {` to `tags = {`
        tags_re = re.compile(r"(^\s+)(tags)(\s*\{)")
        lines = [tags_re.sub(r"\g<1>\g<2> =\g<3>", _) for _ in lines]
        with open(tf, 'wt') as fd:
            fd.truncate()
            fd.write('\n'.join(lines))

        # rule n: validate file
        if not shutil.which("terraform"):
            continue
        td = tempfile.mkdtemp()
        try:
            shutil.copy(tf, path.join(td, path.basename(tf)))
            proc = subprocess.Popen(["terraform", "validate", td],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            o, e = proc.communicate()
            if proc.returncode != 0:
                logger.warning("{} is not valid. Error:{}".format(
                    tf, o.decode() + e.decode()))
        finally:
            shutil.rmtree(td)


@cli.command()
@click.pass_context
@click.option("--types", "-t", required=True, multiple=True,
              type=click.Choice(RESOURCE_TYPES.keys()), help="resource types to sync")
@click.argument('output', default=".", type=click.Path(dir_okay=True))
def sync(ctx: click.Context, types, output):
    flattened = []
    for t in types:
        if isinstance(RESOURCE_TYPES[t], list):
            flattened.extend(RESOURCE_TYPES[t])
        else:
            flattened.append(RESOURCE_TYPES[t])
    click.echo("sync {} to {}".format(
        ",".join([_.__name__ for _ in flattened]), output))
    for r in flattened:
        res, _type = r(logger=logger), r.__name__.lower()
        root = path.join(output, _type)
        if not path.exists(root):
            shutil.os.makedirs(root)
        logger.info("+" * 25 + _type + "+" * 25)
        res.create_tfconfig(root)
        res.load_tfstate(root)
        res.sync_tfstate(root)
