library(did)
att_gt <- att_gt(
  yname = "labor_mobility",     # 劳动力流动率变量名
  tname = "year",
  idname = "state_fips",
  gname = "reform_year",        # 改革实施年份变量
  data = panel_data,
  control_group = "nevertreated",
  anticipation = 0,
  base_period = "universal"
)
att_overall <- aggte(att_gt, type = "simple")
att_event <- aggte(att_gt, type = "dynamic")