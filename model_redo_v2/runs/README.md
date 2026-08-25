# runs

每次训练在本目录创建独立运行文件夹，保存配置、数据哈希、切分摘要、折外权重、模型、校准器、预测和指标。`locked test` 运行目录应归档并禁止覆盖。

本地 `smoke_*` 目录均为工程检查产物，不是正式性能结果。`smoke_xgb_aft/` 特意保留第一次端到端检查捕获的只读权重数组失败记录；修复后的 `smoke_xgb_aft_01/`、`smoke_xgb_reload/` 与 `smoke_full_ensemble/` 均为 `complete`。服务器正式训练请使用新的非 `smoke` 运行名。
