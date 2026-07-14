# -*- coding: utf-8 -*-
"""
产品一致性确认报告渲染器（文字版 .txt + Markdown .md）

只输出纯文本文档，不生成网页(HTML)、Word、Excel 等格式——重实效、不花哨。
报告含：基本信息、确认结果汇总、维度比对表（核对维度/基准值/实测值/偏差/结论）、偏差清单与整改建议。

用法：
  python build_report.py                                  # 内置小样本，产出 txt+md
  python build_report.py --data-file confirm.json          # 自定义数据
  python build_report.py --out-dir D:/临时                 # 指定输出目录

数据文件（--data-file, JSON）结构：
{
  "basic": {"product":"车型/产品标识","confirm_type":"3C","date":"2026-07-13","owner":"质量部"},
  "dimensions": [
    {"dim":"外廓尺寸","base":"公告值 X","actual":"实测值 Y","dev":"±X","result":"一致"},
    {"dim":"关键件型号","base":"CCC备案 A","actual":"实物件 A","dev":"-","result":"一致"}
  ]
}
"""
import argparse
import json
import os
from datetime import date

SAMPLE = {
    "basic": {
        "product": "示例车型/产品标识（待企业补充）",
        "confirm_type": "3C 认证一致性",
        "date": str(date.today()),
        "owner": "质量部",
    },
    "dimensions": [
        {"dim": "外廓尺寸", "base": "公告值 8500×2500×3100mm", "actual": "实测 8502×2500×3098mm",
         "dev": "长度+2mm / 高度-2mm", "result": "一致"},
        {"dim": "整备质量", "base": "公告值 6800kg", "actual": "实测 6820kg",
         "dev": "+20kg（≤3%）", "result": "一致"},
        {"dim": "关键零部件-侧标志灯", "base": "CCC备案 NG09132 / 供应商甲", "actual": "实物件 NG09132 / 供应商甲",
         "dev": "-", "result": "一致"},
        {"dim": "关键零部件-蓄电池", "base": "CCC备案 BT-100 / 供应商乙", "actual": "实物件 BT-120 / 供应商丙",
         "dev": "型号与供应商均变更", "result": "偏差"},
        {"dim": "3C 标志", "base": "样式备案（标准铭牌）", "actual": "实物铭牌一致",
         "dev": "-", "result": "一致"},
    ],
}


def build_md(data):
    b = data.get("basic", {})
    dims = data.get("dimensions", [])
    passed = sum(1 for d in dims if d.get("result") == "一致")
    dev = len(dims) - passed
    lines = []
    lines.append("# 产品一致性确认报告")
    lines.append("")
    lines.append("## 一、基本信息")
    lines.append("")
    lines.append("| 项目 | 内容 |")
    lines.append("|------|------|")
    lines.append(f"| 产品/车型标识 | {b.get('product','待填写')} |")
    lines.append(f"| 确认类型 | {b.get('confirm_type','待填写')} |")
    lines.append(f"| 确认日期 | {b.get('date','待填写')} |")
    lines.append(f"| 责任部门 | {b.get('owner','待填写')} |")
    lines.append("")
    lines.append("## 二、确认结果汇总")
    lines.append("")
    risk = "高" if dev > 0 else "低"
    lines.append(f"- 确认状态：{'偏差' if dev > 0 else '通过'}")
    lines.append(f"- 通过项数：{passed}　偏差项数：{dev}　风险等级：{risk}")
    lines.append("")
    lines.append("## 三、维度比对表")
    lines.append("")
    lines.append("| 核对维度 | 基准值 | 实测/实物值 | 偏差 | 结论 |")
    lines.append("|----------|--------|-------------|------|------|")
    for d in dims:
        mark = "√" if d.get("result") == "一致" else "×"
        lines.append(f"| {d.get('dim','')} | {d.get('base','')} | {d.get('actual','')} | "
                     f"{d.get('dev','')} | {mark} {d.get('result','')} |")
    lines.append("")
    if dev > 0:
        lines.append("## 四、偏差清单与整改建议")
        lines.append("")
        lines.append("| 序号 | 偏差描述 | 整改建议 | 责任人 | 完成时限 |")
        lines.append("|------|----------|----------|--------|----------|")
        n = 1
        for d in dims:
            if d.get("result") != "一致":
                lines.append(f"| {n} | {d.get('dim','')}：{d.get('dev','')} | "
                             f"核查变更审批与 CCC 备案一致性 | 待企业补充 | 待企业补充 |")
                n += 1
        lines.append("")
    lines.append("> 数据原则：基准值、证书编号、标准限值须引用企业/认证文件，本表基准为示例占位，实际以文件为准。")
    lines.append("")
    lines.append("---")
    lines.append("*本报告由 product-conformance-confirm 生成（仅文字/MD，无网页与办公格式）*")
    return "\n".join(lines)


def build_txt(data):
    b = data.get("basic", {})
    dims = data.get("dimensions", [])
    passed = sum(1 for d in dims if d.get("result") == "一致")
    dev = len(dims) - passed
    L = []
    L.append("产品一致性确认报告")
    L.append("=" * 44)
    L.append("")
    L.append("【一、基本信息】")
    L.append("-" * 44)
    L.append(f"产品/车型标识：{b.get('product','待填写')}")
    L.append(f"确认类型：{b.get('confirm_type','待填写')}")
    L.append(f"确认日期：{b.get('date','待填写')}")
    L.append(f"责任部门：{b.get('owner','待填写')}")
    L.append("")
    L.append("【二、确认结果汇总】")
    L.append("-" * 44)
    risk = "高" if dev > 0 else "低"
    L.append(f"确认状态：{'偏差' if dev > 0 else '通过'}")
    L.append(f"通过项数：{passed}　偏差项数：{dev}　风险等级：{risk}")
    L.append("")
    L.append("【三、维度比对表】")
    L.append("-" * 44)
    for i, d in enumerate(dims, 1):
        mark = "√ 一致" if d.get("result") == "一致" else "× 偏差"
        L.append(f"{i}. 核对维度：{d.get('dim','')}")
        L.append(f"   基准值：{d.get('base','')}")
        L.append(f"   实测/实物值：{d.get('actual','')}")
        L.append(f"   偏差：{d.get('dev','')}")
        L.append(f"   结论：{mark}")
        L.append("")
    if dev > 0:
        L.append("【四、偏差清单与整改建议】")
        L.append("-" * 44)
        n = 1
        for d in dims:
            if d.get("result") != "一致":
                L.append(f"{n}. 偏差：{d.get('dim','')}：{d.get('dev','')}")
                L.append(f"   整改建议：核查变更审批与 CCC 备案一致性")
                L.append(f"   责任人：待企业补充　完成时限：待企业补充")
                L.append("")
                n += 1
    L.append("=" * 44)
    L.append("数据原则：基准值、证书编号、标准限值须引用企业/认证文件，本表基准为示例占位，实际以文件为准。")
    L.append("本报告由 product-conformance-confirm 生成（仅文字/MD，无网页与办公格式）")
    return "\n".join(L)


def main():
    parser = argparse.ArgumentParser(description="产品一致性确认报告（文字版 .txt + Markdown .md）")
    parser.add_argument("--data-file", default="", help="JSON 数据文件路径")
    parser.add_argument("--out-dir", default="", help="输出目录，默认当前工作目录")
    args = parser.parse_args()

    data = SAMPLE
    if args.data_file:
        with open(args.data_file, "r", encoding="utf-8") as f:
            data = json.load(f)

    out_dir = args.out_dir or os.getcwd()
    os.makedirs(out_dir, exist_ok=True)

    md_path = os.path.join(out_dir, "conformance_report.md")
    txt_path = os.path.join(out_dir, "conformance_report.txt")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(build_md(data))
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(build_txt(data))
    print(f"[OK] MD  -> {os.path.abspath(md_path)}")
    print(f"[OK] TXT -> {os.path.abspath(txt_path)}")


if __name__ == "__main__":
    main()
