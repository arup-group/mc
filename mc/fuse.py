import os
import pandas as pd
from pathlib import Path


class Stats:

    columns = None

    def __init__(self) -> None:
        self.stats = pd.DataFrame()

    def load(self, path: Path):
        self.stats = pd.read_csv(path, delimiter='\t')
        self.stats.columns = self.columns

    def write(self, path: Path):
        self.stats.to_csv(path, sep="\t")


class FusedScore(Stats):

    columns = ["iteration", "executed", "worst", "average", "best"]

    def fuse(self, prev_dir: Path, latest_dir: Path):
        """
        For given previous directory fuse previously fused scorestats to latest
        directory scorestats. Write to scorestats_fused.txt in latest directory.

        Args:
            prev_dir (Path): previous matsim output directory path
            latest_dir (Path): lastest matsim output directory path
        """

        prev = os.path.join(prev_dir / "scorestats_fused.txt")
        latest = os.path.join(latest_dir / "scorestats.txt")
        out_path = os.path.join(latest_dir / "scorestats_fused.txt")

        if os.path.exists(prev):
            self.load(prev)
            self.stats.drop(self.stats.index[-1], inplace=True)  # this iteration is repeated in latests

        latest_scores = pd.read_csv(latest, delimiter='\t', encoding='utf-8')
        latest_scores.columns = self.columns    
        self.stats.append(latest_scores, ignore_index=True)

        self.write(out_path)


class FusedModeShares(Stats):

    columns = ["mode", "share"]

    def fuse(self, prev_dir: Path, latest_dir: Path):
        """
        For given previous directory fuse previously fused modeshares to latest
        directory modeshares. Write to scorestats_fused.txt in latest directory.

        Args:
            prev_dir (Path): previous matsim output directory path
            latest_dir (Path): lastest matsim output directory path
        """

        prev = os.path.join(prev_dir / "modestats_fused.txt.txt")
        latest = os.path.join(latest_dir / "modestats.txt")
        out_path = os.path.join(latest_dir / "modestats_fused.txt")

        if os.path.exists(prev):
            self.load(prev)
            self.stats.drop(self.stats.index[-1], inplace=True)  # this iteration is repeated in latest

        latest_shares = pd.read_csv(latest, delimiter='\t', encoding='utf-8')
        latest_shares.columns = self.columns
        self.stats.append(latest_shares, ignore_index=True)

        self.write(out_path)