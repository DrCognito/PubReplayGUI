from pathlib import Path
from pubreplaygui import LOG, PARSER_LOC
import subprocess
from subprocess import CompletedProcess


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

    return subprocess.run(process_args, capture_output=True, text=True)


def process_replay_path(replay_dir: Path, output_dir: Path, reprocess=False):
    replays = get_replay_files(replay_dir)

    for r in replays:
        json_path = output_dir / r.name.replace(".dem", ".json")
        if json_path.exists() and not reprocess:
            LOG.info(f"Skipping replay file {r.name} as {json_path.name} exists in output.")
        LOG.info(f"Processing {r.name}.")
        result = process_replay(r, output_dir,)
        LOG.info(f"Process completed with:")
        LOG.info(result.stdout)

    return

if __name__ == "__main__":
    replay_dir = Path("D:\\SteamLibrary\\steamapps\\common\\dota 2 beta\\game\\dota\\replays")
    output_dir = Path("output").resolve()
    
    process_replay_path(replay_dir, output_dir, reprocess=True)