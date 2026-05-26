"""39g_track_discriminant_validity.py — v3.7.3 Plan A v1.0: _full/_ctx/_title track HTMT 3×3.

Thin shim per CLAUDE.md 约定 (v3.7.2 后 39 个; v3.7.3 Plan A v1.0 加 stage 39g 后 40 个).
实现位于 news_process.pipeline.audit.track_discriminant_validity.

锚定: Heston & Sinha (2017) FAJ; Loughran & McDonald (2016) JAR survey §6;
      Boudoukh et al. (2019) JFE; Campbell & Fiske (1959) MTMM;
      Henseler-Ringle-Sarstedt (2015) JAMS HTMT 双 cutoff.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    from news_process.pipeline.audit.track_discriminant_validity import main
    main()
