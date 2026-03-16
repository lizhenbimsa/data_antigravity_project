# -*- coding: utf-8 -*-
"""
APEP 生产基础设施 — 竞赛系统（Tournament）
==========================================
论文头对头比较系统，使用多个 LLM 裁判进行双盲评比，
通过 ELO 积分追踪论文质量排名。
"""

import json
import random
import time
from pathlib import Path
from itertools import combinations
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "09_agent_framework"))

from config import JUDGE_MODELS, TOURNAMENT_CONFIG, setup_logging
from llm_client import create_client
from elo_rating import ELORatingSystem

logger = setup_logging("apep.tournament")

from judge_prompts import build_judge_prompt, parse_judge_verdict


class Match:
    """单场比赛"""

    def __init__(self, paper_a: str, paper_b: str):
        self.paper_a = paper_a
        self.paper_b = paper_b
        self.verdicts: dict[str, dict] = {}  # judge_key -> verdict
        self.final_result: Optional[float] = None  # 1.0=A胜, 0.5=平, 0.0=B胜

    def add_verdict(self, judge_key: str, verdict: dict):
        self.verdicts[judge_key] = verdict

    def compute_result(self) -> float:
        """根据多个裁判的投票计算最终结果"""
        if not self.verdicts:
            return 0.5

        a_wins = 0
        b_wins = 0
        draws = 0

        for verdict in self.verdicts.values():
            winner = verdict.get("winner", "draw")
            if winner == "paper_a":
                a_wins += 1
            elif winner == "paper_b":
                b_wins += 1
            else:
                draws += 1

        total = a_wins + b_wins + draws
        if total == 0:
            return 0.5

        # 加权结果: A胜=1, 平=0.5, B胜=0
        self.final_result = (a_wins + 0.5 * draws) / total
        return self.final_result

    def to_dict(self) -> dict:
        return {
            "paper_a": self.paper_a,
            "paper_b": self.paper_b,
            "verdicts": self.verdicts,
            "final_result": self.final_result,
        }


class Tournament:
    """
    论文竞赛系统。

    组织 APEP 论文之间或 APEP vs AER/AEJ 论文的头对头比较,
    通过 ELO 积分系统追踪论文质量。
    """

    def __init__(
        self,
        papers_dir: Path | str,
        state_file: Optional[Path | str] = None,
    ):
        self.papers_dir = Path(papers_dir)
        self.state_file = Path(state_file) if state_file else (
            self.papers_dir / "tournament_state.json"
        )
        self.elo = ELORatingSystem(
            initial_rating=TOURNAMENT_CONFIG.initial_elo,
            k_factor=TOURNAMENT_CONFIG.k_factor,
        )
        self.matches: list[Match] = []
        self._load_state()

    def _load_state(self):
        """加载已有的竞赛状态"""
        if self.state_file.exists():
            state = json.loads(self.state_file.read_text(encoding="utf-8"))
            # 恢复 ELO 评分
            for player_data in state.get("players", []):
                from elo_rating import ELOPlayer
                player = self.elo.get_or_create_player(player_data["paper_id"])
                player.rating = player_data["rating"]
                player.matches_played = player_data["matches_played"]
                player.wins = player_data["wins"]
                player.losses = player_data["losses"]
                player.draws = player_data["draws"]
            logger.info(f"📂 加载竞赛状态: {len(self.elo.players)} 选手")

    def save_state(self):
        """保存竞赛状态"""
        state = {
            "total_matches": len(self.matches),
            "players": [p.to_dict() for p in self.elo.players.values()],
            "recent_matches": [m.to_dict() for m in self.matches[-50:]],
        }
        self.state_file.write_text(
            json.dumps(state, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    def _read_paper_abstract(self, paper_id: str) -> str:
        """读取论文内容（用于比较）"""
        # 查找论文目录
        paper_dir = self.papers_dir / paper_id
        if not paper_dir.exists():
            # 尝试带版本号
            for vdir in sorted(paper_dir.parent.glob(f"{paper_id}/v*"), reverse=True):
                paper_dir = vdir
                break

        tex_file = paper_dir / "paper.tex" if paper_dir.exists() else None
        if tex_file and tex_file.exists():
            content = tex_file.read_text(encoding="utf-8", errors="ignore")
            # 截取前 8000 字符（摘要 + 引言 + 方法）
            return content[:8000]

        plan_file = paper_dir / "research_plan.md" if paper_dir.exists() else None
        if plan_file and plan_file.exists():
            return plan_file.read_text(encoding="utf-8")[:4000]

        return f"[Paper content not available for {paper_id}]"

    def run_match(
        self,
        paper_a: str,
        paper_b: str,
        judge_keys: Optional[list[str]] = None,
    ) -> Match:
        """
        执行一场头对头比赛。

        Args:
            paper_a: 论文 A 的 ID
            paper_b: 论文 B 的 ID
            judge_keys: 裁判模型 keys（默认使用所有）

        Returns:
            Match 对象
        """
        if judge_keys is None:
            judge_keys = list(JUDGE_MODELS.keys())

        # 随机决定展示顺序（双盲）
        if random.random() > 0.5:
            display_a, display_b = paper_a, paper_b
            swapped = False
        else:
            display_a, display_b = paper_b, paper_a
            swapped = True

        content_a = self._read_paper_abstract(display_a)
        content_b = self._read_paper_abstract(display_b)

        match = Match(paper_a, paper_b)

        logger.info(f"⚔️  比赛: {paper_a} vs {paper_b}")

        # 并行调用裁判
        with ThreadPoolExecutor(max_workers=len(judge_keys)) as executor:
            futures = {}
            for jk in judge_keys:
                if jk not in JUDGE_MODELS:
                    continue
                system, prompt = build_judge_prompt(content_a, content_b)
                future = executor.submit(
                    self._judge_match, jk, system, prompt
                )
                futures[future] = jk

            for future in as_completed(futures):
                jk = futures[future]
                try:
                    verdict_text = future.result()
                    verdict = parse_judge_verdict(verdict_text, swapped)
                    match.add_verdict(jk, verdict)
                    logger.info(
                        f"  🔨 [{jk}] 判定: {verdict.get('winner', '?')} "
                        f"(信心: {verdict.get('confidence', '?')})"
                    )
                except Exception as e:
                    logger.error(f"  ❌ [{jk}] 裁判失败: {e}")

        # 计算最终结果
        result = match.compute_result()
        winner = paper_a if result > 0.5 else (paper_b if result < 0.5 else "平局")
        logger.info(f"  🏆 结果: {winner} (score={result:.2f})")

        # 更新 ELO
        self.elo.update_ratings(paper_a, paper_b, result)
        self.matches.append(match)

        return match

    def _judge_match(self, judge_key: str, system: str, prompt: str) -> str:
        """单个裁判的比赛判定"""
        config = JUDGE_MODELS[judge_key]
        with create_client(config) as client:
            resp = client.generate(prompt=prompt, system=system)
            return resp.content

    def run_round_robin(
        self,
        paper_ids: list[str],
        max_matches: Optional[int] = None,
    ) -> list[Match]:
        """
        运行循环赛。

        Args:
            paper_ids: 参赛论文 ID 列表
            max_matches: 最大比赛数（None = 全部组合）

        Returns:
            所有比赛结果
        """
        all_pairs = list(combinations(paper_ids, 2))
        random.shuffle(all_pairs)

        if max_matches:
            all_pairs = all_pairs[:max_matches]

        logger.info(f"\n🏟️  循环赛开始: {len(paper_ids)} 篇论文, {len(all_pairs)} 场比赛")

        results = []
        for i, (pa, pb) in enumerate(all_pairs, 1):
            logger.info(f"\n--- 比赛 {i}/{len(all_pairs)} ---")
            match = self.run_match(pa, pb)
            results.append(match)

            # 每 5 场保存一次状态
            if i % 5 == 0:
                self.save_state()

        self.save_state()

        # 输出最终排名
        self._print_rankings()

        return results

    def _print_rankings(self):
        """打印排名表"""
        rankings = self.elo.get_rankings(
            min_matches=TOURNAMENT_CONFIG.min_matches
        )
        if not rankings:
            rankings = self.elo.get_rankings(min_matches=0)

        logger.info(f"\n{'='*60}")
        logger.info("🏆 竞赛排名")
        logger.info(f"{'='*60}")
        logger.info(
            f"{'Rank':<6} {'Paper':<20} {'Rating':<10} "
            f"{'W-L-D':<10} {'Win%':<8}"
        )
        logger.info("-" * 54)
        for r in rankings:
            wld = f"{r['wins']}-{r['losses']}-{r['draws']}"
            logger.info(
                f"{r['rank']:<6} {r['paper_id']:<20} "
                f"{r['rating']:<10.1f} {wld:<10} {r['win_rate']:<8.3f}"
            )

    def get_leaderboard(self) -> list[dict]:
        """获取排行榜"""
        return self.elo.get_rankings()


# ============================================================
# CLI 入口
# ============================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="APEP 论文竞赛系统")
    parser.add_argument("papers_dir", help="论文目录")
    parser.add_argument("--papers", nargs="+", required=True,
                        help="参赛论文 ID 列表")
    parser.add_argument("--max-matches", type=int, default=None,
                        help="最大比赛场次")

    args = parser.parse_args()

    tournament = Tournament(args.papers_dir)
    tournament.run_round_robin(args.papers, max_matches=args.max_matches)
