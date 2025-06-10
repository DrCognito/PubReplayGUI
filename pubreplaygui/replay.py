from pathlib import Path
from pubreplaygui import LOG, PARSER_LOC
import subprocess
from subprocess import CompletedProcess
from queue import Queue
from concurrent.futures import ProcessPoolExecutor
import os


def get_replay_files(replay_path: Path, min_bytes: int = 1000000) -> set[Path]:
    replays = list(Path(replay_path).glob('*.dem'))
    output = set()
    for r in replays:
        # Size in bytes
        if r.stat().st_size > min_bytes:
            output.add(r)
        else:
            LOG.info(f"Replay {r} skipped as it is less than 1MB. Check if the download is complete.")

    return output


def get_json_files(output_path: Path) -> set[Path]:
    return set(Path(output_path).glob('*.json'))

# https://github.com/pyinstaller/pyinstaller/wiki/Recipe-subprocess PyInstaller and popen+tkinter
# Create a set of arguments which make a ``subprocess.Popen`` (and
# variants) call work with or without Pyinstaller, ``--noconsole`` or
# not, on Windows and Linux. Typical use::
#
#   subprocess.call(['program_to_run', 'arg_1'], **subprocess_args())
#
# When calling ``check_output``::
#
#   subprocess.check_output(['program_to_run', 'arg_1'],
#                           **subprocess_args(False))
def subprocess_args(include_stdout=True):
    # The following is true only on Windows.
    if hasattr(subprocess, 'STARTUPINFO'):
        # On Windows, subprocess calls will pop up a command window by default
        # when run from Pyinstaller with the ``--noconsole`` option. Avoid this
        # distraction.
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        # Windows doesn't search the path by default. Pass it an environment so
        # it will.
        env = os.environ
    else:
        si = None
        env = None

    # ``subprocess.check_output`` doesn't allow specifying ``stdout``::
    #
    #   Traceback (most recent call last):
    #     File "test_subprocess.py", line 58, in <module>
    #       **subprocess_args(stdout=None))
    #     File "C:\Python27\lib\subprocess.py", line 567, in check_output
    #       raise ValueError('stdout argument not allowed, it will be overridden.')
    #   ValueError: stdout argument not allowed, it will be overridden.
    #
    # So, add it only if it's needed.
    if include_stdout:
        ret = {'stdout': subprocess.PIPE}
    else:
        ret = {}

    # On Windows, running this from the binary produced by Pyinstaller
    # with the ``--noconsole`` option requires redirecting everything
    # (stdin, stdout, stderr) to avoid an OSError exception
    # "[Error 6] the handle is invalid."
    ret.update({'stdin': subprocess.PIPE,
                'stderr': subprocess.PIPE,
                'startupinfo': si,
                'env': env })
    return ret


def process_replay(replay_in: Path, json_out: Path, ignore_existing=False) -> CompletedProcess:
    if ignore_existing and json_out.exists():
        LOG.info(f"Skipping replay file {replay_in.name} as {json_out.name} exists in output.")
        
    process_args = [
        str(PARSER_LOC),
        "-i",
        str(replay_in),
        "-o",
        str(json_out)
        ]

    # return subprocess.run(process_args, capture_output=True, text=True, **subprocess_args(include_stdout=True))
    return subprocess.run(process_args, text=True, **subprocess_args(include_stdout=True))


def process_replay_path(
    replay_dir: Path, output_dir: Path, reprocess=False,
    progress_bar=None):
    replays = get_replay_files(replay_dir)
    if progress_bar is not None:
        progress_bar['maximum'] = len(replays)
    for r in replays:
        json_path = output_dir / r.name.replace(".dem", ".json")
        if json_path.exists() and not reprocess:
            LOG.info(f"Skipping replay file {r.name} as {json_path.name} exists in output.")
        LOG.info(f"Processing {r.name}.")
        result = process_replay(r, output_dir,)
        LOG.debug(f"Process completed with:")
        LOG.debug(result.stdout)
        if progress_bar is not None:
            progress_bar.step()

    return


def thread_replays(replay_dir: Path, output_dir: Path, reprocess=False,
    progress_bar=None, res_queue: Queue | None = None):
    '''
    Runs replay processing in a seperate thread (for a GUI).
    Results are added to a queue for post processing!
    '''
    replays = get_replay_files(replay_dir)
    if progress_bar is not None:
        progress_bar['maximum'] = len(replays)
    executor = ProcessPoolExecutor(max_workers=1)
    for r in replays:
        json_path = output_dir / r.name.replace(".dem", ".json")
        if json_path.exists() and not reprocess:
            LOG.info(f"Skipping replay file {r.name} as {json_path.name} exists in output.")
            if progress_bar is not None:
                progress_bar.step()
            continue
        LOG.debug(f"Adding {r.name} to ProcessPool.")
        task = executor.submit(process_replay, r, output_dir)
        # call_back = lambda x: res_queue.put((str(r.name),x))
        if res_queue is not None:
            # task.add_done_callback(call_back)
            res_queue.put((r.name, task))
            # pass
        # result = process_replay(r, output_dir,)
        # LOG.debug(f"Process completed with:")
        # LOG.debug(result.stdout)

    return


if __name__ == "__main__":
    replay_dir = Path("D:\\SteamLibrary\\steamapps\\common\\dota 2 beta\\game\\dota\\replays")
    output_dir = Path("output").resolve()
    
    process_replay_path(replay_dir, output_dir, reprocess=True)