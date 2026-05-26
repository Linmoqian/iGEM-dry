from dataclasses import dataclass, field
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "1.测试数据-第一版本"
CLEANED_DIR = BASE_DIR / "data" / "cleaned"
MODEL_DIR = BASE_DIR / "models"
FIGURE_DIR = BASE_DIR / "figures"

# 特征分组常量
DROP_COLS = ["SITE_ID", "UNIQUE_ID", "VISIT_NO", "COMID", "DATE_COL"]
TARGET_COLS = ["MICX", "MICX_DET", "B_G_DENS"]
WATER_QUALITY_COLS = [
    "TEMPERATURE", "MAXDEPTH", "STRATIFIED", "AMMONIA_N", "DO_SURF",
    "DOC", "NTL", "PTL", "TURB", "NITRATE_N", "PH", "CHLA_RESULT",
]
CLIMATE_COLS = ["EVAP_INFL", "D_EXCESS", "precip_mean_month", "temp_mean_month"]
LAND_USE_COLS = ["agr_ws", "dev_ws", "fst_ws"]
TERRAIN_COLS = [
    "lakemorpho_fetch", "BFIWs", "AgKffactWs", "RunoffWs",
    "Precip_Minus_EVTWs", "ElevWs", "SlopeWs",
]
N_BUDGET_COLS = ["N_Surplus", "N_Total_Inputs", "N_Fert_Farm", "N_livestock_Waste"]
P_BUDGET_COLS = ["P_Surplus", "P_f_fertilizer", "P_human_waste_kg"]
AGG_INPUT_COLS = ["n_farm_inputs", "n_dev_inputs", "p_farm_inputs", "p_dev_inputs"]
LOCATION_COLS = ["LAT_DD83", "LON_DD83"]
CATEGORICAL_COLS = ["AG_ECO3"]

# 多数据集注册表
DATASET_REGISTRY: dict[str, dict] = {
    "habs_training": {
        "path": "v2_habs_training_cleaned.parquet",
        "target_clf": "MICX_DET",
        "target_reg": "MICX",
        "date_col": "DATE_COL",
    },
    "lake_erie": {
        "path": "v2_lake_erie_cleaned.parquet",
        "target_clf": "Total Microcystins (\u00b5g/L)",
        "target_reg": "Total Microcystins (\u00b5g/L)",
        "date_col": "Date",
        "clf_threshold": 0.15,
    },
    "sf_estuary": {
        "path": "sf_estuary_cleaned.parquet",
        "target_clf": "ucd.ppia.MC.total.ugL",
        "target_reg": "ucd.ppia.MC.total.ugL",
        "date_col": "Collection_Date",
        "clf_threshold": 0.0,
    },
}


@dataclass(frozen=True)
class DatasetConfig:
    name: str
    raw_path: Path
    output_name: str
    encoding: str = "utf-8-sig"
    comment_char: str | None = None
    skip_rows: int = 0
    na_values: list[str] = field(
        default_factory=lambda: ["", "NA", "N/A", "nd"]
    )
    columns_to_drop: list[str] = field(default_factory=list)
    negative_to_nan_cols: list[str] = field(default_factory=list)
    country_corrections: dict[str, str] = field(default_factory=dict)


def get_configs() -> dict[str, DatasetConfig]:
    return {
        "sf_estuary": DatasetConfig(
            name="旧金山河口 (edi.1076.1)",
            raw_path=(
                RAW_DATA_DIR
                / "美国加利福尼亚州旧金山河口上游的蓝藻丰度、蓝霉毒素浓度及水质数据：2014-2019年"
                / "edi.1076.1"
                / "San Francisco Estuary cyanoHAB data 2014 to 2019_v1.csv"
            ),
            output_name="sf_estuary_cleaned",
            columns_to_drop=[
                "bryte.towNet.Pheo.corrected",
                "field.Chla",
                "bryte.towNet.Chla.corrected",
                "bryte.towNet.Pheo.uncorrected",
                "bryte.towNet.Chla.ave.ugL",
            ],
            negative_to_nan_cols=["field.NTU"],
        ),
        "emls_europe": DatasetConfig(
            name="欧洲EMLS (edi.176.5)",
            raw_path=(
                RAW_DATA_DIR
                / "欧洲地区性数据"
                / "edi.176.5"
                / "EMLSdata_10Aug_afterRev_dateformated.csv"
            ),
            output_name="emls_europe_cleaned",
            country_corrections={"FR": "France", "Lithouania": "Lithuania"},
        ),
        "gull_lake": DatasetConfig(
            name="海湾湖 (knb-lter-kbs)",
            raw_path=(
                RAW_DATA_DIR
                / "密歇根州希科里角凯洛格生物站的海湾湖长期微囊虫监测（1998年至2014年）"
                / "539-gull+lake+long+term+microcystis+monitoring+1765090153.csv"
            ),
            output_name="gull_lake_cleaned",
            comment_char="#",
        ),
        "cleo": DatasetConfig(
            name="CLEO公民科学 (edi.569.1)",
            raw_path=(
                RAW_DATA_DIR
                / "公民主导环境观测站（CLEO）于2015-2018年在美国康涅狄格州利利诺纳湖多个近岸站点采集的地表水样本中测量的半定量微囊菌素浓度"
                / "EDI569_toxins.csv"
            ),
            output_name="cleo_cleaned",
        ),
    }


def get_v2_configs() -> dict[str, DatasetConfig]:
    """第二版本数据集配置。"""
    V2_RAW = BASE_DIR / "data" / "1.测试数据-第二版本"
    return {
        "lake_erie": DatasetConfig(
            name="Lake Erie 全湖采样 (2013-2025)",
            raw_path=(
                V2_RAW
                / "01_Lake_Erie_采样"
                / "Lake_Erie_全湖采样数据_2013-2025.csv"
            ),
            output_name="v2_lake_erie_cleaned",
            encoding="latin1",
            columns_to_drop=[
                "Light attenuation coefficient /m",
                "Unnamed: 35", "Unnamed: 36", "Unnamed: 37",
                "Unnamed: 38", "Unnamed: 39", "Unnamed: 40",
                "Unnamed: 41", "Unnamed: 42", "Unnamed: 43",
            ],
        ),
        "esp_sensor": DatasetConfig(
            name="ESP 传感器部署 (2024)",
            raw_path=(
                V2_RAW
                / "01_Lake_Erie_采样"
                / "ESP_传感器部署数据.csv"
            ),
            output_name="v2_esp_sensor_cleaned",
            columns_to_drop=["Estimate ", "Estimate"],
        ),
        "sb_weekly": DatasetConfig(
            name="SB 周监测 (2024)",
            raw_path=(
                V2_RAW
                / "01_Lake_Erie_采样"
                / "SB_周监测数据.csv"
            ),
            output_name="v2_sb_weekly_cleaned",
            columns_to_drop=["Wind_speed_knots", "Wave_Ht_ft"],
        ),
        "habs_prediction": DatasetConfig(
            name="HABs 预测数据 (NLA 2017)",
            raw_path=(
                V2_RAW
                / "02_HABs_驱动因子模型"
                / "HABs_预测数据.csv"
            ),
            output_name="v2_habs_prediction_cleaned",
        ),
        "habs_training": DatasetConfig(
            name="HABs 模型训练 (NLA 2007/2012/2017)",
            raw_path=(
                V2_RAW
                / "02_HABs_驱动因子模型"
                / "HABs_模型训练数据.csv"
            ),
            output_name="v2_habs_training_cleaned",
        ),
        "erie_summary": DatasetConfig(
            name="Erie 汇总数据 (2008-2017)",
            raw_path=(
                V2_RAW
                / "05_EMS_模型模拟"
                / "Erie_汇总数据_2008-2017.csv"
            ),
            output_name="v2_erie_summary_cleaned",
            encoding="latin1",
        ),
        "mc_data": DatasetConfig(
            name="MC 微囊藻毒素 (2016-2017)",
            raw_path=(
                V2_RAW
                / "03_微囊藻毒素_MC"
                / "MC_综合数据.csv"
            ),
            output_name="v2_mc_comprehensive_cleaned",
        ),
        "mc_env": DatasetConfig(
            name="MC 环境因子 (2016-2017)",
            raw_path=(
                V2_RAW
                / "03_微囊藻毒素_MC"
                / "MC_环境因子数据.csv"
            ),
            output_name="v2_mc_env_cleaned",
        ),
        "mix_data": DatasetConfig(
            name="MIX 混合毒素 (2016-2017)",
            raw_path=(
                V2_RAW
                / "04_混合毒素_MIX"
                / "MIX_综合数据.csv"
            ),
            output_name="v2_mix_comprehensive_cleaned",
        ),
        "mix_env": DatasetConfig(
            name="MIX 环境因子 (2016-2017)",
            raw_path=(
                V2_RAW
                / "04_混合毒素_MIX"
                / "MIX_环境因子数据.csv"
            ),
            output_name="v2_mix_env_cleaned",
        ),
    }
