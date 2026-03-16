# -*- coding: utf-8 -*-
"""
APEP 生产基础设施 — ELO 积分系统
==========================================
实现标准 ELO 评分算法，用于论文竞赛排名。
"""

import math
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ELOPlayer:
    """ELO 参赛者（论文）"""
    paper_id: str
    rating: float = 1500.0
    matches_played: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0
    rating_history: list = field(default_factory=list)

    @property
    def win_rate(self) -> float:
        if self.matches_played == 0:
            return 0.0
        return self.wins / self.matches_played

    def record_rating(self):
        """记录当前评分到历史"""
        self.rating_history.append({
            "rating": round(self.rating, 1),
            "match": self.matches_played,
        })

    def to_dict(self) -> dict:
        return {
            "paper_id": self.paper_id,
            "rating": round(self.rating, 1),
            "matches_played": self.matches_played,
            "wins": self.wins,
            "losses": self.losses,
            "draws": self.draws,
            "win_rate": round(self.win_rate, 3),
            "rating_history": self.rating_history,
        }


class ELORatingSystem:
    """
    标准 ELO 评分系统。

    用于 APEP 论文之间以及与发表论文的头对头比较。
    """

    def __init__(
        self,
        initial_rating: float = 1500.0,
        k_factor: float = 32.0,
    ):
        """
        Args:
            initial_rating: 新参赛者的初始评分
            k_factor: K 因子（决定单场比赛对评分的影响大小）
                     较大的 K = 评分变化更快（适合少量比赛）
                     较小的 K = 评分更稳定（适合大量比赛）
        """
        self.initial_rating = initial_rating
        self.k_factor = k_factor
        self.players: dict[str, ELOPlayer] = {}

    def get_or_create_player(self, paper_id: str) -> ELOPlayer:
        """获取或创建参赛者"""
        if paper_id not in self.players:
            self.players[paper_id] = ELOPlayer(
                paper_id=paper_id,
                rating=self.initial_rating,
            )
        return self.players[paper_id]

    def expected_score(self, rating_a: float, rating_b: float) -> float:
        """
        计算 A 的期望得分（胜率）。

        E_A = 1 / (1 + 10^((R_B - R_A) / 400))
        """
        return 1.0 / (1.0 + math.pow(10.0, (rating_b - rating_a) / 400.0))

    def update_ratings(
        self,
        paper_a: str,
        paper_b: str,
        result: float,
        k_factor: Optional[float] = None,
    ) -> tuple[float, float]:
        """
        更新两篇论文的 ELO 评分。

        Args:
            paper_a: 论文 A 的 ID
            paper_b: 论文 B 的 ID
            result: A 的比赛结果
                    1.0 = A 胜
                    0.5 = 平局
                    0.0 = B 胜
            k_factor: 可选覆盖 K 因子

        Returns:
            (A 的新评分, B 的新评分)
        """
        k = k_factor or self.k_factor
        player_a = self.get_or_create_player(paper_a)
        player_b = self.get_or_create_player(paper_b)

        # 期望得分
        expected_a = self.expected_score(player_a.rating, player_b.rating)
        expected_b = 1.0 - expected_a

        # 计算评分变化
        delta_a = k * (result - expected_a)
        delta_b = k * ((1.0 - result) - expected_b)

        # 更新评分
        player_a.rating += delta_a
        player_b.rating += delta_b

        # 更新统计
        player_a.matches_played += 1
        player_b.matches_played += 1

        if result == 1.0:
            player_a.wins += 1
            player_b.losses += 1
        elif result == 0.0:
            player_a.losses += 1
            player_b.wins += 1
        else:
            player_a.draws += 1
            player_b.draws += 1

        player_a.record_rating()
        player_b.record_rating()

        return player_a.rating, player_b.rating

    def get_rankings(self, min_matches: int = 0) -> list[dict]:
        """
        获取按评分排序的排名表。

        Args:
            min_matches: 最少比赛场次门槛

        Returns:
            排名列表
        """
        qualified = [
            p for p in self.players.values()
            if p.matches_played >= min_matches
        ]
        ranked = sorted(qualified, key=lambda x: x.rating, reverse=True)

        return [
            {"rank": i + 1, **p.to_dict()}
            for i, p in enumerate(ranked)
        ]

    def get_rating(self, paper_id: str) -> float:
        """获取论文当前评分"""
        player = self.players.get(paper_id)
        return player.rating if player else self.initial_rating

    def confidence_interval(
        self, paper_id: str, confidence: float = 0.95
    ) -> tuple[float, float]:
        """
        计算评分的置信区间。

        使用正态近似: R ± z * σ
        其中 σ ≈ K / sqrt(n)
        """
        import scipy.stats as stats

        player = self.players.get(paper_id)
        if not player or player.matches_played < 2:
            return (0.0, 3000.0)

        z = stats.norm.ppf((1 + confidence) / 2)
        sigma = self.k_factor / math.sqrt(player.matches_played)

        return (
            round(player.rating - z * sigma, 1),
            round(player.rating + z * sigma, 1),
        )

    def to_dict(self) -> dict:
        """导出完整状态"""
        return {
            "initial_rating": self.initial_rating,
            "k_factor": self.k_factor,
            "total_players": len(self.players),
            "rankings": self.get_rankings(),
        }


# ============================================================
# 自测（含数值验证）
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("ELO 评分系统自测")
    print("=" * 60)

    elo = ELORatingSystem(initial_rating=1500.0, k_factor=32.0)

    # 模拟几场比赛
    print("\n--- 模拟比赛 ---")

    # Paper A (APEP) beats Paper B (AER)
    ra, rb = elo.update_ratings("apep_0001", "aer_ref_001", result=1.0)
    print(f"apep_0001 胜 aer_ref_001: R_A={ra:.1f}, R_B={rb:.1f}")

    # Paper A loses to Paper C
    ra, rc = elo.update_ratings("apep_0001", "aer_ref_002", result=0.0)
    print(f"apep_0001 负 aer_ref_002: R_A={ra:.1f}, R_C={rc:.1f}")

    # Draw
    ra, rb = elo.update_ratings("apep_0001", "apep_0002", result=0.5)
    print(f"apep_0001 平 apep_0002: R_A={ra:.1f}, R_B={rb:.1f}")

    # More matches for robust ranking
    elo.update_ratings("apep_0002", "aer_ref_001", result=1.0)
    elo.update_ratings("apep_0002", "aer_ref_002", result=1.0)
    elo.update_ratings("apep_0002", "apep_0003", result=0.5)
    elo.get_or_create_player("apep_0003")
    elo.update_ratings("apep_0003", "aer_ref_001", result=0.0)

    # 显示排名
    print("\n--- 最终排名 ---")
    rankings = elo.get_rankings()
    print(f"{'Rank':<6} {'Paper':<15} {'Rating':<10} {'W-L-D':<10} {'Win%':<8}")
    print("-" * 50)
    for r in rankings:
        wld = f"{r['wins']}-{r['losses']}-{r['draws']}"
        print(f"{r['rank']:<6} {r['paper_id']:<15} {r['rating']:<10.1f} {wld:<10} {r['win_rate']:<8.3f}")

    # 验证数学
    print("\n--- 数学验证 ---")
    e = elo.expected_score(1500, 1500)
    print(f"期望得分 (1500 vs 1500): {e:.4f} (应为 0.5)")
    assert abs(e - 0.5) < 0.001, "期望得分计算错误"

    e = elo.expected_score(1600, 1400)
    print(f"期望得分 (1600 vs 1400): {e:.4f} (应约为 0.76)")
    assert 0.75 < e < 0.77, "期望得分计算错误"

    print("\n✅ 所有验证通过")
