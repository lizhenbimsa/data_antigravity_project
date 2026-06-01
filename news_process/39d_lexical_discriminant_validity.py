"""39d_lexical_discriminant_validity.py — v3.5.1 A1/A3 discriminant validity (HTMT + AVE + κ + α).

≤30 行 thin shim, 实现位于 news_process.pipeline.audit.lexical_discriminant_validity.

锚定: Henseler-Ringle-Sarstedt 2015 JAMS; Fornell-Larcker 1981 JMR;
      Cohen 1960 EPM; Cronbach 1951 Psychometrika.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    from news_process.pipeline.audit.lexical_discriminant_validity import main
    main()
