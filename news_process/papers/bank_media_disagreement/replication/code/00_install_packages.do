* news_process v3.7.0 — 必需 Stata 包安装 (第 10 篇)
* 幂等: 已安装则跳过

version 19

local required_packages reghdfe ftools estout coefplot asdoc ivreg2 ranktest

foreach pkg of local required_packages {
    capture which `pkg'
    if _rc != 0 {
        display "  Installing `pkg'..."
        capture ssc install `pkg', replace
        if _rc != 0 {
            display "  WARNING: `pkg' install failed; please install manually"
        }
    }
    else {
        display "  `pkg' already installed"
    }
}
