import subprocess
from pathlib import Path

from loguru import logger

from mml_utils.os_utils import bat_or_sh


def run_ctakes(directory: Path, ctakes_home: Path, outdir: Path, umls_key: str = None):
    """
    Run `runClinicalPipeline.bat` from cTAKES installation directory.
    :param umls_key: umls key (not username/password
    :param directory: directory containing text files to run cTAKES on
    :param ctakes_home: home directory of cTAKES, e.g., C:/apache-ctakes-4.x.y.z
    :param outdir: directory to output xmi files
    :return:
    """
    logger.info(f'Running cTKAES in {directory}.')
    exe_path = Path('.') / 'bin' / f'runClinicalPipeline.{bat_or_sh()}'
    umls_arg = f'--key {umls_key}' if umls_key else ''
    cmd = f'{exe_path} -i {directory} --xmiOut {outdir} {umls_arg}'.split()
    res = subprocess.run(cmd, shell=True, universal_newlines=True, cwd=ctakes_home)
    if res.returncode != 0:
        logger.warning(f'cTAKES returned with status code {res.returncode}.')
        logger.info(f'cTAKES STDERR: {res.stderr}')
    return res
